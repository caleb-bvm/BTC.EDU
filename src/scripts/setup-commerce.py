"""Prepare reusable local FakeWallet wallets. Never print provider credentials."""
import json
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
local = ROOT / ".local"
wallet_file = local / "commerce-wallets.json"


def setup():
    credentials = json.loads((local / "demo-credentials.json").read_text(encoding="utf-8"))
    with httpx.Client(base_url="http://127.0.0.1:5000", timeout=15, trust_env=False, follow_redirects=False) as client:
        def call(method, path, **kwargs):
            response = client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        auth = call("POST", "/api/v1/auth", json=credentials)
        provider_settings = call("GET", "/admin/api/v1/settings")
        if provider_settings.get("lnbits_backend_wallet_class") != "FakeWallet":
            raise RuntimeError("El proveedor no usa FakeWallet. No se modificó su configuración ni se prepararon pagos.")
        if wallet_file.exists():
            wallets = json.loads(wallet_file.read_text(encoding="utf-8"))
        else:
            wallets = {"receiver": call("POST", "/api/v1/wallet", json={"name": "BTC.EDU ventas simuladas"}),
                       "payer": call("POST", "/api/v1/wallet", json={"name": "BTC.EDU comprador ficticio"})}
            wallet_file.write_text(json.dumps(wallets), encoding="utf-8")
        # Existing payer balances are checked before topping up; all funds fictitious.
        payer = wallets["payer"]
        balance = call("GET", "/api/v1/wallet", headers={"X-Api-Key": payer["adminkey"]})
        if balance["balance"] < 1_000_000 * 1000:
            call("PUT", "/users/api/v1/balance", json={"id": payer["id"], "amount": 1_000_000})
        env = "\n".join(("COMMERCE_SIMULATION=true", "LNBITS_URL=http://127.0.0.1:5000",
                         "LNBITS_INVOICE_KEY=" + wallets["receiver"]["inkey"],
                         "LNBITS_PAYER_KEY=" + payer["adminkey"], "LNBITS_ADMIN_TOKEN=" + auth["access_token"], ""))
        (local / "commerce.env").write_text(env, encoding="utf-8")
    print("OK: FakeWallet verificada; comercio simulado preparado. Reinicia Django para cargar la configuración local.")


if __name__ == "__main__":
    try:
        setup()
    except (httpx.HTTPError, KeyError, ValueError, OSError, RuntimeError):
        raise SystemExit("No se pudo preparar el comercio. Comprueba LNbits local, sus credenciales y FakeWallet; no se muestran secretos.") from None

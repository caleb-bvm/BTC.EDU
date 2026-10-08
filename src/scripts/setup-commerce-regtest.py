"""Configure the existing LNbits merchant wallet; never print keys or tokens."""
import argparse
import getpass
import os
from pathlib import Path

import httpx


def setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", default="Admin")
    parser.add_argument("--wallet", default="56b78306d7034e7da2c020ce1603f017")
    args = parser.parse_args()
    password = os.getenv("LNBITS_SETUP_PASSWORD") or getpass.getpass("Contraseña del administrador de LNbits regtest: ")
    with httpx.Client(base_url="http://127.0.0.1:5001", timeout=15, trust_env=False) as client:
        response = client.post("/api/v1/auth", json={"username": args.username, "password": password})
        response.raise_for_status()
        token = response.json()["access_token"]
        client.headers["Authorization"] = "Bearer " + token
        response = client.get("/admin/api/v1/settings")
        response.raise_for_status()
        if response.json().get("lnbits_backend_wallet_class") != "LndRestWallet":
            raise ValueError("Se requiere LndRestWallet.")
        response = client.get("/api/v1/wallet/paginated", params={"limit": 100})
        response.raise_for_status()
        wallet = next(w for w in response.json()["data"] if w["id"] == args.wallet)
        if not wallet.get("inkey"):
            raise ValueError("Falta la clave de recepción.")
        local = Path(__file__).resolve().parents[1] / ".local"
        destination = local / "commerce.env"
        backup = local / "commerce-fake.env.backup"
        if destination.exists() and not backup.exists():
            backup.write_bytes(destination.read_bytes())
        destination.write_text("\n".join((
            "COMMERCE_SIMULATION=true", "COMMERCE_PAYMENT_MODE=regtest",
            "LNBITS_URL=http://127.0.0.1:5001", "LNBITS_PAYER_KEY=",
            "LNBITS_INVOICE_KEY=" + wallet["inkey"], "LNBITS_ADMIN_TOKEN=" + token, "",
        )), encoding="utf-8")
    print("LNbits regtest configurado. Reinicia BTC.EDU para cargarlo. No se realizaron pagos.")


if __name__ == "__main__":
    try:
        setup()
    except (httpx.HTTPError, OSError, ValueError, KeyError, StopIteration):
        raise SystemExit("No se pudo configurar el comercio regtest. Revisa LNbits, usuario, contraseña y wallet.") from None

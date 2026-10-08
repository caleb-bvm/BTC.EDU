"""Start a separate LNbits instance after verifying Polar's merchant node."""
import argparse
import os
import ssl
import sys
from pathlib import Path

import httpx


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", default="https://127.0.0.1:8082")
    parser.add_argument("--node-folder", type=Path, default=Path.home() / ".polar/networks/1/volumes/lnd/bob")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    certificate = args.node_folder / "tls.cert"
    macaroon = args.node_folder / "data/chain/bitcoin/regtest/admin.macaroon"
    try:
        context = ssl.create_default_context(cafile=str(certificate))
        with httpx.Client(verify=context, trust_env=False, timeout=10) as client:
            response = client.get(args.endpoint + "/v1/getinfo", headers={"Grpc-Metadata-macaroon": macaroon.read_bytes().hex()})
            response.raise_for_status()
            info = response.json()
        chains = info.get("chains", [])
        if len(chains) != 1 or chains[0].get("chain") != "bitcoin" or chains[0].get("network") != "regtest":
            raise ValueError("El nodo debe operar exclusivamente en Bitcoin regtest.")
        print(f"Nodo regtest confirmado: {info.get('alias')}; canales activos: {info.get('num_active_channels')}", flush=True)
    except (OSError, httpx.HTTPError, ValueError) as exc:
        # Never print requests, headers or credentials.
        print(f"No se pudo verificar bob: {type(exc).__name__}. Revisa Polar, la dirección REST y los archivos TLS/macaroon.", file=sys.stderr)
        return 1
    if args.check_only:
        return 0

    root = Path(__file__).resolve().parents[1]
    data = root / ".local/lnbits-regtest/data"
    for folder in (data, data / "logs", data / "wasm_extensions"):
        folder.mkdir(parents=True, exist_ok=True)
    os.environ.update({
        "HOST": "127.0.0.1", "PORT": "5001", "AUTH_HTTPS_ONLY": "false",
        "LNBITS_ADMIN_UI": "true", "LNBITS_BACKEND_WALLET_CLASS": "LndRestWallet",
        "LNBITS_ALLOWED_FUNDING_SOURCES": '["LndRestWallet"]',
        "LNBITS_DATA_FOLDER": str(data), "LNBITS_DATABASE_URL": "",
        "LNBITS_EXTENSIONS_DEFAULT_INSTALL": "[]",
        "LNBITS_SITE_TITLE": "BTC.EDU · regtest",
        "LNBITS_SITE_TAGLINE": "Red local de prueba con Polar",
        "LND_REST_ENDPOINT": args.endpoint, "LND_REST_CERT": str(certificate),
        "LND_REST_MACAROON": str(macaroon), "LND_REST_MACAROON_ENCRYPTED": "",
        "LND_REST_ROUTE_HINTS": "true", "BUNDLE_ASSETS": "true",
    })
    os.chdir(root / ".local/lnbits")
    # Use the installed package while retaining a separate database and auth key.
    sys.path.insert(0, str(Path.cwd()))
    import uvicorn
    uvicorn.run("lnbits.__main__:app", host="127.0.0.1", port=5001, loop="asyncio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

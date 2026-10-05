import re
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx
from django.conf import settings


class ProviderUnavailable(Exception):
    """An unknown outcome never means unpaid or authorizes another emission."""


@dataclass(frozen=True)
class ProviderInvoice:
    payment_hash: str
    payment_request: str


@dataclass(frozen=True)
class ProviderStatus:
    paid: bool
    amount_msat: int
    payment_hash: str
    failed: bool = False


class LNbitsGateway:
    def __init__(self, transport=None):
        parsed = urlsplit(settings.LNBITS_URL)
        if not settings.COMMERCE_SIMULATION or parsed.hostname != "127.0.0.1" or parsed.scheme != "http" or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise ProviderUnavailable("La simulación requiere LNbits local.")
        if not settings.LNBITS_INVOICE_KEY or not settings.LNBITS_PAYER_KEY or not settings.LNBITS_ADMIN_TOKEN:
            raise ProviderUnavailable("Falta preparar el proveedor de prueba.")
        self.client = httpx.Client(base_url=settings.LNBITS_URL, timeout=8, trust_env=False, follow_redirects=False, transport=transport)

    def request(self, method, path, key=None, **kwargs):
        headers = {"X-Api-Key": key or settings.LNBITS_INVOICE_KEY}
        try:
            response = self.client.request(method, path, headers=headers, **kwargs)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError
            return data
        except (httpx.HTTPError, ValueError):
            raise ProviderUnavailable("No pudimos confirmar la respuesta del proveedor. Conservamos la factura para conciliarla.") from None

    def ensure_fake_wallet(self):
        try:
            response = self.client.get("/admin/api/v1/settings", headers={"Authorization": "Bearer " + settings.LNBITS_ADMIN_TOKEN})
            response.raise_for_status()
            data = response.json()
            if data.get("lnbits_backend_wallet_class") != "FakeWallet":
                raise ProviderUnavailable("Solo se permiten fondos ficticios de FakeWallet.")
        except (httpx.HTTPError, ValueError, AttributeError):
            raise ProviderUnavailable("No pudimos verificar la fuente de fondos ficticios.") from None

    def parse_invoice(self, data):
        payment_hash = data.get("payment_hash", "")
        payment_request = data.get("bolt11", "")
        if not isinstance(payment_hash, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", payment_hash) or not isinstance(payment_request, str) or not payment_request.startswith("ln"):
            raise ProviderUnavailable("El proveedor no devolvió una factura válida.")
        return ProviderInvoice(payment_hash.lower(), payment_request)

    def create(self, invoice):
        self.ensure_fake_wallet()
        data = self.request("POST", "/api/v1/payments", json={"out": False, "amount": invoice.amount_sats,
            "memo": f"BTC.EDU factura {invoice.pk}", "expiry": 900, "external_id": str(invoice.pk)})
        return self.parse_invoice(data)

    def recover(self, invoice):
        data = self.request("GET", "/api/v1/payments/paginated", params={"external_id": str(invoice.pk), "limit": 2})
        rows = data.get("data", [])
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise ProviderUnavailable("No pudimos confirmar la emisión original.")
        matches = [payment for payment in rows if payment.get("external_id") == str(invoice.pk) and payment.get("amount") == invoice.amount_sats * 1000]
        if len(matches) != 1:
            return None
        return self.parse_invoice(matches[0])

    def status(self, invoice):
        data = self.request("GET", "/api/v1/payments/" + invoice.payment_hash)
        details = data.get("details", {})
        if not isinstance(details, dict) or details.get("payment_hash") != invoice.payment_hash or type(details.get("amount")) is not int:
            raise ProviderUnavailable("La respuesta no corresponde a esta factura y su wallet.")
        return ProviderStatus(data.get("paid") is True, details["amount"], invoice.payment_hash, data.get("status") == "failed")

    def simulate(self, invoice):
        self.ensure_fake_wallet()
        self.request("POST", "/api/v1/payments", key=settings.LNBITS_PAYER_KEY, json={"out": True, "bolt11": invoice.payment_request})

    def close(self):
        self.client.close()

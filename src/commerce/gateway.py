"""LNbits client.

Only a local, simulated provider is accepted: http://127.0.0.1 with FakeWallet or LND regtest. Every
unexpected response becomes ProviderUnavailable.
"""
import re
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx
from django.conf import settings
from django.utils.translation import gettext


class ProviderUnavailable(Exception):
    """An unknown outcome never means unpaid or authorizes another emission."""


@dataclass(frozen=True)
class ProviderInvoice:
    """Payment request returned by the provider for an invoice."""
    payment_hash: str
    payment_request: str


@dataclass(frozen=True)
class ProviderStatus:
    """Payment state reported by the provider for one payment hash."""
    paid: bool
    amount_msat: int
    payment_hash: str
    failed: bool = False


class LNbitsGateway:
    """Thin wrapper around the LNbits REST API.

    Creates invoices, checks payment status, simulates payments and sends refunds.
    """
    def __init__(self, transport=None):
        parsed = urlsplit(settings.LNBITS_URL)
        if not settings.COMMERCE_SIMULATION or parsed.hostname != "127.0.0.1" or parsed.scheme != "http" or parsed.username or parsed.password or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
            raise ProviderUnavailable(gettext("El servicio de pagos no está disponible en este entorno."))
        if settings.COMMERCE_PAYMENT_MODE not in ("fake", "regtest"):
            raise ProviderUnavailable(gettext("El modo de pago no está disponible."))
        if not settings.LNBITS_INVOICE_KEY or not settings.LNBITS_ADMIN_TOKEN or (settings.COMMERCE_PAYMENT_MODE == "fake" and not settings.LNBITS_PAYER_KEY):
            raise ProviderUnavailable(gettext("El servicio de pagos no está disponible. Inténtalo más tarde."))
        self.client = httpx.Client(base_url=settings.LNBITS_URL, timeout=8, trust_env=False, follow_redirects=False, transport=transport)

    def request(self, method, path, key=None, **kwargs):
        """Send an authenticated request and return its JSON object.

        Any HTTP or format error raises ProviderUnavailable.
        """
        headers = {"X-Api-Key": key or settings.LNBITS_INVOICE_KEY}
        try:
            response = self.client.request(method, path, headers=headers, **kwargs)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError
            return data
        except (httpx.HTTPError, ValueError):
            raise ProviderUnavailable(gettext("No pudimos confirmar el estado del pago. Consulta esta misma factura antes de volver a pagar.")) from None

    def ensure_backend(self):
        """Confirm LNbits runs the expected wallet backend before moving funds."""
        try:
            response = self.client.get("/admin/api/v1/settings", headers={"Authorization": "Bearer " + settings.LNBITS_ADMIN_TOKEN})
            response.raise_for_status()
            data = response.json()
            expected = "LndRestWallet" if settings.COMMERCE_PAYMENT_MODE == "regtest" else "FakeWallet"
            if data.get("lnbits_backend_wallet_class") != expected:
                raise ProviderUnavailable(gettext("El servicio de pagos no está disponible en este entorno."))
        except (httpx.HTTPError, ValueError, AttributeError):
            raise ProviderUnavailable(gettext("No pudimos verificar el servicio de pagos. Inténtalo más tarde.")) from None

    def parse_invoice(self, data):
        """Validate the payment hash and BOLT11 request returned by LNbits."""
        payment_hash = data.get("payment_hash", "")
        payment_request = data.get("bolt11", "")
        if not isinstance(payment_hash, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", payment_hash) or not isinstance(payment_request, str) or not payment_request.startswith("ln"):
            raise ProviderUnavailable(gettext("El proveedor no devolvió una factura válida."))
        if settings.COMMERCE_PAYMENT_MODE == "regtest" and not payment_request.lower().startswith("lnbcrt"):
            raise ProviderUnavailable(gettext("El proveedor no devolvió una factura de regtest."))
        return ProviderInvoice(payment_hash.lower(), payment_request)

    def create(self, invoice):
        """Create an incoming payment that expires after 15 minutes, tagged with the invoice id."""
        self.ensure_backend()
        data = self.request("POST", "/api/v1/payments", json={"out": False, "amount": invoice.amount_sats,
            "memo": getattr(invoice, "memo", (gettext('BTC.EDU factura %(pk)s') % {"pk": invoice.pk})), "expiry": 900, "external_id": str(invoice.pk)})
        return self.parse_invoice(data)

    def recover(self, invoice):
        """Find the payment created earlier for this invoice.

        Returns None when it cannot be identified exactly.
        """
        data = self.request("GET", "/api/v1/payments/paginated", params={"external_id": str(invoice.pk), "limit": 2})
        rows = data.get("data", [])
        if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
            raise ProviderUnavailable(gettext("No pudimos confirmar la emisión original."))
        matches = [payment for payment in rows if payment.get("external_id") == str(invoice.pk) and payment.get("amount") == invoice.amount_sats * 1000]
        if len(matches) != 1:
            return None
        return self.parse_invoice(matches[0])

    def status(self, invoice):
        """Current status of the invoice payment, checked against its hash."""
        data = self.request("GET", "/api/v1/payments/" + invoice.payment_hash)
        details = data.get("details", {})
        if not isinstance(details, dict) or details.get("payment_hash") != invoice.payment_hash or type(details.get("amount")) is not int:
            raise ProviderUnavailable(gettext("La respuesta no corresponde a esta factura y su wallet."))
        return ProviderStatus(data.get("paid") is True, details["amount"], invoice.payment_hash, data.get("status") == "failed")

    def simulate(self, invoice):
        """Pay the invoice from the FakeWallet payer; regtest invoices are paid from a wallet."""
        if settings.COMMERCE_PAYMENT_MODE != "fake":
            raise ProviderUnavailable(gettext("Paga esta factura desde tu wallet de prueba."))
        self.ensure_backend()
        self.request("POST", "/api/v1/payments", key=settings.LNBITS_PAYER_KEY, json={"out": True, "bolt11": invoice.payment_request})

    def pay(self, payment_request):
        """Send a refund from the receiving wallet; an unknown outcome is never retried here."""
        if not settings.LNBITS_REFUND_KEY:
            raise ProviderUnavailable(gettext("Los reembolsos no están configurados en este entorno."))
        self.ensure_backend()
        data = self.request("POST", "/api/v1/payments", key=settings.LNBITS_REFUND_KEY, json={"out": True, "bolt11": payment_request})
        payment_hash = data.get("payment_hash", "")
        if not isinstance(payment_hash, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", payment_hash):
            raise ProviderUnavailable(gettext("No pudimos confirmar el pago del reembolso."))
        return payment_hash.lower()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

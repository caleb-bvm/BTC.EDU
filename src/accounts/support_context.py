"""Private, server-derived references for platform support; no purchase or access writes."""
from uuid import UUID

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext

from commerce.models import Entitlement, Invoice


def verified_support_context(user, values):
    invoice_id = values.get("factura", "").strip()
    resource_id = values.get("recurso", "").strip()
    if not invoice_id and not resource_id:
        return None
    if not user.is_authenticated or not user.is_active or user.account_type != "student" or invoice_id and resource_id:
        raise Http404
    if invoice_id:
        try:
            invoice_key = UUID(invoice_id)
        except (ValueError, TypeError, AttributeError):
            raise Http404 from None
        invoice = get_object_or_404(Invoice.objects.select_related("order"), pk=invoice_key, buyer=user)
        if invoice.order_id and invoice.order.buyer_id != user.pk:
            raise Http404
        context = {"field": "factura", "id": str(invoice.pk), "reference_label": gettext("Factura"), "title": invoice.title,
                   "return_url": reverse("invoice-detail", args=[invoice.pk]), "return_label": gettext("Volver a la compra"), "heading": gettext("Ayuda con tu compra"),
                   "order_id": str(invoice.order_id) if invoice.order_id else ""}
    else:
        if not resource_id.isdigit() or len(resource_id) > 19 or not 0 < int(resource_id) <= 2**63 - 1:
            raise Http404
        right = get_object_or_404(Entitlement.objects.active().select_related("resource"), resource_id=resource_id, buyer=user)
        context = {"field": "recurso", "id": str(right.resource_id), "reference_label": gettext("Recurso adquirido"), "title": right.resource.title,
                   "return_url": reverse("purchased-resource", args=[right.resource_id]), "return_label": gettext("Volver al recurso"), "heading": gettext("Ayuda con tu acceso")}
    order_reference = gettext("Pedido: %(order_id)s") % {"order_id": context["order_id"]} + "\n" if context.get("order_id") else ""
    context["body_prefix"] = (gettext('Referencia comprobada: %(reference_label)s %(id)s\n%(order_reference)sContenido: %(title)s\n\nConsulta:\n') % {"reference_label": context["reference_label"], "id": context["id"], "order_reference": order_reference, "title": context["title"]})
    return context

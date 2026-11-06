"""Pending refund requests for the administration home page."""
from django import template
from django.db.models import Min

from commerce.models import Refund

register = template.Library()


@register.simple_tag(takes_context=True)
def pending_refunds(context):
    """Open requests and the earliest answer deadline, only for reviewers."""
    user = context["request"].user
    if not user.has_perm("commerce.decide_refund"):
        return None
    pending = Refund.objects.filter(status__in=(Refund.Status.REQUESTED, Refund.Status.REVIEW))
    oldest = pending.aggregate(first=Min("created_at"))["first"]
    if oldest is None:
        return None
    return {"count": pending.count(), "respond_by": Refund(created_at=oldest).respond_by}

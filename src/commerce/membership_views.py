"""Membership plan page and membership payment views."""
from io import BytesIO

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from core.content_translation import translate_content

from .gateway import ProviderUnavailable
from .membership import (
    available_plans,
    check_membership,
    create_membership_payment,
    membership_until,
)
from .models import MembershipPayment, Refund
from .views import student_required


@require_GET
@never_cache
def membership(request):
    from content.catalog import catalog_context
    cards = catalog_context({"acceso": "membresia"})["all_cards"]
    groups = {}
    for card in cards:
        category = card["item"].topic.category if card["item"].topic else None
        groups.setdefault(translate_content(category.name) if category else gettext("Por descubrir"), []).append(card)
    student = request.user.is_authenticated and request.user.account_type == "student"
    history = MembershipPayment.objects.filter(member=request.user).select_related("plan")[:12] if student else []
    return render(request, "commerce/membership.html", {
        "plans": available_plans(), "until": membership_until(request.user), "student": student,
        "history": history, "groups": sorted(groups.items()), "course_count": len(cards),
        "active": "membership",
    })


@student_required
@require_POST
def membership_join(request):
    plan = get_object_or_404(available_plans(), pk=request.POST.get("plan") or 0)
    try:
        payment = create_membership_payment(request.user, plan)
    except (ValidationError, PermissionDenied) as exc:
        messages.warning(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else gettext("Entra con tu cuenta de estudiante."))
        return redirect("membership")
    try:
        check_membership(payment)
    except ProviderUnavailable:
        messages.warning(request, gettext("No pudimos preparar el pago. Actualiza el estado de este mismo pago."))
    return redirect("membership-payment", pk=payment.pk)


@student_required
@require_GET
def membership_payment(request, pk):
    payment = get_object_or_404(MembershipPayment.objects.select_related("plan"), pk=pk, member=request.user)
    if payment.status == "pending":
        try:
            payment = check_membership(payment)
        except ProviderUnavailable:
            payment.refresh_from_db()
            messages.warning(request, gettext("No pudimos comprobar el pago. Usa Actualizar estado para volver a intentarlo."))
    from .refunds import membership_refund_blocker
    refund = getattr(payment, "refund", None)
    return render(request, "commerce/membership_payment.html", {
        "payment": payment, "active": "membership", "until": membership_until(request.user), "refund": refund,
        "can_refund": payment.status == "paid" and not membership_refund_blocker(payment, request.user),
        "can_claim": payment.status == "paid" and not membership_refund_blocker(payment, request.user, claim=True),
        "can_pay": payment.status == "pending" and payment.issue_state == "ready" and payment.expires_at > timezone.now(),
        "external_payment": settings.COMMERCE_PAYMENT_MODE == "regtest",
    })


@student_required
@require_GET
def membership_payment_status(request, pk):
    payment = get_object_or_404(MembershipPayment, pk=pk, member=request.user)
    try:
        payment = check_membership(payment)
    except ProviderUnavailable:
        return JsonResponse({"error": gettext("No pudimos comprobar el pago.")}, status=503)
    return JsonResponse({"status": payment.status, "incident": ""})


@student_required
@require_GET
def membership_payment_qr(request, pk):
    payment = get_object_or_404(MembershipPayment, pk=pk, member=request.user)
    if (settings.COMMERCE_PAYMENT_MODE != "regtest" or payment.status != "pending" or payment.issue_state != "ready"
            or payment.expires_at <= timezone.now() or not payment.payment_request.lower().startswith("lnbcrt")):
        raise Http404
    output = BytesIO()
    qrcode.make(payment.payment_request.upper(), image_factory=qrcode.image.svg.SvgPathImage, border=4).save(output)
    response = HttpResponse(output.getvalue(), content_type="image/svg+xml")
    response["Cache-Control"] = "private, no-store"
    return response


@student_required
@require_POST
def membership_payment_action(request, pk):
    payment = get_object_or_404(MembershipPayment, pk=pk, member=request.user)
    try:
        simulate = request.POST.get("action") == "pay"
        if simulate and settings.COMMERCE_PAYMENT_MODE != "fake":
            raise ProviderUnavailable
        payment = check_membership(payment, simulate=simulate)
        if payment.status == "paid":
            messages.success(request, (gettext('Tu membresía está activa hasta el %(localtime)s.') % {"localtime": f"{timezone.localtime(payment.ends_at):%d/%m/%Y}"}))
    except ProviderUnavailable:
        messages.warning(request, gettext("No pudimos comprobar el pago. Actualiza este mismo pago antes de volver a pagar."))
    return redirect("membership-payment", pk=pk)


@student_required
@require_http_methods(["GET", "POST"])
def membership_refund_request(request, pk, claim=False):
    from .feature_views import render_refund_request
    from .forms import RefundForm
    from .refunds import membership_refund_blocker, request_membership_refund
    payment = get_object_or_404(MembershipPayment.objects.select_related("plan"), pk=pk, member=request.user)
    blocker = membership_refund_blocker(payment, request.user, claim=claim)
    if blocker:
        messages.info(request, blocker)
        return redirect("membership-payment", pk=pk)
    form = RefundForm(request.POST if request.method == "POST" else None, amount=payment.amount_sats, claim=claim)
    if request.method == "POST" and form.is_valid():
        try:
            request_membership_refund(request.user, payment.pk, form.cleaned_data["reason"], form.cleaned_data["payment_request"],
                                      form.cleaned_data.get("kind", Refund.Kind.WITHDRAWAL))
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        else:
            messages.success(request, gettext("Recibimos tu solicitud. Te avisaremos cuando la revisemos."))
            return redirect("membership-payment", pk=pk)
    return render_refund_request(request, form, claim, gettext("Membresía · %(plan)s") % {"plan": payment.plan.name},
                                 payment.amount_sats, reverse("membership-payment", args=[pk]), "membership")

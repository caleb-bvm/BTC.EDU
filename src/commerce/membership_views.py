from io import BytesIO

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from .gateway import ProviderUnavailable
from .membership import (
    available_plans,
    check_membership,
    create_membership_payment,
    membership_until,
)
from .models import MembershipPayment
from .views import student_required


@require_GET
@never_cache
def membership(request):
    from content.catalog import catalog_context
    cards = catalog_context({"acceso": "membresia"})["all_cards"]
    groups = {}
    for card in cards:
        category = card["item"].topic.category if card["item"].topic else None
        groups.setdefault(category.name if category else "Por descubrir", []).append(card)
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
        messages.warning(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else "Entra con tu cuenta de estudiante.")
        return redirect("membership")
    try:
        check_membership(payment)
    except ProviderUnavailable:
        messages.warning(request, "No pudimos preparar el pago. Actualiza el estado de este mismo pago.")
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
            messages.warning(request, "No pudimos comprobar el pago. Usa Actualizar estado para volver a intentarlo.")
    return render(request, "commerce/membership_payment.html", {
        "payment": payment, "active": "membership", "until": membership_until(request.user),
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
        return JsonResponse({"error": "No pudimos comprobar el pago."}, status=503)
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
            messages.success(request, f"Tu membresía está activa hasta el {timezone.localtime(payment.ends_at):%d/%m/%Y}.")
    except ProviderUnavailable:
        messages.warning(request, "No pudimos comprobar el pago. Actualiza este mismo pago antes de volver a pagar.")
    return redirect("membership-payment", pk=pk)

from datetime import timedelta
from io import BytesIO
from urllib.parse import urlencode

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from creators.views import creator_required

from .forms import CouponForm, RefundDecisionForm, RefundForm, TipForm
from .gateway import ProviderUnavailable
from .gifts import gift_for_token, redeem_gift
from .models import Coupon, Invoice, Refund, Tip
from .pricing import coupon_rows, normalize_code
from .refunds import (
    approve_refund,
    confirm_reviewed_refund,
    refund_blocker,
    reject_refund,
    request_refund,
    require_reviewer,
)
from .tips import TIP_PRESETS, check_tip, create_tip, creator_tip_summary, tip_recipient
from .views import student_required


@creator_required
@require_http_methods(["GET", "POST"])
def creator_coupons(request):
    now = timezone.localtime().replace(second=0, microsecond=0)
    form = CouponForm(request.POST if request.method == "POST" else None, actor=request.user,
                      initial={"starts_at": now, "expires_at": now + timedelta(days=14)})
    if request.method == "POST" and request.POST.get("action") == "deactivate":
        coupon = get_object_or_404(Coupon, pk=request.POST.get("coupon"), creator=request.user)
        Coupon.objects.filter(pk=coupon.pk).update(active=False)
        messages.success(request, f"Cupón {coupon.code} desactivado. Los pedidos anteriores conservan su precio.")
        return redirect("creator-coupons")
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        from content.models import Course
        course = get_object_or_404(Course, pk=data["course"], creator=request.user) if data["course"] else None
        try:
            Coupon.objects.create(creator=request.user, code=normalize_code(data["code"]), course=course,
                                  percent_off=data["value"] if data["kind"] == "percent" else None,
                                  amount_off_sats=data["value"] if data["kind"] == "amount" else None,
                                  starts_at=data["starts_at"], expires_at=data["expires_at"], max_uses=data["max_uses"])
        except (ValidationError, IntegrityError):
            form.add_error("code", "Ese código ya existe. Elige otro.")
        else:
            messages.success(request, "Cupón creado. Compártelo con tus estudiantes.")
            return redirect("creator-coupons")
    return render(request, "commerce/creator_coupons.html", {"form": form, "rows": coupon_rows(request.user)})


@never_cache
@require_http_methods(["GET", "POST"])
def gift_detail(request, token):
    gift = gift_for_token(token)
    if gift is None:
        raise Http404
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), reverse("login"))
        try:
            redeem_gift(request.user, token)
        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else "Entra con tu cuenta de estudiante para canjear el regalo.")
        else:
            messages.success(request, "Regalo canjeado. El contenido ya está en Mi aprendizaje.")
            return redirect("workspace")
        return redirect("gift-detail", token=token)
    is_buyer = request.user.is_authenticated and request.user.pk == gift.order.buyer_id
    lines = list(gift.order.lines.all())
    response = render(request, "commerce/gift.html", {
        "gift": gift, "lines": lines, "is_buyer": is_buyer,
        "share_url": request.build_absolute_uri(reverse("gift-detail", args=[gift.token])),
        "sender_name": gift.order.buyer.public_name,
        "signin_url": reverse("login") + "?" + urlencode({"next": request.get_full_path()}),
    })
    response["X-Robots-Tag"] = "noindex, nofollow"
    response["Referrer-Policy"] = "no-referrer"
    return response


def tip_target(request):
    from content.models import VersionLesson
    lesson = None
    value = request.POST.get("leccion") if request.method == "POST" else request.GET.get("leccion")
    if value:
        try:
            lesson = VersionLesson.objects.select_related("content", "chapter__version__course__creator").get(pk=int(value))
        except (ValueError, TypeError, VersionLesson.DoesNotExist):
            raise Http404 from None
        from content.access import content_access
        if not content_access(request.user, lesson).allowed:
            raise Http404
        return lesson.chapter.version.course.creator, lesson
    try:
        creator = get_user_model().objects.get(pk=int(request.POST.get("creador") if request.method == "POST" else request.GET.get("creador")))
    except (ValueError, TypeError, get_user_model().DoesNotExist):
        raise Http404 from None
    return creator, None


@student_required
@require_http_methods(["GET", "POST"])
def tip_create(request):
    creator, lesson = tip_target(request)
    if not tip_recipient(creator):
        raise Http404
    form = TipForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            tip = create_tip(request.user, creator, form.cleaned_data["amount"], form.cleaned_data["message"], lesson)
        except (ValidationError, PermissionDenied) as exc:
            form.add_error(None, " ".join(exc.messages) if isinstance(exc, ValidationError) else "Este educador no puede recibir propinas ahora.")
        else:
            try:
                check_tip(tip)
            except ProviderUnavailable:
                messages.warning(request, "No pudimos preparar el pago. Actualiza el estado de esta misma propina.")
            return redirect("tip-detail", pk=tip.pk)
    profile = getattr(creator, "creator_profile", None)
    return render(request, "commerce/tip_create.html", {"form": form, "creator": creator, "lesson": lesson,
                                                       "creator_name": profile.display_name if profile else "Educador",
                                                       "presets": TIP_PRESETS, "active": "purchases"})


@student_required
@require_GET
def tip_detail(request, pk):
    tip = get_object_or_404(Tip.objects.select_related("creator__creator_profile", "lesson__content", "lesson__chapter__version"), pk=pk, sender=request.user)
    if tip.status == "pending":
        try:
            tip = check_tip(tip)
        except ProviderUnavailable:
            tip.refresh_from_db()
            messages.warning(request, "No pudimos comprobar el pago. Usa Actualizar estado para volver a intentarlo.")
    lesson_link = ""
    if tip.lesson_id:
        from .journey import lesson_url
        lesson_link = lesson_url(tip.lesson)
    return render(request, "commerce/tip.html", {"tip": tip, "lesson_link": lesson_link, "active": "purchases",
                                                "can_pay": tip.status == "pending" and tip.issue_state == "ready" and tip.expires_at > timezone.now(),
                                                "external_payment": settings.COMMERCE_PAYMENT_MODE == "regtest"})


@student_required
@require_GET
def tip_status(request, pk):
    tip = get_object_or_404(Tip, pk=pk, sender=request.user)
    try:
        tip = check_tip(tip)
    except ProviderUnavailable:
        return JsonResponse({"error": "No pudimos comprobar el pago."}, status=503)
    return JsonResponse({"status": tip.status, "incident": ""})


@student_required
@require_GET
def tip_qr(request, pk):
    tip = get_object_or_404(Tip, pk=pk, sender=request.user)
    if (settings.COMMERCE_PAYMENT_MODE != "regtest" or tip.status != "pending" or tip.issue_state != "ready"
            or tip.expires_at <= timezone.now() or not tip.payment_request.lower().startswith("lnbcrt")):
        raise Http404
    output = BytesIO()
    qrcode.make(tip.payment_request.upper(), image_factory=qrcode.image.svg.SvgPathImage, border=4).save(output)
    response = HttpResponse(output.getvalue(), content_type="image/svg+xml")
    response["Cache-Control"] = "private, no-store"
    return response


@student_required
@require_POST
def tip_action(request, pk):
    tip = get_object_or_404(Tip, pk=pk, sender=request.user)
    try:
        simulate = request.POST.get("action") == "pay"
        if simulate and settings.COMMERCE_PAYMENT_MODE != "fake":
            raise ProviderUnavailable
        tip = check_tip(tip, simulate=simulate)
        if tip.status == "paid":
            messages.success(request, "Gracias. Tu propina llegó al educador.")
    except ProviderUnavailable:
        messages.warning(request, "No pudimos comprobar el pago. Actualiza esta misma propina antes de volver a pagar.")
    return redirect("tip-detail", pk=pk)


@student_required
@require_GET
def student_tips(request):
    tips = Tip.objects.filter(sender=request.user).select_related("creator__creator_profile", "lesson__content")
    return render(request, "commerce/tips.html", {"tips": Paginator(tips, 20).get_page(request.GET.get("pagina")), "active": "purchases"})


@creator_required
@require_GET
def creator_tips(request):
    summary = creator_tip_summary(request.user)
    return render(request, "commerce/creator_tips.html", {"summary": summary, "tips": Paginator(summary["recent"], 20).get_page(request.GET.get("pagina"))})


@student_required
@require_http_methods(["GET", "POST"])
def refund_request(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related("order", "offer", "purchase"), pk=pk, buyer=request.user)
    blocker = refund_blocker(invoice, request.user)
    if blocker:
        messages.info(request, blocker)
        return redirect("invoice-detail", pk=pk)
    form = RefundForm(request.POST if request.method == "POST" else None, amount=invoice.amount_sats)
    if request.method == "POST" and form.is_valid():
        try:
            request_refund(request.user, invoice.pk, form.cleaned_data["reason"], form.cleaned_data["payment_request"])
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        else:
            messages.success(request, "Recibimos tu solicitud. Te avisaremos cuando la revisemos.")
            return redirect("invoice-detail", pk=pk)
    return render(request, "commerce/refund_request.html", {"invoice": invoice, "form": form, "active": "purchases",
                                                           "refund_days": settings.COMMERCE_REFUND_DAYS})


@login_required(login_url="admin:login")
@never_cache
@require_http_methods(["GET", "POST"])
def refund_review(request, pk):
    require_reviewer(request.user)
    refund = get_object_or_404(Refund.objects.select_related("invoice", "buyer", "decided_by"), pk=pk)
    form = RefundDecisionForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            if refund.status == "review" and data.get("payment_hash"):
                confirm_reviewed_refund(request.user, refund, data["payment_hash"])
            elif data["decision"] == "approve":
                refund = approve_refund(request.user, refund, data.get("note", ""))
                if refund.status == "review":
                    messages.warning(request, "No pudimos confirmar el pago. Revisa la wallet antes de volver a intentarlo.")
            else:
                reject_refund(request.user, refund, data["note"])
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        else:
            messages.success(request, "Decisión registrada.")
            return redirect("refund-review", pk=pk)
    return render(request, "commerce/refund_review.html", {"refund": refund, "form": form, "reviewer": True})

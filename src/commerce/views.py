from functools import wraps
from io import BytesIO
from urllib.parse import urlencode

import qrcode
import qrcode.image.svg
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from creators.views import creator_required

from .catalog import available, missing_alternatives, ownership, public_version
from .forms import OfferForm, OfferReviewForm
from .gateway import ProviderUnavailable
from .journey import (
    destination,
    invoice_access_conflict,
    invoice_destination,
    lesson_url,
    offer_url,
    order_content,
    public_destination,
    return_lesson,
)
from .models import Invoice, Offer, OrderLine
from .offers import (
    archive_offer,
    create_offer,
    missing_individuals,
    review_offer,
    submit_offer,
)
from .reservations import needs_reservation
from .services import (
    ensure_emitted,
    expire_invoice,
    reconcile,
    reserve_invoice,
    simulate_payment,
)

INVOICE_RELATIONS = ("offer__course_version__course", "offer__resource", "offer__lesson__content",
                     "offer__lesson__chapter__version__course", "return_lesson__content",
                     "return_lesson__chapter__version__course", "purchase", "order__cart", "refund")


def invoice_queryset():
    lines = OrderLine.objects.select_related(
        "creator__creator_profile", "offer__course_version__course", "offer__resource",
        "offer__lesson__content", "offer__lesson__chapter__version__course",
        "return_lesson__content", "return_lesson__chapter__version__course",
    ).order_by("position", "pk")
    return Invoice.objects.select_related(*INVOICE_RELATIONS).prefetch_related(Prefetch("order__lines", queryset=lines))


def student_required(view):
    @login_required
    @never_cache
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.user.account_type != "student":
            return redirect_to_login(request.get_full_path(), reverse("login"))
        return view(request, *args, **kwargs)
    return wrapped


@creator_required
@require_http_methods(["GET", "POST"])
def creator_offers(request):
    from content.models import Course, Material, VersionAttachment, Video
    course = None
    resource = None
    resource_kind = ""
    course_id = request.GET.get("curso") or request.POST.get("curso")
    resource_id = request.GET.get("recurso") or request.POST.get("recurso")
    if course_id:
        try:
            course_id = int(course_id)
        except (TypeError, ValueError):
            course_id = 0
        if not 0 < course_id <= 9223372036854775807:
            from django.http import Http404
            raise Http404
        course = get_object_or_404(Course.objects.select_related("current_version"), pk=course_id, creator=request.user)
    if resource_id:
        from django.http import Http404
        kind = request.GET.get("tipo") or request.POST.get("tipo")
        model, resource_kind = {"video": (Video, "videos"), "videos": (Video, "videos"),
                                "material": (Material, "materiales"), "materiales": (Material, "materiales")}.get(kind, (None, ""))
        try:
            resource_id = int(resource_id)
        except (TypeError, ValueError):
            resource_id = 0
        if course or model is None or not 0 < resource_id <= 9223372036854775807:
            raise Http404
        resource = get_object_or_404(model.objects.select_related("revision"), pk=resource_id, creator=request.user)
    form = OfferForm(request.POST if request.method == "POST" else None, actor=request.user, course=course, resource=resource)
    targets = {key: label for key, label in form.fields["target"].choices if key}
    initial_target = request.GET.get("objetivo")
    if initial_target in targets:
        form.initial["target"] = initial_target
    elif course and course.current_version_id and f"course:{course.current_version_id}" in targets:
        form.initial["target"] = f"course:{course.current_version_id}"
    elif resource and resource.revision_id and f"resource:{resource.revision_id}" in targets:
        form.initial["target"] = f"resource:{resource.revision_id}"
    if request.method == "POST" and form.is_valid():
        try:
            offer = create_offer(request.user, form.cleaned_data["target"], form.cleaned_data["title"], form.cleaned_data["amount_sats"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Oferta preparada. Comprueba lo incluido y envíala a revisión.")
            return redirect("creator-offer", pk=offer.pk)
    offers = Offer.objects.filter(creator=request.user).select_related("course_version__course", "resource")
    if course:
        attached = VersionAttachment.objects.filter(lesson__chapter__version__course=course).values("resource_id")
        offers = offers.filter(Q(course_version__course=course) | Q(resource_id__in=attached))
    elif resource:
        offers = offers.filter(resource__resource_key=resource.revision.resource_key) if resource.revision_id else offers.none()
    query = {"curso": course.pk} if course else {}
    if resource:
        query.update({"recurso": resource.pk, "tipo": resource_kind})
    if initial_target in targets:
        query["objetivo"] = initial_target
    page_query = urlencode(query)
    return render(request, "commerce/creator_offers.html", {"form": form, "offers": Paginator(offers, 20).get_page(request.GET.get("pagina")), "selected_course": course, "selected_resource": resource, "resource_kind": resource_kind, "has_targets": bool(targets), "page_query": page_query})


@creator_required
@require_http_methods(["GET", "POST"])
def creator_offer(request, pk):
    offer = get_object_or_404(Offer.objects.select_related("course_version__course", "resource", "creator"), pk=pk, creator=request.user)
    if request.method == "POST":
        try:
            if request.POST.get("action") == "submit":
                submit_offer(request.user, offer)
                messages.success(request, "Oferta enviada a revisión.")
            elif request.POST.get("action") == "archive":
                archive_offer(request.user, offer)
                messages.success(request, "Oferta retirada. Las compras anteriores se conservan.")
            else:
                messages.error(request, "Elige una acción disponible.")
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
        return redirect("creator-offer", pk=pk)
    from content.models import VersionLesson
    missing = missing_individuals(offer) if offer.kind in ("course", "chapter") and offer.status != "archived" and public_version(offer.course_version) else []
    dependencies = []
    for item in missing:
        lesson = VersionLesson.objects.filter(chapter__version=offer.course_version, content=item.resource).first() if item.resource.kind == "text" else None
        target = f"lesson:{lesson.pk}" if lesson else f"resource:{item.resource_id}"
        query = {"objetivo": target}
        if offer.course_version_id:
            query["curso"] = offer.course_version.course_id
        dependencies.append({"item": item, "url": reverse("creator-offers") + "?" + urlencode(query)})
    return render(request, "commerce/creator_offer.html", {"offer": offer, "items": offer.items.select_related("resource"), "missing": missing, "dependencies": dependencies, "offer_live": available(offer)})


@login_required(login_url="creator-login")
@never_cache
@require_http_methods(["GET", "POST"])
def offer_review(request, pk):
    if not request.user.is_active or not request.user.is_staff or not request.user.has_perm("commerce.change_offer"):
        raise PermissionDenied
    offer = get_object_or_404(Offer.objects.select_related("course_version", "creator"), pk=pk)
    form = OfferReviewForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            review_offer(request.user, offer, form.cleaned_data["decision"] == "approve", form.cleaned_data["feedback"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Decisión registrada.")
            return redirect("offer-review", pk=pk)
    return render(request, "commerce/review.html", {"offer": offer, "form": form, "items": offer.items.select_related("resource"), "reviewer": True})


@require_GET
@never_cache
def offer_detail(request, pk):
    offer = get_object_or_404(Offer.objects.select_related("creator", "course_version__course", "resource"), pk=pk)
    if not available(offer):
        from django.http import Http404
        raise Http404
    state = ownership(request.user, offer)
    chosen_lesson = return_lesson(offer, request.GET.get("leccion"))
    alternatives = missing_alternatives(request.user, offer) if state == "partial" else []
    for alternative in alternatives:
        alternative.purchase_url = offer_url(alternative, return_lesson(alternative, chosen_lesson.pk) if chosen_lesson else None)
    next_destination = destination(request.user, offer, chosen_lesson)
    from .pricing import upgrade_quote
    upgrade = upgrade_quote(request.user, offer) if state == "partial" else None
    from core.telemetry import offer_views
    offer_views(request, [offer])
    gift_url = reverse("direct-checkout", args=[offer.pk]) + "?regalo=1"
    return render(request, "commerce/offer.html", {"offer": offer, "items": offer.items.select_related("resource"), "ownership": state, "alternatives": alternatives,
                                                   "upgrade": upgrade, "gift_url": gift_url, "destination": next_destination["url"], "destination_label": next_destination["label"], "selected_lesson": chosen_lesson, "return_to_content": lesson_url(chosen_lesson) if chosen_lesson else public_destination(offer), "purchase_url": offer_url(offer, chosen_lesson), "inventory_count": offer.items.count()})


@student_required
@require_POST
def checkout(request, pk):
    offer = get_object_or_404(Offer.objects.select_related("course_version__course", "resource"), pk=pk)
    chosen_lesson = return_lesson(offer, request.POST.get("leccion"))
    review_url = offer_url(offer, chosen_lesson)
    if settings.ACCOUNT_REQUIRE_VERIFIED_EMAIL and not request.user.email_verified_at:
        request.session["account_verify_destination"] = review_url
        messages.info(request, "Confirma tu correo antes de comprar para conservar una vía de recuperación.")
        return redirect("student-account-security")
    try:
        from core.telemetry import session_id
        invoice = reserve_invoice(request.user, offer.pk, activity_session=session_id(request), return_lesson_id=request.POST.get("leccion"))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect(review_url)
    try:
        ensure_emitted(invoice)
    except ProviderUnavailable:
        messages.warning(request, "No pudimos preparar el pago. Actualiza el estado de esta misma factura para continuar.")
    return redirect("invoice-detail", pk=invoice.pk)


@student_required
@require_GET
def invoice_detail(request, pk):
    invoice = get_object_or_404(invoice_queryset(), pk=pk, buyer=request.user)
    if invoice.status != "paid":
        try:
            invoice = reconcile(invoice)
        except ProviderUnavailable:
            invoice.refresh_from_db()
            messages.warning(request, "No pudimos comprobar el pago. Usa Actualizar estado para volver a intentarlo.")
    blocked = invoice_access_conflict(invoice, request.user)
    next_destination = invoice_destination(invoice, request.user)
    lines = order_content(invoice, request.user)
    chosen_lesson = return_lesson(invoice.offer, invoice.return_lesson_id) if invoice.offer_id else None
    if invoice.order_id and len(lines) == 1:
        chosen_lesson = lines[0]["line"].return_lesson
    if chosen_lesson and chosen_lesson.content_id not in {item["resource_id"] for item in invoice.inventory}:
        chosen_lesson = None
    from learning.services import can_visit_version
    back_to_lesson = lesson_url(chosen_lesson) if chosen_lesson and can_visit_version(request.user, chosen_lesson.chapter.version) else ""
    needs_review = invoice.evidence is not None if hasattr(invoice, "evidence") else False
    retry_url = ""
    payment_uncertain = invoice.status in ("expired", "failed") and needs_reservation(invoice)
    if not needs_review and not payment_uncertain:
        if invoice.order_id:
            if invoice.order.cart_id:
                retry_url = reverse("cart")
            elif len(lines) == 1:
                from .cart import replacement_offer
                line = lines[0]["line"]
                retry_offer = line.offer if available(line.offer) else replacement_offer(line.offer)
                if retry_offer:
                    retry_lesson = return_lesson(retry_offer, line.return_lesson_id)
                    retry_url = reverse("direct-checkout", args=[retry_offer.pk])
                    if retry_lesson:
                        retry_url += "?" + urlencode({"leccion": retry_lesson.pk})
        else:
            retry_offer = next((offer for offer in Offer.objects.filter(logical_key=invoice.logical_key, status="active").select_related("creator", "course_version__course", "resource") if available(offer)), None)
            retry_lesson = return_lesson(retry_offer, invoice.return_lesson_id) if retry_offer else None
            retry_url = offer_url(retry_offer, retry_lesson) if retry_offer else ""
    from .refunds import refund_blocker
    refund = getattr(invoice, "refund", None)
    can_refund = invoice.status == "paid" and refund is None and not refund_blocker(invoice, request.user)
    return render(request, "commerce/invoice.html", {
        "refund": refund, "can_refund": can_refund, "gift": invoice.order.gift if invoice.order_id else False,
        "invoice": invoice, "order_lines": lines, "destination": next_destination["url"],
        "destination_label": next_destination["label"], "destination_title": next_destination["title"],
        "selected_lesson": chosen_lesson, "return_to_content": back_to_lesson, "retry_url": retry_url,
        "can_pay": invoice.status == "pending" and invoice.issue_state == "ready" and not blocked and not invoice.incident,
        "external_payment": settings.COMMERCE_PAYMENT_MODE == "regtest", "purchase_blocked": blocked,
        "needs_review": needs_review and invoice.status != "paid",
        "payment_uncertain": payment_uncertain,
        "support_url": reverse("student-account-support") + "?" + urlencode({"factura": invoice.pk}),
        "active": "purchases",
    })


@student_required
@require_GET
def invoice_qr(request, pk):
    from django.http import Http404
    from django.utils import timezone
    invoice = get_object_or_404(Invoice.objects.select_related("offer", "order"), pk=pk, buyer=request.user)
    if (settings.COMMERCE_PAYMENT_MODE != "regtest" or invoice.status != "pending"
            or invoice.issue_state != "ready" or invoice.incident or invoice.expires_at <= timezone.now()
            or invoice_access_conflict(invoice, request.user)
            or not invoice.payment_request.lower().startswith("lnbcrt")):
        raise Http404
    output = BytesIO()
    qrcode.make(invoice.payment_request.upper(), image_factory=qrcode.image.svg.SvgPathImage, border=4).save(output)
    response = HttpResponse(output.getvalue(), content_type="image/svg+xml")
    response["Cache-Control"] = "private, no-store"
    return response


@student_required
@require_GET
def invoice_status(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, buyer=request.user)
    try:
        invoice = reconcile(invoice)
    except ProviderUnavailable:
        return JsonResponse({"error": "No pudimos comprobar el pago. Usa Actualizar estado para volver a intentarlo."}, status=503)
    return JsonResponse({"status": invoice.status, "incident": invoice.incident})


@student_required
@require_POST
def invoice_action(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, buyer=request.user)
    try:
        if request.POST.get("action") in ("pay", "simulate"):
            if settings.COMMERCE_PAYMENT_MODE != "fake":
                raise ProviderUnavailable("Abre el pago o escanea el QR para pagar. Después, actualiza el estado de esta misma factura.")
            invoice = simulate_payment(request.user, invoice)
        else:
            invoice = reconcile(invoice)
        if invoice.status == "paid":
            messages.success(request, "Compra confirmada. Tu contenido ya está disponible.")
    except (ProviderUnavailable, ValidationError) as exc:
        messages.warning(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else "No pudimos comprobar el pago. Actualiza esta misma factura antes de volver a pagar.")
    return redirect("invoice-detail", pk=pk)


@student_required
@require_GET
def purchases(request):
    from django.utils import timezone
    invoices = Invoice.objects.filter(buyer=request.user)
    for invoice_id in invoices.filter(status="pending", expires_at__lte=timezone.now()).values_list("pk", flat=True):
        expire_invoice(invoice_id)
    counts = {item["status"]: item["total"] for item in invoices.values("status").annotate(total=Count("pk"))}
    filters = [("all", "Todas", sum(counts.values())), ("paid", "Confirmadas", counts.get("paid", 0)),
               ("pending", "Pendientes", counts.get("pending", 0)),
               ("closed", "Sin completar", counts.get("expired", 0) + counts.get("failed", 0))]
    selected = request.GET.get("estado", "all")
    if selected not in {key for key, _, _ in filters}:
        selected = "all"
    if selected == "closed":
        invoices = invoices.filter(status__in=("expired", "failed"))
    elif selected != "all":
        invoices = invoices.filter(status=selected)
    page = Paginator(invoice_queryset().filter(pk__in=invoices.values("pk")), 20).get_page(request.GET.get("pagina"))
    for invoice in page:
        invoice.open_content = invoice_destination(invoice, request.user)
        invoice.item_count = len(invoice.inventory)
        invoice.order_content = order_content(invoice, request.user)
        invoice.product_count = len(invoice.order_content) if invoice.order_id else 1
    return render(request, "commerce/purchases.html", {"invoices": page, "filters": filters, "selected_status": selected,
                                                       "page_query": urlencode({"estado": selected}), "active": "purchases"})

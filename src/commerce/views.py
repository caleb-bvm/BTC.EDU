from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from creators.views import creator_required

from .catalog import available, missing_alternatives, ownership
from .forms import OfferForm, OfferReviewForm
from .gateway import ProviderUnavailable
from .models import Invoice, Offer
from .offers import (
    archive_offer,
    create_offer,
    missing_individuals,
    review_offer,
    submit_offer,
)
from .services import ensure_emitted, reconcile, reserve_invoice, simulate_payment


def student_required(view):
    @login_required
    @never_cache
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if request.user.account_type != "student":
            return redirect_to_login(request.get_full_path(), reverse("login"))
        return view(request, *args, **kwargs)
    return wrapped


def offer_destination(offer):
    return reverse("course-version", args=[offer.course_version.course_id, offer.course_version.number]) if offer.course_version_id else reverse("purchased-resource", args=[offer.resource_id])


@creator_required
@require_http_methods(["GET", "POST"])
def creator_offers(request):
    form = OfferForm(request.POST if request.method == "POST" else None, actor=request.user)
    if request.method == "POST" and form.is_valid():
        try:
            offer = create_offer(request.user, form.cleaned_data["target"], form.cleaned_data["title"], form.cleaned_data["amount_sats"])
        except ValidationError as exc:
            form.add_error(None, exc)
        else:
            messages.success(request, "Oferta preparada. Comprueba lo incluido y envíala a revisión.")
            return redirect("creator-offer", pk=offer.pk)
    offers = Offer.objects.filter(creator=request.user).select_related("course_version")
    return render(request, "commerce/creator_offers.html", {"form": form, "offers": Paginator(offers, 20).get_page(request.GET.get("pagina"))})


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
    return render(request, "commerce/creator_offer.html", {"offer": offer, "items": offer.items.select_related("resource"), "missing": missing_individuals(offer) if offer.kind in ("course", "chapter") else []})


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
    return render(request, "commerce/offer.html", {"offer": offer, "items": offer.items.select_related("resource"), "ownership": state, "alternatives": missing_alternatives(request.user, offer) if state == "partial" else [], "destination": offer_destination(offer)})


@student_required
@require_POST
def checkout(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    try:
        invoice = reserve_invoice(request.user, offer.pk)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        return redirect("offer-detail", pk=pk)
    try:
        ensure_emitted(invoice)
    except ProviderUnavailable as exc:
        messages.warning(request, str(exc))
    return redirect("invoice-detail", pk=invoice.pk)


@student_required
@require_GET
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice.objects.select_related("offer__course_version", "offer__resource"), pk=pk, buyer=request.user)
    if invoice.status != "paid":
        try:
            invoice = reconcile(invoice)
        except ProviderUnavailable as exc:
            messages.warning(request, str(exc))
    blocked = invoice.status == "pending" and ownership(request.user, invoice.offer) != "none"
    return render(request, "commerce/invoice.html", {"invoice": invoice, "destination": offer_destination(invoice.offer), "can_pay": invoice.status == "pending" and invoice.issue_state == "ready" and not blocked, "purchase_blocked": blocked, "active": "purchases"})


@student_required
@require_POST
def invoice_action(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, buyer=request.user)
    try:
        if request.POST.get("action") in ("pay", "simulate"):
            invoice = simulate_payment(request.user, invoice)
        else:
            invoice = reconcile(invoice)
        if invoice.status == "paid":
            messages.success(request, "Compra confirmada. Tu contenido ya está disponible.")
    except (ProviderUnavailable, ValidationError) as exc:
        messages.warning(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else str(exc))
    return redirect("invoice-detail", pk=pk)


@student_required
@require_GET
def purchases(request):
    invoices = Invoice.objects.filter(buyer=request.user).select_related("offer__course_version", "offer__resource")
    return render(request, "commerce/purchases.html", {"invoices": Paginator(invoices, 20).get_page(request.GET.get("pagina")), "active": "purchases"})

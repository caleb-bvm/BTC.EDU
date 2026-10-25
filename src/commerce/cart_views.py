from urllib.parse import urlencode
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from accounts.destinations import student_destination

from .cart import (
    MAX_ITEMS,
    UNDO_KEY,
    add_item,
    cart_summary,
    decorate_quote,
    get_cart,
    merge_pending_selection,
    ordered_items,
    pending_guest_cart,
    remove_item,
    undo_selection,
)
from .gateway import ProviderUnavailable
from .models import Offer
from .services import ensure_emitted, require_student


def _role(request):
    if request.user.is_authenticated:
        require_student(request.user)


def _quote(request, cart, coupon_code=""):
    from .orders import quote_order, quote_selection
    if cart is None:
        quote = quote_selection(request.user, [])
    elif request.user.is_authenticated:
        quote = quote_order(request.user, cart, coupon_code=coupon_code)
    else:
        selection = [{"offer_id": item.offer_id, "return_lesson_id": item.return_lesson_id,
                      "cart_item_key": str(item.pk)} for item in ordered_items(cart)]
        quote = quote_selection(request.user, selection, cart_revision=cart.revision, cart_id=cart.pk, coupon_code=coupon_code)
    return decorate_quote(request.user, quote)


def _context(request, cart, coupon_code=""):
    pending = pending_guest_cart(request)
    return {"selection": _quote(request, cart, coupon_code), "cart": cart, "undo": undo_selection(request, cart),
            "pending_items": ordered_items(pending) if pending else [], "capacity": MAX_ITEMS,
            "checkout_url": reverse("cart-checkout")}


@never_cache
@require_GET
def cart_detail(request):
    _role(request)
    return render(request, "commerce/cart.html", _context(request, get_cart(request)))


def _changed_response(request, message, status=200):
    destination = student_destination(request, request.POST.get("next", "")) or reverse("cart")
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": status < 400, "message": message, "redirect": destination,
                             "cart_count": cart_summary(request)["cart_count"]}, status=status)
    if status < 400:
        messages.success(request, message)
    else:
        messages.error(request, message)
    return redirect(destination)


@never_cache
@require_POST
def cart_add(request, pk):
    _role(request)
    offer = get_object_or_404(Offer, pk=pk)
    try:
        item, changed = add_item(request.user, get_cart(request, create=True), offer.pk, request.POST.get("leccion"))
    except ValidationError as exc:
        return _changed_response(request, " ".join(exc.messages), 409)
    if changed:
        from core.telemetry import record_commerce_action
        record_commerce_action(request, "cart_added", str(item.pk), offer=offer)
    return _changed_response(request, "Añadido al carrito. Puedes seguir explorando." if changed else "Esta opción ya está en tu carrito.")


@never_cache
@require_POST
def cart_remove(request, pk):
    _role(request)
    cart = get_cart(request)
    if not cart:
        raise Http404
    get_object_or_404(cart.items, pk=pk)
    try:
        removed = remove_item(request.user, cart, pk)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        removed["key"] = str(uuid4())
        request.session[UNDO_KEY] = removed
        messages.success(request, "Artículo retirado del carrito.")
    return redirect("cart")


@never_cache
@require_POST
def cart_undo(request):
    _role(request)
    cart = get_cart(request)
    snapshot = undo_selection(request, cart)
    if not snapshot or request.POST.get("key") != snapshot.get("key"):
        messages.error(request, "No hay un artículo retirado que puedas restaurar en este carrito.")
        return redirect("cart")
    try:
        add_item(request.user, cart, snapshot["offer_id"], snapshot.get("return_lesson_id"), restore=True)
    except (ValidationError, Offer.DoesNotExist) as exc:
        messages.error(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else "Esta opción ya no se puede recuperar.")
    else:
        request.session.pop(UNDO_KEY, None)
        messages.success(request, "Artículo restaurado. Revisa la selección antes de continuar.")
    return redirect("cart")


@never_cache
@require_POST
def cart_save(request, pk):
    if not request.user.is_authenticated:
        return redirect_to_login(reverse("cart"), reverse("login"))
    require_student(request.user)
    cart = get_cart(request)
    if not cart:
        raise Http404
    item = get_object_or_404(cart.items.select_related("offer"), pk=pk)
    from learning.bookmarks import save_item
    try:
        with transaction.atomic():
            offer = item.offer
            kind, target = ("curso", offer.course_version_id) if offer.course_version_id else ("recurso", offer.resource_id)
            save_item(request.user, kind, target, "save")
            remove_item(request.user, cart, item.pk)
    except (ValidationError, PermissionDenied) as exc:
        messages.error(request, " ".join(exc.messages) if isinstance(exc, ValidationError) else "Este contenido no se puede guardar ahora. Tu selección sigue en el carrito.")
    else:
        messages.success(request, "Guardado para después en Mi aprendizaje.")
    return redirect("cart")


@never_cache
@require_POST
def cart_merge(request):
    if not request.user.is_authenticated:
        return redirect_to_login(reverse("cart"), reverse("login"))
    require_student(request.user)
    try:
        pending = merge_pending_selection(request, request.POST.getlist("items"))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "Selección incorporada. Los artículos restantes se conservan." if pending else "Selección incorporada a tu carrito.")
    return redirect("cart")


def _verified(request, destination):
    if settings.ACCOUNT_REQUIRE_VERIFIED_EMAIL and not request.user.email_verified_at:
        request.session["account_verify_destination"] = destination
        messages.info(request, "Confirma tu correo antes de comprar para conservar una vía de recuperación.")
        return redirect("student-account-security")
    return None


def _payment(invoice):
    try:
        ensure_emitted(invoice)
    except ProviderUnavailable:
        # The reserved order is retained; retry the same invoice rather than recreate it.
        messages_text = "No pudimos preparar el pago. Actualiza esta misma factura para continuar."
        return invoice, messages_text
    return invoice, ""


@never_cache
@require_http_methods(["GET", "POST"])
def cart_checkout(request):
    if not request.user.is_authenticated:
        return redirect_to_login(reverse("cart-checkout"), reverse("login"))
    require_student(request.user)
    cart = get_cart(request)
    if cart is None:
        messages.info(request, "Elige contenido para preparar tu compra.")
        return redirect("cart")
    error = ""
    coupon_code = (request.POST if request.method == "POST" else request.GET).get("cupon", "")
    if request.method == "POST":
        verification = _verified(request, reverse("cart-checkout"))
        if verification:
            return verification
        from .orders import reserve_order
        try:
            from core.telemetry import session_id
            invoice = reserve_order(request.user, cart, request.POST.get("token", ""), request_key=request.POST.get("request_key"),
                                    activity_session=session_id(request))
        except ValidationError as exc:
            error = " ".join(exc.messages)
        else:
            invoice, warning = _payment(invoice)
            if warning:
                messages.warning(request, warning)
            return redirect("invoice-detail", pk=invoice.pk)
    context = _context(request, cart, coupon_code)
    context["coupon_input"] = coupon_code
    if request.method == "GET" and context["selection"]["lines"]:
        from core.telemetry import record_commerce_action
        record_commerce_action(request, "checkout_started", context["selection"]["fingerprint"])
    return render(request, "commerce/cart_checkout.html", {**context, "review_error": error},
                  status=409 if error else 200)


@never_cache
@require_http_methods(["GET", "POST"])
def path_checkout(request, slug):
    _role(request)
    from learning.models import LearningPath

    from .bundles import bundle_quote, reserve_path_order
    path = get_object_or_404(LearningPath, slug=slug, published=True)
    review_url = reverse("path-checkout", args=[path.slug])
    error = ""
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(review_url, reverse("login"))
        verification = _verified(request, review_url)
        if verification:
            return verification
        try:
            from core.telemetry import session_id
            invoice = reserve_path_order(request.user, path, request.POST.get("token", ""), request_key=request.POST.get("request_key"),
                                         activity_session=session_id(request))
        except ValidationError as exc:
            error = " ".join(exc.messages)
        else:
            invoice, warning = _payment(invoice)
            if warning:
                messages.warning(request, warning)
            return redirect("invoice-detail", pk=invoice.pk)
    quote = decorate_quote(request.user, bundle_quote(request.user, path))
    return render(request, "commerce/cart_checkout.html", {"selection": quote, "direct_purchase": True, "bundle_path": path,
                  "review_error": error, "return_url": reverse("learning-path", args=[path.slug]),
                  "signin_url": reverse("login") + "?" + urlencode({"next": review_url})}, status=409 if error else 200)


@never_cache
@require_http_methods(["GET", "POST"])
def direct_checkout(request, pk):
    _role(request)
    offer = get_object_or_404(Offer, pk=pk)
    data = request.POST if request.method == "POST" else request.GET
    value = data.get("leccion")
    coupon_code, gift = data.get("cupon", ""), data.get("regalo") == "1"
    from .orders import quote_direct_order, reserve_direct_order
    quote = decorate_quote(request.user, quote_direct_order(request.user, offer.pk, return_lesson_id=value, coupon_code=coupon_code, gift=gift))
    error = ""
    query = urlencode({key: item for key, item in (("leccion", value), ("cupon", coupon_code), ("regalo", "1" if gift else "")) if item})
    review_url = reverse("direct-checkout", args=[offer.pk]) + ("?" + query if query else "")
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(review_url, reverse("login"))
        verification = _verified(request, review_url)
        if verification:
            return verification
        try:
            if not request.POST.get("token"):
                raise ValidationError("Revisa el precio y lo incluido antes de preparar el pago.")
            from core.telemetry import session_id
            invoice = reserve_direct_order(request.user, offer.pk, return_lesson_id=value,
                                           request_key=request.POST.get("request_key"), token=request.POST.get("token", ""),
                                           activity_session=session_id(request), gift_message=request.POST.get("mensaje_regalo", ""))
        except ValidationError as exc:
            error = " ".join(exc.messages)
        else:
            invoice, warning = _payment(invoice)
            if warning:
                messages.warning(request, warning)
            return redirect("invoice-detail", pk=invoice.pk)
    if request.method == "GET" and quote["lines"]:
        from core.telemetry import record_commerce_action
        record_commerce_action(request, "checkout_started", quote["fingerprint"], offer=offer)
    line = quote["lines"][0] if quote["lines"] else {}
    return_url = line.get("details_url") or line.get("replacement", {}).get("url") or reverse("explore")
    toggle = {key: item for key, item in (("leccion", value), ("cupon", coupon_code)) if item}
    if not gift:
        toggle["regalo"] = "1"
    return render(request, "commerce/cart_checkout.html", {"selection": quote, "direct_purchase": True,
                  "selected_lesson_id": value or "", "offer": offer, "review_error": error,
                  "coupon_input": coupon_code, "gift": gift,
                  "gift_toggle_url": reverse("direct-checkout", args=[offer.pk]) + ("?" + urlencode(toggle) if toggle else ""),
                  "return_url": return_url,
                  "signin_url": reverse("login") + "?" + urlencode({"next": review_url})}, status=409 if error else 200)

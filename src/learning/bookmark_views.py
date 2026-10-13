from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from accounts.destinations import student_destination
from commerce.views import student_required

from .bookmarks import resource_target, save_item
from .models import SavedItem


@student_required
@require_POST
def toggle(request, kind, pk):
    try:
        save_item(request.user, kind, pk, request.POST.get("action", ""))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "Recurso guardado en Mi aprendizaje." if request.POST.get("action") == "save" else "Guardado retirado. Tus compras se conservan.")
    return redirect(student_destination(request, request.POST.get("next", "")) or "workspace")


@student_required
@require_GET
def open_saved(request, pk):
    item = get_object_or_404(SavedItem.objects.select_related("resource", "reference"), pk=pk, student=request.user)
    if item.resource_id:
        target = resource_target(request.user, item.resource)
    elif item.reference_id and item.reference.status == "published":
        from django.urls import reverse
        target = reverse("reference-detail", args=[item.reference_id])
    else:
        target = ""
    if target:
        return redirect(target)
    return render(request, "learning/saved_unavailable.html", {"item": item})

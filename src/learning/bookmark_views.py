from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from accounts.destinations import student_destination
from commerce.views import student_required

from .bookmarks import course_target, resource_target, save_item
from .models import SavedItem


@student_required
@require_POST
def collection_change(request, pk=None):
    from django.urls import reverse

    from .collections import change_collection
    try:
        collection = change_collection(request.user, request.POST.get("action", ""), request.POST.get("name", ""), pk)
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
        target = student_destination(request, request.POST.get("next", ""))
    else:
        messages.success(request, "Colección guardada." if collection else "Colección eliminada. Tus guardados se conservan.")
        target = reverse("workspace") + "?seccion=guardados" + (f"&coleccion={collection.pk}" if collection else "")
    return redirect(target or reverse("workspace") + "?seccion=guardados")


@student_required
@require_POST
def organize(request, pk):
    from django.urls import reverse

    from .collections import organize_item
    try:
        organize_item(request.user, pk, request.POST.getlist("collections"))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "Guardado organizado en tus colecciones.")
    return redirect(student_destination(request, request.POST.get("next", "")) or reverse("workspace") + "?seccion=guardados")


@student_required
@require_POST
def toggle(request, kind, pk):
    try:
        save_item(request.user, kind, pk, request.POST.get("action", ""))
    except ValidationError as exc:
        messages.error(request, " ".join(exc.messages))
    else:
        messages.success(request, "Contenido guardado en Mi aprendizaje." if request.POST.get("action") == "save" else "Guardado retirado. Tus compras se conservan.")
    return redirect(student_destination(request, request.POST.get("next", "")) or "workspace")


@student_required
@require_GET
def open_saved(request, pk):
    item = get_object_or_404(SavedItem.objects.select_related("resource", "reference", "course_version__course"), pk=pk, student=request.user)
    if item.course_version_id:
        target = course_target(request.user, item.course_version)
    elif item.resource_id:
        target = resource_target(request.user, item.resource)
    elif item.reference_id and item.reference.status == "published":
        from django.urls import reverse
        target = reverse("reference-detail", args=[item.reference_id])
    else:
        target = ""
    if target:
        return redirect(target)
    return render(request, "learning/saved_unavailable.html", {"item": item})

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from creators.views import creator_required

from .models import LearningPath
from .path_forms import PathForm, parse_steps
from .paths import save_creator_path, studio_courses


@creator_required
def creator_paths(request):
    paths = LearningPath.objects.filter(creator=request.user).annotate(step_count=Count("steps")).order_by("-created_at", "-pk")
    return render(request, "learning/creator_paths.html", {"paths": paths})


@creator_required
@require_http_methods(["GET", "POST"])
def creator_path_edit(request, pk=None):
    path = get_object_or_404(LearningPath, pk=pk, creator=request.user) if pk else LearningPath(creator=request.user)
    courses = studio_courses(request.user)
    form = PathForm(request.POST or None, instance=path)
    errors = []
    if request.method == "POST":
        steps, errors = parse_steps(request.POST, courses)
        if form.is_valid() and not errors:
            fields = {name: form.cleaned_data[name] for name in form.Meta.fields}
            try:
                path = save_creator_path(request.user, LearningPath.objects.get(pk=path.pk) if path.pk else LearningPath(), fields, steps)
            except ValidationError as exc:
                errors = exc.messages
            else:
                messages.success(request, "Ruta publicada." if path.published else "Ruta guardada como borrador.")
                return redirect("creator-path", pk=path.pk)
        rows = {item["course"].pk: {**item, "position": index} for index, item in enumerate(steps, 1)}
    else:
        rows = {step.course_id: {"position": step.position, "optional": step.optional, "note": step.note}
                for step in path.steps.all()} if path.pk else {}
    course_rows = [{"course": course, "selected": course.pk in rows, **rows.get(course.pk, {})} for course in courses]
    course_rows.sort(key=lambda row: (not row["selected"], row.get("position") or 0, row["course"].title))
    return render(request, "learning/creator_path_form.html", {"form": form, "path": path, "course_rows": course_rows, "step_errors": errors})

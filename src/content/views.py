from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from .access import content_access
from .models import Lesson


@require_GET
@never_cache
def lesson_content(request, pk):
    lesson = get_object_or_404(Lesson.objects.select_related("chapter__course"), pk=pk)
    decision = content_access(request.user, lesson)
    if not decision.allowed:
        if decision.reason == "unpublished":
            return JsonResponse({"error": "not_found"}, status=404)
        return JsonResponse({"error": "purchase_required"}, status=403)
    return JsonResponse({"id": lesson.pk, "title": lesson.title, "body": lesson.body, "access": decision.reason})

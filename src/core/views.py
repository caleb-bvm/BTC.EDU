from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.shortcuts import render

from content.catalog import catalog_context


def home(request):
    return render(request, "core/home.html", {"active": "home", **catalog_context({})})


def explore(request):
    context = {"active": "explore", **catalog_context(request.GET)}
    template = "core/_catalog.html" if request.headers.get("HX-Request") == "true" else "core/explore.html"
    return render(request, template, context)


def creators(request):
    return render(request, "core/creators.html", {"active": "creators"})


@login_required
def workspace(request):
    return render(request, "core/workspace.html")


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "unavailable"}, status=503)
    return JsonResponse({"status": "ok"})

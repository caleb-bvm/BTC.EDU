from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.shortcuts import render


def home(request):
    return render(request, "core/home.html", {"active": "home"})


def explore(request):
    # Estado vacío deliberado: todavía no se han creado cursos ni ofertas.
    categories = {"todos": "Todo", "cursos": "Cursos", "videos": "Videos", "materiales": "Materiales"}
    category = request.GET.get("tipo", "todos")
    if category not in categories:
        category = "todos"
    context = {"active": "explore", "category": category, "categories": categories}
    template = "core/_catalog_empty.html" if request.headers.get("HX-Request") == "true" else "core/explore.html"
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

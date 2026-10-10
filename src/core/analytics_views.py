from datetime import timedelta

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from creators.views import creator_required

from .analytics import PeriodForm, dashboard_data


def panel(request, creator=None):
    today = timezone.localdate()
    form = PeriodForm(request.GET if request.GET else {"start": today - timedelta(days=29), "end": today})
    data = dashboard_data(form.cleaned_data["start"], form.cleaned_data["end"], creator) if form.is_valid() else None
    return render(request, "core/analytics.html", {**(admin.site.each_context(request) if creator is None else {}), "form": form, "data": data, "creator_space": bool(creator),
                                               "base_template": "creators/base.html" if creator else "admin/base_site.html"}, status=200 if data else 400)


@creator_required
@require_GET
def creator_analytics(request):
    return panel(request, request.user)


@staff_member_required
@never_cache
@require_GET
def admin_analytics(request):
    if not all(request.user.has_perm(permission) for permission in ("commerce.view_invoice", "learning.view_enrollment", "core.view_activityevent")):
        raise PermissionDenied
    return panel(request)

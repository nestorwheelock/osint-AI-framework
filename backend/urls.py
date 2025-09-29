"""
Main URL configuration for OSINT Framework Django project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def healthz(request):
    """Health check endpoint"""
    return JsonResponse({"ok": True})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/subjects/", include("apps.subjects.urls")),
    path("api/", include("apps.investigations.urls")),
    path("healthz/", healthz, name="healthz"),
]

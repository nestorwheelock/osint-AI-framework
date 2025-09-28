from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

def healthz(request):
    """Health check endpoint"""
    return JsonResponse({"ok": True})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/subjects/', include('apps.subjects.urls')),
    path('api/search/', include('apps.search.urls')),
    path('api/analyze/', include('apps.analyze.urls')),
    path('healthz/', healthz, name='healthz'),
]

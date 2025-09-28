"""
URL configuration for Subject API endpoints.
Defines RESTful routes for Subject CRUD operations.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet

# Create router and register Subject viewset
router = DefaultRouter()
router.register(r"subjects", SubjectViewSet, basename="subject")

urlpatterns = [
    path("", include(router.urls)),
]

# API endpoints provided:
# GET    /subjects/           - List subjects (paginated)
# POST   /subjects/           - Create new subject
# GET    /subjects/{id}/      - Retrieve specific subject
# PUT    /subjects/{id}/      - Update subject (full)
# PATCH  /subjects/{id}/      - Update subject (partial)
# DELETE /subjects/{id}/      - Delete subject

"""
URL configuration for Investigation Sessions API.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Session management for subjects
    path(
        "subjects/<uuid:subject_id>/sessions/",
        views.SubjectSessionListCreateView.as_view(),
        name="subject-sessions",
    ),
    # Individual session operations
    path(
        "sessions/<uuid:id>/", views.SessionDetailView.as_view(), name="session-detail"
    ),
    # Session status management
    path(
        "sessions/<uuid:session_id>/status/",
        views.update_session_status,
        name="session-status",
    ),
    # Convenience endpoints
    path(
        "sessions/<uuid:session_id>/start/", views.start_session, name="session-start"
    ),
    path(
        "sessions/<uuid:session_id>/complete/",
        views.complete_session,
        name="session-complete",
    ),
    # Session filtering
    path("sessions/", views.SessionsByStatusView.as_view(), name="sessions-list"),
]

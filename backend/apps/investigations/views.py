"""
API views for Investigation Session management.
Provides REST endpoints for session CRUD operations.
"""

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import Http404

from .models import Session
from .serializers import (
    SessionSerializer,
    SessionCreateSerializer,
    SessionStatusUpdateSerializer,
    SessionListSerializer,
)
from apps.subjects.models import Subject


class SubjectSessionListCreateView(generics.ListCreateAPIView):
    """
    List sessions for a subject or create a new session.

    GET /subjects/{subject_id}/sessions - List all sessions for subject
    POST /subjects/{subject_id}/sessions - Create new session for subject
    """

    def get_subject(self):
        """Get subject or raise 404."""
        subject_id = self.kwargs["subject_id"]
        return get_object_or_404(Subject, id=subject_id)

    def get_queryset(self):
        """Get sessions for the specific subject."""
        subject = self.get_subject()
        return Session.objects.filter(subject=subject)

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.request.method == "POST":
            return SessionCreateSerializer
        return SessionListSerializer

    def get_serializer_context(self):
        """Add subject to serializer context for creation."""
        context = super().get_serializer_context()
        if self.request.method == "POST":
            context["subject"] = self.get_subject()
        return context

    def create(self, request, *args, **kwargs):
        """Create a new session for the subject."""
        subject = self.get_subject()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save()

        # Return full session details
        response_serializer = SessionSerializer(session)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a session.

    GET /sessions/{id} - Get session details
    PUT /sessions/{id} - Update session
    DELETE /sessions/{id} - Delete session
    """

    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    lookup_field = "id"


@api_view(["PUT"])
def update_session_status(request, session_id):
    """
    Update session status only.

    PUT /sessions/{id}/status - Update session status
    """
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return Response(
            {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = SessionStatusUpdateSerializer(session, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        # Return full session details
        response_serializer = SessionSerializer(session)
        return Response(response_serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Additional helper views for specific use cases


class SessionsByStatusView(generics.ListAPIView):
    """
    List sessions filtered by status.

    GET /sessions?status=running - List sessions by status
    """

    serializer_class = SessionListSerializer

    def get_queryset(self):
        """Filter sessions by status query parameter."""
        queryset = Session.objects.all()
        status_filter = self.request.query_params.get("status", None)

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by("-created_at")


@api_view(["POST"])
def start_session(request, session_id):
    """
    Convenience endpoint to start a session (set status to running).

    POST /sessions/{id}/start - Start session
    """
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return Response(
            {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if session.status != "created":
        return Response(
            {"error": f"Cannot start session with status: {session.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    session.status = "running"
    session.save()

    response_serializer = SessionSerializer(session)
    return Response(response_serializer.data)


@api_view(["POST"])
def complete_session(request, session_id):
    """
    Convenience endpoint to complete a session.

    POST /sessions/{id}/complete - Complete session
    """
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return Response(
            {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if session.status not in ["running", "paused"]:
        return Response(
            {"error": f"Cannot complete session with status: {session.status}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    session.status = "completed"
    session.save()

    response_serializer = SessionSerializer(session)
    return Response(response_serializer.data)

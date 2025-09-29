"""
Test cases for Session management functionality.
Following TDD approach - tests written first, then implementation.
"""

import json
import uuid
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.subjects.models import Subject


class SessionModelTests(TestCase):
    """Test cases for Session model functionality."""

    def setUp(self):
        """Set up test data."""
        self.subject = Subject.objects.create(
            name="Test Subject", description="A test subject for session testing"
        )

    def test_create_session_with_valid_subject_returns_201(self):
        """Test that creating a session with valid subject succeeds."""
        # This test will fail until we implement Session model
        from apps.investigations.models import Session

        session_data = {
            "subject": self.subject,
            "config_json": {
                "search_engines": ["google", "bing"],
                "max_pages_per_engine": 50,
                "rate_limit_delay": 2.0,
            },
        }

        session = Session.objects.create(**session_data)

        self.assertIsNotNone(session.id)
        self.assertEqual(session.subject, self.subject)
        self.assertEqual(session.status, "created")
        self.assertIsNotNone(session.created_at)

    def test_session_subject_relationship_integrity(self):
        """Test that session-subject foreign key relationship works."""
        from apps.investigations.models import Session

        session = Session.objects.create(
            subject=self.subject, config_json={"search_engines": ["google"]}
        )

        # Test relationship
        self.assertEqual(session.subject.name, "Test Subject")

        # Test reverse relationship
        self.assertIn(session, self.subject.sessions.all())

    def test_session_status_transitions_are_valid(self):
        """Test that session status transitions follow business rules."""
        from apps.investigations.models import Session

        session = Session.objects.create(
            subject=self.subject, config_json={"search_engines": ["google"]}
        )

        # Initial status should be 'created'
        self.assertEqual(session.status, "created")

        # Should be able to transition to 'running'
        session.status = "running"
        session.save()
        session.refresh_from_db()
        self.assertEqual(session.status, "running")


class SessionAPITests(APITestCase):
    """Test cases for Session API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.subject = Subject.objects.create(
            name="API Test Subject", description="Subject for API testing"
        )

    def test_create_session_success(self):
        """Test POST /subjects/{subject_id}/sessions creates session successfully."""
        url = reverse("subject-sessions", args=[self.subject.id])
        data = {
            "config_json": {
                "search_engines": ["google", "bing", "duckduckgo"],
                "max_pages_per_engine": 50,
                "rate_limit_delay": 2.0,
                "respect_robots_txt": True,
            }
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(str(response.data["subject"]), str(self.subject.id))
        self.assertEqual(response.data["status"], "created")

    def test_create_session_with_invalid_subject_returns_404(self):
        """Test creating session with non-existent subject returns 404."""
        invalid_subject_id = uuid.uuid4()
        url = reverse("subject-sessions", args=[invalid_subject_id])
        data = {"config_json": {"search_engines": ["google"]}}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_sessions_for_subject(self):
        """Test GET /subjects/{subject_id}/sessions returns session list."""
        # Create a session first
        from apps.investigations.models import Session

        session = Session.objects.create(
            subject=self.subject, config_json={"search_engines": ["google"]}
        )

        url = reverse("subject-sessions", args=[self.subject.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(session.id))

    def test_update_session_status(self):
        """Test PUT /sessions/{id}/status updates session status."""
        from apps.investigations.models import Session

        session = Session.objects.create(
            subject=self.subject, config_json={"search_engines": ["google"]}
        )

        url = reverse("session-status", args=[session.id])
        data = {"status": "running"}

        response = self.client.put(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session.refresh_from_db()
        self.assertEqual(session.status, "running")

    def test_create_session_with_valid_config_stores_json(self):
        """Test that session configuration is properly stored and validated."""
        url = reverse("subject-sessions", args=[self.subject.id])
        config = {
            "search_engines": ["google", "bing"],
            "max_pages_per_engine": 25,
            "rate_limit_delay": 1.5,
            "filters": {
                "languages": ["en", "es"],
                "date_range": {"start": "2024-01-01", "end": "2024-12-31"},
            },
        }
        data = {"config_json": config}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["config_json"], config)

    def test_session_lifecycle_workflow(self):
        """Test complete session lifecycle from creation to completion."""
        # Create session
        url = reverse("subject-sessions", args=[self.subject.id])
        data = {"config_json": {"search_engines": ["google"]}}

        create_response = self.client.post(url, data, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        session_id = create_response.data["id"]

        # Start session (change to running)
        status_url = reverse("session-status", args=[session_id])
        self.client.put(status_url, {"status": "running"}, format="json")

        # Complete session
        self.client.put(status_url, {"status": "completed"}, format="json")

        # Get session details
        detail_url = reverse("session-detail", args=[session_id])
        detail_response = self.client.get(detail_url)

        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["status"], "completed")
        self.assertIsNotNone(detail_response.data["finished_at"])

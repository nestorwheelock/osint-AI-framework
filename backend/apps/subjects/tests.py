"""
Test suite for Subject CRUD operations.
Following TDD approach - tests written first, then minimal implementation.
"""

import json
import uuid
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError

from .models import Subject


class TestSubjectModel(TestCase):
    """Unit tests for Subject model."""

    def test_create_subject_with_valid_data_returns_subject(self):
        """Test creating a subject with valid data."""
        subject = Subject.objects.create(
            name="Test Target",
            description="A test investigation subject",
            aliases=["alias1", "alias2"],
            tags=["high-priority", "active"],
        )

        self.assertIsNotNone(subject.id)
        self.assertIsInstance(subject.id, uuid.UUID)
        self.assertEqual(subject.name, "Test Target")
        self.assertEqual(subject.description, "A test investigation subject")
        self.assertEqual(subject.aliases, ["alias1", "alias2"])
        self.assertEqual(subject.tags, ["high-priority", "active"])
        self.assertIsNotNone(subject.created_at)
        self.assertIsNotNone(subject.updated_at)

    def test_create_subject_with_minimal_data(self):
        """Test creating subject with only required fields."""
        subject = Subject.objects.create(name="Minimal Subject")

        self.assertEqual(subject.name, "Minimal Subject")
        self.assertIsNone(subject.description)
        self.assertEqual(subject.aliases, [])
        self.assertEqual(subject.tags, [])

    def test_subject_name_is_required(self):
        """Test that subject name is required."""
        with self.assertRaises(ValidationError):
            subject = Subject(description="Missing name")
            subject.full_clean()

    def test_subject_name_uniqueness(self):
        """Test that subject names must be unique."""
        Subject.objects.create(name="Unique Name")

        with self.assertRaises(ValidationError):
            duplicate_subject = Subject(name="Unique Name")
            duplicate_subject.full_clean()

    def test_subject_string_representation(self):
        """Test subject string representation."""
        subject = Subject.objects.create(name="Test Subject")
        self.assertEqual(str(subject), "Test Subject")


class TestSubjectCRUD(APITestCase):
    """Integration tests for Subject CRUD API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.subject_data = {
            "name": "Investigation Target",
            "description": "Primary subject of investigation",
            "aliases": ["Target Alpha", "Subject One"],
            "tags": ["active", "high-priority"],
        }

        self.test_subject = Subject.objects.create(
            name="Existing Subject",
            description="Already in database",
            aliases=["existing"],
            tags=["test"],
        )

    def test_create_subject_with_valid_data_returns_201(self):
        """Test POST /subjects with valid data returns 201."""
        url = reverse("subject-list")
        response = self.client.post(url, self.subject_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], self.subject_data["name"])
        self.assertEqual(response.data["description"], self.subject_data["description"])
        self.assertEqual(response.data["aliases"], self.subject_data["aliases"])
        self.assertEqual(response.data["tags"], self.subject_data["tags"])
        self.assertIn("id", response.data)
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_create_subject_with_duplicate_name_returns_400(self):
        """Test POST /subjects with duplicate name returns 400."""
        url = reverse("subject-list")
        duplicate_data = {"name": "Existing Subject"}

        response = self.client.post(url, duplicate_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_subject_with_invalid_data_returns_400(self):
        """Test POST /subjects with invalid data returns 400."""
        url = reverse("subject-list")
        invalid_data = {"description": "Missing required name field"}

        response = self.client.post(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_get_subjects_returns_paginated_list(self):
        """Test GET /subjects returns paginated list."""
        url = reverse("subject-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_get_subject_by_id_returns_200(self):
        """Test GET /subjects/{id} returns 200."""
        url = reverse("subject-detail", kwargs={"pk": self.test_subject.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.test_subject.id))
        self.assertEqual(response.data["name"], self.test_subject.name)

    def test_get_nonexistent_subject_returns_404(self):
        """Test GET /subjects/{invalid_id} returns 404."""
        invalid_id = uuid.uuid4()
        url = reverse("subject-detail", kwargs={"pk": invalid_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_subject_with_valid_data_returns_200(self):
        """Test PUT /subjects/{id} with valid data returns 200."""
        url = reverse("subject-detail", kwargs={"pk": self.test_subject.id})
        update_data = {
            "name": "Updated Subject Name",
            "description": "Updated description",
            "aliases": ["updated", "alias"],
            "tags": ["updated"],
        }

        response = self.client.put(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], update_data["name"])
        self.assertEqual(response.data["description"], update_data["description"])

        # Verify database was updated
        updated_subject = Subject.objects.get(id=self.test_subject.id)
        self.assertEqual(updated_subject.name, update_data["name"])

    def test_partial_update_subject_returns_200(self):
        """Test PATCH /subjects/{id} with partial data returns 200."""
        url = reverse("subject-detail", kwargs={"pk": self.test_subject.id})
        partial_data = {"description": "Partially updated description"}

        response = self.client.patch(url, partial_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["description"], partial_data["description"])
        self.assertEqual(response.data["name"], self.test_subject.name)  # Unchanged

    def test_delete_subject_returns_204(self):
        """Test DELETE /subjects/{id} returns 204."""
        url = reverse("subject-detail", kwargs={"pk": self.test_subject.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify subject was deleted
        with self.assertRaises(Subject.DoesNotExist):
            Subject.objects.get(id=self.test_subject.id)

    def test_delete_nonexistent_subject_returns_404(self):
        """Test DELETE /subjects/{invalid_id} returns 404."""
        invalid_id = uuid.uuid4()
        url = reverse("subject-detail", kwargs={"pk": invalid_id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestSubjectValidation(TestCase):
    """Tests for Subject model validation."""

    def test_name_max_length_validation(self):
        """Test name field max length validation."""
        long_name = "x" * 256  # Assuming 255 char limit
        with self.assertRaises(ValidationError):
            subject = Subject(name=long_name)
            subject.full_clean()

    def test_description_max_length_validation(self):
        """Test description field max length validation."""
        long_description = "x" * 1001  # Assuming 1000 char limit
        with self.assertRaises(ValidationError):
            subject = Subject(name="Valid Name", description=long_description)
            subject.full_clean()

    def test_aliases_default_empty_list(self):
        """Test aliases field defaults to empty list."""
        subject = Subject.objects.create(name="Test")
        self.assertEqual(subject.aliases, [])

    def test_tags_default_empty_list(self):
        """Test tags field defaults to empty list."""
        subject = Subject.objects.create(name="Test")
        self.assertEqual(subject.tags, [])

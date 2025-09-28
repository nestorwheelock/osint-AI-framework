"""
Subject model for OSINT investigation management.
Represents entities under investigation with metadata and organization features.
"""

import uuid
from django.db import models
from django.core.exceptions import ValidationError


class Subject(models.Model):
    """
    Model representing an investigation subject.

    A subject is the primary entity being investigated, such as a person,
    organization, domain, or other target of OSINT research.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the subject",
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Primary name or identifier for the subject",
    )

    description = models.TextField(
        max_length=1000,
        blank=True,
        null=True,
        help_text="Optional detailed description of the subject",
    )

    aliases = models.JSONField(
        default=list,
        blank=True,
        help_text="Alternative names or identifiers for the subject",
    )

    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorizing and organizing subjects",
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when the subject was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the subject was last modified"
    )

    class Meta:
        db_table = "subjects"
        ordering = ["-created_at"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    def __str__(self):
        """Return string representation of the subject."""
        return self.name

    def clean(self):
        """Custom validation for the Subject model."""
        super().clean()

        # Validate name is not empty
        if not self.name or not self.name.strip():
            raise ValidationError(
                {"name": "Name field is required and cannot be empty."}
            )

        # Check for duplicate names (excluding self for updates)
        existing = Subject.objects.filter(name=self.name)
        if self.pk:
            existing = existing.exclude(pk=self.pk)

        if existing.exists():
            raise ValidationError({"name": "A subject with this name already exists."})

    def save(self, *args, **kwargs):
        """Override save to ensure validation is run."""
        self.full_clean()
        super().save(*args, **kwargs)

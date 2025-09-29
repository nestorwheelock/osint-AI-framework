"""
Session model for OSINT investigation management.
Represents investigation sessions that organize research workflows with configuration.
"""

import uuid
from django.db import models
from django.core.exceptions import ValidationError
from apps.subjects.models import Subject


class SessionStatus(models.TextChoices):
    """Status choices for investigation sessions."""

    CREATED = "created", "Created"
    RUNNING = "running", "Running"
    PAUSED = "paused", "Paused"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"


class Session(models.Model):
    """
    Model representing an investigation session.

    A session organizes a specific research workflow for a subject,
    including configuration for search engines, limits, and filters.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the session",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="sessions",
        help_text="The subject being investigated in this session",
    )

    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.CREATED,
        help_text="Current status of the investigation session",
    )

    config_json = models.JSONField(
        default=dict,
        help_text="Session configuration including search engines, limits, and filters",
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the session was started (moved to running)",
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the session was completed or failed",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the session was created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the session was last modified",
    )

    class Meta:
        db_table = "investigation_sessions"
        ordering = ["-created_at"]
        verbose_name = "Investigation Session"
        verbose_name_plural = "Investigation Sessions"

    def __str__(self):
        """Return string representation of the session."""
        return f"Session {self.id} for {self.subject.name} ({self.status})"

    def clean(self):
        """Custom validation for the Session model."""
        super().clean()

        # Validate status transitions
        if self.pk:  # Only validate transitions for existing sessions
            try:
                old_session = Session.objects.get(pk=self.pk)
                if not self._is_valid_status_transition(
                    old_session.status, self.status
                ):
                    raise ValidationError(
                        {
                            "status": f"Invalid status transition from {old_session.status} to {self.status}"
                        }
                    )
            except Session.DoesNotExist:
                pass

        # Validate required configuration fields
        if not isinstance(self.config_json, dict):
            raise ValidationError(
                {"config_json": "Configuration must be a valid JSON object"}
            )

        if "search_engines" not in self.config_json:
            raise ValidationError(
                {"config_json": "Configuration must include search_engines list"}
            )

    def _is_valid_status_transition(self, old_status, new_status):
        """Check if status transition is valid according to business rules."""
        valid_transitions = {
            SessionStatus.CREATED: [SessionStatus.RUNNING, SessionStatus.FAILED],
            SessionStatus.RUNNING: [
                SessionStatus.PAUSED,
                SessionStatus.COMPLETED,
                SessionStatus.FAILED,
            ],
            SessionStatus.PAUSED: [SessionStatus.RUNNING, SessionStatus.FAILED],
            SessionStatus.COMPLETED: [],  # Terminal state
            SessionStatus.FAILED: [],  # Terminal state
        }

        return (
            new_status in valid_transitions.get(old_status, [])
            or old_status == new_status
        )

    def save(self, *args, **kwargs):
        """Override save to ensure validation and update timestamps."""
        # Update started_at when transitioning to running
        if self.status == SessionStatus.RUNNING and not self.started_at:
            from django.utils import timezone

            self.started_at = timezone.now()

        # Update finished_at when transitioning to completed or failed
        if (
            self.status in [SessionStatus.COMPLETED, SessionStatus.FAILED]
            and not self.finished_at
        ):
            from django.utils import timezone

            self.finished_at = timezone.now()

        self.full_clean()
        super().save(*args, **kwargs)

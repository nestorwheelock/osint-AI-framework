"""
Serializers for Investigation Session API endpoints.
Handles JSON serialization/deserialization for Session models.
"""

from rest_framework import serializers
from .models import Session, SessionStatus
from apps.subjects.models import Subject


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for Session model with full details."""

    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())

    class Meta:
        model = Session
        fields = [
            "id",
            "subject",
            "status",
            "config_json",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "started_at",
            "finished_at",
        ]

    def validate_config_json(self, value):
        """Validate session configuration JSON."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Configuration must be a valid JSON object"
            )

        if "search_engines" not in value:
            raise serializers.ValidationError(
                "Configuration must include 'search_engines' list"
            )

        if not isinstance(value["search_engines"], list) or not value["search_engines"]:
            raise serializers.ValidationError(
                "'search_engines' must be a non-empty list"
            )

        # Validate optional fields if present
        if "max_pages_per_engine" in value:
            if (
                not isinstance(value["max_pages_per_engine"], int)
                or value["max_pages_per_engine"] <= 0
            ):
                raise serializers.ValidationError(
                    "'max_pages_per_engine' must be a positive integer"
                )

        if "rate_limit_delay" in value:
            if (
                not isinstance(value["rate_limit_delay"], (int, float))
                or value["rate_limit_delay"] < 0
            ):
                raise serializers.ValidationError(
                    "'rate_limit_delay' must be a non-negative number"
                )

        return value

    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:  # For updates
            old_status = self.instance.status
            if not self.instance._is_valid_status_transition(old_status, value):
                raise serializers.ValidationError(
                    f"Invalid status transition from {old_status} to {value}"
                )
        return value


class SessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new sessions."""

    class Meta:
        model = Session
        fields = ["config_json"]

    def validate_config_json(self, value):
        """Validate session configuration JSON for creation."""
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Configuration must be a valid JSON object"
            )

        if "search_engines" not in value:
            raise serializers.ValidationError(
                "Configuration must include 'search_engines' list"
            )

        if not isinstance(value["search_engines"], list) or not value["search_engines"]:
            raise serializers.ValidationError(
                "'search_engines' must be a non-empty list"
            )

        return value

    def create(self, validated_data):
        """Create session with subject from context."""
        subject = self.context["subject"]
        return Session.objects.create(subject=subject, **validated_data)


class SessionStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating session status only."""

    class Meta:
        model = Session
        fields = ["status"]

    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:
            old_status = self.instance.status
            if not self.instance._is_valid_status_transition(old_status, value):
                raise serializers.ValidationError(
                    f"Invalid status transition from {old_status} to {value}"
                )
        return value


class SessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing sessions."""

    class Meta:
        model = Session
        fields = [
            "id",
            "status",
            "created_at",
            "updated_at",
            "started_at",
            "finished_at",
        ]

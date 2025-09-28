"""
Django REST Framework serializers for Subject model.
Handles serialization, deserialization, and validation for Subject CRUD operations.
"""

from rest_framework import serializers
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    """
    Full serializer for Subject model with all fields.
    Used for read operations and complete object representation.
    """

    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "description",
            "aliases",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value):
        """Validate subject name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty.")

        # Check for uniqueness during updates
        if self.instance:
            existing = Subject.objects.filter(name=value).exclude(pk=self.instance.pk)
        else:
            existing = Subject.objects.filter(name=value)

        if existing.exists():
            raise serializers.ValidationError(
                "A subject with this name already exists."
            )

        return value.strip()

    def validate_aliases(self, value):
        """Validate aliases field."""
        if value is None:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("Aliases must be a list.")

        # Remove empty strings and duplicates while preserving order
        cleaned_aliases = []
        seen = set()
        for alias in value:
            if isinstance(alias, str) and alias.strip() and alias not in seen:
                cleaned_aliases.append(alias.strip())
                seen.add(alias.strip())

        return cleaned_aliases

    def validate_tags(self, value):
        """Validate tags field."""
        if value is None:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list.")

        # Remove empty strings and duplicates while preserving order
        cleaned_tags = []
        seen = set()
        for tag in value:
            if isinstance(tag, str) and tag.strip() and tag not in seen:
                cleaned_tags.append(tag.strip())
                seen.add(tag.strip())

        return cleaned_tags


class SubjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new Subject instances.
    Includes specific validation rules for creation.
    """

    class Meta:
        model = Subject
        fields = ["name", "description", "aliases", "tags"]

    def validate_name(self, value):
        """Validate subject name for creation."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty.")

        if Subject.objects.filter(name=value.strip()).exists():
            raise serializers.ValidationError(
                "A subject with this name already exists."
            )

        return value.strip()

    def validate_aliases(self, value):
        """Validate aliases field."""
        if value is None:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("Aliases must be a list.")

        cleaned_aliases = []
        seen = set()
        for alias in value:
            if isinstance(alias, str) and alias.strip() and alias not in seen:
                cleaned_aliases.append(alias.strip())
                seen.add(alias.strip())

        return cleaned_aliases

    def validate_tags(self, value):
        """Validate tags field."""
        if value is None:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list.")

        cleaned_tags = []
        seen = set()
        for tag in value:
            if isinstance(tag, str) and tag.strip() and tag not in seen:
                cleaned_tags.append(tag.strip())
                seen.add(tag.strip())

        return cleaned_tags


class SubjectUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing Subject instances.
    Supports partial updates and includes update-specific validation.
    """

    class Meta:
        model = Subject
        fields = ["name", "description", "aliases", "tags"]

    def validate_name(self, value):
        """Validate subject name for updates."""
        if not value or not value.strip():
            raise serializers.ValidationError("Name is required and cannot be empty.")

        # Check for uniqueness excluding current instance
        existing = Subject.objects.filter(name=value.strip())
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise serializers.ValidationError(
                "A subject with this name already exists."
            )

        return value.strip()

    def validate_aliases(self, value):
        """Validate aliases field."""
        if value is None:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("Aliases must be a list.")

        cleaned_aliases = []
        seen = set()
        for alias in value:
            if isinstance(alias, str) and alias.strip() and alias not in seen:
                cleaned_aliases.append(alias.strip())
                seen.add(alias.strip())

        return cleaned_aliases

    def validate_tags(self, value):
        """Validate tags field."""
        if value is None:
            return []

        if not isinstance(value, list):
            raise serializers.ValidationError("Tags must be a list.")

        cleaned_tags = []
        seen = set()
        for tag in value:
            if isinstance(tag, str) and tag.strip() and tag not in seen:
                cleaned_tags.append(tag.strip())
                seen.add(tag.strip())

        return cleaned_tags

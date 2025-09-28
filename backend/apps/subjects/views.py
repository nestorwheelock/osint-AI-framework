"""
Django REST Framework views for Subject CRUD operations.
Implements RESTful API endpoints with proper error handling and pagination.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Subject
from .serializers import (
    SubjectSerializer,
    SubjectCreateSerializer,
    SubjectUpdateSerializer,
)


class SubjectPagination(PageNumberPagination):
    """Custom pagination for Subject list views."""

    page_size = 20
    page_size_query_param = "limit"
    max_page_size = 100


class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subject CRUD operations.

    Provides:
    - GET /subjects/ - List subjects with pagination
    - POST /subjects/ - Create new subject
    - GET /subjects/{id}/ - Retrieve specific subject
    - PUT /subjects/{id}/ - Update subject (full)
    - PATCH /subjects/{id}/ - Update subject (partial)
    - DELETE /subjects/{id}/ - Delete subject
    """

    queryset = Subject.objects.all()
    pagination_class = SubjectPagination
    lookup_field = "pk"

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "create":
            return SubjectCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return SubjectUpdateSerializer
        return SubjectSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new subject.

        Returns:
            201: Subject created successfully
            400: Invalid data provided
        """
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                subject = serializer.save()

            # Return full subject data
            response_serializer = SubjectSerializer(subject)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except DjangoValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "An error occurred while creating the subject."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        """
        List subjects with pagination.

        Returns:
            200: Paginated list of subjects
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": "An error occurred while retrieving subjects."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific subject.

        Returns:
            200: Subject data
            404: Subject not found
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        except Subject.DoesNotExist:
            return Response(
                {"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An error occurred while retrieving the subject."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """
        Update a subject (full update).

        Returns:
            200: Subject updated successfully
            400: Invalid data provided
            404: Subject not found
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                subject = serializer.save()

            # Return full subject data
            response_serializer = SubjectSerializer(subject)
            return Response(response_serializer.data)

        except Subject.DoesNotExist:
            return Response(
                {"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except DjangoValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "An error occurred while updating the subject."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a subject.

        Returns:
            200: Subject updated successfully
            400: Invalid data provided
            404: Subject not found
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                subject = serializer.save()

            # Return full subject data
            response_serializer = SubjectSerializer(subject)
            return Response(response_serializer.data)

        except Subject.DoesNotExist:
            return Response(
                {"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except DjangoValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "An error occurred while updating the subject."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, *args, **kwargs):
        """
        Delete a subject.

        Returns:
            204: Subject deleted successfully
            404: Subject not found
        """
        try:
            instance = self.get_object()

            with transaction.atomic():
                instance.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except Subject.DoesNotExist:
            return Response(
                {"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An error occurred while deleting the subject."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

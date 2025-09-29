"""
Search application models for OSINT AI Framework.

This module contains Django models for storing search configurations,
results, and metadata for the meta-search functionality.
"""

from django.db import models
from django.utils import timezone


class SearchQuery(models.Model):
    """Model for storing search queries and their metadata."""

    query_text = models.TextField(help_text="The search query text")
    query_type = models.CharField(
        max_length=50,
        choices=[
            ("general", "General Search"),
            ("person", "Person Search"),
            ("organization", "Organization Search"),
            ("domain", "Domain Search"),
            ("email", "Email Search"),
        ],
        default="general",
        help_text="Type of search query",
    )
    created_at = models.DateTimeField(
        default=timezone.now, help_text="When the search was created"
    )
    subject = models.ForeignKey(
        "subjects.Subject",
        on_delete=models.CASCADE,
        related_name="search_queries",
        help_text="Subject this search belongs to",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Search Query"
        verbose_name_plural = "Search Queries"

    def __str__(self):
        return f"Search: {self.query_text[:50]}..."


class SearchResult(models.Model):
    """Model for storing individual search results."""

    query = models.ForeignKey(
        SearchQuery,
        on_delete=models.CASCADE,
        related_name="results",
        help_text="The search query that generated this result",
    )
    title = models.CharField(max_length=500, help_text="Title of the search result")
    url = models.URLField(max_length=2000, help_text="URL of the search result")
    canonical_url = models.URLField(
        max_length=2000, blank=True, help_text="Canonicalized version of the URL"
    )
    description = models.TextField(
        blank=True, help_text="Description or snippet from the search result"
    )
    search_engine = models.CharField(
        max_length=50, help_text="Search engine that provided this result"
    )
    rank = models.PositiveIntegerField(help_text="Position in search results")
    created_at = models.DateTimeField(
        default=timezone.now, help_text="When this result was captured"
    )

    class Meta:
        ordering = ["rank"]
        unique_together = ["query", "url", "search_engine"]
        verbose_name = "Search Result"
        verbose_name_plural = "Search Results"

    def __str__(self):
        return f"{self.title} ({self.search_engine})"

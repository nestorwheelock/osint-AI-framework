"""Django admin configuration for search application."""

from django.contrib import admin
from .models import SearchQuery, SearchResult


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    """Admin interface for SearchQuery model."""

    list_display = ["query_text", "query_type", "subject", "created_at"]
    list_filter = ["query_type", "created_at"]
    search_fields = ["query_text", "subject__name"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]

    fieldsets = (
        (None, {"fields": ("query_text", "query_type", "subject")}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    """Admin interface for SearchResult model."""

    list_display = ["title", "search_engine", "rank", "query", "created_at"]
    list_filter = ["search_engine", "created_at"]
    search_fields = ["title", "url", "description"]
    date_hierarchy = "created_at"
    readonly_fields = ["created_at"]

    fieldsets = (
        (None, {"fields": ("query", "title", "url", "canonical_url")}),
        ("Content", {"fields": ("description",)}),
        (
            "Metadata",
            {
                "fields": ("search_engine", "rank", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )

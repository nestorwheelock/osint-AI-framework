"""Django app configuration for search application."""

from django.apps import AppConfig


class SearchConfig(AppConfig):
    """Configuration for the search application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.search"
    verbose_name = "Search"

    def ready(self):
        """Initialize the app when Django starts."""
        pass

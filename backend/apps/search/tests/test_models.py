"""Tests for search application models."""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.subjects.models import Subject
from apps.search.models import SearchQuery, SearchResult


class SearchQueryModelTest(TestCase):
    """Test cases for SearchQuery model."""

    def setUp(self):
        """Set up test environment."""
        self.subject = Subject.objects.create(
            name="Test Subject", description="A test subject for search"
        )

    def test_create_search_query(self):
        """Test creating a search query."""
        query = SearchQuery.objects.create(
            query_text="test search query", query_type="general", subject=self.subject
        )

        self.assertEqual(query.query_text, "test search query")
        self.assertEqual(query.query_type, "general")
        self.assertEqual(query.subject, self.subject)
        self.assertIsNotNone(query.created_at)

    def test_search_query_str_representation(self):
        """Test string representation of SearchQuery."""
        query = SearchQuery.objects.create(
            query_text="This is a very long search query that should be truncated",
            query_type="person",
            subject=self.subject,
        )

        expected = "Search: This is a very long search query that should be tr..."
        self.assertEqual(str(query), expected)

    def test_search_query_ordering(self):
        """Test that search queries are ordered by creation date descending."""
        query1 = SearchQuery.objects.create(
            query_text="First query", query_type="general", subject=self.subject
        )

        query2 = SearchQuery.objects.create(
            query_text="Second query", query_type="general", subject=self.subject
        )

        queries = list(SearchQuery.objects.all())
        self.assertEqual(queries[0], query2)  # Most recent first
        self.assertEqual(queries[1], query1)

    def test_search_query_types(self):
        """Test all valid search query types."""
        valid_types = ["general", "person", "organization", "domain", "email"]

        for query_type in valid_types:
            query = SearchQuery.objects.create(
                query_text=f"test {query_type} query",
                query_type=query_type,
                subject=self.subject,
            )
            self.assertEqual(query.query_type, query_type)


class SearchResultModelTest(TestCase):
    """Test cases for SearchResult model."""

    def setUp(self):
        """Set up test environment."""
        self.subject = Subject.objects.create(
            name="Test Subject", description="A test subject for search"
        )

        self.query = SearchQuery.objects.create(
            query_text="test search", query_type="general", subject=self.subject
        )

    def test_create_search_result(self):
        """Test creating a search result."""
        result = SearchResult.objects.create(
            query=self.query,
            title="Test Search Result",
            url="https://example.com/test",
            canonical_url="https://example.com/test",
            description="This is a test search result",
            search_engine="google",
            rank=1,
        )

        self.assertEqual(result.query, self.query)
        self.assertEqual(result.title, "Test Search Result")
        self.assertEqual(result.url, "https://example.com/test")
        self.assertEqual(result.search_engine, "google")
        self.assertEqual(result.rank, 1)

    def test_search_result_str_representation(self):
        """Test string representation of SearchResult."""
        result = SearchResult.objects.create(
            query=self.query,
            title="Test Result",
            url="https://example.com/test",
            search_engine="bing",
            rank=1,
        )

        expected = "Test Result (bing)"
        self.assertEqual(str(result), expected)

    def test_search_result_ordering(self):
        """Test that search results are ordered by rank."""
        result1 = SearchResult.objects.create(
            query=self.query,
            title="Third Result",
            url="https://example.com/third",
            search_engine="google",
            rank=3,
        )

        result2 = SearchResult.objects.create(
            query=self.query,
            title="First Result",
            url="https://example.com/first",
            search_engine="google",
            rank=1,
        )

        result3 = SearchResult.objects.create(
            query=self.query,
            title="Second Result",
            url="https://example.com/second",
            search_engine="google",
            rank=2,
        )

        results = list(SearchResult.objects.all())
        self.assertEqual(results[0], result2)  # rank 1
        self.assertEqual(results[1], result3)  # rank 2
        self.assertEqual(results[2], result1)  # rank 3

    def test_search_result_unique_constraint(self):
        """Test that results are unique per query, URL, and search engine."""
        SearchResult.objects.create(
            query=self.query,
            title="Test Result",
            url="https://example.com/test",
            search_engine="google",
            rank=1,
        )

        # Attempting to create duplicate should work with different search engine
        SearchResult.objects.create(
            query=self.query,
            title="Test Result from Bing",
            url="https://example.com/test",
            search_engine="bing",
            rank=1,
        )

        # But duplicate with same query, URL, and search engine should fail
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            SearchResult.objects.create(
                query=self.query,
                title="Duplicate Result",
                url="https://example.com/test",
                search_engine="google",
                rank=2,
            )

    def test_search_result_optional_fields(self):
        """Test that optional fields work correctly."""
        result = SearchResult.objects.create(
            query=self.query,
            title="Minimal Result",
            url="https://example.com/minimal",
            search_engine="duckduckgo",
            rank=1
            # canonical_url and description are optional
        )

        self.assertEqual(result.canonical_url, "")
        self.assertEqual(result.description, "")

    def test_search_result_cascade_delete(self):
        """Test that results are deleted when query is deleted."""
        result = SearchResult.objects.create(
            query=self.query,
            title="Test Result",
            url="https://example.com/test",
            search_engine="google",
            rank=1,
        )

        result_id = result.id
        self.query.delete()

        # Result should be deleted due to CASCADE
        with self.assertRaises(SearchResult.DoesNotExist):
            SearchResult.objects.get(id=result_id)

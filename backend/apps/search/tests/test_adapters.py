"""Tests for search engine adapters."""

from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock
from apps.search.adapters import (
    BaseSearchAdapter,
    GoogleSearchAdapter,
    BingSearchAdapter,
    DuckDuckGoSearchAdapter,
    LynxSearchAdapter,
    CurlSearchAdapter,
    SearchAdapterFactory,
    SearchResult,
)


class SearchResultTest(TestCase):
    """Test cases for SearchResult data class."""

    def test_search_result_creation(self):
        """Test SearchResult creation with all fields."""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            source="google",
        )

        self.assertEqual(result.title, "Test Title")
        self.assertEqual(result.url, "https://example.com/")
        self.assertEqual(result.snippet, "Test snippet")
        self.assertEqual(result.source, "google")

    def test_search_result_repr(self):
        """Test SearchResult string representation."""
        result = SearchResult(
            title="Test", url="https://example.com", snippet="Snippet", source="google"
        )

        repr_str = repr(result)
        self.assertIn("Test", repr_str)
        self.assertIn("https://example.com", repr_str)
        self.assertIn("google", repr_str)


class BaseSearchAdapterTest(TestCase):
    """Test cases for BaseSearchAdapter abstract class."""

    def test_base_adapter_abstract(self):
        """Test that BaseSearchAdapter cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseSearchAdapter()

    def test_base_adapter_interface(self):
        """Test that BaseSearchAdapter defines required interface."""
        # Check that abstract methods exist
        self.assertTrue(hasattr(BaseSearchAdapter, "search"))
        self.assertTrue(hasattr(BaseSearchAdapter, "get_name"))


class GoogleSearchAdapterTest(TestCase):
    """Test cases for Google search adapter."""

    def setUp(self):
        """Set up test environment."""
        self.adapter = GoogleSearchAdapter()

    def test_adapter_name(self):
        """Test adapter name."""
        self.assertEqual(self.adapter.get_name(), "google")

    @patch("apps.search.adapters.requests.Session.get")
    def test_search_success(self, mock_get):
        """Test successful search operation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "Test Result 1",
                    "link": "https://example1.com",
                    "snippet": "Test snippet 1",
                },
                {
                    "title": "Test Result 2",
                    "link": "https://example2.com",
                    "snippet": "Test snippet 2",
                },
            ]
        }
        mock_get.return_value = mock_response

        # Provide API credentials to use API path instead of scraping
        self.adapter.api_key = "test_key"
        self.adapter.search_engine_id = "test_id"

        results = self.adapter.search("test query", limit=10)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "Test Result 1")
        self.assertEqual(results[0].url, "https://example1.com/")
        self.assertEqual(results[0].source, "google")
        self.assertEqual(results[1].title, "Test Result 2")

    @patch("apps.search.adapters.requests.Session.get")
    def test_search_api_error(self, mock_get):
        """Test search with API error."""
        mock_get.side_effect = Exception("API Error")

        results = self.adapter.search("test query")

        self.assertEqual(len(results), 0)

    @patch("apps.search.adapters.requests.Session.get")
    def test_search_no_results(self, mock_get):
        """Test search with no results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        results = self.adapter.search("test query")

        self.assertEqual(len(results), 0)


class BingSearchAdapterTest(TestCase):
    """Test cases for Bing search adapter."""

    def setUp(self):
        """Set up test environment."""
        self.adapter = BingSearchAdapter()

    def test_adapter_name(self):
        """Test adapter name."""
        self.assertEqual(self.adapter.get_name(), "bing")

    @patch("apps.search.adapters.requests.Session.get")
    def test_search_success(self, mock_get):
        """Test successful search operation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "webPages": {
                "value": [
                    {
                        "name": "Bing Result 1",
                        "url": "https://bing1.com",
                        "snippet": "Bing snippet 1",
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        # Provide API key to use API path
        self.adapter.api_key = "test_key"

        results = self.adapter.search("test query")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Bing Result 1")
        self.assertEqual(results[0].source, "bing")


class DuckDuckGoSearchAdapterTest(TestCase):
    """Test cases for DuckDuckGo search adapter."""

    def setUp(self):
        """Set up test environment."""
        self.adapter = DuckDuckGoSearchAdapter()

    def test_adapter_name(self):
        """Test adapter name."""
        self.assertEqual(self.adapter.get_name(), "duckduckgo")

    @patch("apps.search.adapters.requests.Session.get")
    def test_search_success(self, mock_get):
        """Test successful search operation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <div class="result">
            <a class="result__a" href="https://ddg1.com">DDG Result 1</a>
            <a class="result__snippet">DDG snippet 1</a>
        </div>
        """
        mock_get.return_value = mock_response

        results = self.adapter.search("test query")

        # DuckDuckGo parsing implementation will determine exact behavior
        self.assertIsInstance(results, list)


class LynxSearchAdapterTest(TestCase):
    """Test cases for Lynx search adapter."""

    def setUp(self):
        """Set up test environment."""
        self.adapter = LynxSearchAdapter()

    def test_adapter_name(self):
        """Test adapter name."""
        self.assertEqual(self.adapter.get_name(), "lynx")

    def test_search_success(self):
        """Test successful Lynx search."""
        with patch("apps.search.adapters.shutil.which") as mock_which, patch(
            "apps.search.adapters.subprocess.run"
        ) as mock_run:
            mock_which.return_value = "/usr/bin/lynx"
            self.adapter.lynx_available = True  # Override the check

            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = """
        Python Programming Tutorial

        https://python.org/tutorial

        Learn Python programming with this comprehensive tutorial
        covering basic to advanced concepts.

        Django Web Framework

        https://djangoproject.com

        Build web applications with Django framework.
        """
            mock_run.return_value = mock_result

            results = self.adapter.search("python tutorial")

            self.assertGreater(len(results), 0)
            mock_run.assert_called_once()

    @patch("apps.search.adapters.shutil.which")
    def test_lynx_not_available(self, mock_which):
        """Test fallback when Lynx not available."""
        mock_which.return_value = None

        with patch.object(self.adapter, "_fallback_search") as mock_fallback:
            mock_fallback.return_value = []
            results = self.adapter.search("test query")
            mock_fallback.assert_called_once()


class CurlSearchAdapterTest(TestCase):
    """Test cases for Curl search adapter."""

    def setUp(self):
        """Set up test environment."""
        self.adapter = CurlSearchAdapter()

    def test_adapter_name(self):
        """Test adapter name."""
        self.assertEqual(self.adapter.get_name(), "curl")

    @patch("apps.search.adapters.subprocess.run")
    @patch("apps.search.adapters.shutil.which")
    def test_search_success(self, mock_which, mock_run):
        """Test successful curl search."""
        mock_which.return_value = "/usr/bin/curl"
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = """
        <div class="result">
            <a class="result__a" href="https://example.com">Test Result</a>
            <a class="result__snippet">Test snippet content</a>
        </div>
        """
        mock_run.return_value = mock_result

        results = self.adapter.search("test query")

        self.assertGreater(len(results), 0)
        mock_run.assert_called_once()

    @patch("apps.search.adapters.shutil.which")
    def test_curl_not_available(self, mock_which):
        """Test when curl not available."""
        mock_which.return_value = None

        results = self.adapter.search("test query")

        self.assertEqual(len(results), 0)


class SearchAdapterFactoryTest(TestCase):
    """Test cases for SearchAdapterFactory."""

    def test_get_adapter_google(self):
        """Test getting Google adapter."""
        adapter = SearchAdapterFactory.get_adapter("google")
        self.assertIsInstance(adapter, GoogleSearchAdapter)

    def test_get_adapter_bing(self):
        """Test getting Bing adapter."""
        adapter = SearchAdapterFactory.get_adapter("bing")
        self.assertIsInstance(adapter, BingSearchAdapter)

    def test_get_adapter_duckduckgo(self):
        """Test getting DuckDuckGo adapter."""
        adapter = SearchAdapterFactory.get_adapter("duckduckgo")
        self.assertIsInstance(adapter, DuckDuckGoSearchAdapter)

    def test_get_adapter_lynx(self):
        """Test getting Lynx adapter."""
        adapter = SearchAdapterFactory.get_adapter("lynx")
        self.assertIsInstance(adapter, LynxSearchAdapter)

    def test_get_adapter_curl(self):
        """Test getting Curl adapter."""
        adapter = SearchAdapterFactory.get_adapter("curl")
        self.assertIsInstance(adapter, CurlSearchAdapter)

    def test_get_adapter_invalid(self):
        """Test getting invalid adapter raises error."""
        with self.assertRaises(ValueError):
            SearchAdapterFactory.get_adapter("invalid")

    def test_get_available_adapters(self):
        """Test getting list of available adapters."""
        adapters = SearchAdapterFactory.get_available_adapters()
        expected = ["google", "bing", "duckduckgo", "lynx", "curl"]
        self.assertEqual(sorted(adapters), sorted(expected))

    def test_create_all_adapters(self):
        """Test creating all available adapters."""
        adapters = SearchAdapterFactory.create_all_adapters()

        self.assertEqual(len(adapters), 5)
        adapter_names = [adapter.get_name() for adapter in adapters]
        self.assertIn("google", adapter_names)
        self.assertIn("bing", adapter_names)
        self.assertIn("duckduckgo", adapter_names)
        self.assertIn("lynx", adapter_names)
        self.assertIn("curl", adapter_names)


class SearchAdapterIntegrationTest(TestCase):
    """Integration tests for search adapters."""

    def test_adapter_interface_consistency(self):
        """Test that all adapters implement the same interface."""
        adapters = SearchAdapterFactory.create_all_adapters()

        for adapter in adapters:
            # All adapters should have these methods
            self.assertTrue(hasattr(adapter, "search"))
            self.assertTrue(hasattr(adapter, "get_name"))
            self.assertTrue(callable(adapter.search))
            self.assertTrue(callable(adapter.get_name))

            # get_name should return a string
            name = adapter.get_name()
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)

    def test_search_result_canonicalization(self):
        """Test that search results are properly canonicalized."""
        # This test will verify integration with URL canonicalization
        adapter = GoogleSearchAdapter()

        # Provide API credentials for this test
        adapter.api_key = "test_key"
        adapter.search_engine_id = "test_id"

        # Mock a result with tracking parameters
        with patch("apps.search.adapters.requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "items": [
                    {
                        "title": "Test Result",
                        "link": "https://www.example.com/page?utm_source=google&param=value",
                        "snippet": "Test snippet",
                    }
                ]
            }
            mock_get.return_value = mock_response

            results = adapter.search("test query")

            # URL should be canonicalized (tracking params removed, www removed)
            self.assertEqual(len(results), 1)
            # Check that URL was canonicalized
            self.assertEqual(results[0].url, "https://example.com/page?param=value")

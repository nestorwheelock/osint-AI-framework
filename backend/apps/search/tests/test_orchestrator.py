"""Tests for meta-search orchestration service."""

from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock
from apps.search.orchestrator import (
    MetaSearchOrchestrator,
    SearchStrategy,
    ResultRanker,
    SearchConfig,
    SearchResult,
)
from apps.search.adapters import SearchResult


class SearchConfigTest(TestCase):
    """Test cases for SearchConfig data class."""

    def test_search_config_defaults(self):
        """Test SearchConfig with default values."""
        config = SearchConfig()

        self.assertEqual(config.max_results_per_adapter, 10)
        self.assertEqual(config.timeout_seconds, 30)
        self.assertTrue(config.enable_deduplication)
        self.assertTrue(config.enable_ranking)
        self.assertEqual(config.preferred_adapters, ["duckduckgo", "lynx", "curl"])

    def test_search_config_custom(self):
        """Test SearchConfig with custom values."""
        config = SearchConfig(
            max_results_per_adapter=20,
            timeout_seconds=60,
            enable_deduplication=False,
            preferred_adapters=["google", "bing"],
        )

        self.assertEqual(config.max_results_per_adapter, 20)
        self.assertEqual(config.timeout_seconds, 60)
        self.assertFalse(config.enable_deduplication)
        self.assertEqual(config.preferred_adapters, ["google", "bing"])


class SearchStrategyTest(TestCase):
    """Test cases for search strategy enum."""

    def test_strategy_values(self):
        """Test strategy enum values."""
        self.assertEqual(SearchStrategy.PARALLEL.value, "parallel")
        self.assertEqual(SearchStrategy.SEQUENTIAL.value, "sequential")
        self.assertEqual(SearchStrategy.ADAPTIVE.value, "adaptive")


class ResultRankerTest(TestCase):
    """Test cases for result ranking functionality."""

    def setUp(self):
        """Set up test environment."""
        self.ranker = ResultRanker()

    def test_ranking_algorithm(self):
        """Test result ranking algorithm."""
        results = [
            SearchResult(
                title="Python Programming Guide",
                url="https://python.org/tutorial",
                snippet="Official Python tutorial for beginners",
                source="duckduckgo",
            ),
            SearchResult(
                title="Python Guide",
                url="https://python.org/tutorial",  # Duplicate URL
                snippet="Learn Python programming",
                source="google",
            ),
            SearchResult(
                title="Advanced Python Techniques",
                url="https://realpython.com/advanced",
                snippet="Advanced Python programming techniques",
                source="bing",
            ),
        ]

        ranked = self.ranker.rank_results(results, "Python programming")

        # Should return ranked results
        self.assertEqual(len(ranked), 3)
        self.assertIsInstance(ranked[0], SearchResult)

    def test_ranking_factors(self):
        """Test various ranking factors."""
        results = [
            SearchResult(
                title="Python",  # Short title
                url="https://example.com/python",
                snippet="Python",  # Short snippet
                source="duckduckgo",
            ),
            SearchResult(
                title="Python Programming Tutorial - Complete Guide",  # Long, descriptive
                url="https://tutorial.com/python-guide",
                snippet="Comprehensive Python programming tutorial covering all aspects",
                source="google",
            ),
        ]

        ranked = self.ranker.rank_results(results, "Python programming tutorial")

        # More descriptive result should rank higher
        self.assertIn("Complete Guide", ranked[0].title)

    def test_empty_results(self):
        """Test ranking with empty results."""
        ranked = self.ranker.rank_results([], "test query")
        self.assertEqual(len(ranked), 0)


class MetaSearchOrchestratorTest(TestCase):
    """Test cases for MetaSearchOrchestrator."""

    def setUp(self):
        """Set up test environment."""
        self.orchestrator = MetaSearchOrchestrator()

    def test_initialization(self):
        """Test orchestrator initialization."""
        self.assertIsNotNone(self.orchestrator.config)
        self.assertIsNotNone(self.orchestrator.ranker)
        self.assertEqual(
            len(self.orchestrator.adapters), 0
        )  # No adapters loaded initially

    def test_load_adapters(self):
        """Test loading search adapters."""
        with patch(
            "apps.search.orchestrator.SearchAdapterFactory.create_all_adapters"
        ) as mock_create:
            mock_adapters = [Mock(), Mock(), Mock()]
            mock_adapters[0].get_name.return_value = "duckduckgo"
            mock_adapters[1].get_name.return_value = "google"
            mock_adapters[2].get_name.return_value = "bing"
            mock_create.return_value = mock_adapters

            self.orchestrator.load_adapters()

            self.assertEqual(len(self.orchestrator.adapters), 3)
            mock_create.assert_called_once()

    def test_load_specific_adapters(self):
        """Test loading specific adapters."""
        with patch(
            "apps.search.orchestrator.SearchAdapterFactory.get_adapter"
        ) as mock_get:
            mock_adapter = Mock()
            mock_adapter.get_name.return_value = "duckduckgo"
            mock_get.return_value = mock_adapter

            self.orchestrator.load_adapters(["duckduckgo"])

            self.assertEqual(len(self.orchestrator.adapters), 1)
            mock_get.assert_called_once_with("duckduckgo")

    @patch("apps.search.orchestrator.SearchAdapterFactory.get_adapter")
    def test_parallel_search(self, mock_get_adapter):
        """Test parallel search execution."""
        # Set up mock adapters
        mock_adapter1 = Mock()
        mock_adapter1.get_name.return_value = "duckduckgo"
        mock_adapter1.search.return_value = [
            SearchResult(
                "Result 1",
                "https://example1.com",
                "This is a comprehensive snippet with enough content to pass quality filters",
                "duckduckgo",
            )
        ]

        mock_adapter2 = Mock()
        mock_adapter2.get_name.return_value = "google"
        mock_adapter2.search.return_value = [
            SearchResult(
                "Result 2",
                "https://example2.com",
                "This is another comprehensive snippet with enough content to pass quality filters",
                "google",
            )
        ]

        mock_get_adapter.side_effect = [mock_adapter1, mock_adapter2]

        # Load adapters
        self.orchestrator.load_adapters(["duckduckgo", "google"])

        # Execute search
        results = self.orchestrator.search(
            query="test query", strategy=SearchStrategy.PARALLEL
        )

        # Verify results
        self.assertEqual(len(results), 2)
        sources = [r.source for r in results]
        self.assertIn("duckduckgo", sources)
        self.assertIn("google", sources)

    @patch("apps.search.orchestrator.SearchAdapterFactory.get_adapter")
    def test_sequential_search(self, mock_get_adapter):
        """Test sequential search execution."""
        mock_adapter = Mock()
        mock_adapter.get_name.return_value = "duckduckgo"
        mock_adapter.search.return_value = [
            SearchResult(
                "Result 1",
                "https://example1.com",
                "This is a comprehensive snippet with enough content to pass quality filters",
                "duckduckgo",
            )
        ]

        mock_get_adapter.return_value = mock_adapter
        self.orchestrator.load_adapters(["duckduckgo"])

        results = self.orchestrator.search(
            query="test query", strategy=SearchStrategy.SEQUENTIAL
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source, "duckduckgo")

    @patch("apps.search.orchestrator.SearchAdapterFactory.get_adapter")
    def test_deduplication(self, mock_get_adapter):
        """Test result deduplication."""
        mock_adapter1 = Mock()
        mock_adapter1.get_name.return_value = "duckduckgo"
        mock_adapter1.search.return_value = [
            SearchResult("Same Result", "https://example.com", "Snippet", "duckduckgo")
        ]

        mock_adapter2 = Mock()
        mock_adapter2.get_name.return_value = "google"
        mock_adapter2.search.return_value = [
            SearchResult("Same Result", "https://example.com", "Snippet", "google"),
            SearchResult("Different Result", "https://other.com", "Other", "google"),
        ]

        mock_get_adapter.side_effect = [mock_adapter1, mock_adapter2]

        self.orchestrator.load_adapters(["duckduckgo", "google"])

        results = self.orchestrator.search(
            query="test query", config=SearchConfig(enable_deduplication=True)
        )

        # Should deduplicate by URL
        urls = [r.url for r in results]
        self.assertEqual(len(set(urls)), len(urls))  # All URLs should be unique

    @patch("apps.search.orchestrator.SearchAdapterFactory.get_adapter")
    def test_error_handling(self, mock_get_adapter):
        """Test error handling in search execution."""
        mock_adapter1 = Mock()
        mock_adapter1.get_name.return_value = "duckduckgo"
        mock_adapter1.search.side_effect = Exception("Search failed")

        mock_adapter2 = Mock()
        mock_adapter2.get_name.return_value = "google"
        mock_adapter2.search.return_value = [
            SearchResult(
                "Result 2",
                "https://example2.com",
                "This is a comprehensive snippet with enough content to pass quality filters",
                "google",
            )
        ]

        mock_get_adapter.side_effect = [mock_adapter1, mock_adapter2]

        self.orchestrator.load_adapters(["duckduckgo", "google"])

        results = self.orchestrator.search(query="test query")

        # Should continue with other adapters despite one failing
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source, "google")

    @patch("apps.search.orchestrator.SearchAdapterFactory.get_adapter")
    def test_adaptive_search(self, mock_get_adapter):
        """Test adaptive search strategy."""
        # Fast adapter
        mock_fast_adapter = Mock()
        mock_fast_adapter.get_name.return_value = "duckduckgo"
        mock_fast_adapter.search.return_value = [
            SearchResult(
                "Fast Result",
                "https://fast.com",
                "This is a comprehensive snippet with enough content to pass quality filters",
                "duckduckgo",
            )
        ]

        # Slow adapter (would timeout in real scenario)
        mock_slow_adapter = Mock()
        mock_slow_adapter.get_name.return_value = "google"
        mock_slow_adapter.search.return_value = [
            SearchResult(
                "Slow Result",
                "https://slow.com",
                "This is another comprehensive snippet with enough content to pass quality filters",
                "google",
            )
        ]

        mock_get_adapter.side_effect = [mock_fast_adapter, mock_slow_adapter]

        self.orchestrator.load_adapters(["duckduckgo", "google"])

        results = self.orchestrator.search(
            query="test query", strategy=SearchStrategy.ADAPTIVE
        )

        # Should get results from both adapters
        self.assertGreaterEqual(len(results), 1)

    def test_get_search_statistics(self):
        """Test search statistics collection."""
        stats = self.orchestrator.get_search_statistics()

        expected_keys = [
            "total_searches",
            "successful_searches",
            "failed_searches",
            "average_response_time",
            "adapter_performance",
        ]

        for key in expected_keys:
            self.assertIn(key, stats)

    def test_configure_orchestrator(self):
        """Test orchestrator configuration."""
        new_config = SearchConfig(max_results_per_adapter=5, timeout_seconds=15)

        self.orchestrator.configure(new_config)

        self.assertEqual(self.orchestrator.config.max_results_per_adapter, 5)
        self.assertEqual(self.orchestrator.config.timeout_seconds, 15)


class MetaSearchIntegrationTest(TestCase):
    """Integration tests for meta-search functionality."""

    def test_end_to_end_search(self):
        """Test complete search workflow."""
        orchestrator = MetaSearchOrchestrator()

        with patch(
            "apps.search.orchestrator.SearchAdapterFactory.get_adapter"
        ) as mock_get:
            # Mock DuckDuckGo adapter (primary choice since it works)
            mock_adapter = Mock()
            mock_adapter.get_name.return_value = "duckduckgo"
            mock_adapter.search.return_value = [
                SearchResult(
                    title="OSINT LLM Framework - Open Source Intelligence",
                    url="https://osintframework.com",
                    snippet="Collection of OSINT tools and resources",
                    source="duckduckgo",
                ),
                SearchResult(
                    title="OSINT Tools for Investigators",
                    url="https://osinttools.com",
                    snippet="Professional OSINT investigation tools",
                    source="duckduckgo",
                ),
            ]

            mock_get.return_value = mock_adapter

            # Load and test
            orchestrator.load_adapters(["duckduckgo"])
            results = orchestrator.search("OSINT tools")

            # Verify end-to-end functionality
            self.assertGreater(len(results), 0)
            self.assertTrue(all(r.source == "duckduckgo" for r in results))
            self.assertTrue(all("osint" in r.title.lower() for r in results))

    def test_multi_adapter_integration(self):
        """Test integration with multiple adapters."""
        orchestrator = MetaSearchOrchestrator()

        with patch(
            "apps.search.orchestrator.SearchAdapterFactory.get_adapter"
        ) as mock_get:
            adapters = []

            # DuckDuckGo adapter
            ddg_adapter = Mock()
            ddg_adapter.get_name.return_value = "duckduckgo"
            ddg_adapter.search.return_value = [
                SearchResult(
                    "DDG Result",
                    "https://ddg.com",
                    "This is a comprehensive snippet with enough content to pass quality filters",
                    "duckduckgo",
                )
            ]
            adapters.append(ddg_adapter)

            # Lynx adapter
            lynx_adapter = Mock()
            lynx_adapter.get_name.return_value = "lynx"
            lynx_adapter.search.return_value = [
                SearchResult(
                    "Lynx Result",
                    "https://lynx.com",
                    "This is another comprehensive snippet with enough content to pass quality filters",
                    "lynx",
                )
            ]
            adapters.append(lynx_adapter)

            mock_get.side_effect = adapters

            orchestrator.load_adapters(["duckduckgo", "lynx"])
            results = orchestrator.search("test query")

            # Should get results from multiple sources
            sources = [r.source for r in results]
            self.assertIn("duckduckgo", sources)
            self.assertIn("lynx", sources)

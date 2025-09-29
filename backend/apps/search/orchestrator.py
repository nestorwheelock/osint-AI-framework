"""
Meta-Search Orchestration Service for OSINT AI Framework.

Coordinates multiple search adapters to provide comprehensive, deduplicated,
and ranked search results from various sources. Supports different search
strategies and performance optimization.
"""

import time
import asyncio
import concurrent.futures
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Set, Any
from collections import defaultdict
import threading

from .adapters import SearchAdapterFactory, BaseSearchAdapter, SearchResult
from .utils import deduplicate_urls


class SearchStrategy(Enum):
    """Search execution strategies."""

    PARALLEL = "parallel"  # Execute all adapters simultaneously
    SEQUENTIAL = "sequential"  # Execute adapters one by one
    ADAPTIVE = "adaptive"  # Start with fast adapters, add slower ones


@dataclass
class SearchConfig:
    """Configuration for meta-search orchestration."""

    max_results_per_adapter: int = 10
    timeout_seconds: int = 30
    enable_deduplication: bool = True
    enable_ranking: bool = True
    preferred_adapters: List[str] = field(
        default_factory=lambda: ["duckduckgo", "lynx", "curl"]
    )
    fallback_adapters: List[str] = field(default_factory=lambda: ["google", "bing"])
    min_snippet_length: int = 20
    max_total_results: int = 50


class ResultRanker:
    """Ranks search results based on relevance and quality metrics."""

    def __init__(self):
        """Initialize result ranker."""
        self.ranking_factors = {
            "title_relevance": 0.3,
            "snippet_relevance": 0.25,
            "url_quality": 0.15,
            "source_reliability": 0.15,
            "content_length": 0.1,
            "domain_authority": 0.05,
        }

        # Source reliability scores
        self.source_scores = {
            "duckduckgo": 0.9,
            "google": 0.95,
            "bing": 0.85,
            "lynx": 0.8,
            "curl": 0.75,
        }

    def rank_results(
        self, results: List[SearchResult], query: str
    ) -> List[SearchResult]:
        """
        Rank search results by relevance and quality.

        Args:
            results: List of search results to rank
            query: Original search query for relevance scoring

        Returns:
            Ranked list of search results
        """
        if not results:
            return []

        query_terms = set(query.lower().split())
        scored_results = []

        for result in results:
            score = self._calculate_result_score(result, query_terms)
            scored_results.append((score, result))

        # Sort by score (descending) and return results
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [result for score, result in scored_results]

    def _calculate_result_score(
        self, result: SearchResult, query_terms: Set[str]
    ) -> float:
        """Calculate relevance score for a single result."""
        score = 0.0

        # Title relevance
        title_words = set(result.title.lower().split())
        title_matches = len(query_terms.intersection(title_words))
        title_score = title_matches / len(query_terms) if query_terms else 0
        score += title_score * self.ranking_factors["title_relevance"]

        # Snippet relevance
        snippet_words = set(result.snippet.lower().split())
        snippet_matches = len(query_terms.intersection(snippet_words))
        snippet_score = snippet_matches / len(query_terms) if query_terms else 0
        score += snippet_score * self.ranking_factors["snippet_relevance"]

        # URL quality (shorter, cleaner URLs score higher)
        url_score = max(0, 1 - (len(result.url) / 100))
        score += url_score * self.ranking_factors["url_quality"]

        # Source reliability
        source_score = self.source_scores.get(result.source, 0.5)
        score += source_score * self.ranking_factors["source_reliability"]

        # Content length (longer snippets generally better)
        content_score = min(1.0, len(result.snippet) / 200)
        score += content_score * self.ranking_factors["content_length"]

        # Domain authority (simplified heuristic)
        domain_score = self._calculate_domain_authority(result.url)
        score += domain_score * self.ranking_factors["domain_authority"]

        return score

    def _calculate_domain_authority(self, url: str) -> float:
        """Calculate simple domain authority score."""
        # Simplified domain authority based on domain characteristics
        domain_indicators = {
            ".edu": 0.9,
            ".gov": 0.95,
            ".org": 0.8,
            "wikipedia": 0.85,
            "github": 0.8,
            "stackoverflow": 0.8,
        }

        url_lower = url.lower()
        for indicator, score in domain_indicators.items():
            if indicator in url_lower:
                return score

        # Default score for unknown domains
        return 0.5


class MetaSearchOrchestrator:
    """
    Orchestrates multiple search adapters for comprehensive search results.

    Provides unified interface for executing searches across multiple engines
    with deduplication, ranking, and performance optimization.
    """

    def __init__(self, config: Optional[SearchConfig] = None):
        """Initialize meta-search orchestrator."""
        self.config = config or SearchConfig()
        self.ranker = ResultRanker()
        self.adapters: List[BaseSearchAdapter] = []

        # Performance tracking
        self.search_stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "total_response_time": 0.0,
            "adapter_performance": defaultdict(
                lambda: {"calls": 0, "successes": 0, "total_time": 0.0}
            ),
        }
        self._stats_lock = threading.Lock()

    def load_adapters(self, adapter_names: Optional[List[str]] = None) -> None:
        """
        Load search adapters for orchestration.

        Args:
            adapter_names: Specific adapters to load, or None for all available
        """
        self.adapters = []

        if adapter_names:
            # Load specific adapters
            for name in adapter_names:
                try:
                    adapter = SearchAdapterFactory.get_adapter(name)
                    self.adapters.append(adapter)
                except Exception as e:
                    print(f"Failed to load adapter '{name}': {e}")
        else:
            # Load all available adapters
            self.adapters = SearchAdapterFactory.create_all_adapters()

        print(f"Loaded {len(self.adapters)} search adapters")

    def search(
        self,
        query: str,
        strategy: SearchStrategy = SearchStrategy.PARALLEL,
        config: Optional[SearchConfig] = None,
    ) -> List[SearchResult]:
        """
        Execute meta-search across multiple adapters.

        Args:
            query: Search query string
            strategy: Search execution strategy
            config: Optional config override

        Returns:
            Ranked and deduplicated search results
        """
        search_config = config or self.config
        start_time = time.time()

        with self._stats_lock:
            self.search_stats["total_searches"] += 1

        try:
            # Execute search based on strategy
            if strategy == SearchStrategy.PARALLEL:
                results = self._execute_parallel_search(query, search_config)
            elif strategy == SearchStrategy.SEQUENTIAL:
                results = self._execute_sequential_search(query, search_config)
            elif strategy == SearchStrategy.ADAPTIVE:
                results = self._execute_adaptive_search(query, search_config)
            else:
                raise ValueError(f"Unknown search strategy: {strategy}")

            # Post-process results
            if search_config.enable_deduplication:
                results = self._deduplicate_results(results)

            if search_config.enable_ranking:
                results = self.ranker.rank_results(results, query)

            # Limit total results
            results = results[: search_config.max_total_results]

            # Update statistics
            with self._stats_lock:
                self.search_stats["successful_searches"] += 1
                self.search_stats["total_response_time"] += time.time() - start_time

            return results

        except Exception as e:
            with self._stats_lock:
                self.search_stats["failed_searches"] += 1
            print(f"Meta-search failed: {e}")
            return []

    def _execute_parallel_search(
        self, query: str, config: SearchConfig
    ) -> List[SearchResult]:
        """Execute search across all adapters in parallel."""
        if not self.adapters:
            return []

        results = []

        # Use ThreadPoolExecutor for parallel execution
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.adapters)
        ) as executor:
            # Submit all search tasks
            future_to_adapter = {
                executor.submit(
                    self._search_with_adapter, adapter, query, config
                ): adapter
                for adapter in self.adapters
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(
                future_to_adapter, timeout=config.timeout_seconds
            ):
                adapter = future_to_adapter[future]
                try:
                    adapter_results = future.result()
                    results.extend(adapter_results)
                except Exception as e:
                    print(f"Adapter {adapter.get_name()} failed: {e}")
                    self._update_adapter_stats(adapter.get_name(), success=False)

        return results

    def _execute_sequential_search(
        self, query: str, config: SearchConfig
    ) -> List[SearchResult]:
        """Execute search across adapters sequentially."""
        results = []

        for adapter in self.adapters:
            try:
                adapter_results = self._search_with_adapter(adapter, query, config)
                results.extend(adapter_results)
            except Exception as e:
                print(f"Adapter {adapter.get_name()} failed: {e}")
                self._update_adapter_stats(adapter.get_name(), success=False)

        return results

    def _execute_adaptive_search(
        self, query: str, config: SearchConfig
    ) -> List[SearchResult]:
        """Execute adaptive search starting with preferred adapters."""
        results = []

        # Start with preferred adapters in parallel
        preferred_adapters = [
            a for a in self.adapters if a.get_name() in config.preferred_adapters
        ]

        if preferred_adapters:
            # Quick search with preferred adapters (shorter timeout)
            quick_config = SearchConfig(
                max_results_per_adapter=config.max_results_per_adapter // 2,
                timeout_seconds=config.timeout_seconds // 2,
                enable_deduplication=config.enable_deduplication,
                enable_ranking=False,  # Rank at the end
            )

            temp_adapters = self.adapters
            self.adapters = preferred_adapters
            preferred_results = self._execute_parallel_search(query, quick_config)
            self.adapters = temp_adapters

            results.extend(preferred_results)

        # If we need more results, try fallback adapters
        if len(results) < config.max_total_results // 2:
            fallback_adapters = [
                a for a in self.adapters if a.get_name() in config.fallback_adapters
            ]

            if fallback_adapters:
                temp_adapters = self.adapters
                self.adapters = fallback_adapters
                fallback_results = self._execute_parallel_search(query, config)
                self.adapters = temp_adapters

                results.extend(fallback_results)

        return results

    def _search_with_adapter(
        self, adapter: BaseSearchAdapter, query: str, config: SearchConfig
    ) -> List[SearchResult]:
        """Execute search with a single adapter and track performance."""
        adapter_name = adapter.get_name()
        start_time = time.time()

        try:
            results = adapter.search(query, limit=config.max_results_per_adapter)

            # Filter results by quality
            filtered_results = [
                r for r in results if len(r.snippet) >= config.min_snippet_length
            ]

            search_time = time.time() - start_time
            self._update_adapter_stats(
                adapter_name, success=True, search_time=search_time
            )

            return filtered_results

        except Exception as e:
            search_time = time.time() - start_time
            self._update_adapter_stats(
                adapter_name, success=False, search_time=search_time
            )
            raise e

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on URL canonicalization."""
        if not results:
            return []

        # Extract URLs for deduplication
        urls = [r.url for r in results]
        unique_urls = deduplicate_urls(urls)

        # Keep first occurrence of each unique URL
        seen_urls = set()
        unique_results = []

        for result in results:
            if result.url in unique_urls and result.url not in seen_urls:
                unique_results.append(result)
                seen_urls.add(result.url)

        return unique_results

    def _update_adapter_stats(
        self, adapter_name: str, success: bool, search_time: float = 0.0
    ) -> None:
        """Update performance statistics for an adapter."""
        with self._stats_lock:
            stats = self.search_stats["adapter_performance"][adapter_name]
            stats["calls"] += 1
            stats["total_time"] += search_time

            if success:
                stats["successes"] += 1

    def get_search_statistics(self) -> Dict[str, Any]:
        """Get comprehensive search performance statistics."""
        with self._stats_lock:
            stats = dict(self.search_stats)

            # Calculate derived metrics
            total_searches = stats["total_searches"]
            if total_searches > 0:
                stats["success_rate"] = stats["successful_searches"] / total_searches
                stats["average_response_time"] = (
                    stats["total_response_time"] / total_searches
                )
            else:
                stats["success_rate"] = 0.0
                stats["average_response_time"] = 0.0

            # Adapter performance metrics
            adapter_metrics = {}
            for adapter_name, perf in stats["adapter_performance"].items():
                calls = perf["calls"]
                if calls > 0:
                    adapter_metrics[adapter_name] = {
                        "success_rate": perf["successes"] / calls,
                        "average_time": perf["total_time"] / calls,
                        "total_calls": calls,
                    }

            stats["adapter_performance"] = adapter_metrics

            return stats

    def configure(self, config: SearchConfig) -> None:
        """Update orchestrator configuration."""
        self.config = config

    def reset_statistics(self) -> None:
        """Reset all performance statistics."""
        with self._stats_lock:
            self.search_stats = {
                "total_searches": 0,
                "successful_searches": 0,
                "failed_searches": 0,
                "total_response_time": 0.0,
                "adapter_performance": defaultdict(
                    lambda: {"calls": 0, "successes": 0, "total_time": 0.0}
                ),
            }

    def get_available_adapters(self) -> List[str]:
        """Get list of currently loaded adapter names."""
        return [adapter.get_name() for adapter in self.adapters]


# Convenience functions for easy usage


def search_osint(
    query: str, max_results: int = 20, adapters: Optional[List[str]] = None
) -> List[SearchResult]:
    """
    Convenience function for OSINT searches.

    Args:
        query: Search query
        max_results: Maximum number of results to return
        adapters: Specific adapters to use, defaults to OSINT-optimized set

    Returns:
        Ranked search results
    """
    # OSINT-optimized configuration
    config = SearchConfig(
        max_results_per_adapter=max_results // 2,
        max_total_results=max_results,
        preferred_adapters=adapters or ["duckduckgo", "lynx", "curl"],
        enable_deduplication=True,
        enable_ranking=True,
    )

    orchestrator = MetaSearchOrchestrator(config)
    orchestrator.load_adapters(adapters)

    return orchestrator.search(query, strategy=SearchStrategy.ADAPTIVE)


def quick_search(query: str, adapter_name: str = "duckduckgo") -> List[SearchResult]:
    """
    Quick search using a single adapter.

    Args:
        query: Search query
        adapter_name: Specific adapter to use

    Returns:
        Search results from single adapter
    """
    orchestrator = MetaSearchOrchestrator()
    orchestrator.load_adapters([adapter_name])

    return orchestrator.search(query, strategy=SearchStrategy.SEQUENTIAL)

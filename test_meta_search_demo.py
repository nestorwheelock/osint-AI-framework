#!/usr/bin/env python3
"""
Demo script to test meta-search orchestration service.

Tests comprehensive search across multiple adapters with deduplication,
ranking, and performance metrics.
"""

import sys

sys.path.append("backend")

from apps.search.orchestrator import (
    MetaSearchOrchestrator,
    SearchStrategy,
    SearchConfig,
    search_osint,
    quick_search,
)


def test_basic_orchestration():
    """Test basic meta-search orchestration."""
    print("\n=== Basic Meta-Search Orchestration ===")

    orchestrator = MetaSearchOrchestrator()

    # Load available adapters (focusing on working ones)
    orchestrator.load_adapters(["duckduckgo", "curl"])

    print(f"Loaded adapters: {orchestrator.get_available_adapters()}")

    # Execute search
    results = orchestrator.search(
        "OSINT framework tools", strategy=SearchStrategy.PARALLEL
    )

    print(f"\nFound {len(results)} total results:")
    for i, result in enumerate(results[:5], 1):
        print(f"\n{i}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Source: {result.source}")
        print(f"   Snippet: {result.snippet[:100]}...")


def test_search_strategies():
    """Test different search strategies."""
    print("\n=== Testing Search Strategies ===")

    orchestrator = MetaSearchOrchestrator()
    orchestrator.load_adapters(["duckduckgo"])

    query = "cybersecurity tools"

    strategies = [
        SearchStrategy.SEQUENTIAL,
        SearchStrategy.PARALLEL,
        SearchStrategy.ADAPTIVE,
    ]

    for strategy in strategies:
        print(f"\n--- {strategy.value.upper()} Strategy ---")
        results = orchestrator.search(query, strategy=strategy)
        print(f"Results: {len(results)}")

        if results:
            print(f"Top result: {results[0].title}")


def test_configuration_options():
    """Test different configuration options."""
    print("\n=== Testing Configuration Options ===")

    # Custom configuration
    config = SearchConfig(
        max_results_per_adapter=5,
        max_total_results=15,
        enable_deduplication=True,
        enable_ranking=True,
        min_snippet_length=10,
    )

    orchestrator = MetaSearchOrchestrator(config)
    orchestrator.load_adapters(["duckduckgo"])

    results = orchestrator.search("digital forensics", config=config)

    print(f"Configured search found {len(results)} results")
    print(f"Max configured: {config.max_total_results}")


def test_convenience_functions():
    """Test convenience functions for easy usage."""
    print("\n=== Testing Convenience Functions ===")

    # OSINT-optimized search
    print("\n--- OSINT Search ---")
    results = search_osint("threat intelligence", max_results=10)
    print(f"OSINT search results: {len(results)}")

    # Quick single-adapter search
    print("\n--- Quick Search ---")
    results = quick_search("malware analysis", adapter_name="duckduckgo")
    print(f"Quick search results: {len(results)}")


def test_performance_metrics():
    """Test performance tracking and statistics."""
    print("\n=== Performance Metrics ===")

    orchestrator = MetaSearchOrchestrator()
    orchestrator.load_adapters(["duckduckgo"])

    # Execute multiple searches
    queries = ["OSINT", "cybersecurity", "digital forensics"]

    for query in queries:
        results = orchestrator.search(query)
        print(f"Query '{query}': {len(results)} results")

    # Get performance statistics
    stats = orchestrator.get_search_statistics()

    print(f"\n--- Performance Statistics ---")
    print(f"Total searches: {stats['total_searches']}")
    print(f"Success rate: {stats['success_rate']:.2%}")
    print(f"Average response time: {stats['average_response_time']:.3f}s")

    print(f"\n--- Adapter Performance ---")
    for adapter, perf in stats["adapter_performance"].items():
        print(f"{adapter}:")
        print(f"  Success rate: {perf['success_rate']:.2%}")
        print(f"  Average time: {perf['average_time']:.3f}s")
        print(f"  Total calls: {perf['total_calls']}")


def test_deduplication_ranking():
    """Test deduplication and ranking features."""
    print("\n=== Deduplication and Ranking ===")

    # Test with deduplication enabled
    config_with_dedup = SearchConfig(enable_deduplication=True, enable_ranking=True)
    orchestrator = MetaSearchOrchestrator(config_with_dedup)
    orchestrator.load_adapters(["duckduckgo"])

    results_dedup = orchestrator.search("python programming", config=config_with_dedup)

    # Test without deduplication
    config_no_dedup = SearchConfig(enable_deduplication=False, enable_ranking=False)
    orchestrator.configure(config_no_dedup)

    results_no_dedup = orchestrator.search("python programming", config=config_no_dedup)

    print(f"With deduplication/ranking: {len(results_dedup)} results")
    print(f"Without deduplication/ranking: {len(results_no_dedup)} results")

    if results_dedup:
        print(f"Top ranked result: {results_dedup[0].title}")


def main():
    """Run all meta-search orchestration demos."""
    print("Meta-Search Orchestration Demo")
    print("=" * 50)

    try:
        test_basic_orchestration()
        test_search_strategies()
        test_configuration_options()
        test_convenience_functions()
        test_performance_metrics()
        test_deduplication_ranking()

        print("\n" + "=" * 50)
        print("All meta-search orchestration tests completed successfully!")

    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

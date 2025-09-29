#!/usr/bin/env python3
"""
Demo script to test search adapters.

Tests DuckDuckGo, Lynx, and Curl adapters with real searches.
"""

import sys

sys.path.append("backend")

from apps.search.adapters import SearchAdapterFactory


def test_adapter(adapter_name, query="python programming"):
    """Test a specific search adapter."""
    print(f"\n=== Testing {adapter_name.upper()} Adapter ===")

    try:
        adapter = SearchAdapterFactory.get_adapter(adapter_name)
        print(f"Adapter: {adapter.get_name()}")

        results = adapter.search(query, limit=3)
        print(f"Found {len(results)} results for '{query}':")

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   Snippet: {result.snippet[:100]}...")
            print(f"   Source: {result.source}")

    except Exception as e:
        print(f"Error with {adapter_name}: {e}")


def main():
    """Test available search adapters."""
    print("Search Adapter Demo")
    print("==================")

    # Test adapters that should work without external dependencies
    adapters_to_test = ["duckduckgo"]

    # Test terminal-based adapters if available
    try:
        import shutil

        if shutil.which("curl"):
            adapters_to_test.append("curl")
            print(" curl is available")
        else:
            print(" curl not available")

        if shutil.which("lynx"):
            adapters_to_test.append("lynx")
            print(" lynx is available")
        else:
            print(" lynx not available")
    except:
        pass

    query = "OSINT tools"

    for adapter_name in adapters_to_test:
        test_adapter(adapter_name, query)

    print("\n=== Factory Methods Test ===")
    available = SearchAdapterFactory.get_available_adapters()
    print(f"Available adapters: {available}")

    all_adapters = SearchAdapterFactory.create_all_adapters()
    print(f"Created {len(all_adapters)} adapter instances")


if __name__ == "__main__":
    main()

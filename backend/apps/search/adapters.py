"""
Search Engine Adapters for OSINT AI Framework.

Provides unified interface for different search engines including Google, Bing,
and DuckDuckGo. Each adapter handles API-specific formatting and response parsing
while providing a consistent interface for the meta-search orchestration service.
"""

import re
import requests
import subprocess
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from .utils import canonicalize_url


@dataclass
class SearchResult:
    """Standardized search result representation."""

    title: str
    url: str
    snippet: str
    source: str

    def __post_init__(self):
        """Post-initialization processing."""
        # Canonicalize URL to ensure consistency
        self.url = canonicalize_url(self.url)

    def __repr__(self):
        return f"SearchResult(title='{self.title[:50]}...', url='{self.url}', source='{self.source}')"


class BaseSearchAdapter(ABC):
    """Abstract base class for search engine adapters."""

    def __init__(self):
        """Initialize base adapter."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Perform search and return standardized results.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this search adapter."""
        pass

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text.strip())

        # Remove HTML entities
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')

        return text


class GoogleSearchAdapter(BaseSearchAdapter):
    """Google Custom Search API adapter."""

    def __init__(
        self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None
    ):
        """Initialize Google search adapter."""
        super().__init__()
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"

    def get_name(self) -> str:
        """Return adapter name."""
        return "google"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search using Google Custom Search API.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        if not self.api_key or not self.search_engine_id:
            # Fallback to scraping if no API credentials
            return self._search_scraping(query, limit)

        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(limit, 10),  # Google API max is 10 per request
            }

            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get("items", []):
                result = SearchResult(
                    title=self._clean_text(item.get("title", "")),
                    url=item.get("link", ""),
                    snippet=self._clean_text(item.get("snippet", "")),
                    source=self.get_name(),
                )
                results.append(result)

            return results

        except Exception as e:
            print(f"Google search error: {e}")
            return []

    def _search_scraping(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Fallback scraping method for Google search."""
        try:
            params = {"q": query, "num": limit}

            url = f"https://www.google.com/search?{urlencode(params)}"
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # Parse Google search results
            for result_div in soup.find_all("div", class_="g")[:limit]:
                title_elem = result_div.find("h3")
                link_elem = result_div.find("a")
                snippet_elem = result_div.find("div", class_=["VwiC3b", "s3v9rd"])

                if title_elem and link_elem:
                    title = self._clean_text(title_elem.get_text())
                    url = link_elem.get("href", "")
                    snippet = self._clean_text(
                        snippet_elem.get_text() if snippet_elem else ""
                    )

                    if url.startswith("/url?q="):
                        # Extract actual URL from Google redirect
                        url = url.split("/url?q=")[1].split("&")[0]

                    if title and url:
                        result = SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source=self.get_name(),
                        )
                        results.append(result)

            return results

        except Exception as e:
            print(f"Google scraping error: {e}")
            return []


class BingSearchAdapter(BaseSearchAdapter):
    """Bing Search API adapter."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Bing search adapter."""
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.cognitive.microsoft.com/bing/v7.0/search"

    def get_name(self) -> str:
        """Return adapter name."""
        return "bing"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search using Bing Search API.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        if not self.api_key:
            # Fallback to scraping if no API key
            return self._search_scraping(query, limit)

        try:
            headers = {"Ocp-Apim-Subscription-Key": self.api_key}

            params = {
                "q": query,
                "count": min(limit, 50),  # Bing API max is 50
                "responseFilter": "Webpages",
            }

            response = self.session.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            web_pages = data.get("webPages", {})
            for item in web_pages.get("value", []):
                result = SearchResult(
                    title=self._clean_text(item.get("name", "")),
                    url=item.get("url", ""),
                    snippet=self._clean_text(item.get("snippet", "")),
                    source=self.get_name(),
                )
                results.append(result)

            return results

        except Exception as e:
            print(f"Bing search error: {e}")
            return []

    def _search_scraping(self, query: str, limit: int = 10) -> List[SearchResult]:
        """Fallback scraping method for Bing search."""
        try:
            params = {"q": query, "count": limit}

            url = f"https://www.bing.com/search?{urlencode(params)}"
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # Parse Bing search results
            for result_li in soup.find_all("li", class_="b_algo")[:limit]:
                title_elem = result_li.find("h2")
                link_elem = title_elem.find("a") if title_elem else None
                snippet_elem = result_li.find("p")

                if title_elem and link_elem:
                    title = self._clean_text(title_elem.get_text())
                    url = link_elem.get("href", "")
                    snippet = self._clean_text(
                        snippet_elem.get_text() if snippet_elem else ""
                    )

                    if title and url:
                        result = SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source=self.get_name(),
                        )
                        results.append(result)

            return results

        except Exception as e:
            print(f"Bing scraping error: {e}")
            return []


class DuckDuckGoSearchAdapter(BaseSearchAdapter):
    """DuckDuckGo search adapter (scraping-based)."""

    def get_name(self) -> str:
        """Return adapter name."""
        return "duckduckgo"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search using DuckDuckGo (scraping).

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        try:
            params = {
                "q": query,
                "s": "0",  # Start from first result
                "dc": str(limit),  # Number of results
            }

            url = f"https://html.duckduckgo.com/html/?{urlencode(params)}"
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # Parse DuckDuckGo search results
            for result_div in soup.find_all("div", class_="result")[:limit]:
                title_elem = result_div.find("a", class_="result__a")
                snippet_elem = result_div.find("a", class_="result__snippet")

                if title_elem:
                    title = self._clean_text(title_elem.get_text())
                    url = title_elem.get("href", "")
                    snippet = self._clean_text(
                        snippet_elem.get_text() if snippet_elem else ""
                    )

                    # DuckDuckGo uses redirect URLs, extract actual URL
                    if url.startswith("/l/?kh="):
                        # Extract actual URL from DuckDuckGo redirect
                        try:
                            import urllib.parse

                            parsed = urllib.parse.parse_qs(url.split("?")[1])
                            if "uddg" in parsed:
                                url = urllib.parse.unquote(parsed["uddg"][0])
                        except:
                            pass

                    if title and url:
                        result = SearchResult(
                            title=title,
                            url=url,
                            snippet=snippet,
                            source=self.get_name(),
                        )
                        results.append(result)

            return results

        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return []


class LynxSearchAdapter(BaseSearchAdapter):
    """Terminal-based search adapter using Lynx browser."""

    def __init__(self):
        """Initialize Lynx search adapter."""
        super().__init__()
        self.lynx_available = shutil.which("lynx") is not None

    def get_name(self) -> str:
        """Return adapter name."""
        return "lynx"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search using Lynx terminal browser for DuckDuckGo.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        if not self.lynx_available:
            print("Lynx not available, falling back to requests")
            return self._fallback_search(query, limit)

        try:
            # Use DuckDuckGo with Lynx (less likely to be blocked)
            search_url = f"https://html.duckduckgo.com/html/?q={query}&s=0&dc={limit}"

            # Use Lynx to get text output
            cmd = [
                "lynx",
                "-dump",
                "-nolist",
                "-width=200",
                "-user_agent=Lynx/2.8.9rel.1 libwww-FM/2.14 SSL-MM/1.4.1",
                search_url,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                print(f"Lynx command failed: {result.stderr}")
                return self._fallback_search(query, limit)

            return self._parse_lynx_output(result.stdout)

        except Exception as e:
            print(f"Lynx search error: {e}")
            return self._fallback_search(query, limit)

    def _parse_lynx_output(self, text: str) -> List[SearchResult]:
        """Parse Lynx text output for search results."""
        results = []
        lines = text.split("\n")

        i = 0
        while i < len(lines) and len(results) < 10:
            line = lines[i].strip()

            # Look for result titles (typically bold or numbered)
            if (
                line
                and not line.startswith("_")
                and not line.startswith("[")
                and len(line) > 10
                and not line.startswith("Search")
                and "DuckDuckGo" not in line
            ):
                # Try to find URL in following lines
                url = None
                snippet = ""

                # Look ahead for URL pattern
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line.startswith("http"):
                        url = next_line
                        break
                    elif len(next_line) > 20 and not next_line.startswith("http"):
                        snippet = next_line[:200]

                if url and "duckduckgo.com" not in url:
                    result = SearchResult(
                        title=self._clean_text(line),
                        url=url,
                        snippet=self._clean_text(snippet),
                        source=self.get_name(),
                    )
                    results.append(result)

            i += 1

        return results

    def _fallback_search(self, query: str, limit: int) -> List[SearchResult]:
        """Fallback to regular DuckDuckGo adapter if Lynx fails."""
        fallback = DuckDuckGoSearchAdapter()
        return fallback.search(query, limit)


class CurlSearchAdapter(BaseSearchAdapter):
    """Terminal-based search adapter using curl with custom headers."""

    def __init__(self):
        """Initialize curl search adapter."""
        super().__init__()
        self.curl_available = shutil.which("curl") is not None

    def get_name(self) -> str:
        """Return adapter name."""
        return "curl"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search using curl with rotating user agents.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of SearchResult objects
        """
        if not self.curl_available:
            return []

        try:
            # Use DuckDuckGo with curl and random user agent
            search_url = f"https://html.duckduckgo.com/html/?q={query}&s=0&dc={limit}"

            # Rotating user agents to avoid detection
            user_agents = [
                "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            ]

            import random

            user_agent = random.choice(user_agents)

            cmd = [
                "curl",
                "-s",
                "-L",
                "-H",
                f"User-Agent: {user_agent}",
                "-H",
                "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "-H",
                "Accept-Language: en-US,en;q=0.5",
                "-H",
                "Accept-Encoding: gzip, deflate",
                "-H",
                "Connection: keep-alive",
                search_url,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return []

            # Parse HTML using BeautifulSoup
            soup = BeautifulSoup(result.stdout, "html.parser")
            return self._parse_curl_results(soup)

        except Exception as e:
            print(f"Curl search error: {e}")
            return []

    def _parse_curl_results(self, soup: BeautifulSoup) -> List[SearchResult]:
        """Parse curl results from DuckDuckGo HTML."""
        results = []

        for result_div in soup.find_all("div", class_="result")[:10]:
            title_elem = result_div.find("a", class_="result__a")
            snippet_elem = result_div.find("a", class_="result__snippet")

            if title_elem:
                title = self._clean_text(title_elem.get_text())
                url = title_elem.get("href", "")
                snippet = self._clean_text(
                    snippet_elem.get_text() if snippet_elem else ""
                )

                if title and url:
                    result = SearchResult(
                        title=title, url=url, snippet=snippet, source=self.get_name()
                    )
                    results.append(result)

        return results


class SearchAdapterFactory:
    """Factory for creating search adapters."""

    _adapters = {
        "google": GoogleSearchAdapter,
        "bing": BingSearchAdapter,
        "duckduckgo": DuckDuckGoSearchAdapter,
        "lynx": LynxSearchAdapter,
        "curl": CurlSearchAdapter,
    }

    @classmethod
    def get_adapter(cls, adapter_name: str, **kwargs) -> BaseSearchAdapter:
        """
        Get a search adapter by name.

        Args:
            adapter_name: Name of the adapter ('google', 'bing', 'duckduckgo')
            **kwargs: Additional arguments to pass to adapter constructor

        Returns:
            Search adapter instance

        Raises:
            ValueError: If adapter name is not recognized
        """
        if adapter_name not in cls._adapters:
            available = ", ".join(cls._adapters.keys())
            raise ValueError(
                f"Unknown adapter '{adapter_name}'. Available: {available}"
            )

        adapter_class = cls._adapters[adapter_name]
        return adapter_class(**kwargs)

    @classmethod
    def get_available_adapters(cls) -> List[str]:
        """Get list of available adapter names."""
        return list(cls._adapters.keys())

    @classmethod
    def create_all_adapters(cls, **kwargs) -> List[BaseSearchAdapter]:
        """Create instances of all available adapters."""
        adapters = []
        for adapter_name in cls._adapters.keys():
            try:
                adapter = cls.get_adapter(adapter_name, **kwargs)
                adapters.append(adapter)
            except Exception as e:
                print(f"Failed to create adapter '{adapter_name}': {e}")

        return adapters

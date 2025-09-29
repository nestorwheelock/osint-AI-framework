"""
URL canonicalization utilities for OSINT AI Framework search functionality.

This module provides utilities for normalizing and canonicalizing URLs to ensure
consistent handling across different search engines and data sources.
"""

import re
import urllib.parse
from typing import Optional, Dict, List
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


class URLCanonicalizer:
    """URL canonicalization utilities for search functionality."""

    def __init__(self):
        """Initialize URL canonicalizer with default settings."""
        # Common URL parameters to remove during canonicalization
        self.tracking_params = {
            # Google Analytics and tracking
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "utm_id",
            "utm_source_platform",
            "utm_creative_format",
            "utm_marketing_tactic",
            # Facebook tracking
            "fbclid",
            "fb_action_ids",
            "fb_action_types",
            "fb_ref",
            "fb_source",
            # Twitter tracking
            "ref_src",
            "ref_url",
            "twclid",
            # Other common tracking parameters
            "gclid",
            "gclsrc",
            "dclid",
            "zanpid",
            "ranMID",
            "ranEAID",
            "ranSiteID",
            "spm",
            "_hsenc",
            "_hsmi",
            "hsctatracking",
            "mc_cid",
            "mc_eid",
            "pk_campaign",
            "pk_kwd",
            "pk_medium",
            "pk_source",
            # Session and reference tracking
            "ref",
            "referer",
            "referrer",
            "source",
            "campaign",
            "medium",
            # Time-based parameters
            "t",
            "timestamp",
            "_t",
            # Common noise parameters
            "v",
            "version",
            "ver",
            "cache",
            "random",
            "r",
            "_",
        }

        # Common www removal patterns
        self.www_patterns = [
            r"^www\d*\.",  # www, www2, www3, etc.
            r"^m\.",  # mobile versions
            r"^mobile\.",  # mobile versions
        ]

    def canonicalize_url(
        self,
        url: str,
        remove_fragment: bool = True,
        remove_tracking: bool = True,
        normalize_domain: bool = True,
        sort_query_params: bool = True,
    ) -> str:
        """
        Canonicalize a URL by applying various normalization rules.

        Args:
            url: The URL to canonicalize
            remove_fragment: Whether to remove URL fragments (#section)
            remove_tracking: Whether to remove tracking parameters
            normalize_domain: Whether to normalize domain (remove www, etc.)
            sort_query_params: Whether to sort query parameters alphabetically

        Returns:
            Canonicalized URL string
        """
        if not url or not isinstance(url, str):
            return ""

        url = url.strip()
        if not url:
            return ""

        try:
            # Parse the URL
            parsed = urlparse(url)

            # If no scheme and netloc, might be invalid URL
            if not parsed.scheme and not parsed.netloc:
                return url  # Return as-is for invalid URLs

            # Normalize scheme (always use lowercase, default to https if missing)
            scheme = parsed.scheme.lower() if parsed.scheme else "https"

            # Normalize domain
            netloc = parsed.netloc.lower() if parsed.netloc else ""
            if normalize_domain:
                netloc = self._normalize_domain(netloc)

            # Normalize path
            path = self._normalize_path(parsed.path)

            # Handle query parameters
            query = self._normalize_query(
                parsed.query,
                remove_tracking=remove_tracking,
                sort_params=sort_query_params,
            )

            # Handle fragment
            fragment = "" if remove_fragment else parsed.fragment

            # Reconstruct URL
            canonical_url = urlunparse(
                (scheme, netloc, path, parsed.params, query, fragment)
            )

            return canonical_url

        except Exception:
            # Return original URL if canonicalization fails
            return url

    def _normalize_domain(self, domain: str) -> str:
        """Normalize domain name by removing www and mobile prefixes."""
        if not domain:
            return domain

        # Remove www and mobile prefixes
        for pattern in self.www_patterns:
            domain = re.sub(pattern, "", domain, flags=re.IGNORECASE)

        return domain

    def _normalize_path(self, path: str) -> str:
        """Normalize URL path."""
        if not path:
            return "/"

        # Remove duplicate slashes
        path = re.sub(r"/+", "/", path)

        # Remove trailing slash for non-root paths
        if len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")

        # Ensure path starts with /
        if not path.startswith("/"):
            path = "/" + path

        return path

    def _normalize_query(
        self, query: str, remove_tracking: bool = True, sort_params: bool = True
    ) -> str:
        """Normalize query string parameters."""
        if not query:
            return ""

        try:
            # Parse query parameters
            params = parse_qs(query, keep_blank_values=False)

            # Remove tracking parameters if requested
            if remove_tracking:
                params = {
                    key: values
                    for key, values in params.items()
                    if key.lower() not in self.tracking_params
                    and not any(key.lower().startswith(prefix) for prefix in ["utm_"])
                }

            # Remove empty parameters
            params = {
                key: values
                for key, values in params.items()
                if values and any(v.strip() for v in values)
            }

            if not params:
                return ""

            # Sort parameters if requested
            if sort_params:
                sorted_params = []
                for key in sorted(params.keys()):
                    for value in sorted(params[key]):
                        sorted_params.append((key, value))
                return urlencode(sorted_params)
            else:
                # Maintain original order but clean up
                clean_params = []
                for key, values in params.items():
                    for value in values:
                        clean_params.append((key, value))
                return urlencode(clean_params)

        except Exception:
            # Return original query if parsing fails
            return query

    def extract_domain(self, url: str) -> str:
        """Extract and normalize the domain from a URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return self._normalize_domain(domain)
        except Exception:
            return ""

    def are_urls_equivalent(self, url1: str, url2: str) -> bool:
        """Check if two URLs are equivalent after canonicalization."""
        canonical1 = self.canonicalize_url(url1)
        canonical2 = self.canonicalize_url(url2)
        return canonical1 == canonical2

    def group_urls_by_canonical(self, urls: List[str]) -> Dict[str, List[str]]:
        """Group URLs by their canonical form."""
        groups = {}

        for url in urls:
            canonical = self.canonicalize_url(url)
            if canonical not in groups:
                groups[canonical] = []
            groups[canonical].append(url)

        return groups

    def deduplicate_urls(self, urls: List[str]) -> List[str]:
        """Remove duplicate URLs based on canonical form."""
        seen_canonical = set()
        deduplicated = []

        for url in urls:
            canonical = self.canonicalize_url(url)
            if canonical not in seen_canonical:
                seen_canonical.add(canonical)
                deduplicated.append(url)

        return deduplicated


def canonicalize_url(url: str, **kwargs) -> str:
    """Convenience function for URL canonicalization."""
    canonicalizer = URLCanonicalizer()
    return canonicalizer.canonicalize_url(url, **kwargs)


def extract_domain(url: str) -> str:
    """Convenience function for domain extraction."""
    canonicalizer = URLCanonicalizer()
    return canonicalizer.extract_domain(url)


def deduplicate_urls(urls: List[str]) -> List[str]:
    """Convenience function for URL deduplication."""
    canonicalizer = URLCanonicalizer()
    return canonicalizer.deduplicate_urls(urls)

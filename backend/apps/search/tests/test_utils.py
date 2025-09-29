"""Tests for search application utilities."""

from django.test import TestCase
from apps.search.utils import (
    URLCanonicalizer,
    canonicalize_url,
    extract_domain,
    deduplicate_urls,
)


class URLCanonicalizerTest(TestCase):
    """Test cases for URLCanonicalizer class."""

    def setUp(self):
        """Set up test environment."""
        self.canonicalizer = URLCanonicalizer()

    def test_basic_url_canonicalization(self):
        """Test basic URL canonicalization."""
        url = "https://example.com/path?param=value"
        canonical = self.canonicalizer.canonicalize_url(url)
        self.assertEqual(canonical, "https://example.com/path?param=value")

    def test_www_removal(self):
        """Test removal of www from domains."""
        test_cases = [
            ("https://www.example.com/path", "https://example.com/path"),
            ("https://www2.example.com/path", "https://example.com/path"),
            ("https://www123.example.com/path", "https://example.com/path"),
            ("http://www.example.com", "http://example.com/"),
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                canonical = self.canonicalizer.canonicalize_url(original)
                self.assertEqual(canonical, expected)

    def test_mobile_prefix_removal(self):
        """Test removal of mobile prefixes from domains."""
        test_cases = [
            ("https://m.example.com/path", "https://example.com/path"),
            ("https://mobile.example.com/path", "https://example.com/path"),
            ("http://m.twitter.com", "http://twitter.com/"),
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                canonical = self.canonicalizer.canonicalize_url(original)
                self.assertEqual(canonical, expected)

    def test_tracking_parameter_removal(self):
        """Test removal of tracking parameters."""
        test_cases = [
            (
                "https://example.com/path?utm_source=google&utm_medium=cpc&param=value",
                "https://example.com/path?param=value",
            ),
            (
                "https://example.com/article?fbclid=ABC123&content=important",
                "https://example.com/article?content=important",
            ),
            (
                "https://example.com/page?gclid=xyz&twclid=abc&useful=data",
                "https://example.com/page?useful=data",
            ),
            (
                "https://example.com/test?utm_campaign=test&utm_source=email",
                "https://example.com/test",
            ),
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                canonical = self.canonicalizer.canonicalize_url(original)
                self.assertEqual(canonical, expected)

    def test_query_parameter_sorting(self):
        """Test sorting of query parameters."""
        url = "https://example.com/path?c=3&a=1&b=2"
        canonical = self.canonicalizer.canonicalize_url(url, sort_query_params=True)
        self.assertEqual(canonical, "https://example.com/path?a=1&b=2&c=3")

    def test_query_parameter_no_sorting(self):
        """Test preservation of query parameter order when sorting disabled."""
        url = "https://example.com/path?c=3&a=1&b=2"
        canonical = self.canonicalizer.canonicalize_url(url, sort_query_params=False)
        self.assertEqual(canonical, "https://example.com/path?c=3&a=1&b=2")

    def test_fragment_removal(self):
        """Test removal of URL fragments."""
        test_cases = [
            ("https://example.com/page#section1", "https://example.com/page"),
            (
                "https://example.com/article?param=value#conclusion",
                "https://example.com/article?param=value",
            ),
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                canonical = self.canonicalizer.canonicalize_url(
                    original, remove_fragment=True
                )
                self.assertEqual(canonical, expected)

    def test_fragment_preservation(self):
        """Test preservation of URL fragments when requested."""
        url = "https://example.com/page#section1"
        canonical = self.canonicalizer.canonicalize_url(url, remove_fragment=False)
        self.assertEqual(canonical, "https://example.com/page#section1")

    def test_path_normalization(self):
        """Test path normalization."""
        test_cases = [
            ("https://example.com//double//slash", "https://example.com/double/slash"),
            ("https://example.com/trailing/", "https://example.com/trailing"),
            ("https://example.com", "https://example.com/"),
            ("https://example.com/", "https://example.com/"),
            (
                "https://example.com/path//to//resource/",
                "https://example.com/path/to/resource",
            ),
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                canonical = self.canonicalizer.canonicalize_url(original)
                self.assertEqual(canonical, expected)

    def test_scheme_normalization(self):
        """Test scheme normalization to lowercase."""
        test_cases = [
            ("HTTP://example.com", "http://example.com/"),
            ("HTTPS://example.com", "https://example.com/"),
            ("FTP://example.com", "ftp://example.com/"),
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                canonical = self.canonicalizer.canonicalize_url(original)
                self.assertEqual(canonical, expected)

    def test_domain_case_normalization(self):
        """Test domain name case normalization."""
        test_cases = [
            ("https://EXAMPLE.COM/path", "https://example.com/path"),
            ("https://Example.Com/PATH", "https://example.com/PATH"),
            ("https://WWW.EXAMPLE.COM", "https://example.com/"),
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                canonical = self.canonicalizer.canonicalize_url(original)
                self.assertEqual(canonical, expected)

    def test_empty_and_invalid_urls(self):
        """Test handling of empty and invalid URLs."""
        test_cases = [
            ("", ""),
            (None, ""),
            ("   ", ""),
            ("not-a-url", "not-a-url"),
            ("http://", "http:///"),  # Preserves original scheme
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                canonical = self.canonicalizer.canonicalize_url(original)
                self.assertEqual(canonical, expected)

    def test_extract_domain(self):
        """Test domain extraction."""
        test_cases = [
            ("https://www.example.com/path", "example.com"),
            ("http://m.twitter.com/user", "twitter.com"),
            ("https://subdomain.example.com", "subdomain.example.com"),
            ("ftp://files.example.org", "files.example.org"),
            ("", ""),
            ("invalid-url", ""),
        ]

        for url, expected_domain in test_cases:
            with self.subTest(url=url):
                domain = self.canonicalizer.extract_domain(url)
                self.assertEqual(domain, expected_domain)

    def test_urls_equivalent(self):
        """Test URL equivalence checking."""
        equivalent_pairs = [
            (
                "https://www.example.com/path?utm_source=google",
                "https://example.com/path",
            ),
            (
                "https://example.com/path/?param=value",
                "https://example.com/path?param=value",
            ),
            (
                "HTTP://EXAMPLE.COM/PATH",
                "http://example.com/PATH",  # Preserves original scheme and case in path
            ),
        ]

        for url1, url2 in equivalent_pairs:
            with self.subTest(url1=url1, url2=url2):
                self.assertTrue(self.canonicalizer.are_urls_equivalent(url1, url2))

        non_equivalent_pairs = [
            ("https://example.com/path1", "https://example.com/path2"),
            ("https://example.com", "https://different.com"),
            ("https://example.com/path?param=1", "https://example.com/path?param=2"),
        ]

        for url1, url2 in non_equivalent_pairs:
            with self.subTest(url1=url1, url2=url2):
                self.assertFalse(self.canonicalizer.are_urls_equivalent(url1, url2))

    def test_group_urls_by_canonical(self):
        """Test grouping URLs by canonical form."""
        urls = [
            "https://www.example.com/page?utm_source=google",
            "https://example.com/page",
            "http://example.com/page/",
            "https://different.com/page",
            "https://www.example.com/page?fbclid=123",
        ]

        groups = self.canonicalizer.group_urls_by_canonical(urls)

        # Should have fewer groups than original URLs due to canonicalization
        # Some URLs will be grouped together as equivalent
        self.assertLessEqual(len(groups), len(urls))

        # Find the groups with example.com and different.com
        example_groups = []
        different_group = None
        for canonical, group_urls in groups.items():
            if "example.com" in canonical:
                example_groups.append(group_urls)
            elif "different.com" in canonical:
                different_group = group_urls

        self.assertGreater(len(example_groups), 0)
        self.assertIsNotNone(different_group)
        # Should have at least one group with 3 URLs (HTTPS example.com URLs)
        # The HTTP URL forms a separate group due to scheme difference
        largest_example_group = max(example_groups, key=len)
        self.assertGreaterEqual(len(largest_example_group), 3)
        self.assertEqual(len(different_group), 1)

    def test_deduplicate_urls(self):
        """Test URL deduplication."""
        urls = [
            "https://www.example.com/page?utm_source=google",
            "https://example.com/page",
            "https://example.com/page/",
            "https://different.com/page",
            "https://www.example.com/page?fbclid=123",
            "https://another.com/page",
        ]

        deduplicated = self.canonicalizer.deduplicate_urls(urls)

        # Should keep only unique canonical URLs
        self.assertEqual(len(deduplicated), 3)

        # Check that we kept one from each canonical group
        domains = [extract_domain(url) for url in deduplicated]
        self.assertIn("example.com", domains)
        self.assertIn("different.com", domains)
        self.assertIn("another.com", domains)

    def test_complex_real_world_urls(self):
        """Test canonicalization of complex real-world URLs."""
        test_cases = [
            (
                "https://www.google.com/search?q=test&utm_source=bookmark&utm_medium=organic&gclid=123",
                "https://google.com/search?q=test",
            ),
            (
                "https://m.facebook.com/profile?id=123&fbclid=abc&ref=bookmark",
                "https://facebook.com/profile?id=123",
            ),
            (
                "https://twitter.com/user/status/123?utm_campaign=share&s=20&t=abc",
                "https://twitter.com/user/status/123?s=20",
            ),
        ]

        for original, expected in test_cases:
            with self.subTest(original=original):
                canonical = self.canonicalizer.canonicalize_url(original)
                self.assertEqual(canonical, expected)


class UtilityFunctionTest(TestCase):
    """Test cases for utility convenience functions."""

    def test_canonicalize_url_function(self):
        """Test canonicalize_url convenience function."""
        url = "https://www.example.com/path?utm_source=test"
        canonical = canonicalize_url(url)
        self.assertEqual(canonical, "https://example.com/path")

    def test_extract_domain_function(self):
        """Test extract_domain convenience function."""
        url = "https://www.example.com/path"
        domain = extract_domain(url)
        self.assertEqual(domain, "example.com")

    def test_deduplicate_urls_function(self):
        """Test deduplicate_urls convenience function."""
        urls = [
            "https://www.example.com/page",
            "https://example.com/page?utm_source=test",
            "https://different.com/page",
        ]

        deduplicated = deduplicate_urls(urls)
        self.assertEqual(len(deduplicated), 2)

    def test_tracking_parameters_coverage(self):
        """Test comprehensive tracking parameter removal."""
        # Test all major tracking parameter categories
        url_with_all_tracking = (
            "https://example.com/page?"
            "utm_source=google&utm_medium=cpc&utm_campaign=test&"
            "fbclid=fb123&gclid=g123&twclid=tw123&"
            "ref=bookmark&source=newsletter&"
            "hsCtaTracking=hs123&mc_cid=mc123&"
            "t=123456&v=1.0&_=cache"
        )

        canonical = canonicalize_url(url_with_all_tracking)
        self.assertEqual(canonical, "https://example.com/page")

    def test_performance_with_long_urls(self):
        """Test performance with very long URLs."""
        # Create a URL with many parameters
        base_url = "https://example.com/path?"
        params = []
        for i in range(100):
            params.append(f"param{i}=value{i}")
            if i % 10 == 0:
                params.append(f"utm_param{i}=tracking{i}")

        long_url = base_url + "&".join(params)

        # Should complete without errors
        canonical = canonicalize_url(long_url)
        self.assertTrue(canonical.startswith("https://example.com/path"))
        # Should have removed utm parameters
        self.assertNotIn("utm_param", canonical)

#!/usr/bin/env python3
"""
Tests for emoji prevention and professional standards enforcement.
"""

import tempfile
import pytest
import sys
from pathlib import Path

# Add scripts directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import importlib.util


def load_module_from_file(module_name: str, file_path: Path):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load the emoji checker module
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
emoji_module = load_module_from_file(
    "check_no_emojis", scripts_dir / "check-no-emojis.py"
)


class TestEmojiDetection:
    """Test emoji detection functionality."""

    def test_detect_simple_emojis(self):
        """Test detection of common emojis."""
        text = "This has a check mark [SUCCESS] and warning [WARNING]"
        matches = emoji_module.detect_emojis(text)

        assert len(matches) == 2
        assert matches[0][2] == "[SUCCESS]"  # emoji content
        assert matches[1][2] == "[WARNING]"  # emoji content

    def test_detect_complex_emojis(self):
        """Test detection of complex unicode emojis."""
        text = "Rocket [DEPLOY] and robot [AI] and celebration [COMPLETE]"
        matches = emoji_module.detect_emojis(text)

        assert len(matches) == 3
        emoji_chars = [match[2] for match in matches]
        assert "[DEPLOY]" in emoji_chars
        assert "[AI]" in emoji_chars
        assert "[COMPLETE]" in emoji_chars

    def test_no_emojis_detected(self):
        """Test that text without emojis returns no matches."""
        text = "This is professional text with [SUCCESS] and [WARNING] markers"
        matches = emoji_module.detect_emojis(text)

        assert len(matches) == 0

    def test_mixed_content_detection(self):
        """Test detection in mixed content with code and markdown."""
        text = """
        # Title with check [SUCCESS]

        ```python
        # Code with success [TARGET]
        def function():
            return "professional"
        ```

        Normal text [SUCCESS] without emoji.
        """
        matches = emoji_module.detect_emojis(text)

        assert len(matches) == 2


class TestEmojiReplacement:
    """Test emoji replacement functionality."""

    def test_replace_common_emojis(self):
        """Test replacement of common emojis with professional text."""
        text = "Status: [SUCCESS] Success and [FAIL] Failure"
        result, _ = emoji_module.replace_emojis(text, fix_mode=True)

        assert "[SUCCESS]" not in result
        assert "[FAIL]" not in result
        assert "[SUCCESS]" in result
        assert "[FAIL]" in result

    def test_replace_all_known_emojis(self):
        """Test replacement of all known emoji mappings."""
        # Test a few key mappings
        test_cases = [
            ("Deploy [DEPLOY] now", "Deploy [DEPLOY] now"),
            ("Warning [WARNING] message", "Warning [WARNING] message"),
            ("Documentation [DOCS] update", "Documentation [DOCS] update"),
            ("Search [SEARCH] function", "Search [SEARCH] function"),
            ("Critical [CRITICAL] alert", "Critical [CRITICAL] alert"),
        ]

        for input_text, expected in test_cases:
            result, _ = emoji_module.replace_emojis(input_text, fix_mode=True)
            assert result == expected

    def test_remove_unknown_emojis(self):
        """Test that unknown emojis are removed."""
        # Use an emoji not in our replacement map
        text = "Unknown emoji  should be removed"
        result, _ = emoji_module.replace_emojis(text, fix_mode=True)

        assert "" not in result
        assert result == "Unknown emoji  should be removed"

    def test_preserve_professional_text(self):
        """Test that professional text alternatives are preserved."""
        text = "Status: [SUCCESS] and [FAIL] and [WARNING]"
        result, _ = emoji_module.replace_emojis(text, fix_mode=True)

        assert result == text  # Should be unchanged


class TestFileProcessing:
    """Test file processing functionality."""

    def test_check_file_with_emojis(self):
        """Test checking a file that contains emojis."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                "# Test Document\n\nStatus: [SUCCESS] Complete\nWarning: [WARNING] Issue"
            )
            temp_path = f.name

        try:
            # Check without fix - should return False (violations found)
            result = emoji_module.check_file(temp_path, fix_mode=False)
            assert result is False

            # Check with fix - should return False (file was modified)
            result = emoji_module.check_file(temp_path, fix_mode=True)
            assert result is False

            # Verify content was fixed
            with open(temp_path, "r") as f:
                content = f.read()
            assert "[SUCCESS]" not in content
            assert "[WARNING]" not in content
            assert "[SUCCESS]" in content
            assert "[WARNING]" in content

        finally:
            Path(temp_path).unlink()

    def test_check_file_without_emojis(self):
        """Test checking a file that contains no emojis."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Professional Document\n\nStatus: [SUCCESS]\nNote: [INFO]")
            temp_path = f.name

        try:
            # Should return True (no violations)
            result = emoji_module.check_file(temp_path, fix_mode=False)
            assert result is True

            result = emoji_module.check_file(temp_path, fix_mode=True)
            assert result is True

        finally:
            Path(temp_path).unlink()

    def test_skip_binary_files(self):
        """Test that binary files are skipped gracefully."""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # PNG header
            temp_path = f.name

        try:
            # Should return True (skipped)
            result = emoji_module.check_file(temp_path, fix_mode=False)
            assert result is True

        finally:
            Path(temp_path).unlink()


class TestProfessionalStandards:
    """Test professional standards enforcement."""

    def test_markdown_document_cleanup(self):
        """Test cleaning up a typical markdown document."""
        markdown_content = """
        # Project Status Report [METRICS]

        ## Implementation Results [SUCCESS]

        - Database setup: [SUCCESS] Complete
        - API endpoints: [SUCCESS] Working
        - Tests: [WARNING] Needs review
        - Documentation: [DOCS] In progress

        ## Issues [CRITICAL]

        Critical bugs found! Need immediate attention [CONFIG]

        ## Next Steps [DEPLOY]

        Deploy to production [TARGET]
        """

        result, _ = emoji_module.replace_emojis(markdown_content, fix_mode=True)

        # Verify all emojis are replaced or removed
        for emoji in [
            "[METRICS]",
            "[SUCCESS]",
            "[WARNING]",
            "[DOCS]",
            "[CRITICAL]",
            "[CONFIG]",
            "[DEPLOY]",
            "[TARGET]",
        ]:
            assert emoji not in result

        # Verify professional replacements exist
        assert "[METRICS]" in result
        assert "[SUCCESS]" in result
        assert "[WARNING]" in result
        assert "[DOCS]" in result
        assert "[CRITICAL]" in result
        assert "[CONFIG]" in result
        assert "[DEPLOY]" in result
        assert "[TARGET]" in result

    def test_code_file_cleanup(self):
        """Test cleaning up code files with emoji comments."""
        code_content = '''
        # [SUCCESS] TODO: Implement this function
        def process_data():
            """
            Process the data [METRICS]
            Returns success [SUCCESS] or failure [FAIL]
            """
            try:
                # [DEPLOY] Fast processing here
                return True  # [SUCCESS] Success
            except Exception:
                return False  # [FAIL] Failure
        '''

        result, _ = emoji_module.replace_emojis(code_content, fix_mode=True)

        # Verify no emojis remain
        emoji_chars = ["[SUCCESS]", "[METRICS]", "[FAIL]", "[DEPLOY]"]
        for emoji in emoji_chars:
            assert emoji not in result

        # Verify professional alternatives
        assert "[SUCCESS]" in result
        assert "[FAIL]" in result
        assert "[METRICS]" in result
        assert "[DEPLOY]" in result


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_string(self):
        """Test handling of empty strings."""
        result, matches = emoji_module.replace_emojis("", fix_mode=True)
        assert result == ""
        assert len(matches) == 0

    def test_only_emojis(self):
        """Test string with only emojis."""
        text = "[SUCCESS][DEPLOY][TARGET]"
        result, _ = emoji_module.replace_emojis(text, fix_mode=True)
        assert result == "[SUCCESS][DEPLOY][TARGET]"

    def test_repeated_emojis(self):
        """Test handling of repeated emojis."""
        text = "Status: [SUCCESS][SUCCESS][SUCCESS] Triple success!"
        result, _ = emoji_module.replace_emojis(text, fix_mode=True)
        assert result == "Status: [SUCCESS][SUCCESS][SUCCESS] Triple success!"

    def test_unicode_normalization(self):
        """Test that different unicode representations are handled."""
        # Some emojis can have different unicode representations
        text = "Check [SUCCESS] and check "  # Different check marks
        result, _ = emoji_module.replace_emojis(text, fix_mode=True)
        # At least the emoji should be replaced
        assert "[SUCCESS]" not in result


def test_integration_with_precommit():
    """Test integration with pre-commit hooks."""
    # This tests the command-line interface
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("Test file with emoji [SUCCESS] content")
        temp_path = f.name

    try:
        # Test detection mode
        result = subprocess.run(
            ["python3", str(scripts_dir / "check-no-emojis.py"), temp_path],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1  # Should fail due to emojis
        assert "EMOJI VIOLATION" in result.stderr

        # Test fix mode
        result = subprocess.run(
            ["python3", str(scripts_dir / "check-no-emojis.py"), "--fix", temp_path],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1  # Returns 1 when files are modified
        assert "FIXED" in result.stderr

        # Verify fix worked
        with open(temp_path, "r") as f:
            content = f.read()
        assert "[SUCCESS]" not in content
        assert "[SUCCESS]" in content

    finally:
        Path(temp_path).unlink()


if __name__ == "__main__":
    # Run tests without pytest to avoid dependency issues
    import unittest

    # Convert to unittest format
    suite = unittest.TestSuite()

    # Add test classes
    for test_class in [
        TestEmojiDetection,
        TestEmojiReplacement,
        TestFileProcessing,
        TestProfessionalStandards,
        TestEdgeCases,
    ]:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)

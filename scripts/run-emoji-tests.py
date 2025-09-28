#!/usr/bin/env python3
"""
Simple test runner for emoji prevention functionality.
"""

import sys
import tempfile
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# Import using module loading approach
import importlib.util


def load_module_from_file(module_name: str, file_path: Path):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load the emoji checker module
emoji_module = load_module_from_file(
    "check_no_emojis", scripts_dir / "check-no-emojis.py"
)
detect_emojis = emoji_module.detect_emojis
replace_emojis = emoji_module.replace_emojis
check_file = emoji_module.check_file


def run_test(test_name, test_func):
    """Run a single test and report results."""
    try:
        test_func()
        print(f"[SUCCESS] {test_name}")
        return True
    except Exception as e:
        print(f"[FAIL] {test_name}: {e}")
        return False


def test_detect_simple_emojis():
    """Test detection of common emojis."""
    text = "This has a check mark [SUCCESS] and warning [WARNING]"
    matches = detect_emojis(text)

    assert len(matches) == 2
    assert matches[0][2] == "[SUCCESS]"
    assert matches[1][2] == "[WARNING]"


def test_detect_no_emojis():
    """Test that text without emojis returns no matches."""
    text = "This is professional text with [SUCCESS] and [WARNING] markers"
    matches = detect_emojis(text)

    assert len(matches) == 0


def test_replace_common_emojis():
    """Test replacement of common emojis with professional text."""
    text = "Status: [SUCCESS] Success and [FAIL] Failure"
    result, _ = replace_emojis(text, fix_mode=True)

    assert "[SUCCESS]" not in result
    assert "[FAIL]" not in result
    assert "[SUCCESS]" in result
    assert "[FAIL]" in result


def test_replace_all_known_emojis():
    """Test replacement of all known emoji mappings."""
    test_cases = [
        ("Deploy [DEPLOY] now", "Deploy [DEPLOY] now"),
        ("Warning [WARNING] message", "Warning [WARNING] message"),
        ("Documentation [DOCS] update", "Documentation [DOCS] update"),
        ("Critical [CRITICAL] alert", "Critical [CRITICAL] alert"),
    ]

    for input_text, expected in test_cases:
        result, _ = replace_emojis(input_text, fix_mode=True)
        assert result == expected, f"Expected '{expected}', got '{result}'"


def test_file_processing():
    """Test checking and fixing files."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            "# Test Document\n\nStatus: [SUCCESS] Complete\nWarning: [WARNING] Issue"
        )
        temp_path = f.name

    try:
        # Check without fix - should return False (violations found)
        result = check_file(temp_path, fix_mode=False)
        assert result is False

        # Check with fix - should return False (file was modified)
        result = check_file(temp_path, fix_mode=True)
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


def test_professional_cleanup():
    """Test comprehensive professional cleanup."""
    markdown_content = """
    # Project Status Report [METRICS]

    ## Implementation Results [SUCCESS]

    - Database setup: [SUCCESS] Complete
    - API endpoints: [SUCCESS] Working
    - Tests: [WARNING] Needs review
    - Documentation: [DOCS] In progress

    ## Issues [CRITICAL]

    Critical bugs found! Need immediate attention [CONFIG]
    """

    result, _ = replace_emojis(markdown_content, fix_mode=True)

    # Verify all emojis are replaced or removed
    for emoji in [
        "[METRICS]",
        "[SUCCESS]",
        "[WARNING]",
        "[DOCS]",
        "[CRITICAL]",
        "[CONFIG]",
    ]:
        assert emoji not in result, f"Emoji {emoji} still present"

    # Verify professional replacements exist
    assert "[METRICS]" in result
    assert "[SUCCESS]" in result
    assert "[WARNING]" in result
    assert "[DOCS]" in result
    assert "[CRITICAL]" in result
    assert "[CONFIG]" in result


def test_edge_cases():
    """Test edge cases."""
    # Empty string
    result, matches = replace_emojis("", fix_mode=True)
    assert result == ""
    assert len(matches) == 0

    # Only emojis
    text = "[SUCCESS][DEPLOY][TARGET]"
    result, _ = replace_emojis(text, fix_mode=True)
    assert result == "[SUCCESS][DEPLOY][TARGET]"

    # Repeated emojis
    text = "Status: [SUCCESS][SUCCESS][SUCCESS] Triple success!"
    result, _ = replace_emojis(text, fix_mode=True)
    assert result == "Status: [SUCCESS][SUCCESS][SUCCESS] Triple success!"


def main():
    """Run all tests."""
    print(" Running Emoji Prevention Tests")
    print("=" * 50)

    tests = [
        ("Detect Simple Emojis", test_detect_simple_emojis),
        ("Detect No Emojis", test_detect_no_emojis),
        ("Replace Common Emojis", test_replace_common_emojis),
        ("Replace All Known Emojis", test_replace_all_known_emojis),
        ("File Processing", test_file_processing),
        ("Professional Cleanup", test_professional_cleanup),
        ("Edge Cases", test_edge_cases),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        if run_test(test_name, test_func):
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("[SUCCESS] All emoji prevention tests passed!")
        return True
    else:
        print("[FAIL] Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

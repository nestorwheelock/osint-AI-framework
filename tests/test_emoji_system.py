#!/usr/bin/env python3
"""
Pytest-compatible tests for emoji prevention system.
"""

import tempfile
import sys
from pathlib import Path

# Add scripts directory to path
project_root = Path(__file__).parent.parent
scripts_dir = project_root / "scripts"
sys.path.insert(0, str(scripts_dir))

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


def test_detect_simple_emojis():
    """Test detection of common emojis."""
    text = "This has a check mark [SUCCESS] and warning [WARNING]"
    matches = emoji_module.detect_emojis(text)

    assert len(matches) == 2
    assert matches[0][2] == "[SUCCESS]"
    assert matches[1][2] == "[WARNING]"


def test_detect_no_emojis():
    """Test that text without emojis returns no matches."""
    text = "This is professional text with [SUCCESS] and [WARNING] markers"
    matches = emoji_module.detect_emojis(text)

    assert len(matches) == 0


def test_replace_common_emojis():
    """Test replacement of common emojis with professional text."""
    text = "Status: [SUCCESS] Success and [FAIL] Failure"
    result, _ = emoji_module.replace_emojis(text, fix_mode=True)

    assert "[SUCCESS]" not in result
    assert "[FAIL]" not in result
    assert "[SUCCESS]" in result
    assert "[FAIL]" in result


def test_replace_emoji_mappings():
    """Test specific emoji to text mappings."""
    test_cases = [
        ("Deploy [DEPLOY] now", "Deploy [DEPLOY] now"),
        ("Warning [WARNING] message", "Warning [WARNING] message"),
        ("Documentation [DOCS] update", "Documentation [DOCS] update"),
        ("Critical [CRITICAL] alert", "Critical [CRITICAL] alert"),
    ]

    for input_text, expected in test_cases:
        result, _ = emoji_module.replace_emojis(input_text, fix_mode=True)
        assert result == expected


def test_file_processing():
    """Test checking and fixing files."""
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


def test_professional_markdown_cleanup():
    """Test cleaning up a professional markdown document."""
    markdown_content = """
    # Project Status Report [METRICS]

    ## Results [SUCCESS]

    - Database: [SUCCESS] Complete
    - API: [SUCCESS] Working
    - Tests: [WARNING] Review needed
    - Docs: [DOCS] In progress

    ## Critical Issues [CRITICAL]

    Need immediate attention [CONFIG]
    """

    result, _ = emoji_module.replace_emojis(markdown_content, fix_mode=True)

    # Verify all emojis are replaced or removed
    emoji_chars = [
        "[METRICS]",
        "[SUCCESS]",
        "[WARNING]",
        "[DOCS]",
        "[CRITICAL]",
        "[CONFIG]",
    ]
    for emoji in emoji_chars:
        assert emoji not in result

    # Verify professional replacements exist
    expected_replacements = [
        "[METRICS]",
        "[SUCCESS]",
        "[WARNING]",
        "[DOCS]",
        "[CRITICAL]",
        "[CONFIG]",
    ]
    for replacement in expected_replacements:
        assert replacement in result


def test_edge_cases():
    """Test edge cases."""
    # Empty string
    result, matches = emoji_module.replace_emojis("", fix_mode=True)
    assert result == ""
    assert len(matches) == 0

    # Only emojis
    text = "[SUCCESS][DEPLOY][TARGET]"
    result, _ = emoji_module.replace_emojis(text, fix_mode=True)
    assert result == "[SUCCESS][DEPLOY][TARGET]"

    # Repeated emojis
    text = "Status: [SUCCESS][SUCCESS][SUCCESS] Triple success!"
    result, _ = emoji_module.replace_emojis(text, fix_mode=True)
    assert result == "Status: [SUCCESS][SUCCESS][SUCCESS] Triple success!"


def test_constraint_system_integration():
    """Test integration with constraint system."""
    # Load constraint parser
    constraint_module = load_module_from_file(
        "ai_constraint_parser", scripts_dir / "ai-constraint-parser.py"
    )

    # Create professional constraints
    constraints = constraint_module.AIConstraints(
        task_id="T-TEST",
        title="Professional Task",
        role="Senior Developer",
        objective="Build professional feature",
        allowed_paths=["src/test.py"],
        security_requirements=[
            "[CRITICAL] NEVER include any AI attribution",
            "[CRITICAL] This is a SECURITY REQUIREMENT",
        ],
    )

    # Verify no emojis in constraint fields
    for field in [constraints.role, constraints.objective, constraints.title]:
        if field:
            common_emojis = [
                "[SUCCESS]",
                "[FAIL]",
                "[DEPLOY]",
                "[DOCS]",
                "[CRITICAL]",
                "[WARNING]",
            ]
            for emoji in common_emojis:
                assert emoji not in field


if __name__ == "__main__":
    # Run with pytest
    import pytest

    pytest.main([__file__, "-v"])

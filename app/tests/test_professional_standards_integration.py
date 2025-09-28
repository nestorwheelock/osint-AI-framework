#!/usr/bin/env python3
"""
Tests for professional standards integration with AI constraint system.
"""

import tempfile
import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import importlib.util


def load_module_from_file(module_name: str, file_path: Path):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load modules
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
constraint_module = load_module_from_file(
    "ai_constraint_parser", scripts_dir / "ai-constraint-parser.py"
)
prompt_module = load_module_from_file(
    "generate_ai_prompt", scripts_dir / "generate-ai-prompt.py"
)


class TestProfessionalStandardsConstraints:
    """Test professional standards in AI constraints."""

    def test_constraint_parsing_with_professional_standards(self):
        """Test that professional standards are parsed correctly."""
        # Create temporary project structure
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            stories_dir = project_root / "planning" / "stories"
            tasks_dir = project_root / "planning" / "tasks"

            stories_dir.mkdir(parents=True)
            tasks_dir.mkdir(parents=True)

            # Create story with professional standards
            story_content = """# S-001 — Test Story

## AI Coding Brief
```yaml
role: "Senior Developer"
objective: "Build professional feature"
constraints:
  allowed_paths:
    - backend/app/test.py
  security:
    - "[CRITICAL] NEVER include any AI attribution"
    - "[CRITICAL] This is a SECURITY REQUIREMENT"
  professional_standards:
    - "[REQUIRED] NO EMOJIS in any code, documentation, comments, or deliverables"
    - "[REQUIRED] Use text alternatives: [SUCCESS], [FAIL], [WARNING], [INFO]"
    - "[REQUIRED] Professional formatting only: **bold**, *italic*, `code`"
    - "[REQUIRED] All deliverables must be enterprise-appropriate"
```
"""

            story_file = stories_dir / "S-001-test-story.md"
            story_file.write_text(story_content)

            # Create task file
            task_content = """# T-001 — Test Task

Professional implementation task.
"""

            task_file = tasks_dir / "T-001-test-task.md"
            task_file.write_text(task_content)

            # Test parsing
            parser = constraint_module.AIConstraintParser(project_root)
            constraints = parser.parse_task_constraints("T-001")

            assert constraints is not None
            assert constraints.task_id == "T-001"
            assert constraints.role == "Senior Developer"
            assert constraints.objective == "Build professional feature"

            # Verify security constraints don't have emojis
            security_reqs = constraints.security_requirements
            assert len(security_reqs) == 2
            for req in security_reqs:
                assert "[CRITICAL]" not in req
                assert "[CRITICAL]" in req

    def test_prompt_generation_without_emojis(self):
        """Test that generated prompts contain no emojis."""
        # Create constraints object
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
            definition_of_done=[
                "[SUCCESS] All tests pass",
                "[SUCCESS] Code is production ready",
            ],
        )

        # Generate prompt
        generator = prompt_module.AIPromptGenerator()
        prompt = generator.generate_prompt(constraints, "claude-code")

        # Verify no emojis in prompt
        import re

        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002500-\U00002BEF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\U0001f926-\U0001f937"
            "\U00010000-\U0010ffff"
            "\u2640-\u2642"
            "\u2600-\u2B55"
            "\u200d"
            "\u23cf"
            "\u23e9"
            "\u231a"
            "\ufe0f"
            "\u3030"
            "]+",
            flags=re.UNICODE,
        )

        emoji_matches = emoji_pattern.findall(prompt)
        assert len(emoji_matches) == 0, f"Found emojis in prompt: {emoji_matches}"

        # Verify professional alternatives are present
        assert "[CRITICAL]" in prompt
        assert "[SUCCESS]" in prompt
        assert "Professional Task" in prompt

    def test_constraint_validation_with_professional_standards(self):
        """Test constraint validation includes professional standards."""
        # Create constraints with professional standards
        constraints = constraint_module.AIConstraints(
            task_id="T-TEST",
            title="Test Task",
            role="Developer",
            objective="Build feature",
            allowed_paths=["src/test.py"],
            security_requirements=[
                "[CRITICAL] No AI attribution",
                "[REQUIRED] No emojis allowed",
            ],
        )

        # Test validation
        parser = constraint_module.AIConstraintParser()
        issues = parser.validate_constraints(constraints)

        # Should have no validation issues
        assert len(issues) == 0

    def test_markdown_cleaning_preserves_constraints(self):
        """Test that markdown cleaning preserves constraint structure."""
        markdown_with_emojis = """
        ## AI Coding Brief
        ```yaml
        role: "Senior Developer"
        objective: "Build feature [SUCCESS]"
        constraints:
          security:
            - "[CRITICAL] CRITICAL: No attribution"
          professional_standards:
            - "[DOCS] Use professional formatting"
        ```
        """

        # Clean the markdown
        from scripts.clean_markdown_for_pdf import clean_markdown_for_latex

        # Import the cleaning function
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "clean_markdown", scripts_dir / "clean-markdown-for-pdf.py"
        )
        clean_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(clean_module)

        cleaned = clean_module.clean_markdown_for_latex(markdown_with_emojis)

        # Verify YAML structure is preserved
        assert "```yaml" in cleaned
        assert "role:" in cleaned
        assert "constraints:" in cleaned

        # Verify emojis are removed/replaced
        assert "[SUCCESS]" not in cleaned
        assert "[CRITICAL]" not in cleaned
        assert "[DOCS]" not in cleaned

    def test_pre_commit_integration(self):
        """Test that pre-commit hooks work together properly."""
        # Create a file with both emojis and potential AI attribution
        content_with_issues = '''
        # Test File [SUCCESS]

        def test_function():
            """
            Test function [DEPLOY]
            Generated with Claude AI assistance
            """
            return True  # [SUCCESS] Success
        '''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content_with_issues)
            temp_path = f.name

        try:
            # Test emoji removal
            emoji_module = load_module_from_file(
                "check_no_emojis", scripts_dir / "check-no-emojis.py"
            )
            emoji_module.check_file(temp_path, fix_mode=True)

            # Read result
            with open(temp_path, "r") as f:
                result = f.read()

            # Verify emojis are gone
            assert "[SUCCESS]" not in result
            assert "[DEPLOY]" not in result
            assert "[SUCCESS]" in result
            assert "[DEPLOY]" in result

            # Note: AI attribution removal would be handled by separate hook

        finally:
            Path(temp_path).unlink()


class TestWorkflowIntegration:
    """Test integration with the full workflow."""

    def test_end_to_end_professional_workflow(self):
        """Test complete workflow maintains professional standards."""
        # This simulates the full AI assignment workflow
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Set up project structure
            stories_dir = project_root / "planning" / "stories"
            tasks_dir = project_root / "planning" / "tasks"
            stories_dir.mkdir(parents=True)
            tasks_dir.mkdir(parents=True)

            # Create story with professional constraints
            story_content = """# S-001 — Professional Feature

## AI Coding Brief
```yaml
role: "Senior Python Developer"
objective: "Implement professional feature with strict standards"
constraints:
  allowed_paths:
    - backend/app/feature.py
    - backend/app/tests.py
  security:
    - "[CRITICAL] NEVER include any AI attribution"
    - "[CRITICAL] No AI references in code or comments"
  professional_standards:
    - "[REQUIRED] NO EMOJIS in any deliverables"
    - "[REQUIRED] Use professional text: [SUCCESS], [FAIL], [WARNING]"
    - "[REQUIRED] Enterprise-appropriate formatting only"
    - "[REQUIRED] LaTeX-compatible documentation"
  testing: "Write comprehensive tests first"
  database: "Use professional ORM patterns"
definition_of_done:
  - "[SUCCESS] All tests pass"
  - "[SUCCESS] Code follows professional standards"
  - "[SUCCESS] No emojis or AI attribution anywhere"
```
"""

            story_file = stories_dir / "S-001-professional-feature.md"
            story_file.write_text(story_content)

            task_content = """# T-001 — Professional Implementation

Implementation task following strict professional standards.
"""

            task_file = tasks_dir / "T-001-professional-implementation.md"
            task_file.write_text(task_content)

            # Test full workflow
            parser = constraint_module.AIConstraintParser(project_root)
            constraints = parser.parse_task_constraints("T-001")

            # Verify constraints are professional
            assert constraints is not None

            # Check that all text fields are emoji-free
            for field in [constraints.role, constraints.objective, constraints.title]:
                if field:
                    # Basic emoji check
                    assert "[SUCCESS]" not in field
                    assert "[DEPLOY]" not in field
                    assert "[FAIL]" not in field

            # Generate prompt
            generator = prompt_module.AIPromptGenerator()
            prompt = generator.generate_prompt(constraints, "claude-code")

            # Verify prompt is professional
            assert "[CRITICAL]" in prompt
            assert "[REQUIRED]" in prompt
            assert "[SUCCESS]" in prompt

            # Verify no common emojis
            emoji_chars = [
                "[SUCCESS]",
                "[FAIL]",
                "[DEPLOY]",
                "[DOCS]",
                "[CRITICAL]",
                "[WARNING]",
            ]
            for emoji in emoji_chars:
                assert emoji not in prompt, f"Found emoji {emoji} in generated prompt"

    def test_documentation_generation_professional(self):
        """Test that documentation generation maintains professional standards."""
        # Test that when we generate documentation, it's professional

        # Create professional constraints
        constraints = constraint_module.AIConstraints(
            task_id="T-DOC",
            title="Documentation Generation",
            role="Technical Writer",
            objective="Generate professional documentation",
            allowed_paths=["docs/"],
            definition_of_done=[
                "[SUCCESS] Documentation is complete",
                "[SUCCESS] All examples are professional",
                "[SUCCESS] No emojis used anywhere",
            ],
        )

        # Generate interactive prompt
        generator = prompt_module.AIPromptGenerator()
        interactive_prompt = generator.generate_interactive_prompt(constraints)

        # Verify professional standards
        assert "[SUCCESS]" in interactive_prompt
        assert "Documentation Generation" in interactive_prompt
        assert "Technical Writer" in interactive_prompt

        # Verify no emojis
        common_emojis = [
            "[SUCCESS]",
            "[FAIL]",
            "[DEPLOY]",
            "[DOCS]",
            "[TARGET]",
            "[IDEA]",
            "[SEARCH]",
        ]
        for emoji in common_emojis:
            assert emoji not in interactive_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

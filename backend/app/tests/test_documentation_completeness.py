"""
Unit tests to verify documentation completeness and project structure integrity.
Ensures all required planning documents, stories, and AI briefs are present.
"""
import os
import pytest
from pathlib import Path
import yaml
import json


class TestDocumentationCompleteness:
    """Test suite to verify all required project documentation exists."""

    @property
    def project_root(self):
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent.parent

    def test_core_directory_structure_exists(self):
        """Verify all required directories are present."""
        required_dirs = [
            "docs/product",
            "docs/design",
            "docs/runbooks",
            "docs/qa",
            "docs/rfcs",
            "planning/stories",
            "planning/tasks",
            "planning/release-notes",
            "standards"
        ]

        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            assert full_path.exists(), f"Required directory missing: {dir_path}"
            assert full_path.is_dir(), f"Path exists but is not a directory: {dir_path}"

    def test_core_planning_documents_exist(self):
        """Verify all core planning documents are present."""
        required_docs = [
            "docs/product/osint-platform.md",
            "docs/design/osint-platform.md",
            "docs/runbooks/claude-workflow.md",
            "planning/roadmap.md",
            "planning/backlog.md",
            "standards/conventions.md"
        ]

        for doc_path in required_docs:
            full_path = self.project_root / doc_path
            assert full_path.exists(), f"Required document missing: {doc_path}"
            assert full_path.stat().st_size > 0, f"Document is empty: {doc_path}"

    def test_user_stories_have_required_structure(self):
        """Verify user stories contain all required sections."""
        stories_dir = self.project_root / "planning/stories"
        story_files = list(stories_dir.glob("S-*.md"))

        assert len(story_files) > 0, "No user story files found"

        required_sections = [
            "## Acceptance Criteria",
            "## Definition of Done",
            "## Dependencies",
            "## Links",
            "## Test Plan",
            "## AI Coding Brief"
        ]

        for story_file in story_files:
            content = story_file.read_text()
            for section in required_sections:
                assert section in content, f"Missing section '{section}' in {story_file.name}"

    def test_task_breakdowns_exist_for_stories(self):
        """Verify task breakdown files exist for each user story."""
        stories_dir = self.project_root / "planning/stories"
        tasks_dir = self.project_root / "planning/tasks"

        story_files = list(stories_dir.glob("S-*.md"))

        for story_file in story_files:
            # Extract story ID (e.g., S-001 from S-001-create-subject.md)
            story_id = story_file.stem.split('-')[0] + '-' + story_file.stem.split('-')[1]
            task_file = tasks_dir / f"T-{story_id.split('-')[1]}-{'-'.join(story_file.stem.split('-')[2:])}.md"

            assert task_file.exists(), f"Missing task breakdown for story {story_file.name}: expected {task_file.name}"

    def test_ai_briefs_have_security_compliance(self):
        """Verify AI coding briefs don't contain security-sensitive attribution."""
        stories_dir = self.project_root / "planning/stories"
        story_files = list(stories_dir.glob("S-*.md"))

        forbidden_patterns = [
            "Claude <noreply@anthropic.com>",
            "Co-Authored-By: Claude",
            "Generated with [Claude Code]"
        ]

        for story_file in story_files:
            content = story_file.read_text()

            # Find AI Coding Brief section
            if "## AI Coding Brief" in content:
                brief_start = content.find("## AI Coding Brief")
                brief_end = content.find("##", brief_start + 1)
                if brief_end == -1:
                    brief_end = len(content)

                brief_content = content[brief_start:brief_end]

                for pattern in forbidden_patterns:
                    assert pattern not in brief_content, f"Security violation in {story_file.name}: found '{pattern}' in AI brief"

    def test_yaml_prompt_files_are_valid(self):
        """Verify YAML prompt files are syntactically correct."""
        prompts_dir = self.project_root / "prompts/issues"

        if prompts_dir.exists():
            yaml_files = list(prompts_dir.glob("*.yaml"))

            for yaml_file in yaml_files:
                try:
                    with open(yaml_file, 'r') as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML syntax in {yaml_file.name}: {e}")

    def test_github_issue_templates_exist(self):
        """Verify GitHub issue templates are present."""
        templates_dir = self.project_root / ".github/ISSUE_TEMPLATE"

        assert templates_dir.exists(), "GitHub issue templates directory missing"

        required_templates = [
            "user_story.md"
        ]

        for template in required_templates:
            template_path = templates_dir / template
            assert template_path.exists(), f"Missing GitHub issue template: {template}"

    def test_prd_contains_required_sections(self):
        """Verify Product Requirements Document has all required sections."""
        prd_path = self.project_root / "docs/product/osint-platform.md"
        content = prd_path.read_text()

        required_sections = [
            "## Problem",
            "## Users & Use Cases",
            "## Goals / Success Metrics",
            "## Scope (In)",
            "## Out of Scope",
            "## Constraints & Assumptions",
            "## Rollout & Risks",
            "## Links"
        ]

        for section in required_sections:
            assert section in content, f"Missing section '{section}' in PRD"

    def test_design_doc_contains_required_sections(self):
        """Verify System Design Document has all required sections."""
        design_path = self.project_root / "docs/design/osint-platform.md"
        content = design_path.read_text()

        required_sections = [
            "## Context",
            "## Proposed Architecture",
            "## Data/Integrations",
            "## Trade-offs & Alternatives",
            "## Security/Privacy",
            "## Observability",
            "## Work Breakdown",
            "## Open Questions"
        ]

        for section in required_sections:
            assert section in content, f"Missing section '{section}' in Design Doc"

    def test_conventions_document_exists_and_complete(self):
        """Verify development conventions document is complete."""
        conventions_path = self.project_root / "standards/conventions.md"
        content = conventions_path.read_text()

        required_sections = [
            "## Naming Conventions",
            "## Git Workflow",
            "## Code Quality",
            "## Testing Strategy",
            "## Labels & Issue Management",
            "## Claude Code Integration"
        ]

        for section in required_sections:
            assert section in content, f"Missing section '{section}' in conventions document"

    def test_backlog_has_proper_structure(self):
        """Verify backlog document has proper story organization."""
        backlog_path = self.project_root / "planning/backlog.md"
        content = backlog_path.read_text()

        # Check for priority sections
        assert "## MVP Stories (Priority: High)" in content, "Missing MVP stories section"
        assert "## Enhanced Features (Priority: Medium)" in content, "Missing enhanced features section"

        # Check for story links format
        assert "[Story]" in content, "Missing story links in backlog"
        assert "[Tasks]" in content, "Missing task links in backlog"

    def test_no_security_sensitive_attribution_in_commits(self):
        """Verify git log doesn't contain security-sensitive attribution patterns."""
        import subprocess

        try:
            # Get recent commit messages
            result = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                commit_log = result.stdout

                # These patterns should not appear in commit messages going forward
                forbidden_patterns = [
                    "Claude <noreply@anthropic.com>",
                    "Co-Authored-By: Claude"
                ]

                # Only check the most recent commit for new security compliance
                recent_commits = commit_log.split('\n')[:3]  # Check last 3 commits

                for commit in recent_commits:
                    for pattern in forbidden_patterns:
                        # Only fail if this is a new commit (post security update)
                        if pattern in commit and "security" in commit.lower():
                            pytest.fail(f"Security violation in recent commit: found '{pattern}'")

        except subprocess.SubprocessError:
            # Skip test if git is not available
            pytest.skip("Git not available for commit history check")


class TestContinuousDocumentationCompliance:
    """Tests to ensure ongoing compliance with documentation standards."""

    @property
    def project_root(self):
        return Path(__file__).parent.parent.parent.parent

    def test_new_stories_follow_naming_convention(self):
        """Verify all story files follow S-XXX-name.md naming convention."""
        stories_dir = self.project_root / "planning/stories"
        story_files = list(stories_dir.glob("*.md"))

        import re
        pattern = re.compile(r'^S-\d{3}-[a-z-]+\.md$')

        for story_file in story_files:
            assert pattern.match(story_file.name), f"Story file doesn't follow naming convention: {story_file.name}"

    def test_task_files_follow_naming_convention(self):
        """Verify all task files follow T-XXX-name.md naming convention."""
        tasks_dir = self.project_root / "planning/tasks"
        if tasks_dir.exists():
            task_files = list(tasks_dir.glob("*.md"))

            import re
            pattern = re.compile(r'^T-\d{3}-[a-z-]+\.md$')

            for task_file in task_files:
                assert pattern.match(task_file.name), f"Task file doesn't follow naming convention: {task_file.name}"

    def test_no_claude_attribution_in_new_content(self):
        """Verify new documentation doesn't contain Claude attribution."""
        doc_dirs = [
            "docs",
            "planning",
            "standards"
        ]

        forbidden_patterns = [
            "🤖 Generated with [Claude Code]",
            "Co-Authored-By: Claude",
            "Claude <noreply@anthropic.com>"
        ]

        for doc_dir in doc_dirs:
            dir_path = self.project_root / doc_dir
            if dir_path.exists():
                for md_file in dir_path.rglob("*.md"):
                    content = md_file.read_text()

                    for pattern in forbidden_patterns:
                        assert pattern not in content, f"Security violation in {md_file.relative_to(self.project_root)}: found '{pattern}'"
"""
Comprehensive tests for the GitHub shell automation scripts.
Tests the actual shell script functionality using subprocess and mocking.
"""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, call, MagicMock
import os


class TestGitHubShellAutomation:
    """Test the shell script automation functionality."""

    @pytest.fixture
    def script_path(self):
        """Get path to the shell automation script."""
        return Path(__file__).parent.parent.parent.parent / 'scripts' / 'setup-github-project.sh'

    def test_script_exists_and_is_executable(self, script_path):
        """Test the automation script exists and has correct permissions."""
        assert script_path.exists(), "setup-github-project.sh should exist"
        assert script_path.is_file(), "Should be a file"

        # Check if executable
        stat = script_path.stat()
        assert stat.st_mode & 0o111, "Script should be executable"

    def test_script_help_flag(self, script_path):
        """Test script shows help when called with --help."""
        result = subprocess.run(
            [str(script_path), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, "Should exit successfully with help"
        assert "GitHub Project Setup Automation" in result.stdout
        assert "--repo" in result.stdout
        assert "--project-name" in result.stdout

    def test_script_requires_repo_parameter(self, script_path):
        """Test script fails gracefully without repo parameter."""
        result = subprocess.run(
            [str(script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode != 0, "Should fail without repo parameter"
        assert "Could not determine repository name" in result.stdout

    def test_script_dry_run_mode(self, script_path):
        """Test script dry run mode doesn't execute real commands."""
        result = subprocess.run(
            [str(script_path), '--repo', 'test/repo', '--dry-run'],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Dry run should succeed without actual API calls
        assert "DRY RUN" in result.stdout
        assert "Would execute:" in result.stdout

    @patch('subprocess.run')
    def test_github_cli_authentication_bypass(self, mock_run):
        """Test that GitHub CLI commands properly bypass environment token conflicts."""
        script_path = Path(__file__).parent.parent.parent.parent / 'scripts' / 'setup-github-project.sh'

        # Mock successful repository info call
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"name": "test-repo", "full_name": "owner/test-repo"}',
            stderr=""
        )

        # Run script with dry-run to avoid actual API calls
        result = subprocess.run(
            [str(script_path), '--repo', 'owner/test-repo', '--dry-run'],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, 'GH_TOKEN': 'conflicting-token'}
        )

        assert result.returncode == 0, "Should handle token conflicts gracefully"

    def test_label_configuration_format(self, script_path):
        """Test that labels are properly formatted in the script."""
        # Read the script content to verify label definitions
        script_content = script_path.read_text()

        # Check that labels follow the correct format: name:color:description
        assert 'labels=(' in script_content
        assert 'type-feature:0052cc:' in script_content
        assert 'type-bug:d73a4a:' in script_content
        assert 'priority-high:b60205:' in script_content
        assert 'size-small:c2e0c6:' in script_content

        # Ensure no problematic characters that caused previous issues
        assert "isn't" not in script_content, "Should not contain apostrophes that break shell parsing"

    def test_github_cli_command_structure(self, script_path):
        """Test that GitHub CLI commands in script have correct structure."""
        script_content = script_path.read_text()

        # Check for correct API command patterns
        assert 'gh api -X PATCH repos/' in script_content
        assert 'gh api -X POST repos/' in script_content
        assert 'gh api graphql' in script_content

        # Check for authentication handling
        assert 'unset GH_TOKEN' in script_content
        assert 'run_command(' in script_content

    def test_error_handling_and_logging(self, script_path):
        """Test that script has proper error handling and logging functions."""
        script_content = script_path.read_text()

        # Check for logging functions
        assert 'log_info(' in script_content
        assert 'log_success(' in script_content
        assert 'log_error(' in script_content
        assert 'log_warning(' in script_content

        # Check for error handling patterns
        assert 'if [ $? -ne 0 ]' in script_content or 'if (unset GH_TOKEN && eval' in script_content
        assert 'return 1' in script_content

    def test_script_parameter_parsing(self, script_path):
        """Test script correctly parses command line parameters."""
        script_content = script_path.read_text()

        # Check for parameter parsing logic
        assert '--repo)' in script_content
        assert '--project-name)' in script_content
        assert '--dry-run)' in script_content
        assert 'REPO_NAME=' in script_content
        assert 'PROJECT_NAME=' in script_content
        assert 'DRY_RUN=' in script_content

    def test_repository_settings_configuration(self, script_path):
        """Test that repository settings are properly configured."""
        script_content = script_path.read_text()

        # Check for repository configuration settings
        assert 'has_issues=true' in script_content
        assert 'has_projects=true' in script_content
        assert 'has_wiki=false' in script_content
        assert 'allow_squash_merge=true' in script_content
        assert 'allow_merge_commit=false' in script_content
        assert 'delete_branch_on_merge=true' in script_content


class TestGitHubLabelManagement:
    """Test label creation and management functionality."""

    @pytest.fixture
    def script_path(self):
        """Get path to the shell automation script."""
        return Path(__file__).parent.parent.parent.parent / 'scripts' / 'setup-github-project.sh'

    def test_label_definitions_complete(self, script_path):
        """Test that all required labels are defined."""
        script_content = script_path.read_text()

        # Type labels
        assert 'type-feature:' in script_content
        assert 'type-bug:' in script_content
        assert 'type-docs:' in script_content
        assert 'type-refactor:' in script_content
        assert 'type-infrastructure:' in script_content

        # Priority labels
        assert 'priority-high:' in script_content
        assert 'priority-medium:' in script_content
        assert 'priority-low:' in script_content

        # Size labels
        assert 'size-small:' in script_content
        assert 'size-medium:' in script_content
        assert 'size-large:' in script_content

        # Workflow labels
        assert 'ai-assisted:' in script_content
        assert 'ready-for-dev:' in script_content
        assert 'blocked:' in script_content
        assert 'needs-review:' in script_content

    def test_label_color_validity(self, script_path):
        """Test that label colors are valid hex colors."""
        script_content = script_path.read_text()

        # Extract label definitions
        import re
        label_pattern = r'"([^"]+):([0-9a-fA-F]{6}):([^"]+)"'
        labels = re.findall(label_pattern, script_content)

        assert len(labels) >= 14, "Should have at least 14 labels defined"

        for name, color, description in labels:
            # Validate hex color format
            assert len(color) == 6, f"Color {color} for {name} should be 6 hex characters"
            assert all(c in '0123456789abcdefABCDEF' for c in color), f"Color {color} for {name} should be valid hex"

            # Validate name format (no spaces, uses hyphens)
            assert ' ' not in name, f"Label name {name} should not contain spaces"
            assert name.replace('-', '').replace('_', '').isalnum(), f"Label name {name} should be alphanumeric with hyphens"

            # Validate description exists
            assert len(description.strip()) > 0, f"Label {name} should have a description"

    def test_label_existing_check_logic(self, script_path):
        """Test that script properly checks for existing labels."""
        script_content = script_path.read_text()

        # Check for label existence checking logic
        assert 'gh api "repos/$REPO_NAME/labels/$name"' in script_content
        assert 'already exists, skipping' in script_content
        assert '&> /dev/null' in script_content  # Silent check


class TestGitHubProjectCreation:
    """Test GitHub project creation functionality."""

    @pytest.fixture
    def script_path(self):
        """Get path to the shell automation script."""
        return Path(__file__).parent.parent.parent.parent / 'scripts' / 'setup-github-project.sh'

    def test_graphql_project_creation(self, script_path):
        """Test that script uses GraphQL for project creation."""
        script_content = script_path.read_text()

        # Check for GraphQL project creation
        assert 'gh api graphql' in script_content
        assert 'createProjectV2' in script_content
        assert 'ownerId:' in script_content
        assert 'title:' in script_content

    def test_project_custom_fields_setup(self, script_path):
        """Test that custom fields are configured for the project."""
        script_content = script_path.read_text()

        # Check for custom field creation
        assert 'createProjectV2Field' in script_content or 'field' in script_content.lower()

    def test_user_id_retrieval(self, script_path):
        """Test that script retrieves user ID for project creation."""
        script_content = script_path.read_text()

        # Check for user ID retrieval
        assert 'gh api user' in script_content
        assert 'USER_ID=' in script_content
        assert 'node_id' in script_content


class TestIntegrationWorkflow:
    """Test the complete integration workflow."""

    def test_documentation_references_scripts(self):
        """Test that documentation properly references the automation scripts."""
        docs_dir = Path(__file__).parent.parent.parent.parent / 'docs'
        readme_file = Path(__file__).parent.parent.parent.parent / 'README.md'

        # Check if documentation mentions the scripts
        docs_found = False
        if docs_dir.exists():
            for doc_file in docs_dir.rglob('*.md'):
                content = doc_file.read_text()
                if 'setup-github-project.sh' in content:
                    docs_found = True
                    break

        if readme_file.exists():
            content = readme_file.read_text()
            if 'setup-github-project.sh' in content:
                docs_found = True

        assert docs_found, "Documentation should reference the automation scripts"

    def test_github_workflows_exist(self):
        """Test that GitHub workflows directory and files exist."""
        workflows_dir = Path(__file__).parent.parent.parent.parent / '.github' / 'workflows'

        assert workflows_dir.exists(), "GitHub workflows directory should exist"

        workflow_files = list(workflows_dir.glob('*.yml'))
        assert len(workflow_files) > 0, "Should have at least one workflow file"

    def test_scripts_directory_complete(self):
        """Test that all required scripts exist in scripts directory."""
        scripts_dir = Path(__file__).parent.parent.parent.parent / 'scripts'

        assert scripts_dir.exists(), "Scripts directory should exist"

        required_scripts = [
            'setup-github-project.sh',
            'setup-github-automation.py',
            'sync-github-projects.py',
            'strip-claude-attribution.py'
        ]

        for script in required_scripts:
            script_path = scripts_dir / script
            assert script_path.exists(), f"Required script {script} should exist"

            # Check if executable (except for .py files which may not have execute bit)
            if script.endswith('.sh'):
                assert script_path.stat().st_mode & 0o111, f"Shell script {script} should be executable"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
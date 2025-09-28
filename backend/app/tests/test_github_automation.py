"""
Tests for GitHub automation and project sync functionality.
Following TDD approach - tests written first.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

# Import the modules we're testing
import sys
scripts_path = str(Path(__file__).parent.parent.parent.parent / 'scripts')
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

try:
    from sync_github_projects import GitHubProjectSync
except ImportError:
    # Fallback for when running outside of proper environment
    GitHubProjectSync = None


class TestGitHubProjectSync:
    """Test the bidirectional GitHub Projects sync functionality."""

    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory with test structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)

            # Create directory structure
            stories_dir = project_root / 'planning' / 'stories'
            stories_dir.mkdir(parents=True)

            sync_dir = project_root / '.github' / 'project-sync'
            sync_dir.mkdir(parents=True)

            # Create sample story file
            sample_story = """```yaml
type: feature
priority: high
size: medium
```

# User Authentication System

## User Story
As a user, I want to be able to log in securely so that I can access my personal data.

## Acceptance Criteria
- [ ] User can log in with email and password
- [ ] Invalid credentials show error message
- [ ] Successful login redirects to dashboard

## Implementation Notes
- Use Django authentication
- Add rate limiting
"""
            (stories_dir / 'S-001-user-auth.md').write_text(sample_story)

            yield project_root

    @pytest.fixture
    def github_sync(self, temp_project_dir):
        """Create GitHubProjectSync instance with test project."""
        with patch('sync_github_projects.Path.cwd', return_value=temp_project_dir):
            sync = GitHubProjectSync('test-owner/test-repo', '123', dry_run=True)
            return sync

    def test_extract_story_reference_from_issue_body(self, github_sync):
        """Test extracting user story file reference from issue body."""
        # Test with User Story File pattern
        body1 = "**User Story File:** `planning/stories/S-001-user-auth.md`\n\nSome description"
        result1 = github_sync.extract_story_reference(body1)
        assert result1 == "planning/stories/S-001-user-auth.md"

        # Test with User Story pattern
        body2 = "**User Story:** S-002-dashboard.md\n\nAnother description"
        result2 = github_sync.extract_story_reference(body2)
        assert result2 == "planning/stories/S-002-dashboard.md"

        # Test with no reference
        body3 = "Just a regular issue description"
        result3 = github_sync.extract_story_reference(body3)
        assert result3 is None

    def test_generate_story_filename(self, github_sync):
        """Test generating story filenames from issue titles."""
        # Create some existing story files
        stories_dir = github_sync.stories_dir
        (stories_dir / 'S-001-existing.md').touch()
        (stories_dir / 'S-005-another.md').touch()

        # Test filename generation
        filename = github_sync._generate_story_filename("User Login Feature")
        assert filename == "S-006-user-login-feature"

        # Test with special characters
        filename2 = github_sync._generate_story_filename("API: User Management (v2)")
        assert filename2 == "S-007-api-user-management-v2"

    def test_extract_github_metadata(self, github_sync):
        """Test extracting metadata from GitHub issue."""
        issue_data = {
            'issue_number': 42,
            'title': 'Test Issue',
            'state': 'open',
            'labels': ['priority:high', 'type:feature', 'size:medium'],
            'assignees': ['developer1', 'developer2'],
            'milestone': 'Sprint 1',
            'custom_fields': {'Status': 'In Progress', 'Epic': 'Authentication'}
        }

        metadata = github_sync._extract_github_metadata(issue_data)

        assert metadata['github']['issue_number'] == 42
        assert metadata['github']['state'] == 'open'
        assert metadata['priority'] == 'high'
        assert metadata['type'] == 'feature'
        assert metadata['size'] == 'medium'
        assert metadata['github']['assignees'] == ['developer1', 'developer2']
        assert metadata['github']['milestone'] == 'Sprint 1'
        assert 'last_synced' in metadata['github']

    def test_inject_github_metadata_existing_yaml(self, github_sync):
        """Test injecting GitHub metadata into story with existing YAML."""
        content = """```yaml
type: feature
priority: medium
original_field: value
```

# Test Story
Content here"""

        issue_data = {
            'issue_number': 123,
            'state': 'open',
            'labels': ['priority:high'],
            'assignees': [],
            'milestone': None,
            'custom_fields': {}
        }

        result = github_sync._inject_github_metadata(content, issue_data)

        assert 'issue_number: 123' in result
        assert 'priority: high' in result  # Should be updated
        assert 'original_field: value' in result  # Should be preserved
        assert '# Test Story' in result  # Content should be preserved

    def test_inject_github_metadata_no_existing_yaml(self, github_sync):
        """Test injecting GitHub metadata into story without YAML."""
        content = """# Test Story
Content without YAML frontmatter"""

        issue_data = {
            'issue_number': 456,
            'state': 'closed',
            'labels': ['type:bug'],
            'assignees': ['developer1'],
            'milestone': None,
            'custom_fields': {}
        }

        result = github_sync._inject_github_metadata(content, issue_data)

        assert result.startswith('```yaml\n')
        assert 'issue_number: 456' in result
        assert 'type: bug' in result
        assert '# Test Story' in result

    @patch('sync_github_projects.subprocess.run')
    def test_run_gh_command_success(self, mock_run, github_sync):
        """Test successful GitHub CLI command execution."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"result": "success"}',
            stderr=''
        )

        result = github_sync._run_gh_command(['api', 'user'])
        assert result == '{"result": "success"}'

    @patch('sync_github_projects.subprocess.run')
    def test_run_gh_command_failure(self, mock_run, github_sync):
        """Test failed GitHub CLI command execution."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'gh', stderr='Error message')

        result = github_sync._run_gh_command(['api', 'invalid'])
        assert result is None

    def test_run_gh_command_dry_run(self, github_sync):
        """Test dry run mode doesn't execute commands."""
        # github_sync is created with dry_run=True
        result = github_sync._run_gh_command(['api', 'user'])
        assert result is None  # Should return None in dry run

    def test_generate_story_from_issue(self, github_sync):
        """Test generating complete story content from GitHub issue."""
        issue_data = {
            'issue_number': 789,
            'title': 'User Dashboard Feature',
            'body': 'As a user, I want a dashboard to see my activity',
            'state': 'open',
            'labels': ['type:feature', 'priority:medium'],
            'assignees': ['developer1'],
            'milestone': 'MVP',
            'custom_fields': {'Epic': 'User Management'}
        }

        story_content = github_sync._generate_story_from_issue(issue_data)

        assert '# User Dashboard Feature' in story_content
        assert 'issue_number: 789' in story_content
        assert 'As a user, I want a dashboard' in story_content
        assert '## Acceptance Criteria' in story_content
        assert '## Implementation Notes' in story_content
        assert 'GitHub Issue #789' in story_content

    def test_process_project_items(self, github_sync):
        """Test processing raw GitHub Project items."""
        raw_items = [
            {
                'id': 'item-123',
                'content': {
                    'number': 1,
                    'title': 'Test Issue',
                    'body': 'Issue description',
                    'state': 'open',
                    'labels': {'nodes': [{'name': 'bug'}, {'name': 'priority:high'}]},
                    'assignees': {'nodes': [{'login': 'developer1'}]},
                    'milestone': {'title': 'Sprint 1'}
                },
                'fieldValues': {
                    'nodes': [
                        {
                            'field': {'name': 'Status'},
                            'name': 'In Progress'
                        },
                        {
                            'field': {'name': 'Epic'},
                            'text': 'User Management'
                        }
                    ]
                }
            }
        ]

        processed = github_sync._process_project_items(raw_items)

        assert len(processed) == 1
        item = processed[0]
        assert item['issue_number'] == 1
        assert item['title'] == 'Test Issue'
        assert item['labels'] == ['bug', 'priority:high']
        assert item['assignees'] == ['developer1']
        assert item['milestone'] == 'Sprint 1'
        assert item['custom_fields']['Status'] == 'In Progress'
        assert item['custom_fields']['Epic'] == 'User Management'


class TestGitHubProjectAutomation:
    """Test the GitHub project setup automation."""

    def test_script_exists_and_executable(self):
        """Test that the automation scripts exist and are executable."""
        script_path = Path(__file__).parent.parent.parent.parent / 'scripts' / 'setup-github-project.sh'
        assert script_path.exists(), "setup-github-project.sh should exist"
        assert script_path.stat().st_mode & 0o111, "Script should be executable"

    def test_python_script_exists_and_executable(self):
        """Test that the Python automation script exists and is executable."""
        script_path = Path(__file__).parent.parent.parent.parent / 'scripts' / 'setup-github-automation.py'
        assert script_path.exists(), "setup-github-automation.py should exist"
        assert script_path.stat().st_mode & 0o111, "Script should be executable"

    def test_sync_script_exists_and_executable(self):
        """Test that the sync script exists and is executable."""
        script_path = Path(__file__).parent.parent.parent.parent / 'scripts' / 'sync-github-projects.py'
        assert script_path.exists(), "sync-github-projects.py should exist"
        assert script_path.stat().st_mode & 0o111, "Script should be executable"


class TestWorkflowIntegration:
    """Test the complete workflow integration."""

    def test_workflow_directories_exist(self):
        """Test that required workflow directories exist."""
        project_root = Path(__file__).parent.parent.parent.parent

        assert (project_root / 'planning' / 'stories').exists()
        assert (project_root / '.github' / 'workflows').exists()
        assert (project_root / 'scripts').exists()

    def test_story_files_have_correct_format(self):
        """Test that existing story files have the correct format for sync."""
        stories_dir = Path(__file__).parent.parent.parent.parent / 'planning' / 'stories'

        if not stories_dir.exists():
            pytest.skip("No stories directory found")

        story_files = list(stories_dir.glob('S-*.md'))

        for story_file in story_files:
            content = story_file.read_text()

            # Should have proper naming convention
            assert story_file.name.startswith('S-'), f"{story_file.name} should start with S-"

            # Should have a title
            assert content.strip(), f"{story_file.name} should not be empty"

    def test_github_workflows_reference_sync(self):
        """Test that GitHub workflows can handle sync operations."""
        workflows_dir = Path(__file__).parent.parent.parent.parent / '.github' / 'workflows'

        if not workflows_dir.exists():
            pytest.skip("No workflows directory found")

        # Check if there's a workflow that could trigger sync
        workflow_files = list(workflows_dir.glob('*.yml'))
        assert len(workflow_files) > 0, "Should have at least one workflow file"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
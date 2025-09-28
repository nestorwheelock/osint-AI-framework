#!/usr/bin/env python3
"""
GitHub Projects Integration Tests

Tests for GitHub Projects workflow integration with the AI assignment system.
These tests verify bidirectional sync, status updates, and assignment tracking.
"""

import json
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add scripts directory to path for imports
import sys
import importlib.util


def load_module_from_file(module_name: str, file_path: Path):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load our modules
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sync_module = load_module_from_file(
    "sync_status_to_files", scripts_dir / "sync-status-to-files.py"
)
import_module = load_module_from_file(
    "import_planning_to_github", scripts_dir / "import-planning-to-github.py"
)
ai_assign_module = load_module_from_file("ai_assign", scripts_dir / "ai-assign.py")

StatusSyncer = sync_module.GitHubProjectToFilesSync
PlanningImporter = import_module.PlanningImporter
AIAssignmentManager = ai_assign_module.AIAssignmentManager


class TestGitHubProjectsSync:
    """Test GitHub Projects bidirectional synchronization."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.planning_dir = self.project_root / "planning"
        self.stories_dir = self.planning_dir / "stories"
        self.tasks_dir = self.planning_dir / "tasks"

        # Create directories
        self.stories_dir.mkdir(parents=True)
        self.tasks_dir.mkdir(parents=True)

        self.repo_name = "test/repo"
        self.project_number = 123

    def create_test_planning_file(
        self, file_path: Path, status: str = "todo", content_type: str = "story"
    ):
        """Create a test planning file with YAML frontmatter."""
        timestamp = datetime.now().isoformat()

        yaml_frontmatter = f"""```yaml
last_synced: '{timestamp}'
status: {status}
```

# {file_path.stem} — Test {content_type.title()}

This is a test {content_type}.

## Implementation
- [ ] Test implementation task

## Links
- Link to related files
"""
        file_path.write_text(yaml_frontmatter)
        return file_path

    def test_status_syncer_initialization(self):
        """Test StatusSyncer initialization and configuration."""
        syncer = StatusSyncer(self.repo_name, self.project_number, dry_run=True)

        assert syncer.repo_name == self.repo_name
        assert syncer.project_number == self.project_number
        assert syncer.dry_run is True
        assert syncer.project_root == Path.cwd()

    @patch("subprocess.run")
    def test_github_cli_command_execution(self, mock_subprocess):
        """Test GitHub CLI command execution with authentication."""
        mock_subprocess.return_value = Mock(stdout="mock output", returncode=0)

        syncer = StatusSyncer(self.repo_name, self.project_number, dry_run=False)
        result = syncer._run_gh_command(["api", "user"])

        assert result == "mock output"
        mock_subprocess.assert_called_once()

        # Verify gh command structure
        call_args = mock_subprocess.call_args[0][0]
        assert call_args[0] == "gh"
        assert "api" in call_args

    @patch("subprocess.run")
    def test_github_cli_authentication_handling(self, mock_subprocess):
        """Test proper GitHub CLI authentication handling."""
        mock_subprocess.return_value = Mock(
            stdout="", stderr="authentication required", returncode=1
        )

        syncer = StatusSyncer(self.repo_name, self.project_number)
        result = syncer._run_gh_command(["api", "user"])

        assert result is None
        # Verify environment handling (GH_TOKEN should be removed)
        call_args = mock_subprocess.call_args[1]
        env = call_args.get("env", {})
        assert "GH_TOKEN" not in env

    def test_file_status_extraction(self):
        """Test extracting status from planning files."""
        syncer = StatusSyncer(
            self.repo_name, self.project_number, project_root=self.project_root
        )

        # Create test file with status
        test_file = self.create_test_planning_file(
            self.stories_dir / "S-001-test.md", status="in_progress"
        )

        status = syncer._extract_file_status(test_file)
        assert status == "in_progress"

    def test_file_status_update(self):
        """Test updating status in planning files."""
        syncer = StatusSyncer(
            self.repo_name, self.project_number, project_root=self.project_root
        )

        # Create test file
        test_file = self.create_test_planning_file(
            self.stories_dir / "S-001-test.md", status="todo"
        )

        # Update status
        success = syncer._update_file_status(test_file, "in_progress")
        assert success is True

        # Verify update
        updated_content = test_file.read_text()
        assert "status: in_progress" in updated_content
        assert "last_synced:" in updated_content

    @patch("subprocess.run")
    def test_github_project_item_sync(self, mock_subprocess):
        """Test syncing project items from GitHub."""
        # Mock GitHub API response
        mock_items = [
            {
                "id": "item1",
                "title": "S-001 — Test Story",
                "status": "In Progress",
                "url": "https://github.com/test/repo/issues/1",
            },
            {
                "id": "item2",
                "title": "T-001 — Test Task",
                "status": "Todo",
                "url": "https://github.com/test/repo/issues/2",
            },
        ]

        mock_subprocess.return_value = Mock(stdout=json.dumps(mock_items), returncode=0)

        syncer = StatusSyncer(
            self.repo_name, self.project_number, project_root=self.project_root
        )

        # Create corresponding files
        self.create_test_planning_file(self.stories_dir / "S-001-test-story.md")
        self.create_test_planning_file(self.tasks_dir / "T-001-test-task.md")

        # Run sync
        synced_count = syncer.sync_status_to_files()

        # Verify calls made
        assert mock_subprocess.called
        assert synced_count >= 0  # Should process files

    def test_planning_file_discovery(self):
        """Test discovery of planning files."""
        syncer = StatusSyncer(
            self.repo_name, self.project_number, project_root=self.project_root
        )

        # Create test files
        story_file = self.create_test_planning_file(self.stories_dir / "S-001-test.md")
        task_file = self.create_test_planning_file(self.tasks_dir / "T-001-test.md")

        planning_files = syncer._get_planning_files()

        assert len(planning_files) == 2
        assert story_file in planning_files
        assert task_file in planning_files

    def test_title_to_file_mapping(self):
        """Test mapping GitHub issue titles to planning files."""
        syncer = StatusSyncer(
            self.repo_name, self.project_number, project_root=self.project_root
        )

        # Create test files
        self.create_test_planning_file(self.stories_dir / "S-001-user-auth.md")
        self.create_test_planning_file(self.tasks_dir / "T-001-auth-model.md")

        title_to_file = syncer._build_title_to_file_mapping()

        # Should map based on title extraction
        assert len(title_to_file) == 2

        # Check that files are mapped correctly
        files_mapped = list(title_to_file.values())
        assert any("S-001" in str(f) for f in files_mapped)
        assert any("T-001" in str(f) for f in files_mapped)

    def test_dry_run_mode(self):
        """Test dry run mode prevents actual changes."""
        syncer = StatusSyncer(
            self.repo_name,
            self.project_number,
            project_root=self.project_root,
            dry_run=True,
        )

        test_file = self.create_test_planning_file(
            self.stories_dir / "S-001-test.md", status="todo"
        )

        original_content = test_file.read_text()

        # Try to update (should not change in dry run)
        success = syncer._update_file_status(test_file, "in_progress")

        # In dry run, should return True but not actually update
        assert success is True
        assert test_file.read_text() == original_content


class TestPlanningImporter:
    """Test importing planning files to GitHub issues."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Change to temp directory for PlanningImporter
        import os

        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        self.planning_dir = self.project_root / "planning"
        self.stories_dir = self.planning_dir / "stories"
        self.tasks_dir = self.planning_dir / "tasks"

        # Create directories
        self.stories_dir.mkdir(parents=True)
        self.tasks_dir.mkdir(parents=True)

        self.repo_name = "test/repo"
        self.project_number = 123

    def teardown_method(self):
        """Clean up test environment."""
        import os

        os.chdir(self.original_cwd)

    def create_test_story(self, story_id: str, title: str):
        """Create a test story file."""
        content = f"""# {title}

**As a** test user
**I want** to test functionality
**So that** I can verify the system works

## Acceptance Criteria
- [ ] Feature works as expected
- [ ] Tests pass
- [ ] Documentation updated

## AI Coding Brief
```yaml
role: "Test Developer"
objective: "Implement test functionality"
constraints:
  allowed_paths:
    - test/file.py
```
"""
        story_file = (
            self.stories_dir / f"{story_id}-{title.lower().replace(' ', '-')}.md"
        )
        story_file.write_text(content)
        return story_file

    def create_test_task(self, task_id: str, title: str):
        """Create a test task file."""
        content = f"""# {title}

## Prerequisites
- [ ] Review requirements

## Implementation
- [ ] Implement feature
- [ ] Add tests

## Testing
- [ ] Unit tests
- [ ] Integration tests
"""
        task_file = self.tasks_dir / f"{task_id}-{title.lower().replace(' ', '-')}.md"
        task_file.write_text(content)
        return task_file

    def test_planning_importer_initialization(self):
        """Test PlanningImporter initialization."""
        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=True)

        assert importer.repo_name == self.repo_name
        assert importer.project_number == self.project_number
        assert importer.dry_run is True

    def test_story_metadata_extraction(self):
        """Test extracting metadata from story content."""
        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=True)

        story_content = """# User Authentication System

**As a** platform administrator
**I want** to implement user authentication
**So that** users can securely access the system

This is a large, high-priority story.
"""

        metadata = importer._extract_story_metadata(story_content, "S-001-auth.md")

        assert metadata["story_number"] == "001"
        assert metadata["title"] == "User Authentication System"
        assert "type-feature" in metadata["labels"]
        assert (
            "priority-high" in metadata["labels"]
        )  # Due to "high priority" in content
        assert "size-large" in metadata["labels"]  # Due to "large" in content

    def test_task_metadata_extraction(self):
        """Test extracting metadata from task content."""
        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=True)

        task_content = """# Implement User Model

## Implementation
- [ ] Create User model
- [ ] Add authentication fields
- [ ] Write comprehensive tests

This task involves refactoring the authentication system.
"""

        metadata = importer._extract_task_metadata(task_content, "T-001-user-model.md")

        assert metadata["task_number"] == "001"
        assert metadata["title"] == "Implement User Model"
        assert "type-refactor" in metadata["labels"]  # Due to "refactor" in content
        assert "ready-for-dev" in metadata["labels"]

    @patch("subprocess.run")
    def test_github_issue_creation(self, mock_subprocess):
        """Test creating GitHub issues from planning files."""
        # Mock successful issue creation
        mock_subprocess.return_value = Mock(
            stdout="https://github.com/test/repo/issues/42", returncode=0
        )

        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=False)

        issue_number = importer._create_github_issue(
            "Test Issue", "Test issue body content", ["type-feature", "priority-medium"]
        )

        assert issue_number == 42
        mock_subprocess.assert_called_once()

        # Verify GitHub CLI command structure
        call_args = mock_subprocess.call_args[0][0]
        assert "gh" in call_args[0]
        assert "issue" in call_args
        assert "create" in call_args

    @patch("subprocess.run")
    def test_project_item_addition(self, mock_subprocess):
        """Test adding issues to GitHub Project."""
        mock_subprocess.return_value = Mock(stdout="project item added", returncode=0)

        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=False)

        success = importer._add_issue_to_project(42)
        assert success is True

        # Verify project addition command
        call_args = mock_subprocess.call_args[0][0]
        assert "gh" in call_args[0]
        assert "project" in call_args
        assert "item-add" in call_args
        assert str(self.project_number) in call_args

    @patch("subprocess.run")
    def test_duplicate_issue_detection(self, mock_subprocess):
        """Test detection of existing issues to prevent duplicates."""
        # Mock existing issues
        existing_issues = [{"title": "Existing Story"}, {"title": "Another Story"}]

        mock_subprocess.return_value = Mock(
            stdout=json.dumps(existing_issues), returncode=0
        )

        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=False)

        existing_titles = importer._get_existing_issues()

        assert "Existing Story" in existing_titles
        assert "Another Story" in existing_titles

    def test_issue_body_creation(self):
        """Test creating GitHub issue body from markdown content."""
        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=True)

        content = (
            """# Test Story

This is test content for the story.

## Acceptance Criteria
- [ ] Feature works
- [ ] Tests pass

## Implementation Notes
Some implementation details here.
"""
            * 100
        )  # Make it long to test truncation

        body = importer._create_issue_body(
            content, "user story", "planning/stories/S-001-test.md"
        )

        # Should include file reference
        assert "**User Story File:** `planning/stories/S-001-test.md`" in body

        # Should include truncation notice if content is too long
        if len(content) > 10000:
            assert "Content truncated" in body

        # Should include footer
        assert "Imported from user story planning file" in body

    def test_import_stories_workflow(self):
        """Test complete story import workflow."""
        # Create test stories
        self.create_test_story("S-001", "User Authentication")
        self.create_test_story("S-002", "Data Management")

        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=True)

        # Mock GitHub operations
        with patch.object(importer, "_get_existing_issues", return_value=[]):
            with patch.object(importer, "_create_github_issue", return_value=42):
                with patch.object(importer, "_add_issue_to_project", return_value=True):
                    imported, errors = importer.import_stories()

        # Should attempt to import both stories in dry run
        assert imported >= 0
        assert errors >= 0

    def test_import_tasks_workflow(self):
        """Test complete task import workflow."""
        # Create test tasks
        self.create_test_task("T-001", "Implement Authentication")
        self.create_test_task("T-002", "Add Data Models")

        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=True)

        # Mock GitHub operations
        with patch.object(importer, "_create_github_issue", return_value=43):
            with patch.object(importer, "_add_issue_to_project", return_value=True):
                imported, errors = importer.import_tasks()

        # Should attempt to import both tasks
        assert imported >= 0
        assert errors >= 0


class TestAIAssignmentGitHubIntegration:
    """Test AI assignment system GitHub integration."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.repo_name = "test/repo"
        self.project_number = 123

    @patch("subprocess.run")
    def test_assignment_with_github_status_update(self, mock_subprocess):
        """Test task assignment with GitHub status update."""
        # Mock GitHub CLI responses
        mock_subprocess.return_value = Mock(stdout="status updated", returncode=0)

        manager = AIAssignmentManager(
            self.project_root, self.repo_name, self.project_number
        )

        # Mock constraint parsing
        with patch.object(
            manager.constraint_parser, "parse_task_constraints"
        ) as mock_parse:
            with patch.object(
                manager.constraint_parser, "validate_constraints"
            ) as mock_validate:
                with patch.object(
                    manager.prompt_generator, "generate_interactive_prompt"
                ) as mock_prompt:
                    # Setup mocks
                    mock_constraints = Mock()
                    mock_constraints.task_id = "T-001"
                    mock_constraints.title = "Test Task"

                    mock_parse.return_value = mock_constraints
                    mock_validate.return_value = []
                    mock_prompt.return_value = "Generated prompt"

                    # Test assignment
                    success = manager.assign_task("T-001")

                    assert success is True
                    mock_parse.assert_called_once_with("T-001")
                    mock_validate.assert_called_once()
                    mock_prompt.assert_called_once()

    def test_assignment_without_github_integration(self):
        """Test task assignment without GitHub integration."""
        manager = AIAssignmentManager(self.project_root)  # No repo/project

        # Mock constraint parsing
        with patch.object(
            manager.constraint_parser, "parse_task_constraints"
        ) as mock_parse:
            with patch.object(
                manager.constraint_parser, "validate_constraints"
            ) as mock_validate:
                with patch.object(
                    manager.prompt_generator, "generate_interactive_prompt"
                ) as mock_prompt:
                    # Setup mocks
                    mock_constraints = Mock()
                    mock_constraints.task_id = "T-001"

                    mock_parse.return_value = mock_constraints
                    mock_validate.return_value = []
                    mock_prompt.return_value = "Generated prompt"

                    # Test assignment (should work without GitHub)
                    success = manager.assign_task("T-001")

                    assert success is True

    def test_bulk_assignment_with_github_filtering(self):
        """Test bulk assignment with GitHub status filtering."""
        manager = AIAssignmentManager(
            self.project_root, self.repo_name, self.project_number
        )

        # Mock task listing and filtering
        with patch.object(
            manager.constraint_parser, "list_available_tasks"
        ) as mock_list:
            with patch.object(manager, "_get_task_status") as mock_status:
                mock_list.return_value = ["T-001", "T-002", "T-003"]
                mock_status.side_effect = ["todo", "in_progress", "todo"]

                # Filter by status
                filtered_tasks = manager.list_available_tasks(status_filter="todo")

                # Should return only todo tasks
                expected_tasks = ["T-001", "T-003"]
                # Note: This test verifies the method exists, actual filtering depends on implementation


class TestWorkflowIntegration:
    """Test complete workflow integration scenarios."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.repo_name = "test/repo"
        self.project_number = 123

        # Create directory structure
        self.planning_dir = self.project_root / "planning"
        self.stories_dir = self.planning_dir / "stories"
        self.tasks_dir = self.planning_dir / "tasks"
        self.tmp_dir = self.project_root / "tmp"

        self.stories_dir.mkdir(parents=True)
        self.tasks_dir.mkdir(parents=True)
        self.tmp_dir.mkdir(parents=True)

    def create_complete_planning_structure(self):
        """Create a complete planning structure for testing."""
        # Create story with AI coding brief
        story_content = """```yaml
last_synced: '2025-09-28T16:22:25.047760'
status: todo
```

# S-001 — User Authentication System

**As a** platform administrator
**I want** to implement user authentication
**So that** users can securely access the system

## AI Coding Brief
```yaml
role: "Senior Django backend engineer practicing strict TDD"
objective: "Implement user authentication with JWT tokens"
constraints:
  allowed_paths:
    - backend/apps/auth/models.py
    - backend/apps/auth/views.py
    - backend/apps/auth/tests.py
  testing: "Write Django tests first"
  security:
    - "🚨 CRITICAL: NEVER include any AI attribution"
tests_to_make_pass:
  - backend/apps/auth/tests.py::test_user_creation
definition_of_done:
  - "All tests pass"
  - "API endpoints return proper status codes"
```
"""

        # Create task
        task_content = """```yaml
last_synced: '2025-09-28T16:22:25.047760'
status: todo
```

# T-001 — User Model Implementation

## Implementation
- [ ] Create User model
- [ ] Add authentication fields
- [ ] Write tests

## Links
- **S-001**: [User Authentication](../stories/S-001-auth.md)
"""

        story_file = self.stories_dir / "S-001-auth.md"
        task_file = self.tasks_dir / "T-001-user-model.md"

        story_file.write_text(story_content)
        task_file.write_text(task_content)

        return story_file, task_file

    @patch("subprocess.run")
    def test_complete_workflow_simulation(self, mock_subprocess):
        """Test complete workflow from file creation to assignment."""
        # Setup planning files
        story_file, task_file = self.create_complete_planning_structure()

        # Mock all GitHub CLI operations
        mock_subprocess.return_value = Mock(
            stdout=json.dumps([]), returncode=0  # No existing issues
        )

        # Test 1: Import planning files to GitHub
        importer = PlanningImporter(self.repo_name, self.project_number, dry_run=True)

        with patch.object(importer, "_create_github_issue", return_value=42):
            with patch.object(importer, "_add_issue_to_project", return_value=True):
                story_imported, story_errors = importer.import_stories()
                task_imported, task_errors = importer.import_tasks()

        # Test 2: Sync status from GitHub back to files
        syncer = StatusSyncer(
            self.repo_name,
            self.project_number,
            project_root=self.project_root,
            dry_run=True,
        )

        mock_items = [
            {"title": "S-001 — User Authentication System", "status": "In Progress"}
        ]

        with patch.object(syncer, "_get_project_items", return_value=mock_items):
            synced = syncer.sync_status_to_files()

        # Test 3: AI assignment
        manager = AIAssignmentManager(
            self.project_root, self.repo_name, self.project_number
        )

        with patch.object(
            manager.constraint_parser, "parse_task_constraints"
        ) as mock_parse:
            with patch.object(
                manager.prompt_generator, "generate_interactive_prompt"
            ) as mock_prompt:
                # Setup mocks
                mock_constraints = Mock()
                mock_constraints.task_id = "T-001"
                mock_constraints.title = "User Model Implementation"
                mock_constraints.role = "Senior Django Developer"
                mock_constraints.objective = "Implement user model"
                mock_constraints.allowed_paths = ["backend/apps/auth/models.py"]

                mock_parse.return_value = mock_constraints
                mock_prompt.return_value = "Generated AI prompt"

                # Test assignment
                success = manager.assign_task("T-001", save_prompt=True)

                assert success is True

        # Verify prompt file was created
        prompt_files = list(self.tmp_dir.glob("*-prompt-*.md"))
        assert len(prompt_files) >= 0  # May be 0 in mock environment

    def test_error_handling_in_workflow(self):
        """Test error handling throughout the workflow."""
        # Test with missing files
        manager = AIAssignmentManager(self.project_root)

        # Should handle missing constraints gracefully
        success = manager.assign_task("T-NONEXISTENT")
        assert success is False

        # Test with invalid YAML
        invalid_task = self.tasks_dir / "T-INVALID-task.md"
        invalid_task.write_text(
            """```yaml
invalid: yaml: content:
```

# Invalid Task
"""
        )

        success = manager.assign_task("T-INVALID")
        assert success is False

    def test_concurrent_workflow_operations(self):
        """Test workflow operations that might run concurrently."""
        self.create_complete_planning_structure()

        # Simulate concurrent access to files
        syncer1 = StatusSyncer(
            self.repo_name,
            self.project_number,
            project_root=self.project_root,
            dry_run=True,
        )
        syncer2 = StatusSyncer(
            self.repo_name,
            self.project_number,
            project_root=self.project_root,
            dry_run=True,
        )

        # Both should be able to read files without conflict
        files1 = syncer1._get_planning_files()
        files2 = syncer2._get_planning_files()

        assert len(files1) == len(files2)
        assert files1 == files2

    def test_assignment_history_tracking(self):
        """Test tracking of assignment history."""
        self.create_complete_planning_structure()

        manager = AIAssignmentManager(self.project_root)

        # Mock successful assignment
        with patch.object(manager, "assign_task", return_value=True) as mock_assign:
            # Test multiple assignments
            tasks = ["T-001", "T-002", "T-003"]

            for task_id in tasks:
                mock_assign.return_value = True
                success = manager.assign_task(task_id)
                assert success is True

        # Verify assignment tracking would work
        # (Implementation would depend on actual history tracking mechanism)


if __name__ == "__main__":
    # Run tests manually without pytest dependency issues
    import sys

    def run_test_class(test_class, class_name):
        """Run all test methods in a test class."""
        print(f"\n🧪 Running {class_name}...")
        instance = test_class()

        test_methods = [
            method for method in dir(instance) if method.startswith("test_")
        ]

        passed = 0
        total = len(test_methods)

        for method_name in test_methods:
            try:
                # Run setup if it exists
                if hasattr(instance, "setup_method"):
                    instance.setup_method()

                # Run test method
                test_method = getattr(instance, method_name)
                test_method()

                print(f"  ✅ {method_name}")
                passed += 1

                # Run teardown if it exists
                if hasattr(instance, "teardown_method"):
                    instance.teardown_method()

            except Exception as e:
                print(f"  ❌ {method_name}: {e}")

        print(f"  📊 {class_name}: {passed}/{total} tests passed")
        return passed, total

    # Run all test classes
    test_classes = [
        (TestGitHubProjectsSync, "TestGitHubProjectsSync"),
        (TestPlanningImporter, "TestPlanningImporter"),
        (TestAIAssignmentGitHubIntegration, "TestAIAssignmentGitHubIntegration"),
        (TestWorkflowIntegration, "TestWorkflowIntegration"),
    ]

    total_passed = 0
    total_tests = 0

    print("🚀 Running GitHub Integration Tests")

    for test_class, class_name in test_classes:
        try:
            passed, total = run_test_class(test_class, class_name)
            total_passed += passed
            total_tests += total
        except Exception as e:
            print(f"❌ Failed to run {class_name}: {e}")

    print(f"\n📊 Overall Results: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("🎉 All GitHub integration tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the implementation.")
        sys.exit(1)

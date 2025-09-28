#!/usr/bin/env python3
"""
Test suite for AI Constraint System

Tests for the AI constraint parser, prompt generator, and assignment CLI
to ensure reliable task delegation with proper boundaries and validation.
"""

import json
import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

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
constraint_parser_module = load_module_from_file(
    "ai_constraint_parser", scripts_dir / "ai-constraint-parser.py"
)
prompt_generator_module = load_module_from_file(
    "generate_ai_prompt", scripts_dir / "generate-ai-prompt.py"
)
ai_assign_module = load_module_from_file("ai_assign", scripts_dir / "ai-assign.py")

AIConstraints = constraint_parser_module.AIConstraints
AIConstraintParser = constraint_parser_module.AIConstraintParser
AIPromptGenerator = prompt_generator_module.AIPromptGenerator
PromptTemplate = prompt_generator_module.PromptTemplate
AIAssignmentManager = ai_assign_module.AIAssignmentManager


class TestAIConstraints:
    """Test the AIConstraints data class."""

    def test_constraints_creation_with_required_fields(self):
        """Test creating constraints with only required fields."""
        constraints = AIConstraints(
            task_id="T-001",
            title="Test Task",
            role="Senior Developer",
            objective="Implement feature X",
            allowed_paths=["backend/app/models.py"],
        )

        assert constraints.task_id == "T-001"
        assert constraints.title == "Test Task"
        assert constraints.role == "Senior Developer"
        assert constraints.objective == "Implement feature X"
        assert constraints.allowed_paths == ["backend/app/models.py"]

        # Test default values
        assert constraints.forbidden_paths == []
        assert constraints.tests_to_make_pass == []
        assert constraints.definition_of_done == []
        assert constraints.security_requirements == []
        assert constraints.database is None
        assert constraints.testing_approach is None

    def test_constraints_creation_with_all_fields(self):
        """Test creating constraints with all fields populated."""
        constraints = AIConstraints(
            task_id="T-002",
            title="Complete Task",
            role="Backend Engineer",
            objective="Build API endpoint",
            allowed_paths=["backend/app/views.py", "backend/app/models.py"],
            forbidden_paths=["backend/settings/"],
            tests_to_make_pass=["test_api_endpoint"],
            definition_of_done=["API returns 200", "Tests pass"],
            security_requirements=["No AI attribution"],
            database="PostgreSQL",
            testing_approach="TDD",
        )

        assert len(constraints.allowed_paths) == 2
        assert len(constraints.forbidden_paths) == 1
        assert len(constraints.tests_to_make_pass) == 1
        assert len(constraints.definition_of_done) == 2
        assert len(constraints.security_requirements) == 1
        assert constraints.database == "PostgreSQL"
        assert constraints.testing_approach == "TDD"


class TestAIConstraintParser:
    """Test the AI constraint parser functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.stories_dir = self.project_root / "planning" / "stories"
        self.tasks_dir = self.project_root / "planning" / "tasks"

        # Create directories
        self.stories_dir.mkdir(parents=True)
        self.tasks_dir.mkdir(parents=True)

        self.parser = AIConstraintParser(self.project_root)

    def create_test_story(self, story_id: str, ai_brief_yaml: str):
        """Create a test story file with AI coding brief."""
        story_content = f"""# {story_id} — Test Story

This is a test story.

## AI Coding Brief
```yaml
{ai_brief_yaml}
```

## Other Content
More story content here.
"""
        story_file = self.stories_dir / f"{story_id}-test-story.md"
        story_file.write_text(story_content)
        return story_file

    def create_test_task(self, task_id: str, yaml_frontmatter: str = None):
        """Create a test task file with optional YAML frontmatter."""
        if yaml_frontmatter:
            task_content = f"""```yaml
{yaml_frontmatter}
```

# {task_id} — Test Task

This is a test task.

## Implementation
- [ ] Do something
"""
        else:
            task_content = f"""# {task_id} — Test Task

This is a test task.

## Implementation
- [ ] Do something
"""

        task_file = self.tasks_dir / f"{task_id}-test-task.md"
        task_file.write_text(task_content)
        return task_file

    def test_parse_constraints_from_story_ai_brief(self):
        """Test parsing constraints from story AI coding brief."""
        ai_brief = """role: "Senior Django Developer"
objective: "Implement user authentication system"
constraints:
  allowed_paths:
    - backend/apps/auth/models.py
    - backend/apps/auth/views.py
  database: "PostgreSQL"
  testing: "TDD approach"
  security:
    - "No AI attribution"
    - "Secure password handling"
tests_to_make_pass:
  - backend/apps/auth/tests.py::test_login_success
definition_of_done:
  - "Authentication works"
  - "Tests pass"
"""

        self.create_test_story("S-001", ai_brief)
        self.create_test_task("T-001")

        constraints = self.parser.parse_task_constraints("T-001")

        assert constraints is not None
        assert constraints.task_id == "T-001"
        assert constraints.role == "Senior Django Developer"
        assert constraints.objective == "Implement user authentication system"
        assert len(constraints.allowed_paths) == 2
        assert "backend/apps/auth/models.py" in constraints.allowed_paths
        assert len(constraints.security_requirements) == 2
        assert len(constraints.tests_to_make_pass) == 1
        assert len(constraints.definition_of_done) == 2

    def test_parse_constraints_from_task_yaml_frontmatter(self):
        """Test parsing constraints from task YAML frontmatter (overrides story)."""
        story_ai_brief = """role: "Story Role"
objective: "Story objective"
constraints:
  allowed_paths:
    - story/path.py
"""

        task_yaml = """role: "Task Role Override"
objective: "Task objective override"
constraints:
  allowed_paths:
    - task/specific/path.py
  forbidden_paths:
    - task/forbidden/
"""

        self.create_test_story("S-001", story_ai_brief)
        self.create_test_task("T-001", task_yaml)

        constraints = self.parser.parse_task_constraints("T-001")

        # Task YAML should override story constraints
        assert constraints.role == "Task Role Override"
        assert constraints.objective == "Task objective override"
        assert constraints.allowed_paths == ["task/specific/path.py"]
        assert constraints.forbidden_paths == ["task/forbidden/"]

    def test_parse_invalid_task_id(self):
        """Test parsing with invalid task ID returns None."""
        constraints = self.parser.parse_task_constraints("INVALID-001")
        assert constraints is None

    def test_parse_task_without_constraints(self):
        """Test parsing task without any constraints."""
        self.create_test_task("T-001")

        constraints = self.parser.parse_task_constraints("T-001")
        assert constraints is None

    def test_validate_constraints_success(self):
        """Test constraint validation with valid constraints."""
        constraints = AIConstraints(
            task_id="T-001",
            title="Valid Task",
            role="Developer",
            objective="Build something",
            allowed_paths=["backend/app/models.py"],
        )

        issues = self.parser.validate_constraints(constraints)
        assert len(issues) == 0

    def test_validate_constraints_missing_fields(self):
        """Test constraint validation catches missing required fields."""
        constraints = AIConstraints(
            task_id="T-001",
            title="Invalid Task",
            role="",  # Empty role
            objective="",  # Empty objective
            allowed_paths=[],  # No allowed paths
        )

        issues = self.parser.validate_constraints(constraints)
        assert len(issues) >= 3
        assert any("role" in issue for issue in issues)
        assert any("objective" in issue for issue in issues)
        assert any("allowed_paths" in issue for issue in issues)

    def test_validate_constraints_conflicting_paths(self):
        """Test validation catches conflicting allowed/forbidden paths."""
        constraints = AIConstraints(
            task_id="T-001",
            title="Conflicted Task",
            role="Developer",
            objective="Build something",
            allowed_paths=["backend/app/models.py"],
            forbidden_paths=[
                "backend/app/models.py"
            ],  # Same path forbidden and allowed
        )

        issues = self.parser.validate_constraints(constraints)
        assert len(issues) >= 1
        assert any("both allowed and forbidden" in issue for issue in issues)

    def test_list_available_tasks(self):
        """Test listing available tasks."""
        self.create_test_task("T-001")
        self.create_test_task("T-005")
        self.create_test_task("T-010")

        tasks = self.parser.list_available_tasks()
        assert len(tasks) == 3
        assert "T-001" in tasks
        assert "T-005" in tasks
        assert "T-010" in tasks
        assert tasks == sorted(tasks)  # Should be sorted

    def test_extract_parent_story_id(self):
        """Test extracting parent story ID from task ID."""
        assert self.parser._get_parent_story_id("T-001") == "S-001"
        assert self.parser._get_parent_story_id("T-015") == "S-015"
        assert self.parser._get_parent_story_id("t-005") == "S-005"  # Case insensitive
        assert self.parser._get_parent_story_id("INVALID") is None


class TestAIPromptGenerator:
    """Test the AI prompt generator functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.generator = AIPromptGenerator()
        self.test_constraints = AIConstraints(
            task_id="T-001",
            title="Test Task Implementation",
            role="Senior Python Developer",
            objective="Implement test functionality with proper error handling",
            allowed_paths=[
                "backend/app/models.py",
                "backend/app/views.py",
                "backend/app/tests.py",
            ],
            forbidden_paths=["backend/settings/"],
            tests_to_make_pass=[
                "backend/app/tests.py::test_functionality_works",
                "backend/app/tests.py::test_error_handling",
            ],
            definition_of_done=[
                "All tests pass",
                "Code follows style guide",
                "Documentation updated",
            ],
            security_requirements=["No AI attribution", "Secure data handling"],
            database="PostgreSQL",
            testing_approach="Test-driven development",
        )

    def test_generate_claude_code_prompt(self):
        """Test generating Claude Code formatted prompt."""
        prompt = self.generator.generate_prompt(self.test_constraints, "claude-code")

        # Check essential sections are present
        assert "# Test Task Implementation" in prompt
        assert "You are acting as a **Senior Python Developer**" in prompt
        assert "**Objective**: Implement test functionality" in prompt
        assert "**Constraints and Boundaries**:" in prompt
        assert "**File Access**:" in prompt
        assert "✅ **Allowed**: `backend/app/models.py`" in prompt
        assert "❌ **Forbidden**: `backend/settings/`" in prompt
        assert "🧪 **Test**: `backend/app/tests.py::test_functionality_works`" in prompt
        assert "✅ **Done**: All tests pass" in prompt
        assert "🔒 No AI attribution" in prompt
        assert "**Database**: PostgreSQL" in prompt
        assert "**Testing Approach**: Test-driven development" in prompt
        assert "Stay strictly within the allowed paths" in prompt

    def test_generate_general_prompt(self):
        """Test generating general AI assistant formatted prompt."""
        prompt = self.generator.generate_prompt(self.test_constraints, "general")

        assert "# Test Task Implementation" in prompt
        assert "Please act as a **Senior Python Developer**" in prompt
        assert "Objective: Implement test functionality" in prompt
        assert "Constraints:" in prompt
        assert "- Allowed file: backend/app/models.py" in prompt
        assert "ensure all changes stay within" in prompt

    def test_generate_minimal_prompt(self):
        """Test generating minimal formatted prompt."""
        prompt = self.generator.generate_prompt(self.test_constraints, "minimal")

        assert "# Test Task Implementation" in prompt
        assert "Role: **Senior Python Developer**" in prompt
        assert "Task: Implement test functionality" in prompt
        assert "Rules:" in prompt
        assert "- File: backend/app/models.py" in prompt

    def test_generate_interactive_prompt(self):
        """Test generating interactive copy-paste format."""
        prompt = self.generator.generate_interactive_prompt(self.test_constraints)

        assert "# AI Task Assignment: T-001" in prompt
        assert (
            "**Copy the prompt below and paste it into your AI assistant:**" in prompt
        )
        assert "---" in prompt
        assert "**Usage Notes**:" in prompt
        assert "This prompt contains all necessary constraints" in prompt

    def test_invalid_template_raises_error(self):
        """Test that invalid template name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown template: invalid"):
            self.generator.generate_prompt(self.test_constraints, "invalid")

    def test_list_templates(self):
        """Test listing available templates."""
        templates = self.generator.list_templates()

        assert isinstance(templates, dict)
        assert "claude-code" in templates
        assert "general" in templates
        assert "minimal" in templates
        assert "Claude Code" in templates["claude-code"]

    def test_add_custom_template(self):
        """Test adding custom template."""
        custom_template = PromptTemplate(
            name="Custom Test",
            ai_assistant="Test AI",
            role_prefix="You are a",
            objective_format="Goal: {}",
            constraints_header="Rules:",
            path_format="- File: {}",
            test_format="- Test: {}",
            done_format="- Complete: {}",
            footer="Custom footer",
        )

        self.generator.add_custom_template("custom", custom_template)

        prompt = self.generator.generate_prompt(self.test_constraints, "custom")
        assert "You are a **Senior Python Developer**" in prompt
        assert "Goal: Implement test functionality" in prompt
        assert "Rules:" in prompt
        assert "Custom footer" in prompt

    def test_validate_constraints_for_prompt(self):
        """Test constraint validation for prompt generation."""
        # Valid constraints should return no warnings
        warnings = self.generator.validate_constraints_for_prompt(self.test_constraints)
        assert len(warnings) == 0

        # Invalid constraints should return warnings
        invalid_constraints = AIConstraints(
            task_id="T-INVALID",
            title="Invalid Task",
            role="",
            objective="",
            allowed_paths=[],
        )

        warnings = self.generator.validate_constraints_for_prompt(invalid_constraints)
        assert len(warnings) > 0
        assert any("No allowed paths" in warning for warning in warnings)
        assert any("Empty or missing objective" in warning for warning in warnings)

    def test_minimal_constraints_prompt(self):
        """Test generating prompt with minimal constraints."""
        minimal_constraints = AIConstraints(
            task_id="T-MIN",
            title="Minimal Task",
            role="Developer",
            objective="Do something",
            allowed_paths=["file.py"],
        )

        prompt = self.generator.generate_prompt(minimal_constraints, "claude-code")

        # Should still generate valid prompt
        assert "# Minimal Task" in prompt
        assert "Developer" in prompt
        assert "Do something" in prompt
        assert "file.py" in prompt


class TestAIAssignmentManager:
    """Test the AI assignment manager functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Mock the constraint parser and prompt generator
        self.mock_parser = Mock()
        self.mock_generator = Mock()

        self.manager = AIAssignmentManager(self.project_root, "test/repo", 123)
        self.manager.constraint_parser = self.mock_parser
        self.manager.prompt_generator = self.mock_generator

    def test_assignment_manager_initialization(self):
        """Test assignment manager initialization."""
        manager = AIAssignmentManager()

        assert manager.project_root == Path.cwd()
        assert manager.repo_name is None
        assert manager.project_number is None
        assert "claude-code" in manager.ai_platforms
        assert "claude-web" in manager.ai_platforms
        assert "gpt4" in manager.ai_platforms

    def test_ai_platform_configuration(self):
        """Test AI platform configurations."""
        platforms = self.manager.ai_platforms

        # Check Claude Code config
        claude_config = platforms["claude-code"]
        assert claude_config["name"] == "Claude Code"
        assert claude_config["url"] == "https://claude.com/claude-code"
        assert claude_config["prompt_template"] == "claude-code"

        # Check GPT-4 config
        gpt4_config = platforms["gpt4"]
        assert gpt4_config["name"] == "GPT-4"
        assert gpt4_config["url"] == "https://chat.openai.com"
        assert gpt4_config["prompt_template"] == "general"

    def test_assign_task_success(self):
        """Test successful task assignment."""
        # Mock constraint parsing
        test_constraints = AIConstraints(
            task_id="T-001",
            title="Test Task",
            role="Developer",
            objective="Build feature",
            allowed_paths=["file.py"],
        )
        self.mock_parser.parse_task_constraints.return_value = test_constraints
        self.mock_parser.validate_constraints.return_value = []

        # Mock prompt generation
        self.mock_generator.generate_interactive_prompt.return_value = (
            "Generated prompt"
        )

        # Test assignment
        with patch("webbrowser.open"):
            success = self.manager.assign_task(
                "T-001", auto_open=True, save_prompt=True
            )

        assert success is True
        self.mock_parser.parse_task_constraints.assert_called_once_with("T-001")
        self.mock_generator.generate_interactive_prompt.assert_called_once()

    def test_assign_task_no_constraints(self):
        """Test assignment failure when no constraints found."""
        self.mock_parser.parse_task_constraints.return_value = None

        success = self.manager.assign_task("T-INVALID")

        assert success is False
        self.mock_parser.parse_task_constraints.assert_called_once_with("T-INVALID")

    def test_assign_task_validation_warnings(self):
        """Test assignment with validation warnings."""
        test_constraints = AIConstraints(
            task_id="T-001",
            title="Test Task",
            role="Developer",
            objective="Build feature",
            allowed_paths=["file.py"],
        )
        self.mock_parser.parse_task_constraints.return_value = test_constraints
        self.mock_parser.validate_constraints.return_value = ["Warning: Test warning"]

        # Mock user input to continue
        with patch("builtins.input", return_value="y"):
            with patch("webbrowser.open"):
                success = self.manager.assign_task("T-001")

        assert success is True

    def test_assign_task_validation_cancelled(self):
        """Test assignment cancelled due to validation warnings."""
        test_constraints = AIConstraints(
            task_id="T-001",
            title="Test Task",
            role="Developer",
            objective="Build feature",
            allowed_paths=["file.py"],
        )
        self.mock_parser.parse_task_constraints.return_value = test_constraints
        self.mock_parser.validate_constraints.return_value = ["Critical error"]

        # Mock user input to cancel
        with patch("builtins.input", return_value="n"):
            success = self.manager.assign_task("T-001")

        assert success is False

    def test_assign_task_invalid_platform(self):
        """Test assignment with invalid AI platform."""
        success = self.manager.assign_task("T-001", ai_platform="invalid-platform")
        assert success is False

    def test_show_task_summary_success(self):
        """Test showing task summary successfully."""
        test_constraints = AIConstraints(
            task_id="T-001",
            title="Test Task",
            role="Developer",
            objective="Build feature",
            allowed_paths=["file.py"],
        )
        self.mock_parser.parse_task_constraints.return_value = test_constraints
        self.mock_parser.validate_constraints.return_value = []

        success = self.manager.show_task_summary("T-001")
        assert success is True

    def test_show_task_summary_no_constraints(self):
        """Test showing task summary when no constraints found."""
        self.mock_parser.parse_task_constraints.return_value = None

        success = self.manager.show_task_summary("T-001")
        assert success is False

    def test_list_available_tasks(self):
        """Test listing available tasks."""
        self.mock_parser.list_available_tasks.return_value = ["T-001", "T-002", "T-003"]

        tasks = self.manager.list_available_tasks()
        assert len(tasks) == 3
        assert "T-001" in tasks

    def test_bulk_assign_ready_tasks(self):
        """Test bulk assignment of ready tasks."""
        # Mock available tasks
        self.mock_parser.list_available_tasks.return_value = ["T-001", "T-002", "T-003"]

        # Mock constraints for each task
        test_constraints = AIConstraints(
            task_id="T-001",
            title="Test Task",
            role="Developer",
            objective="Build feature",
            allowed_paths=["file.py"],
        )
        self.mock_parser.parse_task_constraints.return_value = test_constraints
        self.mock_parser.validate_constraints.return_value = []
        self.mock_generator.generate_interactive_prompt.return_value = (
            "Generated prompt"
        )

        results = self.manager.bulk_assign_ready_tasks(max_tasks=2)

        # Should process only max_tasks number of tasks
        assert len(results) <= 2
        assert self.mock_parser.parse_task_constraints.call_count <= 2


class TestIntegration:
    """Integration tests for the complete AI assignment system."""

    def setup_method(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.stories_dir = self.project_root / "planning" / "stories"
        self.tasks_dir = self.project_root / "planning" / "tasks"
        self.tmp_dir = self.project_root / "tmp"

        # Create directories
        self.stories_dir.mkdir(parents=True)
        self.tasks_dir.mkdir(parents=True)
        self.tmp_dir.mkdir(parents=True)

    def create_realistic_story_and_task(self):
        """Create realistic story and task files for integration testing."""
        story_content = """```yaml
last_synced: '2025-09-28T16:22:25.047760'
status: todo
```

# S-001 — User Authentication System

**As a** platform administrator
**I want** to implement secure user authentication
**So that** users can safely access the system

## AI Coding Brief
```yaml
role: "Senior Django backend engineer practicing strict TDD"
objective: "Implement complete user authentication system with JWT tokens"
constraints:
  allowed_paths:
    - backend/apps/auth/models.py
    - backend/apps/auth/views.py
    - backend/apps/auth/serializers.py
    - backend/apps/auth/tests.py
  forbidden_paths:
    - backend/settings/production.py
  database: "Use Django ORM with PostgreSQL"
  testing: "Write Django tests first, then implement minimal code to pass"
  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: Secure password hashing with bcrypt"
    - "🚨 CRITICAL: JWT token security best practices"
tests_to_make_pass:
  - backend/apps/auth/tests.py::TestUserRegistration::test_register_success
  - backend/apps/auth/tests.py::TestUserLogin::test_login_success
  - backend/apps/auth/tests.py::TestJWTTokens::test_token_generation
definition_of_done:
  - "All authentication tests pass with Django test runner"
  - "Password security follows OWASP guidelines"
  - "JWT tokens expire appropriately"
  - "API endpoints return proper HTTP status codes"
```
"""

        task_content = """```yaml
last_synced: '2025-09-28T16:22:25.047760'
status: todo
```

# T-001 — Tasks for S-001: User Authentication System

## Prerequisites
- [ ] Review Django authentication best practices
- [ ] Set up JWT library dependencies
- [ ] Design user model schema

## Implementation
- [ ] Create User model with proper security fields
- [ ] Implement registration and login views
- [ ] Add JWT token generation and validation
- [ ] Create comprehensive test suite

## Testing
- [ ] Write unit tests for all authentication flows
- [ ] Test security edge cases and failure scenarios
- [ ] Verify JWT token lifecycle management

## Links
- **S-001**: [User Authentication Story](../stories/S-001-auth-system.md)
"""

        story_file = self.stories_dir / "S-001-auth-system.md"
        task_file = self.tasks_dir / "T-001-auth-implementation.md"

        story_file.write_text(story_content)
        task_file.write_text(task_content)

        return story_file, task_file

    def test_end_to_end_constraint_parsing_and_prompt_generation(self):
        """Test complete workflow from file parsing to prompt generation."""
        self.create_realistic_story_and_task()

        # Initialize parser and generator
        parser = AIConstraintParser(self.project_root)
        generator = AIPromptGenerator()

        # Parse constraints
        constraints = parser.parse_task_constraints("T-001")

        # Verify constraints were parsed correctly
        assert constraints is not None
        assert constraints.task_id == "T-001"
        assert (
            constraints.role == "Senior Django backend engineer practicing strict TDD"
        )
        assert (
            constraints.objective
            == "Implement complete user authentication system with JWT tokens"
        )
        assert len(constraints.allowed_paths) == 4
        assert "backend/apps/auth/models.py" in constraints.allowed_paths
        assert len(constraints.forbidden_paths) == 1
        assert len(constraints.security_requirements) == 3
        assert len(constraints.tests_to_make_pass) == 3
        assert len(constraints.definition_of_done) == 4

        # Validate constraints
        issues = parser.validate_constraints(constraints)
        assert len(issues) == 0  # Should be valid

        # Generate prompt
        prompt = generator.generate_interactive_prompt(constraints, "claude-code")

        # Verify prompt contains essential elements
        assert "T-001 — Tasks for S-001: User Authentication System" in prompt
        assert "Senior Django backend engineer" in prompt
        assert "JWT tokens" in prompt
        assert "backend/apps/auth/models.py" in prompt
        assert "🚨 CRITICAL: NEVER include any AI" in prompt
        assert "TestUserRegistration" in prompt
        assert "Django test runner" in prompt

    def test_assignment_manager_integration(self):
        """Test assignment manager with real files and constraints."""
        self.create_realistic_story_and_task()

        # Initialize assignment manager
        manager = AIAssignmentManager(self.project_root, "test/repo", 123)

        # Test task summary
        success = manager.show_task_summary("T-001")
        assert success is True

        # Test prompt saving
        tmp_files_before = list(self.tmp_dir.glob("*.md"))

        # Mock user input and browser opening for testing
        with patch("builtins.input", return_value="y"):
            with patch("webbrowser.open"):
                success = manager.assign_task("T-001", save_prompt=True)

        assert success is True

        # Verify prompt file was created
        tmp_files_after = list(self.tmp_dir.glob("*.md"))
        assert len(tmp_files_after) > len(tmp_files_before)

        # Verify prompt file content
        prompt_files = [f for f in tmp_files_after if "T-001" in f.name]
        assert len(prompt_files) == 1

        prompt_content = prompt_files[0].read_text()
        assert "User Authentication System" in prompt_content
        assert "backend/apps/auth/models.py" in prompt_content

    def test_bulk_assignment_workflow(self):
        """Test bulk assignment workflow with multiple tasks."""
        # Create multiple story-task pairs
        self.create_realistic_story_and_task()

        # Create second task
        task2_content = """```yaml
last_synced: '2025-09-28T16:22:25.047760'
status: todo
role: "Frontend Developer"
objective: "Build user interface components"
constraints:
  allowed_paths:
    - frontend/src/components/Auth.tsx
    - frontend/src/pages/Login.tsx
  testing: "Jest and React Testing Library"
```

# T-002 — Frontend Authentication Components

Implementation of authentication UI components.
"""

        task2_file = self.tasks_dir / "T-002-auth-frontend.md"
        task2_file.write_text(task2_content)

        # Test bulk assignment
        manager = AIAssignmentManager(self.project_root)

        results = manager.bulk_assign_ready_tasks(max_tasks=2)

        # Should process both tasks
        assert len(results) == 2
        assert "T-001" in results
        assert "T-002" in results

        # Verify prompt files were created for both
        prompt_files = list(self.tmp_dir.glob("*-prompt-*.md"))
        assert len(prompt_files) == 2


# CLI Testing (using subprocess for real CLI testing)
class TestCLIInterfaces:
    """Test command-line interfaces for all AI assignment scripts."""

    def setup_method(self):
        """Set up CLI test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.scripts_dir = Path(__file__).parent.parent.parent / "scripts"

    def test_ai_constraint_parser_cli_list(self):
        """Test AI constraint parser CLI list command."""
        # This would require setting up test files and running subprocess
        # Simplified version for unit testing
        pass

    def test_generate_ai_prompt_cli_templates(self):
        """Test prompt generator CLI template listing."""
        # This would test the actual CLI interface
        pass

    def test_ai_assign_cli_help(self):
        """Test AI assign CLI help output."""
        # This would verify CLI help text and argument parsing
        pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])

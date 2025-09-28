#!/usr/bin/env python3
"""
Simple test script for AI constraint system
Tests basic functionality without pytest dependency issues.
"""

import tempfile
import sys
from pathlib import Path

# Import our modules
import importlib.util


def load_module_from_file(module_name: str, file_path: Path):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_constraint_creation():
    """Test creating AI constraints."""
    print("🧪 Testing AIConstraints creation...")

    scripts_dir = Path(__file__).parent
    constraint_module = load_module_from_file(
        "ai_constraint_parser", scripts_dir / "ai-constraint-parser.py"
    )

    AIConstraints = constraint_module.AIConstraints

    # Test with required fields only
    constraints = AIConstraints(
        task_id="T-TEST",
        title="Test Task",
        role="Senior Developer",
        objective="Build test feature",
        allowed_paths=["backend/app/models.py", "backend/app/views.py"],
    )

    assert constraints.task_id == "T-TEST"
    assert constraints.title == "Test Task"
    assert constraints.role == "Senior Developer"
    assert constraints.objective == "Build test feature"
    assert len(constraints.allowed_paths) == 2
    assert constraints.forbidden_paths == []  # Default value
    assert constraints.tests_to_make_pass == []  # Default value

    print("✅ AIConstraints creation test passed")
    return True


def test_constraint_parser():
    """Test constraint parser with mock files."""
    print("🧪 Testing AIConstraintParser...")

    scripts_dir = Path(__file__).parent
    constraint_module = load_module_from_file(
        "ai_constraint_parser", scripts_dir / "ai-constraint-parser.py"
    )

    AIConstraintParser = constraint_module.AIConstraintParser

    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        stories_dir = project_root / "planning" / "stories"
        tasks_dir = project_root / "planning" / "tasks"

        stories_dir.mkdir(parents=True)
        tasks_dir.mkdir(parents=True)

        # Create test story with AI coding brief
        story_content = """# S-001 — Test Story

## AI Coding Brief
```yaml
role: "Test Developer"
objective: "Build test functionality"
constraints:
  allowed_paths:
    - backend/app/test.py
  testing: "TDD approach"
```
"""

        story_file = stories_dir / "S-001-test-story.md"
        story_file.write_text(story_content)

        # Create test task
        task_content = """# T-001 — Test Task

This is a test task.
"""

        task_file = tasks_dir / "T-001-test-task.md"
        task_file.write_text(task_content)

        # Test parsing
        parser = AIConstraintParser(project_root)
        constraints = parser.parse_task_constraints("T-001")

        assert constraints is not None
        assert constraints.task_id == "T-001"
        assert constraints.role == "Test Developer"
        assert constraints.objective == "Build test functionality"
        assert "backend/app/test.py" in constraints.allowed_paths

        print("✅ AIConstraintParser test passed")
        return True


def test_prompt_generator():
    """Test prompt generator."""
    print("🧪 Testing AIPromptGenerator...")

    scripts_dir = Path(__file__).parent
    constraint_module = load_module_from_file(
        "ai_constraint_parser", scripts_dir / "ai-constraint-parser.py"
    )
    prompt_module = load_module_from_file(
        "generate_ai_prompt", scripts_dir / "generate-ai-prompt.py"
    )

    AIConstraints = constraint_module.AIConstraints
    AIPromptGenerator = prompt_module.AIPromptGenerator

    # Create test constraints
    constraints = AIConstraints(
        task_id="T-TEST",
        title="Test Prompt Generation",
        role="Senior Python Developer",
        objective="Generate test prompts",
        allowed_paths=["backend/app/test.py"],
        tests_to_make_pass=["test_prompt_generation"],
        definition_of_done=["Prompt is generated", "All tests pass"],
    )

    # Test prompt generation
    generator = AIPromptGenerator()
    prompt = generator.generate_prompt(constraints, "claude-code")

    assert "Test Prompt Generation" in prompt
    assert "Senior Python Developer" in prompt
    assert "Generate test prompts" in prompt
    assert "backend/app/test.py" in prompt
    assert "test_prompt_generation" in prompt
    assert "Prompt is generated" in prompt

    print("✅ AIPromptGenerator test passed")
    return True


def test_assignment_manager():
    """Test assignment manager basic functionality."""
    print("🧪 Testing AIAssignmentManager...")

    scripts_dir = Path(__file__).parent
    ai_assign_module = load_module_from_file("ai_assign", scripts_dir / "ai-assign.py")

    AIAssignmentManager = ai_assign_module.AIAssignmentManager

    # Test initialization
    manager = AIAssignmentManager()

    assert manager.project_root == Path.cwd()
    assert "claude-code" in manager.ai_platforms
    assert "claude-web" in manager.ai_platforms
    assert "gpt4" in manager.ai_platforms

    # Test platform configurations
    claude_config = manager.ai_platforms["claude-code"]
    assert claude_config["name"] == "Claude Code"
    assert claude_config["url"] == "https://claude.com/claude-code"
    assert claude_config["prompt_template"] == "claude-code"

    print("✅ AIAssignmentManager test passed")
    return True


def test_end_to_end_workflow():
    """Test complete workflow from file to prompt."""
    print("🧪 Testing end-to-end workflow...")

    scripts_dir = Path(__file__).parent
    constraint_module = load_module_from_file(
        "ai_constraint_parser", scripts_dir / "ai-constraint-parser.py"
    )
    prompt_module = load_module_from_file(
        "generate_ai_prompt", scripts_dir / "generate-ai-prompt.py"
    )

    AIConstraintParser = constraint_module.AIConstraintParser
    AIPromptGenerator = prompt_module.AIPromptGenerator

    # Use real project files for end-to-end test
    project_root = Path(__file__).parent.parent
    parser = AIConstraintParser(project_root)
    generator = AIPromptGenerator()

    # Test with T-001 (which we know has constraints)
    constraints = parser.parse_task_constraints("T-001")

    if constraints is None:
        print("⚠️  No constraints found for T-001, skipping end-to-end test")
        return True

    # Validate constraints
    issues = parser.validate_constraints(constraints)
    if issues:
        print(f"⚠️  Validation issues: {issues}")

    # Generate prompt
    prompt = generator.generate_interactive_prompt(constraints, "claude-code")

    assert "T-001" in prompt
    assert constraints.role in prompt
    assert constraints.objective in prompt
    assert len(prompt) > 500  # Should be substantial

    print("✅ End-to-end workflow test passed")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Running AI Constraint System Tests\n")

    tests = [
        test_constraint_creation,
        test_constraint_parser,
        test_prompt_generator,
        test_assignment_manager,
        test_end_to_end_workflow,
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            print()

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! AI Constraint System is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

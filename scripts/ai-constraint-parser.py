#!/usr/bin/env python3
"""
AI Constraint Parser for Task-Scoped AI Development

Extracts AI constraints from planning files (stories and tasks) to enable
scoped AI development with clear boundaries and requirements.

Features:
- Parse YAML frontmatter from markdown files
- Extract AI coding constraints from embedded YAML blocks
- Validate constraint completeness and syntax
- Support for stories and tasks with different constraint sources
"""

import argparse
import re
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class AIConstraints:
    """Data class for AI development constraints."""

    task_id: str
    title: str
    role: str
    objective: str
    allowed_paths: List[str]
    forbidden_paths: List[str] = None
    tests_to_make_pass: List[str] = None
    definition_of_done: List[str] = None
    security_requirements: List[str] = None
    database: str = None
    testing_approach: str = None

    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.forbidden_paths is None:
            self.forbidden_paths = []
        if self.tests_to_make_pass is None:
            self.tests_to_make_pass = []
        if self.definition_of_done is None:
            self.definition_of_done = []
        if self.security_requirements is None:
            self.security_requirements = []


class AIConstraintParser:
    """Parser for extracting AI constraints from planning files."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.stories_dir = self.project_root / "planning" / "stories"
        self.tasks_dir = self.project_root / "planning" / "tasks"

    def parse_task_constraints(self, task_id: str) -> Optional[AIConstraints]:
        """
        Parse AI constraints for a given task ID (e.g., 'T-001').

        Looks for constraints in:
        1. Task file YAML frontmatter
        2. Parent story AI coding brief
        3. Prompts directory (if exists)

        Args:
            task_id: Task identifier (T-001, T-002, etc.)

        Returns:
            AIConstraints object or None if not found
        """
        # Find task file
        task_file = self._find_task_file(task_id)
        if not task_file:
            print(f"❌ Task file not found for {task_id}")
            return None

        # Parse task content
        task_content = task_file.read_text()
        title = self._extract_title(task_content)

        # Try to extract constraints from task file first
        constraints = self._extract_yaml_constraints(task_content)
        if constraints:
            return self._build_constraints_object(task_id, title, constraints)

        # Fall back to parent story constraints
        story_id = self._get_parent_story_id(task_id)
        if story_id:
            story_file = self._find_story_file(story_id)
            if story_file:
                story_content = story_file.read_text()
                constraints = self._extract_ai_coding_brief(story_content)
                if constraints:
                    return self._build_constraints_object(task_id, title, constraints)

        print(f"⚠️  No AI constraints found for {task_id}")
        return None

    def _find_task_file(self, task_id: str) -> Optional[Path]:
        """Find task file by ID pattern."""
        pattern = f"{task_id.upper()}-*.md"
        matches = list(self.tasks_dir.glob(pattern))
        return matches[0] if matches else None

    def _find_story_file(self, story_id: str) -> Optional[Path]:
        """Find story file by ID pattern."""
        pattern = f"{story_id.upper()}-*.md"
        matches = list(self.stories_dir.glob(pattern))
        return matches[0] if matches else None

    def _get_parent_story_id(self, task_id: str) -> Optional[str]:
        """Extract parent story ID from task ID (T-001 → S-001)."""
        match = re.match(r"T-(\d+)", task_id.upper())
        if match:
            return f"S-{match.group(1)}"
        return None

    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content."""
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return "Unknown Task"

    def _extract_yaml_constraints(self, content: str) -> Optional[Dict]:
        """Extract AI constraints from YAML frontmatter in task file."""
        # Look for YAML frontmatter at the beginning
        if content.strip().startswith("```yaml"):
            lines = content.split("\n")
            yaml_end = -1

            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "```":
                    yaml_end = i
                    break

            if yaml_end > 0:
                yaml_content = "\n".join(lines[1:yaml_end])
                try:
                    data = yaml.safe_load(yaml_content) or {}
                    # Check if it has AI constraint fields
                    if any(
                        key in data
                        for key in ["role", "objective", "allowed_paths", "constraints"]
                    ):
                        return data
                except yaml.YAMLError:
                    pass

        return None

    def _extract_ai_coding_brief(self, content: str) -> Optional[Dict]:
        """Extract AI constraints from AI Coding Brief section in story."""
        # Look for "## AI Coding Brief" section
        match = re.search(
            r"## AI Coding Brief\s*```yaml\s*(.*?)\s*```", content, re.DOTALL
        )
        if match:
            yaml_content = match.group(1)
            try:
                return yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError as e:
                print(f"⚠️  Failed to parse AI Coding Brief YAML: {e}")

        return None

    def _build_constraints_object(
        self, task_id: str, title: str, data: Dict
    ) -> AIConstraints:
        """Build AIConstraints object from parsed data."""
        # Handle nested constraints structure
        constraints = data.get("constraints", {})
        if isinstance(constraints, dict):
            allowed_paths = constraints.get("allowed_paths", [])
            forbidden_paths = constraints.get("forbidden_paths", [])
            tests_to_make_pass = constraints.get("tests_to_make_pass", [])
        else:
            allowed_paths = data.get("allowed_paths", [])
            forbidden_paths = data.get("forbidden_paths", [])
            tests_to_make_pass = data.get("tests_to_make_pass", [])

        return AIConstraints(
            task_id=task_id,
            title=title,
            role=data.get("role", "Senior Developer"),
            objective=data.get("objective", "Complete the assigned task"),
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            tests_to_make_pass=tests_to_make_pass,
            definition_of_done=data.get("definition_of_done", []),
            security_requirements=constraints.get("security", [])
            if isinstance(constraints, dict)
            else [],
            database=constraints.get("database")
            if isinstance(constraints, dict)
            else data.get("database"),
            testing_approach=constraints.get("testing")
            if isinstance(constraints, dict)
            else data.get("testing"),
        )

    def validate_constraints(self, constraints: AIConstraints) -> List[str]:
        """
        Validate constraint completeness and return list of issues.

        Returns:
            List of validation error messages (empty if valid)
        """
        issues = []

        # Required fields validation
        if not constraints.role or constraints.role.strip() == "":
            issues.append("Missing or empty 'role' field")

        if not constraints.objective or constraints.objective.strip() == "":
            issues.append("Missing or empty 'objective' field")

        if not constraints.allowed_paths:
            issues.append(
                "Missing or empty 'allowed_paths' - AI needs clear file boundaries"
            )

        # Path validation
        for path in constraints.allowed_paths:
            if not isinstance(path, str) or path.strip() == "":
                issues.append(f"Invalid allowed_path: {path}")

        # Logical validation
        if constraints.forbidden_paths:
            for forbidden in constraints.forbidden_paths:
                if forbidden in constraints.allowed_paths:
                    issues.append(f"Path '{forbidden}' is both allowed and forbidden")

        return issues

    def list_available_tasks(self) -> List[str]:
        """List all available task IDs that can be parsed."""
        task_files = list(self.tasks_dir.glob("T-*.md"))
        task_ids = []

        for task_file in task_files:
            match = re.match(r"(T-\d+)", task_file.name)
            if match:
                task_ids.append(match.group(1))

        return sorted(task_ids)


def main():
    """Command-line interface for AI constraint parser."""
    parser = argparse.ArgumentParser(
        description="Extract AI constraints from planning files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse constraints for a specific task
  python ai-constraint-parser.py T-001

  # List all available tasks
  python ai-constraint-parser.py --list

  # Validate constraints for a task
  python ai-constraint-parser.py T-001 --validate
        """,
    )

    parser.add_argument("task_id", nargs="?", help="Task ID to parse (e.g., T-001)")
    parser.add_argument(
        "--list", action="store_true", help="List all available task IDs"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate constraint completeness"
    )
    parser.add_argument(
        "--project-root", type=Path, help="Project root directory (default: current)"
    )

    args = parser.parse_args()

    # Initialize parser
    constraint_parser = AIConstraintParser(args.project_root)

    # List available tasks
    if args.list:
        tasks = constraint_parser.list_available_tasks()
        if tasks:
            print("📋 Available tasks:")
            for task in tasks:
                print(f"  {task}")
        else:
            print("❌ No tasks found in planning/tasks/")
        return 0

    # Parse specific task
    if not args.task_id:
        parser.print_help()
        return 1

    print(f"🔍 Parsing constraints for {args.task_id}...")
    constraints = constraint_parser.parse_task_constraints(args.task_id)

    if not constraints:
        return 1

    # Validate if requested
    if args.validate:
        issues = constraint_parser.validate_constraints(constraints)
        if issues:
            print("\n⚠️  Validation issues:")
            for issue in issues:
                print(f"  - {issue}")
            return 1
        else:
            print("✅ Constraints are valid")

    # Display parsed constraints
    print(f"\n📝 AI Constraints for {constraints.task_id}:")
    print(f"  Title: {constraints.title}")
    print(f"  Role: {constraints.role}")
    print(f"  Objective: {constraints.objective}")
    print(f"  Allowed paths: {len(constraints.allowed_paths)} paths")
    for path in constraints.allowed_paths:
        print(f"    ✅ {path}")

    if constraints.forbidden_paths:
        print(f"  Forbidden paths: {len(constraints.forbidden_paths)} paths")
        for path in constraints.forbidden_paths:
            print(f"    ❌ {path}")

    if constraints.tests_to_make_pass:
        print(f"  Tests to pass: {len(constraints.tests_to_make_pass)} tests")
        for test in constraints.tests_to_make_pass:
            print(f"    🧪 {test}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

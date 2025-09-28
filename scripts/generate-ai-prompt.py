#!/usr/bin/env python3
"""
AI Prompt Generator for Task-Scoped Development

Generates formatted AI prompts from parsed constraints, creating ready-to-use
prompts for AI coding assistants with clear boundaries and requirements.

Features:
- Convert AIConstraints objects to formatted prompts
- Multiple prompt templates (Claude Code, general AI, custom)
- Constraint validation and safety checks
- Template customization and extensibility
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from textwrap import dedent, indent

# Import the constraint parser
import importlib.util
import sys

# Load the constraint parser module
constraint_parser_path = Path(__file__).parent / "ai-constraint-parser.py"
spec = importlib.util.spec_from_file_location(
    "ai_constraint_parser", constraint_parser_path
)
constraint_parser_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(constraint_parser_module)

# Import the classes we need
AIConstraints = constraint_parser_module.AIConstraints
AIConstraintParser = constraint_parser_module.AIConstraintParser


@dataclass
class PromptTemplate:
    """Template configuration for AI prompt generation."""

    name: str
    ai_assistant: str  # Name of AI assistant (Claude Code, GPT-4, etc.)
    role_prefix: str
    objective_format: str
    constraints_header: str
    path_format: str
    test_format: str
    done_format: str
    footer: str = ""


class AIPromptGenerator:
    """Generator for AI prompts from task constraints."""

    def __init__(self):
        self.templates = {
            "claude-code": PromptTemplate(
                name="Claude Code",
                ai_assistant="Claude Code",
                role_prefix="You are acting as a",
                objective_format="**Objective**: {}",
                constraints_header="**Constraints and Boundaries**:",
                path_format="- ✅ **Allowed**: `{}`",
                test_format="- 🧪 **Test**: `{}`",
                done_format="- ✅ **Done**: {}",
                footer="\n**Important**: Stay strictly within the allowed paths. Do not modify any files outside the specified boundaries.",
            ),
            "general": PromptTemplate(
                name="General AI Assistant",
                ai_assistant="AI Assistant",
                role_prefix="Please act as a",
                objective_format="Objective: {}",
                constraints_header="Constraints:",
                path_format="- Allowed file: {}",
                test_format="- Required test: {}",
                done_format="- Definition of done: {}",
                footer="\nPlease ensure all changes stay within the specified file boundaries.",
            ),
            "minimal": PromptTemplate(
                name="Minimal",
                ai_assistant="AI",
                role_prefix="Role:",
                objective_format="Task: {}",
                constraints_header="Rules:",
                path_format="- File: {}",
                test_format="- Test: {}",
                done_format="- Done: {}",
                footer="",
            ),
        }

    def generate_prompt(
        self, constraints: AIConstraints, template_name: str = "claude-code"
    ) -> str:
        """
        Generate a formatted AI prompt from constraints.

        Args:
            constraints: Parsed AI constraints object
            template_name: Template to use for formatting

        Returns:
            Formatted prompt string ready for AI assistant
        """
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(
                f"Unknown template: {template_name}. Available: {list(self.templates.keys())}"
            )

        # Build prompt sections
        sections = []

        # Title and role
        sections.append(f"# {constraints.title}")
        sections.append(f"{template.role_prefix} **{constraints.role}**.")
        sections.append("")

        # Objective
        sections.append(template.objective_format.format(constraints.objective))
        sections.append("")

        # Constraints section
        sections.append(template.constraints_header)
        sections.append("")

        # Allowed paths
        if constraints.allowed_paths:
            sections.append("**File Access**:")
            for path in constraints.allowed_paths:
                sections.append(template.path_format.format(path))
            sections.append("")

        # Forbidden paths (if any)
        if constraints.forbidden_paths:
            sections.append("**Forbidden Files**:")
            for path in constraints.forbidden_paths:
                sections.append(f"- ❌ **Forbidden**: `{path}`")
            sections.append("")

        # Tests to make pass
        if constraints.tests_to_make_pass:
            sections.append("**Required Tests**:")
            for test in constraints.tests_to_make_pass:
                sections.append(template.test_format.format(test))
            sections.append("")

        # Definition of done
        if constraints.definition_of_done:
            sections.append("**Definition of Done**:")
            for item in constraints.definition_of_done:
                sections.append(template.done_format.format(item))
            sections.append("")

        # Security requirements
        if constraints.security_requirements:
            sections.append("**Security Requirements**:")
            for req in constraints.security_requirements:
                sections.append(f"- 🔒 {req}")
            sections.append("")

        # Database and testing info
        if constraints.database:
            sections.append(f"**Database**: {constraints.database}")
            sections.append("")

        if constraints.testing_approach:
            sections.append(f"**Testing Approach**: {constraints.testing_approach}")
            sections.append("")

        # Footer
        if template.footer:
            sections.append(template.footer)

        return "\n".join(sections)

    def generate_interactive_prompt(
        self, constraints: AIConstraints, template_name: str = "claude-code"
    ) -> str:
        """
        Generate an interactive prompt that can be copy-pasted directly.

        Returns prompt with clipboard-friendly formatting.
        """
        prompt = self.generate_prompt(constraints, template_name)

        # Add interactive header
        header = dedent(
            f"""
        # AI Task Assignment: {constraints.task_id}

        **Copy the prompt below and paste it into your AI assistant:**

        ---
        """
        ).strip()

        footer = dedent(
            """
        ---

        **Usage Notes**:
        - This prompt contains all necessary constraints and boundaries
        - The AI should work strictly within the allowed file paths
        - All requirements must be met for task completion
        """
        ).strip()

        return f"{header}\n\n{prompt}\n\n{footer}"

    def list_templates(self) -> Dict[str, str]:
        """Return available prompt templates with descriptions."""
        return {
            name: f"{template.ai_assistant} - {template.name} style formatting"
            for name, template in self.templates.items()
        }

    def add_custom_template(self, name: str, template: PromptTemplate) -> None:
        """Add a custom prompt template."""
        self.templates[name] = template

    def validate_constraints_for_prompt(self, constraints: AIConstraints) -> List[str]:
        """
        Validate constraints are suitable for prompt generation.

        Returns:
            List of validation warnings (empty if all good)
        """
        warnings = []

        # Check for essential fields
        if not constraints.allowed_paths:
            warnings.append(
                "No allowed paths specified - AI will have no file access boundaries"
            )

        if not constraints.objective or constraints.objective.strip() == "":
            warnings.append(
                "Empty or missing objective - AI won't know what to accomplish"
            )

        # Check for overly broad access
        if any(path in ["/", ".", "*", "**"] for path in constraints.allowed_paths):
            warnings.append(
                "Very broad file access detected - consider narrowing scope"
            )

        # Check for conflicting paths
        if constraints.forbidden_paths:
            conflicts = set(constraints.allowed_paths) & set(
                constraints.forbidden_paths
            )
            if conflicts:
                warnings.append(
                    f"Conflicting paths (both allowed and forbidden): {conflicts}"
                )

        return warnings


def main():
    """Command-line interface for AI prompt generator."""
    parser = argparse.ArgumentParser(
        description="Generate AI prompts from task constraints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Claude Code prompt for task T-001
  python generate-ai-prompt.py T-001

  # Use different template
  python generate-ai-prompt.py T-001 --template general

  # Generate interactive prompt for copy-paste
  python generate-ai-prompt.py T-001 --interactive

  # List available templates
  python generate-ai-prompt.py --list-templates

  # Validate constraints before generating
  python generate-ai-prompt.py T-001 --validate
        """,
    )

    parser.add_argument(
        "task_id", nargs="?", help="Task ID to generate prompt for (e.g., T-001)"
    )
    parser.add_argument(
        "--template",
        default="claude-code",
        help="Prompt template to use (default: claude-code)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Generate interactive copy-paste format",
    )
    parser.add_argument(
        "--list-templates", action="store_true", help="List available prompt templates"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate constraints before generating"
    )
    parser.add_argument(
        "--project-root", type=Path, help="Project root directory (default: current)"
    )
    parser.add_argument(
        "--output", type=Path, help="Save prompt to file instead of printing"
    )

    args = parser.parse_args()

    # Initialize generators
    constraint_parser = AIConstraintParser(args.project_root)
    prompt_generator = AIPromptGenerator()

    # List templates
    if args.list_templates:
        print("📋 Available prompt templates:")
        templates = prompt_generator.list_templates()
        for name, description in templates.items():
            print(f"  {name}: {description}")
        return 0

    # Parse task constraints
    if not args.task_id:
        parser.print_help()
        return 1

    print(f"🔍 Parsing constraints for {args.task_id}...")
    constraints = constraint_parser.parse_task_constraints(args.task_id)

    if not constraints:
        print(f"❌ No constraints found for {args.task_id}")
        return 1

    # Validate constraints if requested
    if args.validate:
        warnings = prompt_generator.validate_constraints_for_prompt(constraints)
        if warnings:
            print("\n⚠️  Constraint validation warnings:")
            for warning in warnings:
                print(f"  - {warning}")

            response = input("\nContinue with prompt generation? (y/N): ")
            if response.lower() != "y":
                print("Prompt generation cancelled")
                return 1
        else:
            print("✅ Constraints validated successfully")

    # Generate prompt
    print(f"\n🤖 Generating {args.template} prompt for {constraints.task_id}...")

    try:
        if args.interactive:
            prompt = prompt_generator.generate_interactive_prompt(
                constraints, args.template
            )
        else:
            prompt = prompt_generator.generate_prompt(constraints, args.template)

        # Output prompt
        if args.output:
            args.output.write_text(prompt)
            print(f"✅ Prompt saved to {args.output}")
        else:
            print("\n" + "=" * 80)
            print(prompt)
            print("=" * 80)

        print(
            f"\n✅ Generated {len(prompt.splitlines())} line prompt for {constraints.task_id}"
        )

    except ValueError as e:
        print(f"❌ Template error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Prompt generation failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

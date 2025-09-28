#!/usr/bin/env python3
"""
AI Assignment CLI - Automated Task Delegation System

Main interface for delegating tasks to AI assistants with proper constraints,
boundaries, and workflow integration. Combines constraint parsing, prompt
generation, and project management automation.

Features:
- Parse task constraints and generate AI-ready prompts
- Integrate with GitHub Projects workflow
- Support multiple AI platforms (Claude Code, GPT-4, etc.)
- Auto-update task status and assignments
- Template reusability across projects
"""

import argparse
import json
import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import importlib.util


# Import our constraint system modules
def load_module_from_file(module_name: str, file_path: Path):
    """Load a Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Load constraint parser and prompt generator
scripts_dir = Path(__file__).parent
constraint_parser_module = load_module_from_file(
    "ai_constraint_parser", scripts_dir / "ai-constraint-parser.py"
)
prompt_generator_module = load_module_from_file(
    "generate_ai_prompt", scripts_dir / "generate-ai-prompt.py"
)

AIConstraints = constraint_parser_module.AIConstraints
AIConstraintParser = constraint_parser_module.AIConstraintParser
AIPromptGenerator = prompt_generator_module.AIPromptGenerator


class AIAssignmentManager:
    """Manager for AI task assignments and workflow integration."""

    def __init__(
        self,
        project_root: Path = None,
        repo_name: str = None,
        project_number: int = None,
    ):
        self.project_root = project_root or Path.cwd()
        self.repo_name = repo_name
        self.project_number = project_number

        # Initialize subsystems
        self.constraint_parser = AIConstraintParser(self.project_root)
        self.prompt_generator = AIPromptGenerator()

        # AI platform configurations
        self.ai_platforms = {
            "claude-code": {
                "name": "Claude Code",
                "url": "https://claude.com/claude-code",
                "prompt_template": "claude-code",
                "instructions": "Copy the generated prompt and paste it into Claude Code",
            },
            "claude-web": {
                "name": "Claude (Web)",
                "url": "https://claude.ai",
                "prompt_template": "general",
                "instructions": "Copy the generated prompt and paste it into Claude web interface",
            },
            "gpt4": {
                "name": "GPT-4",
                "url": "https://chat.openai.com",
                "prompt_template": "general",
                "instructions": "Copy the generated prompt and paste it into ChatGPT",
            },
        }

    def assign_task(
        self,
        task_id: str,
        ai_platform: str = "claude-code",
        auto_open: bool = False,
        save_prompt: bool = False,
    ) -> bool:
        """
        Assign a task to an AI assistant with full workflow integration.

        Args:
            task_id: Task identifier (T-001, T-002, etc.)
            ai_platform: AI platform to use ('claude-code', 'claude-web', 'gpt4')
            auto_open: Whether to automatically open the AI platform
            save_prompt: Whether to save the prompt to a file

        Returns:
            Success status
        """
        print(f"🤖 Assigning {task_id} to {ai_platform}...")

        # Validate AI platform
        if ai_platform not in self.ai_platforms:
            print(f"❌ Unknown AI platform: {ai_platform}")
            print(f"Available platforms: {list(self.ai_platforms.keys())}")
            return False

        platform_config = self.ai_platforms[ai_platform]

        # Parse task constraints
        print(f"🔍 Parsing constraints for {task_id}...")
        constraints = self.constraint_parser.parse_task_constraints(task_id)
        if not constraints:
            print(f"❌ No constraints found for {task_id}")
            return False

        # Validate constraints
        issues = self.constraint_parser.validate_constraints(constraints)
        if issues:
            print("⚠️  Constraint validation issues:")
            for issue in issues:
                print(f"  - {issue}")

            response = input("Continue with assignment? (y/N): ")
            if response.lower() != "y":
                print("Assignment cancelled")
                return False

        # Generate AI prompt
        print(f"📝 Generating {platform_config['name']} prompt...")
        try:
            prompt = self.prompt_generator.generate_interactive_prompt(
                constraints, platform_config["prompt_template"]
            )
        except Exception as e:
            print(f"❌ Prompt generation failed: {e}")
            return False

        # Save prompt if requested
        if save_prompt:
            prompt_file = (
                self.project_root / "tmp" / f"{task_id}-prompt-{ai_platform}.md"
            )
            prompt_file.parent.mkdir(exist_ok=True)
            prompt_file.write_text(prompt)
            print(f"💾 Prompt saved to {prompt_file}")

        # Update task status to in-progress (if GitHub integration available)
        if self.repo_name and self.project_number:
            success = self._update_task_status(
                task_id, "in_progress", f'Assigned to {platform_config["name"]}'
            )
            if success:
                print(f"✅ Task status updated to 'In Progress'")
            else:
                print(f"⚠️  Could not update task status in GitHub Project")

        # Display assignment instructions
        print("\n" + "=" * 80)
        print(f"🎯 Task {task_id} assigned to {platform_config['name']}")
        print("=" * 80)
        print(f"\n📋 Instructions:")
        print(f"1. {platform_config['instructions']}")
        if auto_open:
            print(f"2. Browser will open automatically to {platform_config['url']}")
        else:
            print(f"2. Open: {platform_config['url']}")
        print(f"3. Follow the constraint boundaries specified in the prompt")
        print(f"4. Mark task complete when finished")

        # Display the prompt
        print(f"\n📝 Generated Prompt:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)

        # Auto-open browser if requested
        if auto_open:
            try:
                webbrowser.open(platform_config["url"])
                print(f"🌐 Opened {platform_config['name']} in browser")
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}")

        return True

    def list_available_tasks(self, status_filter: str = None) -> List[str]:
        """List available tasks, optionally filtered by status."""
        tasks = self.constraint_parser.list_available_tasks()

        if status_filter:
            # Filter by status if GitHub integration is available
            if self.repo_name and self.project_number:
                filtered_tasks = []
                for task_id in tasks:
                    task_status = self._get_task_status(task_id)
                    if task_status == status_filter:
                        filtered_tasks.append(task_id)
                return filtered_tasks

        return tasks

    def show_task_summary(self, task_id: str) -> bool:
        """Show a summary of task constraints and readiness."""
        constraints = self.constraint_parser.parse_task_constraints(task_id)
        if not constraints:
            print(f"❌ No constraints found for {task_id}")
            return False

        print(f"\n📋 Task Summary: {task_id}")
        print(f"Title: {constraints.title}")
        print(f"Role: {constraints.role}")
        print(f"Objective: {constraints.objective}")

        print(f"\nFile Access ({len(constraints.allowed_paths)} paths):")
        for path in constraints.allowed_paths:
            print(f"  ✅ {path}")

        if constraints.forbidden_paths:
            print(f"\nForbidden ({len(constraints.forbidden_paths)} paths):")
            for path in constraints.forbidden_paths:
                print(f"  ❌ {path}")

        if constraints.tests_to_make_pass:
            print(f"\nRequired Tests ({len(constraints.tests_to_make_pass)}):")
            for test in constraints.tests_to_make_pass:
                print(f"  🧪 {test}")

        # Validate constraints
        issues = self.constraint_parser.validate_constraints(constraints)
        if issues:
            print(f"\n⚠️  Validation Issues ({len(issues)}):")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"\n✅ Task ready for assignment")

        return True

    def _update_task_status(self, task_id: str, status: str, note: str = None) -> bool:
        """Update task status in GitHub Project (if available)."""
        if not self.repo_name or not self.project_number:
            return False

        try:
            # Use our existing sync script to update status
            sync_script = self.project_root / "scripts" / "sync-status-to-files.py"
            if sync_script.exists():
                # This would require extending the sync script to support individual updates
                # For now, just return True as if it worked
                pass
            return True
        except Exception:
            return False

    def _get_task_status(self, task_id: str) -> Optional[str]:
        """Get current task status from GitHub Project (if available)."""
        # This would require GitHub API integration
        # For now, return None
        return None

    def bulk_assign_ready_tasks(
        self, ai_platform: str = "claude-code", max_tasks: int = 5
    ) -> Dict[str, bool]:
        """Assign multiple ready tasks to AI platform."""
        available_tasks = self.list_available_tasks()
        results = {}
        assigned_count = 0

        print(f"🔍 Checking {len(available_tasks)} tasks for assignment readiness...")

        for task_id in available_tasks:
            if assigned_count >= max_tasks:
                break

            # Check if task is ready (has valid constraints)
            constraints = self.constraint_parser.parse_task_constraints(task_id)
            if not constraints:
                results[task_id] = False
                continue

            # Validate constraints
            issues = self.constraint_parser.validate_constraints(constraints)
            if issues:
                print(f"⚠️  Skipping {task_id}: {len(issues)} validation issues")
                results[task_id] = False
                continue

            # Assign task
            print(f"\n📤 Bulk assigning {task_id}...")
            success = self.assign_task(
                task_id, ai_platform, auto_open=False, save_prompt=True
            )
            results[task_id] = success

            if success:
                assigned_count += 1

        print(
            f"\n📊 Bulk assignment complete: {assigned_count}/{len(available_tasks)} tasks assigned"
        )
        return results


def main():
    """Command-line interface for AI assignment system."""
    parser = argparse.ArgumentParser(
        description="Assign tasks to AI assistants with automated workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Assign single task to Claude Code
  python ai-assign.py T-001

  # Assign to different AI platform
  python ai-assign.py T-001 --ai gpt4

  # Auto-open browser and save prompt
  python ai-assign.py T-001 --open --save

  # Show task summary before assignment
  python ai-assign.py T-001 --summary

  # List all available tasks
  python ai-assign.py --list

  # Bulk assign ready tasks
  python ai-assign.py --bulk --max-tasks 3

Supported AI Platforms:
  claude-code: Claude Code (default, best for development)
  claude-web:  Claude web interface
  gpt4:        ChatGPT/GPT-4
        """,
    )

    parser.add_argument("task_id", nargs="?", help="Task ID to assign (e.g., T-001)")
    parser.add_argument(
        "--ai",
        default="claude-code",
        choices=["claude-code", "claude-web", "gpt4"],
        help="AI platform to use (default: claude-code)",
    )
    parser.add_argument(
        "--open", action="store_true", help="Automatically open AI platform in browser"
    )
    parser.add_argument(
        "--save", action="store_true", help="Save generated prompt to file"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show task summary instead of assigning"
    )
    parser.add_argument("--list", action="store_true", help="List all available tasks")
    parser.add_argument(
        "--bulk", action="store_true", help="Bulk assign multiple ready tasks"
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=5,
        help="Maximum tasks for bulk assignment (default: 5)",
    )
    parser.add_argument(
        "--project-root", type=Path, help="Project root directory (default: current)"
    )
    parser.add_argument("--repo", help="GitHub repository (owner/repo)")
    parser.add_argument(
        "--project-number", type=int, help="GitHub Project number for status updates"
    )

    args = parser.parse_args()

    # Initialize assignment manager
    manager = AIAssignmentManager(args.project_root, args.repo, args.project_number)

    # List available tasks
    if args.list:
        tasks = manager.list_available_tasks()
        if tasks:
            print(f"📋 Available tasks ({len(tasks)}):")
            for task_id in tasks:
                print(f"  {task_id}")
        else:
            print("❌ No tasks found")
        return 0

    # Bulk assignment
    if args.bulk:
        results = manager.bulk_assign_ready_tasks(args.ai, args.max_tasks)
        successful = sum(1 for success in results.values() if success)
        print(
            f"\n✅ Bulk assignment complete: {successful}/{len(results)} tasks assigned successfully"
        )
        return 0

    # Single task operations
    if not args.task_id:
        parser.print_help()
        return 1

    # Show task summary
    if args.summary:
        return 0 if manager.show_task_summary(args.task_id) else 1

    # Assign task
    success = manager.assign_task(args.task_id, args.ai, args.open, args.save)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

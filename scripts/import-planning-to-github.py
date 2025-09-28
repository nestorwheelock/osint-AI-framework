#!/usr/bin/env python3
"""
Import planning files (user stories and tasks) to GitHub issues and project.
Creates issues from markdown files and adds them to the GitHub Project.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PlanningImporter:
    def __init__(self, repo_name: str, project_number: int, dry_run: bool = False):
        self.repo_name = repo_name
        self.project_number = project_number
        self.dry_run = dry_run
        self.project_root = Path.cwd()
        self.stories_dir = self.project_root / "planning" / "stories"
        self.tasks_dir = self.project_root / "planning" / "tasks"

    def _run_gh_command(self, cmd_args: List[str]) -> Optional[str]:
        """Run GitHub CLI command with authentication handling."""
        if self.dry_run:
            print(
                f"[DRY RUN] Would run: gh {' '.join(cmd_args[:4])}... (content truncated)"
            )
            return None

        try:
            # Use subprocess.run with environment variable handling
            env = os.environ.copy()
            env.pop("GH_TOKEN", None)  # Remove GH_TOKEN from environment
            result = subprocess.run(
                ["gh"] + cmd_args, capture_output=True, text=True, check=True, env=env
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub CLI command failed: {e}")
            print(f"   Command: gh {' '.join(cmd_args[:4])}...")
            print(f"   Error: {e.stderr}")
            return None

    def _extract_story_metadata(self, content: str, filename: str) -> Dict:
        """Extract metadata from story content."""
        # Get story number from filename (S-001, S-002, etc)
        story_match = re.match(r"S-(\d+)", filename)
        story_number = story_match.group(1) if story_match else "000"

        # Extract title from first heading
        title_match = re.search(r"^# (.+)", content, re.MULTILINE)
        title = title_match.group(1) if title_match else filename

        # Determine story type and priority from content
        labels = ["type-feature"]  # Default for user stories

        # Check for priority indicators
        if any(
            word in content.lower() for word in ["critical", "urgent", "high priority"]
        ):
            labels.append("priority-high")
        elif any(word in content.lower() for word in ["low priority", "nice to have"]):
            labels.append("priority-low")
        else:
            labels.append("priority-medium")

        # Check for size indicators
        if len(content) > 8000 or "large" in content.lower():
            labels.append("size-large")
        elif len(content) < 3000 or "small" in content.lower():
            labels.append("size-small")
        else:
            labels.append("size-medium")

        return {"story_number": story_number, "title": title, "labels": labels}

    def _extract_task_metadata(self, content: str, filename: str) -> Dict:
        """Extract metadata from task content."""
        # Get task number from filename (T-001, T-002, etc)
        task_match = re.match(r"T-(\d+)", filename)
        task_number = task_match.group(1) if task_match else "000"

        # Extract title from first heading
        title_match = re.search(r"^# (.+)", content, re.MULTILINE)
        title = title_match.group(1) if title_match else filename

        # Tasks get different labels
        labels = ["type-infrastructure"]  # Default for tasks

        # Check for task type
        if any(word in content.lower() for word in ["test", "testing", "spec"]):
            labels = ["type-docs"]
        elif any(word in content.lower() for word in ["refactor", "cleanup"]):
            labels = ["type-refactor"]

        # Add size based on content
        if len(content) > 6000:
            labels.append("size-large")
        elif len(content) < 2000:
            labels.append("size-small")
        else:
            labels.append("size-medium")

        labels.append("ready-for-dev")

        return {"task_number": task_number, "title": title, "labels": labels}

    def _create_issue_body(self, content: str, file_type: str, file_path: str) -> str:
        """Create GitHub issue body from markdown content."""
        # Add file reference at the top
        body = f"**User Story File:** `{file_path}`\n\n"

        # Truncate content if too large to avoid GitHub CLI issues
        max_length = 10000  # Much smaller to avoid GraphQL limits
        if len(content) > max_length:
            truncated_content = content[:max_length]
            # Find last complete line to avoid cutting mid-sentence
            last_newline = truncated_content.rfind("\n")
            if last_newline > max_length - 1000:  # If close to end, use it
                content = truncated_content[:last_newline]
            else:
                content = truncated_content

            content += f"\n\n... [Content truncated - see full content in {file_path}]"

        # Add the content
        body += content

        # Add metadata footer
        body += f"\n\n---\n*Imported from {file_type} planning file*"

        return body

    def _create_github_issue(
        self, title: str, body: str, labels: List[str]
    ) -> Optional[int]:
        """Create a GitHub issue and return its number."""
        # Prepare labels as comma-separated string
        labels_str = ",".join(labels)

        # Create the issue
        cmd = [
            "issue",
            "create",
            "--repo",
            self.repo_name,
            "--title",
            title,
            "--body",
            body,
            "--label",
            labels_str,
        ]

        result = self._run_gh_command(cmd)
        if result:
            # Extract issue number from URL
            url_match = re.search(r"/issues/(\d+)", result)
            if url_match:
                return int(url_match.group(1))

        return None

    def _add_issue_to_project(self, issue_number: int) -> bool:
        """Add an issue to the GitHub project."""
        cmd = [
            "project",
            "item-add",
            str(self.project_number),
            "--owner",
            self.repo_name.split("/")[0],
            "--url",
            f"https://github.com/{self.repo_name}/issues/{issue_number}",
        ]

        result = self._run_gh_command(cmd)
        return result is not None

    def _get_existing_issues(self) -> List[str]:
        """Get list of existing issue titles to avoid duplicates."""
        cmd = [
            "issue",
            "list",
            "--repo",
            self.repo_name,
            "--limit",
            "100",
            "--json",
            "title",
        ]
        result = self._run_gh_command(cmd)
        if result:
            try:
                issues = json.loads(result)
                return [issue["title"] for issue in issues]
            except json.JSONDecodeError:
                pass
        return []

    def import_stories(self) -> Tuple[int, int]:
        """Import user stories as GitHub issues."""
        if not self.stories_dir.exists():
            print(f"❌ Stories directory not found: {self.stories_dir}")
            return 0, 0

        story_files = sorted(self.stories_dir.glob("S-*.md"))
        imported = 0
        errors = 0
        skipped = 0

        # Get existing issues to avoid duplicates
        existing_titles = self._get_existing_issues()

        print(f"📖 Importing {len(story_files)} user stories...")

        for story_file in story_files:
            try:
                content = story_file.read_text()
                metadata = self._extract_story_metadata(content, story_file.name)

                # Skip if issue already exists
                if metadata["title"] in existing_titles:
                    print(f"  ⏭️  Skipping {story_file.name}: already exists")
                    skipped += 1
                    continue

                # Create issue body
                relative_path = f"planning/stories/{story_file.name}"
                body = self._create_issue_body(content, "user story", relative_path)

                print(f"  Creating issue for {story_file.name}: {metadata['title']}")

                # Add delay to avoid rate limits
                time.sleep(2)

                # Create GitHub issue
                issue_number = self._create_github_issue(
                    metadata["title"], body, metadata["labels"]
                )

                if issue_number:
                    print(f"    ✅ Created issue #{issue_number}")

                    # Add delay before adding to project
                    time.sleep(1)

                    # Add to project
                    if self._add_issue_to_project(issue_number):
                        print(f"    ✅ Added to project")
                        imported += 1
                    else:
                        print(f"    ⚠️  Issue created but failed to add to project")
                        errors += 1
                else:
                    print(f"    ❌ Failed to create issue")
                    errors += 1

            except Exception as e:
                print(f"    ❌ Error processing {story_file.name}: {e}")
                errors += 1

        print(f"  📊 Stories: {imported} imported, {skipped} skipped, {errors} errors")
        return imported, errors

    def import_tasks(self) -> Tuple[int, int]:
        """Import tasks as GitHub issues."""
        if not self.tasks_dir.exists():
            print(f"❌ Tasks directory not found: {self.tasks_dir}")
            return 0, 0

        task_files = sorted(self.tasks_dir.glob("T-*.md"))
        imported = 0
        errors = 0

        print(f"🔧 Importing {len(task_files)} tasks...")

        for task_file in task_files:
            try:
                content = task_file.read_text()
                metadata = self._extract_task_metadata(content, task_file.name)

                # Create issue body
                relative_path = f"planning/tasks/{task_file.name}"
                body = self._create_issue_body(content, "task", relative_path)

                print(f"  Creating issue for {task_file.name}: {metadata['title']}")

                # Create GitHub issue
                issue_number = self._create_github_issue(
                    metadata["title"], body, metadata["labels"]
                )

                if issue_number:
                    print(f"    ✅ Created issue #{issue_number}")

                    # Add delay before adding to project
                    time.sleep(1)

                    # Add to project
                    if self._add_issue_to_project(issue_number):
                        print(f"    ✅ Added to project")
                        imported += 1
                    else:
                        print(f"    ⚠️  Issue created but failed to add to project")
                        errors += 1
                else:
                    print(f"    ❌ Failed to create issue")
                    errors += 1

            except Exception as e:
                print(f"    ❌ Error processing {task_file.name}: {e}")
                errors += 1

        return imported, errors

    def run_import(self):
        """Run the complete import process."""
        print(f"🚀 Importing planning files to GitHub")
        print(f"   Repository: {self.repo_name}")
        print(f"   Project: #{self.project_number}")
        print(f"   Dry run: {self.dry_run}")
        print()

        # Import stories
        story_imported, story_errors = self.import_stories()

        # Import tasks
        task_imported, task_errors = self.import_tasks()

        # Summary
        total_imported = story_imported + task_imported
        total_errors = story_errors + task_errors

        print()
        print("📊 Import Summary:")
        print(f"   Stories imported: {story_imported}")
        print(f"   Tasks imported: {task_imported}")
        print(f"   Total imported: {total_imported}")
        print(f"   Errors: {total_errors}")

        if total_imported > 0:
            print(f"🎉 Successfully imported {total_imported} planning items to GitHub!")
            print(
                f"   View your project: https://github.com/{self.repo_name}/projects/{self.project_number}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Import planning files to GitHub issues and project"
    )
    parser.add_argument("repo", help="Repository name (owner/repo)")
    parser.add_argument(
        "--project-number", type=int, required=True, help="GitHub Project number"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--stories-only", action="store_true", help="Import only user stories"
    )
    parser.add_argument("--tasks-only", action="store_true", help="Import only tasks")

    args = parser.parse_args()

    importer = PlanningImporter(args.repo, args.project_number, args.dry_run)

    if args.stories_only:
        story_imported, story_errors = importer.import_stories()
        print(f"Imported {story_imported} stories with {story_errors} errors")
    elif args.tasks_only:
        task_imported, task_errors = importer.import_tasks()
        print(f"Imported {task_imported} tasks with {task_errors} errors")
    else:
        importer.run_import()


if __name__ == "__main__":
    main()

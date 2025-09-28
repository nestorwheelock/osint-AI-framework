#!/usr/bin/env python3
"""
Pre-commit hook to sync GitHub Project status back to planning files.
Ensures documentation stays in sync with GitHub Project state before commits.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class GitHubProjectToFilesSync:
    """Sync GitHub Project status back to planning files before commits."""

    def __init__(self, repo_name: str, project_number: int, dry_run: bool = False):
        self.repo_name = repo_name
        self.project_number = project_number
        self.dry_run = dry_run
        self.project_root = Path.cwd()
        self.stories_dir = self.project_root / "planning" / "stories"
        self.tasks_dir = self.project_root / "planning" / "tasks"

        # GitHub Project status mapping to file status
        self.status_mapping = {
            "Todo": "todo",
            "In Progress": "in_progress",
            "Done": "completed",
            "Backlog": "backlog",
            "Ready": "ready",
            "Review": "review",
        }

    def _run_gh_command(self, cmd_args: List[str]) -> Optional[str]:
        """Run GitHub CLI command with authentication handling."""
        if self.dry_run:
            print(f"[DRY RUN] Would run: gh {' '.join(cmd_args)}")
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
            print(f"   Command: gh {' '.join(cmd_args)}")
            print(f"   Error: {e.stderr}")
            return None

    def _get_project_items_with_status(self) -> List[Dict]:
        """Get all project items with their current status from GitHub."""
        print("🔄 Fetching GitHub Project status...")

        # Get project items with status using GraphQL
        query = """
        query($owner: String!, $number: Int!) {
          user(login: $owner) {
            projectV2(number: $number) {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      number
                      title
                      state
                    }
                  }
                  fieldValues(first: 20) {
                    nodes {
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field {
                          ... on ProjectV2SingleSelectField {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldTextValue {
                        text
                        field {
                          ... on ProjectV2Field {
                            name
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        variables = {
            "owner": self.repo_name.split("/")[0],
            "number": self.project_number,
        }

        cmd = [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            f'owner={variables["owner"]}',
            "-F",
            f'number={variables["number"]}',
        ]

        result = self._run_gh_command(cmd)
        if not result:
            return []

        try:
            data = json.loads(result)
            items = data["data"]["user"]["projectV2"]["items"]["nodes"]

            processed_items = []
            for item in items:
                if not item.get("content"):
                    continue

                content = item["content"]
                issue_data = {
                    "issue_number": content.get("number"),
                    "title": content.get("title", ""),
                    "state": content.get("state", "open"),
                    "status": "todo",  # default
                }

                # Extract status from field values
                for field_value in item.get("fieldValues", {}).get("nodes", []):
                    field_name = field_value.get("field", {}).get("name", "")

                    if field_name.lower() == "status":
                        github_status = field_value.get("name", "Todo")
                        issue_data["status"] = self.status_mapping.get(
                            github_status, "todo"
                        )
                        break

                processed_items.append(issue_data)

            return processed_items

        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Error parsing GitHub Project data: {e}")
            return []

    def _extract_story_number(self, title: str) -> Optional[str]:
        """Extract story/task number from title (S-001, T-001, etc)."""
        match = re.match(r"([ST]-\d+)", title)
        return match.group(1) if match else None

    def _find_planning_file(self, item_id: str) -> Optional[Path]:
        """Find the corresponding planning file for a story/task ID."""
        if item_id.startswith("S-"):
            # Look for files matching the pattern S-001-*
            pattern = f"{item_id}-*.md"
            matches = list(self.stories_dir.glob(pattern))
            return matches[0] if matches else None
        elif item_id.startswith("T-"):
            # Look for files matching the pattern T-001-*
            pattern = f"{item_id}-*.md"
            matches = list(self.tasks_dir.glob(pattern))
            return matches[0] if matches else None
        return None

    def _update_file_status(self, file_path: Path, new_status: str) -> bool:
        """Update status in planning file YAML frontmatter."""
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return False

        try:
            content = file_path.read_text()

            # Check if file has YAML frontmatter
            if content.strip().startswith("```yaml"):
                lines = content.split("\n")
                yaml_end = -1

                # Find end of YAML block
                for i, line in enumerate(lines[1:], 1):
                    if line.strip() == "```":
                        yaml_end = i
                        break

                if yaml_end > 0:
                    # Parse existing YAML
                    yaml_content = "\n".join(lines[1:yaml_end])
                    try:
                        metadata = yaml.safe_load(yaml_content) or {}
                    except yaml.YAMLError:
                        metadata = {}

                    # Update status
                    metadata["status"] = new_status
                    metadata["last_synced"] = self._get_current_timestamp()

                    # Reconstruct file
                    new_yaml = yaml.dump(metadata, default_flow_style=False)
                    remaining_content = "\n".join(lines[yaml_end + 1 :])
                    new_content = f"```yaml\n{new_yaml}```\n{remaining_content}"

                    if not self.dry_run:
                        file_path.write_text(new_content)

                    return True
            else:
                # Add YAML frontmatter if it doesn't exist
                metadata = {
                    "status": new_status,
                    "last_synced": self._get_current_timestamp(),
                }

                yaml_str = yaml.dump(metadata, default_flow_style=False)
                new_content = f"```yaml\n{yaml_str}```\n\n{content}"

                if not self.dry_run:
                    file_path.write_text(new_content)

                return True

        except Exception as e:
            print(f"❌ Error updating {file_path}: {e}")
            return False

        return False

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()

    def sync_status_to_files(self) -> Tuple[int, int]:
        """Sync GitHub Project status back to planning files."""
        print("🔄 Syncing GitHub Project status to planning files...")

        # Get project items with status
        project_items = self._get_project_items_with_status()
        if not project_items:
            print("❌ No project items found or error fetching data")
            return 0, 0

        updated = 0
        errors = 0

        for item in project_items:
            title = item.get("title", "")
            status = item.get("status", "todo")

            # Extract story/task ID from title
            item_id = self._extract_story_number(title)
            if not item_id:
                continue

            # Find corresponding planning file
            file_path = self._find_planning_file(item_id)
            if not file_path:
                continue

            print(f"  📝 Updating {item_id}: {status}")

            if self._update_file_status(file_path, status):
                updated += 1
            else:
                errors += 1

        return updated, errors

    def run_sync(self):
        """Run the complete sync process."""
        print(f"🔄 GitHub Project → Files Sync")
        print(f"   Repository: {self.repo_name}")
        print(f"   Project: #{self.project_number}")
        print(f"   Dry run: {self.dry_run}")
        print()

        updated, errors = self.sync_status_to_files()

        print()
        print("📊 Sync Summary:")
        print(f"   Files updated: {updated}")
        print(f"   Errors: {errors}")

        if errors > 0:
            print("⚠️  Some files could not be updated")
            return 1

        if updated > 0:
            print("✅ Planning files synced with GitHub Project status")
        else:
            print("ℹ️  No updates needed - files already in sync")

        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Sync GitHub Project status to planning files"
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

    args = parser.parse_args()

    syncer = GitHubProjectToFilesSync(args.repo, args.project_number, args.dry_run)
    exit_code = syncer.run_sync()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

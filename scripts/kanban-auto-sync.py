#!/usr/bin/env python3
"""
Automated Kanban Board Synchronization

Automatically syncs GitHub Project kanban board status when tasks are completed,
tested, committed, and pushed. Integrates with the incremental commit workflow
to ensure project status always reflects actual development progress.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def run_gh_command(cmd_args: List[str]) -> str:
    """Run GitHub CLI command and return output."""
    try:
        env = os.environ.copy()
        env.pop("GH_TOKEN", None)  # Use keyring authentication
        result = subprocess.run(
            ["gh"] + cmd_args, capture_output=True, text=True, check=True, env=env
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: GitHub CLI command failed: {e}")
        print(f"   Error: {e.stderr}")
        raise


class KanbanAutoSync:
    """Automated kanban board synchronization."""

    def __init__(self, project_id: str = "PVT_kwHOAfm3mM4BEQpc"):
        self.project_id = project_id
        self.status_field_id = "PVTSSF_lAHOAfm3mM4BEQpczg17_m0"

        # Status mapping based on enhanced kanban system
        self.status_options = {
            "Backlog": "f75ad846",  # Product backlog
            "Todo": "47fc9ee4",  # Epoch planning
            "In Progress": "98236657",  # Active sprint
            "Done": "8d28c7d0",  # Completed
        }

        # Task status mapping based on our todo system
        self.todo_to_kanban_mapping = {
            "pending": "Backlog",  # Not started yet
            "in_progress": "In Progress",  # Currently working
            "completed": "Done",  # Finished and tested
        }

    def get_project_items(self) -> Dict:
        """Get all items from the GitHub Project."""
        query = f"""
        query {{
          node(id: "{self.project_id}") {{
            ... on ProjectV2 {{
              title
              items(first: 100) {{
                nodes {{
                  id
                  content {{
                    ... on Issue {{
                      number
                      title
                      body
                    }}
                  }}
                  fieldValues(first: 10) {{
                    nodes {{
                      ... on ProjectV2ItemFieldSingleSelectValue {{
                        name
                        field {{
                          ... on ProjectV2SingleSelectField {{
                            name
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """

        result = run_gh_command(["api", "graphql", "-f", f"query={query}"])
        return json.loads(result)

    def find_issue_by_title_pattern(
        self, pattern: str, items: List[Dict]
    ) -> Optional[Dict]:
        """Find a GitHub issue by title pattern."""
        for item in items:
            if not item.get("content"):
                continue

            title = item["content"]["title"]
            if pattern.lower() in title.lower():
                return item

        return None

    def get_current_status(self, item: Dict) -> str:
        """Get current kanban status of an item."""
        field_values = item.get("fieldValues", {}).get("nodes", [])
        for field_value in field_values:
            field_name = field_value.get("field", {}).get("name", "")
            if field_name == "Status":
                return field_value.get("name", "Backlog")
        return "Backlog"

    def update_item_status(self, item_id: str, new_status: str, title: str) -> bool:
        """Update an item's status in the kanban board."""
        if new_status not in self.status_options:
            print(
                f"ERROR: Invalid status '{new_status}'. Valid options: {list(self.status_options.keys())}"
            )
            return False

        print(f"SYNC: Moving '{title}' to {new_status}")

        mutation = f"""
        mutation {{
          updateProjectV2ItemFieldValue(
            input: {{
              projectId: "{self.project_id}"
              itemId: "{item_id}"
              fieldId: "{self.status_field_id}"
              value: {{
                singleSelectOptionId: "{self.status_options[new_status]}"
              }}
            }}
          ) {{
            projectV2Item {{
              id
            }}
          }}
        }}
        """

        try:
            run_gh_command(["api", "graphql", "-f", f"query={mutation}"])
            print(f"SUCCESS: Moved '{title}' to {new_status}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to move '{title}': {e}")
            return False

    def sync_todo_list_to_kanban(self, todos: List[Dict]) -> Dict:
        """Sync todo list status to kanban board."""
        print("KANBAN AUTO-SYNC: Starting synchronization...")

        # Get current project items
        project_data = self.get_project_items()
        items = project_data["data"]["node"]["items"]["nodes"]

        sync_results = {"updated": [], "not_found": [], "errors": [], "no_change": []}

        # Define todo patterns to search for in GitHub issues
        todo_patterns = {
            "Create GitHub milestone for Sprint 1 completion": "milestone",
            "Document Sprint 1 completion with all deliverables": "sprint-1-completion",
            "Create milestone automation algorithm with tests": "milestone-automation",
            "Analyze template extraction potential": "template-extraction",
            "Update whitepapers and PDFs to reflect Sprint 1": "whitepaper",
            "Implement checkbox acceptance testing system": "acceptance-testing",
            "Create comprehensive development logging system": "development-logging",
            "Setup React frontend foundation": "react-frontend",
            "Document client billing and mobile strategy": "billing-methodology",
            "Plan flexible next sprint composition": "sprint-planning",
            "Enhance kanban with backlog support": "enhanced-kanban",
            "Create Django search app foundation": "search-app",
            "Document incremental commit workflow": "commit-workflow",
            "Implement URL canonicalization utilities": "url-canonicalization",
            "Build search engine adapter pattern": "search-adapter",
            "Create meta-search orchestration service": "meta-search",
        }

        for todo in todos:
            todo_content = todo["content"]
            todo_status = todo["status"]

            # Find corresponding pattern
            pattern = None
            for todo_pattern, search_pattern in todo_patterns.items():
                if todo_pattern.lower() in todo_content.lower():
                    pattern = search_pattern
                    break

            if not pattern:
                # Try to match by story/task numbers
                if "S-" in todo_content or "T-" in todo_content:
                    pattern = (
                        todo_content.split("—")[0].strip()
                        if "—" in todo_content
                        else todo_content[:20]
                    )
                else:
                    sync_results["not_found"].append(todo_content)
                    continue

            # Find the GitHub issue
            item = self.find_issue_by_title_pattern(pattern, items)
            if not item:
                sync_results["not_found"].append(f"{todo_content} (pattern: {pattern})")
                continue

            # Map todo status to kanban status
            kanban_status = self.todo_to_kanban_mapping.get(todo_status, "Backlog")
            current_status = self.get_current_status(item)

            # Only update if status has changed
            if current_status != kanban_status:
                success = self.update_item_status(
                    item["id"], kanban_status, item["content"]["title"]
                )

                if success:
                    sync_results["updated"].append(
                        {
                            "title": item["content"]["title"],
                            "from": current_status,
                            "to": kanban_status,
                        }
                    )
                else:
                    sync_results["errors"].append(item["content"]["title"])
            else:
                sync_results["no_change"].append(item["content"]["title"])

        return sync_results

    def sync_completed_tasks(self, completed_tasks: List[str]) -> Dict:
        """Sync specific completed tasks to Done status."""
        print("KANBAN AUTO-SYNC: Syncing completed tasks...")

        project_data = self.get_project_items()
        items = project_data["data"]["node"]["items"]["nodes"]

        sync_results = {"updated": [], "not_found": [], "errors": []}

        for task in completed_tasks:
            # Find the GitHub issue by title pattern
            item = self.find_issue_by_title_pattern(task, items)
            if not item:
                sync_results["not_found"].append(task)
                continue

            current_status = self.get_current_status(item)

            # Move to Done if not already there
            if current_status != "Done":
                success = self.update_item_status(
                    item["id"], "Done", item["content"]["title"]
                )

                if success:
                    sync_results["updated"].append(
                        {
                            "title": item["content"]["title"],
                            "from": current_status,
                            "to": "Done",
                        }
                    )
                else:
                    sync_results["errors"].append(item["content"]["title"])

        return sync_results


def sync_kanban_from_todos(todos: List[Dict]) -> Dict:
    """Sync kanban board from todo list - main entry point."""
    kanban = KanbanAutoSync()
    return kanban.sync_todo_list_to_kanban(todos)


def sync_completed_tasks(tasks: List[str]) -> Dict:
    """Sync completed tasks to kanban board."""
    kanban = KanbanAutoSync()
    return kanban.sync_completed_tasks(tasks)


def main():
    """CLI interface for kanban auto-sync."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated Kanban Board Synchronization"
    )
    parser.add_argument(
        "--sync-todos", action="store_true", help="Sync from current todo list"
    )
    parser.add_argument(
        "--completed-tasks",
        nargs="+",
        metavar="TASK",
        help="Mark specific tasks as completed",
    )
    parser.add_argument(
        "--test-connection", action="store_true", help="Test GitHub API connection"
    )

    args = parser.parse_args()

    kanban = KanbanAutoSync()

    if args.test_connection:
        try:
            project_data = kanban.get_project_items()
            project_title = project_data["data"]["node"]["title"]
            item_count = len(project_data["data"]["node"]["items"]["nodes"])
            print(
                f"SUCCESS: Connected to project '{project_title}' with {item_count} items"
            )
        except Exception as e:
            print(f"ERROR: Failed to connect to GitHub Project: {e}")

    elif args.sync_todos:
        # Would need to load current todo list - this is a placeholder
        print("INFO: Todo list sync requires integration with TodoWrite system")

    elif args.completed_tasks:
        results = kanban.sync_completed_tasks(args.completed_tasks)

        print(f"\nKANBAN SYNC RESULTS:")
        if results["updated"]:
            print(f"  Updated: {len(results['updated'])} items")
            for item in results["updated"]:
                print(f"    - {item['title']}: {item['from']} → {item['to']}")

        if results["not_found"]:
            print(f"  Not Found: {len(results['not_found'])} items")
            for item in results["not_found"]:
                print(f"    - {item}")

        if results["errors"]:
            print(f"  Errors: {len(results['errors'])} items")
            for item in results["errors"]:
                print(f"    - {item}")

    else:
        print("Automated Kanban Board Synchronization")
        print("Usage:")
        print("  --test-connection")
        print("  --completed-tasks 'task1' 'task2'")
        print("  --sync-todos")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Enhanced Kanban System with Backlog Support

Implements a 4-column kanban system that maps to our development methodology:
- Backlog: Product backlog (all discovered features, dependencies, future work)
- Todo: Epoch planning (locked-in stories for current budget cycle)
- In Progress: Active sprint work (current sprint execution)
- Done: Completed deliverables

This system integrates with GitHub Projects to provide proper workflow management.
"""

import json
import os
import subprocess
import sys
from typing import Dict, List, Optional
from datetime import datetime


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
        print(f" Command failed: {e}")
        print(f"   Error: {e.stderr}")
        raise


class EnhancedKanbanSystem:
    """Enhanced kanban system with proper workflow mapping."""

    def __init__(self, project_id: str = "PVT_kwHOAfm3mM4BEQpc"):
        self.project_id = project_id
        self.status_field_id = "PVTSSF_lAHOAfm3mM4BEQpczg17_m0"

        # Enhanced status mapping
        self.status_options = {
            "Backlog": "f75ad846",  # Product backlog
            "Todo": "47fc9ee4",  # Epoch planning
            "In Progress": "98236657",  # Active sprint
            "Done": "8d28c7d0",  # Completed
        }

    def get_project_structure(self) -> Dict:
        """Get current project structure and field information."""
        query = f"""
        query {{
          node(id: "{self.project_id}") {{
            ... on ProjectV2 {{
              title
              fields(first: 20) {{
                nodes {{
                  ... on ProjectV2SingleSelectField {{
                    id
                    name
                    options {{
                      id
                      name
                    }}
                  }}
                }}
              }}
              items(first: 100) {{
                nodes {{
                  id
                  content {{
                    ... on Issue {{
                      number
                      title
                      body
                      labels(first: 10) {{
                        nodes {{
                          name
                        }}
                      }}
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

    def categorize_items_by_type(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize items by type for proper backlog management."""
        categories = {
            "stories": [],  # S-XXX items
            "tasks": [],  # T-XXX items
            "epics": [],  # Epic-level items
            "dependencies": [],  # Infrastructure/dependency items
            "enhancements": [],  # Feature enhancements
            "bugs": [],  # Bug fixes
        }

        for item in items:
            if not item.get("content"):
                continue

            title = item["content"]["title"]
            labels = [
                label["name"]
                for label in item["content"].get("labels", {}).get("nodes", [])
            ]

            # Categorize by title patterns and labels
            if title.startswith("S-"):
                categories["stories"].append(item)
            elif title.startswith("T-"):
                categories["tasks"].append(item)
            elif "epic" in labels or "Epic" in title:
                categories["epics"].append(item)
            elif any(label in labels for label in ["bug", "fix", "hotfix"]):
                categories["bugs"].append(item)
            elif any(
                label in labels for label in ["enhancement", "feature", "improvement"]
            ):
                categories["enhancements"].append(item)
            elif any(
                keyword in title.lower()
                for keyword in ["dependency", "dependencies", "infrastructure", "setup"]
            ):
                categories["dependencies"].append(item)
            else:
                categories["enhancements"].append(item)  # Default category

        return categories

    def suggest_backlog_organization(self, categories: Dict[str, List[Dict]]) -> Dict:
        """Suggest optimal backlog organization based on current items."""
        suggestions = {
            "immediate_backlog": [],  # Ready for next epoch
            "future_backlog": [],  # Future planning
            "dependencies": [],  # Must be completed first
            "current_epoch": [],  # Current budget cycle items
            "completed": [],  # Done items
        }

        # Analyze current status and suggest organization
        for category, items in categories.items():
            for item in items:
                current_status = self.get_item_status(item)

                if current_status == "Done":
                    suggestions["completed"].append(item)
                elif current_status == "In Progress":
                    suggestions["current_epoch"].append(item)
                elif current_status == "Todo":
                    suggestions["current_epoch"].append(item)
                elif category == "dependencies":
                    suggestions["dependencies"].append(item)
                elif category in ["stories", "epics"]:
                    suggestions["immediate_backlog"].append(item)
                else:
                    suggestions["future_backlog"].append(item)

        return suggestions

    def get_item_status(self, item: Dict) -> str:
        """Get current status of an item."""
        field_values = item.get("fieldValues", {}).get("nodes", [])
        for field_value in field_values:
            field_name = field_value.get("field", {}).get("name", "")
            if field_name == "Status":
                return field_value.get("name", "Backlog")
        return "Backlog"

    def create_backlog_view(self) -> str:
        """Create a comprehensive backlog view report."""
        print(" Analyzing project structure...")

        # Get project data
        project_data = self.get_project_structure()
        items = project_data["data"]["node"]["items"]["nodes"]

        # Categorize items
        categories = self.categorize_items_by_type(items)
        suggestions = self.suggest_backlog_organization(categories)

        # Generate report
        report = f"""# Enhanced Kanban Backlog Analysis

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Project**: {project_data['data']['node']['title']}

## Kanban Column Mapping

###  Workflow Philosophy
- **Backlog**: Product backlog → All discovered features, dependencies, future work
- **Todo**: Epoch planning → Locked-in stories for current budget cycle
- **In Progress**: Active sprint → Current sprint execution
- **Done**: Completed deliverables → Finished work

## Current Backlog Organization

###  Product Backlog (Ready for Planning)
"""

        # Add immediate backlog items
        if suggestions["immediate_backlog"]:
            report += "**Immediate Backlog** (Ready for next epoch):\n"
            for item in suggestions["immediate_backlog"]:
                title = item["content"]["title"]
                report += f"- {title}\n"
            report += "\n"

        # Add dependencies
        if suggestions["dependencies"]:
            report += "**Dependencies** (Must complete first):\n"
            for item in suggestions["dependencies"]:
                title = item["content"]["title"]
                report += f"- {title}\n"
            report += "\n"

        # Add future backlog
        if suggestions["future_backlog"]:
            report += "**Future Backlog** (Later planning):\n"
            for item in suggestions["future_backlog"]:
                title = item["content"]["title"]
                report += f"- {title}\n"
            report += "\n"

        # Current epoch status
        report += "###  Current Epoch Status\n"
        if suggestions["current_epoch"]:
            report += "**Active Items** (Todo + In Progress):\n"
            for item in suggestions["current_epoch"]:
                title = item["content"]["title"]
                status = self.get_item_status(item)
                report += f"- [{status}] {title}\n"
        else:
            report += "No active epoch items\n"

        report += "\n"

        # Statistics
        report += "##  Backlog Statistics\n\n"
        total_items = len(items)
        report += f"**Total Items**: {total_items}\n"

        for category, items_list in categories.items():
            report += f"**{category.title()}**: {len(items_list)} items\n"

        report += f"\n**Status Distribution**:\n"
        for status, items_list in suggestions.items():
            report += f"- {status.replace('_', ' ').title()}: {len(items_list)} items\n"

        # Recommendations
        report += "\n##  Recommendations\n\n"

        if suggestions["dependencies"]:
            report += (
                "**Priority**: Complete dependency items before starting new epocs\n"
            )

        if len(suggestions["immediate_backlog"]) > 10:
            report += "**Planning**: Large backlog - consider epic consolidation\n"

        if len(suggestions["current_epoch"]) > 15:
            report += "**Sprint Focus**: Current epoch may be overloaded - consider splitting\n"

        report += f"\n**Suggested Next Epoch**: Select {min(5, len(suggestions['immediate_backlog']))} items from immediate backlog\n"

        return report

    def move_item_to_backlog(self, item_id: str, issue_title: str) -> bool:
        """Move an item to backlog status."""
        print(f" Moving '{issue_title}' to backlog...")

        mutation = f"""
        mutation {{
          updateProjectV2ItemFieldValue(
            input: {{
              projectId: "{self.project_id}"
              itemId: "{item_id}"
              fieldId: "{self.status_field_id}"
              value: {{
                singleSelectOptionId: "{self.status_options['Backlog']}"
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
            print(f"    Moved to backlog")
            return True
        except Exception as e:
            print(f"    Failed: {e}")
            return False

    def organize_backlog_by_priority(self, dry_run: bool = True) -> Dict:
        """Organize backlog items by priority and dependencies."""
        print(" Organizing backlog by priority...")

        project_data = self.get_project_structure()
        items = project_data["data"]["node"]["items"]["nodes"]

        # Identify items that should be in backlog
        backlog_candidates = []

        for item in items:
            if not item.get("content"):
                continue

            current_status = self.get_item_status(item)
            title = item["content"]["title"]

            # Items that should be in backlog
            if current_status not in ["In Progress", "Done"] and not any(
                keyword in title.lower() for keyword in ["current", "active", "sprint"]
            ):
                backlog_candidates.append(item)

        # Organize by priority
        organization_plan = {
            "high_priority": [],
            "medium_priority": [],
            "low_priority": [],
            "dependencies": [],
            "actions_taken": [],
        }

        for item in backlog_candidates:
            title = item["content"]["title"]

            # Priority classification
            if any(
                keyword in title.lower()
                for keyword in ["critical", "urgent", "dependency", "infrastructure"]
            ):
                organization_plan["dependencies"].append(item)
            elif title.startswith("S-") or "Epic" in title:
                organization_plan["high_priority"].append(item)
            elif title.startswith("T-"):
                organization_plan["medium_priority"].append(item)
            else:
                organization_plan["low_priority"].append(item)

        # Execute moves if not dry run
        if not dry_run:
            for category, items_list in organization_plan.items():
                if category == "actions_taken":
                    continue

                for item in items_list:
                    if self.get_item_status(item) != "Backlog":
                        success = self.move_item_to_backlog(
                            item["id"], item["content"]["title"]
                        )
                        if success:
                            organization_plan["actions_taken"].append(
                                item["content"]["title"]
                            )

        return organization_plan


def main():
    """CLI interface for enhanced kanban system."""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Kanban System with Backlog")
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze current backlog organization"
    )
    parser.add_argument(
        "--organize", action="store_true", help="Organize backlog by priority"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show organization plan without making changes",
    )

    args = parser.parse_args()

    kanban = EnhancedKanbanSystem()

    if args.analyze:
        report = kanban.create_backlog_view()
        print(report)

        # Save report
        with open("logs/backlog-analysis.md", "w") as f:
            f.write(report)
        print(f"\n Report saved to logs/backlog-analysis.md")

    elif args.organize:
        dry_run = args.dry_run
        plan = kanban.organize_backlog_by_priority(dry_run=dry_run)

        print(f"\n Backlog Organization Plan:")
        for category, items in plan.items():
            if items and category != "actions_taken":
                print(f"\n**{category.replace('_', ' ').title()}**:")
                for item in items:
                    print(f"  - {item['content']['title']}")

        if not dry_run and plan["actions_taken"]:
            print(f"\n Moved {len(plan['actions_taken'])} items to backlog")
        elif dry_run:
            print(f"\n Use --organize without --dry-run to execute moves")

    else:
        print("Enhanced Kanban System")
        print("Usage: --analyze | --organize [--dry-run]")


if __name__ == "__main__":
    main()

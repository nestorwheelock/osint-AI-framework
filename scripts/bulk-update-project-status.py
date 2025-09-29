#!/usr/bin/env python3
"""
Bulk update GitHub Project with proper parent/child relationships and statuses.
Sets up Stories as parents with Tasks as sub-issues.
"""

import json
import os
import subprocess
import sys
from typing import Dict, List, Optional

# Project field IDs from the API response
PROJECT_ID = "PVT_kwHOAfm3mM4BEQpc"
STATUS_FIELD_ID = "PVTSSF_lAHOAfm3mM4BEQpczg17_m0"
PARENT_ISSUE_FIELD_ID = "PVTF_lAHOAfm3mM4BEQpczg17_nM"

# Status option IDs
STATUS_OPTIONS = {"Todo": "f75ad846", "In Progress": "47fc9ee4", "Done": "98236657"}

# Parent/child relationships - Stories → Tasks
PARENT_CHILD_RELATIONSHIPS = {
    # S-000 → T-000
    "T-000: Pre-Epoch Environment Design & Infrastructure Setup": "S-000: Pre-Epoch Environment Design & Infrastructure Setup",
    # S-001 → T-001
    "T-001 — Tasks for S-001: Create Subject": "S-001 — Create Subject",
    # S-002 → T-002 (note: S-002 might be missing from project)
    "T-002 — Tasks for S-002: Start Investigation Session": "S-002",
    # S-003 → T-003
    "T-003 — Tasks for S-003: Meta-Search Implementation": "S-003 — Meta-Search Implementation",
    # S-004 → T-004 (note: S-004 might be missing from project)
    "T-004 — Tasks for S-004: Playwright Web Scraping": "S-004",
    # S-005 → T-005
    "T-005 — Tasks for S-005: Text Extraction & Language Detection": "S-005 — Text Extraction & Language Detection",
    # S-006 → T-006
    "T-006 — Tasks for S-006: AI Entity Extraction": "S-006 — AI Entity Extraction",
    # S-007 → T-007 (note: S-007 might be missing from project)
    "T-007 — Tasks for S-007: Labeling & Filtering System": "S-007",
    # S-008 → T-008 (note: S-008 might be missing from project)
    "T-008 — Tasks for S-008: Export Functionality": "S-008",
    # S-009 → T-009 (note: S-009 might be missing from project)
    "T-009 — Tasks for S-009: Configuration Management": "S-009",
    # S-010 → T-010 (note: S-010 might be missing from project)
    "T-010 — Tasks for S-010: Ethical Scraping Controls": "S-010",
    # S-011 → T-011 (note: S-011 might be missing from project)
    "T-011 — Tasks for S-011: Timeline Assembly": "S-011",
    # S-012 → T-012 (note: S-012 might be missing from project)
    "T-012 — Tasks for S-012: Duplicate Detection": "S-012",
    # S-013 → T-013 (note: S-013 might be missing from project)
    "T-013 — Tasks for S-013: PDF Report Generation": "S-013",
    # S-014 → T-014 (note: S-014 might be missing from project)
    "T-014 — Tasks for S-014: Job Monitoring": "S-014",
    # S-015 → T-015
    "T-015: Final Integration & Production Deployment": "S-015: Final Integration & Production Deployment",
}

# Status assignments based on actual progress
STATUS_UPDATES = {
    # IN PROGRESS WORK
    # S-000 and T-000 - Environment setup in progress (basic dev environment exists, but full infrastructure not complete)
    "S-000: Pre-Epoch Environment Design & Infrastructure Setup": "In Progress",
    "T-000: Pre-Epoch Environment Design & Infrastructure Setup": "In Progress",
    # COMPLETED WORK
    # S-001 and T-001 - Subject CRUD is complete (779 lines of production Django code implemented)
    "S-001 — Create Subject": "Done",
    "T-001 — Tasks for S-001: Create Subject": "Done",
    # COMPLETED WORK
    # S-002 Start Session - COMPLETE! Session model + API implemented with TDD, all tests passing
    "S-002 — Start Investigation Session": "Done",
    "T-002 — Tasks for S-002: Start Investigation Session": "Done",
    # TODO ITEMS (not started yet)
    # All other stories
    "S-003 — Meta-Search Implementation": "Todo",
    "S-005 — Text Extraction & Language Detection": "Todo",
    "S-006 — AI Entity Extraction": "Todo",
    "S-015: Final Integration & Production Deployment": "Todo",
    # All other tasks
    "T-003 — Tasks for S-003: Meta-Search Implementation": "Todo",
    "T-004 — Tasks for S-004: Playwright Web Scraping": "Todo",
    "T-005 — Tasks for S-005: Text Extraction & Language Detection": "Todo",
    "T-006 — Tasks for S-006: AI Entity Extraction": "Todo",
    "T-007 — Tasks for S-007: Labeling & Filtering System": "Todo",
    "T-008 — Tasks for S-008: Export Functionality": "Todo",
    "T-009 — Tasks for S-009: Configuration Management": "Todo",
    "T-010 — Tasks for S-010: Ethical Scraping Controls": "Todo",
    "T-011 — Tasks for S-011: Timeline Assembly": "Todo",
    "T-012 — Tasks for S-012: Duplicate Detection": "Todo",
    "T-013 — Tasks for S-013: PDF Report Generation": "Todo",
    "T-014 — Tasks for S-014: Job Monitoring": "Todo",
    "T-015: Final Integration & Production Deployment": "Todo",
}


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


def update_item_status(item_id: str, status: str, title: str):
    """Update a single project item's status."""
    status_option_id = STATUS_OPTIONS[status]

    mutation = f"""
    mutation {{
      updateProjectV2ItemFieldValue(
        input: {{
          projectId: "{PROJECT_ID}"
          itemId: "{item_id}"
          fieldId: "{STATUS_FIELD_ID}"
          value: {{
            singleSelectOptionId: "{status_option_id}"
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
        print(f" Updated {title} → {status}")
        return True
    except Exception as e:
        print(f" Failed to update {title}: {e}")
        return False


def get_issue_node_id(item_id: str) -> Optional[str]:
    """Get the Issue node ID from a project item."""
    query = f"""
    query {{
      node(id: "{item_id}") {{
        ... on ProjectV2Item {{
          content {{
            ... on Issue {{
              id
            }}
          }}
        }}
      }}
    }}
    """

    try:
        result = run_gh_command(["api", "graphql", "-f", f"query={query}"])
        data = json.loads(result)
        return data["data"]["node"]["content"]["id"]
    except Exception as e:
        print(f" Failed to get issue ID for {item_id}: {e}")
        return None


def set_parent_relationship(
    child_item_id: str, parent_item_id: str, child_title: str, parent_title: str
):
    """Set parent relationship for a task (child) to story (parent) using sub-issues."""
    # First, get the actual issue node IDs from the project items
    parent_issue_id = get_issue_node_id(parent_item_id)
    child_issue_id = get_issue_node_id(child_item_id)

    if not parent_issue_id or not child_issue_id:
        print(f" Could not get issue IDs for {child_title} → {parent_title}")
        return False

    mutation = f"""
    mutation {{
      addSubIssue(
        input: {{
          issueId: "{parent_issue_id}"
          subIssueId: "{child_issue_id}"
        }}
      ) {{
        issue {{
          title
        }}
        subIssue {{
          title
        }}
      }}
    }}
    """

    try:
        # Need to include GraphQL-Features header for sub-issues
        run_gh_command(
            [
                "api",
                "graphql",
                "-H",
                "GraphQL-Features: sub_issues",
                "-f",
                f"query={mutation}",
            ]
        )
        print(f" Linked {child_title} → {parent_title}")
        return True
    except Exception as e:
        print(f" Failed to link {child_title} to {parent_title}: {e}")
        return False


def get_project_items():
    """Get all project items."""
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
                }
              }
            }
          }
        }
      }
    }
    """

    result = run_gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            "owner=nestorwheelock",
            "-F",
            "number=5",
        ]
    )

    data = json.loads(result)
    return data["data"]["user"]["projectV2"]["items"]["nodes"]


def main():
    """Bulk update project statuses and parent/child relationships."""
    print(" Bulk updating GitHub Project statuses and relationships...")

    # Get all project items
    items = get_project_items()

    # Create title to item mapping for relationship setup
    title_to_item = {}
    for item in items:
        if item.get("content"):
            title_to_item[item["content"]["title"]] = item

    updated_count = 0
    skipped_count = 0
    linked_count = 0

    # Phase 1: Update statuses
    print("\n Phase 1: Updating statuses...")
    for item in items:
        if not item.get("content"):
            continue

        title = item["content"]["title"]
        item_id = item["id"]

        # Find matching status update
        target_status = None
        for pattern, status in STATUS_UPDATES.items():
            if pattern in title:
                target_status = status
                break

        if target_status:
            if update_item_status(item_id, target_status, title):
                updated_count += 1
            else:
                skipped_count += 1
        else:
            print(f"  No status rule for: {title}")
            skipped_count += 1

    # Phase 2: Set up parent/child relationships
    print("\n Phase 2: Setting up parent/child relationships...")
    for child_title, parent_title in PARENT_CHILD_RELATIONSHIPS.items():
        child_item = title_to_item.get(child_title)
        parent_item = title_to_item.get(parent_title)

        if child_item and parent_item:
            if set_parent_relationship(
                child_item["id"], parent_item["id"], child_title, parent_title
            ):
                linked_count += 1
        else:
            if not child_item:
                print(f"  Child not found: {child_title}")
            if not parent_item:
                print(f"  Parent not found: {parent_title}")

    print(f"\n Bulk update complete:")
    print(f"    Updated statuses: {updated_count} items")
    print(f"    Linked relationships: {linked_count} items")
    print(f"     Skipped: {skipped_count} items")

    # Show expected results
    print(f"\n Expected results:")
    print(f"   In Progress: S-000, T-000 (environment setup ongoing)")
    print(f"   Done: S-001, T-001 (subject CRUD completed)")
    print(f"   Todo: All other stories and tasks")
    print(f"   Hierarchy: Tasks linked as sub-issues to their parent Stories")
    print(f"   This should show clear progress with proper organization!")


if __name__ == "__main__":
    main()

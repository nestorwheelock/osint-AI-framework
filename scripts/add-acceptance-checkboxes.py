#!/usr/bin/env python3
"""
Add acceptance testing checkboxes to GitHub issues for human validation.

This script adds interactive checkboxes to completed GitHub issues that allow
humans to verify and accept AI-assisted work before final milestone closure.
"""

import json
import os
import subprocess
import sys
from typing import Dict, List, Optional
import re


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


def get_milestone_issues(milestone_number: int) -> List[Dict]:
    """Get all issues in a specific milestone."""
    print(f" Getting issues for milestone #{milestone_number}...")

    result = run_gh_command(
        [
            "api",
            "repos/:owner/:repo/issues",
            "--jq",
            f".[] | select(.milestone.number == {milestone_number})",
        ]
    )

    if not result:
        return []

    # Handle multiple JSON objects
    issues = []
    for line in result.split("\n"):
        if line.strip():
            issues.append(json.loads(line))

    return issues


def create_acceptance_checklist(issue_title: str, issue_body: str) -> str:
    """Create acceptance testing checklist based on issue content."""

    # Standard acceptance criteria for all issues
    standard_checks = [
        "[ ] Code review completed - no security vulnerabilities",
        "[ ] All tests pass - no failing test cases",
        "[ ] Documentation is accurate and complete",
        "[ ] No AI attribution found in code or commits",
        "[ ] Implementation matches requirements specification",
        "[ ] Error handling is appropriate and comprehensive",
    ]

    # Issue-specific checks based on content
    specific_checks = []

    # Django/Backend specific
    if any(
        keyword in issue_title.lower() or keyword in issue_body.lower()
        for keyword in ["django", "model", "api", "backend", "crud"]
    ):
        specific_checks.extend(
            [
                "[ ] Database migrations are properly structured",
                "[ ] API endpoints return correct HTTP status codes",
                "[ ] Data validation is working correctly",
                "[ ] Database operations are atomic and safe",
            ]
        )

    # Frontend specific
    if any(
        keyword in issue_title.lower() or keyword in issue_body.lower()
        for keyword in ["react", "frontend", "ui", "component"]
    ):
        specific_checks.extend(
            [
                "[ ] UI components render correctly across browsers",
                "[ ] Responsive design works on mobile and desktop",
                "[ ] Accessibility requirements are met",
                "[ ] User experience is intuitive and smooth",
            ]
        )

    # Testing specific
    if any(
        keyword in issue_title.lower() or keyword in issue_body.lower()
        for keyword in ["test", "testing", "coverage"]
    ):
        specific_checks.extend(
            [
                "[ ] Test coverage is adequate (>90% for critical paths)",
                "[ ] Edge cases are properly tested",
                "[ ] Test data is realistic and comprehensive",
                "[ ] Performance tests pass within acceptable limits",
            ]
        )

    # Create the full checklist
    checklist_content = f"""
##  Human Acceptance Testing

**Reviewer**: _[Add your name here]_
**Review Date**: _[Add review date]_

### Standard Quality Checks
{chr(10).join(standard_checks)}

### Implementation-Specific Checks
{chr(10).join(specific_checks) if specific_checks else "[ ] Implementation-specific requirements verified"}

### Final Acceptance
- [ ] **ACCEPTED**: This implementation meets all requirements and quality standards
- [ ] **REJECTED**: Issues found - see comments below for required changes

### Review Notes
_[Add any additional comments, suggestions, or required changes here]_

---
**Acceptance Status**: ⏳ PENDING HUMAN REVIEW
"""

    return checklist_content


def add_acceptance_checklist_to_issue(
    issue_number: int, issue_title: str, issue_body: str
) -> bool:
    """Add acceptance testing checklist to a GitHub issue."""

    # Check if issue already has acceptance checklist
    if "Human Acceptance Testing" in issue_body:
        print(f"   ℹ  Issue #{issue_number} already has acceptance checklist")
        return True

    # Create the acceptance checklist
    checklist = create_acceptance_checklist(issue_title, issue_body)

    # Append to existing issue body
    updated_body = issue_body + "\n" + checklist

    try:
        # Update the issue
        run_gh_command(
            [
                "api",
                f"repos/:owner/:repo/issues/{issue_number}",
                "-X",
                "PATCH",
                "-f",
                f"body={updated_body}",
            ]
        )

        print(f"    Added acceptance checklist to issue #{issue_number}")
        return True

    except Exception as e:
        print(f"    Failed to update issue #{issue_number}: {e}")
        return False


def process_milestone_for_acceptance(milestone_number: int) -> Dict:
    """Add acceptance checklists to all completed issues in a milestone."""
    print(f" Processing milestone #{milestone_number} for acceptance testing...")

    # Get milestone issues
    issues = get_milestone_issues(milestone_number)

    if not issues:
        print(f"     No issues found for milestone #{milestone_number}")
        return {"processed": 0, "updated": 0, "skipped": 0}

    results = {"processed": 0, "updated": 0, "skipped": 0}

    for issue in issues:
        issue_number = issue["number"]
        issue_title = issue["title"]
        issue_body = issue.get("body", "")
        issue_state = issue["state"]

        results["processed"] += 1

        print(f" Processing issue #{issue_number}: {issue_title}")

        # Only add acceptance testing to closed issues (completed work)
        if issue_state != "closed":
            print(f"   ⏭  Skipping open issue #{issue_number}")
            results["skipped"] += 1
            continue

        # Add acceptance checklist
        if add_acceptance_checklist_to_issue(issue_number, issue_title, issue_body):
            results["updated"] += 1
        else:
            results["skipped"] += 1

    return results


def check_acceptance_status(milestone_number: int) -> Dict:
    """Check acceptance status of all issues in a milestone."""
    print(f" Checking acceptance status for milestone #{milestone_number}...")

    issues = get_milestone_issues(milestone_number)

    status = {
        "total_issues": len(issues),
        "accepted": 0,
        "rejected": 0,
        "pending": 0,
        "no_checklist": 0,
    }

    for issue in issues:
        issue_number = issue["number"]
        issue_body = issue.get("body", "")

        if "Human Acceptance Testing" not in issue_body:
            status["no_checklist"] += 1
            print(f"    Issue #{issue_number}: No acceptance checklist")
            continue

        # Check acceptance status
        if "- [x] **ACCEPTED**" in issue_body:
            status["accepted"] += 1
            print(f"    Issue #{issue_number}: ACCEPTED")
        elif "- [x] **REJECTED**" in issue_body:
            status["rejected"] += 1
            print(f"    Issue #{issue_number}: REJECTED")
        else:
            status["pending"] += 1
            print(f"   ⏳ Issue #{issue_number}: PENDING REVIEW")

    return status


def main():
    """Main CLI interface for acceptance testing management."""
    import argparse

    parser = argparse.ArgumentParser(
        description="GitHub Issue Acceptance Testing Manager"
    )
    parser.add_argument("milestone", type=int, help="Milestone number to process")
    parser.add_argument(
        "--add-checklists",
        action="store_true",
        help="Add acceptance checklists to milestone issues",
    )
    parser.add_argument(
        "--check-status",
        action="store_true",
        help="Check acceptance status of milestone issues",
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show detailed acceptance summary"
    )

    args = parser.parse_args()

    if args.add_checklists:
        results = process_milestone_for_acceptance(args.milestone)
        print(f"\n Acceptance Testing Setup Complete:")
        print(f"    Processed: {results['processed']} issues")
        print(f"    Updated: {results['updated']} issues")
        print(f"   ⏭  Skipped: {results['skipped']} issues")

    elif args.check_status or args.summary:
        status = check_acceptance_status(args.milestone)
        print(f"\n Milestone #{args.milestone} Acceptance Status:")
        print(f"    Total Issues: {status['total_issues']}")
        print(f"    Accepted: {status['accepted']}")
        print(f"    Rejected: {status['rejected']}")
        print(f"   ⏳ Pending Review: {status['pending']}")
        print(f"    No Checklist: {status['no_checklist']}")

        # Calculate completion percentage
        reviewed = status["accepted"] + status["rejected"]
        if status["total_issues"] > 0:
            completion_rate = (reviewed / status["total_issues"]) * 100
            acceptance_rate = (
                (status["accepted"] / reviewed * 100) if reviewed > 0 else 0
            )
            print(f"\n Metrics:")
            print(f"    Review Completion: {completion_rate:.1f}%")
            print(f"    Acceptance Rate: {acceptance_rate:.1f}%")

            if completion_rate == 100 and status["rejected"] == 0:
                print(
                    f"\n Milestone #{args.milestone} is FULLY ACCEPTED and ready for closure!"
                )
            elif status["rejected"] > 0:
                print(
                    f"\n  Milestone #{args.milestone} has rejected items requiring fixes"
                )
            else:
                print(f"\n⏳ Milestone #{args.milestone} is awaiting human review")

    else:
        print("Please specify --add-checklists or --check-status")
        sys.exit(1)


if __name__ == "__main__":
    main()

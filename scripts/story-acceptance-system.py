#!/usr/bin/env python3
"""
Story-Level Acceptance Testing System

Implements user story acceptance with automatic task cascade. Clients interact
at the story level while the system automatically manages technical task acceptance.

Key Features:
- Story-level acceptance checkboxes for client review
- Automatic cascade to related tasks when story is accepted
- Business-focused acceptance criteria (not technical details)
- Dependency tracking and validation
"""

import json
import os
import subprocess
import sys
from typing import Dict, List, Optional, Set
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


def get_all_milestone_issues(milestone_number: int) -> List[Dict]:
    """Get all issues in a milestone with their relationships."""
    print(f" Getting all issues for milestone #{milestone_number}...")

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


def categorize_issues(issues: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize issues into stories and tasks with relationship mapping."""
    stories = []
    tasks = []
    orphaned = []

    story_to_tasks = {}  # Map story ID to list of task IDs
    task_to_story = {}  # Map task ID to story ID

    for issue in issues:
        title = issue["title"]
        number = issue["number"]

        # Identify stories (S-XXX pattern)
        if re.match(r"S-\d+", title):
            stories.append(issue)
            story_id = re.search(r"S-(\d+)", title).group(1)
            story_to_tasks[story_id] = []

        # Identify tasks (T-XXX pattern)
        elif re.match(r"T-\d+", title):
            tasks.append(issue)
            # Extract story relationship from title
            story_match = re.search(r"for S-(\d+)", title)
            if story_match:
                story_id = story_match.group(1)
                task_id = re.search(r"T-(\d+)", title).group(1)

                if story_id in story_to_tasks:
                    story_to_tasks[story_id].append(number)
                    task_to_story[number] = story_id
                else:
                    orphaned.append(issue)
            else:
                orphaned.append(issue)
        else:
            orphaned.append(issue)

    return {
        "stories": stories,
        "tasks": tasks,
        "orphaned": orphaned,
        "story_to_tasks": story_to_tasks,
        "task_to_story": task_to_story,
    }


def create_story_acceptance_checklist(
    story_issue: Dict, related_tasks: List[int]
) -> str:
    """Create business-focused acceptance checklist for user stories."""
    story_title = story_issue["title"]
    story_body = story_issue.get("body", "")

    # Extract business value and acceptance criteria from story
    business_value = "Feature delivered as specified"
    if "business value" in story_body.lower():
        # Extract business value section if present
        lines = story_body.split("\n")
        for i, line in enumerate(lines):
            if "business value" in line.lower():
                business_value = lines[i + 1 : i + 3]  # Get next 1-2 lines
                break

    # Standard business acceptance criteria
    business_checks = [
        "[ ] Feature works as described in user story",
        "[ ] All acceptance criteria are met",
        "[ ] User experience is intuitive and smooth",
        "[ ] Feature integrates properly with existing functionality",
        "[ ] No breaking changes to existing features",
        "[ ] Documentation is updated for end users",
    ]

    # Story-specific checks based on content
    specific_checks = []

    # Subject management
    if any(
        keyword in story_title.lower() for keyword in ["subject", "create", "manage"]
    ):
        specific_checks.extend(
            [
                "[ ] Users can create new subjects successfully",
                "[ ] Subject information is properly stored and retrieved",
                "[ ] Subject validation prevents invalid data entry",
                "[ ] Users can edit and delete subjects as needed",
            ]
        )

    # Session management
    if any(keyword in story_title.lower() for keyword in ["session", "investigation"]):
        specific_checks.extend(
            [
                "[ ] Investigation sessions can be started and managed",
                "[ ] Session status tracking works correctly",
                "[ ] Users can configure investigation parameters",
                "[ ] Session data is properly organized and accessible",
            ]
        )

    # Search functionality
    if any(keyword in story_title.lower() for keyword in ["search", "meta-search"]):
        specific_checks.extend(
            [
                "[ ] Search functionality returns relevant results",
                "[ ] Multiple search engines are properly integrated",
                "[ ] Search results are well-formatted and useful",
                "[ ] Search performance is acceptable for user needs",
            ]
        )

    # Technical quality (hidden from client view)
    technical_checks = [
        "[ ] All automated tests pass",
        "[ ] Code quality meets professional standards",
        "[ ] Security requirements are satisfied",
        "[ ] Performance requirements are met",
    ]

    # Task completion status
    task_status = ""
    if related_tasks:
        task_status = f"""
###  Related Technical Tasks
{chr(10).join([f'- Task #{task_id}: Ready for acceptance' for task_id in related_tasks])}
"""

    checklist_content = f"""
##  User Story Acceptance

**Story**: {story_title}
**Reviewer**: _[Product Owner/Client Name]_
**Review Date**: _[Review Date]_

### Business Acceptance Criteria
{chr(10).join(business_checks)}

### Feature-Specific Validation
{chr(10).join(specific_checks) if specific_checks else "[ ] All feature requirements validated"}

{task_status}

### Technical Quality Assurance
<details>
<summary>Technical Validation (Click to expand)</summary>

{chr(10).join(technical_checks)}

**Technical Review**: ⏳ PENDING TECHNICAL VALIDATION
</details>

### Final Story Acceptance
- [ ] ** STORY ACCEPTED**: This user story is complete and ready for production
- [ ] ** STORY REJECTED**: Changes required - see comments below

### Review Comments
_[Add any feedback, change requests, or acceptance notes here]_

---
**Story Status**: ⏳ PENDING CLIENT ACCEPTANCE

*When this story is accepted, all related technical tasks will be automatically marked as accepted.*
"""

    return checklist_content


def create_task_technical_checklist(task_issue: Dict, story_id: str) -> str:
    """Create technical validation checklist for tasks."""
    task_title = task_issue["title"]

    technical_checks = [
        "[ ] Code review completed - no security issues",
        "[ ] All unit tests pass",
        "[ ] Integration tests pass",
        "[ ] No AI attribution in code or commits",
        "[ ] Implementation follows coding standards",
        "[ ] Documentation is accurate and complete",
        "[ ] Database operations are safe and atomic",
        "[ ] Error handling is comprehensive",
        "[ ] Performance requirements are met",
    ]

    checklist_content = f"""
##  Technical Task Validation

**Task**: {task_title}
**Parent Story**: S-{story_id}
**Technical Reviewer**: _[Developer/Tech Lead Name]_
**Review Date**: _[Review Date]_

### Technical Quality Checks
{chr(10).join(technical_checks)}

### Technical Acceptance
- [ ] ** TECHNICAL ACCEPTED**: Implementation meets all technical requirements
- [ ] ** TECHNICAL REJECTED**: Technical issues found - see comments

### Technical Notes
_[Add technical feedback, code review comments, or required changes]_

---
**Technical Status**: ⏳ PENDING TECHNICAL REVIEW

*This task will be automatically accepted when parent story S-{story_id} is accepted.*
"""

    return checklist_content


def add_story_acceptance_system(milestone_number: int) -> Dict:
    """Add story-level acceptance system to milestone."""
    print(f" Setting up story-level acceptance for milestone #{milestone_number}...")

    # Get and categorize all issues
    issues = get_all_milestone_issues(milestone_number)
    categorized = categorize_issues(issues)

    results = {
        "stories_processed": 0,
        "tasks_processed": 0,
        "stories_updated": 0,
        "tasks_updated": 0,
        "errors": [],
    }

    # Process stories first
    for story in categorized["stories"]:
        story_number = story["number"]
        story_title = story["title"]
        story_body = story.get("body", "")

        results["stories_processed"] += 1

        print(f" Processing story #{story_number}: {story_title}")

        # Skip if already has acceptance checklist
        if "User Story Acceptance" in story_body:
            print(f"   ℹ  Story already has acceptance checklist")
            continue

        # Get related tasks
        story_id = re.search(r"S-(\d+)", story_title).group(1)
        related_tasks = categorized["story_to_tasks"].get(story_id, [])

        # Create and add story acceptance checklist
        try:
            checklist = create_story_acceptance_checklist(story, related_tasks)
            updated_body = story_body + "\n" + checklist

            run_gh_command(
                [
                    "api",
                    f"repos/:owner/:repo/issues/{story_number}",
                    "-X",
                    "PATCH",
                    "-f",
                    f"body={updated_body}",
                ]
            )

            print(f"    Added story acceptance checklist")
            results["stories_updated"] += 1

        except Exception as e:
            error_msg = f"Failed to update story #{story_number}: {e}"
            print(f"    {error_msg}")
            results["errors"].append(error_msg)

    # Process tasks
    for task in categorized["tasks"]:
        task_number = task["number"]
        task_title = task["title"]
        task_body = task.get("body", "")

        results["tasks_processed"] += 1

        print(f" Processing task #{task_number}: {task_title}")

        # Skip if already has technical checklist
        if "Technical Task Validation" in task_body:
            print(f"   ℹ  Task already has technical checklist")
            continue

        # Get parent story
        parent_story = categorized["task_to_story"].get(task_number)
        if not parent_story:
            print(f"     Task has no parent story - skipping")
            continue

        # Create and add technical checklist
        try:
            checklist = create_task_technical_checklist(task, parent_story)
            updated_body = task_body + "\n" + checklist

            run_gh_command(
                [
                    "api",
                    f"repos/:owner/:repo/issues/{task_number}",
                    "-X",
                    "PATCH",
                    "-f",
                    f"body={updated_body}",
                ]
            )

            print(f"    Added technical validation checklist")
            results["tasks_updated"] += 1

        except Exception as e:
            error_msg = f"Failed to update task #{task_number}: {e}"
            print(f"    {error_msg}")
            results["errors"].append(error_msg)

    return results


def cascade_story_acceptance(story_number: int) -> Dict:
    """When a story is accepted, automatically accept all related tasks."""
    print(f" Cascading acceptance for story #{story_number}...")

    # Get story details
    story_result = run_gh_command(["api", f"repos/:owner/:repo/issues/{story_number}"])
    story_data = json.loads(story_result)

    # Check if story is actually accepted
    story_body = story_data.get("body", "")
    if "- [x] ** STORY ACCEPTED**" not in story_body:
        return {"error": "Story is not marked as accepted"}

    # Find related tasks
    story_title = story_data["title"]
    story_id_match = re.search(r"S-(\d+)", story_title)
    if not story_id_match:
        return {"error": "Could not extract story ID"}

    story_id = story_id_match.group(1)

    # Get all issues to find related tasks
    all_issues = run_gh_command(
        [
            "api",
            "repos/:owner/:repo/issues",
            "--jq",
            f'.[] | select(.title | contains("for S-{story_id}"))',
        ]
    )

    if not all_issues:
        return {"cascaded_tasks": 0, "message": "No related tasks found"}

    cascaded_count = 0
    errors = []

    # Process each related task
    for line in all_issues.split("\n"):
        if not line.strip():
            continue

        task_data = json.loads(line)
        task_number = task_data["number"]
        task_body = task_data.get("body", "")

        # Update task to show acceptance cascade
        if "Technical Task Validation" in task_body:
            # Mark technical acceptance as cascaded from story
            updated_body = task_body.replace(
                "- [ ] ** TECHNICAL ACCEPTED**",
                "- [x] ** TECHNICAL ACCEPTED** (Cascaded from Story S-"
                + story_id
                + " acceptance)",
            )

            # Add cascade note
            cascade_note = f"\n\n** AUTOMATICALLY ACCEPTED**: This task was accepted via cascade from parent Story S-{story_id} acceptance on {json.dumps('now')}."
            updated_body += cascade_note

            try:
                run_gh_command(
                    [
                        "api",
                        f"repos/:owner/:repo/issues/{task_number}",
                        "-X",
                        "PATCH",
                        "-f",
                        f"body={updated_body}",
                    ]
                )

                print(f"    Cascaded acceptance to task #{task_number}")
                cascaded_count += 1

            except Exception as e:
                error_msg = f"Failed to cascade to task #{task_number}: {e}"
                print(f"    {error_msg}")
                errors.append(error_msg)

    return {"cascaded_tasks": cascaded_count, "errors": errors, "story_id": story_id}


def check_story_acceptance_status(milestone_number: int) -> Dict:
    """Check story-level acceptance status for milestone."""
    print(f" Checking story acceptance status for milestone #{milestone_number}...")

    issues = get_all_milestone_issues(milestone_number)
    categorized = categorize_issues(issues)

    status = {
        "total_stories": len(categorized["stories"]),
        "stories_accepted": 0,
        "stories_rejected": 0,
        "stories_pending": 0,
        "total_tasks": len(categorized["tasks"]),
        "tasks_technically_accepted": 0,
        "tasks_cascaded": 0,
        "milestone_ready": False,
    }

    # Check story acceptance status
    for story in categorized["stories"]:
        story_body = story.get("body", "")

        if "- [x] ** STORY ACCEPTED**" in story_body:
            status["stories_accepted"] += 1
            print(f"    Story #{story['number']}: ACCEPTED")
        elif "- [x] ** STORY REJECTED**" in story_body:
            status["stories_rejected"] += 1
            print(f"    Story #{story['number']}: REJECTED")
        else:
            status["stories_pending"] += 1
            print(f"   ⏳ Story #{story['number']}: PENDING")

    # Check task technical acceptance
    for task in categorized["tasks"]:
        task_body = task.get("body", "")

        if "- [x] ** TECHNICAL ACCEPTED**" in task_body:
            status["tasks_technically_accepted"] += 1
            if "Cascaded from Story" in task_body:
                status["tasks_cascaded"] += 1

    # Determine if milestone is ready for closure
    status["milestone_ready"] = (
        status["stories_accepted"] == status["total_stories"]
        and status["stories_rejected"] == 0
    )

    return status


def main():
    """CLI interface for story-level acceptance testing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Story-Level Acceptance Testing System"
    )
    parser.add_argument("milestone", type=int, help="Milestone number to process")
    parser.add_argument(
        "--setup", action="store_true", help="Set up story-level acceptance system"
    )
    parser.add_argument(
        "--cascade",
        type=int,
        metavar="STORY_NUMBER",
        help="Cascade acceptance from story to related tasks",
    )
    parser.add_argument(
        "--status", action="store_true", help="Check story acceptance status"
    )

    args = parser.parse_args()

    if args.setup:
        results = add_story_acceptance_system(args.milestone)
        print(f"\n Story Acceptance System Setup Complete:")
        print(f"    Stories processed: {results['stories_processed']}")
        print(f"    Stories updated: {results['stories_updated']}")
        print(f"    Tasks processed: {results['tasks_processed']}")
        print(f"    Tasks updated: {results['tasks_updated']}")
        if results["errors"]:
            print(f"    Errors: {len(results['errors'])}")

    elif args.cascade:
        results = cascade_story_acceptance(args.cascade)
        if "error" in results:
            print(f" Cascade failed: {results['error']}")
        else:
            print(f" Cascaded acceptance to {results['cascaded_tasks']} tasks")

    elif args.status:
        status = check_story_acceptance_status(args.milestone)
        print(f"\n Milestone #{args.milestone} Story Acceptance Status:")
        print(f"    Total Stories: {status['total_stories']}")
        print(f"    Stories Accepted: {status['stories_accepted']}")
        print(f"    Stories Rejected: {status['stories_rejected']}")
        print(f"   ⏳ Stories Pending: {status['stories_pending']}")
        print(f"    Tasks Technical Accepted: {status['tasks_technically_accepted']}")
        print(f"    Tasks Cascaded: {status['tasks_cascaded']}")

        if status["milestone_ready"]:
            print(f"\n Milestone #{args.milestone} is READY FOR CLOSURE!")
        else:
            print(f"\n⏳ Milestone #{args.milestone} awaiting story acceptance")

    else:
        print("Please specify --setup, --cascade STORY_NUMBER, or --status")
        sys.exit(1)


if __name__ == "__main__":
    main()

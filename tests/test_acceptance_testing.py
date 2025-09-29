#!/usr/bin/env python3
"""
Test suite for acceptance testing checkbox system.

Validates the GitHub issue acceptance testing functionality including
checklist generation, status checking, and milestone management.
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add scripts to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from add_acceptance_checkboxes import (
    create_acceptance_checklist,
    add_acceptance_checklist_to_issue,
    process_milestone_for_acceptance,
    check_acceptance_status,
    run_gh_command,
)


class TestAcceptanceTestingSystem(unittest.TestCase):
    """Test cases for acceptance testing checkbox system."""

    def test_create_acceptance_checklist_standard(self):
        """Test creation of standard acceptance checklist."""
        issue_title = "Fix user authentication bug"
        issue_body = "Standard bug fix implementation"

        checklist = create_acceptance_checklist(issue_title, issue_body)

        # Check standard elements are present
        self.assertIn("Human Acceptance Testing", checklist)
        self.assertIn("Standard Quality Checks", checklist)
        self.assertIn("[ ] Code review completed", checklist)
        self.assertIn("[ ] All tests pass", checklist)
        self.assertIn("[ ] No AI attribution found", checklist)
        self.assertIn("**ACCEPTED**", checklist)
        self.assertIn("**REJECTED**", checklist)

    def test_create_acceptance_checklist_django_specific(self):
        """Test creation of Django-specific acceptance checklist."""
        issue_title = "S-001 — Django Model Implementation"
        issue_body = "Implement Django model with CRUD API endpoints"

        checklist = create_acceptance_checklist(issue_title, issue_body)

        # Check Django-specific elements
        self.assertIn("Database migrations are properly structured", checklist)
        self.assertIn("API endpoints return correct HTTP status codes", checklist)
        self.assertIn("Data validation is working correctly", checklist)
        self.assertIn("Database operations are atomic", checklist)

    def test_create_acceptance_checklist_frontend_specific(self):
        """Test creation of frontend-specific acceptance checklist."""
        issue_title = "React Component Development"
        issue_body = "Create responsive UI components"

        checklist = create_acceptance_checklist(issue_title, issue_body)

        # Check frontend-specific elements
        self.assertIn("UI components render correctly", checklist)
        self.assertIn("Responsive design works", checklist)
        self.assertIn("Accessibility requirements", checklist)
        self.assertIn("User experience is intuitive", checklist)

    def test_create_acceptance_checklist_testing_specific(self):
        """Test creation of testing-specific acceptance checklist."""
        issue_title = "Test Coverage Implementation"
        issue_body = "Add comprehensive test suite with coverage reporting"

        checklist = create_acceptance_checklist(issue_title, issue_body)

        # Check testing-specific elements
        self.assertIn("Test coverage is adequate", checklist)
        self.assertIn("Edge cases are properly tested", checklist)
        self.assertIn("Test data is realistic", checklist)
        self.assertIn("Performance tests pass", checklist)

    @patch("add_acceptance_checkboxes.run_gh_command")
    def test_add_acceptance_checklist_success(self, mock_run_gh):
        """Test successful addition of acceptance checklist to issue."""
        mock_run_gh.return_value = ""

        issue_title = "Test Issue"
        issue_body = "Original issue body"

        result = add_acceptance_checklist_to_issue(123, issue_title, issue_body)

        self.assertTrue(result)
        mock_run_gh.assert_called_once()

        # Check the API call was made correctly
        call_args = mock_run_gh.call_args[0][0]
        self.assertIn("repos/:owner/:repo/issues/123", call_args)
        self.assertIn("-X", call_args)
        self.assertIn("PATCH", call_args)

    @patch("add_acceptance_checkboxes.run_gh_command")
    def test_add_acceptance_checklist_already_exists(self, mock_run_gh):
        """Test handling when acceptance checklist already exists."""
        issue_title = "Test Issue"
        issue_body = "Original body\n##  Human Acceptance Testing\nExisting checklist"

        result = add_acceptance_checklist_to_issue(123, issue_title, issue_body)

        self.assertTrue(result)
        # Should not call GitHub API if checklist already exists
        mock_run_gh.assert_not_called()

    @patch("add_acceptance_checkboxes.run_gh_command")
    def test_add_acceptance_checklist_failure(self, mock_run_gh):
        """Test handling of GitHub API failure."""
        mock_run_gh.side_effect = Exception("API Error")

        issue_title = "Test Issue"
        issue_body = "Original issue body"

        result = add_acceptance_checklist_to_issue(123, issue_title, issue_body)

        self.assertFalse(result)

    @patch("add_acceptance_checkboxes.get_milestone_issues")
    @patch("add_acceptance_checkboxes.add_acceptance_checklist_to_issue")
    def test_process_milestone_for_acceptance(
        self, mock_add_checklist, mock_get_issues
    ):
        """Test processing entire milestone for acceptance testing."""
        # Mock milestone issues
        mock_get_issues.return_value = [
            {"number": 67, "title": "Issue 1", "body": "Body 1", "state": "closed"},
            {"number": 68, "title": "Issue 2", "body": "Body 2", "state": "closed"},
            {"number": 69, "title": "Issue 3", "body": "Body 3", "state": "open"},
        ]

        mock_add_checklist.return_value = True

        result = process_milestone_for_acceptance(1)

        # Should process 3 issues, update 2 closed ones, skip 1 open
        self.assertEqual(result["processed"], 3)
        self.assertEqual(result["updated"], 2)
        self.assertEqual(result["skipped"], 1)

        # Should have called add_checklist for closed issues only
        self.assertEqual(mock_add_checklist.call_count, 2)

    @patch("add_acceptance_checkboxes.get_milestone_issues")
    def test_check_acceptance_status(self, mock_get_issues):
        """Test checking acceptance status of milestone issues."""
        # Mock milestone issues with different acceptance states
        mock_get_issues.return_value = [
            {
                "number": 67,
                "body": "Issue with acceptance\n- [x] **ACCEPTED**: This implementation meets all requirements",
            },
            {
                "number": 68,
                "body": "Issue with rejection\n- [x] **REJECTED**: Issues found - see comments below",
            },
            {
                "number": 69,
                "body": "Issue pending\n##  Human Acceptance Testing\n- [ ] **ACCEPTED**",
            },
            {"number": 70, "body": "Issue without checklist"},
        ]

        status = check_acceptance_status(1)

        self.assertEqual(status["total_issues"], 4)
        self.assertEqual(status["accepted"], 1)
        self.assertEqual(status["rejected"], 1)
        self.assertEqual(status["pending"], 1)
        self.assertEqual(status["no_checklist"], 1)

    @patch("subprocess.run")
    def test_run_gh_command_success(self, mock_run):
        """Test successful GitHub CLI command execution."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "command output"
        mock_run.return_value.stderr = ""

        result = run_gh_command(["api", "repos/:owner/:repo/issues"])

        self.assertEqual(result, "command output")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_gh_command_failure(self, mock_run):
        """Test GitHub CLI command execution failure."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, ["gh"], "error output", "stderr")

        with self.assertRaises(CalledProcessError):
            run_gh_command(["api", "invalid-endpoint"])

    def test_checklist_format_consistency(self):
        """Test that generated checklists have consistent format."""
        issue_title = "Test Issue"
        issue_body = "Test body"

        checklist = create_acceptance_checklist(issue_title, issue_body)

        # Check required sections are present
        required_sections = [
            " Human Acceptance Testing",
            "Standard Quality Checks",
            "Implementation-Specific Checks",
            "Final Acceptance",
            "Review Notes",
        ]

        for section in required_sections:
            self.assertIn(section, checklist)

        # Check checkbox format consistency
        checkbox_patterns = [
            "[ ] Code review completed",
            "[ ] All tests pass",
            "[ ] **ACCEPTED**",
            "[ ] **REJECTED**",
        ]

        for pattern in checkbox_patterns:
            self.assertIn(pattern, checklist)


class TestAcceptanceTestingIntegration(unittest.TestCase):
    """Integration tests for acceptance testing system."""

    def setUp(self):
        """Set up integration test environment."""
        self.sample_issues = [
            {
                "number": 67,
                "title": "S-002 — Django Session Management",
                "body": "Implement Django session model with status tracking",
                "state": "closed",
            },
            {
                "number": 68,
                "title": "T-001 — React Component Development",
                "body": "Create responsive UI components with accessibility",
                "state": "closed",
            },
        ]

    def test_end_to_end_checklist_creation(self):
        """Test complete checklist creation workflow."""
        for issue in self.sample_issues:
            checklist = create_acceptance_checklist(issue["title"], issue["body"])

            # Verify checklist contains appropriate content
            self.assertIn("Human Acceptance Testing", checklist)

            # Check for technology-specific content
            if "Django" in issue["title"]:
                self.assertIn("Database migrations", checklist)
            if "React" in issue["title"]:
                self.assertIn("UI components render", checklist)

            # Verify checklist structure
            self.assertIn("[ ] **ACCEPTED**", checklist)
            self.assertIn("[ ] **REJECTED**", checklist)
            self.assertIn("Acceptance Status", checklist)

    def test_checklist_customization_by_technology(self):
        """Test that checklists are properly customized by technology stack."""
        technologies = [
            (
                "Django API Implementation",
                ["Database migrations", "API endpoints", "Data validation"],
            ),
            ("React Frontend", ["UI components", "Responsive design", "Accessibility"]),
            (
                "Test Suite Development",
                ["Test coverage", "Edge cases", "Performance tests"],
            ),
        ]

        for title, expected_content in technologies:
            checklist = create_acceptance_checklist(title, f"Implementation of {title}")

            for content in expected_content:
                self.assertIn(
                    content, checklist, f"Missing '{content}' in {title} checklist"
                )


if __name__ == "__main__":
    # Create test configuration for CLI testing
    print(" Running acceptance testing system tests...")
    print("=" * 50)

    # Run all tests
    unittest.main(verbosity=2)

    print("=" * 50)
    print(" Acceptance testing system validation complete!")
    print(" Usage examples:")
    print("   # Add checklists to milestone issues:")
    print("   python scripts/add-acceptance-checkboxes.py 1 --add-checklists")
    print("   # Check acceptance status:")
    print("   python scripts/add-acceptance-checkboxes.py 1 --check-status")
    print("   # Detailed summary:")
    print("   python scripts/add-acceptance-checkboxes.py 1 --summary")

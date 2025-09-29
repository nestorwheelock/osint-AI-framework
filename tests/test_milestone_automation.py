#!/usr/bin/env python3
"""
Test suite for Milestone Automation System

Validates the complete milestone workflow including GitHub integration,
documentation generation, and PDF updates.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add scripts to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from milestone_automation import MilestoneAutomation


class TestMilestoneAutomation(unittest.TestCase):
    """Test cases for milestone automation system."""

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Create project structure
        (self.project_root / "docs" / "sprints").mkdir(parents=True)
        (self.project_root / "scripts").mkdir(parents=True)

        # Create sample files
        (self.project_root / "docs" / "WHITEPAPER-TEST.md").write_text(
            "# Test Whitepaper\n\nContent here\n"
        )

        self.automation = MilestoneAutomation(str(self.project_root))

    def tearDown(self):
        """Clean up temporary files."""
        import shutil

        shutil.rmtree(self.temp_dir)

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test successful command execution."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "success output"
        mock_run.return_value.stderr = ""

        success, stdout, stderr = self.automation.run_command(["echo", "test"])

        self.assertTrue(success)
        self.assertEqual(stdout, "success output")
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test command execution failure."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(
            1, ["false"], "error output", "stderr"
        )

        success, stdout, stderr = self.automation.run_command(["false"])

        self.assertFalse(success)
        self.assertEqual(stderr, "stderr")

    @patch.object(MilestoneAutomation, "run_command")
    def test_run_tests_success(self, mock_run_command):
        """Test successful test execution."""
        # Create manage.py
        (self.project_root / "backend" / "manage.py").parent.mkdir()
        (self.project_root / "backend" / "manage.py").write_text(
            "#!/usr/bin/env python"
        )

        mock_run_command.return_value = (True, "Ran 28 tests in 2.5s\nOK", "")

        success, results = self.automation.run_tests()

        self.assertTrue(success)
        self.assertEqual(results["total_tests"], 28)
        self.assertEqual(results["status"], "PASSED")

    @patch.object(MilestoneAutomation, "run_command")
    def test_run_tests_failure(self, mock_run_command):
        """Test test execution failure."""
        # Create manage.py
        (self.project_root / "backend" / "manage.py").parent.mkdir()
        (self.project_root / "backend" / "manage.py").write_text(
            "#!/usr/bin/env python"
        )

        mock_run_command.return_value = (False, "", "Test failed")

        success, results = self.automation.run_tests()

        self.assertFalse(success)
        self.assertIn("error", results)

    def test_run_tests_no_manage_py(self):
        """Test test execution when manage.py doesn't exist."""
        success, results = self.automation.run_tests()

        self.assertFalse(success)
        self.assertIn("Django manage.py not found", results["error"])

    @patch.object(MilestoneAutomation, "run_command")
    def test_create_github_milestone_success(self, mock_run_command):
        """Test successful GitHub milestone creation."""
        milestone_data = {
            "number": 1,
            "title": "Test Milestone",
            "html_url": "https://github.com/test/repo/milestone/1",
        }

        mock_run_command.return_value = (True, json.dumps(milestone_data), "")

        success, result = self.automation.create_github_milestone(
            "Test Milestone", "Test description"
        )

        self.assertTrue(success)
        self.assertEqual(result["number"], 1)
        self.assertEqual(result["title"], "Test Milestone")

    @patch.object(MilestoneAutomation, "run_command")
    def test_create_github_milestone_failure(self, mock_run_command):
        """Test GitHub milestone creation failure."""
        mock_run_command.return_value = (False, "", "API error")

        success, result = self.automation.create_github_milestone(
            "Test Milestone", "Test description"
        )

        self.assertFalse(success)
        self.assertIn("error", result)

    @patch.object(MilestoneAutomation, "run_command")
    def test_close_milestone(self, mock_run_command):
        """Test milestone closure."""
        mock_run_command.return_value = (True, "", "")

        success = self.automation.close_milestone(1)

        self.assertTrue(success)
        mock_run_command.assert_called_once()

    @patch.object(MilestoneAutomation, "run_command")
    def test_assign_issues_to_milestone(self, mock_run_command):
        """Test issue assignment to milestone."""
        mock_run_command.return_value = (True, "", "")

        results = self.automation.assign_issues_to_milestone(1, [67, 68])

        self.assertEqual(len(results["assigned"]), 2)
        self.assertEqual(len(results["failed"]), 0)
        self.assertIn(67, results["assigned"])
        self.assertIn(68, results["assigned"])

    @patch.object(MilestoneAutomation, "run_command")
    def test_assign_issues_partial_failure(self, mock_run_command):
        """Test issue assignment with partial failures."""
        # First call succeeds, second fails
        mock_run_command.side_effect = [(True, "", ""), (False, "", "Issue not found")]

        results = self.automation.assign_issues_to_milestone(1, [67, 999])

        self.assertEqual(len(results["assigned"]), 1)
        self.assertEqual(len(results["failed"]), 1)
        self.assertIn(67, results["assigned"])
        self.assertEqual(results["failed"][0]["issue"], 999)

    def test_generate_sprint_documentation(self):
        """Test sprint documentation generation."""
        stories = ["S-001 — Create Subject", "S-002 — Start Session"]
        metrics = {"total_tests": 28, "test_status": "PASSED"}

        doc_content = self.automation.generate_sprint_documentation(
            "Sprint 1: Foundation", stories, metrics
        )

        self.assertIn("Sprint 1: Foundation", doc_content)
        self.assertIn("S-001 — Create Subject", doc_content)
        self.assertIn("S-002 — Start Session", doc_content)
        self.assertIn("28 tests passing", doc_content)
        self.assertIn("PASSED", doc_content)

    @patch.object(MilestoneAutomation, "run_command")
    def test_update_whitepapers(self, mock_run_command):
        """Test whitepaper updating."""
        # Mock pandoc command success
        mock_run_command.return_value = (True, "", "")

        sprint_data = {"sprint_name": "Sprint 1: Foundation", "total_tests": 28}

        updated_files = self.automation.update_whitepapers(sprint_data)

        # Check that whitepaper was updated
        whitepaper_file = self.project_root / "docs" / "WHITEPAPER-TEST.md"
        content = whitepaper_file.read_text()

        self.assertIn("Sprint Completion Update", content)
        self.assertIn("Sprint 1: Foundation", content)
        self.assertIn("28 passing", content)
        self.assertTrue(len(updated_files) > 0)

    @patch.object(MilestoneAutomation, "run_tests")
    @patch.object(MilestoneAutomation, "create_github_milestone")
    @patch.object(MilestoneAutomation, "assign_issues_to_milestone")
    @patch.object(MilestoneAutomation, "close_milestone")
    @patch.object(MilestoneAutomation, "update_whitepapers")
    def test_complete_milestone_success(
        self,
        mock_update_whitepapers,
        mock_close_milestone,
        mock_assign_issues,
        mock_create_milestone,
        mock_run_tests,
    ):
        """Test complete milestone workflow success."""
        # Setup mocks
        mock_run_tests.return_value = (
            True,
            {"total_tests": 28, "test_status": "PASSED"},
        )
        mock_create_milestone.return_value = (True, {"number": 1, "title": "Test"})
        mock_assign_issues.return_value = {"assigned": [67, 68], "failed": []}
        mock_close_milestone.return_value = True
        mock_update_whitepapers.return_value = ["whitepaper.md", "whitepaper.pdf"]

        milestone_config = {
            "title": "Sprint 1: Foundation",
            "description": "Test sprint",
            "issues": [67, 68],
            "stories": ["S-001", "S-002"],
            "close_milestone": True,
        }

        results = self.automation.complete_milestone(milestone_config)

        self.assertTrue(results["success"])
        self.assertEqual(len(results["steps"]), 7)  # All steps completed

        # Verify all steps were called
        mock_run_tests.assert_called_once()
        mock_create_milestone.assert_called_once()
        mock_assign_issues.assert_called_once()
        mock_close_milestone.assert_called_once()
        mock_update_whitepapers.assert_called_once()

    @patch.object(MilestoneAutomation, "run_tests")
    def test_complete_milestone_test_failure(self, mock_run_tests):
        """Test milestone completion with test failures."""
        mock_run_tests.return_value = (False, {"error": "Tests failed"})

        milestone_config = {
            "title": "Sprint 1: Foundation",
            "description": "Test sprint",
        }

        results = self.automation.complete_milestone(milestone_config)

        self.assertFalse(results["success"])
        self.assertIn("Tests failed", results["error"])

    @patch.object(MilestoneAutomation, "run_tests")
    @patch.object(MilestoneAutomation, "create_github_milestone")
    def test_complete_milestone_github_failure(
        self, mock_create_milestone, mock_run_tests
    ):
        """Test milestone completion with GitHub milestone failure."""
        mock_run_tests.return_value = (True, {"total_tests": 28})
        mock_create_milestone.return_value = (False, {"error": "GitHub API error"})

        milestone_config = {
            "title": "Sprint 1: Foundation",
            "description": "Test sprint",
        }

        results = self.automation.complete_milestone(milestone_config)

        self.assertFalse(results["success"])
        self.assertIn("Failed to create GitHub milestone", results["error"])

    def test_milestone_automation_initialization(self):
        """Test MilestoneAutomation class initialization."""
        automation = MilestoneAutomation(str(self.project_root))

        self.assertEqual(automation.project_root, self.project_root)
        self.assertEqual(automation.docs_dir, self.project_root / "docs")
        self.assertEqual(automation.scripts_dir, self.project_root / "scripts")

    def test_milestone_automation_default_path(self):
        """Test MilestoneAutomation with default current directory."""
        with patch("os.getcwd", return_value=str(self.project_root)):
            automation = MilestoneAutomation()
            self.assertEqual(automation.project_root, self.project_root)


class TestMilestoneAutomationIntegration(unittest.TestCase):
    """Integration tests for milestone automation system."""

    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Create realistic project structure
        (self.project_root / "backend").mkdir()
        (self.project_root / "docs" / "sprints").mkdir(parents=True)
        (self.project_root / "scripts").mkdir()

        # Create manage.py
        (self.project_root / "backend" / "manage.py").write_text(
            "#!/usr/bin/env python\nprint('Django manage.py')"
        )

        # Create whitepaper
        (
            self.project_root / "docs" / "WHITEPAPER-AI-CONSTRAINT-METHODOLOGY.md"
        ).write_text("# AI Constraint Methodology\n\nOriginal content\n")

    def tearDown(self):
        """Clean up integration test environment."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_integration_file_creation(self):
        """Test that milestone automation creates expected files."""
        automation = MilestoneAutomation(str(self.project_root))

        # Test sprint documentation generation
        doc_content = automation.generate_sprint_documentation(
            "Sprint 1: Test", ["S-001"], {"total_tests": 10, "test_status": "PASSED"}
        )

        self.assertIn("Sprint 1: Test", doc_content)
        self.assertIn("Template Components", doc_content)
        self.assertIn("10 tests passing", doc_content)

    def test_integration_whitepaper_update(self):
        """Test whitepaper updating integration."""
        automation = MilestoneAutomation(str(self.project_root))

        # Mock pandoc command
        with patch.object(automation, "run_command") as mock_run:
            mock_run.return_value = (True, "", "")

            updated_files = automation.update_whitepapers(
                {"sprint_name": "Sprint 1: Test", "total_tests": 10}
            )

            # Check file was updated
            whitepaper = (
                self.project_root / "docs" / "WHITEPAPER-AI-CONSTRAINT-METHODOLOGY.md"
            )
            content = whitepaper.read_text()

            self.assertIn("Sprint Completion Update", content)
            self.assertIn("Sprint 1: Test", content)
            self.assertIn("Original content", content)  # Original content preserved


if __name__ == "__main__":
    # Create test configuration file for CLI testing
    test_config = {
        "title": "Test Sprint: Foundation",
        "description": "Test sprint for milestone automation",
        "issues": [67, 68],
        "stories": ["S-001 — Test Story", "S-002 — Another Story"],
        "close_milestone": False,
    }

    config_file = Path(__file__).parent / "test_milestone_config.json"
    with open(config_file, "w") as f:
        json.dump(test_config, f, indent=2)

    print(f"Test configuration created at: {config_file}")
    print("Run tests with: python -m unittest test_milestone_automation.py")
    print(
        "Run CLI test with: python scripts/milestone-automation.py --config tests/test_milestone_config.json"
    )

    unittest.main()

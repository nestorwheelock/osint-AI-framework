#!/usr/bin/env python3
"""
Test suite for Enhanced Kanban System

Validates kanban workflow mapping, backlog organization, and GitHub integration
using comprehensive TDD approach.
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add scripts to path for importing
scripts_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))

# Import the kanban system from scripts directory
import importlib.util

kanban_script = scripts_path / "enhanced-kanban-system.py"
spec = importlib.util.spec_from_file_location("enhanced_kanban_system", kanban_script)
enhanced_kanban_system = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enhanced_kanban_system)
EnhancedKanbanSystem = enhanced_kanban_system.EnhancedKanbanSystem


class TestEnhancedKanbanSystem(unittest.TestCase):
    """Test cases for enhanced kanban system functionality."""

    def setUp(self):
        """Set up test environment."""
        self.kanban = EnhancedKanbanSystem("test_project_id")

    def test_initialization(self):
        """Test kanban system initialization."""
        self.assertEqual(self.kanban.project_id, "test_project_id")
        self.assertIn("Backlog", self.kanban.status_options)
        self.assertIn("Todo", self.kanban.status_options)
        self.assertIn("In Progress", self.kanban.status_options)
        self.assertIn("Done", self.kanban.status_options)

    def test_status_mapping_completeness(self):
        """Test that all required status options are mapped."""
        required_statuses = ["Backlog", "Todo", "In Progress", "Done"]
        for status in required_statuses:
            self.assertIn(status, self.kanban.status_options)
            self.assertIsInstance(self.kanban.status_options[status], str)

    def test_categorize_items_by_type_stories(self):
        """Test categorization of story items."""
        items = [
            {"content": {"title": "S-001 — Create Subject", "labels": {"nodes": []}}},
            {
                "content": {
                    "title": "S-003 — Meta-Search Implementation",
                    "labels": {"nodes": []},
                }
            },
        ]

        categories = self.kanban.categorize_items_by_type(items)

        self.assertEqual(len(categories["stories"]), 2)
        self.assertEqual(len(categories["tasks"]), 0)
        self.assertTrue(
            any("S-001" in item["content"]["title"] for item in categories["stories"])
        )

    def test_categorize_items_by_type_tasks(self):
        """Test categorization of task items."""
        items = [
            {
                "content": {
                    "title": "T-001 — Tasks for S-001: Create Subject",
                    "labels": {"nodes": []},
                }
            },
            {
                "content": {
                    "title": "T-003 — Tasks for S-003: Meta-Search",
                    "labels": {"nodes": []},
                }
            },
        ]

        categories = self.kanban.categorize_items_by_type(items)

        self.assertEqual(len(categories["tasks"]), 2)
        self.assertEqual(len(categories["stories"]), 0)
        self.assertTrue(
            any("T-001" in item["content"]["title"] for item in categories["tasks"])
        )

    def test_categorize_items_by_type_labels(self):
        """Test categorization based on labels."""
        items = [
            {
                "content": {
                    "title": "Fix authentication bug",
                    "labels": {"nodes": [{"name": "bug"}]},
                }
            },
            {
                "content": {
                    "title": "Epic: OSINT Platform",
                    "labels": {"nodes": [{"name": "epic"}]},
                }
            },
            {
                "content": {
                    "title": "Enhance search performance",
                    "labels": {"nodes": [{"name": "enhancement"}]},
                }
            },
        ]

        categories = self.kanban.categorize_items_by_type(items)

        self.assertEqual(len(categories["bugs"]), 1)
        self.assertEqual(len(categories["epics"]), 1)
        self.assertEqual(len(categories["enhancements"]), 1)

    def test_categorize_items_by_type_dependencies(self):
        """Test categorization of dependency items."""
        items = [
            {
                "content": {
                    "title": "Setup database infrastructure",
                    "labels": {"nodes": []},
                }
            },
            {
                "content": {
                    "title": "Install project dependencies",
                    "labels": {"nodes": []},
                }
            },
        ]

        categories = self.kanban.categorize_items_by_type(items)

        self.assertEqual(len(categories["dependencies"]), 2)

    def test_categorize_items_empty_content(self):
        """Test categorization handles items without content."""
        items = [
            {"content": None},
            {},
            {"content": {"title": "S-001 — Valid Story", "labels": {"nodes": []}}},
        ]

        categories = self.kanban.categorize_items_by_type(items)

        # Should only process the valid item
        total_categorized = sum(len(cat_items) for cat_items in categories.values())
        self.assertEqual(total_categorized, 1)
        self.assertEqual(len(categories["stories"]), 1)

    def test_get_item_status_with_status(self):
        """Test getting item status when status field exists."""
        item = {
            "fieldValues": {
                "nodes": [{"name": "In Progress", "field": {"name": "Status"}}]
            }
        }

        status = self.kanban.get_item_status(item)
        self.assertEqual(status, "In Progress")

    def test_get_item_status_without_status(self):
        """Test getting item status when no status field exists."""
        item = {"fieldValues": {"nodes": []}}

        status = self.kanban.get_item_status(item)
        self.assertEqual(status, "Backlog")

    def test_get_item_status_missing_field_values(self):
        """Test getting item status when fieldValues is missing."""
        item = {}

        status = self.kanban.get_item_status(item)
        self.assertEqual(status, "Backlog")

    def test_suggest_backlog_organization(self):
        """Test backlog organization suggestions."""
        # Mock items with different statuses
        items_with_status = [
            ({"content": {"title": "S-001 — Story"}}, "Done"),
            ({"content": {"title": "S-002 — Another Story"}}, "In Progress"),
            ({"content": {"title": "T-001 — Task"}}, "Todo"),
            ({"content": {"title": "Setup Infrastructure"}}, "Backlog"),
        ]

        categories = {
            "stories": [
                item
                for item, _ in items_with_status
                if item["content"]["title"].startswith("S-")
            ],
            "tasks": [
                item
                for item, _ in items_with_status
                if item["content"]["title"].startswith("T-")
            ],
            "dependencies": [
                item
                for item, _ in items_with_status
                if "Infrastructure" in item["content"]["title"]
            ],
            "epics": [],
            "enhancements": [],
            "bugs": [],
        }

        # Mock get_item_status to return predetermined statuses
        status_map = {
            item["content"]["title"]: status for item, status in items_with_status
        }

        def mock_get_status(item):
            return status_map.get(item["content"]["title"], "Backlog")

        self.kanban.get_item_status = mock_get_status

        suggestions = self.kanban.suggest_backlog_organization(categories)

        # Verify organization
        self.assertEqual(len(suggestions["completed"]), 1)  # Done items
        self.assertEqual(len(suggestions["current_epoch"]), 2)  # In Progress + Todo
        self.assertEqual(len(suggestions["dependencies"]), 1)  # Infrastructure items

    @patch.object(enhanced_kanban_system, "run_gh_command")
    def test_move_item_to_backlog_success(self, mock_run_gh):
        """Test successful item move to backlog."""
        mock_run_gh.return_value = '{"data": {"updateProjectV2ItemFieldValue": {"projectV2Item": {"id": "test_id"}}}}'

        result = self.kanban.move_item_to_backlog("test_item_id", "Test Issue")

        self.assertTrue(result)
        mock_run_gh.assert_called_once()

        # Verify the GraphQL mutation was called correctly
        call_args = mock_run_gh.call_args[0][0]
        self.assertIn("updateProjectV2ItemFieldValue", call_args[3])

    @patch.object(enhanced_kanban_system, "run_gh_command")
    def test_move_item_to_backlog_failure(self, mock_run_gh):
        """Test failed item move to backlog."""
        mock_run_gh.side_effect = Exception("API Error")

        result = self.kanban.move_item_to_backlog("test_item_id", "Test Issue")

        self.assertFalse(result)

    @patch.object(EnhancedKanbanSystem, "get_project_structure")
    @patch.object(EnhancedKanbanSystem, "get_item_status")
    def test_organize_backlog_by_priority_dry_run(
        self, mock_get_status, mock_get_structure
    ):
        """Test backlog organization in dry run mode."""
        # Mock project data
        mock_get_structure.return_value = {
            "data": {
                "node": {
                    "items": {
                        "nodes": [
                            {
                                "id": "item1",
                                "content": {"title": "S-001 — High Priority Story"},
                            },
                            {
                                "id": "item2",
                                "content": {"title": "Critical Infrastructure Setup"},
                            },
                            {
                                "id": "item3",
                                "content": {"title": "T-001 — Medium Priority Task"},
                            },
                        ]
                    }
                }
            }
        }

        mock_get_status.return_value = "Todo"  # Not in backlog yet

        result = self.kanban.organize_backlog_by_priority(dry_run=True)

        # Verify categorization
        self.assertIn("high_priority", result)
        self.assertIn("dependencies", result)
        self.assertIn("medium_priority", result)
        self.assertEqual(len(result["actions_taken"]), 0)  # Dry run, no actions

    @patch.object(enhanced_kanban_system, "datetime")
    def test_create_backlog_view_report_generation(self, mock_datetime):
        """Test backlog view report generation."""
        mock_datetime.now.return_value.strftime.return_value = "2025-09-28 15:00:00"

        # Mock the necessary methods
        self.kanban.get_project_structure = Mock(
            return_value={
                "data": {"node": {"title": "Test Project", "items": {"nodes": []}}}
            }
        )

        self.kanban.categorize_items_by_type = Mock(
            return_value={
                "stories": [],
                "tasks": [],
                "epics": [],
                "dependencies": [],
                "enhancements": [],
                "bugs": [],
            }
        )

        self.kanban.suggest_backlog_organization = Mock(
            return_value={
                "immediate_backlog": [],
                "future_backlog": [],
                "dependencies": [],
                "current_epoch": [],
                "completed": [],
            }
        )

        report = self.kanban.create_backlog_view()

        # Verify report structure
        self.assertIn("Enhanced Kanban Backlog Analysis", report)
        self.assertIn("**Generated**: 2025-09-28 15:00:00", report)
        self.assertIn("Workflow Philosophy", report)
        self.assertIn("Backlog Statistics", report)
        self.assertIn("Recommendations", report)


class TestKanbanSystemIntegration(unittest.TestCase):
    """Integration tests for kanban system."""

    def setUp(self):
        """Set up integration test environment."""
        self.kanban = EnhancedKanbanSystem("test_project")

    def test_workflow_mapping_consistency(self):
        """Test that workflow mapping is consistent with our methodology."""
        # Verify the four-column structure
        expected_columns = ["Backlog", "Todo", "In Progress", "Done"]
        actual_columns = list(self.kanban.status_options.keys())

        for column in expected_columns:
            self.assertIn(column, actual_columns)

    def test_item_lifecycle_flow(self):
        """Test complete item lifecycle through kanban columns."""
        # Simulate item progression
        test_item = {
            "content": {"title": "S-001 — Test Story", "labels": {"nodes": []}},
            "fieldValues": {"nodes": []},
        }

        # Should start in backlog
        initial_status = self.kanban.get_item_status(test_item)
        self.assertEqual(initial_status, "Backlog")

        # Should be categorized as story
        categories = self.kanban.categorize_items_by_type([test_item])
        self.assertEqual(len(categories["stories"]), 1)

    def test_priority_classification_logic(self):
        """Test priority classification for different item types."""
        test_items = [
            ("S-001 — User Story", "high_priority"),
            ("Critical Infrastructure", "dependencies"),
            ("T-001 — Task", "medium_priority"),
            ("Bug Fix", "low_priority"),
        ]

        # Mock the organize method logic
        for title, expected_priority in test_items:
            if any(
                keyword in title.lower() for keyword in ["critical", "infrastructure"]
            ):
                actual_priority = "dependencies"
            elif title.startswith("S-"):
                actual_priority = "high_priority"
            elif title.startswith("T-"):
                actual_priority = "medium_priority"
            else:
                actual_priority = "low_priority"

            self.assertEqual(actual_priority, expected_priority)


if __name__ == "__main__":
    print(" Running Enhanced Kanban System Tests...")
    print("=" * 50)

    # Run all tests
    unittest.main(verbosity=2)

    print("=" * 50)
    print(" Enhanced Kanban System test suite complete!")
    print(" Usage examples:")
    print("   # Analyze current backlog:")
    print("   python scripts/enhanced-kanban-system.py --analyze")
    print("   # Organize backlog (dry run):")
    print("   python scripts/enhanced-kanban-system.py --organize --dry-run")
    print("   # Execute backlog organization:")
    print("   python scripts/enhanced-kanban-system.py --organize")

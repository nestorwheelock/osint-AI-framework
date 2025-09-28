#!/usr/bin/env python3
"""
GitHub API automation script for setting up project structure.
This script automates the manual GitHub setup work including:
- Creating GitHub Projects
- Setting up issues from user stories
- Configuring repository settings
- Setting up branch protection
- Managing labels and milestones
"""

import os
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import yaml
import re

class GitHubProjectAutomation:
    """Automates GitHub project setup using GitHub CLI and API."""

    def __init__(self, repo_name: str, dry_run: bool = False):
        self.repo_name = repo_name
        self.dry_run = dry_run
        self.project_root = Path.cwd()

        # Check if gh CLI is available
        if not self._check_gh_cli():
            raise RuntimeError("GitHub CLI (gh) is required but not found")

    def _check_gh_cli(self) -> bool:
        """Check if GitHub CLI is installed and authenticated."""
        try:
            result = subprocess.run(['gh', 'auth', 'status'],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _run_gh_command(self, cmd: List[str]) -> Optional[str]:
        """Run a GitHub CLI command and return output."""
        full_cmd = ['gh'] + cmd

        if self.dry_run:
            print(f"[DRY RUN] Would execute: {' '.join(full_cmd)}")
            return None

        try:
            result = subprocess.run(full_cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running command {' '.join(full_cmd)}: {e}")
            print(f"STDERR: {e.stderr}")
            return None

    def setup_repository_settings(self):
        """Configure repository settings via GitHub API."""
        print("🔧 Configuring repository settings...")

        settings = {
            'has_issues': True,
            'has_projects': True,
            'has_wiki': False,
            'allow_squash_merge': True,
            'allow_merge_commit': False,
            'allow_rebase_merge': False,
            'delete_branch_on_merge': True,
        }

        for setting, value in settings.items():
            cmd = ['api', '-X', 'PATCH', f'repos/{self.repo_name}',
                   '-f', f'{setting}={str(value).lower()}']
            self._run_gh_command(cmd)

    def setup_labels(self):
        """Create standardized labels for the project."""
        print("🏷️  Setting up project labels...")

        labels = [
            {'name': 'type:feature', 'color': '0052cc', 'description': 'New feature or enhancement'},
            {'name': 'type:bug', 'color': 'd73a4a', 'description': 'Something isn\'t working'},
            {'name': 'type:docs', 'color': '0075ca', 'description': 'Documentation improvement'},
            {'name': 'type:refactor', 'color': 'fbca04', 'description': 'Code refactoring'},
            {'name': 'priority:high', 'color': 'b60205', 'description': 'High priority'},
            {'name': 'priority:medium', 'color': 'fbca04', 'description': 'Medium priority'},
            {'name': 'priority:low', 'color': '0e8a16', 'description': 'Low priority'},
            {'name': 'size:small', 'color': 'c2e0c6', 'description': '1-2 days of work'},
            {'name': 'size:medium', 'color': 'fef2c0', 'description': '3-5 days of work'},
            {'name': 'size:large', 'color': 'f9d0c4', 'description': '1+ weeks of work'},
            {'name': 'ai-assisted', 'color': '7057ff', 'description': 'Work done with AI assistance'},
            {'name': 'ready-for-dev', 'color': '0e8a16', 'description': 'Ready for development'},
        ]

        for label in labels:
            cmd = ['api', '-X', 'POST', f'repos/{self.repo_name}/labels',
                   '-f', f'name={label["name"]}',
                   '-f', f'color={label["color"]}',
                   '-f', f'description={label["description"]}']
            self._run_gh_command(cmd)

    def create_github_project(self, project_name: str = "OSINT Framework Development") -> Optional[str]:
        """Create a GitHub Project (beta) for the repository."""
        print(f"📋 Creating GitHub Project: {project_name}")

        # Create project
        cmd = ['project', 'create', '--title', project_name, '--owner', '@me']
        project_output = self._run_gh_command(cmd)

        if not project_output:
            return None

        # Extract project number from URL
        project_number = project_output.split('/')[-1] if project_output else None

        if project_number:
            # Add custom fields
            self._setup_project_fields(project_number)

        return project_number

    def _setup_project_fields(self, project_number: str):
        """Set up custom fields for the GitHub Project."""
        print(f"⚙️  Setting up project fields for project {project_number}")

        # Add Status field with custom options
        status_options = ["Backlog", "Ready", "In Progress", "In Review", "Done"]

        # Add Priority field
        priority_options = ["High", "Medium", "Low"]

        # Add Size field
        size_options = ["Small", "Medium", "Large"]

        # Note: GitHub Projects v2 field management via CLI is limited
        # This would need to be done via GraphQL API for full automation
        print("   Custom fields need to be configured manually in the GitHub UI")
        print("   Recommended fields: Status, Priority, Size, Sprint")

    def parse_user_stories(self) -> List[Dict]:
        """Parse user stories from planning/stories directory."""
        print("📖 Parsing user stories...")

        stories_dir = self.project_root / 'planning' / 'stories'
        stories = []

        if not stories_dir.exists():
            print("Warning: No stories directory found")
            return stories

        for story_file in stories_dir.glob('S-*.md'):
            try:
                story = self._parse_story_file(story_file)
                if story:
                    stories.append(story)
            except Exception as e:
                print(f"Error parsing {story_file}: {e}")

        print(f"Found {len(stories)} user stories")
        return stories

    def _parse_story_file(self, file_path: Path) -> Optional[Dict]:
        """Parse a single user story markdown file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract title from filename or first heading
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem

        # Extract YAML frontmatter if present
        yaml_match = re.search(r'^```yaml\n(.*?)\n```', content, re.DOTALL | re.MULTILINE)
        metadata = {}
        if yaml_match:
            try:
                metadata = yaml.safe_load(yaml_match.group(1))
            except yaml.YAMLError:
                pass

        # Extract acceptance criteria
        acceptance_criteria = []
        ac_match = re.search(r'## Acceptance Criteria\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
        if ac_match:
            ac_text = ac_match.group(1).strip()
            acceptance_criteria = [line.strip('- ') for line in ac_text.split('\n') if line.strip().startswith('-')]

        return {
            'file': file_path.name,
            'title': title,
            'content': content,
            'metadata': metadata,
            'acceptance_criteria': acceptance_criteria,
            'labels': self._determine_labels(metadata, content),
            'priority': metadata.get('priority', 'medium'),
            'size': metadata.get('size', 'medium')
        }

    def _determine_labels(self, metadata: Dict, content: str) -> List[str]:
        """Determine appropriate labels for a story."""
        labels = ['ai-assisted']  # All issues are AI-assisted

        # Add type label
        if 'type' in metadata:
            labels.append(f"type:{metadata['type']}")
        else:
            labels.append('type:feature')  # Default for user stories

        # Add priority label
        if 'priority' in metadata:
            labels.append(f"priority:{metadata['priority']}")

        # Add size label
        if 'size' in metadata:
            labels.append(f"size:{metadata['size']}")

        return labels

    def create_issues_from_stories(self, stories: List[Dict], project_number: Optional[str] = None):
        """Create GitHub issues from parsed user stories."""
        print(f"🎫 Creating {len(stories)} issues from user stories...")

        created_issues = []

        for story in stories:
            issue_title = story['title']
            issue_body = self._format_issue_body(story)
            labels = ','.join(story['labels'])

            # Create issue
            cmd = ['issue', 'create',
                   '--title', issue_title,
                   '--body', issue_body,
                   '--label', labels]

            issue_url = self._run_gh_command(cmd)

            if issue_url:
                issue_number = issue_url.split('/')[-1] if issue_url else None
                created_issues.append({
                    'story': story['file'],
                    'issue_number': issue_number,
                    'url': issue_url
                })

                # Add to project if project exists
                if project_number and issue_number:
                    self._add_issue_to_project(project_number, issue_number)

        return created_issues

    def _format_issue_body(self, story: Dict) -> str:
        """Format the issue body from story content."""
        body_parts = []

        # Add story reference
        body_parts.append(f"**User Story:** {story['file']}")
        body_parts.append("")

        # Add story content (cleaned up)
        content = story['content']

        # Remove YAML frontmatter
        content = re.sub(r'^```yaml\n.*?\n```\n?', '', content, flags=re.DOTALL | re.MULTILINE)

        body_parts.append(content.strip())
        body_parts.append("")

        # Add metadata
        if story['acceptance_criteria']:
            body_parts.append("## Checklist")
            for criteria in story['acceptance_criteria']:
                body_parts.append(f"- [ ] {criteria}")
            body_parts.append("")

        # Add automation note
        body_parts.append("---")
        body_parts.append("*This issue was automatically created from a user story*")

        return '\n'.join(body_parts)

    def _add_issue_to_project(self, project_number: str, issue_number: str):
        """Add an issue to a GitHub Project."""
        # Note: This requires GraphQL API calls which are more complex
        # For now, we'll skip this and add them manually or via web interface
        pass

    def setup_branch_protection(self, branch: str = "main"):
        """Set up branch protection rules."""
        print(f"🛡️  Setting up branch protection for {branch}")

        protection_rules = {
            'required_status_checks': {
                'strict': True,
                'contexts': ['backend', 'e2e']  # From CI workflow
            },
            'enforce_admins': False,
            'required_pull_request_reviews': {
                'required_approving_review_count': 1,
                'dismiss_stale_reviews': True,
                'require_code_owner_reviews': False
            },
            'restrictions': None  # No restrictions on who can push
        }

        # GitHub CLI doesn't have direct branch protection commands
        # This would need to be done via API calls
        cmd = ['api', '-X', 'PUT', f'repos/{self.repo_name}/branches/{branch}/protection',
               '--input', '-']

        if not self.dry_run:
            # This would need the JSON payload piped to stdin
            print("   Branch protection setup requires manual configuration or API calls")

    def run_full_setup(self):
        """Run the complete GitHub project setup automation."""
        print(f"🚀 Starting GitHub automation for {self.repo_name}")
        print("=" * 60)

        try:
            # 1. Configure repository settings
            self.setup_repository_settings()

            # 2. Set up labels
            self.setup_labels()

            # 3. Create GitHub Project
            project_number = self.create_github_project()

            # 4. Parse user stories
            stories = self.parse_user_stories()

            # 5. Create issues from stories
            if stories:
                created_issues = self.create_issues_from_stories(stories, project_number)
                print(f"✅ Created {len(created_issues)} issues")

            # 6. Set up branch protection
            self.setup_branch_protection()

            print("=" * 60)
            print("🎉 GitHub automation completed successfully!")

            if project_number:
                print(f"📋 Project created: https://github.com/users/{self.repo_name.split('/')[0]}/projects/{project_number}")

        except Exception as e:
            print(f"❌ Error during automation: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Automate GitHub project setup')
    parser.add_argument('repo', help='Repository name (owner/repo)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--project-name', default='OSINT Framework Development',
                       help='Name for the GitHub Project')

    args = parser.parse_args()

    automation = GitHubProjectAutomation(args.repo, args.dry_run)
    automation.run_full_setup()


if __name__ == '__main__':
    main()
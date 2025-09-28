#!/usr/bin/env python3
"""
Bidirectional GitHub Projects <-> File System Sync
Enables hybrid planning workflow:
1. AI creates initial user stories in files
2. Client/team uses GitHub Projects GUI for planning
3. Changes sync back to files for next AI sprint
"""

import os
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import yaml
import re
from datetime import datetime

class GitHubProjectSync:
    """Bidirectional sync between GitHub Projects and planning files."""

    def __init__(self, repo_name: str, project_number: str = None, dry_run: bool = False):
        self.repo_name = repo_name
        self.project_number = project_number
        self.dry_run = dry_run
        self.project_root = Path.cwd()

        # Directories
        self.stories_dir = self.project_root / 'planning' / 'stories'
        self.sync_data_dir = self.project_root / '.github' / 'project-sync'

        # Ensure directories exist
        self.sync_data_dir.mkdir(parents=True, exist_ok=True)

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
            return None

    def _run_gh_json_command(self, cmd: List[str]) -> Optional[Dict]:
        """Run a GitHub CLI command and return JSON output."""
        output = self._run_gh_command(cmd)
        if output:
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON from: {output}")
        return None

    def get_project_items(self) -> List[Dict]:
        """Get all items from the GitHub Project."""
        print(f"📋 Fetching items from GitHub Project {self.project_number}")

        if not self.project_number:
            print("❌ No project number specified")
            return []

        # Use GraphQL to get project items with custom fields
        query = '''
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
                      body
                      state
                      labels(first: 20) {
                        nodes {
                          name
                        }
                      }
                      assignees(first: 5) {
                        nodes {
                          login
                        }
                      }
                      milestone {
                        title
                      }
                    }
                  }
                  fieldValues(first: 20) {
                    nodes {
                      ... on ProjectV2ItemFieldTextValue {
                        text
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                      }
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field {
                          ... on ProjectV2FieldCommon {
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
        '''

        owner = self.repo_name.split('/')[0]
        variables = {"owner": owner, "number": int(self.project_number)}

        cmd = ['api', 'graphql', '-f', f'query={query}', '-F', f'owner={owner}', '-F', f'number={self.project_number}']

        result = self._run_gh_json_command(cmd)

        if result and 'data' in result:
            items = result['data']['user']['projectV2']['items']['nodes']
            return self._process_project_items(items)

        return []

    def _process_project_items(self, items: List[Dict]) -> List[Dict]:
        """Process raw project items into a structured format."""
        processed = []

        for item in items:
            if not item.get('content'):
                continue

            content = item['content']

            # Extract custom field values
            custom_fields = {}
            for field_value in item.get('fieldValues', {}).get('nodes', []):
                field_name = field_value.get('field', {}).get('name', '')

                if 'text' in field_value:
                    custom_fields[field_name] = field_value['text']
                elif 'name' in field_value:
                    custom_fields[field_name] = field_value['name']

            processed_item = {
                'issue_number': content.get('number'),
                'title': content.get('title', ''),
                'body': content.get('body', ''),
                'state': content.get('state', ''),
                'labels': [label['name'] for label in content.get('labels', {}).get('nodes', [])],
                'assignees': [assignee['login'] for assignee in content.get('assignees', {}).get('nodes', [])],
                'milestone': content.get('milestone', {}).get('title') if content.get('milestone') else None,
                'custom_fields': custom_fields,
                'project_item_id': item['id']
            }

            processed.append(processed_item)

        return processed

    def extract_story_reference(self, issue_body: str) -> Optional[str]:
        """Extract user story file reference from issue body."""
        # Look for pattern like: **User Story File:** `planning/stories/S-001-example.md`
        match = re.search(r'\*\*User Story File:\*\*\s*`([^`]+)`', issue_body)
        if match:
            return match.group(1)

        # Look for pattern like: **User Story:** S-001-example.md
        match = re.search(r'\*\*User Story:\*\*\s*([^\n]+)', issue_body)
        if match:
            story_ref = match.group(1).strip()
            if story_ref.endswith('.md'):
                return f"planning/stories/{story_ref}"

        return None

    def sync_from_github_to_files(self) -> Dict[str, Any]:
        """Sync changes from GitHub Project back to user story files."""
        print("🔄 Syncing from GitHub Project to files...")

        project_items = self.get_project_items()
        sync_results = {
            'updated_files': [],
            'new_files': [],
            'errors': []
        }

        for item in project_items:
            try:
                story_file = self.extract_story_reference(item['body'])

                if story_file:
                    # Update existing story file
                    file_path = self.project_root / story_file
                    if file_path.exists():
                        self._update_story_file_from_issue(file_path, item)
                        sync_results['updated_files'].append(str(file_path))
                    else:
                        # Create new story file from issue
                        self._create_story_file_from_issue(file_path, item)
                        sync_results['new_files'].append(str(file_path))
                else:
                    # Issue without story reference - create new story
                    story_filename = self._generate_story_filename(item['title'])
                    file_path = self.stories_dir / f"{story_filename}.md"

                    if not file_path.exists():
                        self._create_story_file_from_issue(file_path, item)
                        sync_results['new_files'].append(str(file_path))

            except Exception as e:
                sync_results['errors'].append(f"Error processing issue #{item['issue_number']}: {e}")

        # Save sync metadata
        self._save_sync_metadata(project_items)

        return sync_results

    def _update_story_file_from_issue(self, file_path: Path, issue: Dict):
        """Update an existing story file with issue changes."""
        if self.dry_run:
            print(f"[DRY RUN] Would update {file_path}")
            return

        # Read current file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update YAML frontmatter with GitHub data
        updated_content = self._inject_github_metadata(content, issue)

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        print(f"✅ Updated {file_path}")

    def _create_story_file_from_issue(self, file_path: Path, issue: Dict):
        """Create a new story file from a GitHub issue."""
        if self.dry_run:
            print(f"[DRY RUN] Would create {file_path}")
            return

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate story content
        story_content = self._generate_story_from_issue(issue)

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(story_content)

        print(f"✅ Created {file_path}")

    def _inject_github_metadata(self, content: str, issue: Dict) -> str:
        """Inject GitHub metadata into existing story content."""
        metadata = self._extract_github_metadata(issue)

        # Check if YAML frontmatter exists
        yaml_match = re.search(r'^```yaml\n(.*?)\n```', content, re.DOTALL | re.MULTILINE)

        if yaml_match:
            # Update existing YAML
            try:
                existing_yaml = yaml.safe_load(yaml_match.group(1))
                existing_yaml.update(metadata)

                new_yaml = yaml.dump(existing_yaml, default_flow_style=False, sort_keys=False)
                updated_content = re.sub(
                    r'^```yaml\n.*?\n```',
                    f'```yaml\n{new_yaml}```',
                    content,
                    flags=re.DOTALL | re.MULTILINE
                )
                return updated_content
            except yaml.YAMLError:
                pass

        # Add new YAML frontmatter at the beginning
        yaml_block = f"```yaml\n{yaml.dump(metadata, default_flow_style=False, sort_keys=False)}```\n\n"
        return yaml_block + content

    def _extract_github_metadata(self, issue: Dict) -> Dict:
        """Extract metadata from GitHub issue for YAML frontmatter."""
        metadata = {
            'github': {
                'issue_number': issue['issue_number'],
                'state': issue['state'],
                'last_synced': datetime.now().isoformat()
            }
        }

        if issue['assignees']:
            metadata['github']['assignees'] = issue['assignees']

        if issue['milestone']:
            metadata['github']['milestone'] = issue['milestone']

        # Extract priority and size from labels
        for label in issue['labels']:
            if label.startswith('priority:'):
                metadata['priority'] = label.split(':', 1)[1]
            elif label.startswith('size:'):
                metadata['size'] = label.split(':', 1)[1]
            elif label.startswith('type:'):
                metadata['type'] = label.split(':', 1)[1]

        # Add custom fields
        if issue['custom_fields']:
            metadata['github']['custom_fields'] = issue['custom_fields']

        return metadata

    def _generate_story_from_issue(self, issue: Dict) -> str:
        """Generate a complete user story file from a GitHub issue."""
        metadata = self._extract_github_metadata(issue)

        # Generate YAML frontmatter
        yaml_block = f"```yaml\n{yaml.dump(metadata, default_flow_style=False, sort_keys=False)}```\n\n"

        # Generate story content
        content_parts = [
            yaml_block,
            f"# {issue['title']}\n",
            "## User Story\n",
            f"{issue['body']}\n",
            "## Acceptance Criteria\n",
            "- [ ] TODO: Define acceptance criteria\n",
            "## Implementation Notes\n",
            "*Add implementation details here*\n",
            "## Definition of Done\n",
            "- [ ] Feature implemented and tested\n",
            "- [ ] Documentation updated\n",
            "- [ ] Code reviewed and approved\n",
            "---\n",
            f"*Synced from GitHub Issue #{issue['issue_number']}*\n"
        ]

        return '\n'.join(content_parts)

    def _generate_story_filename(self, title: str) -> str:
        """Generate a story filename from issue title."""
        # Get next story number
        existing_stories = list(self.stories_dir.glob('S-*.md'))
        story_numbers = []

        for story in existing_stories:
            match = re.match(r'S-(\d+)', story.stem)
            if match:
                story_numbers.append(int(match.group(1)))

        next_number = max(story_numbers, default=0) + 1

        # Generate clean filename
        clean_title = re.sub(r'[^\w\s-]', '', title.lower())
        clean_title = re.sub(r'[-\s]+', '-', clean_title)

        return f"S-{next_number:03d}-{clean_title[:40]}"

    def _save_sync_metadata(self, project_items: List[Dict]):
        """Save sync metadata for tracking changes."""
        metadata = {
            'last_sync': datetime.now().isoformat(),
            'project_number': self.project_number,
            'items_count': len(project_items),
            'items': {item['issue_number']: {
                'title': item['title'],
                'state': item['state'],
                'labels': item['labels']
            } for item in project_items}
        }

        metadata_file = self.sync_data_dir / 'last_sync.json'

        if not self.dry_run:
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

    def sync_from_files_to_github(self) -> Dict[str, Any]:
        """Sync changes from user story files to GitHub Project."""
        print("🔄 Syncing from files to GitHub Project...")

        # This would update GitHub issues based on story file changes
        # Implementation would involve:
        # 1. Reading all story files
        # 2. Checking for changes since last sync
        # 3. Updating issue titles, bodies, labels based on file content
        # 4. Creating new issues for new story files

        return {
            'updated_issues': [],
            'new_issues': [],
            'errors': ['Not yet implemented - use setup-github-project.sh for files -> GitHub']
        }

    def show_status(self):
        """Show current sync status."""
        print("📊 GitHub Project Sync Status")
        print("=" * 40)

        # Check for sync metadata
        metadata_file = self.sync_data_dir / 'last_sync.json'
        if metadata_file.exists():
            with open(metadata_file) as f:
                metadata = json.load(f)

            print(f"Last sync: {metadata['last_sync']}")
            print(f"Project: {metadata['project_number']}")
            print(f"Items synced: {metadata['items_count']}")
        else:
            print("No sync data found - never synced")

        # Check story files
        if self.stories_dir.exists():
            story_files = list(self.stories_dir.glob('S-*.md'))
            print(f"Story files: {len(story_files)}")
        else:
            print("No stories directory found")


def main():
    parser = argparse.ArgumentParser(description='Sync GitHub Projects with planning files')
    parser.add_argument('repo', help='Repository name (owner/repo)')
    parser.add_argument('--project-number', help='GitHub Project number')
    parser.add_argument('--sync-to-files', action='store_true',
                       help='Sync from GitHub Project to files')
    parser.add_argument('--sync-to-github', action='store_true',
                       help='Sync from files to GitHub Project')
    parser.add_argument('--status', action='store_true',
                       help='Show sync status')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')

    args = parser.parse_args()

    # Auto-detect project number if not provided
    project_number = args.project_number
    if not project_number:
        project_file = Path('.github-project-number')
        if project_file.exists():
            project_number = project_file.read_text().strip()

    sync = GitHubProjectSync(args.repo, project_number, args.dry_run)

    if args.status:
        sync.show_status()
    elif args.sync_to_files:
        results = sync.sync_from_github_to_files()
        print(f"\n✅ Sync complete: {len(results['updated_files'])} updated, {len(results['new_files'])} new")
        if results['errors']:
            print(f"❌ Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   {error}")
    elif args.sync_to_github:
        results = sync.sync_from_files_to_github()
        print(f"\n✅ Sync complete: {len(results['updated_issues'])} updated, {len(results['new_issues'])} new")
        if results['errors']:
            print(f"❌ Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   {error}")
    else:
        print("Please specify --sync-to-files, --sync-to-github, or --status")
        sys.exit(1)


if __name__ == '__main__':
    main()
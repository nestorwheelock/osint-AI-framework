#!/usr/bin/env python3
"""
Fix YAML formatting issues in story files.
Addresses missing newlines before YAML keys in AI coding briefs.
"""

import re
from pathlib import Path


def fix_yaml_formatting():
    """Fix YAML formatting issues in all story files."""
    stories_dir = Path("planning/stories")
    fixed_count = 0

    for story_file in stories_dir.glob("S-*.md"):
        content = story_file.read_text()

        # Fix the specific YAML formatting issue
        # Pattern: 'something'  security: (missing newline)
        patterns = [
            (r'"([^"]+)"  (security:)', r'"\1"\n  \2'),
            (r'"([^"]+)"  (dependencies:)', r'"\1"\n  \2'),
            (r'"([^"]+)"  (testing:)', r'"\1"\n  \2'),
            (r'"([^"]+)"  (database:)', r'"\1"\n  \2'),
        ]

        new_content = content
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, new_content)

        if new_content != content:
            story_file.write_text(new_content)
            print(f"Fixed YAML formatting in {story_file.name}")
            fixed_count += 1

    print(f"Fixed {fixed_count} files")
    return fixed_count


if __name__ == "__main__":
    fix_yaml_formatting()

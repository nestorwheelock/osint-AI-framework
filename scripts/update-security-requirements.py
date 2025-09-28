#!/usr/bin/env python3
"""
Script to update security requirements in all user stories and task files.
Replaces weak security requirements with strong no-attribution requirements.
"""

import os
import re
from pathlib import Path

# Old security pattern to replace
OLD_SECURITY_PATTERN = r'(\s+security:\s*\n\s+- "NEVER include author attribution in commits or code"\s*\n\s+- "Do not reference AI assistance in any deliverables")'

# New strong security requirements
NEW_SECURITY_REQUIREMENTS = '''  security:
    - "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"
    - "🚨 CRITICAL: NEVER use phrases like 'Generated with Claude', 'Co-Authored-By: Claude', etc."
    - "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"
    - "🚨 CRITICAL: This is a SECURITY REQUIREMENT - violations will be automatically detected and removed"'''

def update_file_security_requirements(file_path: Path) -> bool:
    """Update security requirements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Replace old security requirements with new ones
        content = re.sub(
            OLD_SECURITY_PATTERN,
            NEW_SECURITY_REQUIREMENTS,
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        # Also update any standalone instances
        content = re.sub(
            r'- "NEVER include author attribution in commits or code"',
            '- "🚨 CRITICAL: NEVER include any AI, Claude, or assistant attribution anywhere"',
            content
        )

        content = re.sub(
            r'- "Do not reference AI assistance in any deliverables"',
            '- "🚨 CRITICAL: Do not reference AI assistance in code, comments, commits, or any deliverables"',
            content
        )

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"⏭️  No changes needed: {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Update security requirements in all planning files."""
    updated_files = 0
    total_files = 0

    # Directories to scan
    scan_dirs = ['planning/stories', 'planning/tasks']

    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            print(f"⚠️  Directory not found: {scan_dir}")
            continue

        print(f"\n🔍 Scanning {scan_dir}/")

        for file_path in Path(scan_dir).glob('*.md'):
            total_files += 1
            if update_file_security_requirements(file_path):
                updated_files += 1

    print(f"\n📊 Summary:")
    print(f"   Files scanned: {total_files}")
    print(f"   Files updated: {updated_files}")

    if updated_files > 0:
        print(f"\n✅ Security requirements strengthened in {updated_files} files!")
        print("   All files now have explicit no-attribution requirements.")
    else:
        print(f"\n✅ All files already have up-to-date security requirements.")

if __name__ == '__main__':
    main()
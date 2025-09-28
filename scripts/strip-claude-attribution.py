#!/usr/bin/env python3
"""
Script to detect and strip Claude attribution from all files in the repository.
This ensures no AI attribution is present in the codebase for security/compliance reasons.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Patterns to detect Claude attribution
CLAUDE_PATTERNS = [
    r'🤖 Generated with \[Claude Code\].*',
    r'Co-Authored-By: Claude <.*>',
    r'Built with Claude Code.*',
    r'Generated with Claude.*',
    r'Co-authored-by: Claude.*',
    r'@claude\s+authored.*',
    r'Created by Claude.*',
    r'Developed with Claude.*',
    r'AI-assisted by Claude.*',
    # More subtle patterns
    r'.*[Tt]hanks to Claude.*',
    r'.*[Ww]ith help from Claude.*',
    r'.*[Uu]sing Claude.*for development.*',
]

# File patterns to exclude from scanning
EXCLUDE_PATTERNS = [
    r'\.git/',
    r'__pycache__/',
    r'node_modules/',
    r'\.venv/',
    r'\.pytest_cache/',
    r'.*\.egg-info/',
    r'claude-prompts-used-for-planning\.md$',  # This file is specifically about Claude prompts
    r'CLAUDE\.md$',  # Configuration file that mentions Claude by design
    r'docs/devops/github-ai-integration\.md$',  # Documentation about Claude integration
]

def should_exclude_file(file_path: str) -> bool:
    """Check if file should be excluded from scanning."""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False

def is_security_documentation(line: str) -> bool:
    """Check if line is security documentation telling people what NOT to do."""
    security_keywords = [
        'CRITICAL:', 'NEVER use phrases like', 'security:', 'SECURITY REQUIREMENT',
        'NEVER include any', 'prohibition', 'violations will be', 'automatically detected'
    ]
    return any(keyword in line for keyword in security_keywords)

def is_detection_code(line: str, file_path: Path) -> bool:
    """Check if line is part of detection/testing code that legitimately contains patterns."""
    # Files that legitimately need to reference these patterns
    detection_files = [
        'strip-claude-attribution.py', 'test_documentation_completeness.py',
        'pre-commit', 'no-ai-attribution.yml'
    ]

    if any(detection_file in str(file_path) for detection_file in detection_files):
        return True

    # Lines that are clearly detection code
    detection_indicators = [
        'grep -', 'pattern', 'CLAUDE_PATTERNS', 'violations', 'detect',
        'strip', 'test_', 'assert', 'should_fail'
    ]
    return any(indicator in line.lower() for indicator in detection_indicators)

def scan_file_for_attribution(file_path: Path) -> List[Tuple[int, str]]:
    """Scan a single file for Claude attribution patterns."""
    violations = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Skip security documentation and detection code
                if is_security_documentation(line) or is_detection_code(line, file_path):
                    continue

                for pattern in CLAUDE_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append((line_num, line.strip()))
    except Exception as e:
        print(f"Warning: Could not scan {file_path}: {e}")

    return violations

def strip_attribution_from_file(file_path: Path, dry_run: bool = True) -> bool:
    """Remove Claude attribution from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Remove Claude attribution patterns
        for pattern in CLAUDE_PATTERNS:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)

        # Clean up multiple consecutive newlines left by removals
        content = re.sub(r'\n\n\n+', '\n\n', content)

        if content != original_content:
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Cleaned: {file_path}")
            else:
                print(f"🔍 Would clean: {file_path}")
            return True

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")

    return False

def scan_repository(repo_path: Path, fix: bool = False, dry_run: bool = True) -> Tuple[int, int]:
    """Scan entire repository for Claude attribution."""
    total_files_scanned = 0
    files_with_violations = 0
    total_violations = 0

    print(f"🔍 Scanning repository: {repo_path}")
    print(f"Mode: {'FIX' if fix else 'SCAN ONLY'} {'(DRY RUN)' if dry_run else ''}")
    print("-" * 60)

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(repo_path)

            if should_exclude_file(str(relative_path)):
                continue

            # Only scan text files
            if not is_text_file(file_path):
                continue

            total_files_scanned += 1
            violations = scan_file_for_attribution(file_path)

            if violations:
                files_with_violations += 1
                total_violations += len(violations)

                print(f"\n⚠️  VIOLATIONS in {relative_path}:")
                for line_num, line in violations:
                    print(f"   Line {line_num}: {line}")

                if fix:
                    strip_attribution_from_file(file_path, dry_run)

    print("\n" + "=" * 60)
    print(f"📊 SCAN RESULTS:")
    print(f"   Files scanned: {total_files_scanned}")
    print(f"   Files with violations: {files_with_violations}")
    print(f"   Total violations: {total_violations}")

    if total_violations > 0:
        print(f"\n❌ COMPLIANCE VIOLATION: {total_violations} Claude attribution(s) found!")
        if not fix:
            print("   Run with --fix to automatically remove them.")
        return 1, total_violations
    else:
        print(f"\n✅ COMPLIANCE OK: No Claude attribution found.")
        return 0, 0

def is_text_file(file_path: Path) -> bool:
    """Check if file is likely a text file."""
    text_extensions = {
        '.py', '.md', '.txt', '.yml', '.yaml', '.json', '.js', '.ts',
        '.jsx', '.tsx', '.html', '.css', '.scss', '.sh', '.bash',
        '.sql', '.env', '.toml', '.ini', '.cfg', '.conf'
    }

    if file_path.suffix.lower() in text_extensions:
        return True

    # Check for files without extensions that might be text
    if not file_path.suffix:
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return chunk.isascii() or b'\0' not in chunk[:500]
        except:
            return False

    return False

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect and strip Claude attribution from repository files"
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Repository path to scan (default: current directory)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Actually remove attribution (default: scan only)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Show what would be changed without making changes'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Actually make changes (disables dry-run)'
    )

    args = parser.parse_args()

    # Override dry_run if force is specified
    if args.force:
        args.dry_run = False

    repo_path = Path(args.path).resolve()

    if not repo_path.exists():
        print(f"❌ Error: Path {repo_path} does not exist")
        sys.exit(1)

    exit_code, violation_count = scan_repository(
        repo_path,
        fix=args.fix,
        dry_run=args.dry_run
    )

    sys.exit(exit_code)

if __name__ == '__main__':
    main()
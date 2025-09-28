#!/usr/bin/env python3
"""
Pre-commit hook to detect and remove emojis from code and documentation.
Enforces professional code standards by preventing emoji usage.
"""

import re
import sys
import argparse
from pathlib import Path

# Comprehensive emoji regex pattern
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002500-\U00002BEF"  # chinese char
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u2640-\u2642"
    "\u2600-\u2B55"
    "\u200d"
    "\u23cf"
    "\u23e9"
    "\u231a"
    "\ufe0f"  # dingbats
    "\u3030"
    "]+",
    flags=re.UNICODE,
)

# Professional text replacements for common emojis
EMOJI_REPLACEMENTS = {
    "[SUCCESS]": "[SUCCESS]",
    "[FAIL]": "[FAIL]",
    "[WARNING]": "[WARNING]",
    "[DEPLOY]": "[DEPLOY]",
    "[DOCS]": "[DOCS]",
    "[SEARCH]": "[SEARCH]",
    "[IDEA]": "[IDEA]",
    "[TARGET]": "[TARGET]",
    "[METRICS]": "[METRICS]",
    "[CONFIG]": "[CONFIG]",
    "[FAST]": "[FAST]",
    "[ACHIEVEMENT]": "[ACHIEVEMENT]",
    "[COMPLETE]": "[COMPLETE]",
    "[AI]": "[AI]",
    "[GROWTH]": "[GROWTH]",
    "[SECURE]": "[SECURE]",
    "[FEATURE]": "[FEATURE]",
    "[CRITICAL]": "[CRITICAL]",
    "[INFO]": "[INFO]",
    "[HOT]": "[HOT]",
    "[PERFECT]": "[PERFECT]",
    "[APPROVED]": "[APPROVED]",
    "[REJECTED]": "[REJECTED]",
    "[TOOLS]": "[TOOLS]",
    "[PACKAGE]": "[PACKAGE]",
    "[WEB]": "[WEB]",
    "[SAVE]": "[SAVE]",
    "[FILES]": "[FILES]",
    "[SYNC]": "[SYNC]",
    "[TASKS]": "[TASKS]",
}


def detect_emojis(text):
    """Detect emoji characters in text and return their positions."""
    matches = []
    for match in EMOJI_PATTERN.finditer(text):
        matches.append((match.start(), match.end(), match.group()))
    return matches


def replace_emojis(text, fix_mode=False):
    """Replace emojis with professional text alternatives."""
    if not fix_mode:
        return text, detect_emojis(text)

    # First try specific replacements
    for emoji, replacement in EMOJI_REPLACEMENTS.items():
        text = text.replace(emoji, replacement)

    # Then remove any remaining emojis
    text = EMOJI_PATTERN.sub("", text)

    return text, []


def check_file(file_path, fix_mode=False):
    """Check a single file for emojis."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return True  # Skip binary files or missing files

    original_content = content
    modified_content, emoji_matches = replace_emojis(content, fix_mode)

    if emoji_matches:
        print(f"[EMOJI VIOLATION] {file_path}")
        for start, end, emoji in emoji_matches:
            line_num = content[:start].count("\n") + 1
            print(f"  Line {line_num}: Found emoji '{emoji}'")

        if fix_mode:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(modified_content)
            print(f"  [FIXED] Emojis replaced with professional alternatives")
        else:
            print(f"  [FAIL] Use --fix to automatically replace emojis")

        return False

    elif fix_mode and modified_content != original_content:
        # Content was modified (emojis were replaced)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        print(f"[FIXED] {file_path} - Emojis replaced with professional text")
        return False  # Return False to indicate file was modified

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Check files for emoji usage and enforce professional standards"
    )
    parser.add_argument("files", nargs="*", help="Files to check")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically replace emojis with professional alternatives",
    )
    args = parser.parse_args()

    if not args.files:
        print("No files specified")
        return 0

    failed_files = []

    for file_path in args.files:
        if not Path(file_path).exists():
            continue

        # Skip certain file types
        if file_path.endswith(
            (
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".ico",
                ".svg",
                ".pdf",
                ".zip",
                ".tar",
                ".gz",
                ".exe",
                ".bin",
            )
        ):
            continue

        if not check_file(file_path, args.fix):
            failed_files.append(file_path)

    if failed_files:
        print(f"\n[SUMMARY] {len(failed_files)} files contain emojis")
        if not args.fix:
            print(
                "Run with --fix to automatically replace emojis with professional alternatives"
            )
            print("\nProfessional code standards require emoji-free deliverables for:")
            print("- Enterprise compatibility")
            print("- LaTeX/PDF generation")
            print("- Accessibility compliance")
            print("- Professional appearance")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

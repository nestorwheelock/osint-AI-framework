#!/usr/bin/env python3
"""
Clean markdown file for LaTeX PDF generation by removing emojis and fixing formatting.
"""

import re
import sys
from pathlib import Path


def clean_markdown_for_latex(content):
    """Remove emojis and LaTeX-incompatible characters from markdown content."""

    # Remove emoji characters
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
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

    content = emoji_pattern.sub("", content)

    # Replace common emoji with text equivalents
    replacements = {
        "[SUCCESS]": "[]",
        "[FAIL]": "[]",
        "[WARNING]": "[WARNING]",
        "[DEPLOY]": "[ROCKET]",
        "[DOCS]": "[DOCUMENT]",
        "[SEARCH]": "[SEARCH]",
        "[IDEA]": "[IDEA]",
        "[TARGET]": "[TARGET]",
        "[METRICS]": "[CHART]",
        "[CONFIG]": "[TOOL]",
        "[FAST]": "[LIGHTNING]",
        "[ACHIEVEMENT]": "[TROPHY]",
        "[COMPLETE]": "[CELEBRATION]",
        "[AI]": "[ROBOT]",
        "[GROWTH]": "[GRAPH]",
        "[SECURE]": "[LOCK]",
        "[FEATURE]": "[STAR]",
    }

    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)

    # Clean up any remaining unicode issues
    content = content.encode("ascii", "ignore").decode("ascii")

    return content


def main():
    if len(sys.argv) != 3:
        print("Usage: python clean-markdown-for-pdf.py input.md output.md")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)

    content = input_file.read_text(encoding="utf-8")
    cleaned_content = clean_markdown_for_latex(content)

    output_file.write_text(cleaned_content, encoding="utf-8")
    print(f"Cleaned markdown saved to {output_file}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive Development Session Logger

Captures the complete development process including AI interactions, reasoning,
decisions, code changes, and outcomes. Creates a detailed audit trail for
template extraction and future project learning.

Features:
- Real-time session logging with timestamps
- AI response and reasoning capture
- Code change tracking with git integration
- Decision point documentation
- Error and resolution tracking
- Template-ready log format
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib
import difflib


class DevelopmentLogger:
    """Comprehensive development session logger."""

    def __init__(self, project_root: str = None, session_name: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Session identification
        self.session_name = (
            session_name or f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        self.session_id = hashlib.md5(self.session_name.encode()).hexdigest()[:8]

        # Log files
        self.session_log = self.logs_dir / f"{self.session_name}.md"
        self.raw_log = self.logs_dir / f"{self.session_name}-raw.json"
        self.milestone_log = (
            self.logs_dir / f"milestone-{datetime.now().strftime('%Y%m%d')}.md"
        )

        # Session state
        self.session_start = datetime.now(timezone.utc)
        self.entries = []
        self.current_context = {}
        self.git_baseline = self._get_git_state()

        # Initialize session
        self._initialize_session()

    def _get_git_state(self) -> Dict:
        """Get current git state for change tracking."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            commit_hash = result.stdout.strip()

            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )
            status = result.stdout.strip()

            return {
                "commit_hash": commit_hash,
                "status": status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except subprocess.CalledProcessError:
            return {"error": "Not in git repository"}

    def _initialize_session(self):
        """Initialize logging session with metadata."""
        session_metadata = {
            "session_name": self.session_name,
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "project_root": str(self.project_root),
            "git_baseline": self.git_baseline,
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cwd": os.getcwd(),
            },
        }

        self.log_entry(
            "session_start", "Development session initialized", session_metadata
        )

        # Write session header
        header = f"""# Development Session Log: {self.session_name}

**Session ID**: {self.session_id}
**Start Time**: {self.session_start.strftime('%Y-%m-%d %H:%M:%S UTC')}
**Project**: {self.project_root.name}
**Git Baseline**: {self.git_baseline.get('commit_hash', 'N/A')[:8]}

## Session Overview

This log captures the complete development process including AI interactions,
reasoning, decisions, code changes, and outcomes for template extraction and
future project learning.

---

## Timeline

"""
        self.session_log.write_text(header)

    def log_entry(
        self,
        entry_type: str,
        title: str,
        data: Any = None,
        ai_response: str = None,
        reasoning: str = None,
    ):
        """Log a development entry with full context."""
        timestamp = datetime.now(timezone.utc)

        entry = {
            "timestamp": timestamp.isoformat(),
            "entry_type": entry_type,
            "title": title,
            "data": data,
            "ai_response": ai_response,
            "reasoning": reasoning,
            "context": self.current_context.copy(),
            "git_state": self._get_git_state(),
        }

        self.entries.append(entry)
        self._append_to_session_log(entry)
        self._update_raw_log()

    def _append_to_session_log(self, entry: Dict):
        """Append formatted entry to session log."""
        timestamp = datetime.fromisoformat(entry["timestamp"])
        time_str = timestamp.strftime("%H:%M:%S")

        # Format entry based on type
        if entry["entry_type"] == "user_input":
            formatted_entry = f"""
### {time_str} -  User Input: {entry["title"]}

{entry["data"]["message"]}
"""

        elif entry["entry_type"] == "ai_response":
            formatted_entry = f"""
### {time_str} -  AI Response: {entry["title"]}

**Reasoning**: {entry.get("reasoning", "N/A")}

**Response**:
{entry.get("ai_response", "N/A")}

**Actions Taken**:
{chr(10).join([f"- {action}" for action in entry.get("data", {}).get("actions", [])])}
"""

        elif entry["entry_type"] == "code_change":
            formatted_entry = f"""
### {time_str} -  Code Change: {entry["title"]}

**Files Modified**: {', '.join(entry.get("data", {}).get("files", []))}
**Git Status**: {entry.get("git_state", {}).get("status", "N/A")}

**Changes**:
```
{entry.get("data", {}).get("diff", "No diff available")}
```
"""

        elif entry["entry_type"] == "decision_point":
            formatted_entry = f"""
### {time_str} -  Decision Point: {entry["title"]}

**Context**: {entry.get("data", {}).get("context", "N/A")}
**Options Considered**:
{chr(10).join([f"- {option}" for option in entry.get("data", {}).get("options", [])])}
**Decision**: {entry.get("data", {}).get("decision", "N/A")}
**Rationale**: {entry.get("reasoning", "N/A")}
"""

        elif entry["entry_type"] == "error":
            formatted_entry = f"""
### {time_str} -  Error: {entry["title"]}

**Error**: {entry.get("data", {}).get("error", "N/A")}
**Resolution**: {entry.get("data", {}).get("resolution", "N/A")}
**Lessons Learned**: {entry.get("reasoning", "N/A")}
"""

        elif entry["entry_type"] == "milestone":
            formatted_entry = f"""
### {time_str} -  Milestone: {entry["title"]}

**Achievement**: {entry.get("data", {}).get("achievement", "N/A")}
**Metrics**: {json.dumps(entry.get("data", {}).get("metrics", {}), indent=2)}
**Next Steps**: {entry.get("data", {}).get("next_steps", "N/A")}
"""

        else:
            formatted_entry = f"""
### {time_str} -  {entry["entry_type"].title()}: {entry["title"]}

{json.dumps(entry.get("data", {}), indent=2)}
"""

        # Append to session log
        with open(self.session_log, "a") as f:
            f.write(formatted_entry)

    def _update_raw_log(self):
        """Update raw JSON log with all entries."""
        raw_data = {
            "session_metadata": {
                "session_name": self.session_name,
                "session_id": self.session_id,
                "start_time": self.session_start.isoformat(),
                "project_root": str(self.project_root),
            },
            "entries": self.entries,
        }

        with open(self.raw_log, "w") as f:
            json.dump(raw_data, f, indent=2)

    def log_user_input(self, message: str, context: Dict = None):
        """Log user input with context."""
        if context:
            self.current_context.update(context)

        self.log_entry("user_input", "User Request", {"message": message})

    def log_ai_response(
        self, title: str, response: str, reasoning: str, actions: List[str]
    ):
        """Log AI response with reasoning and actions."""
        self.log_entry("ai_response", title, {"actions": actions}, response, reasoning)

    def log_code_change(self, files: List[str], description: str):
        """Log code changes with git diff."""
        try:
            # Get git diff for changed files
            result = subprocess.run(
                ["git", "diff", "--no-index", "/dev/null"] + files,
                capture_output=True,
                text=True,
            )
            diff = result.stdout

        except subprocess.CalledProcessError:
            diff = "Could not generate diff"

        self.log_entry(
            "code_change",
            description,
            {"files": files, "diff": diff[:2000]},  # Limit diff size
        )

    def log_decision_point(
        self,
        title: str,
        context: str,
        options: List[str],
        decision: str,
        rationale: str,
    ):
        """Log decision points with full reasoning."""
        self.log_entry(
            "decision_point",
            title,
            {"context": context, "options": options, "decision": decision},
            reasoning=rationale,
        )

    def log_error(self, title: str, error: str, resolution: str, lessons_learned: str):
        """Log errors and their resolutions."""
        self.log_entry(
            "error",
            title,
            {"error": error, "resolution": resolution},
            reasoning=lessons_learned,
        )

    def log_milestone(
        self, title: str, achievement: str, metrics: Dict, next_steps: str
    ):
        """Log milestone achievements."""
        self.log_entry(
            "milestone",
            title,
            {
                "achievement": achievement,
                "metrics": metrics,
                "next_steps": next_steps,
                "commit_required": True,  # MANDATORY: Every milestone requires commit
            },
        )

        # Also update milestone log
        self._update_milestone_log(title, achievement, metrics)

        # Log development workflow mandate
        self.log_entry(
            "workflow_reminder",
            "Incremental Commit Protocol",
            {
                "mandate": "DEVELOPMENT WORKFLOW MANDATE",
                "description": "After each task with working tests:",
                "steps": [
                    "1. Run all tests to verify functionality",
                    "2. Git add modified files",
                    "3. Git commit with descriptive message",
                    "4. Git push to remote repository",
                    "5. Update kanban board to sync project status",
                ],
                "rationale": "Ensures incremental progress is preserved and trackable with live project status",
            },
        )

    def _update_milestone_log(self, title: str, achievement: str, metrics: Dict):
        """Update the milestone-specific log."""
        milestone_entry = f"""
## {datetime.now().strftime('%H:%M:%S')} - {title}

**Achievement**: {achievement}
**Session**: {self.session_name}

**Metrics**:
{chr(10).join([f"- {k}: {v}" for k, v in metrics.items()])}

---
"""

        # Append or create milestone log
        if self.milestone_log.exists():
            with open(self.milestone_log, "a") as f:
                f.write(milestone_entry)
        else:
            header = f"""# Milestone Log - {datetime.now().strftime('%Y-%m-%d')}

Daily milestone and achievement tracking for template extraction and project learning.

---
"""
            with open(self.milestone_log, "w") as f:
                f.write(header + milestone_entry)

    def finalize_session(
        self, summary: str, outcomes: List[str], lessons_learned: List[str]
    ):
        """Finalize logging session with summary."""
        session_end = datetime.now(timezone.utc)
        duration = session_end - self.session_start

        final_git_state = self._get_git_state()

        summary_data = {
            "summary": summary,
            "outcomes": outcomes,
            "lessons_learned": lessons_learned,
            "duration_minutes": duration.total_seconds() / 60,
            "total_entries": len(self.entries),
            "git_changes": {"baseline": self.git_baseline, "final": final_git_state},
        }

        self.log_entry("session_end", "Development session completed", summary_data)

        # Add session summary to log
        summary_section = f"""

---

## Session Summary

**Duration**: {duration.total_seconds() / 60:.1f} minutes
**Total Entries**: {len(self.entries)}
**Outcomes**:
{chr(10).join([f"- {outcome}" for outcome in outcomes])}

**Lessons Learned**:
{chr(10).join([f"- {lesson}" for lesson in lessons_learned])}

**Summary**: {summary}

**Final Git State**:
- Commit: {final_git_state.get('commit_hash', 'N/A')[:8]}
- Status: {final_git_state.get('status', 'Clean') or 'Clean'}

---

*Session logged for template extraction and future project learning*
"""

        with open(self.session_log, "a") as f:
            f.write(summary_section)

        print(f" Session logged to: {self.session_log}")
        print(f" Raw data saved to: {self.raw_log}")
        print(f" Milestones logged to: {self.milestone_log}")

    def get_session_stats(self) -> Dict:
        """Get current session statistics."""
        entry_types = {}
        for entry in self.entries:
            entry_type = entry["entry_type"]
            entry_types[entry_type] = entry_types.get(entry_type, 0) + 1

        duration = datetime.now(timezone.utc) - self.session_start

        return {
            "session_name": self.session_name,
            "duration_minutes": duration.total_seconds() / 60,
            "total_entries": len(self.entries),
            "entry_types": entry_types,
            "current_context": self.current_context,
        }


# CLI interface and utility functions
def create_session_logger(session_name: str = None) -> DevelopmentLogger:
    """Create a new development session logger."""
    return DevelopmentLogger(session_name=session_name)


def main():
    """CLI interface for development logging."""
    import argparse

    parser = argparse.ArgumentParser(description="Development Session Logger")
    parser.add_argument(
        "--new-session", metavar="NAME", help="Start new logging session"
    )
    parser.add_argument(
        "--log-milestone",
        nargs=3,
        metavar=("TITLE", "ACHIEVEMENT", "METRICS"),
        help="Log milestone achievement",
    )
    parser.add_argument(
        "--session-stats", action="store_true", help="Show current session statistics"
    )

    args = parser.parse_args()

    if args.new_session:
        logger = create_session_logger(args.new_session)
        print(f" Started logging session: {args.new_session}")
        print(f"   Session ID: {logger.session_id}")
        print(f"   Log file: {logger.session_log}")

    elif args.log_milestone:
        title, achievement, metrics_str = args.log_milestone
        try:
            metrics = json.loads(metrics_str)
        except json.JSONDecodeError:
            metrics = {"description": metrics_str}

        logger = DevelopmentLogger()  # Use existing session
        logger.log_milestone(title, achievement, metrics, "Continuing development")
        print(f" Logged milestone: {title}")

    elif args.session_stats:
        logger = DevelopmentLogger()  # Use existing session
        stats = logger.get_session_stats()
        print(f" Session Statistics:")
        print(f"   Duration: {stats['duration_minutes']:.1f} minutes")
        print(f"   Total entries: {stats['total_entries']}")
        print(f"   Entry types: {stats['entry_types']}")

    else:
        print("Development Logger - Comprehensive session tracking")
        print("Usage examples:")
        print("  --new-session 'sprint-1-completion'")
        print(
            "  --log-milestone 'Sprint 1 Complete' 'All tests passing' '{\"tests\": 28}'"
        )
        print("  --session-stats")


if __name__ == "__main__":
    main()

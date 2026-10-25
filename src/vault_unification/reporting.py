"""Machine-readable report writing with run metadata.

Every report carries the framework version, the command, resolved arguments,
UTC timestamp and (when available) the current git commit, so a fresh session
can reproduce and audit any result.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import FRAMEWORK_NAME, __version__

REPORT_SCHEMA_VERSION = "1.0"


def git_commit(path: str | Path | None = None) -> str | None:
    """Best-effort current git commit; None when git is unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            cwd=path or Path.cwd(),
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def report_metadata(command: str, args: dict | None = None, repo_root: str | Path | None = None) -> dict:
    """Standard metadata block attached to every generated report."""
    return {
        "framework": FRAMEWORK_NAME,
        "framework_version": __version__,
        "report_schema_version": REPORT_SCHEMA_VERSION,
        "command": command,
        "args": args or {},
        "utc_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": git_commit(repo_root),
    }


def write_json_report(
    path: str | Path,
    command: str,
    payload: dict,
    *,
    args: dict | None = None,
    repo_root: str | Path | None = None,
) -> dict:
    """Write *payload* plus standard metadata to *path* as JSON.

    Returns the full report dict that was written. The parent directory is
    created when missing. File writes are explicit destinations; callers are
    responsible for passing paths already validated by pathsafety.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    report = dict(payload)
    report["report_meta"] = report_metadata(command, args, repo_root)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=False)
        handle.write("\n")
    return report


def write_jsonl(path: str | Path, records: list[dict]) -> int:
    """Write JSONL records; returns count written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec, sort_keys=True) + "\n")
    return len(records)

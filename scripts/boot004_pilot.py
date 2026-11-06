"""BOOT-004: run the omission-detection pilot end-to-end and record evidence.

This is the hard-gate evidence run required by AGENTS.md section 7.5,
TOOLING_FRAMEWORK.md sections 7/9 and VERIFICATION_SPECIFICATION.md
section 6 before any large-scale synthesis is permitted.

Steps (each recorded with its real exit code; nothing is asserted from
model attention):

1. ``vu verify-manifest`` on BOTH real source vaults before the pilot
   (sources must be unchanged when the pilot starts);
2. ``vu omission-pilot`` in a temporary directory with the canonical report
   written to reports/bootstrap/boot-004-omission-pilot.json
   (12 planted defects: detection, localization, false positives, verdict);
3. ``vu verify-manifest`` on BOTH real source vaults after the pilot
   (the pilot must never have touched them);
4. a run-summary JSON with every command, exit code and report path.

The pilot fixture and all mutated copies live only in the temporary
directory; the committed evidence is the report plus this script.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

REPORTS = REPO_ROOT / "reports" / "bootstrap"
PILOT_REPORT = REPORTS / "boot-004-omission-pilot.json"
RUN_SUMMARY = REPORTS / "boot-004-run-summary.json"

VAULTS = [
    ("master-ai", "source-vaults/AI /Master AI", "state/manifests/master-ai.jsonl",
     "boot-004-immutable-before-master-ai.json", "boot-004-immutable-after-master-ai.json"),
    ("ai-course", "source-vaults/AI /AI Course", "state/manifests/ai-course.jsonl",
     "boot-004-immutable-before-ai-course.json", "boot-004-immutable-after-ai-course.json"),
]


def run(command: list[str], *, report: Path | None = None) -> dict:
    """Run a CLI command as a real subprocess; record stdout-tail + exit code."""
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-m", "vault_unification", *command],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=900,
        env=env,
    )
    record = {
        "command": " ".join(["vu", *command]),
        "exit_code": proc.returncode,
    }
    if report is not None:
        record["report"] = str(report.relative_to(REPO_ROOT))
        record["report_exists"] = report.is_file()
    record["stdout_tail"] = proc.stdout[-1500:]
    if proc.returncode != 0:
        record["stderr_tail"] = proc.stderr[-800:]
    print(f"  exit={proc.returncode}  vu {' '.join(command[:2])} ...")
    return record


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    steps: list[dict] = []
    all_ok = True

    print("[1/3] verifying source-vault immutability BEFORE the pilot")
    for name, root, manifest, before_report, _ in VAULTS:
        record = run(
            ["verify-manifest", "--root", root, "--manifest", manifest,
             "--report", str(REPORTS / before_report)],
            report=REPORTS / before_report,
        )
        record["vault"] = name
        record["phase"] = "before"
        steps.append(record)
        all_ok &= record["exit_code"] == 0

    print("[2/3] running the omission-detection pilot (synthetic fixture in a temp dir)")
    with tempfile.TemporaryDirectory(prefix="boot004-pilot-") as tmp:
        record = run(
            ["omission-pilot", "--dest", tmp, "--report", str(PILOT_REPORT)],
            report=PILOT_REPORT,
        )
        steps.append(record)
        pilot_exit = record["exit_code"]
        all_ok &= pilot_exit == 0

    print("[3/3] verifying source-vault immutability AFTER the pilot")
    for name, root, manifest, _, after_report in VAULTS:
        record = run(
            ["verify-manifest", "--root", root, "--manifest", manifest,
             "--report", str(REPORTS / after_report)],
            report=REPORTS / after_report,
        )
        record["vault"] = name
        record["phase"] = "after"
        steps.append(record)
        all_ok &= record["exit_code"] == 0

    # extract the verdict from the canonical pilot report (not from memory)
    verdict = None
    summary = None
    if PILOT_REPORT.is_file():
        with open(PILOT_REPORT, encoding="utf-8") as handle:
            pilot_data = json.load(handle)
        verdict = pilot_data["result"]["verdict"]
        summary = pilot_data["result"]["summary"]

    run_summary = {
        "task_id": "BOOT-004",
        "purpose": "omission-detection pilot evidence run (hard gate before large-scale synthesis)",
        "steps": steps,
        "pilot_verdict": verdict,
        "pilot_summary": summary,
        "source_immutability": {
            "before_exit_codes": [s["exit_code"] for s in steps if s.get("phase") == "before"],
            "after_exit_codes": [s["exit_code"] for s in steps if s.get("phase") == "after"],
        },
        "all_steps_ok": all_ok,
    }
    with open(RUN_SUMMARY, "w", encoding="utf-8") as handle:
        json.dump(run_summary, handle, indent=2, ensure_ascii=False)

    print()
    print(f"pilot verdict: {json.dumps(verdict)}")
    print(f"summary:      {json.dumps(summary)}")
    print(f"all steps ok: {all_ok}")
    print(f"run summary:  {RUN_SUMMARY.relative_to(REPO_ROOT)}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

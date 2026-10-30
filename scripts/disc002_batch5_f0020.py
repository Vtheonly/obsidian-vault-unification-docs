#!/usr/bin/env python3
"""Append finding F-0020 (silent no-op `python -m vault_unification.cli`)."""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path("state/findings.jsonl")

finding = {
    "category": "tooling-defect",
    "discovered_by": "DISC-002 session 5 (2026-10-30)",
    "evidence": "src/vault_unification/cli.py had no `if __name__ == \"__main__\"` guard, so `python3 -m vault_unification.cli <cmd>` imported the module, executed nothing, and exited 0 with no output and no report/out files. Reproduced in this session: the first run of scripts/disc002_batch5_replay.py drove all seven CLI steps via `python3 -m vault_unification.cli`; every subprocess returned 0 while zero output files appeared (scratch stayed empty), and a direct `python3 -m vault_unification.cli discovery-validate --candidates /nonexistent` also exited 0 silently. The `vu` entry point and `python3 -m vault_unification` (src/vault_unification/__main__.py) were never affected.",
    "expected_condition": "any documented CLI invocation either runs the command or exits nonzero with an error; an invocation that looks successful but does nothing is a silent-failure hazard for every scripted pipeline",
    "finding_id": "F-0020",
    "impact": "any script or operator using the documented-looking `python -m vault_unification.cli` form would silently skip work while observing exit code 0 (worse than a crash: no error is raised at all)",
    "observed": "scratch/ empty after a full 7-step replay that exited 0 at every step; `python3 -m vault_unification.cli --version` printed nothing; equivalent `vu --version` printed the version",
    "regression_prevention": "tests/test_cli.py::test_module_cli_execution_is_not_a_silent_noop runs both a happy path (--version must print) and a failure path (discovery-validate with a missing file must exit 1 and print an error) through `python -m vault_unification.cli` as real subprocesses",
    "remaining_risk": "none identified for this entry point; other invocations (python -m vault_unification, vu console script) already had guards or wrappers and are covered by existing tests",
    "repair": "added `if __name__ == \"__main__\": raise SystemExit(main())` to src/vault_unification/cli.py (behavior identical to the vu entry point)",
    "root_cause": "the package grew a __main__.py wrapper (python -m vault_unification) but the cli module itself never gained the __main__ guard, and no test exercised the module-execution path",
    "severity": "medium",
    "status": "fixed",
    "title": "`python -m vault_unification.cli` was a silent no-op (exit 0, no output)",
    "verification": "new regression test passed (1 passed in tests/test_cli.py::test_module_cli_execution_is_not_a_silent_noop); scripts/disc002_batch5_replay.py re-run after the fix executed every step and produced real outputs",
}

with open(OUT, "a", encoding="utf-8") as fh:
    fh.write(json.dumps(finding, sort_keys=True, ensure_ascii=False) + "\n")

print("appended F-0020 to", OUT)

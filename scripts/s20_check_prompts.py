#!/usr/bin/env python3
"""S20/SYNTH-001: validate every generation-prompt spec for an area with vu check-prompt.

Usage: python3 scripts/s20_check_prompts.py <slug>
Writes reports/synthesis/s20-<slug>-checkprompt.json (committed evidence).
Exit 0 only when every spec passes.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def main() -> int:
    slug = sys.argv[1] if len(sys.argv) > 1 else ""
    if not slug:
        print("usage: s20_check_prompts.py <slug>", file=sys.stderr)
        return 2
    batches = sorted(str(p) for p in (REPO / "state/knowledge-units").glob("*.jsonl"))
    specs = sorted(str(p) for p in (REPO / "scratch/synth" / slug / "specs").glob("*.json"))
    results = []
    fails = 0
    for i, s in enumerate(specs):
        rep_path = f"/tmp/s20-cp/{slug}-{i}.json"
        cmd = ["vu", "check-prompt", s, "--report", rep_path]
        for b in batches:
            cmd += ["--ku-batch", b]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
        try:
            rep = json.loads(Path(rep_path).read_text())["result"]
        except Exception:
            rep = {
                "ok": False,
                "failures": None,
                "raw": (p.stdout + p.stderr)[:400],
            }
        rec = {"spec": s, "exit": p.returncode, "ok": rep.get("ok"), "failures": rep.get("failures")}
        if not rep.get("ok"):
            fails += 1
            rec["failing_checks"] = [c for c in rep.get("checks", []) if not c.get("ok")]
        results.append(rec)
    summary = {"specs_total": len(specs), "ok": len(specs) - fails, "failed": fails, "results": results}
    out = REPO / "reports/synthesis" / f"s20-{slug}-checkprompt.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=1))
    if fails:
        for r in results:
            if not r["ok"]:
                print("FAILED:", r["spec"], json.dumps(r.get("failing_checks"), indent=1)[:600])
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

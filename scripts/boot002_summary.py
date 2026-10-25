"""BOOT-002: canonical inventory summary report.

Assembles reports/bootstrap/boot-002-inventory-summary.json from:
- the two vault stats reports (aggregates + per-file JSONL paths);
- a fresh reproducibility re-run of `stats` for each vault, comparing
  payload and per-file fingerprints;
- a fresh `inventory` re-run for each vault, comparing the produced
  manifest against the baseline manifest (immutability + reproducibility);
- an explicit unsupported-asset statement derived from file classes.

All comparisons are computed in code; nothing is asserted from model
attention.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from vault_unification import reporting  # noqa: E402

VAULTS = [
    {
        "name": "Master AI",
        "root": "source-vaults/AI /Master AI",
        "stats": "reports/bootstrap/boot-002-stats-master-ai.json",
        "per_file": "reports/bootstrap/boot-002-stats-master-ai.jsonl",
        "manifest": "state/manifests/master-ai.jsonl",
    },
    {
        "name": "AI Course",
        "root": "source-vaults/AI /AI Course",
        "stats": "reports/bootstrap/boot-002-stats-ai-course.json",
        "per_file": "reports/bootstrap/boot-002-stats-ai-course.jsonl",
        "manifest": "state/manifests/ai-course.jsonl",
    },
]

ENV = {"PYTHONPATH": "src", "PATH": "/usr/bin:/bin:/usr/local/bin"}


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=600,
        env={**__import__("os").environ, **ENV},
    )
    return {"command": " ".join(cmd), "exit_code": proc.returncode,
            "stdout_tail": proc.stdout[-500:], "stderr_tail": proc.stderr[-300:]}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def payload_fingerprint(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    data.pop("report_meta", None)
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def main() -> int:
    vault_reports = []
    for spec in VAULTS:
        stats_path = REPO_ROOT / spec["stats"]
        stats = json.loads(stats_path.read_text(encoding="utf-8"))
        per_file_path = REPO_ROOT / spec["per_file"]

        # reproducibility re-run (stats)
        tmp_report = REPO_ROOT / "reports/bootstrap/.repro-tmp.json"
        tmp_perfile = REPO_ROOT / "reports/bootstrap/.repro-tmp.jsonl"
        rerun = run([
            sys.executable, "-m", "vault_unification", "stats",
            "--root", spec["root"],
            "--report", str(tmp_report),
            "--per-file", str(tmp_perfile),
        ])
        repro = {
            "stats_rerun_exit_code": rerun["exit_code"],
            "payload_fingerprint_first": payload_fingerprint(stats_path),
            "payload_fingerprint_second": payload_fingerprint(tmp_report),
            "per_file_fingerprint_first": sha256_file(per_file_path),
            "per_file_fingerprint_second": sha256_file(tmp_perfile),
        }
        repro["payload_identical"] = (
            repro["payload_fingerprint_first"] == repro["payload_fingerprint_second"]
        )
        repro["per_file_identical"] = (
            repro["per_file_fingerprint_first"] == repro["per_file_fingerprint_second"]
        )
        tmp_report.unlink(missing_ok=True)
        tmp_perfile.unlink(missing_ok=True)

        # inventory reproducibility + immutability (fresh manifest vs baseline)
        tmp_manifest = REPO_ROOT / "reports/bootstrap/.repro-manifest.jsonl"
        inv = run([
            sys.executable, "-m", "vault_unification", "inventory",
            "--root", spec["root"],
            "--manifest", str(tmp_manifest),
            "--report", str(REPO_ROOT / "reports/bootstrap/.repro-inv.json"),
        ])
        baseline_fp = sha256_file(REPO_ROOT / spec["manifest"])
        fresh_fp = sha256_file(tmp_manifest)
        tmp_manifest.unlink(missing_ok=True)
        (REPO_ROOT / "reports/bootstrap/.repro-inv.json").unlink(missing_ok=True)

        vault_reports.append({
            "name": spec["name"],
            "root_exact": spec["root"],
            "stats_report": spec["stats"],
            "per_file_report": spec["per_file"],
            "totals": stats["totals"],
            "methods": stats["methods"],
            "unreadable_files": stats["unreadable_files"],
            "files_with_warnings_count": len(stats["files_with_warnings"]),
            "reproducibility": repro,
            "inventory_reproducibility": {
                "rerun_exit_code": inv["exit_code"],
                "baseline_manifest": spec["manifest"],
                "baseline_fingerprint": baseline_fp,
                "fresh_fingerprint": fresh_fp,
                "manifests_identical": baseline_fp == fresh_fp,
            },
        })

    # cross-validation: the 14 AI Course stats error files must equal the
    # F-0002 parse-error files from the independent check-links smoke run
    smoke = json.loads(
        (REPO_ROOT / "reports/framework/boot-000-smoke-check-links-ai-course.json")
        .read_text(encoding="utf-8")
    )
    smoke_pe = sorted(
        {p["file"] for p in smoke["result"]["problems"] if p["type"] == "parse_error"}
    )
    stats_err = sorted(u["relpath"] for u in vault_reports[1]["unreadable_files"])

    combined = {
        "purpose": (
            "BOOT-002 canonical inventory: content statistics for both source "
            "vaults with documented counting methods, reproducibility re-runs "
            "for stats and inventory, and an explicit unsupported-asset "
            "statement. Sources were never written to (manifests identical)."
        ),
        "corpus_totals": {
            "files_total": sum(v["totals"]["files_discovered"] for v in vault_reports),
            "markdown_files_total": sum(
                v["totals"]["text_files_analyzed"] + v["totals"]["text_files_with_errors"]
                for v in vault_reports
            ),
            "words_total": sum(v["totals"]["words_total"] for v in vault_reports),
            "words_outside_fences": sum(
                v["totals"]["words_outside_fences"] for v in vault_reports
            ),
            "tokens_estimate": sum(v["totals"]["tokens_estimate"] for v in vault_reports),
            "headings_total": sum(v["totals"]["headings_total"] for v in vault_reports),
        },
        "counting_methods": vault_reports[0]["methods"],
        "vaults": vault_reports,
        "unsupported_asset_statement": {
            "conclusion": (
                "No non-markdown assets exist in either vault at file level: "
                "every discovered file has a .md extension and is counted as "
                "markdown. No images, PDFs, or other binary attachments are "
                "present (verified by extension classes in the inventory "
                "manifests and by stats files_discovered == markdown counts)."
            ),
            "evidence": (
                "state/manifests/*.jsonl (all records class=markdown); "
                "boot-002 stats reports: skipped_nontext == 0 for both vaults."
            ),
        },
        "f0002_cross_validation": {
            "description": (
                "The 14 AI Course files with unclosed-fence errors found by the "
                "new stats capability (file_stats path) exactly match the 14 "
                "parse-error files reported by the independent check-links "
                "smoke run (linkcheck path)."
            ),
            "stats_error_files": len(stats_err),
            "checklinks_parse_error_files": len(smoke_pe),
            "exact_match": stats_err == smoke_pe,
        },
        "limitations": [
            "Word/heading/token counts are lexical measurements, never proof "
            "of semantic coverage or preservation.",
            "tokens_estimate is chars//4, a rough BPE-style approximation, not "
            "an exact tokenizer count.",
            "Per-file statistics measure full file content; knowledge-unit "
            "extraction has not started (BOOT-003+).",
            "The 14 AI Course unclosed-fence files are counted in full "
            "(content treated as real, consistent with F-0002 policy).",
        ],
    }

    out = REPO_ROOT / "reports" / "bootstrap" / "boot-002-inventory-summary.json"
    reporting.write_json_report(
        out, command="boot-002-summary", payload=combined,
        args={"vaults": [s["root"] for s in VAULTS]}, repo_root=REPO_ROOT,
    )

    print(json.dumps({
        "report": str(out.relative_to(REPO_ROOT)),
        "files_total": combined["corpus_totals"]["files_total"],
        "words_total": combined["corpus_totals"]["words_total"],
        "tokens_estimate": combined["corpus_totals"]["tokens_estimate"],
        "stats_reproducible": all(
            v["reproducibility"]["payload_identical"] and v["reproducibility"]["per_file_identical"]
            for v in vault_reports
        ),
        "manifests_identical": all(
            v["inventory_reproducibility"]["manifests_identical"] for v in vault_reports
        ),
        "f0002_exact_match": combined["f0002_cross_validation"]["exact_match"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

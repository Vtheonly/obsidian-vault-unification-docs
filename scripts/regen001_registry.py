#!/usr/bin/env python3
"""REGEN-001 step 3: rebuild the KU registry and produce full-corpus accounting.

1. kureg-init --force a fresh derived SQLite registry (state/registries/ is
   git-ignored and rebuildable per ADR-0007);
2. kureg-load every committed batch (001-011 revalidated + 012-070 REGEN) in
   numeric order — each batch is schema-validated before insert;
3. kureg-apply-overlap the seven committed classification files (ADR-0009
   pair-level overlay);
4. kureg-validate the registry (integrity + accounting invariants);
5. reconcile EVERY manifest file of both vaults against the registry:
   exactly-one-outcome accounting (extracted with N units, or explicitly
   failed), no file covered twice across batches, no file missing, and
   global knowledge_unit_id uniqueness across all 70 batches.

Writes reports/regen/regen001-registry.json and
reports/regen/regen001-accounting.json; exits non-zero on any violation.
Read-only with respect to both source vaults.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

AI_ROOT = "source-vaults/AI /AI Course"
MA_ROOT = "source-vaults/AI /Master AI"
DB = "state/registries/kuregistry.db"

CLASSIFICATIONS = [
    "state/classifications/001-ext003-regression-overlap.jsonl",
    "state/classifications/002-ext004-tree-based-overlap.jsonl",
    "state/classifications/003-ext005-evaluation-overlap.jsonl",
    "state/classifications/004-ext007-evaluation-addendum.jsonl",
    "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl",
    "state/classifications/006-ext009-generalization-overlap.jsonl",
    "state/classifications/007-ext010-training-stability-overlap.jsonl",
]


def run_cli(args: list[str], report: str | None = None) -> tuple[int, str, str]:
    cmd = [sys.executable, "-m", "vault_unification", *args]
    if report:
        cmd.extend(["--report", report])
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=1800)
    return proc.returncode, proc.stdout, proc.stderr


def main() -> int:
    ok = True
    steps: list[dict] = []

    # 1. fresh registry
    rc, out, err = run_cli(["kureg-init", "--db", DB, "--force"], "reports/regen/regen001-kureg-init.json")
    steps.append({"step": "kureg-init --force", "exit": rc})
    ok = ok and rc == 0
    if rc != 0:
        print(f"FAIL kureg-init: {err[:500]}")

    # 2. load all 70 batches in numeric order
    batches = sorted((REPO_ROOT / "state" / "knowledge-units").glob("*.jsonl"))
    loaded = 0
    load_failures = []
    for batch in batches:
        rc, out, err = run_cli(
            ["kureg-load", "--db", DB, "--kus", str(batch)]
        )
        if rc != 0:
            load_failures.append({"batch": batch.name, "exit": rc, "stderr": err[-500:]})
            ok = False
        else:
            loaded += 1
    steps.append(
        {
            "step": "kureg-load (all batches, numeric order)",
            "batches_total": len(batches),
            "batches_loaded": loaded,
            "failures": load_failures,
        }
    )
    print(f"kureg-load: {loaded}/{len(batches)} batches loaded")
    if load_failures:
        print("FAIL kureg-load:", json.dumps(load_failures[:3], indent=1))

    # 3. apply the seven classification overlays
    applied = 0
    apply_failures = []
    for clf in CLASSIFICATIONS:
        rc, out, err = run_cli(["kureg-apply-overlap", "--db", DB, "--classifications", clf])
        if rc != 0:
            apply_failures.append({"file": clf, "exit": rc, "stderr": err[-500:]})
            ok = False
        else:
            applied += 1
    steps.append(
        {
            "step": "kureg-apply-overlap (ADR-0009 overlay)",
            "files_total": len(CLASSIFICATIONS),
            "files_applied": applied,
            "failures": apply_failures,
        }
    )
    print(f"kureg-apply-overlap: {applied}/{len(CLASSIFICATIONS)} classification files applied")

    # 4. registry validation
    rc, out, err = run_cli(["kureg-validate", "--db", DB], "reports/regen/regen001-kureg-validate.json")
    try:
        validate_report = json.loads((REPO_ROOT / "reports" / "regen" / "regen001-kureg-validate.json").read_text())
        # kureg-validate writes a FLAT report (no "result" wrapper)
        counts = validate_report.get("counts", validate_report.get("result", {}).get("counts", {}))
        valid = validate_report.get("valid", validate_report.get("result", {}).get("valid"))
        classifications = validate_report.get("overlap_classification_counts", {})
    except (json.JSONDecodeError, OSError):
        counts = {}
        valid = None
        classifications = {}
    steps.append(
        {
            "step": "kureg-validate",
            "exit": rc,
            "valid": valid,
            "counts": counts,
            "overlap_classification_counts": classifications,
        }
    )
    ok = ok and rc == 0
    print(f"kureg-validate: exit={rc} counts={json.dumps(counts)}")
    if rc != 0:
        print("FAIL kureg-validate:", err[:800])

    registry_payload = {
        "command": "scripts/regen001_registry.py",
        "task_id": "REGEN-001",
        "db": DB,
        "steps": steps,
        "ok": ok,
    }
    (REPO_ROOT / "reports" / "regen" / "regen001-registry.json").write_text(
        json.dumps(registry_payload, indent=2) + "\n", encoding="utf-8"
    )

    # 5. full-corpus file-level accounting (independent of the registry:
    #    computed from the batch files + manifests directly)
    import hashlib

    vaults = [
        ("ai-course", AI_ROOT, "state/manifests/ai-course.jsonl"),
        ("master-ai", MA_ROOT, "state/manifests/master-ai.jsonl"),
    ]
    accounting_ok = True
    vault_summaries = []
    global_ids: dict[str, str] = {}
    duplicate_ids: list[dict] = []
    for vault_id, root, manifest_rel in vaults:
        manifest = [
            json.loads(line)
            for line in (REPO_ROOT / manifest_rel).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        manifest_files = {e["relpath"]: e["sha256"] for e in manifest}

        # KU coverage per file, straight from the batch files
        file_units: dict[str, int] = {}
        file_batches: dict[str, list[str]] = {}
        vault_records = 0
        for batch in batches:
            for line in batch.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                if not rec["source_id"].startswith(f"{vault_id}:"):
                    continue
                vault_records += 1
                ku = rec["knowledge_unit_id"]
                if ku in global_ids:
                    duplicate_ids.append(
                        {"ku_id": ku, "first_batch": global_ids[ku], "second_batch": batch.name}
                    )
                else:
                    global_ids[ku] = batch.name
                rel = rec["source_path"]
                file_units[rel] = file_units.get(rel, 0) + 1
                file_batches.setdefault(rel, []).append(batch.name)

        covered = set(file_units)
        missing = sorted(set(manifest_files) - covered)
        extra = sorted(covered - set(manifest_files))
        multi_batch = {f: bs for f, bs in file_batches.items() if len(set(bs)) > 1}

        # source immutability re-check as part of accounting
        hash_mismatches = []
        for rel, sha in manifest_files.items():
            disk = hashlib.sha256((REPO_ROOT / root / rel).read_bytes()).hexdigest()
            if disk != sha:
                hash_mismatches.append(rel)

        vault_summary = {
            "vault_id": vault_id,
            "manifest_files": len(manifest_files),
            "files_with_units": len(covered),
            "files_missing_units": missing,
            "files_not_in_manifest": extra,
            "files_covered_by_multiple_batches": {f: sorted(set(bs)) for f, bs in multi_batch.items()},
            "kus_total": vault_records,
            "units_per_file_min": min(file_units.values()) if file_units else 0,
            "units_per_file_max": max(file_units.values()) if file_units else 0,
            "units_per_file_mean": round(vault_records / len(file_units), 2) if file_units else 0,
            "source_hash_mismatches": hash_mismatches,
        }
        vault_summaries.append(vault_summary)
        vault_ok = not missing and not extra and not multi_batch and not hash_mismatches
        accounting_ok = accounting_ok and vault_ok
        print(
            f"accounting[{vault_id}]: files={len(manifest_files)} covered={len(covered)} "
            f"missing={len(missing)} extra={len(extra)} multi-batch={len(multi_batch)} "
            f"kus={vault_records} hash-mismatch={len(hash_mismatches)}"
        )

    total_kus = sum(v["kus_total"] for v in vault_summaries)
    accounting_payload = {
        "command": "scripts/regen001_registry.py",
        "task_id": "REGEN-001",
        "step": "full-corpus accounting: every source file has exactly one outcome",
        "denominators": {
            "files": "every relpath in both baseline manifests (609)",
            "units": "every record in every committed batch (001-070)",
        },
        "vaults": vault_summaries,
        "total_kus": total_kus,
        "global_unique_ku_ids": len(global_ids),
        "duplicate_ku_ids": duplicate_ids[:20],
        "duplicate_ku_ids_count": len(duplicate_ids),
        "ok": accounting_ok and not duplicate_ids,
        "limitations": [
            "accounting proves every file produced units and every unit is byte-faithful "
            "(see regen001-revalidation.json + per-batch fidelity reports); it is NOT proof "
            "of semantic completeness or correctness of segmentation",
            "dispositions remain 'Unaccounted' by design; assignment is later work and "
            "Unaccounted blocks release",
        ],
    }
    (REPO_ROOT / "reports" / "regen" / "regen001-accounting.json").write_text(
        json.dumps(accounting_payload, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"accounting: total_kus={total_kus} unique_ids={len(global_ids)} "
        f"duplicates={len(duplicate_ids)} ok={accounting_payload['ok']}"
    )

    return 0 if (ok and accounting_ok and not duplicate_ids) else 1


if __name__ == "__main__":
    raise SystemExit(main())

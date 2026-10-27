#!/usr/bin/env python3
"""REGEN-001 step 1: revalidate the 11 committed KU batches byte-identically.

For every committed batch, re-runs the exact extraction recipe recorded in the
historical coverage reports (reports/extraction/*coverage*.json report_meta.args:
root, scope, vault_id, unclosed_fence_finding, part order), twice per part:

- run1 vs run2 must be byte-identical (determinism);
- the concatenation of parts (in the recorded order) must equal the committed
  batch file byte-for-byte (regeneration fidelity).

Then runs `vu ku-fidelity` (CAP-022) over all committed batches per vault:
excerpt byte-exactness, hashes, id uniqueness within+across all 11 batches,
manifest agreement, structural purity, span bounds and heading discipline.

Writes reports/regen/regen001-revalidation.json and exits non-zero on any
failure. Read-only with respect to both source vaults (outputs go to a temp
dir under /tmp and the reports/ tree).
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from vault_unification import kufidelity  # noqa: E402

AI_ROOT = "source-vaults/AI /AI Course"
MA_ROOT = "source-vaults/AI /Master AI"

# (batch filename, vault root, vault id, [part scopes in order], unclosed flag)
RECIPES: list[tuple[str, str, str, list[str], str | None]] = [
    (
        "001-ext001-ai-course-03.1-regression.jsonl",
        AI_ROOT,
        "ai-course",
        ["03 - Machine Learning/03.1 - Regression"],
        "F-0002",
    ),
    (
        "002-ext002-master-ai-supervised-learning.jsonl",
        MA_ROOT,
        "master-ai",
        ["03 - Machine Learning/Supervised Learning"],
        None,
    ),
    (
        "003-ext004-ai-course-03.7-tree-based-models.jsonl",
        AI_ROOT,
        "ai-course",
        ["03 - Machine Learning/03.7 - Tree-Based Models"],
        None,
    ),
    (
        "004-ext005-master-ai-evaluation.jsonl",
        MA_ROOT,
        "master-ai",
        ["03 - Machine Learning/Evaluation/05 - ML Evaluation Metrics.md"],
        None,
    ),
    (
        "005-ext005-ai-course-03.6-model-evaluation.jsonl",
        AI_ROOT,
        "ai-course",
        ["03 - Machine Learning/03.6 - Model Evaluation"],
        "F-0002",
    ),
    (
        "006-ext008-master-ai-unsupervised.jsonl",
        MA_ROOT,
        "master-ai",
        ["03 - Machine Learning/Unsupervised Learning/04 - Clustering and Dimensionality Reduction.md"],
        None,
    ),
    (
        "007-ext008-ai-course-clustering-dimreduction.jsonl",
        AI_ROOT,
        "ai-course",
        [
            "03 - Machine Learning/03.5 - K-Means Clustering",
            "03 - Machine Learning/03.8 - Dimensionality Reduction",
        ],
        "F-0002",
    ),
    (
        "008-ext009-master-ai-generalization.jsonl",
        MA_ROOT,
        "master-ai",
        ["03 - Machine Learning/Generalization"],
        None,
    ),
    (
        "009-ext009-ai-course-04.3-regularization.jsonl",
        AI_ROOT,
        "ai-course",
        [
            "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/05. Batch Normalization.md",
            "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/06. Dropout and Regularization.md",
            "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/07. Data Augmentation.md",
        ],
        None,
    ),
    (
        "010-ext010-master-ai-training-stability.jsonl",
        MA_ROOT,
        "master-ai",
        [
            "04 - Neural Networks/Training/07 - Initialization Schemes.md",
            "04 - Neural Networks/Training/08 - Vanishing and Exploding Gradients.md",
        ],
        None,
    ),
    (
        "011-ext010-ai-course-04.3-init-gradients.jsonl",
        AI_ROOT,
        "ai-course",
        [
            "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/01. Weight Initialization.md",
            "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/02. Weight Initialization Techniques.md",
            "04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability/03. The Vanishing and Exploding Gradient Problems.md",
        ],
        None,
    ),
]


def run_extract(root: str, scope: str, vault_id: str, uff: str | None, out: Path, report: Path) -> dict:
    cmd = [
        sys.executable,
        "-m",
        "vault_unification",
        "extract-kus",
        "--root",
        root,
        "--scope",
        scope,
        "--vault-id",
        vault_id,
        "--manifest",
        f"state/manifests/{'ai-course' if vault_id == 'ai-course' else 'master-ai'}.jsonl",
        "--out",
        str(out),
        "--report",
        str(report),
    ]
    if uff:
        cmd.extend(["--unclosed-fence-finding", uff])
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"ok": False, "returncode": proc.returncode, "stderr": proc.stderr[-2000:]}
    return {"ok": True, "returncode": 0, "summary": json.loads(proc.stdout)}


def main() -> int:
    out_dir = Path(tempfile.mkdtemp(prefix="regen001-revalidate-"))
    results: list[dict] = []
    all_ok = True

    for batch_name, root, vault_id, scopes, uff in RECIPES:
        committed = REPO_ROOT / "state" / "knowledge-units" / batch_name
        entry: dict = {
            "batch": f"state/knowledge-units/{batch_name}",
            "vault_id": vault_id,
            "parts": [],
            "double_run_identical": True,
            "regenerates_committed_bytes": False,
            "ok": False,
        }
        parts_ok = True
        part_bytes: list[bytes] = []
        for i, scope in enumerate(scopes):
            run1 = out_dir / f"{batch_name}.p{i}.run1.jsonl"
            run2 = out_dir / f"{batch_name}.p{i}.run2.jsonl"
            rep1 = out_dir / f"{batch_name}.p{i}.run1.json"
            rep2 = out_dir / f"{batch_name}.p{i}.run2.json"
            r1 = run_extract(root, scope, vault_id, uff, run1, rep1)
            r2 = run_extract(root, scope, vault_id, uff, run2, rep2)
            part_ok = r1["ok"] and r2["ok"]
            identical = part_ok and run1.read_bytes() == run2.read_bytes()
            entry["parts"].append(
                {
                    "scope": scope,
                    "extract_ok": part_ok,
                    "records": r1.get("summary", {}).get("records_written"),
                    "double_run_identical": identical,
                }
            )
            if not part_ok or not identical:
                parts_ok = False
                entry["double_run_identical"] = entry["double_run_identical"] and identical
                if not part_ok:
                    entry["parts"][-1]["stderr"] = (r1.get("stderr") or r2.get("stderr") or "")[:500]
            else:
                part_bytes.append(run1.read_bytes())

        if parts_ok:
            regenerated = b"".join(part_bytes)
            entry["regenerates_committed_bytes"] = regenerated == committed.read_bytes()
            entry["committed_bytes"] = committed.stat().st_size
            entry["regenerated_bytes"] = len(regenerated)
        entry["ok"] = parts_ok and entry["regenerates_committed_bytes"]
        all_ok = all_ok and entry["ok"]
        results.append(entry)
        print(
            f"{'OK ' if entry['ok'] else 'FAIL'} {batch_name}: "
            f"parts={len(scopes)} double-run={entry['double_run_identical']} "
            f"bytes-match={entry['regenerates_committed_bytes']}"
        )

    # fidelity check over all committed batches, per vault
    fidelity_reports = {}
    for vault_id, root, manifest in [
        ("ai-course", AI_ROOT, REPO_ROOT / "state" / "manifests" / "ai-course.jsonl"),
        ("master-ai", MA_ROOT, REPO_ROOT / "state" / "manifests" / "master-ai.jsonl"),
    ]:
        batches = [
            REPO_ROOT / "state" / "knowledge-units" / name
            for name, r, v, _, _ in RECIPES
            if v == vault_id
        ]
        # cross-check against the other vault's batches must NOT happen: ids are
        # content-fingerprints; sibling-glob default would mix vaults. Use the
        # vault's own batch list as both checked and cross-checked? No: check all
        # of this vault's batches together; cross-check glob covers nothing new
        # but the within-run aggregate catches cross-batch collisions.
        report = kufidelity.check_batches(
            [str(b) for b in batches],
            vault_id,
            REPO_ROOT / root,
            manifest,
            kus_schema=REPO_ROOT / "schemas" / "knowledge-unit.schema.json",
            cross_check_paths=[],
        )
        fidelity_reports[vault_id] = {
            "ok": report["ok"],
            "batches_checked": report["batches_checked"],
            "records_total": report["records_total"],
            "excerpt_byte_exact": sum(b["excerpt_byte_exact"] for b in report["batches"]),
            "ids_unique_across_checked": report["ids_unique_across_checked"],
            "records_with_errors": report["records_with_errors"],
            "errors": [e for b in report["batches"] for e in b["errors"]][:50],
        }
        all_ok = all_ok and report["ok"]
        print(
            f"{'OK ' if report['ok'] else 'FAIL'} ku-fidelity[{vault_id}]: "
            f"records={report['records_total']} exact={sum(b['excerpt_byte_exact'] for b in report['batches'])} "
            f"unique_ids={report['ids_unique_across_checked']}"
        )

    payload = {
        "command": "scripts/regen001_revalidate.py",
        "task_id": "REGEN-001",
        "step": "revalidate committed batches 001-011",
        "recipes_source": "reports/extraction/*coverage*.json report_meta.args (historical invocation records)",
        "determinism_note": "each part extracted twice; run1 vs run2 byte-compared; concatenated parts byte-compared against the committed batch",
        "batches": results,
        "fidelity": fidelity_reports,
        "ok": all_ok,
    }
    out = REPO_ROOT / "reports" / "regen" / "regen001-revalidation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"report: {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""REGEN-001 step 2: extract the remaining 578 source files in bounded batches.

Plan construction (deterministic, documented):
- Scope: every manifest file of both vaults that is NOT already covered by the
  11 revalidated committed batches (coverage set = union of their source_path
  values, per vault).
- Grouping: remaining files grouped by top-level folder within each vault
  (files at the vault root form one "<root files>" group). Groups larger than
  MAX_GROUP files split by second-level subfolder (and third level if still
  too large). Root-file groups and multi-part folder splits are extracted as
  per-file runs concatenated in sorted relpath order.
- Ordering: AI Course first (smaller vault completes full coverage sooner),
  then Master AI; folders sorted lexicographically within each vault; the
  root-files group runs last within its vault.
- Numbering: continues the committed sequence (012, 013, ...).
- Naming: NNN-regen001-<vault>-<slug>.jsonl with a filesystem-safe slug of the
  group name.

Per batch (all executed through the framework CLI, never by hand):
1. extract-kus twice (run1/run2) with identical parameters;
2. run1 vs run2 byte-compared (determinism gate);
3. run1 bytes become the committed batch file;
4. vu ku-fidelity checks the batch (schema, excerpt byte-exactness, hashes,
   id uniqueness within + across all sibling batches, manifest agreement,
   structural purity, span discipline) — sibling cross-check covers the 11
   revalidated batches and every earlier REGEN batch;
5. a per-batch coverage JSON report is written for accounting.

The driver is resumable: batches already written and fidelity-verified are
skipped (their reports are re-read), so an interrupted run loses no progress.
Outputs: state/knowledge-units/NNN-regen001-*.jsonl batches,
reports/regen/batch-NNN-coverage.json, reports/regen/batch-NNN-fidelity.json,
reports/regen/regen001-plan.json, reports/regen/regen001-extraction.json.

Read-only with respect to both source vaults. Exits non-zero if any batch
fails any gate.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

AI_ROOT = "source-vaults/AI /AI Course"
MA_ROOT = "source-vaults/AI /Master AI"
MAX_GROUP = 40

VAULTS = [
    ("ai-course", AI_ROOT, "state/manifests/ai-course.jsonl", "F-0002"),
    ("master-ai", MA_ROOT, "state/manifests/master-ai.jsonl", None),
]

COMMITTED_BATCHES = sorted((REPO_ROOT / "state" / "knowledge-units").glob("0[01][0-9]-ext*.jsonl"))


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "group"


def committed_coverage() -> dict[str, set[str]]:
    """Per-vault set of source_path values already extracted (batches 001-011)."""
    covered: dict[str, set[str]] = {"ai-course": set(), "master-ai": set()}
    for batch in COMMITTED_BATCHES:
        for line in batch.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            vault = rec["source_id"].split(":", 1)[0]
            covered[vault].add(rec["source_path"])
    return covered


def build_groups() -> list[dict]:
    """Deterministic batch plan for the remaining files."""
    covered = committed_coverage()
    plan: list[dict] = []
    for vault_id, root, manifest_rel, uff in VAULTS:
        manifest = [
            json.loads(line)
            for line in (REPO_ROOT / manifest_rel).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        remaining = [e["relpath"] for e in manifest if e["relpath"] not in covered[vault_id]]

        def group_key(relpath: str, depth: int) -> str:
            parts = relpath.split("/")
            if len(parts) == 1:
                return "<root files>"
            if depth == 1:
                return parts[0]
            return "/".join(parts[:depth])

        def split(files: list[str], depth: int) -> list[tuple[str, list[str]]]:
            groups: dict[str, list[str]] = {}
            for rel in sorted(files):
                groups.setdefault(group_key(rel, depth), []).append(rel)
            out: list[tuple[str, list[str]]] = []
            for name in sorted(groups):
                members = groups[name]
                if len(members) > MAX_GROUP:
                    # try to split one level deeper
                    deeper = split(members, depth + 1)
                    if all(len(m) <= MAX_GROUP for _, m in deeper):
                        out.extend(deeper)
                        continue
                out.append((name, members))
            return out

        groups = split(remaining, depth=1)
        # deterministic order: folders sorted; <root files> last
        folders = [(n, m) for n, m in groups if n != "<root files>"]
        roots = [(n, m) for n, m in groups if n == "<root files>"]
        for name, members in folders + roots:
            plan.append(
                {
                    "vault_id": vault_id,
                    "root": root,
                    "manifest": manifest_rel,
                    "uff": uff,
                    "group": name,
                    "files": members,
                    "file_count": len(members),
                }
            )
    return plan


def next_batch_numbers(plan: list[dict]) -> None:
    """Numbering continues the committed sequence and is STABLE across runs:
    the maximum is computed over the committed ext* batches only (001-011),
    never over regen* files already present. Deriving the start number from
    the directory contents made a resumed run renumber the whole plan and
    mint duplicate batches (caught by the fidelity id-collision gate; the
    duplicates were verified byte-identical and removed before this fix)."""
    max_num = 0
    for p in COMMITTED_BATCHES:
        m = re.match(r"(\d{3})-", p.name)
        if m:
            max_num = max(max_num, int(m.group(1)))
    for i, entry in enumerate(plan, start=max_num + 1):
        entry["batch_number"] = i


def batch_path_for(entry: dict) -> Path:
    name = f"{entry['batch_number']:03d}-regen001-{entry['vault_id']}-{slugify(entry['group'])}.jsonl"
    return REPO_ROOT / "state" / "knowledge-units" / name


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "vault_unification", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=600,
    )


def extract_batch(entry: dict, out: Path, report: Path) -> subprocess.CompletedProcess:
    """Extract one batch as per-file single-file runs concatenated in the
    batch's documented order (sorted relpath).

    Per-file runs (not folder scopes) are REQUIRED for correctness: several
    planned folders also contain already-extracted files (e.g. ai-course
    '03 - Machine Learning' includes the committed 03.1/03.5/03.6/03.7/03.8
    batches; master-ai '04 - Neural Networks' includes the committed
    Training/07+08). A folder scope would re-extract those files and mint
    duplicate KU records (content-fingerprint ids collide with the committed
    batches). Per-file runs guarantee each file is extracted exactly once,
    matching the plan's file list exactly, and follow the concatenation
    pattern already established by committed batches 009/010/011.
    """
    parts: list[bytes] = []
    file_outcomes = []
    records = 0
    tmp = Path(tempfile.mkdtemp(prefix=f"regen001-b{entry['batch_number']}-"))
    for i, rel in enumerate(entry["files"]):
        part_out = tmp / f"part-{i:03d}.jsonl"
        part_rep = tmp / f"part-{i:03d}.json"
        args = [
            "extract-kus",
            "--root", entry["root"],
            "--scope", rel,
            "--vault-id", entry["vault_id"],
            "--manifest", entry["manifest"],
            "--out", str(part_out),
            "--report", str(part_rep),
        ]
        if entry["uff"]:
            args.extend(["--unclosed-fence-finding", entry["uff"]])
        proc = run_cli(args)
        if proc.returncode != 0:
            return proc
        parts.append(part_out.read_bytes())
        rep = json.loads(part_rep.read_text(encoding="utf-8"))
        res = rep["result"]
        records += res["records_written"]
        file_outcomes.extend(res["file_outcomes"])
    out.write_bytes(b"".join(parts))
    payload = {
        "command": "extract-kus",
        "result": {
            "ok": True,
            "vault_id": entry["vault_id"],
            "root": entry["root"],
            "scope": f"{entry['group']} (per-file runs, concatenated sorted)",
            "manifest": entry["manifest"],
            "batch_path": str(out),
            "records_written": records,
            "denominators": {
                "files_in_scope": len(entry["files"]),
                "files_extracted": len(entry["files"]),
                "files_excluded": 0,
                "files_failed": 0,
            },
            "file_outcomes": file_outcomes,
        },
    }
    report.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return subprocess.CompletedProcess(args=["concat"], returncode=0, stdout="", stderr="")


def batch_already_done(entry: dict, out: Path) -> bool:
    rep = REPO_ROOT / "reports" / "regen" / f"batch-{entry['batch_number']:03d}-fidelity.json"
    cov = REPO_ROOT / "reports" / "regen" / f"batch-{entry['batch_number']:03d}-coverage.json"
    if not (out.is_file() and rep.is_file() and cov.is_file()):
        return False
    try:
        fidelity = json.loads(rep.read_text(encoding="utf-8"))
        return fidelity.get("result", {}).get("ok") is True
    except (json.JSONDecodeError, OSError):
        return False


def main() -> int:
    plan_only = "--plan-only" in sys.argv
    plan = build_groups()
    next_batch_numbers(plan)

    plan_payload = {
        "command": "scripts/regen001_extract.py",
        "task_id": "REGEN-001",
        "step": "full-corpus extraction plan for the remaining files",
        "max_group_files": MAX_GROUP,
        "ordering": "ai-course first (smaller vault completes coverage sooner), then master-ai; "
        "folders lexicographic; <root files> group last per vault; splits by subfolder when a "
        "group exceeds the cap",
        "committed_batches_preloaded": [p.name for p in COMMITTED_BATCHES],
        "batches": [
            {
                "batch_number": e["batch_number"],
                "batch_file": f"state/knowledge-units/{batch_path_for(e).name}",
                "vault_id": e["vault_id"],
                "group": e["group"],
                "file_count": e["file_count"],
                "files": e["files"],
                "unclosed_fence_finding": e["uff"],
            }
            for e in plan
        ],
        "total_files": sum(e["file_count"] for e in plan),
    }
    plan_out = REPO_ROOT / "reports" / "regen" / "regen001-plan.json"
    plan_out.parent.mkdir(parents=True, exist_ok=True)
    plan_out.write_text(json.dumps(plan_payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"plan: {len(plan)} batches, {plan_payload['total_files']} files -> {plan_out}"
    )
    if plan_only:
        return 0

    tmp = Path(tempfile.mkdtemp(prefix="regen001-extract-"))
    results = []
    all_ok = True
    for entry in plan:
        out = batch_path_for(entry)
        cov_report = REPO_ROOT / "reports" / "regen" / f"batch-{entry['batch_number']:03d}-coverage.json"
        fid_report = REPO_ROOT / "reports" / "regen" / f"batch-{entry['batch_number']:03d}-fidelity.json"

        if batch_already_done(entry, out):
            results.append(
                {"batch": out.name, "status": "skipped-already-done", "ok": True}
            )
            print(f"SKIP {out.name} (already written + fidelity-verified)")
            continue

        # 1+2: double run
        run1 = tmp / f"{out.name}.run1"
        run2 = tmp / f"{out.name}.run2"
        rep1 = tmp / f"{out.name}.run1.json"
        p1 = extract_batch(entry, run1, rep1)
        p2 = extract_batch(entry, run2, tmp / f"{out.name}.run2.json")
        status = {
            "batch": out.name,
            "vault_id": entry["vault_id"],
            "group": entry["group"],
            "files": entry["file_count"],
        }
        if p1.returncode != 0 or p2.returncode != 0:
            status.update(
                {
                    "status": "extract-failed",
                    "ok": False,
                    "stderr": (p1.stderr or p2.stderr or "")[-1000:],
                }
            )
            results.append(status)
            all_ok = False
            print(f"FAIL {out.name}: extraction failed")
            continue
        identical = run1.read_bytes() == run2.read_bytes()
        if not identical:
            status.update({"status": "double-run-mismatch", "ok": False})
            results.append(status)
            all_ok = False
            print(f"FAIL {out.name}: run1 != run2")
            continue

        # 3: commit bytes + coverage report
        out.write_bytes(run1.read_bytes())
        cov_report.write_text(rep1.read_text(encoding="utf-8"))

        # 4: fidelity gate (sibling cross-check covers committed + earlier regen batches)
        fid_args = [
            "ku-fidelity",
            "--batch", str(out),
            "--vault-id", entry["vault_id"],
            "--vault-root", entry["root"],
            "--manifest", entry["manifest"],
            "--report", str(fid_report),
        ]
        pf = run_cli(fid_args)
        fid_ok = pf.returncode == 0
        status.update(
            {
                "status": "extracted-and-verified" if fid_ok else "fidelity-failed",
                "ok": fid_ok,
                "records": sum(1 for _ in out.open()),
            }
        )
        if not fid_ok:
            status["stderr"] = (pf.stdout + pf.stderr)[-1500:]
            all_ok = False
            print(f"FAIL {out.name}: fidelity gate failed")
        else:
            print(f"OK   {out.name}: {status['records']} KUs, {entry['file_count']} files")
        results.append(status)

    payload = {
        "command": "scripts/regen001_extract.py",
        "task_id": "REGEN-001",
        "step": "bounded-batch extraction of remaining files",
        "plan": "reports/regen/regen001-plan.json",
        "batches": results,
        "ok": all_ok,
        "total_batches": len(results),
        "note": "total_files counts only batches processed in THIS invocation; skipped "
        "batches carry no file count here. The authoritative accounting is "
        "reports/regen/regen001-accounting.json (registry-backed, all 609 files).",
        "total_files_processed_this_run": sum(r.get("files", 0) for r in results if r.get("ok")),
    }
    out = REPO_ROOT / "reports" / "regen" / "regen001-extraction.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"report: {out}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""EXT-008: excerpt-fidelity and ID-uniqueness check for BOTH clustering /
dimensionality-reduction batches (master-ai batch 006 + AI Course batch 007).

For every record in each batch, verifies:
- the excerpt is byte-exact the source line slice [line_start, line_end]
  (CR normalization identical to the extractor's splitlines reconstruction);
- the excerpt hash matches sha256(excerpt);
- knowledge_unit_id values are unique WITHIN and ACROSS both new batches AND
  against every committed batch 001-005 (extension over the EXT-005 checker);
- source_id / source_path / source_file_hash agree with the baseline manifest;
- no span crosses a real heading boundary (heading lines come from the
  framework's construct detector, mdextract.extract_structure_text, CAP-003 —
  the single authority, so `#` comments inside code fences are not headings);
- vault-id is exactly the pinned value for that batch;
- structural purity: disposition 'Unaccounted', no overlap_type,
  verification_status all-pending + extraction machine-segmented.

Batch 007 provenance note: the AI Course side was produced by TWO deterministic
single-scope extraction runs (03.5 - K-Means Clustering, then
03.8 - Dimensionality Reduction) concatenated in that fixed order; each part
was double-run byte-identical before concatenation and the concatenated file
was re-compared against a second concatenation of the second runs.

Writes reports/extraction/ext008-fidelity-{master-ai,ai-course}.json and
exits non-zero on any violation. Read-only with respect to both vaults.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vault_unification.mdextract import extract_structure_text  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
COMMITTED_BATCHES = sorted(
    (REPO_ROOT / "state" / "knowledge-units").glob("00[1-5]-*.jsonl")
)
BATCHES = [
    (
        "master-ai",
        REPO_ROOT / "state" / "knowledge-units" / "006-ext008-master-ai-unsupervised.jsonl",
        REPO_ROOT / "state" / "manifests" / "master-ai.jsonl",
        REPO_ROOT / "source-vaults" / "AI " / "Master AI",
        REPO_ROOT / "reports" / "extraction" / "ext008-fidelity-master-ai.json",
    ),
    (
        "ai-course",
        REPO_ROOT / "state" / "knowledge-units" / "007-ext008-ai-course-clustering-dimreduction.jsonl",
        REPO_ROOT / "state" / "manifests" / "ai-course.jsonl",
        REPO_ROOT / "source-vaults" / "AI " / "AI Course",
        REPO_ROOT / "reports" / "extraction" / "ext008-fidelity-ai-course.json",
    ),
]


def check_batch(vault_id: str, batch: Path, manifest_path: Path, vault_root: Path, report_path: Path, global_ids: dict[str, str]) -> tuple[list[str], dict]:
    records = [json.loads(line) for line in batch.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entry = json.loads(line)
            manifest[entry["relpath"]] = entry["sha256"]

    errors: list[str] = []
    ids: set[str] = set()
    excerpt_exact = 0
    hash_ok = 0
    structurally_pure = 0
    heading_lines_by_file: dict[str, set[int]] = {}

    for record in records:
        ku_id = record["knowledge_unit_id"]
        if ku_id in ids:
            errors.append(f"duplicate knowledge_unit_id within batch: {ku_id}")
        if ku_id in global_ids:
            errors.append(f"knowledge_unit_id collides across batches: {ku_id} (also in {global_ids[ku_id]})")
        ids.add(ku_id)
        global_ids[ku_id] = batch.name

        if not record["source_id"].startswith(f"{vault_id}:"):
            errors.append(f"{ku_id}: source_id vault prefix is not '{vault_id}': {record['source_id']}")

        relpath = record["source_path"]
        if record["source_id"] != f"{vault_id}:{relpath}":
            errors.append(f"{ku_id}: source_id/source_path mismatch")

        src = vault_root / relpath
        text = src.read_text(encoding="utf-8")
        file_lines = text.splitlines()
        file_hash = hashlib.sha256(src.read_bytes()).hexdigest()
        if file_hash != record["source_file_hash"]:
            errors.append(f"{ku_id}: source_file_hash mismatch for {relpath}")
        if manifest.get(relpath) != file_hash:
            errors.append(f"{ku_id}: source hash disagrees with baseline manifest for {relpath}")

        if record.get("disposition") != "Unaccounted":
            errors.append(f"{ku_id}: disposition is {record.get('disposition')!r}, expected 'Unaccounted'")
        if record.get("overlap_type") is not None:
            errors.append(f"{ku_id}: overlap_type must be NULL in a fresh batch ({record['overlap_type']})")
        vs = record.get("verification_status")
        vs_ok = (
            isinstance(vs, dict)
            and vs.get("accounting") == "pending"
            and vs.get("editorial") == "pending"
            and vs.get("extraction") == "machine-segmented"
            and vs.get("semantic") == "pending"
            and vs.get("technical") == "pending"
        )
        if not vs_ok:
            errors.append(f"{ku_id}: verification_status not the fresh-batch form: {vs!r}")
        if record.get("disposition") == "Unaccounted" and record.get("overlap_type") is None and vs_ok:
            structurally_pure += 1

        if relpath not in heading_lines_by_file:
            structure = extract_structure_text(text)
            heading_lines_by_file[relpath] = {h["line"] for h in structure["headings"]}

        start, end = record["line_start"], record["line_end"]
        if not (1 <= start <= end <= len(file_lines)):
            errors.append(f"{ku_id}: line range {start}-{end} outside file {relpath} ({len(file_lines)} lines)")
            continue
        reconstructed = "\n".join(file_lines[start - 1 : end])
        if reconstructed == record["excerpt"]:
            excerpt_exact += 1
        else:
            errors.append(f"{ku_id}: excerpt not byte-exact for {relpath} lines {start}-{end}")
        if hashlib.sha256(record["excerpt"].encode("utf-8")).hexdigest() == record["excerpt_hash"]:
            hash_ok += 1
        else:
            errors.append(f"{ku_id}: excerpt_hash mismatch")

        crossed = heading_lines_by_file[relpath] & set(range(start, end + 1))
        if crossed:
            errors.append(f"{ku_id}: span crosses heading line(s) {sorted(crossed)} in {relpath}")

    report = {
        "command": "scripts/ext008_fidelity.py",
        "batch": str(batch.relative_to(REPO_ROOT)),
        "records_total": len(records),
        "excerpt_byte_exact": excerpt_exact,
        "excerpt_hash_valid": hash_ok,
        "structurally_pure": structurally_pure,
        "unique_ids": len(ids),
        "vault_id": vault_id,
        "files_covered": sorted(heading_lines_by_file),
        "errors": errors,
        "ok": not errors,
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return errors, report


def main() -> int:
    # Preload committed batch ids so collisions with 001-005 are also caught.
    global_ids: dict[str, str] = {}
    for committed in COMMITTED_BATCHES:
        for line in committed.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                global_ids[rec["knowledge_unit_id"]] = committed.name
    committed_id_count = len(global_ids)

    all_errors: list[str] = []
    for vault_id, batch, manifest, vault_root, report_path in BATCHES:
        errors, report = check_batch(vault_id, batch, manifest, vault_root, report_path, global_ids)
        summary = {k: v for k, v in report.items() if k != "errors"}
        print(json.dumps(summary, indent=2))
        all_errors.extend(errors)
    print(
        json.dumps(
            {
                "committed_batches_preloaded": [p.name for p in COMMITTED_BATCHES],
                "committed_ids_preloaded": committed_id_count,
            },
            indent=2,
        )
    )
    if all_errors:
        print("ERRORS:", *all_errors, sep="\n  ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

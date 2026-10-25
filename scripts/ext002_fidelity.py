"""EXT-002: excerpt-fidelity and ID-uniqueness check for the Master AI batch.

Verifies, for every record in
state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl:
- the excerpt is byte-exact the source line slice [line_start, line_end]
  (CR normalization identical to the extractor's splitlines reconstruction);
- the excerpt hash matches sha256(excerpt);
- knowledge_unit_id values are unique within the batch;
- source_id / source_path / source_file_hash agree with the baseline manifest;
- no span crosses a real heading boundary (heading lines belong to heading
  context, not unit spans). Heading lines come from the framework's own
  construct detector (mdextract.extract_structure_text, CAP-003 — the single
  authority), so `#` comments inside code fences are not headings;
- vault-id is exactly 'master-ai' (pinned; ADR in docs/FRAMEWORK_SETUP.md).

Writes reports/extraction/ext002-fidelity.json and exits non-zero on any
violation. Read-only with respect to both source vaults.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vault_unification.mdextract import extract_structure_text  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH = REPO_ROOT / "state" / "knowledge-units" / "002-ext002-master-ai-supervised-learning.jsonl"
MANIFEST = REPO_ROOT / "state" / "manifests" / "master-ai.jsonl"
VAULT_ROOT = REPO_ROOT / "source-vaults" / "AI " / "Master AI"
REPORT = REPO_ROOT / "reports" / "extraction" / "ext002-fidelity.json"

EXPECTED_VAULT_ID = "master-ai"


def main() -> int:
    records = [json.loads(line) for line in BATCH.read_text(encoding="utf-8").splitlines() if line.strip()]
    manifest = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entry = json.loads(line)
            manifest[entry["relpath"]] = entry["sha256"]

    errors: list[str] = []
    ids: set[str] = set()
    excerpt_exact = 0
    hash_ok = 0
    heading_lines_by_file: dict[str, set[int]] = {}

    for record in records:
        ku_id = record["knowledge_unit_id"]
        if ku_id in ids:
            errors.append(f"duplicate knowledge_unit_id {ku_id}")
        ids.add(ku_id)

        if not record["source_id"].startswith(f"{EXPECTED_VAULT_ID}:"):
            errors.append(f"{ku_id}: source_id vault prefix is not '{EXPECTED_VAULT_ID}': {record['source_id']}")

        relpath = record["source_path"]
        if record["source_id"] != f"{EXPECTED_VAULT_ID}:{relpath}":
            errors.append(f"{ku_id}: source_id/source_path mismatch")

        src = VAULT_ROOT / relpath
        text = src.read_text(encoding="utf-8")
        file_lines = text.splitlines()
        file_hash = hashlib.sha256(src.read_bytes()).hexdigest()
        if file_hash != record["source_file_hash"]:
            errors.append(f"{ku_id}: source_file_hash mismatch for {relpath}")
        if manifest.get(relpath) != file_hash:
            errors.append(f"{ku_id}: source hash disagrees with baseline manifest for {relpath}")

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
        "command": "scripts/ext002_fidelity.py",
        "batch": str(BATCH.relative_to(REPO_ROOT)),
        "records_total": len(records),
        "excerpt_byte_exact": excerpt_exact,
        "excerpt_hash_valid": hash_ok,
        "unique_ids": len(ids),
        "vault_id": EXPECTED_VAULT_ID,
        "files_covered": sorted(heading_lines_by_file),
        "errors": errors,
        "ok": not errors,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "errors"}, indent=2))
    if errors:
        print("ERRORS:", *errors, sep="\n  ", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""CAP-022: KU batch fidelity verification (kufidelity).

Verifies that committed knowledge-unit batches are faithful to their immutable
sources, replacing the per-task fidelity scripts used by EXT-001..EXT-010
(retrospective finding: task-local scripts duplicated this functionality; the
reusable command is the single authority from REGEN-001 onward).

Checks, per batch and in aggregate:

- schema validity of every record (when a KU schema path is supplied);
- ``knowledge_unit_id`` uniqueness within each batch and across all
  cross-checked batches (default: every sibling ``*.jsonl`` file that is not
  itself one of the checked batches);
- ``source_id`` carries exactly the pinned ``vault_id`` prefix and agrees
  with ``source_path``;
- ``source_file_hash`` equals the sha256 of the file on disk AND the baseline
  manifest entry (source immutability evidence);
- fresh-batch structural purity: ``disposition`` Unaccounted, ``overlap_type``
  null and ``verification_status`` in the fresh form (relaxable via
  ``allow_processed`` for post-disposition re-verification);
- the excerpt is the byte-exact source line slice ``[line_start, line_end]``
  (CR normalization identical to the extractor's ``splitlines`` behaviour);
- ``excerpt_hash`` equals sha256(excerpt);
- spans stay inside file bounds;
- spans never cross a real heading line (heading lines come from
  ``mdextract.extract_structure_text`` — the single construct authority — so
  ``#`` comments inside code fences are not headings).

The check is read-only with respect to the vault root: only the optional
report path is written, and it must live outside the vault root.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from . import mdextract
from .registry import validate_ku_file

FRESH_VERIFICATION_STATUS = {
    "accounting": "pending",
    "editorial": "pending",
    "extraction": "machine-segmented",
    "semantic": "pending",
    "technical": "pending",
}


class FidelityError(Exception):
    """Raised for unusable inputs (missing files, unreadable batches)."""


def _load_manifest(manifest_path: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FidelityError(f"cannot read manifest: {manifest_path} ({exc})") from exc
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise FidelityError(f"manifest line is not JSON: {exc}") from exc
        relpath = entry.get("relpath")
        sha = entry.get("sha256")
        if not relpath or not sha:
            raise FidelityError(f"manifest entry missing relpath/sha256: {entry!r}")
        manifest[relpath] = sha
    return manifest


def _sibling_cross_checks(batch_paths: list[Path]) -> list[Path]:
    """Every sibling ``*.jsonl`` in the batches' parent dirs, minus the batches."""
    cross: dict[str, Path] = {}
    for batch in batch_paths:
        parent = batch.resolve().parent
        if not parent.is_dir():
            continue
        for candidate in sorted(parent.glob("*.jsonl")):
            resolved = candidate.resolve()
            if resolved in {b.resolve() for b in batch_paths}:
                continue
            cross[str(resolved)] = resolved
    return sorted(cross.values())


def _preload_ids(paths: list[Path]) -> dict[str, str]:
    ids: dict[str, str] = {}
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise FidelityError(f"cannot read cross-check batch: {path} ({exc})") from exc
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise FidelityError(f"cross-check batch {path.name} has a non-JSON line: {exc}") from exc
            ku_id = record.get("knowledge_unit_id")
            if ku_id:
                ids[ku_id] = path.name
    return ids


def check_batches(
    batch_paths: list[str | Path],
    vault_id: str,
    vault_root: str | Path,
    manifest_path: str | Path,
    *,
    kus_schema: str | Path | None = None,
    cross_check_paths: list[str | Path] | None = None,
    allow_processed: bool = False,
) -> dict:
    """Run the full fidelity check over one or more batches of a single vault.

    Returns a report dict; ``ok`` is True only when every check passes for
    every record of every batch. Raises :class:`FidelityError` for unusable
    inputs (missing batch/manifest/vault root). Never writes to the vault.
    """
    if not vault_id or not vault_id.strip():
        raise FidelityError("vault_id must be a non-empty stable identifier")
    root_path = Path(vault_root)
    if not root_path.is_dir():
        raise FidelityError(f"vault root is not a directory: {root_path}")

    resolved_batches: list[Path] = []
    for bp in batch_paths:
        path = Path(bp)
        if not path.is_file():
            raise FidelityError(f"batch file does not exist: {path}")
        resolved_batches.append(path)

    manifest = _load_manifest(Path(manifest_path))

    if cross_check_paths is None:
        cross_paths = _sibling_cross_checks(resolved_batches)
    else:
        cross_paths = [Path(p) for p in cross_check_paths]
    cross_ids = _preload_ids(cross_paths)

    errors: list[str] = []
    batch_reports: list[dict] = []
    all_ids: dict[str, str] = {}  # id -> batch name (across the checked batches)
    id_collisions: list[dict] = []

    for batch in resolved_batches:
        try:
            text = batch.read_text(encoding="utf-8")
        except OSError as exc:
            raise FidelityError(f"cannot read batch: {batch} ({exc})") from exc
        records = [json.loads(line) for line in text.splitlines() if line.strip()]

        b_errors: list[str] = []
        ids: set[str] = set()
        excerpt_exact = 0
        hash_ok = 0
        structurally_pure = 0
        manifest_agree = 0
        file_cache: dict[str, tuple[list[str], str, set[int]]] = {}  # relpath -> (lines, sha, heading_lines)

        schema_valid = None
        if kus_schema is not None:
            schema_report = validate_ku_file(batch, kus_schema)
            schema_valid = bool(schema_report.get("valid"))
            if not schema_valid:
                for err in schema_report.get("errors", []):
                    b_errors.append(f"schema: {err}")

        for record in records:
            ku_id = record.get("knowledge_unit_id")
            if ku_id in ids:
                b_errors.append(f"duplicate knowledge_unit_id within batch: {ku_id}")
            if ku_id in cross_ids:
                id_collisions.append({"ku_id": ku_id, "checked_batch": batch.name, "existing_batch": cross_ids[ku_id]})
                b_errors.append(
                    f"knowledge_unit_id collides across batches: {ku_id} (also in {cross_ids[ku_id]})"
                )
            if ku_id in all_ids:
                b_errors.append(
                    f"knowledge_unit_id collides across checked batches: {ku_id} (also in {all_ids[ku_id]})"
                )
            ids.add(ku_id)
            all_ids[ku_id] = batch.name

            source_id = record.get("source_id")
            if not str(source_id).startswith(f"{vault_id}:"):
                b_errors.append(f"{ku_id}: source_id vault prefix is not '{vault_id}': {source_id}")

            relpath = record.get("source_path")
            if not isinstance(relpath, str) or not relpath:
                b_errors.append(f"{ku_id}: source_path missing or not a string: {relpath!r}")
                relpath = None
            elif source_id != f"{vault_id}:{relpath}":
                b_errors.append(f"{ku_id}: source_id/source_path mismatch")

            disposition = record.get("disposition")
            vs = record.get("verification_status")
            vs_ok = isinstance(vs, dict) and all(vs.get(k) == v for k, v in FRESH_VERIFICATION_STATUS.items())
            if not allow_processed:
                if disposition != "Unaccounted":
                    b_errors.append(f"{ku_id}: disposition is {disposition!r}, expected 'Unaccounted'")
                if record.get("overlap_type") is not None:
                    b_errors.append(
                        f"{ku_id}: overlap_type must be null in a fresh batch ({record['overlap_type']})"
                    )
                if not vs_ok:
                    b_errors.append(f"{ku_id}: verification_status not the fresh-batch form: {vs!r}")
                if disposition == "Unaccounted" and record.get("overlap_type") is None and vs_ok:
                    structurally_pure += 1
            else:
                structurally_pure += 1

            if relpath and relpath not in file_cache:
                src = root_path / relpath
                if not src.is_file():
                    b_errors.append(f"{ku_id}: source file missing under vault root: {relpath}")
                    file_cache[relpath] = ([], "", set())
                else:
                    raw = src.read_bytes()
                    src_text = raw.decode("utf-8")
                    sha = hashlib.sha256(raw).hexdigest()
                    structure = mdextract.extract_structure_text(src_text)
                    heading_lines = {h["line"] for h in structure["headings"]}
                    file_cache[relpath] = (src_text.splitlines(), sha, heading_lines)

            if relpath is None:
                continue  # source_path unusable: already recorded as an error

            file_lines, disk_sha, heading_lines = file_cache[relpath]
            if disk_sha:
                if record.get("source_file_hash") != disk_sha:
                    b_errors.append(f"{ku_id}: source_file_hash mismatch for {relpath}")
                if manifest.get(relpath) == disk_sha:
                    manifest_agree += 1
                else:
                    b_errors.append(
                        f"{ku_id}: source hash disagrees with baseline manifest for {relpath}"
                    )

            start, end = record.get("line_start"), record.get("line_end")
            if not (1 <= start <= end <= len(file_lines)):
                b_errors.append(
                    f"{ku_id}: line range {start}-{end} outside file {relpath} ({len(file_lines)} lines)"
                )
                continue

            reconstructed = "\n".join(file_lines[start - 1 : end])
            if reconstructed == record.get("excerpt"):
                excerpt_exact += 1
            else:
                b_errors.append(f"{ku_id}: excerpt not byte-exact for {relpath} lines {start}-{end}")

            if hashlib.sha256(str(record.get("excerpt", "")).encode("utf-8")).hexdigest() == record.get(
                "excerpt_hash"
            ):
                hash_ok += 1
            else:
                b_errors.append(f"{ku_id}: excerpt_hash mismatch")

            crossed = heading_lines & set(range(start, end + 1))
            if record.get("unit_type") == "empty_section":
                # design contract (kuextract): an empty_section unit sits
                # exactly ON its heading line — the line IS the unit — so the
                # generic no-heading-crossing rule does not apply; instead the
                # span must be exactly one heading line.
                if start != end or start not in heading_lines:
                    b_errors.append(
                        f"{ku_id}: empty_section span must be exactly one heading line "
                        f"(got {start}-{end}; heading lines: {sorted(heading_lines)[:20]})"
                    )
            elif crossed:
                b_errors.append(f"{ku_id}: span crosses heading line(s) {sorted(crossed)} in {relpath}")

        batch_report = {
            "batch": str(batch),
            "records_total": len(records),
            "excerpt_byte_exact": excerpt_exact,
            "excerpt_hash_valid": hash_ok,
            "structurally_pure": structurally_pure,
            "manifest_agree": manifest_agree,
            "schema_valid": schema_valid,
            "unique_ids_in_batch": len(ids),
            "files_covered": sorted(file_cache),
            "errors": b_errors,
            "ok": not b_errors,
        }
        batch_reports.append(batch_report)
        errors.extend(b_errors)

    total_records = sum(b["records_total"] for b in batch_reports)
    report = {
        "command": "ku-fidelity",
        "ok": not errors,
        "vault_id": vault_id,
        "vault_root": str(vault_root),
        "manifest": str(manifest_path),
        "allow_processed": allow_processed,
        "batches_checked": len(batch_reports),
        "records_total": total_records,
        "records_with_errors": len(errors),
        "batches": batch_reports,
        "cross_check_batches": [str(p) for p in cross_paths],
        "cross_check_ids_preloaded": len(cross_ids),
        "ids_unique_across_checked": len(all_ids),
        "id_collisions": id_collisions,
        "denominators": {
            "records": "every record in every checked batch",
            "checks": "schema (when supplied), id uniqueness (within + cross-batch), vault prefix, "
            "source_id/path agreement, source_file_hash vs disk and manifest, structural purity, "
            "excerpt byte-fidelity, excerpt hash, span bounds, heading-crossing",
            "exclusions": "cross-check batches are only preload-checked for id collisions, not fidelity",
        },
        "limitations": [
            "byte-exact excerpt verification proves mechanical fidelity to source lines, "
            "not semantic completeness or correctness of the segmentation itself",
            "heading-boundary authority is mdextract.extract_structure_text; setext headings "
            "remain unsupported (L-05)",
        ],
    }
    return report

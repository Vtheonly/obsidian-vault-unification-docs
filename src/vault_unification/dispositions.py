"""Rule-driven disposition assignment (DISP-001, ADR-0014 pipeline step).

Computes exactly one disposition per knowledge unit from:
  * v2 concept dossiers (dossier membership -> Consolidated),
  * the committed file-level synthesis mapping
    (state/synthesis/file-mapping-v1.jsonl: destinations + feeder counts),
  * an explicit, documented exception table (individually reviewed units).

The output is a disposition LEDGER: a committed, append-only JSONL decision
record (one record per KU). The KU batch files stay untouched — the
ADR-0007/0009 pattern: the extraction store is immutable, decisions live in
committed JSONL, and the derived registry applies them as overlays via
``kureg-apply-dispositions``.

Rules (priority order; every rule records destinations from the file
mapping's canonical paths for the KU's source file):
  DISP-R4 archival context: the KU's source file maps into the internal
        context archive area ("20 - Vault and Project Context") ->
        Contextualized (the area-20 files were individually reviewed in
        session 19; ordinary notes never narrate merges, SOURCE_POLICY).
  DISP-X  exceptions: the explicit EXCEPTIONS table (each entry carries its
        own rationale; individually reviewed).
  DISP-R1 dossier concept member: the KU participates in >= 1 v2 dossier
        concept -> Consolidated (its evidence consolidates into the
        concept's canonical treatment at synthesis; source_refs carry the
        concept ids so synthesis can pull the full concept evidence).
  DISP-R2 consolidated note: the KU's source file is one of several feeding
        its canonical note -> Consolidated.
  DISP-R3 preserved note: the KU's source file is the sole feeder of its
        canonical note -> Preserved (content rewritten substantially intact).

Known limitations (documented, non-exhaustive):
  * Dispositions are planning statements with destinations; semantic
    verification that the destination note actually preserves the content
    happens at the synthesis gates (M6/M7), not here.
  * No Superseded dispositions are bulk-assigned: Superseded requires
    per-unit evidence that unique details are preserved elsewhere
    (KNOWLEDGE_AND_PROVENANCE invariant 3) — a semantic judgment reserved
    for synthesis-time individual review. The only Superseded entries are
    the individually reviewed exception-table units below.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

DISPOSITIONS = (
    "Preserved",
    "Consolidated",
    "Contextualized",
    "Superseded",
    "Needs review",
    "Unaccounted",
)

CONTEXT_AREA = "20 - Vault and Project Context"

# The exception table is keyed by (source_id, optional unit_type or excerpt
# substring) rather than ku_id so it stays stable across re-extractions;
# every entry carries its own individually reviewed rationale.
EXCEPTION_KEYS = [
    {
        "source_id": "ai-course:09 - Quizzes and Question Banks/"
                     "03. Question Series/Qs4.md",
        "match_excerpt_substring": "use this in the 2d to 3d",
        "disposition": "Contextualized",
        "rule_id": "DISP-X1",
        "rationale": "Qs4.md is a 25-byte content-free planning stub; its "
                     "planning intent (use these questions in the 2D-to-3D "
                     "transition) is preserved as context of the Question "
                     "Series note (individually reviewed, session 19).",
    },
    {
        "source_id": "ai-course:03 - Machine Learning/03.3 - K-Nearest "
                     "Neighbors (KNN)/01. K-Nearest Neighbors (KNN) - "
                     "Comprehensive.md",
        "match_unit_type": "empty_section",
        "disposition": "Superseded",
        "rule_id": "DISP-X2",
        "rationale": "'END OF FILE' marker heading — a source-formatting "
                     "artifact (finding F-0014), not knowledge; superseded by "
                     "the note's real structure. The marker text itself is "
                     "preserved verbatim in this registry record and in the "
                     "immutable source, so no unique detail is lost.",
    },
    {
        "source_id": "ai-course:04 - Neural Networks and Deep Learning "
                     "Foundations/04.1 - Neural Network Basics/01. "
                     "Fundamentals of Neural Networks.md",
        "match_unit_type": "empty_section",
        "disposition": "Superseded",
        "rule_id": "DISP-X2",
        "rationale": "'File Name' marker heading — a source-formatting "
                     "artifact (finding F-0014), not knowledge; superseded by "
                     "the note's real structure. The marker text itself is "
                     "preserved verbatim in this registry record and in the "
                     "immutable source, so no unique detail is lost.",
    },
]

ASSIGNED_BY = "vu assign-dispositions (DISP-001 session 19 orchestrator)"


class DispositionError(Exception):
    """Raised on invalid inputs or contract violations (fail visibly)."""


def load_jsonl(path: str | Path) -> list[dict]:
    records = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise DispositionError(
                        f"{path}:{lineno}: invalid JSON: {exc}"
                    ) from exc
    return records


def _exception_lookup(ku: dict) -> dict | None:
    for entry in EXCEPTION_KEYS:
        if ku["source_id"] != entry["source_id"]:
            continue
        if "match_unit_type" in entry and ku.get("unit_type") != entry["match_unit_type"]:
            continue
        if "match_excerpt_substring" in entry and entry[
            "match_excerpt_substring"
        ] not in (ku.get("excerpt") or ""):
            continue
        return entry
    return None


def assign_dispositions(
    ku_batches: list[str | Path],
    dossiers: list[str | Path],
    file_mapping: str | Path,
    *,
    date: str = "2026-11-01",
) -> tuple[list[dict], dict]:
    """Compute the disposition ledger + accounting report.

    Inputs: committed KU batches, committed v2 dossier JSON files, and the
    committed file-level synthesis mapping JSONL. Returns (records, report);
    records are sorted by ku_id and every KU in the batches receives exactly
    one record (a missing or duplicated outcome raises DispositionError).
    """
    # ---- load KUs ---------------------------------------------------------
    kus: dict[str, dict] = {}
    for batch in ku_batches:
        for rec in load_jsonl(batch):
            kid = rec["knowledge_unit_id"]
            if kid in kus:
                raise DispositionError(f"duplicate KU id across batches: {kid}")
            kus[kid] = rec

    # ---- load dossier concept membership (v2 dossiers) --------------------
    concept_of: dict[str, list[str]] = {}
    dossier_domains: dict[str, str] = {}
    for dpath in dossiers:
        dossier = json.loads(Path(dpath).read_text(encoding="utf-8"))
        if dossier.get("version") != "v2":
            raise DispositionError(
                f"{dpath}: expected a v2 dossier (extension records included)"
            )
        domain = dossier["domain"]
        for concept in dossier["concepts"]:
            dossier_domains[concept["concept_id"]] = domain
            for kid in concept["ku_ids"]:
                concept_of.setdefault(kid, []).append(concept["concept_id"])

    # ---- load the file-level synthesis mapping ----------------------------
    mapping: dict[str, dict] = {}
    for rec in load_jsonl(file_mapping):
        key = f"{rec['vault']}:{rec['source_path']}"
        if key in mapping:
            raise DispositionError(f"duplicate mapping record for {key}")
        mapping[key] = rec

    note_feeders: dict[str, set] = {}
    for key, rec in mapping.items():
        for cp in rec["canonical_paths"]:
            note_feeders.setdefault(cp, set()).add(key)

    # ---- rule application --------------------------------------------------
    records: list[dict] = []
    by_disposition: dict[str, int] = {d: 0 for d in DISPOSITIONS}
    by_rule: dict[str, int] = {}
    by_area: dict[str, dict[str, int]] = {}
    problems: list[str] = []
    for kid in sorted(kus):
        ku = kus[kid]
        key = ku["source_id"]
        entry = mapping.get(key)
        if entry is None:
            problems.append(f"no file-mapping record for source {key}")
            continue
        destinations = [{"path": cp, "heading": None} for cp in entry["canonical_paths"]]
        areas = tuple(sorted({cp.split("/", 1)[0] for cp in entry["canonical_paths"]}))

        # priority: exceptions -> archival context -> dossier -> note shape
        exc = _exception_lookup(ku)
        if exc is not None:
            disposition = exc["disposition"]
            rule_id = exc["rule_id"]
            rationale = exc["rationale"]
            source_refs = []
        elif CONTEXT_AREA in areas:
            disposition = "Contextualized"
            rule_id = "DISP-R4"
            rationale = (
                "source file is an archival vault/project-context document "
                "(individually reviewed, session 19): retained as labeled "
                "internal context — "
                + entry.get("rationale", "")
            )
            source_refs = []
        elif kid in concept_of:
            disposition = "Consolidated"
            rule_id = "DISP-R1"
            concepts = sorted(concept_of[kid])
            domains = sorted({dossier_domains[c] for c in concepts})
            rationale = (
                f"participates in {len(concepts)} v2 dossier concept(s) "
                f"({', '.join(concepts[:5])}{'…' if len(concepts) > 5 else ''}; "
                f"domain(s): {', '.join(domains)}): its evidence consolidates "
                "into the concept's canonical treatment at synthesis, with "
                "unique details preserved per the dossier's category "
                "assignments"
            )
            source_refs = concepts
        elif any(len(note_feeders[cp]) > 1 for cp in entry["canonical_paths"]):
            disposition = "Consolidated"
            rule_id = "DISP-R2"
            feed_note = next(cp for cp in entry["canonical_paths"]
                             if len(note_feeders[cp]) > 1)
            rationale = (
                f"source file is one of {len(note_feeders[feed_note])} "
                f"feeding '{feed_note}' (file-mapping v1): content merges "
                "into that canonical note at synthesis"
            )
            source_refs = []
        else:
            disposition = "Preserved"
            rule_id = "DISP-R3"
            rationale = (
                "source file is the sole feeder of its canonical note "
                f"('{entry['canonical_paths'][0]}'): content is rewritten "
                "substantially intact at synthesis"
            )
            source_refs = []

        if disposition == "Superseded" and not rationale:
            problems.append(f"{kid}: Superseded without rationale")

        records.append({
            "ku_id": kid,
            "disposition": disposition,
            "destinations": destinations,
            "rule_id": rule_id,
            "rationale": rationale,
            "source_refs": source_refs,
            "assigned_by": ASSIGNED_BY,
            "date": date,
        })
        by_disposition[disposition] += 1
        by_rule[rule_id] = by_rule.get(rule_id, 0) + 1
        for area in areas:
            area_stats = by_area.setdefault(area, {d: 0 for d in DISPOSITIONS})
            area_stats[disposition] += 1

    if problems:
        raise DispositionError(
            "contract violations: " + "; ".join(problems[:5])
            + (f" (+{len(problems) - 5} more)" if len(problems) > 5 else "")
        )
    if len(records) != len(kus):
        raise DispositionError(
            f"ledger has {len(records)} records for {len(kus)} KUs"
        )
    if by_disposition["Unaccounted"] or by_disposition["Needs review"]:
        raise DispositionError(
            "rule engine must not emit Unaccounted or Needs review "
            f"(got {by_disposition['Unaccounted']} / "
            f"{by_disposition['Needs review']})"
        )

    report = {
        "kus_total": len(records),
        "by_disposition": by_disposition,
        "by_rule": dict(sorted(by_rule.items())),
        "by_area": by_area,
        "dossier_member_kus": len(concept_of),
        "context_area_kus": sum(by_area.get(CONTEXT_AREA, {}).values()),
        "exception_kus": sum(1 for r in records if r["rule_id"].startswith("DISP-X")),
        "notes_total": len(note_feeders),
        "multi_destination_kus": sum(1 for r in records if len(r["destinations"]) > 1),
    }
    return records, report


def write_ledger(records: list[dict], out_path: str | Path) -> str:
    """Write the ledger JSONL (sorted by ku_id); returns the sha256."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
    return hashlib.sha256(out_path.read_bytes()).hexdigest()

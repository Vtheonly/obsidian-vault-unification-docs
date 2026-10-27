"""Note quality assessment, drift detection and batch gating (FRAME-002, CAP-019).

Deterministic, evidence-carrying quality measurement for generated notes,
per the Phase 0 quality-tooling requirements. The design directly targets
the quality-degradation failure mode observed in large AI vaults: first
notes polished, later notes thin — the tool must DETECT that drift with
measurable evidence, not assume it away.

SCOPE — DETERMINISTIC MEASUREMENT ONLY (no pseudo-semantic scoring):
- Every dimension score is computed from countable document features with
  the evidence attached (which lines, which counts, which thresholds).
- Semantic adequacy (is the explanation CORRECT and COMPLETE for its
  concept?) is a review decision; this tool prepares the evidence review
  needs (coverage ratios, uncovered source terms, drift tables) and never
  replaces it. There is deliberately no "AI judge" score here.
- Scores are comparable across iterations because the standard definitions
  are versioned (STANDARDS_VERSION) and deterministic.

NOTE TYPES (a short reference note and a mathematical tutorial are held to
different expectations — NOT to different slack):
- concept        — a definition + boundaries + intuition + links note
- reference      — lookup material: syntax, tables, parameters
- tutorial       — step-by-step teaching with worked examples
- derivation     — mathematical derivation with rigor
- overview       — map-of-the-territory note
- example        — worked example / case study
- Unknown types fall back to 'generic' with conservative expectations.

DIMENSIONS (check ids are stable for the repair loop):
- structure            — headings, intro section, heading-hierarchy sanity
- definitions          — definition patterns present where the type demands
- depth                — word/sentence/paragraph depth vs type band
- math_rigor           — display/inline math + derivation markers (derivation)
- examples             — example markers / code blocks where demanded
- source_coverage      — mapped source KU terms present in the note (needs a
                         provenance mapping; without one this dimension is
                         reported as 'unmeasured', never guessed)
- provenance           — source attribution present (frontmatter/links)
- links                — internal links present and resolving (lint evidence)
- editorial            — heading-case consistency, math-delimiter style,
                         list punctuation consistency

DRIFT DETECTION (:func:`detect_drift`):
- Groups notes by type, orders them by generation sequence (frontmatter
  'created_index'/'batch', else filename natural order), splits into first
  and last thirds, and compares per-dimension means. A dimension drifts
  when the last-third mean drops by more than ``rel_drop`` (default 15%)
  AND the absolute gap exceeds ``abs_drop`` (default 0.10), or when the
  whole-note pass rate falls monotonically across tertiles. Output carries
  per-dimension evidence (which notes, which deltas) — no black boxes.

GATES (:func:`batch_gate`):
- expected-notes present (manifest), per-note dimension thresholds met or
  explicitly waived with reason, artifactlint errors = 0, provenance
  accounted, drift explained. A high average can never hide a failing
  note: per-note failures are enumerated individually.
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

from .artifactlint import lint_file
from .search import boundary_pattern

__all__ = [
    "QualityError",
    "STANDARDS_VERSION",
    "NOTE_TYPES",
    "assess_note",
    "assess_tree",
    "detect_drift",
    "batch_gate",
    "load_provenance",
]

STANDARDS_VERSION = "1.0.0"


class QualityError(Exception):
    """Raised for invalid quality-tooling inputs."""


# ---------------------------------------------------------------------------
# note-type standards: dimension -> (weight, min, max) per type
#
# min/max are EXPECTATION BANDS on the 0..1 dimension score, not hard pass
# marks; the hard pass mark for a batch is set in the gate call and must be
# justified per project phase. weights sum to 1.0 per type.

_TYPE_STANDARDS: dict[str, dict] = {
    "concept": {
        "dimensions": {
            "structure": (0.15, 0.5, 1.0),
            "definitions": (0.20, 0.5, 1.0),
            "depth": (0.20, 0.4, 1.0),
            "math_rigor": (0.05, 0.0, 1.0),
            "examples": (0.10, 0.0, 1.0),
            "source_coverage": (0.15, 0.6, 1.0),
            "provenance": (0.10, 0.5, 1.0),
            "links": (0.05, 0.25, 1.0),
            "editorial": (0.05, 0.4, 1.0),
        }
    },
    "reference": {
        "dimensions": {
            "structure": (0.20, 0.5, 1.0),
            "definitions": (0.05, 0.0, 1.0),
            "depth": (0.10, 0.2, 1.0),
            "math_rigor": (0.05, 0.0, 1.0),
            "examples": (0.10, 0.0, 1.0),
            "source_coverage": (0.20, 0.6, 1.0),
            "provenance": (0.20, 0.5, 1.0),
            "links": (0.10, 0.25, 1.0),
            "editorial": (0.05, 0.4, 1.0),
        }
    },
    "tutorial": {
        "dimensions": {
            "structure": (0.15, 0.5, 1.0),
            "definitions": (0.10, 0.25, 1.0),
            "depth": (0.20, 0.5, 1.0),
            "math_rigor": (0.10, 0.0, 1.0),
            "examples": (0.20, 0.5, 1.0),
            "source_coverage": (0.15, 0.6, 1.0),
            "provenance": (0.05, 0.25, 1.0),
            "links": (0.05, 0.25, 1.0),
            "editorial": (0.05, 0.4, 1.0),
        }
    },
    "derivation": {
        "dimensions": {
            "structure": (0.10, 0.4, 1.0),
            "definitions": (0.05, 0.0, 1.0),
            "depth": (0.15, 0.4, 1.0),
            "math_rigor": (0.35, 0.6, 1.0),
            "examples": (0.05, 0.0, 1.0),
            "source_coverage": (0.15, 0.6, 1.0),
            "provenance": (0.10, 0.5, 1.0),
            "links": (0.05, 0.25, 1.0),
            "editorial": (0.05, 0.4, 1.0),
        }
    },
    "overview": {
        "dimensions": {
            "structure": (0.20, 0.5, 1.0),
            "definitions": (0.05, 0.0, 1.0),
            "depth": (0.10, 0.3, 1.0),
            "math_rigor": (0.0, 0.0, 1.0),
            "examples": (0.05, 0.0, 1.0),
            "source_coverage": (0.10, 0.5, 1.0),
            "provenance": (0.10, 0.5, 1.0),
            "links": (0.40, 0.6, 1.0),
            "editorial": (0.05, 0.4, 1.0),
        }
    },
    "example": {
        "dimensions": {
            "structure": (0.10, 0.3, 1.0),
            "definitions": (0.05, 0.0, 1.0),
            "depth": (0.15, 0.4, 1.0),
            "math_rigor": (0.10, 0.0, 1.0),
            "examples": (0.30, 0.6, 1.0),
            "source_coverage": (0.15, 0.6, 1.0),
            "provenance": (0.10, 0.5, 1.0),
            "links": (0.05, 0.25, 1.0),
            "editorial": (0.05, 0.4, 1.0),
        }
    },
    "generic": {
        "dimensions": {
            "structure": (0.15, 0.4, 1.0),
            "definitions": (0.10, 0.0, 1.0),
            "depth": (0.20, 0.3, 1.0),
            "math_rigor": (0.05, 0.0, 1.0),
            "examples": (0.10, 0.0, 1.0),
            "source_coverage": (0.20, 0.5, 1.0),
            "provenance": (0.10, 0.5, 1.0),
            "links": (0.10, 0.25, 1.0),
            "editorial": (0.05, 0.4, 1.0),
        }
    },
}

NOTE_TYPES = tuple(sorted(_TYPE_STANDARDS))

# depth bands per type: (min_words_floor, target_words, max_words_cap)
# used for the depth score; floors are LOW deliberately — the drift detector
# cares about RELATIVE decline between comparable notes, and hard floors
# would encode assumptions this tool cannot defend.
_DEPTH_BANDS = {
    "concept": (80, 350, 1500),
    "reference": (40, 180, 1200),
    "tutorial": (200, 700, 2500),
    "derivation": (150, 550, 2500),
    "overview": (100, 400, 1500),
    "example": (100, 400, 1500),
    "generic": (60, 300, 2000),
}

_DEFINITION_RE = re.compile(
    r"\b(?:is|are)\s+(?:a|an|the)\s+\w|defined\s+as|refers\s+to|denotes|"
    r"means\b|definition\s+of|call(?:ed)?\s+\w+\s+(?:a|an|the)\b",
    re.IGNORECASE,
)
_EXAMPLE_RE = re.compile(
    r"\bexample\b|\bfor\s+instance\b|\be\.g\.|worked\s+(?:example|case)|"
    r"\bcase\s+study\b|\bin\s+practice\b|let's\s+|\blet\s+us\b|consider\s+the",
    re.IGNORECASE,
)
_DERIVATION_RE = re.compile(
    r"∂|∇|(?<![A-Za-z])d[A-Za-z]/d[A-Za-z]|derivation|derive[sd]?|therefore|"
    r"it\s+follows|substitut\w*|simplif\w*|which\s+gives|=\s*$",
    re.IGNORECASE,
)


def _note_type(frontmatter: dict | None, fallback: str = "generic") -> str:
    """Infer the note type from frontmatter 'type', else fallback."""
    if frontmatter:
        t = str(frontmatter.get("type", "")).strip().lower()
        if t in _TYPE_STANDARDS:
            return t
    return fallback if fallback in _TYPE_STANDARDS else "generic"


def load_provenance(path: str | Path) -> dict[str, list[str]]:
    """Load a note->KU provenance mapping (JSONL: {note, ku_ids})."""
    records: dict[str, list[str]] = {}
    p = Path(path)
    if not p.is_file():
        raise QualityError(f"provenance mapping not found: {p}")
    with p.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                raise QualityError(f"provenance line {lineno} is not JSON: {exc}") from exc
            note = rec.get("note") or rec.get("path") or rec.get("file")
            kus = rec.get("ku_ids") or rec.get("kus")
            if not note or not isinstance(kus, list):
                raise QualityError(f"provenance line {lineno} must carry 'note' and 'ku_ids'")
            records[str(note)] = [str(k) for k in kus]
    return records


def _ku_terms(batches: list[Path] | None) -> dict[str, list[str]]:
    """Build ku_id -> key terms (title + heading path tokens) from batches."""
    terms: dict[str, list[str]] = {}
    for batch in batches or []:
        with Path(batch).open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                ku_id = rec.get("ku_id") or rec.get("id")
                if not ku_id:
                    continue
                candidates: list[str] = []
                for field in ("topic", "title", "heading_path", "heading"):
                    value = rec.get(field)
                    if isinstance(value, list):
                        value = " ".join(str(v) for v in value)
                    if isinstance(value, str) and value.strip():
                        candidates.append(value.strip())
                excerpt = rec.get("excerpt") or rec.get("text") or ""
                if isinstance(excerpt, str) and excerpt.strip() and not candidates:
                    candidates.append(excerpt.strip()[:200])
                # extract salient tokens: keep tokens >= 4 chars, not stopwords
                toks: list[str] = []
                for cand in candidates:
                    for tok in re.findall(r"[A-Za-z][A-Za-z\-]{3,}", cand):
                        low = tok.lower()
                        if low not in ("this", "that", "with", "from", "which", "where", "when", "what"):
                            toks.append(low)
                if toks:
                    terms[str(ku_id)] = sorted(set(toks))
    return terms


def _score_structure(structure: dict, lint_report: dict) -> tuple[float, list[str]]:
    evidence: list[str] = []
    heads = structure.get("headings") or []
    score = 0.0
    if heads:
        score += 0.3
        evidence.append(f"{len(heads)} headings")
    else:
        evidence.append("no headings")
    if len(heads) >= 2:
        score += 0.2
        evidence.append("sectioned (>=2 headings)")
    # intro: some content before the first heading OR after H1 before H2
    if heads:
        first = heads[0]["line"]
        intro = [ln for ln in structure.get("_pretext_lines", [])[: first - 1] if ln.strip()]
        if intro:
            score += 0.2
            evidence.append(f"intro paragraph before first heading ({len(intro)} lines)")
    else:
        score += 0.2
        evidence.append("single-section note (no heading structure required)")
    skips = [d for d in lint_report["defects"] if d["check"] == "HEADING_SKIP"]
    empty = [d for d in lint_report["defects"] if d["check"] == "EMPTY_SECTION"]
    score += 0.3 * (1.0 if not skips else 0.5)
    if skips:
        evidence.append(f"{len(skips)} heading hierarchy skips")
    if empty:
        evidence.append(f"{len(empty)} empty sections")
    return min(1.0, score), evidence


def _score_definitions(text: str) -> tuple[float, list[str]]:
    hits = _DEFINITION_RE.findall(text)
    score = 1.0 if hits else 0.0
    return score, [f"{len(hits)} definition-pattern matches"] if hits else ["no definition patterns detected"]


def _score_depth(text: str, ntype: str) -> tuple[float, list[str]]:
    words = len(re.findall(r"\S+", text))
    para_blocks = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    lo, target, hi = _DEPTH_BANDS.get(ntype, _DEPTH_BANDS["generic"])
    if words < lo:
        score = max(0.0, words / lo) * 0.5
    elif words <= hi:
        score = 0.5 + 0.5 * min(1.0, words / target)
    else:
        score = max(0.5, 1.0 - 0.25 * (words - hi) / hi)
    # paragraph discipline: proportion of multi-sentence paragraphs
    multi = [p for p in para_blocks if len(re.split(r"(?<=[.!?])\s+", p)) >= 3]
    para_ratio = len(multi) / len(para_blocks) if para_blocks else 0.0
    score = 0.7 * score + 0.3 * para_ratio
    evidence = [
        f"{words} words (band {lo}..{hi}, target {target})",
        f"{len(para_blocks)} paragraphs, {len(multi)} with >=3 sentences (ratio {para_ratio:.2f})",
        f"{len(sentences)} sentences",
    ]
    return min(1.0, score), evidence


def _score_math(structure: dict, text: str) -> tuple[float, list[str]]:
    blocks = len(structure.get("math_blocks") or [])
    inline = structure.get("inline_math_count", 0)
    markers = len(_DERIVATION_RE.findall(text))
    evidence = [f"{blocks} display math blocks", f"{inline} inline math", f"{markers} derivation markers"]
    score = 0.0
    if blocks:
        score += 0.5
    if inline:
        score += 0.2
    if markers >= 2:
        score += 0.3
    elif markers == 1:
        score += 0.15
    return min(1.0, score), evidence


def _score_examples(text: str, structure: dict) -> tuple[float, list[str]]:
    markers = _EXAMPLE_RE.findall(text)
    code = [f for f in structure.get("code_fences") or [] if (f.get("info") or "").strip()]
    evidence = [f"{len(markers)} example markers", f"{len(code)} labeled code blocks"]
    score = 0.0
    if markers:
        score += 0.6
    if code:
        score += 0.4
    return min(1.0, score), evidence


def _score_source_coverage(
    note_key: str | None, provenance: dict[str, list[str]], ku_terms: dict[str, list[str]], text: str
) -> tuple[float | None, list[str], list[dict]]:
    """Coverage = fraction of mapped KUs whose key terms appear in the note.

    Returns (score, evidence, uncovered_records). Score is None when no
    provenance mapping covers this note — the dimension is 'unmeasured',
    NEVER guessed as 0 or 1.
    """
    if not note_key or note_key not in provenance:
        return None, ["no provenance mapping for this note (dimension unmeasured)"], []
    ku_ids = provenance[note_key]
    covered = 0
    uncovered: list[dict] = []
    for ku_id in ku_ids:
        terms = ku_terms.get(ku_id)
        if terms is None:
            uncovered.append({"ku_id": ku_id, "reason": "ku_id not found in provided batches"})
            continue
        matched = [t for t in terms if boundary_pattern(t).search(text)]
        if matched:
            covered += 1
        else:
            uncovered.append({"ku_id": ku_id, "reason": "no key term found in note", "terms": terms[:12]})
    score = covered / len(ku_ids) if ku_ids else None
    evidence = [f"{covered}/{len(ku_ids)} mapped KUs have >=1 key term present in the note"]
    return score, evidence, uncovered


def _score_provenance(frontmatter: dict | None, text: str) -> tuple[float, list[str]]:
    evidence: list[str] = []
    score = 0.0
    if frontmatter:
        src = frontmatter.get("sources") or frontmatter.get("source") or frontmatter.get("provenance")
        if src:
            score += 0.6
            evidence.append("frontmatter carries source attribution")
    if re.search(r"\[\[|\]\(|source[s]?[:：]", text):
        score += 0.4
        evidence.append("in-text links or source mentions present")
    if score == 0.0:
        evidence.append("no source attribution found (frontmatter or text)")
    return min(1.0, score), evidence


def _score_links(structure: dict, lint_report: dict) -> tuple[float, list[str]]:
    total = len(structure.get("wikilinks") or []) + len(structure.get("embeds") or [])
    broken = [d for d in lint_report["defects"] if d["check"].startswith("LINK_")]
    if total == 0:
        return 0.0, ["no internal links"]
    score = max(0.0, 1.0 - len(broken) / total)
    evidence = [f"{total} internal links", f"{len(broken)} link defects"]
    return score, evidence


def _score_editorial(structure: dict, text: str, lint_report: dict) -> tuple[float, list[str]]:
    evidence: list[str] = []
    score = 1.0
    heads = [h["text"] for h in structure.get("headings") or []]
    if len(heads) >= 3:
        title_case = sum(1 for h in heads if h == h.title() or (h[:1].isupper() and not h.islower()))
        ratio = title_case / len(heads)
        if 0.25 < ratio < 0.75:
            score -= 0.2
            evidence.append(f"heading case style mixed ({title_case}/{len(heads)} title-case)")
    if any(d["check"] == "MATH_DELIM_STYLE_MIXED" for d in lint_report["defects"]):
        score -= 0.2
        evidence.append("math delimiter styles mixed")
    if any(d["check"] == "LIST_INDENT_MIXED" for d in lint_report["defects"]):
        score -= 0.2
        evidence.append("list indentation style mixed")
    if not evidence:
        evidence.append("no editorial inconsistencies detected by deterministic checks")
    return max(0.0, min(1.0, score)), evidence


def assess_note(
    path: str | Path,
    *,
    note_key: str | None = None,
    provenance: dict[str, list[str]] | None = None,
    ku_batches: list[str | Path] | None = None,
    vault_root: str | Path | None = None,
    link_context: dict | None = None,
    type_fallback: str = "generic",
) -> dict:
    """Assess one note against its type standard; returns dimension scores,
    evidence, band verdicts and an overall weighted score."""
    from .mdextract import extract_structure_text

    file_path = Path(path)
    if not file_path.is_file():
        raise QualityError(f"note not found: {file_path}")
    text = file_path.read_text(encoding="utf-8")
    structure = extract_structure_text(text)
    structure["_pretext_lines"] = text.split("\n")
    lint_report = lint_file(file_path, vault_root=vault_root, link_context=link_context)

    ntype = _note_type(structure.get("frontmatter"), type_fallback)
    std = _TYPE_STANDARDS[ntype]

    if note_key is None:
        note_key = file_path.name

    ku_terms = _ku_terms([Path(b) for b in ku_batches]) if ku_batches else {}
    prov = provenance or {}

    dims: dict[str, dict] = {}
    for name in std["dimensions"]:
        dims[name] = {"score": None, "evidence": [], "band": "unmeasured", "weight": std["dimensions"][name][0]}

    s, ev = _score_structure(structure, lint_report)
    dims["structure"].update(score=s, evidence=ev)
    s, ev = _score_definitions(text)
    dims["definitions"].update(score=s, evidence=ev)
    s, ev = _score_depth(text, ntype)
    dims["depth"].update(score=s, evidence=ev)
    s, ev = _score_math(structure, text)
    dims["math_rigor"].update(score=s, evidence=ev)
    s, ev = _score_examples(text, structure)
    dims["examples"].update(score=s, evidence=ev)
    cov, ev, uncovered = _score_source_coverage(note_key, prov, ku_terms, text)
    if cov is not None:
        dims["source_coverage"].update(score=cov, evidence=ev, uncovered=uncovered)
    else:
        dims["source_coverage"].update(evidence=ev)
    s, ev = _score_provenance(structure.get("frontmatter"), text)
    dims["provenance"].update(score=s, evidence=ev)
    s, ev = _score_links(structure, lint_report)
    dims["links"].update(score=s, evidence=ev)
    s, ev = _score_editorial(structure, text, lint_report)
    dims["editorial"].update(score=s, evidence=ev)

    # band verdicts + weighted overall (unmeasured dimensions re-normalize)
    measured_weight = 0.0
    weighted_sum = 0.0
    for name, d in dims.items():
        weight, lo, hi = std["dimensions"][name]
        if d["score"] is None:
            d["band"] = "unmeasured"
            continue
        measured_weight += weight
        weighted_sum += weight * d["score"]
        d["band"] = "below_band" if d["score"] < lo else ("within_band" if d["score"] <= hi else "above_band")
    overall = weighted_sum / measured_weight if measured_weight else None

    return {
        "note": str(file_path),
        "note_key": note_key,
        "type": ntype,
        "standards_version": STANDARDS_VERSION,
        "dimensions": {k: {kk: vv for kk, vv in d.items()} for k, d in dims.items()},
        "overall": overall,
        "overall_measured_weight": measured_weight,
        "lint_error_count": lint_report["error_count"],
        "lint_defect_count": lint_report["defect_count"],
        "caveat": "deterministic measurement only; semantic adequacy is a review decision",
    }


def assess_tree(
    root: str | Path,
    *,
    provenance: dict[str, list[str]] | None = None,
    ku_batches: list[str | Path] | None = None,
    skip_dirs: tuple[str, ...] = (".git", ".obsidian"),
    link_context: dict | None = None,
) -> dict:
    """Assess every Markdown note under *root* (one shared link context)."""
    from .artifactlint import build_link_context

    root_path = Path(root)
    if not root_path.is_dir():
        raise QualityError(f"assess root is not a directory: {root_path}")
    ctx = link_context
    if ctx is None:
        ctx = build_link_context(root_path)
    notes = []
    for path in sorted(root_path.rglob("*.md")):
        if any(part in skip_dirs for part in path.relative_to(root_path).parts):
            continue
        report = assess_note(
            path,
            note_key=path.relative_to(root_path).as_posix(),
            provenance=provenance,
            ku_batches=ku_batches,
            link_context=ctx,
        )
        report["note"] = path.relative_to(root_path).as_posix()
        report["sequence_hint"] = _sequence_key(path, report)
        notes.append(report)
    return {"root": str(root_path), "standards_version": STANDARDS_VERSION, "notes": notes}


def _sequence_key(path: Path, report: dict):
    """Generation-order hint: frontmatter index/batch, else filename."""
    # assessed notes carry frontmatter in lint? cheap re-read avoided: use
    # filename natural sort as the fallback and frontmatter via note text
    fm = None
    try:
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            import yaml

            end = text.find("\n---", 3)
            if end != -1:
                fm = yaml.safe_load(text[3:end]) or {}
    except Exception:  # noqa: BLE001
        fm = None
    if fm:
        for key in ("created_index", "generation_index", "batch", "seq", "order"):
            if key in fm:
                try:
                    return (0, float(fm[key]), path.name)
                except (TypeError, ValueError):
                    pass
    return (1, 0.0, _natural_key(path.name))


def _natural_key(name: str):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


# ---------------------------------------------------------------------------
# drift detection


def detect_drift(
    assessments: list[dict],
    *,
    rel_drop: float = 0.15,
    abs_drop: float = 0.10,
) -> dict:
    """Compare early vs late notes per type; flag systematic quality drift.

    Evidence-first: every flagged dimension carries both tertile means, the
    delta, and the contributing notes. Notes are ordered by their
    sequence_hint (frontmatter index > natural filename order).
    """
    by_type: dict[str, list[dict]] = {}
    for note in assessments:
        by_type.setdefault(note["type"], []).append(note)

    drift: list[dict] = []
    clean: list[dict] = []
    for ntype, notes in sorted(by_type.items()):
        notes = sorted(notes, key=lambda n: n.get("sequence_hint") or (1, 0.0, _natural_key(Path(n["note"]).name)))
        if len(notes) < 3:
            clean.append({"type": ntype, "notes": len(notes), "verdict": "too_few_notes_to_compare"})
            continue
        third = max(1, len(notes) // 3)
        first, last = notes[:third], notes[-third:]

        dim_drifts: list[dict] = []
        for dim in sorted({d for n in notes for d in n["dimensions"]}):
            fv = [n["dimensions"][dim]["score"] for n in first if n["dimensions"][dim]["score"] is not None]
            lv = [n["dimensions"][dim]["score"] for n in last if n["dimensions"][dim]["score"] is not None]
            if not fv or not lv:
                continue
            f_mean, l_mean = statistics.fmean(fv), statistics.fmean(lv)
            delta = l_mean - f_mean
            rel = abs(delta) / f_mean if f_mean else 0.0
            if delta < 0 and rel >= rel_drop and abs(delta) >= abs_drop:
                dim_drifts.append(
                    {
                        "dimension": dim,
                        "first_third_mean": round(f_mean, 4),
                        "last_third_mean": round(l_mean, 4),
                        "delta": round(delta, 4),
                        "relative_drop": round(rel, 4),
                        "first_notes": [n["note"] for n in first],
                        "last_notes": [n["note"] for n in last],
                    }
                )
        overall_first = [n["overall"] for n in first if n["overall"] is not None]
        overall_last = [n["overall"] for n in last if n["overall"] is not None]
        entry = {
            "type": ntype,
            "notes": len(notes),
            "first_third": [n["note"] for n in first],
            "last_third": [n["note"] for n in last],
            "overall_first_third_mean": round(statistics.fmean(overall_first), 4) if overall_first else None,
            "overall_last_third_mean": round(statistics.fmean(overall_last), 4) if overall_last else None,
            "drifted_dimensions": dim_drifts,
            "verdict": "drift_detected" if dim_drifts else "no_systematic_drift",
        }
        (drift if dim_drifts else clean).append(entry)

    return {
        "standards_version": STANDARDS_VERSION,
        "thresholds": {"rel_drop": rel_drop, "abs_drop": abs_drop},
        "drifted_types": drift,
        "clean_types": clean,
        "verdict": "drift_detected" if drift else "no_systematic_drift",
        "caveat": "tertile-mean comparison on deterministic dimensions; investigate flagged evidence, do not treat as final judgment",
    }


# ---------------------------------------------------------------------------
# batch gate


def batch_gate(
    assessments: list[dict],
    *,
    expected_notes: list[str] | None = None,
    lint_errors_allowed: int = 0,
    drift_report: dict | None = None,
    waivers: dict[str, str] | None = None,
) -> dict:
    """Evaluate batch acceptance criteria; enumerate EVERY failure per note.

    A batch passes only when: every expected note was assessed (or is
    explicitly recorded as unresolved), every note has zero lint errors,
    every measured dimension is within band (or explicitly waived with a
    reason), and the drift report shows no unexplained systematic drift.
    A high average NEVER compensates a failing note.
    """
    waivers = waivers or {}
    failures: list[dict] = []
    by_note = {a["note"]: a for a in assessments}

    if expected_notes is not None:
        for expected in expected_notes:
            if expected not in by_note:
                failures.append(
                    {
                        "criterion": "expected_note_present",
                        "note": expected,
                        "detail": "expected note was not assessed (missing or not generated)",
                    }
                )
        # the batch gate scopes to the DECLARED batch: notes outside
        # expected_notes live in the same tree but are not this batch's
        # responsibility (they belong to their own batch and their own gate)
        gated_notes = [n for n in expected_notes if n in by_note]
    else:
        gated_notes = sorted(by_note)

    for note in gated_notes:
        a = by_note[note]
        if a["lint_error_count"] > lint_errors_allowed:
            failures.append(
                {
                    "criterion": "artifact_lint_clean",
                    "note": note,
                    "detail": f"{a['lint_error_count']} lint errors (allowed: {lint_errors_allowed})",
                }
            )
        for dim, d in a["dimensions"].items():
            if d["band"] == "unmeasured":
                continue
            if d["band"] == "below_band":
                waiver = waivers.get(f"{note}::{dim}")
                if waiver:
                    continue
                failures.append(
                    {
                        "criterion": "dimension_within_band",
                        "note": note,
                        "dimension": dim,
                        "detail": f"score {d['score']:.3f} below band; evidence: {'; '.join(d['evidence'][:3])}",
                    }
                )

    if drift_report and drift_report.get("verdict") == "drift_detected":
        for entry in drift_report.get("drifted_types", []):
            waiver = waivers.get(f"drift::{entry['type']}")
            if not waiver:
                failures.append(
                    {
                        "criterion": "no_unexplained_quality_drift",
                        "note": f"(type: {entry['type']})",
                        "detail": "; ".join(
                            f"{d['dimension']}: {d['first_third_mean']} -> {d['last_third_mean']} "
                            f"(rel drop {d['relative_drop']})"
                            for d in entry["drifted_dimensions"]
                        ),
                    }
                )

    passed = not failures
    return {
        "passed": passed,
        "criteria": [
            "every expected note assessed or explicitly unresolved",
            f"every note lint-error clean (allowed: {lint_errors_allowed})",
            "every measured dimension within its type band or explicitly waived with reason",
            "no unexplained systematic quality drift",
        ],
        "failures": failures,
        "notes_assessed": len(assessments),
        "waivers_applied": sorted(waivers.items()),
        "verdict": "pass" if passed else "fail",
    }

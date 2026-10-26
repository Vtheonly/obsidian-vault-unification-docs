"""Cross-vault overlap candidate discovery (CAP-013).

Deterministic candidate generation over committed KU batches. This module
NEVER assigns overlap classifications: it produces candidate pairs with
word-boundary term/alias evidence (plus exact/normalized hash duplicates)
that a human/agent reviewer must confirm against excerpts before any
classification is recorded (F-0006; docs/KNOWLEDGE_AND_PROVENANCE.md
section 7; ADR-0009).

Evidence-safety rules baked in (F-0006 regression cases):

- Word-boundary matching only: ``bridge`` must NOT match the term ``ridge``
  because the match is preceded by a word character. Boundaries use
  ``(?<!\\w)`` / ``(?!\\w)`` lookarounds (not ``\\b``) so terms that start
  or end with non-word characters behave predictably.
- Mermaid-node suspicion: a match immediately followed by ``[`` (mermaid
  node syntax like ``L1[Constant Change]`` or ``L2[Equation: y = ax + b]``)
  is flagged ``mermaid_node_suspect`` and NEVER counts toward a candidate's
  confirmed evidence. Word-boundary matching alone does not reject these
  (``[`` IS a word boundary for ``L1``), so the flag is mandatory.
  Furthermore, EVERY match inside a mermaid-declared code block is flagged
  the same way: mermaid edge references (``L1 --> L2 --> L3``) are node ids,
  not concepts, and must not count as confirmed evidence either (found on
  the real EXT-001 batch: KU-067bca8c3b42624f).
- Matches inside ``code_block`` units carry an informational
  ``unit_is_code_block`` flag: they are real text evidence (e.g. sklearn
  import lines) but the reviewer must weigh them as code, not prose.
- A candidate pair is ``confirmed`` only when BOTH sides have at least one
  match with no ``mermaid_node_suspect`` flag (or exact/normalized hash
  equality). Flagged-only candidates are still emitted, but marked
  ``unconfirmed_only: true`` so they cannot silently masquerade as
  evidence-backed pairs.

All outputs are deterministic (sorted, no timestamps in the JSONL pairs
file). Candidate ids are content fingerprints of the pair evidence.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


class OverlapError(Exception):
    """Raised for actionable candidate-discovery failures."""


# ---------------------------------------------------------------------------
# batch loading


def vault_of(source_id: str) -> str:
    """Vault identifier = source_id prefix before the first ':'."""
    if ":" not in source_id:
        raise OverlapError(
            f"source_id {source_id!r} has no vault prefix (expected '<vault>:<relpath>')"
        )
    return source_id.split(":", 1)[0]


def load_ku_batches(
    batch_paths: list[str | Path],
    kus_schema: str | Path,
) -> list[dict]:
    """Load, schema-validate and concatenate KU batches.

    Records keep their batch origin in a non-persistent ``_batch`` key.
    Raises :class:`OverlapError` on unreadable files, invalid JSON lines or
    schema violations (validation delegates to the shared KU schema).
    """
    try:
        import jsonschema
    except ImportError as exc:  # pragma: no cover - environment guard
        raise OverlapError(f"jsonschema package unavailable: {exc}") from exc

    schema_path = Path(kus_schema)
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise OverlapError(f"cannot read KU schema {schema_path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise OverlapError(f"invalid JSON in KU schema {schema_path}: {exc}") from exc

    records: list[dict] = []
    for batch_path in batch_paths:
        path = Path(batch_path)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise OverlapError(f"cannot read KU batch {path}: {exc}") from exc
        batch_records = 0
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                raise OverlapError(
                    f"{path}:{lineno}: invalid JSON: {exc}"
                ) from exc
            try:
                jsonschema.validate(rec, schema)
            except jsonschema.ValidationError as exc:
                raise OverlapError(
                    f"{path}:{lineno}: schema violation: "
                    f"{exc.message} (at {'/'.join(str(p) for p in exc.absolute_path)})"
                ) from exc
            if "knowledge_unit_id" not in rec:
                raise OverlapError(f"{path}:{lineno}: record lacks knowledge_unit_id")
            try:
                vault_of(rec["source_id"])
            except OverlapError as exc:
                raise OverlapError(f"{path}:{lineno}: {exc}") from exc
            stored = dict(rec)
            stored["_batch"] = str(path)
            records.append(stored)
            batch_records += 1
        if batch_records == 0:
            raise OverlapError(f"KU batch {path} contains no records")
    ids = [r["knowledge_unit_id"] for r in records]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise OverlapError(f"duplicate knowledge_unit_id across batches: {dupes[:5]}")
    return records


# ---------------------------------------------------------------------------
# term patterns


def _boundary_pattern(term: str) -> re.Pattern:
    """Case-insensitive word-boundary pattern for *term*.

    Boundaries: no ``[a-zA-Z0-9_]`` (word character) immediately before or
    after the match. This is what rejects 'ridge' inside 'bridge' while
    still matching 'ridge' at 'ridge:' or '(ridge)'.
    """
    escaped = re.escape(term.casefold())
    return re.compile(rf"(?<!\w){escaped}(?!\w)", re.IGNORECASE)


def build_term_patterns(terms: dict[str, list[str]] | list[str]) -> dict[str, list[tuple[str, re.Pattern]]]:
    """Map canonical term -> [(alias_or_term, pattern), ...].

    Accepts either a ``{term: [aliases]}`` mapping or a plain list of terms
    (no aliases). Empty terms/aliases are rejected. The canonical term
    itself is always included as a pattern.
    """
    if isinstance(terms, list):
        terms = {t: [] for t in terms}
    if not terms:
        raise OverlapError("terms map must contain at least one term")
    patterns: dict[str, list[tuple[str, re.Pattern]]] = {}
    for term, aliases in terms.items():
        if not isinstance(term, str) or not term.strip():
            raise OverlapError(f"invalid term {term!r}: must be a non-empty string")
        if not isinstance(aliases, list) or any(
            not isinstance(a, str) or not a.strip() for a in aliases
        ):
            raise OverlapError(
                f"aliases for term {term!r} must be a list of non-empty strings"
            )
        variants: list[tuple[str, re.Pattern]] = [(term, _boundary_pattern(term))]
        seen = {term.casefold()}
        for alias in aliases:
            if alias.casefold() in seen:
                continue
            seen.add(alias.casefold())
            variants.append((alias, _boundary_pattern(alias)))
        patterns[term] = variants
    return patterns


def load_terms_file(path: str | Path) -> dict[str, list[str]]:
    """Load a terms JSON file: either {term: [aliases]} or [term, ...].

    The canonicalized output is always ``{term: [aliases]}``.
    """
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except OSError as exc:
        raise OverlapError(f"cannot read terms file {p}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise OverlapError(f"invalid JSON in terms file {p}: {exc}") from exc
    if isinstance(data, list):
        if not data:
            raise OverlapError(f"terms file {p} is an empty list")
        if any(not isinstance(t, str) or not t.strip() for t in data):
            raise OverlapError(f"terms file {p}: all list entries must be non-empty strings")
        return {t: [] for t in data}
    if isinstance(data, dict):
        if not data:
            raise OverlapError(f"terms file {p} is an empty object")
        out: dict[str, list[str]] = {}
        for term, aliases in data.items():
            if term.startswith("_"):
                # documentation keys (e.g. _comment) are ignored
                continue
            if not isinstance(term, str) or not term.strip():
                raise OverlapError(f"terms file {p}: invalid term key {term!r}")
            if aliases is None:
                aliases = []
            if not isinstance(aliases, list) or any(
                not isinstance(a, str) or not a.strip() for a in aliases
            ):
                raise OverlapError(
                    f"terms file {p}: aliases for {term!r} must be a list of non-empty strings"
                )
            out[term] = aliases
        if not out:
            raise OverlapError(
                f"terms file {p}: no terms found (only _-prefixed documentation keys?)"
            )
        return out
    raise OverlapError(
        f"terms file {p}: expected a JSON object {{term: [aliases]}} or a list of terms"
    )


# ---------------------------------------------------------------------------
# matching


@dataclass
class TermMatch:
    term: str
    alias: str
    matched_text: str
    source_line: int
    char_start: int
    char_end: int
    context: str
    mermaid_node_suspect: bool
    unit_is_code_block: bool

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "alias": self.alias,
            "matched_text": self.matched_text,
            "source_line": self.source_line,
            "char_span": [self.char_start, self.char_end],
            "context": self.context,
            "mermaid_node_suspect": self.mermaid_node_suspect,
            "unit_is_code_block": self.unit_is_code_block,
        }


_CONTEXT_RADIUS = 60


def context_snippet(line: str, start: int, end: int) -> str:
    """Human-readable context around [start, end) with the match marked."""
    lo = max(0, start - _CONTEXT_RADIUS)
    hi = min(len(line), end + _CONTEXT_RADIUS)
    prefix = "…" if lo > 0 else ""
    suffix = "…" if hi < len(line) else ""
    return f"{prefix}{line[lo:start]}⟦{line[start:end]}⟧{line[end:hi]}{suffix}"


def _is_mermaid_unit(excerpt: str) -> bool:
    """True when the excerpt is a code block declaring mermaid.

    Detects an opening fence whose info string is (exactly) 'mermaid',
    e.g. '```mermaid'. All term matches inside such a unit are diagram
    syntax (node labels, edge references), never prose evidence.
    """
    lines = excerpt.splitlines()
    if not lines:
        return False
    first = lines[0].strip()
    if first.startswith("```"):
        info = first[3:].strip().casefold()
        return info == "mermaid"
    return False


def find_term_matches(
    record: dict,
    patterns: dict[str, list[tuple[str, re.Pattern]]],
) -> list[TermMatch]:
    """Find all word-boundary term/alias matches in a KU record's excerpt.

    Match positions are expressed as source line numbers (record line_start
    + index within the excerpt) and character spans within that line.
    Mermaid-node-suspect and code-block flags are computed per match: a
    match is mermaid-suspect when the unit is a mermaid code block (any
    position) or when the match is immediately followed by '['.
    """
    excerpt = record.get("excerpt")
    if not excerpt or not isinstance(excerpt, str):
        return []
    line_start = record.get("line_start") or 0
    unit_is_code = record.get("unit_type") == "code_block"
    unit_is_mermaid = unit_is_code and _is_mermaid_unit(excerpt)
    matches: list[TermMatch] = []
    for offset, line in enumerate(excerpt.splitlines()):
        source_line = line_start + offset if line_start else None
        for term, variants in patterns.items():
            for alias, pattern in variants:
                for m in pattern.finditer(line):
                    end = m.end()
                    suspect = unit_is_mermaid or (
                        end < len(line) and line[end] == "["
                    )
                    matches.append(
                        TermMatch(
                            term=term,
                            alias=alias,
                            matched_text=m.group(0),
                            source_line=source_line,
                            char_start=m.start(),
                            char_end=end,
                            context=context_snippet(line, m.start(), end),
                            mermaid_node_suspect=suspect,
                            unit_is_code_block=unit_is_code,
                        )
                    )
    matches.sort(
        key=lambda mm: (
            mm.source_line if mm.source_line is not None else -1,
            mm.char_start,
            mm.term.casefold(),
            mm.alias.casefold(),
        )
    )
    return matches


def _confirmed(matches: list[TermMatch]) -> list[TermMatch]:
    return [m for m in matches if not m.mermaid_node_suspect]


# ---------------------------------------------------------------------------
# candidate construction


def _candidate_id(topic: str, kind: str, ku_a: str, ku_b: str, salt: str) -> str:
    digest = hashlib.sha256(
        f"{topic}\x00{kind}\x00{ku_a}\x00{ku_b}\x00{salt}".encode("utf-8")
    ).hexdigest()[:16]
    return f"CAND-{digest}"


def _ku_side(record: dict) -> dict:
    return {
        "vault": vault_of(record["source_id"]),
        "ku_id": record["knowledge_unit_id"],
        "source_id": record["source_id"],
        "source_path": record["source_path"],
        "unit_type": record.get("unit_type"),
        "heading_path": record.get("heading_path") or [],
        "source_lines": [
            record.get("line_start"),
            record.get("line_end"),
        ],
    }


def _pair_sort_key(record: dict) -> tuple:
    return (
        vault_of(record["source_id"]),
        record["source_path"],
        record.get("line_start") or 0,
        record["knowledge_unit_id"],
    )


def discover_candidates(
    records: list[dict],
    patterns: dict[str, list[tuple[str, re.Pattern]]],
    *,
    max_pairs_per_topic: int = 250,
) -> dict:
    """Discover cross-vault overlap candidates.

    Returns a dict with:
    - ``topics``: per canonical term, per-vault KU + match evidence
    - ``pairs``: flat list of cross-vault candidate pair records
    - ``exact_hash_pairs`` / ``normalized_hash_pairs``: duplicate candidates
    - ``truncated_topics``: topics whose pair cross-product exceeded the cap
    - ``excluded_no_excerpt``: KU ids without excerpt text (unmatchable)
    - ``method`` / ``limitations``: stated explicitly
    """
    if max_pairs_per_topic < 1:
        raise OverlapError("max_pairs_per_topic must be >= 1")

    by_id = {r["knowledge_unit_id"]: r for r in records}
    excluded_no_excerpt = sorted(
        r["knowledge_unit_id"] for r in records if not r.get("excerpt")
    )

    # term evidence per KU
    ku_matches: dict[str, list[TermMatch]] = {}
    ku_terms: dict[str, set[str]] = {}
    for rec in records:
        if not rec.get("excerpt"):
            continue
        ms = find_term_matches(rec, patterns)
        if ms:
            ku_matches[rec["knowledge_unit_id"]] = ms
            ku_terms[rec["knowledge_unit_id"]] = {m.term for m in ms}

    # topic -> vault -> ku_ids
    topics: dict[str, dict[str, list[str]]] = {}
    for ku_id, terms in ku_terms.items():
        vault = vault_of(by_id[ku_id]["source_id"])
        for term in terms:
            topics.setdefault(term, {}).setdefault(vault, []).append(ku_id)
    for term_map in topics.values():
        for ku_list in term_map.values():
            ku_list.sort()

    pairs: list[dict] = []
    truncated: list[dict] = []
    for term in sorted(topics):
        vault_map = topics[term]
        vaults = sorted(vault_map)
        if len(vaults) < 2:
            continue  # single-vault topic: no cross-vault candidate
        cross_pairs = [
            (a, b)
            for i, va in enumerate(vaults)
            for vb in vaults[i + 1 :]
            for a in vault_map[va]
            for b in vault_map[vb]
        ]
        # deterministic ordering: sort each pair canonically
        ordered: list[tuple[dict, dict]] = []
        for a, b in cross_pairs:
            ra, rb = by_id[a], by_id[b]
            lo, hi = sorted((ra, rb), key=_pair_sort_key)
            ordered.append((lo, hi))
        ordered.sort(key=lambda t: (_pair_sort_key(t[0]), _pair_sort_key(t[1])))
        topic_pair_count = len(ordered)
        if topic_pair_count > max_pairs_per_topic:
            truncated.append(
                {
                    "topic": term,
                    "pair_count": topic_pair_count,
                    "emitted": max_pairs_per_topic,
                    "note": "pair cross-product exceeded cap; per-KU evidence in topics section remains complete",
                }
            )
            ordered = ordered[:max_pairs_per_topic]
        for lo, hi in ordered:
            m_lo = ku_matches.get(lo["knowledge_unit_id"], [])
            m_hi = ku_matches.get(hi["knowledge_unit_id"], [])
            m_topic_lo = [m for m in m_lo if m.term == term]
            m_topic_hi = [m for m in m_hi if m.term == term]
            pair = {
                "candidate_id": _candidate_id(
                    term, "term",
                    lo["knowledge_unit_id"], hi["knowledge_unit_id"],
                    salt="",
                ),
                "topic": term,
                "kind": "term",
                "ku_a": _ku_side(lo),
                "ku_b": _ku_side(hi),
                "matches_a": [m.to_dict() for m in m_topic_lo],
                "matches_b": [m.to_dict() for m in m_topic_hi],
                "confirmed": bool(_confirmed(m_topic_lo)) and bool(_confirmed(m_topic_hi)),
                "unconfirmed_only": not (
                    bool(_confirmed(m_topic_lo)) and bool(_confirmed(m_topic_hi))
                ),
            }
            if pair["unconfirmed_only"]:
                pair["unconfirmed_reason"] = (
                    "all matches on at least one side are flagged "
                    "(mermaid_node_suspect); excerpt confirmation required"
                )
            pairs.append(pair)

    # exact / normalized duplicate candidates
    hash_groups: dict[str, list[dict]] = {}
    norm_groups: dict[str, list[dict]] = {}
    for rec in records:
        excerpt = rec.get("excerpt")
        if not excerpt:
            continue
        eh = rec.get("excerpt_hash")
        if eh:
            hash_groups.setdefault(eh, []).append(rec)
        norm = re.sub(r"\s+", " ", excerpt.casefold()).strip()
        norm_digest = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        norm_groups.setdefault(norm_digest, []).append(rec)

    def _dup_pairs(groups: dict[str, list[dict]], kind: str) -> list[dict]:
        out: list[dict] = []
        for key in sorted(groups):
            recs = groups[key]
            files = {(r["source_id"]) for r in recs}
            if len(files) < 2:
                continue
            ordered_recs = sorted(recs, key=_pair_sort_key)
            for i, lo in enumerate(ordered_recs):
                for hi in ordered_recs[i + 1 :]:
                    if vault_of(lo["source_id"]) == vault_of(hi["source_id"]):
                        continue
                    out.append(
                        {
                            "candidate_id": _candidate_id(
                                kind, kind,
                                lo["knowledge_unit_id"],
                                hi["knowledge_unit_id"],
                                salt=key,
                            ),
                            "topic": f"__{kind}__",
                            "kind": kind,
                            "ku_a": _ku_side(lo),
                            "ku_b": _ku_side(hi),
                            "matches_a": [],
                            "matches_b": [],
                            "shared_excerpt_hash": key if kind == "exact_hash" else None,
                            "confirmed": True,
                            "unconfirmed_only": False,
                        }
                    )
        return out

    exact_pairs = _dup_pairs(hash_groups, "exact_hash")
    normalized_pairs = [
        p for p in _dup_pairs(norm_groups, "exact_normalized")
        if not any(  # suppress normalized dup when byte-exact already covers it
            p["ku_a"]["ku_id"] == e["ku_a"]["ku_id"]
            and p["ku_b"]["ku_id"] == e["ku_b"]["ku_id"]
            for e in exact_pairs
        )
    ]

    return {
        "method": (
            "word-boundary case-insensitive term/alias matching over KU excerpts "
            "((?<!\\w)term(?!\\w) lookarounds); matches inside mermaid code blocks "
            "and matches immediately followed by '[' are flagged "
            "mermaid_node_suspect and never count as confirmed evidence; "
            "code_block-unit matches carry an informational flag"
        ),
        "topics": {
            term: {
                vault: {
                    "ku_ids": ku_ids,
                    "per_ku_matches": {
                        ku_id: [m.to_dict() for m in ku_matches[ku_id] if m.term == term]
                        for ku_id in ku_ids
                    },
                }
                for vault, ku_ids in sorted(vault_map.items())
            }
            for term, vault_map in sorted(topics.items())
        },
        "pairs": pairs,
        "exact_hash_pairs": exact_pairs,
        "normalized_hash_pairs": normalized_pairs,
        "truncated_topics": truncated,
        "excluded_no_excerpt": excluded_no_excerpt,
        "counts": {
            "records_total": len(records),
            "records_with_excerpt": len(records) - len(excluded_no_excerpt),
            "topics_total": len(topics),
            "topics_cross_vault": sum(
                1 for tm in topics.values() if len(tm) >= 2
            ),
            "term_pairs": len(pairs),
            "exact_hash_pairs": len(exact_pairs),
            "normalized_hash_pairs": len(normalized_pairs),
            "confirmed_term_pairs": sum(1 for p in pairs if p["confirmed"]),
            "unconfirmed_only_term_pairs": sum(1 for p in pairs if p["unconfirmed_only"]),
        },
        "limitations": [
            "candidate generation only: no overlap_type is assigned or implied",
            "term coverage is exactly the provided terms/aliases map; topics outside it are invisible to this run",
            "word-boundary matching does not stem: 'ridges' does not match 'ridge' unless declared as an alias",
            "mermaid_node_suspect flags matches inside mermaid code blocks (node labels AND edge references) plus the immediate-'[' heuristic outside them; other diagram syntaxes are not detected",
            "hash duplicates compare whole KU excerpts only, not fragments inside units",
            "counts are never semantic evidence; every classification requires excerpt review",
        ],
    }


def write_pair_jsonl(path: str | Path, result: dict) -> dict:
    """Write the flat candidate-pair list (term + hash kinds) as JSONL."""
    all_pairs = (
        result["pairs"]
        + result["exact_hash_pairs"]
        + result["normalized_hash_pairs"]
    )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for pair in all_pairs:
            handle.write(json.dumps(pair, sort_keys=True) + "\n")
    return {"path": str(path), "pairs_written": len(all_pairs)}


def run_discovery(
    batch_paths: list[str | Path],
    terms_path: str | Path,
    out_path: str | Path,
    *,
    kus_schema: str | Path,
    max_pairs_per_topic: int = 250,
) -> dict:
    """End-to-end discovery: load batches, match terms, write pair JSONL.

    Returns the full discovery result (the caller writes the JSON report).
    """
    records = load_ku_batches(batch_paths, kus_schema)
    if len({vault_of(r["source_id"]) for r in records}) < 2:
        raise OverlapError(
            "candidate discovery requires KUs from at least two distinct vaults "
            "(source_id prefixes); got one"
        )
    terms = load_terms_file(terms_path)
    patterns = build_term_patterns(terms)
    result = discover_candidates(records, patterns, max_pairs_per_topic=max_pairs_per_topic)
    result["scope"] = {
        "batches": [str(Path(b)) for b in batch_paths],
        "terms_file": str(Path(terms_path)),
        "terms_count": len(terms),
        "aliases_count": sum(len(v) for v in terms.values()),
        "max_pairs_per_topic": max_pairs_per_topic,
    }
    written = write_pair_jsonl(out_path, result)
    result["pairs_jsonl"] = written
    return result

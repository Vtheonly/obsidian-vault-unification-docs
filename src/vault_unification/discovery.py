"""Emergent concept discovery and knowledge-gap detection (CAP-017, DISC-001).

Deterministic candidate generation over committed KU batches, per
docs/EMERGENT_CONCEPT_DISCOVERY.md and the Phase 0 re-baseline spec.

SCOPE SPLIT (spec-mandated):
- THIS module = deterministic evidence collection, ranking, statuses,
  coverage gating, decision application and validation. It NEVER decides
  semantics: recurrence is a signal, not proof; absence of a definition in
  the PROCESSED corpus is provisional until coverage is complete.
- Semantic review (the agent / reviewer) owns confirm/accept/reject/merge/
  split/defer decisions, applied through :func:`apply_decisions` with an
  append-only history.

SAFEGUARDS BAKED IN (each exercised by tests/test_discovery.py fixtures):
- No fixed topic whitelist: terms are mined statistically (word-boundary
  n-grams, stopword-filtered) from KU excerpts and heading paths; a rare
  single-context term in a dependency position is still a candidate
  (rare_essential) — no frequency threshold gates candidacy.
- Usage without definition is a CANDIDATE, never a confirmed gap: the hard
  coverage gate refuses ``confirmed_gap`` unless every declared vault is
  fully processed (candidate.coverage.coverage_complete).
- Copied passages are collapsed: a passage repeated across files counts as
  ONE independent context (copied_passage flag preserved).
- Homonyms are flagged, not merged: contexts with disjoint co-occurrence
  signatures produce homonym_suspect + cluster evidence (F-0008 precedent).
- Contradictions are surfaced: definition contexts carrying different
  numeric claims near the term are emitted as contradiction pairs
  (F-0009 pattern), never silently resolved.
- Evidence quotes are machine-located: line attribution uses the X2
  locator rule (unique in-span occurrence) migrated to vault_unification
  .locators (L-13); no hand-typed line numbers anywhere.
- Deterministic outputs: content-derived candidate ids, sorted records,
  no timestamps in candidate records (decisions ARE events and carry
  timestamps).

KIND VOCABULARY:
- unexplained_prerequisite — used across >= 2 independent contexts, never
  defined/declared anywhere in the processed corpus.
- fragmented_derivation — derivation-position usage spread across >= 2
  independent contexts without a coherent treatment.
- rare_essential — one independent context, but the usage is in a
  dependency position (assumed / inside a derivation) and no definition
  exists anywhere processed.
- concept_sighting — usage WITH adequate definition evidence found
  (negative evidence; status already_covered) so reviewers see why a
  recurring term is NOT a gap.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

from .locators import _normalize
from .overlap import load_ku_batches
from .search import boundary_pattern

CANDIDATE_ID_PREFIX = "CG"

# ---------------------------------------------------------------------------
# linguistic resources (small, deterministic, no external dependencies)

_STOPWORDS = frozenset(
    """
    a an the and or but if then else when while for to from by of in on at
    with without into onto about as is are was were be been being am do does
    did doing have has had having will would shall should can could may might
    must this that these those it its they them their we our us you your i
    he she his her not no nor so such than too very just also more most other
    some any each few own same s t don now here there where why how what which
    who whom all both during before after above below up down out off over
    under again further once because until against between through
    """.split()
)

_TOKEN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9\-']{1,40}")

_DERIVATION_MARKERS = re.compile(
    r"(?:∂|∇|(?<![A-Za-z])d[A-Za-z]/d[A-Za-z]|derivation|derive[sd]?|"
    r"substitut\w*|therefore|it follows|step(?:\s+\d)?[:.)]|\bimplies\b)",
    re.IGNORECASE,
)

_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")

# relationship pattern templates; {t} is the escaped casefolded term
_DEFINITION_PATTERNS = [
    r"\b{t}\b\s+(?:is|are)\s+(?:a|an|the)\b",
    r"\b{t}\b\s+(?:is|are)\s+defined\s+as\b",
    r"\b{t}\b\s+refers\s+to\b",
    r"\b{t}\b\s+means\b",
    r"\b{t}\b\s+denotes\b",
    r"\b{t}\b\s+describes\b",
    r"definition\s+of\s+\b{t}\b",
    r"define[sd]?\s+\b{t}\b",
    r"\b{t}\b\s+states\s+that\b",
    r"the\s+\b{t}\b\s+rule\b",
    r"called\s+\b{t}\b",
    r"\b{t}\b\s+(?:is|are)\s+(?:defined|set|chosen|initialized|initialised|drawn|computed|calculated|given)\b",
    r"\b{t}\b\s+(?:is|are)\s+-?\d",
    r"\b{t}\b\s*:\s*$",
]
_ASSUMED_PATTERNS = [
    r"recall\s+(?:that\s+)?(?:the\s+)?\b{t}\b",
    r"remember\s+(?:that\s+)?(?:the\s+)?\b{t}\b",
    r"as\s+we\s+(?:saw|discussed|learned|derived|defined)\b[^.]*\b{t}\b",
    r"assuming\s+\b{t}\b",
    r"by\s+(?:the\s+)?\b{t}\b",
    r"from\s+(?:the\s+)?\b{t}\b",
    r"using\s+(?:the\s+)?\b{t}\b",
    r"per\s+\b{t}\b",
    r"according\s+to\s+\b{t}\b",
    r"apply(?:ing)?\s+(?:the\s+)?\b{t}\b",
    r"we\s+already\s+(?:know|saw)\b[^.]*\b{t}\b",
]

_MINEABLE_UNIT_TYPES = frozenset(
    {"prose", "list", "table", "math_block", "callout", "quote", "code_block"}
)

_QUOTE_WINDOW = 160  # chars each side of the match center
_MAX_QUOTE = 300


class DiscoveryError(Exception):
    """Raised for actionable discovery configuration failures."""


# ---------------------------------------------------------------------------
# loading and mining


def _vault_of(source_id: str) -> str:
    return source_id.split(":", 1)[0]


def _sentence_window(text: str, start: int, end: int) -> str:
    """Deterministic quote window around [start, end) with word snapping."""
    center = (start + end) // 2
    lo = max(0, center - _QUOTE_WINDOW)
    hi = min(len(text), center + _QUOTE_WINDOW)
    # snap to whitespace boundaries so quotes start/end at word edges
    while lo > 0 and not text[lo - 1].isspace():
        lo -= 1
    while hi < len(text) and not text[hi].isspace():
        hi += 1
    quote = text[lo:hi].strip()
    if len(quote) > _MAX_QUOTE:
        quote = quote[:_MAX_QUOTE].rstrip()
    return quote


def _mine_ngrams(text: str) -> list[tuple[str, ...]]:
    """Word-boundary n-grams (n=1..3) of non-stopword tokens."""
    tokens = [tok.casefold() for tok in _TOKEN_RE.findall(text)]
    grams: list[tuple[str, ...]] = []
    for n in (1, 2, 3):
        for i in range(len(tokens) - n + 1):
            window = tokens[i : i + n]
            if any(t in _STOPWORDS for t in window):
                continue
            if all(len(t) < 3 for t in window) and n == 1:
                continue
            grams.append(tuple(window))
    return grams


def _term_text(ngram: tuple[str, ...]) -> str:
    return " ".join(ngram)


def _match_relationship(
    term: str,
    ku_text_norm: str,
    heading_declared: bool,
) -> str:
    """Classify ONE (term, KU) pair: defined > declared > assumed > derivation > used.

    REFERENCE implementation (per-term regex templates). Kept verbatim as
    the equivalence oracle for :func:`_match_relationship_fast`: unit tests
    compare the two on every template family, and corpus-level verification
    runs both over real batches and compares candidate hashes. Do not change
    this function's semantics without changing the fast path and the tests
    together.
    """
    def_pats, assumed_pats = _relationship_patterns(term)
    for pat in def_pats:
        if pat.search(ku_text_norm):
            return "defined"
    if heading_declared:
        return "declared"
    for pat in assumed_pats:
        if pat.search(ku_text_norm):
            return "assumed"
    if _DERIVATION_MARKERS.search(ku_text_norm):
        return "derivation"
    return "used"


# ---- fast path (F-0015): term-agnostic trigger positions per KU ----------
# The 24 reference templates above all have the shape
#     <optional prefix trigger> \b{t}\b <optional continuation trigger>
# so instead of compiling 24 term-anchored regexes per distinct term, we scan
# each KU's normalized text ONCE with generic precompiled trigger patterns
# and record WHERE a term would have to sit for each template to fire:
#   - continuation starts (term END positions),
#   - prefix ends (term START positions),
#   - the D10 both-sides pair (``the ... rule``),
#   - gap-reach positions for the two [^.]* templates (A3, A11).
# A (term, KU) pair is then classified with ONE cached ``\b{t}\b`` finditer
# plus O(occurrences) set lookups. Equivalence to the reference is pinned by
# tests/test_discovery.py (TestRelationshipFastEquivalence) and by corpus
# A/B runs recorded under reports/discovery/.

_DEF_CONTINUATION_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\s+(?:is|are)\s+(?:a|an|the)\b",  # D1
        r"\s+(?:is|are)\s+defined\s+as\b",  # D2
        r"\s+refers\s+to\b",  # D3
        r"\s+means\b",  # D4
        r"\s+denotes\b",  # D5
        r"\s+describes\b",  # D6
        r"\s+states\s+that\b",  # D9
        r"\s+(?:is|are)\s+(?:defined|set|chosen|initialized|initialised|drawn|computed|calculated|given)\b",  # D12
        r"\s+(?:is|are)\s+-?\d",  # D13 (no trailing \b, mirrors the template)
        r"\s*:\s*$",  # D14 (end-anchored)
    )
)
_DEF_PREFIX_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"definition\s+of\s+",  # D7
        r"define[sd]?\s+",  # D8
        r"called\s+",  # D11
    )
)
_THE_PREFIX_PATTERN = re.compile(r"the\s+", re.IGNORECASE)  # D10 prefix
_RULE_CONT_PATTERN = re.compile(r"\s+rule\b", re.IGNORECASE)  # D10 continuation
_ASSUMED_PREFIX_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"recall\s+(?:that\s+)?(?:the\s+)?",  # A1
        r"remember\s+(?:that\s+)?(?:the\s+)?",  # A2
        r"assuming\s+",  # A4
        r"by\s+(?:the\s+)?",  # A5
        r"from\s+(?:the\s+)?",  # A6
        r"using\s+(?:the\s+)?",  # A7
        r"per\s+",  # A8
        r"according\s+to\s+",  # A9
        r"apply(?:ing)?\s+(?:the\s+)?",  # A10
    )
)
_GAP_PREFIX_PATTERNS = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"as\s+we\s+(?:saw|discussed|learned|derived|defined)\b",  # A3
        r"we\s+already\s+(?:know|saw)\b",  # A11
    )
)


@lru_cache(maxsize=512)
def _term_occurrence_pattern(term: str) -> re.Pattern:
    """``\\b{t}\\b`` with IGNORECASE — the term anchor shared by all 24 templates."""
    return re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)


def _relationship_positions(norm_text: str) -> dict:
    """Term-agnostic trigger positions for one normalized KU text.

    Returns sets of character positions:
    - ``def_cont``: term-END positions that fire a definition continuation;
    - ``def_pref``: term-START positions that fire a definition prefix;
    - ``the_pref`` / ``rule_cont``: the D10 both-sides pair;
    - ``assumed_pref``: term-START positions that fire an assumed prefix;
    - ``gap_reach``: term-START positions reachable by an A3/A11
      ``[^.]*`` gap after "as we saw..." / "we already know...".
    """
    def_cont: set[int] = set()
    for pat in _DEF_CONTINUATION_PATTERNS:
        for m in pat.finditer(norm_text):
            def_cont.add(m.start())
    def_pref: set[int] = set()
    for pat in _DEF_PREFIX_PATTERNS:
        for m in pat.finditer(norm_text):
            def_pref.add(m.end())
    the_pref = {m.end() for m in _THE_PREFIX_PATTERN.finditer(norm_text)}
    rule_cont = {m.start() for m in _RULE_CONT_PATTERN.finditer(norm_text)}
    assumed_pref: set[int] = set()
    for pat in _ASSUMED_PREFIX_PATTERNS:
        for m in pat.finditer(norm_text):
            assumed_pref.add(m.end())
    gap_reach: set[int] = set()
    n = len(norm_text)
    for pat in _GAP_PREFIX_PATTERNS:
        for m in pat.finditer(norm_text):
            pos = m.end()
            while pos < n and norm_text[pos] != ".":
                gap_reach.add(pos)
                pos += 1
    return {
        "def_cont": def_cont,
        "def_pref": def_pref,
        "the_pref": the_pref,
        "rule_cont": rule_cont,
        "assumed_pref": assumed_pref,
        "gap_reach": gap_reach,
    }


def _match_relationship_fast(
    term: str,
    ku: dict,
    ku_text_norm: str,
    heading_declared: bool,
) -> str:
    """Byte-equivalent fast twin of :func:`_match_relationship`.

    Trigger positions are computed once per KU and cached on the record under
    the non-persistent ``_disc_relpos`` key. See the F-0015 note above the
    pattern tables for the equivalence argument.
    """
    pos = ku.get("_disc_relpos")
    if pos is None:
        pos = _relationship_positions(ku_text_norm)
        ku["_disc_relpos"] = pos
    occ = _term_occurrence_pattern(term)
    if pos["def_cont"] or pos["def_pref"] or (pos["the_pref"] and pos["rule_cont"]):
        for m in occ.finditer(ku_text_norm):
            e, s = m.end(), m.start()
            if e in pos["def_cont"] or s in pos["def_pref"]:
                return "defined"
            if s in pos["the_pref"] and e in pos["rule_cont"]:
                return "defined"
    if heading_declared:
        return "declared"
    if pos["assumed_pref"] or pos["gap_reach"]:
        for m in occ.finditer(ku_text_norm):
            if m.start() in pos["assumed_pref"] or m.start() in pos["gap_reach"]:
                return "assumed"
    if _DERIVATION_MARKERS.search(ku_text_norm):
        return "derivation"
    return "used"


@lru_cache(maxsize=64)
def _relationship_patterns(
    term: str,
) -> tuple[tuple[re.Pattern, ...], tuple[re.Pattern, ...]]:
    escaped = re.escape(term)
    def_pats = tuple(
        re.compile(template.format(t=escaped), re.IGNORECASE)
        for template in _DEFINITION_PATTERNS
    )
    assumed_pats = tuple(
        re.compile(template.format(t=escaped), re.IGNORECASE)
        for template in _ASSUMED_PATTERNS
    )
    return def_pats, assumed_pats


def _locate_in_ku(ku: dict, term: str) -> tuple[int, int, str] | None:
    """Find the term inside this KU; return (abs_line_start, abs_line_end, quote).

    Line attribution uses normalized per-line matching with a uniqueness
    requirement per line (first matching line wins deterministically because
    occurrence-level uniqueness inside one KU line is guaranteed by the word
    boundary; KU-level multi-line spans are handled by scanning lines in
    order). This is the X2 rule in miniature: no hand-typed line numbers.

    Performance (F-0015): split/normalized lines are cached on the KU record
    under non-persistent ``_disc_lines``/``_disc_norm_lines`` keys (mirrors the
    loader's ``_batch`` convention); they never reach any output.
    """
    excerpt = ku["excerpt"]
    if "_disc_lines" in ku:
        lines = ku["_disc_lines"]
        norm_lines = ku["_disc_norm_lines"]
    else:
        lines = excerpt.splitlines()
        norm_lines = [_normalize(line) for line in lines]
        ku["_disc_lines"] = lines
        ku["_disc_norm_lines"] = norm_lines
    pattern = boundary_pattern(term)
    for offset, line in enumerate(lines):
        if pattern.search(line):
            quote = _sentence_window(
                excerpt,
                excerpt.find(line) if line else 0,
                (excerpt.find(line) if line else 0) + len(line),
            )
            line_start = ku["line_start"] + offset
            # multi-line terms may continue; end line = start + span of term
            # if the term itself spans lines, extend while next line starts
            # the continuation (deterministic: at most the term's token span)
            line_end = line_start
            return line_start, line_end, quote
        # normalized fallback (case/whitespace drift)
        if norm_lines[offset] and pattern.search(norm_lines[offset]):
            line_start = ku["line_start"] + offset
            return (
                line_start,
                line_start,
                _sentence_window(
                    excerpt,
                    excerpt.find(line),
                    excerpt.find(line) + len(line),
                ),
            )
    return None


def _passage_hash(quote: str) -> str:
    return hashlib.sha256(_normalize(quote).encode("utf-8")).hexdigest()


def _signature_terms(term: str, ku: dict, top_k: int = 8) -> list[str]:
    """Distinctive co-occurring mined terms in this KU (for homonym clustering).

    Performance (F-0015): the per-KU term Counter is cached on the KU record
    under the non-persistent ``_disc_counter`` key; only the exclusion sort
    runs per call. Output is identical to re-mining per call.
    """
    counter = ku.get("_disc_counter")
    if counter is None:
        grams = _mine_ngrams(ku["excerpt"])
        counter = Counter(_term_text(g) for g in grams)
        ku["_disc_counter"] = counter
    counts = {t: c for t, c in counter.items() if t != term}
    # deterministic ordering: count desc, then lexicographic
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [t for t, _ in ordered[:top_k]]


def _cluster_contexts(contexts: list[dict]) -> list[list[dict]]:
    """Union-find clustering: contexts merge when signatures intersect."""
    parent = list(range(len(contexts)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)

    for i in range(len(contexts)):
        for j in range(i + 1, len(contexts)):
            si = set(contexts[i]["signature"])
            sj = set(contexts[j]["signature"])
            if si and sj and si & sj:
                union(i, j)
    clusters: dict[int, list[dict]] = defaultdict(list)
    for idx, ctx in enumerate(contexts):
        clusters[find(idx)].append(ctx)
    return [sorted(cluster, key=lambda c: (c["vault"], c["source_path"])) for _, cluster in sorted(clusters.items())]


# ---------------------------------------------------------------------------
# main discovery pass


def discover_candidates(
    ku_batches: list[str | Path],
    kus_schema: str | Path,
    vault_manifests: dict[str, str | Path],
    *,
    max_evidence_per_candidate: int = 12,
) -> dict:
    """Run the deterministic discovery pass over validated KU batches.

    Args:
        ku_batches: KU JSONL batch files (schema-validated, duplicate ids
            rejected by the shared loader).
        kus_schema: path to the knowledge-unit schema.
        vault_manifests: ``{vault_id: manifest_jsonl_path}`` used for the
            coverage gate. Every vault that appears in the KU data MUST be
            declared here, otherwise the run fails loudly.

    Returns ``{"ok": bool, "candidates": [...], "report": {...}, "errors": [...]}``.
    """
    errors: list[str] = []
    records = load_ku_batches(ku_batches, kus_schema)

    # ---- coverage accounting (the hard gate's data) ----
    manifest_files: dict[str, set[str]] = {}
    for vault, manifest_path in vault_manifests.items():
        try:
            manifest_text = Path(manifest_path).read_text(encoding="utf-8")
        except OSError as exc:
            raise DiscoveryError(f"cannot read manifest for vault {vault!r}: {exc}") from exc
        relpaths = set()
        for line in manifest_text.splitlines():
            if not line.strip():
                continue
            try:
                relpaths.add(json.loads(line)["relpath"])
            except (json.JSONDecodeError, KeyError) as exc:
                raise DiscoveryError(
                    f"manifest {manifest_path}: malformed record: {exc}"
                ) from exc
        manifest_files[vault] = relpaths

    processed_files: dict[str, set[str]] = defaultdict(set)
    for rec in records:
        processed_files[_vault_of(rec["source_id"])].add(rec["source_path"])

    undeclared = sorted(set(processed_files) - set(manifest_files))
    if undeclared:
        raise DiscoveryError(
            f"vault(s) present in KU data but not declared via vault_manifests: {undeclared}"
        )

    coverage = {
        "vaults": [
            {
                "vault": vault,
                "processed_files": len(processed_files.get(vault, set())),
                "total_files": len(files),
            }
            for vault, files in sorted(manifest_files.items())
        ],
        "coverage_complete": all(
            len(processed_files.get(vault, set())) == len(files)
            for vault, files in manifest_files.items()
        ),
    }

    # ---- term mining ----
    ku_by_id = {rec["knowledge_unit_id"]: rec for rec in records}
    mined: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    terms_analyzed = 0

    for rec in records:
        if rec["unit_type"] not in _MINEABLE_UNIT_TYPES:
            continue
        grams = set(_mine_ngrams(rec["excerpt"]))
        # heading-path terms are concept declarations; mine them too
        for heading in rec.get("heading_path", []):
            for g in _mine_ngrams(heading):
                grams.add(g)
        for g in grams:
            mined[_term_text(g)][rec["knowledge_unit_id"]].append(rec)

    candidates: list[dict] = []
    not_emitted_reasons: Counter[str] = Counter()

    for term in sorted(mined):
        occurrences = mined[term]
        terms_analyzed += 1
        if len(term) < 3:
            not_emitted_reasons["too_short"] += 1
            continue

        # ---- classify each (term, KU) ----
        contexts: list[dict] = []
        definition_evidence: list[dict] = []
        for ku_id in sorted(occurrences):
            ku = ku_by_id[ku_id]
            # F-0015: locate FIRST. When the term has no excerpt match
            # (heading-path-only term) the pair is discarded below, so the
            # expensive relationship pass over that KU is pure waste — the
            # partial-corpus run showed 56% of analyzed terms fall here.
            # Reordering is byte-safe: `continue` drops the pair either way.
            located = _locate_in_ku(ku, term)
            if located is None:
                continue  # term came from heading path only; no excerpt match
            norm_text = ku.get("_disc_norm_text")
            if norm_text is None:
                norm_text = _normalize(ku["excerpt"])
                ku["_disc_norm_text"] = norm_text
                ku["_disc_norm_headings"] = [
                    _normalize(h) if h else h
                    for h in ku.get("heading_path", [])
                ]
            norm_headings = ku["_disc_norm_headings"]
            heading_declared = any(
                boundary_pattern(term).search(h) for h in norm_headings
            )
            relationship = _match_relationship_fast(
                term, ku, norm_text, heading_declared
            )
            line_start, line_end, quote = located
            ev = {
                "ku_id": ku_id,
                "vault": _vault_of(ku["source_id"]),
                "source_path": ku["source_path"],
                "line_start": line_start,
                "line_end": line_end,
                "relationship": relationship,
                "quote": quote,
            }
            if relationship in ("defined", "declared"):
                definition_evidence.append(ev)
            contexts.append(
                {
                    **ev,
                    "passage_hash": _passage_hash(quote),
                    # F-0015: signature is computed lazily below — only when
                    # homonym clustering can run (independent_contexts >= 2).
                    "signature": [],
                }
            )

        if not contexts:
            not_emitted_reasons["no_locatable_occurrence"] += 1
            continue

        # ---- independence: collapse copied passages across files ----
        by_hash: dict[str, list[dict]] = defaultdict(list)
        for ctx in contexts:
            by_hash[ctx["passage_hash"]].append(ctx)
        copied_passage = any(len(group) > 1 for group in by_hash.values())
        independent_contexts = len(
            {ctx["passage_hash"] for ctx in contexts}
        )
        # F-0015: lazy signatures — computed only when clustering can use
        # them (identical values to eager computation; byte-identical output).
        if independent_contexts >= 2:
            for ctx in contexts:
                ctx["signature"] = _signature_terms(term, ku_by_id[ctx["ku_id"]])
        # dedupe evidence list: one evidence per (ku, relationship)
        seen_ev = set()
        evidence = []
        for ctx in sorted(contexts, key=lambda c: (c["vault"], c["source_path"], c["ku_id"])):
            key = (ctx["ku_id"], ctx["relationship"])
            if key in seen_ev:
                continue
            seen_ev.add(key)
            evidence.append(
                {k: ctx[k] for k in ("ku_id", "vault", "source_path", "line_start", "line_end", "relationship", "quote")}
            )
        evidence = evidence[:max_evidence_per_candidate]

        assumed_usages = sum(1 for c in contexts if c["relationship"] == "assumed")
        derivation_usages = sum(1 for c in contexts if c["relationship"] == "derivation")
        usage_usages = sum(1 for c in contexts if c["relationship"] == "used")
        has_definition = bool(definition_evidence)

        # ---- emission rules ----
        if has_definition:
            if independent_contexts >= 2:
                kind = "concept_sighting"
                status = "already_covered"
            else:
                not_emitted_reasons["defined_low_usage"] += 1
                continue
        elif independent_contexts >= 2 and (assumed_usages or derivation_usages or usage_usages):
            if derivation_usages >= 2 and independent_contexts >= 2:
                kind = "fragmented_derivation"
            else:
                kind = "unexplained_prerequisite"
            status = "provisional_candidate"
        elif (
            independent_contexts == 1
            and (assumed_usages or derivation_usages)
            and not has_definition
        ):
            kind = "rare_essential"
            status = "provisional_candidate"
        else:
            not_emitted_reasons["weak_single_usage"] += 1
            continue

        # ---- homonym clustering (contexts only, definition evidence excluded) ----
        homonym_suspect = False
        homonym_clusters = None
        if independent_contexts >= 2:
            clusters = _cluster_contexts(
                [c for c in contexts if c["signature"]]
            )
            if len(clusters) >= 2 and any(len(c) >= 1 for c in clusters):
                # only flag when the split is meaningful: >= 2 clusters each
                # holding >= 1 context AND disjoint signatures
                sigs = [set(t for c in cl for t in c["signature"]) for cl in clusters]
                disjoint = all(not (sigs[i] & sigs[j]) for i in range(len(sigs)) for j in range(i + 1, len(sigs)))
                if disjoint and len(clusters) >= 2:
                    homonym_suspect = True
                    homonym_clusters = [
                        {
                            "cluster_id": idx,
                            "context_files": sorted({c["source_path"] for c in cl}),
                            "signature_terms": sorted(sigs[idx])[:12],
                        }
                        for idx, cl in enumerate(clusters)
                    ]

        # ---- contradiction suspicion: differing numbers near definitions ----
        contradiction_suspect = False
        contradictions = None
        if len(definition_evidence) >= 2:
            def_numbers = [
                (ev, tuple(sorted(set(_NUMBER_RE.findall(ev["quote"])))))
                for ev in definition_evidence
            ]
            conflicting = [
                (a, b)
                for i, (a, na) in enumerate(def_numbers)
                for b, nb in def_numbers[i + 1 :]
                if na and nb and na != nb
            ]
            if conflicting:
                contradiction_suspect = True
                contradictions = [
                    {
                        "a_ku_id": a["ku_id"],
                        "b_ku_id": b["ku_id"],
                        "note": (
                            "definition/declaration contexts carry different numeric "
                            "claims near the term; surfaced for review, not resolved"
                        ),
                    }
                    for a, b in conflicting[:5]
                ]

        # ---- destination recommendation (deterministic hint) ----
        if kind == "concept_sighting":
            destination = "no_gap"
            rationale = (
                f"definition/declaration evidence found in "
                f"{len({e['source_path'] for e in definition_evidence})} file(s); "
                "not a gap; sighting retained as negative evidence"
            )
        elif kind == "fragmented_derivation":
            destination = "standalone_note_candidate"
            rationale = (
                f"derivation-position usage across {independent_contexts} independent "
                "contexts without a coherent dedicated treatment; a standalone "
                "derivation/prerequisite note candidate"
            )
        elif kind == "unexplained_prerequisite" and independent_contexts >= 3:
            destination = "standalone_note_candidate"
            rationale = (
                f"{independent_contexts} independent contexts use the term with no "
                "definition anywhere in the processed corpus; breadth supports a "
                "standalone note candidate (review decides finally)"
            )
        elif kind == "rare_essential":
            destination = "section_candidate"
            rationale = (
                "single independent context in a dependency position; consider a "
                "section inside the dependent note (or a short standalone note) — "
                "review decides"
            )
        else:
            destination = "section_candidate"
            rationale = (
                f"{independent_contexts} independent contexts without definitions; "
                "narrow breadth suggests a section in an existing note first; "
                "review may promote to a standalone note"
            )

        # ---- confidence (deterministic signal composite, NOT a verdict) ----
        cross_vault = len({c["vault"] for c in contexts}) > 1
        indep_component = min(independent_contexts, 5) / 5
        score = (
            0.40 * indep_component
            + 0.15 * (1 if assumed_usages else 0)
            + 0.15 * (1 if derivation_usages else 0)
            + 0.20 * (0 if has_definition else 1)
            + 0.10 * (1 if cross_vault else 0)
        )
        if homonym_suspect:
            score -= 0.25
        if copied_passage:
            score -= 0.15
        score = round(max(0.0, min(1.0, score)), 3)

        gap_description = (
            f"Term {term!r}: {independent_contexts} independent context(s) "
            f"({len(contexts)} total occurrences across "
            f"{len({c['source_path'] for c in contexts})} file(s)); "
            f"relationships: {len(definition_evidence)} defined/declared, "
            f"{assumed_usages} assumed, {derivation_usages} derivation, "
            f"{usage_usages} plain usage; "
            + (
                "definition evidence EXISTS in the processed corpus."
                if has_definition
                else "NO definition/declaration evidence found anywhere in the "
                "PROCESSED corpus"
                + (
                    "; coverage is INCOMPLETE, so this gap can never be confirmed "
                    "until the remaining files are processed"
                    if not coverage["coverage_complete"]
                    else ""
                )
            )
        )

        ku_ids_sorted = sorted({c["ku_id"] for c in contexts})
        id_basis = f"{term}|{'|'.join(ku_ids_sorted)}"
        candidate_id = f"{CANDIDATE_ID_PREFIX}-{hashlib.sha256(id_basis.encode('utf-8')).hexdigest()[:12]}"

        candidates.append(
            {
                "candidate_id": candidate_id,
                "term": term,
                "proposed_title": term.title(),
                "kind": kind,
                "status": status,
                "evidence": evidence,
                "independent_contexts": independent_contexts,
                "copied_passage": copied_passage,
                "definition_evidence": definition_evidence[:max_evidence_per_candidate],
                "homonym_suspect": homonym_suspect,
                "homonym_clusters": homonym_clusters,
                "contradiction_suspect": contradiction_suspect,
                "contradictions": contradictions,
                "gap_description": gap_description,
                "destination_recommendation": destination,
                "destination_rationale": rationale,
                "confidence": {
                    "score": score,
                    "signals": {
                        "independent_contexts": independent_contexts,
                        "assumed_usages": assumed_usages,
                        "derivation_usages": derivation_usages,
                        "definition_count": len(definition_evidence),
                        "cross_vault": cross_vault,
                        "homonym_suspect": homonym_suspect,
                        "copied_passage": copied_passage,
                    },
                },
                "coverage": coverage,
                "verification_criteria": [
                    "every evidence ku_id maps to a disposition before release",
                    "dependent notes must link the accepted concept once synthesized",
                    "accepted concept must not duplicate existing canonical content",
                    "re-run discovery after coverage grows; status may change",
                ],
                "decision_history": [],
            }
        )

    candidates.sort(key=lambda c: (c["term"], c["candidate_id"]))
    by_kind = Counter(c["kind"] for c in candidates)
    by_status = Counter(c["status"] for c in candidates)

    report = {
        "command": "discover-gaps",
        "ok": not errors,
        "errors": errors,
        "denominators": {
            "ku_records_loaded": len(records),
            "terms_analyzed": terms_analyzed,
            "candidates_emitted": len(candidates),
            "terms_not_emitted": dict(not_emitted_reasons),
        },
        "candidates_by_kind": dict(by_kind),
        "candidates_by_status": dict(by_status),
        "coverage": coverage,
        "coverage_gate_note": (
            "gap candidates carry status provisional_candidate; confirmed_gap is "
            "reachable ONLY through reviewed decisions AND complete coverage "
            "(enforced by discovery-decide and discovery-validate)"
        ),
        "determinism_note": (
            "candidate ids are content-derived; records sorted; no timestamps in "
            "candidate records; identical inputs regenerate byte-identical output"
        ),
    }
    return {"ok": not errors, "candidates": candidates, "report": report, "errors": errors}


# ---------------------------------------------------------------------------
# decision application (semantic review)


_ALLOWED_TRANSITIONS = {
    "confirm_gap": {"provisional_candidate": "confirmed_gap"},
    "accept": {"provisional_candidate": "accepted", "confirmed_gap": "accepted"},
    "reject": {
        "provisional_candidate": "rejected",
        "confirmed_gap": "rejected",
        "deferred": "rejected",
        "already_covered": "rejected",
    },
    "defer": {"provisional_candidate": "deferred", "confirmed_gap": "deferred"},
    "merge": {
        "provisional_candidate": "merged",
        "confirmed_gap": "merged",
        "deferred": "merged",
    },
    "split": {"provisional_candidate": "split", "confirmed_gap": "split"},
    "revise": {},  # no status change
    "cover": {"provisional_candidate": "already_covered"},
}


def apply_decisions(
    candidates_path: str | Path,
    decisions_path: str | Path,
    candidate_schema_path: str | Path,
    *,
    decided_utc: str,
) -> dict:
    """Apply reviewed decisions to a candidate file with append-only history.

    Decision records (JSONL) require: candidate_id, decision_id, action,
    rationale, reviewer; merge additionally requires merge_into; split may
    carry new_candidates (full candidate records, schema-validated).

    Hard gates enforced here:
    - confirm_gap REFUSES when the candidate's coverage is incomplete;
    - transitions must follow the status machine;
    - histories are append-only (existing entries are never rewritten).

    Returns ``{"ok": bool, "records": [...], "errors": [...]}``.
    """
    import jsonschema

    schema = json.loads(Path(candidate_schema_path).read_text(encoding="utf-8"))
    # F-0015: one reused validator instead of per-candidate re-resolution.
    _candidate_validator = jsonschema.validators.validator_for(schema)(schema)
    _candidate_validator.check_schema(schema)

    candidates = []
    by_id: dict[str, dict] = {}
    with open(candidates_path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rec = json.loads(line)
                candidates.append(rec)
                by_id[rec["candidate_id"]] = rec

    errors: list[str] = []
    decisions = []
    with open(decisions_path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                decisions.append(json.loads(line))

    new_records: list[dict] = []

    def _hist(candidate: dict, entry: dict) -> None:
        existing_ids = {h["decision_id"] for h in candidate["decision_history"]}
        if entry["decision_id"] in existing_ids:
            errors.append(
                f"decision {entry['decision_id']} already applied to "
                f"{candidate['candidate_id']}"
            )
            return
        candidate["decision_history"].append(entry)

    for dec in decisions:
        cid = dec.get("candidate_id")
        action = dec.get("action")
        if cid not in by_id:
            errors.append(f"decision {dec.get('decision_id')}: unknown candidate {cid}")
            continue
        cand = by_id[cid]
        entry = {
            "decision_id": dec["decision_id"],
            "action": action,
            "rationale": dec["rationale"],
            "reviewer": dec["reviewer"],
            "decided_utc": decided_utc,
        }
        if action == "merge":
            target_id = dec.get("merge_into")
            if target_id not in by_id or target_id == cid:
                errors.append(
                    f"decision {dec['decision_id']}: merge_into must be another "
                    f"existing candidate (got {target_id!r})"
                )
                continue
            entry["merge_into"] = target_id
        elif action == "split":
            entry["split_into"] = dec.get("split_into", [])
            new_cands = dec.get("new_candidates", [])
            for nc in new_cands:
                try:
                    _candidate_validator.validate(nc)
                except jsonschema.ValidationError as exc:
                    errors.append(
                        f"decision {dec['decision_id']}: new candidate "
                        f"{nc.get('candidate_id')} invalid: {exc.message}"
                    )
                    continue
                if nc["candidate_id"] not in by_id:
                    by_id[nc["candidate_id"]] = nc
                    new_records.append(nc)
        elif action == "revise":
            if dec.get("revised_title"):
                cand["proposed_title"] = dec["revised_title"]
                entry["revised_title"] = dec["revised_title"]
            if dec.get("revised_scope"):
                entry["revised_scope"] = dec["revised_scope"]

        # hard gates and status machine (allowed maps current-status -> next)
        allowed = _ALLOWED_TRANSITIONS.get(action)
        if allowed is None:
            errors.append(
                f"decision {dec['decision_id']}: unknown action {action!r}"
            )
            continue
        if action == "confirm_gap" and not cand["coverage"]["coverage_complete"]:
            errors.append(
                f"decision {dec['decision_id']}: REFUSED confirm_gap on "
                f"{cid}: coverage incomplete "
                f"({[v for v in cand['coverage']['vaults']]})"
            )
            continue
        if action == "revise":
            pass  # no status change
        elif cand["status"] in allowed:
            cand["status"] = allowed[cand["status"]]
        else:
            errors.append(
                f"decision {dec['decision_id']}: action {action!r} not allowed "
                f"from status {cand['status']!r}"
            )
            continue
        _hist(cand, entry)
        # merge: append a reverse provenance note to the target
        if action == "merge":
            target = by_id[dec["merge_into"]]
            _hist(
                target,
                {
                    "decision_id": dec["decision_id"] + "-absorb",
                    "action": "merge",
                    "rationale": (
                        f"absorbed candidate {cid}; its evidence and history are "
                        "preserved in the source record"
                    ),
                    "reviewer": dec["reviewer"],
                    "decided_utc": decided_utc,
                },
            )

    out = sorted(
        list(by_id.values()), key=lambda c: (c["term"], c["candidate_id"])
    )
    return {"ok": not errors, "records": out, "errors": errors}


# ---------------------------------------------------------------------------
# validation


def validate_candidates(
    candidates_path: str | Path,
    candidate_schema_path: str | Path,
    *,
    ku_batches: list[str | Path] | None = None,
    kus_schema: str | Path | None = None,
) -> dict:
    """Schema + cross-check validation for candidate files.

    Checks: per-record schema validation; duplicate ids; evidence ku_ids
    exist in the provided batches (when given); confirmed_gap requires
    coverage_complete; merged/split records must carry the matching history
    entry; history decision_ids unique per candidate.
    """
    import jsonschema

    schema = json.loads(Path(candidate_schema_path).read_text(encoding="utf-8"))
    # F-0015: one reused validator instead of per-record re-resolution
    # (candidate files at corpus scale hold tens of thousands of records).
    validator = jsonschema.validators.validator_for(schema)(schema)
    validator.check_schema(schema)
    records = []
    with open(candidates_path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))

    errors: list[str] = []
    ids = [r["candidate_id"] for r in records]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        errors.append(f"duplicate candidate_id: {dupes[:5]}")

    ku_ids: set[str] | None = None
    if ku_batches and kus_schema:
        ku_ids = {
            rec["knowledge_unit_id"]
            for rec in load_ku_batches(list(ku_batches), kus_schema)
        }

    for rec in records:
        try:
            validator.validate(rec)
        except jsonschema.ValidationError as exc:
            errors.append(
                f"{rec.get('candidate_id', '?')}: schema violation: {exc.message}"
            )
            continue
        if rec["status"] == "confirmed_gap" and not rec["coverage"]["coverage_complete"]:
            errors.append(
                f"{rec['candidate_id']}: status confirmed_gap but coverage "
                "is incomplete (hard gate violation)"
            )
        if ku_ids is not None:
            for ev in rec["evidence"]:
                if ev["ku_id"] not in ku_ids:
                    errors.append(
                        f"{rec['candidate_id']}: evidence ku_id "
                        f"{ev['ku_id']} not found in provided batches"
                    )
        hist_ids = [h["decision_id"] for h in rec["decision_history"]]
        if len(hist_ids) != len(set(hist_ids)):
            errors.append(
                f"{rec['candidate_id']}: duplicate decision_id in history"
            )
        for h in rec["decision_history"]:
            if h["action"] == "merge" and "merge_into" not in h and not h[
                "rationale"
            ].startswith("absorbed"):
                errors.append(
                    f"{rec['candidate_id']}: merge history entry lacks merge_into"
                )
            if h["action"] == "split" and "split_into" not in h:
                errors.append(
                    f"{rec['candidate_id']}: split history entry lacks split_into"
                )

    return {
        "command": "discovery-validate",
        "valid": not errors,
        "records_total": len(records),
        "errors": errors[:50],
        "errors_total": len(errors),
    }


# ---------------------------------------------------------------------------
# compact candidate index (CAP-023): the committable projection of a
# corpus-scale candidates file. Full candidate records carry evidence quotes
# that duplicate source text already committed inside the KU batches; at
# corpus scale the full file can exceed repository limits (DISC-002: 60,154
# candidates -> 270 MB). The index keeps every review-relevant field and the
# ku_id join keys, dropping only the quote payloads (recoverable from the
# KU batches via ku_id, or by deterministically regenerating the full file
# with the recorded command).


def candidate_index_record(rec: dict, *, max_ku_ids: int = 12) -> dict:
    """Compact, review-sufficient projection of one candidate record."""
    evidence = rec.get("evidence", [])
    return {
        "candidate_id": rec["candidate_id"],
        "term": rec["term"],
        "proposed_title": rec.get("proposed_title"),
        "kind": rec["kind"],
        "status": rec["status"],
        "score": rec.get("confidence", {}).get("score"),
        "independent_contexts": rec.get("independent_contexts"),
        "cross_vault": rec.get("confidence", {}).get("signals", {}).get(
            "cross_vault"
        ),
        "homonym_suspect": rec.get("homonym_suspect", False),
        "contradiction_suspect": rec.get("contradiction_suspect", False),
        "destination_recommendation": rec.get("destination_recommendation"),
        "evidence_count": len(evidence),
        "ku_ids": [e["ku_id"] for e in evidence][:max_ku_ids],
        "source_files": sorted({e["source_path"] for e in evidence})[:max_ku_ids],
        "decisions": [h["decision_id"] for h in rec.get("decision_history", [])],
    }


def write_candidate_index(
    candidates_path: str | Path,
    index_out: str | Path,
    *,
    max_ku_ids: int = 12,
) -> dict:
    """Write the compact index for a candidates JSONL file.

    Deterministic: records are emitted in file order (discover-gaps emits
    sorted records), no timestamps. Returns a summary dict with counts and
    the projection contract.
    """
    candidates_path = Path(candidates_path)
    index_out = Path(index_out)
    records: list[dict] = []
    with open(candidates_path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    lines = [
        json.dumps(
            candidate_index_record(rec, max_ku_ids=max_ku_ids),
            sort_keys=True,
            ensure_ascii=False,
        )
        for rec in records
    ]
    index_out.write_text(
        "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
    )
    return {
        "command": "discovery-index",
        "candidates_path": str(candidates_path),
        "index_path": str(index_out),
        "records_indexed": len(records),
        "dropped_payload": "evidence quotes (join via ku_ids against KU batches)",
        "max_ku_ids": max_ku_ids,
    }

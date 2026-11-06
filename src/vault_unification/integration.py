"""Integration campaign machinery (INTEG; sessions 31-45).

Deterministic tooling for the "index of the missing things" campaign
(docs/INTEGRATION_CAMPAIGN_PLAN.md). Two capabilities:

1. **Inventory parse** (:func:`parse_integration_list`) — the user-supplied
   taxonomy file (commit 77cf6cf) is parsed into a canonical item inventory:

   - nine project *clusters* (SYNPATH, MAPDIG, MATHSOLVER, WEATHER, NLME,
     VAULTX, MASTER-INDEX, MEDNLP, 2D3D) detected by title keywords, robust
     to the file's two halves and its restarting section numbering;
   - *items* = bullet lines (any indent) + typed carrier lines (``Genes:``,
     ``Proteins:``, ``Drugs:``, ``Drug Brand Names:``, ``Procedures:``) whose
     payloads are split into entities + master-index table rows (tab
     separated: the *field* column is the item; the *principal concepts*
     column is a cross-reference list recorded on the field item and resolved
     against the inventory, per the section's own "without repeating"
     declaration — principal-concept entries never create items);
   - *aliases* = trailing parentheticals (``Long Short-Term Memory (LSTM)``);
     escaped LaTeX parentheticals (``\\(W^O\\)``) are unescaped first;
   - *dedup* by normalized name (ASCII fold, lowercase, punctuation to
     spaces, British->American spelling, whitespace collapse); every
     occurrence (cluster, section, line) is retained on the item record;
   - *context records* (``Repository:``, ``Important distinction:``,
     ``Status note:``, group labels like ``Named medical vocabularies and
     databases:`` and free-text annotations) are captured per cluster —
     they constrain later integration content and are never dropped;
   - *exclusions*: the transcript-noise block between the ``TAHT ISNTA``
     marker line and the ``You're right. I missed two major project
     folders`` marker line (inclusive) — chat artifacts around the second
     half of the file — plus pre-cluster preamble lines. Every excluded line
     is recorded with its number and reason.

   Item ids ``INT-0001..`` are assigned in first-occurrence order and are
   stable across re-runs (deterministic given the input file).

2. **Lexical coverage** (:func:`build_coverage`) — for every inventory item,
   match its surface forms (name + alias) against a vault:

   - bands: ``title`` (normalized equality with a note title or frontmatter
     alias), ``heading`` (equality with a heading, numbering stripped),
     ``partial`` (substring relation with a title or heading; only for
     multi-token or >=8-char surfaces — acronyms require equality),
     ``body-multi`` (>=2 word-boundary occurrences in note bodies),
     ``body-single``, ``none``;
   - body matching uses flexible token regexes (separator-flexible,
     optional plural 's/es' per token, British/American alternation) so
     ``K-Nearest Neighbour Matching`` matches "K-nearest-neighbor matching"
     and ``Gaussian Basis Functions`` matches "Gaussian Basis Function";
   - a token prefilter (per-note normalized token sets, singular-folded)
     shortlists candidate notes before regex confirmation;
   - lexical evidence NEVER decides coverage by itself (terminology differs
     across the vault); it is the substrate for the semantic judgment
     sessions (campaign plan section 5).

Everything is read-only over the vault; outputs go to explicit destination
paths guarded against source-root overlap by the CLI layer.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# errors


class IntegrationError(ValueError):
    """Raised for unusable integration-campaign inputs or invalid state."""


# ---------------------------------------------------------------------------
# normalization (shared by inventory dedup and coverage matching)

_BRITISH_TO_AMERICAN = {
    "neighbour": "neighbor", "neighbours": "neighbors", "neighbouring": "neighboring",
    "modelling": "modeling", "modelled": "modeled",
    "normalisation": "normalization", "normalise": "normalize", "normalised": "normalized",
    "fibre": "fiber", "fibres": "fibers",
    "centre": "center", "centres": "centers", "centralised": "centralized",
    "analyse": "analyze", "analysed": "analyzed", "analysing": "analyzing",
    "optimisation": "optimization", "optimise": "optimize", "optimised": "optimized",
    "regularisation": "regularization", "regularise": "regularize",
    "quantisation": "quantization", "quantise": "quantize",
    "colour": "color", "colours": "colors", "coloured": "colored",
    "grey": "gray", "greys": "grays",
    "catalogue": "catalog", "catalogues": "catalogs",
    "synthesise": "synthesize", "synthesised": "synthesized", "synthesiser": "synthesizer",
    "utilisation": "utilization", "utilise": "utilize",
    "minimisation": "minimization", "maximisation": "maximization",
    "summarise": "summarize", "summarisation": "summarization",
    "characterise": "characterize", "characterised": "characterized",
    "emphasise": "emphasize", "organisation": "organization", "organised": "organized",
    "recognise": "recognize", "recognised": "recognized",
    "stabilise": "stabilize", "stabilised": "stabilized", "stabiliser": "stabilizer",
    "parameterise": "parameterize", "parameterised": "parameterized",
    "factorise": "factorize", "factorisation": "factorization",
    "practise": "practice", "defence": "defense", "licence": "license",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize_name(text: str) -> str:
    """Canonical form for name comparison.

    ASCII fold, lowercase, punctuation to single spaces, British->American
    spelling per token, whitespace collapse.
    """
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    folded = folded.lower()
    folded = re.sub(r"[^a-z0-9]+", " ", folded)
    tokens = [_BRITISH_TO_AMERICAN.get(tok, tok) for tok in folded.split()]
    return " ".join(tokens)


def fold_singular(token: str) -> str:
    """Fold a trailing plural 's' (tokens of >=4 chars) for index lookups."""
    if len(token) >= 4 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _folded_key(norm: str) -> str:
    return " ".join(fold_singular(t) for t in norm.split())


# ---------------------------------------------------------------------------
# inventory parse

_CLUSTER_RULES: list[tuple[str, str]] = [
    ("SynPath", "SYNPATH"),
    ("Map Digitizer", "MAPDIG"),
    ("Math Solver", "MATHSOLVER"),
    ("Weather", "WEATHER"),
    ("InfiniChatbot", "NLME"),
    ("Additional AI concepts", "VAULTX"),
    ("Consolidated master index", "MASTER-INDEX"),
    ("Medical NLP", "MEDNLP"),
    ("2D3D", "2D3D"),
]

_CARRIER_KEYS = ("Genes", "Proteins", "Drugs", "Drug Brand Names", "Procedures")
_NOISE_START = "TAHT ISNTA"
_NOISE_END_PREFIX = "You're right. I missed two major project folders"

_SECTION_RE = re.compile(r"^(\d+)\.\s+(.+)$")
_SUBSECTION_RE = re.compile(r"^(\d+\.\d+)\.?\s+(.+)$")
_ITEM_RE = re.compile(r"^\s*-\s+(.+?)\s*$")
_TABLE_ROW_RE = re.compile(r"^(\d+)\t(.+?)\t(.+)$")
_CARRIER_RE = re.compile(r"^(" + "|".join(re.escape(k) for k in _CARRIER_KEYS) + r"):\s*(.+)$")
_LABEL_RE = re.compile(r"^[A-Z][^:]{2,80}:\s*$")
_ALIAS_RE = re.compile(r"\(([^()]*)\)\s*$")


def _cluster_for(title: str) -> str | None:
    for needle, cluster_id in _CLUSTER_RULES:
        if needle.lower() in title.lower():
            return cluster_id
    return None


_ESCAPED_ALIAS_RE = re.compile(r"\((.*\\[()].*)\)\s*$")
_WRAP_PAREN_RE = re.compile(r"^\((.*)\)$")


def _split_alias(raw: str) -> tuple[str, str | None]:
    """Split a trailing parenthetical alias off an item name.

    Two forms:

    - plain: ``Long Short-Term Memory (LSTM)`` → name ``Long Short-Term
      Memory``, alias ``LSTM``;
    - LaTeX-escaped: ``Output Projection (\\(W^O\\))`` → the outer parens
      delimit the alias and the inner escaped pair is LaTeX, so the alias
      unescapes and unwraps to ``W^O`` with name ``Output Projection``.

    A naive unescape-first approach would produce ``((W^O))`` (nested plain
    parens) and fail to match, so the escaped form is handled explicitly.
    """
    m = _ALIAS_RE.search(raw)
    if m:
        alias = m.group(1).strip()
        name = raw[: m.start()].strip().rstrip(",").strip()
        if alias and name:
            return name, alias
        return raw.strip(), None
    em = _ESCAPED_ALIAS_RE.search(raw)
    if em:
        inner = em.group(1).replace("\\(", "(").replace("\\)", ")")
        wm = _WRAP_PAREN_RE.match(inner.strip())
        alias = (wm.group(1) if wm else inner).strip()
        name = raw[: em.start()].strip().rstrip(",").strip()
        if alias and name:
            return name, alias
    return raw.strip(), None


def parse_integration_list(list_path: str | Path) -> dict:
    """Parse the user's taxonomy file into the canonical inventory structure.

    Returns a dict with ``clusters`` (ordered), ``items`` (deduplicated,
    first-occurrence ids), ``excluded_lines`` and ``parse_stats``. Raises
    :class:`IntegrationError` for missing/empty input, an unrecognized
    structure, or missing noise markers (a changed file must fail loudly,
    never silently produce a partial inventory).
    """
    list_path = Path(list_path)
    if not list_path.is_file():
        raise IntegrationError(f"taxonomy file not found: {list_path}")
    text = list_path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if not any(ln.strip() for ln in lines):
        raise IntegrationError(f"taxonomy file is empty: {list_path}")

    clusters: dict[str, dict] = {}
    cluster_order: list[str] = []
    items_by_key: dict[str, dict] = {}
    item_order: list[str] = []
    excluded: list[dict] = []

    state = {"cluster": None, "section": None, "group_label": None}
    noise = {"active": False, "start": None, "end": None}

    def add_context(line_no: int, line: str, kind: str) -> None:
        if state["cluster"] is not None:
            clusters[state["cluster"]]["context"].append(
                {"line": line_no, "kind": kind, "text": line.strip()}
            )

    def record_item(line_no: int, raw_name: str) -> None:
        name, alias = _split_alias(raw_name)
        if not name:
            return
        key = normalize_name(name)
        if not key:
            return
        cluster_id = state["cluster"]
        occ = {"cluster": cluster_id, "section": state["section"], "line": line_no}
        if key in items_by_key:
            item = items_by_key[key]
            item["occurrences"].append(occ)
            if cluster_id not in item["clusters"]:
                item["clusters"].append(cluster_id)
            if alias and not item.get("alias"):
                item["alias"] = alias
            if state["group_label"] and state["group_label"] not in item["group_labels"]:
                item["group_labels"].append(state["group_label"])
        else:
            item = {
                "item_id": f"INT-{len(item_order) + 1:04d}",
                "name": name,
                "alias": alias,
                "key": key,
                "clusters": [cluster_id],
                "occurrences": [occ],
                "group_labels": [state["group_label"]] if state["group_label"] else [],
                "principal_concepts": [],
                "principal_refs": [],
            }
            items_by_key[key] = item
            item_order.append(key)

    for line_no, raw in enumerate(lines, start=1):
        line = raw.rstrip("\r")
        stripped = line.strip()

        # ---- transcript-noise block (documented exclusion) ----
        if not noise["active"] and stripped.startswith(_NOISE_START):
            noise["active"] = True
            noise["start"] = line_no
        if noise["active"]:
            excluded.append({"line": line_no, "text": line, "reason": "transcript-noise-block"})
            if stripped.startswith(_NOISE_END_PREFIX):
                noise["active"] = False
                noise["end"] = line_no
            continue
        if not stripped:
            state["group_label"] = None
            continue

        # ---- master-index table rows (tab separated) ----
        tm = _TABLE_ROW_RE.match(line)
        if tm and state["cluster"] == "MASTER-INDEX":
            field = tm.group(2).strip()
            principal = [p.strip() for p in tm.group(3).split(",") if p.strip()]
            record_item(line_no, field)
            items_by_key[normalize_name(field)]["principal_concepts"].extend(principal)
            continue

        # ---- top-level section (cluster) header ----
        sm = _SECTION_RE.match(stripped)
        if sm and not _SUBSECTION_RE.match(stripped):
            title = sm.group(2).strip()
            cluster_id = _cluster_for(title)
            if cluster_id:
                if cluster_id not in clusters:
                    clusters[cluster_id] = {
                        "cluster_id": cluster_id,
                        "title": title,
                        "first_line": line_no,
                        "repository": None,
                        "sections": [],
                        "context": [],
                    }
                    cluster_order.append(cluster_id)
                state["cluster"] = cluster_id
                state["section"] = None
                state["group_label"] = None
            else:
                add_context(line_no, line, "unrecognized-section-header")
            continue

        # ---- subsection header ----
        ssm = _SUBSECTION_RE.match(stripped)
        if ssm:
            if state["cluster"] is None:
                excluded.append({"line": line_no, "text": line, "reason": "subsection-before-any-cluster"})
                continue
            state["section"] = ssm.group(2).strip()
            clusters[state["cluster"]]["sections"].append(
                {"number": ssm.group(1), "title": state["section"], "line": line_no}
            )
            state["group_label"] = None
            continue

        # ---- carrier lines with typed entity payloads ----
        cm = _CARRIER_RE.match(stripped)
        if cm:
            if state["cluster"] is None:
                excluded.append({"line": line_no, "text": line, "reason": "carrier-before-any-cluster"})
                continue
            entity_type = cm.group(1).lower().replace(" ", "_")
            for part in cm.group(2).split(","):
                part = part.strip()
                if not part:
                    continue
                record_item(line_no, part)
                key = normalize_name(_split_alias(part)[0])
                if key in items_by_key:
                    item = items_by_key[key]
                    if entity_type not in item.setdefault("entity_types", []):
                        item["entity_types"].append(entity_type)
            continue

        # ---- item bullets (any indent) ----
        im = _ITEM_RE.match(line)
        if im:
            if state["cluster"] is None:
                excluded.append({"line": line_no, "text": line, "reason": "item-before-any-cluster"})
                continue
            record_item(line_no, im.group(1))
            continue

        # ---- group labels ("Named medical vocabularies and databases:") ----
        if _LABEL_RE.match(stripped):
            if state["cluster"] is None:
                excluded.append({"line": line_no, "text": line, "reason": "label-before-any-cluster"})
                continue
            state["group_label"] = stripped.rstrip(":").strip()
            add_context(line_no, line, "group-label")
            continue

        # ---- everything else: cluster context (Repository:, distinctions, notes) ----
        if state["cluster"] is None:
            excluded.append({"line": line_no, "text": line, "reason": "context-before-any-cluster"})
            continue
        add_context(line_no, line, "context")
        if stripped.startswith("Repository:"):
            clusters[state["cluster"]]["repository"] = stripped[len("Repository:"):].strip()

    if not clusters:
        raise IntegrationError("no cluster recognized in the taxonomy file (expected section markers)")
    if noise["start"] is None or noise["end"] is None:
        raise IntegrationError(
            "transcript-noise block markers not found (TAHT ISNTA... / You're right. I missed...); "
            "the file structure changed and the parser must be re-validated"
        )

    items = [items_by_key[k] for k in item_order]

    # resolve master-index principal concepts against the inventory
    # (cross-references only; they never create items)
    principal_unmatched: list[str] = []
    for item in items:
        for pc in item.pop("principal_concepts"):
            target = _match_principal_concept(pc, items_by_key)
            if target is None:
                principal_unmatched.append(f"{item['item_id']}:{pc}")
                item["principal_refs"].append({"concept": pc, "item_id": None})
            else:
                item["principal_refs"].append({"concept": pc, "item_id": target})

    for item in items:
        item.pop("key", None)

    return {
        "source_file": str(list_path),
        "source_sha256": _sha256(list_path),
        "clusters": [clusters[c] for c in cluster_order],
        "items": items,
        "excluded_lines": excluded,
        "noise_block": {"start_line": noise["start"], "end_line": noise["end"]},
        "parse_stats": {
            "clusters_total": len(cluster_order),
            "sections_total": sum(len(c["sections"]) for c in clusters.values()),
            "raw_item_lines": sum(len(i["occurrences"]) for i in items),
            "unique_items": len(items),
            "items_with_alias": sum(1 for i in items if i.get("alias")),
            "names_in_multiple_sections": sum(1 for i in items if len(i["occurrences"]) > 1),
            "excluded_lines_total": len(excluded),
            "context_records_total": sum(len(c["context"]) for c in clusters.values()),
            "principal_concepts_crossrefs": sum(len(i.get("principal_refs", [])) for i in items),
            "principal_concepts_unmatched": principal_unmatched,
        },
    }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _match_principal_concept(pc: str, items_by_key: dict) -> str | None:
    """Match a master-index principal-concept entry to an inventory item.

    Tries normalized equality, then normalized alias equality, then
    singular-folded equality. Returns the item id or None.
    """
    key = normalize_name(pc)
    if key in items_by_key:
        return items_by_key[key]["item_id"]
    folded = _folded_key(key)
    for item in items_by_key.values():
        if item.get("alias") and normalize_name(item["alias"]) == key:
            return item["item_id"]
        if _folded_key(item["name"]) == folded:
            return item["item_id"]
    return None


# ---------------------------------------------------------------------------
# lexical coverage

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
_NUMBERING_PREFIX_RE = re.compile(r"^\d+(\.\d+)*\.?\s+")
_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n?", re.S)
_HEADING_DECOR_RE = re.compile(r"\[\[|\]\]|`|\*\*")
_INLINE_ALIAS_RE = re.compile(r"^aliases:\s*\[(.*)\]\s*$")


def _clean_heading(text: str) -> str:
    text = _HEADING_DECOR_RE.sub("", text)
    text = _NUMBERING_PREFIX_RE.sub("", text)
    return text.strip()


def _parse_frontmatter_aliases(frontmatter: str) -> list[str]:
    aliases: list[str] = []
    if "aliases:" not in frontmatter:
        return aliases
    block = frontmatter.split("aliases:", 1)[1]
    in_block = False
    for ln in block.split("\n"):
        stripped = ln.strip()
        if not in_block:
            # first line after the key
            inline = _INLINE_ALIAS_RE.match("aliases:" + ln)
            if inline:
                for part in inline.group(1).split(","):
                    part = part.strip().strip('"').strip("'")
                    if part:
                        aliases.append(part)
                break
            if stripped.startswith("- ") or stripped.startswith('"-'):
                in_block = True
            elif not stripped:
                continue
            else:
                break
        if in_block:
            if not (ln[:1] in (" ", "\t")) and not stripped.startswith("-"):
                break
            if not stripped.startswith("-"):
                break
            part = stripped[1:].strip().strip('"').strip("'")
            if part:
                aliases.append(part)
    return aliases


def _load_vault(vault_root: Path) -> list[dict]:
    notes: list[dict] = []
    for path in sorted(vault_root.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        fm = _FRONTMATTER_RE.match(text)
        frontmatter = fm.group(0) if fm else ""
        body = text[fm.end():] if fm else text
        rel = path.relative_to(vault_root).as_posix()
        headings = [
            {"level": len(m.group(1)), "text": _clean_heading(m.group(2))}
            for m in _HEADING_RE.finditer(body)
        ]
        aliases = _parse_frontmatter_aliases(frontmatter)
        body_tokens = _TOKEN_RE.findall(normalize_name(body))
        token_set = set(body_tokens) | {fold_singular(t) for t in body_tokens}
        notes.append(
            {
                "relpath": rel,
                "title": path.stem,
                "title_norm": normalize_name(path.stem),
                "alias_norms": [normalize_name(a) for a in aliases],
                "headings": headings,
                "heading_norms": [normalize_name(h["text"]) for h in headings],
                "token_set": token_set,
                "body": body,
            }
        )
    return notes


def _flexible_regex(surface: str) -> re.Pattern:
    """Word-boundary, separator-flexible, plural-flexible, Brit/US pattern."""
    norm = normalize_name(surface)
    toks = _TOKEN_RE.findall(norm)
    parts = []
    for tok in toks:
        if len(tok) <= 2:
            parts.append(re.escape(tok))
            continue
        stem = fold_singular(tok)
        us = _BRITISH_TO_AMERICAN.get(stem, stem)
        brit = None
        for b, a in _BRITISH_TO_AMERICAN.items():
            if a == us and b != us:
                brit = b
                break
        core = re.escape(us)
        if brit:
            core = f"(?:{re.escape(brit)}|{re.escape(us)})"
        parts.append(core + r"(?:s|es)?")
    pattern = r"[\s\-_]*".join(parts)
    return re.compile(r"(?<![A-Za-z0-9])" + pattern + r"(?![A-Za-z0-9])", re.IGNORECASE)


def _surface_prefilter_ok(surface: str, note_tokens: set) -> bool:
    toks = _TOKEN_RE.findall(normalize_name(surface))
    if not toks:
        return False
    distinctive = [t for t in toks if len(t) >= 3] or toks
    for t in distinctive:
        if t in note_tokens or fold_singular(t) in note_tokens:
            continue
        return False
    return True


def build_coverage(inventory_items: list[dict], vault_root: str | Path) -> dict:
    """Match every inventory item's surface forms against the vault.

    Returns ``{"items": [...per-item evidence...], "aggregate": {...}}``.
    Read-only over the vault.
    """
    vault_root = Path(vault_root)
    if not vault_root.is_dir():
        raise IntegrationError(f"vault root is not a directory: {vault_root}")
    notes = _load_vault(vault_root)
    if not notes:
        raise IntegrationError(f"no markdown notes found under {vault_root}")

    band_counts = {"title": 0, "heading": 0, "partial": 0, "body-multi": 0, "body-single": 0, "none": 0}
    cluster_bands: dict[str, dict] = {}
    results: list[dict] = []

    # precomputed title/heading lookup tables
    title_exact: dict[str, list[tuple]] = {}
    heading_exact: dict[str, list[tuple]] = {}
    partial_targets: list[tuple] = []  # (norm, relpath, kind, display)
    for note in notes:
        for norm, via in [(note["title_norm"], "title")] + [
            (a, "frontmatter-alias") for a in note["alias_norms"]
        ]:
            if norm:
                title_exact.setdefault(norm, []).append((note["relpath"], via))
        for h, hn in zip(note["headings"], note["heading_norms"]):
            if hn:
                heading_exact.setdefault(hn, []).append((note["relpath"], h["text"]))
        if note["title_norm"] and len(note["title_norm"]) >= 3:
            partial_targets.append((note["title_norm"], note["relpath"], "title", note["title"]))
        for h, hn in zip(note["headings"], note["heading_norms"]):
            if hn and len(hn) >= 3:
                partial_targets.append((hn, note["relpath"], "heading", h["text"]))

    for item in inventory_items:
        surfaces: list[tuple[str, str]] = [(item["name"], "name")]
        if item.get("alias"):
            surfaces.append((item["alias"], "alias"))

        title_matches: list[dict] = []
        heading_matches: list[dict] = []

        for surface, role in surfaces:
            norm = normalize_name(surface)
            if not norm:
                continue
            for relpath, via in title_exact.get(norm, []):
                title_matches.append(
                    {"note": relpath, "kind": "exact", "surface_role": role, "via": via}
                )
            for relpath, heading_text in heading_exact.get(norm, []):
                heading_matches.append(
                    {"note": relpath, "heading": heading_text, "kind": "exact", "surface_role": role}
                )
            # partial matching: only for multi-token or >=8-char surfaces
            if len(norm.split()) >= 2 or len(norm) >= 8:
                for target_norm, relpath, kind, display in partial_targets:
                    if norm == target_norm:
                        continue
                    if norm in target_norm or (target_norm in norm and len(target_norm) >= 5):
                        rec = {
                            "note": relpath, "kind": "partial", "surface_role": role,
                            "surface": surface,
                        }
                        if kind == "title":
                            title_matches.append(rec)
                        else:
                            rec["heading"] = display
                            heading_matches.append(rec)

        # body matching with token prefilter
        per_note_counts: dict[str, int] = {}
        for surface, _role in surfaces:
            if not surface.strip():
                continue
            rx = _flexible_regex(surface)
            for note in notes:
                if not _surface_prefilter_ok(surface, note["token_set"]):
                    continue
                n = len(rx.findall(note["body"]))
                if n:
                    per_note_counts[note["relpath"]] = per_note_counts.get(note["relpath"], 0) + n

        body_occurrences = sum(per_note_counts.values())
        body_notes = len(per_note_counts)
        top_notes = sorted(per_note_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:5]

        exact_title = [m for m in title_matches if m["kind"] == "exact"]
        exact_heading = [m for m in heading_matches if m["kind"] == "exact"]
        partial_any = [m for m in title_matches + heading_matches if m["kind"] == "partial"]

        if exact_title:
            band = "title"
        elif exact_heading:
            band = "heading"
        elif partial_any:
            band = "partial"
        elif body_occurrences >= 2:
            band = "body-multi"
        elif body_occurrences == 1:
            band = "body-single"
        else:
            band = "none"
        band_counts[band] += 1
        for cluster in item.get("clusters", []):
            cluster_bands.setdefault(cluster, {}).setdefault(band, 0)
            cluster_bands[cluster][band] += 1

        results.append(
            {
                "item_id": item["item_id"],
                "name": item["name"],
                "alias": item.get("alias"),
                "band": band,
                "title_matches": _dedupe_matches(title_matches),
                "heading_matches": _dedupe_matches(heading_matches)[:10],
                "body": {
                    "notes": body_notes,
                    "occurrences": body_occurrences,
                    "top_notes": [{"note": n, "count": c} for n, c in top_notes],
                },
            }
        )

    aggregate = {
        "items_total": len(results),
        "notes_scanned": len(notes),
        "band_counts": band_counts,
        "cluster_bands": cluster_bands,
        "method": {
            "match_order": ["title", "heading", "partial", "body-multi", "body-single", "none"],
            "title": "normalized equality (ASCII fold, lowercase, punctuation->space, Brit->US) of name or alias vs note title or frontmatter alias",
            "heading": "normalized equality vs heading text (numbering prefix and decoration stripped)",
            "partial": "substring relation between surface and title/heading; only for multi-token or >=8-char surfaces (acronyms require equality)",
            "body": "word-boundary flexible token regex (separator-flexible, optional plural s/es, Brit/US alternation) over note bodies (frontmatter excluded, fences included), prefiltered by per-note token sets",
            "limitation": "lexical evidence only; terminology differences require the semantic judgment phase (campaign plan section 5)",
        },
    }
    return {"items": results, "aggregate": aggregate}


def _dedupe_matches(matches: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for m in matches:
        key = (m["note"], m.get("heading"), m["kind"], m["surface_role"], m.get("via"))
        if key not in seen:
            seen.add(key)
            out.append(m)
    return out


# ---------------------------------------------------------------------------
# serialization helpers


def inventory_items_jsonl(inventory: dict) -> list[str]:
    """Serialize inventory items to JSONL lines (stable field order)."""
    lines = []
    for item in inventory["items"]:
        rec = {
            "item_id": item["item_id"],
            "name": item["name"],
            "alias": item.get("alias"),
            "clusters": item["clusters"],
            "occurrences": item["occurrences"],
        }
        if item.get("group_labels"):
            rec["group_labels"] = item["group_labels"]
        if item.get("entity_types"):
            rec["entity_types"] = item["entity_types"]
        if item.get("principal_refs"):
            rec["principal_refs"] = item["principal_refs"]
        lines.append(json.dumps(rec, ensure_ascii=False))
    return lines


def coverage_items_jsonl(coverage: dict) -> list[str]:
    return [json.dumps(r, ensure_ascii=False) for r in coverage["items"]]


def load_inventory_items(path: str | Path) -> list[dict]:
    """Load item records from an inventory JSONL written by ``integ-inventory``.

    Validates record shape (``item_id`` + ``name`` required), rejects
    malformed lines and duplicate item ids loudly — the coverage phase must
    never run against a silently truncated or duplicated inventory.
    """
    path = Path(path)
    if not path.is_file():
        raise IntegrationError(f"inventory file not found: {path}")
    items: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise IntegrationError(f"malformed inventory JSONL at line {line_no}: {exc}") from exc
        if not isinstance(rec, dict) or not rec.get("item_id") or not rec.get("name"):
            raise IntegrationError(
                f"invalid item record at line {line_no} (item_id and name are required)"
            )
        items.append(rec)
    if not items:
        raise IntegrationError(f"inventory contains no item records: {path}")
    ids = [rec["item_id"] for rec in items]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise IntegrationError(f"duplicate item ids in inventory: {dupes}")
    return items

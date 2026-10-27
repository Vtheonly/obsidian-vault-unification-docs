"""Generation-prompt specification and validation (FRAME-002, CAP-021).

Before each generation batch, the agent should receive a carefully
constructed prompt: task, source evidence, expected output, quality
requirements, constraints, and TESTABLE validation criteria. This module
makes those prompts first-class, schema-validated artifacts so the toolkit
can check them BEFORE use, per the Phase 0 iterative-generation workflow:

- Is the objective precise (bounded to one note, names the target path)?
- Is the source evidence present and resolvable (ku_ids exist in the KU
  batches; file paths exist)?
- Is every acceptance criterion TESTABLE — mapped to a lint check id, a
  quality dimension, or explicitly marked manual_review? (Unverifiable
  criteria like "well-written" are rejected.)
- Is the task bounded for the context and output budget (estimated context
  size vs declared budget; requirements count; source-excerpt volume)?
- Are the standing constraints present (no invention, preserve unrelated
  content on repair, provenance requirements)?

The prompt-generation process is prevented from producing ever-longer
instructions: total requirements/constraints are capped with a warning,
and the context estimate is measured against the declared budget.

REPAIR PROMPTS: :func:`build_repair_prompt` converts a repair task
(:mod:`vault_unification.repair`) into a generation-prompt record with the
SMALLEST sufficient context (defect + excerpt + expected fix + acceptance
criterion = the originating check passing + scope discipline), so repairs
never degrade into whole-note rewrites.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

__all__ = [
    "PromptSpecError",
    "SCHEMA_VERSION",
    "VAGUE_TERMS",
    "check_prompt",
    "build_repair_prompt",
    "load_prompt_spec",
]

SCHEMA_VERSION = "1.0.0"

# words that signal an unoperationalized criterion when used inside an
# acceptance criterion or requirement without a measurable attachment
VAGUE_TERMS = (
    "good",
    "nice",
    "appropriate",
    "properly",
    "reasonable",
    "clean",
    "elegant",
    "well-written",
    "high quality",
    "polished",
    "thorough",
    "clearly",
    "as needed",
    "if necessary",
    "etc.",
)

_KNOWN_CHECK_IDS = frozenset(
    """
    FENCE_UNCLOSED CODE_LANG_MISSING CODE_LANG_UNKNOWN CODE_PYTHON_SYNTAX
    CODE_JSON_INVALID MERMAID_PARSE MATH_BLOCK_UNCLOSED MATH_INLINE_ODD
    MATH_ENV_MISMATCH MATH_DELIM_STYLE_MIXED TABLE_SEPARATOR_BAD
    TABLE_CELL_MISMATCH TABLE_SEPARATOR_MISSING HEADING_SKIP HEADING_EMPTY
    HEADING_MULTI_H1 LIST_INDENT_MIXED LINK_BROKEN LINK_AMBIGUOUS
    LINK_MISSING_ANCHOR LINK_MISSING_BLOCK TRUNCATION_MID_SENTENCE
    PLACEHOLDER_TEXT BRACKET_UNBALANCED FRONTMATTER_INVALID
    TRUNCATION_OPEN_CONSTRUCT EMPTY_SECTION
    """.split()
)

_KNOWN_DIMENSIONS = frozenset(
    """
    structure definitions depth math_rigor examples source_coverage
    provenance links editorial
    """.split()
)

_STANDING_CONSTRAINT_PATTERNS = (
    (r"invent|fabricat|make\s+up|hallucinat", "no-invention"),
    (r"unrelated|preserve|do\s+not\s+(?:rewrite|remove|alter)", "preserve-unrelated-content"),
    (r"provenance|source\s+attribution|cite", "provenance"),
)


class PromptSpecError(Exception):
    """Raised for invalid prompt-spec inputs."""


def load_prompt_spec(path: str | Path) -> dict:
    """Load a generation-prompt spec from a JSON file."""
    p = Path(path)
    if not p.is_file():
        raise PromptSpecError(f"prompt spec not found: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PromptSpecError(f"prompt spec is not valid JSON: {exc}") from exc


def _check_ids_ok(criterion: dict) -> bool:
    check = str(criterion.get("check", "")).strip()
    if check.startswith("lint:"):
        return check[5:] in _KNOWN_CHECK_IDS
    if check.startswith("quality:"):
        return check[8:] in _KNOWN_DIMENSIONS
    if check in ("manual_review", "registry:ku_accounted", "gate:batch_gate"):
        return True
    return check in _KNOWN_CHECK_IDS or check in _KNOWN_DIMENSIONS


def check_prompt(
    spec: dict,
    *,
    ku_batches: list[str | Path] | None = None,
    context_budget_words: int = 4000,
    max_requirements: int = 25,
) -> dict:
    """Validate a generation-prompt spec; returns per-check results.

    ku_batches: when provided, every ku_id referenced in source_evidence
    must exist in those batches (evidence resolvability).
    """
    if not isinstance(spec, dict):
        raise PromptSpecError("spec must be an object")
    results: list[dict] = []
    failures = 0

    def check(name: str, ok: bool, detail: str) -> None:
        nonlocal failures
        if not ok:
            failures += 1
        results.append({"check": name, "ok": ok, "detail": detail})

    # -- structure ------------------------------------------------------
    objective = spec.get("objective")
    check(
        "objective_present",
        isinstance(objective, str) and bool(objective.strip()),
        "objective must be a non-empty string",
    )
    target = spec.get("target_note") or {}
    if not isinstance(target, dict):
        target = {}
    check(
        "target_note_present",
        bool(target.get("path")),
        "target_note.path must name the note file to produce",
    )
    check(
        "target_type_known",
        str(target.get("type", "")).lower()
        in (
            "concept",
            "reference",
            "tutorial",
            "derivation",
            "overview",
            "example",
            "generic",
            "repair",
        ),
        "target_note.type must be a known note type (drives the quality standard; 'repair' for targeted repair prompts)",
    )

    # -- source evidence --------------------------------------------------
    evidence = spec.get("source_evidence") or {}
    ku_ids = evidence.get("ku_ids") or []
    file_paths = evidence.get("files") or []
    check(
        "source_evidence_present",
        bool(ku_ids or file_paths or evidence.get("dossier") or evidence.get("defect")),
        "source_evidence must carry ku_ids, files, a dossier reference, or (repairs) the defect record",
    )

    if ku_batches and ku_ids:
        known_ids: set[str] = set()
        for batch in ku_batches:
            with Path(batch).open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    kid = rec.get("ku_id") or rec.get("id")
                    if kid:
                        known_ids.add(str(kid))
        missing = [k for k in ku_ids if str(k) not in known_ids]
        check(
            "source_evidence_resolvable",
            not missing,
            f"ku_ids not found in provided batches: {missing[:8]}"
            + ("..." if len(missing) > 8 else "")
            if missing
            else f"all {len(ku_ids)} ku_ids resolve in the provided batches",
        )
    else:
        check(
            "source_evidence_resolvable",
            True,
            "not checked (no ku batches provided)" if ku_ids else "no ku_ids to resolve",
        )

    for fp in file_paths:
        check(
            f"source_file_exists:{fp}",
            Path(fp).is_file(),
            f"source file {fp} must exist",
        )

    # -- acceptance criteria --------------------------------------------
    criteria = spec.get("acceptance_criteria") or []
    check(
        "acceptance_criteria_present",
        len(criteria) > 0,
        "at least one acceptance criterion is required",
    )
    untestable: list[str] = []
    for c in criteria:
        if not isinstance(c, dict):
            untestable.append(str(c)[:60])
            continue
        if not _check_ids_ok(c):
            untestable.append(f"{c.get('check', '?')}: {str(c.get('criterion', ''))[:60]}")
    check(
        "acceptance_criteria_testable",
        not untestable,
        "every criterion must map to a lint check, quality dimension, "
        "registry/gate reference, or be explicitly 'manual_review'; "
        f"untestable: {untestable[:5]}"
        if untestable
        else f"all {len(criteria)} criteria are testable or explicitly manual",
    )
    machine_checks = [c for c in criteria if isinstance(c, dict) and not str(c.get("check")) == "manual_review"]
    check(
        "at_least_one_machine_check",
        len(machine_checks) > 0,
        "at least one criterion must be machine-checkable (lint/quality/registry/gate)",
    )

    # vague language inside criteria
    vague_hits: list[str] = []
    for c in criteria:
        text = json.dumps(c, ensure_ascii=False) if isinstance(c, dict) else str(c)
        for term in VAGUE_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
                vague_hits.append(f"{term} in: {text[:70]}")
    check(
        "no_unoperationalized_language",
        not vague_hits,
        "; ".join(vague_hits[:3]) if vague_hits else "no vague quality language in criteria",
    )

    # -- constraints ------------------------------------------------------
    constraints = spec.get("constraints") or []
    check(
        "constraints_present",
        len(constraints) > 0,
        "standing constraints must be listed explicitly",
    )
    constraint_text = " ".join(str(c) for c in constraints).lower()
    for pattern, label in _STANDING_CONSTRAINT_PATTERNS:
        check(
            f"constraint:{label}",
            re.search(pattern, constraint_text) is not None,
            f"standing constraint '{label}' not found in constraints",
        )

    # -- boundedness -----------------------------------------------------
    requirements = spec.get("requirements") or []
    check(
        "requirements_bounded",
        len(requirements) <= max_requirements,
        f"{len(requirements)} requirements exceeds the cap {max_requirements}; "
        "split the task — do not grow the prompt indefinitely"
        if len(requirements) > max_requirements
        else f"{len(requirements)} requirements (cap {max_requirements})",
    )

    # context estimate: excerpt words + requirement words
    est = 0
    for c in criteria + requirements + constraints:
        est += len(re.findall(r"\S+", json.dumps(c, ensure_ascii=False)))
    excerpts = evidence.get("excerpts") or []
    for ex in excerpts:
        est += len(re.findall(r"\S+", ex if isinstance(ex, str) else json.dumps(ex)))
    check(
        "context_budget_respected",
        est <= context_budget_words,
        f"estimated context {est} words <= budget {context_budget_words}"
        if est <= context_budget_words
        else f"estimated context {est} words EXCEEDS budget {context_budget_words}; trim source material",
    )

    # -- output contract -------------------------------------------------
    contract = spec.get("output_contract") or {}
    check(
        "output_contract_present",
        bool(contract.get("path")) and bool(contract.get("format")),
        "output_contract must declare path and format",
    )

    ok = failures == 0
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": ok,
        "failures": failures,
        "checks": results,
        "estimated_context_words": est,
        "context_budget_words": context_budget_words,
        "spec_objective": objective if isinstance(objective, str) else "",
    }


def build_repair_prompt(task: dict, *, note_path: str, max_context_lines: int = 24) -> dict:
    """Convert a repair task into a generation-prompt spec record.

    The prompt carries the SMALLEST sufficient context: the defect, its
    excerpt, the expected fix, the acceptance criterion (the originating
    check passing + no new defects + local scope), and the standing
    constraints. It explicitly forbids rewriting unrelated content.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "objective": (
            f"Repair ONE defect in {note_path}: {task['check']} at line {task['line']} — {task['message']}"
        ),
        "target_note": {"path": note_path, "type": "repair"},
        "source_evidence": {
            "defect": {
                "repair_id": task["repair_id"],
                "check": task["check"],
                "line": task["line"],
                "message": task["message"],
                "excerpt": task.get("original_excerpt", "")[:2000],
            }
        },
        "requirements": [
            task["expected_fix"],
            "make the smallest possible edit that fixes the defect",
        ],
        "constraints": [
            "do not rewrite or remove unrelated content; the repair must stay local to the defect region",
            "do not invent content; if the fix needs facts, they must come from the cited source evidence",
            "preserve provenance links and source attribution",
        ],
        "acceptance_criteria": [
            {"criterion": f"check {task['check']} no longer fires on this file", "check": f"lint:{task['check']}"},
            {"criterion": "no new lint defects introduced", "check": "gate:batch_gate"},
            {"criterion": "diff stays local to the defect region", "check": "manual_review"},
        ],
        "output_contract": {"path": note_path, "format": "markdown (in-place edit)"},
        "max_context_lines": max_context_lines,
    }

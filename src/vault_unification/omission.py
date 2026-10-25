"""Omission-detection pilot and reusable output auditor (CAP-012).

This module implements the hard gate required before any large-scale
synthesis (AGENTS.md section 7.5, TOOLING_FRAMEWORK.md sections 7 and 9,
VERIFICATION_SPECIFICATION.md sections 6 and 13):

- :func:`build_fixture` creates a *synthetic* paired-source fixture in an
  explicit destination (never inside the protected source vaults): two source
  notes with exact and semantic duplicates, partial overlap, complementary
  theory/code, a conflicting historical attribution, a rare fact, equations
  with intermediate derivation steps, a project caveat, code blocks and
  internal links; a known-good baseline synthesis; a KU batch whose records
  carry IDs minted through :func:`vault_unification.kuregistry.mint_ku_id`;
  and an accepted-output manifest of the baseline.
- :data:`DEFECTS` declares twelve planted defects mirroring the deliberate
  omission/corruption taxonomy of VERIFICATION_SPECIFICATION.md (unique
  detail, equation, derivation step, caveat, sign alteration, obscure
  one-off concept, broken link, heading-convention change, bullet-only
  prose degradation, version-distinction loss, accepted-output drift during
  later repair, implementation-parameter deletion).
- :func:`apply_mutation` writes each defect into a *copy* of the baseline.
- :func:`audit_output` is the reusable, real-work audit pipeline: output
  inventory regression against an accepted manifest, KU batch validation,
  disposition/destination accounting, marker retention (rare-term,
  equation and code fingerprints), link integrity, heading-convention and
  prose-quality lint. Findings always carry stable KU IDs and destination
  locators.
- :func:`run_pilot` orchestrates the whole experiment: audit the clean
  baseline (false positives must be zero), mutate one defect at a time,
  re-audit and compare findings, and report detection + localization per
  defect with explicit denominators.

Honesty rules: the pilot verdict is fail unless *every* declared defect is
detected AND localized to the expected KU and destination note and the
clean baseline produces zero findings. A passing unit test that does not
exercise the omission path does not count as pilot evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import unicodedata
from pathlib import Path

from .inventory import load_manifest, manifest_records, scan_root, write_manifest
from .kuregistry import mint_ku_id
from .linkcheck import check_links
from .mdextract import extract_structure, heading_path
from .pathsafety import ensure_dest_safe
from .registry import load_jsonl_records, validate_ku_file  # noqa: F401 (load_jsonl_records re-exported for CLI/tests)

# ---------------------------------------------------------------------------
# synthetic fixture content (fixed constants => deterministic KU IDs/hashes)
# ---------------------------------------------------------------------------

VAULT_A_NOTE = r"""---
tags: [neural-networks, optimization, deep-learning]
---

# Backpropagation - Deep Working Notes (Vault A)

## 1. The Chain Rule Foundation

Backpropagation is the algorithm that computes the gradient of the loss with respect to every weight in a network by applying the chain rule backwards through the composition of layers. For a two-layer network the total derivative expands into a product of local factors:

$$
\frac{\partial L}{\partial w_1}
= \frac{\partial L}{\partial a}\,\frac{\partial a}{\partial z}\,\frac{\partial z}{\partial w_1}
$$

where L is the scalar loss, a the activation of the output unit, z the pre-activation and w_1 a first-layer weight. The beauty of the formulation is that each factor is a local computation available inside its own layer, which is what makes the algorithm cheap to run.

### 1.1 Derivation Step by Step

First write the squared loss for one example as $L = (a - y)^2$ where y is the target value. Second, differentiate the outer function with respect to the activation:

$$
\frac{\partial L}{\partial a} = 2(a - y)
$$

Third, differentiate the sigmoid activation with respect to its pre-activation, which yields the classic self-gated form:

$$
\frac{\partial a}{\partial z} = \sigma(z)(1 - \sigma(z))
$$

Fourth, fold the factors into the gradient descent update rule for a single timestep, where the timestep superscript keeps training iterations distinct:

$$
\Delta w^{(t)} = -\eta \,\delta^{(t)}\,x^{(t)}
$$

## 2. Project Caveats From the 2022 Warehouse Forecast

In the 2022 warehouse-demand forecasting project the team discovered that backpropagation silently produced NaN gradients whenever the learning rate exceeded 0.5 on the unnormalized inventory features. The post-mortem recommended always running a numerical gradient check before trusting a new architecture, and logging the gradient norm per batch. This lesson cost three debugging days and is recorded here so it is not repeated.

## 3. Rare Historical Note on Priority

Seppo Linnainmaa first coded the reverse mode of automatic differentiation in his 1970 master's thesis at the University of Helsinki, sixteen years before Rumelhart, Hinton and Williams popularized backpropagation in 1986. Most course material omits this priority question entirely, which is why it is recorded here.

## 4. Version Distinction: PyTorch 1.x vs 2.0

In PyTorch 1.x, calling .backward() twice on the same graph without retain_graph=True raised a RuntimeError about freeing the graph buffers; since PyTorch 2.0 the same double call still raises but the error message explicitly names the intermediate buffers being released. Code that parsed the 1.x message text broke when upgrading, so the distinction matters for regression tests.

## 5. Reference Implementation

```python
def backward_pass(grad_output, layer):
    delta = grad_output * layer.activation_derivative(layer.z)
    layer.dW = delta @ layer.x.T
    return delta @ layer.W.T
```

See also [[Gradient Descent]] and [[Chain Rule Refresher]].
"""

VAULT_B_NOTE = r"""# Backpropagation (Course Notes)

## Overview

Backpropagation is the standard algorithm for training neural networks: it measures how much each weight contributed to the prediction error by propagating the loss gradient backwards from the output layer to the input layer, one layer at a time. The course notes attribute the popularization of backpropagation to Parker's 1985 report, a chronology that differs from the deeper vault's account and is worth recording explicitly.

## Loss Gradient Equation

The loss gradient with respect to the activation for the squared loss is the same everywhere in the course material:

$$
\frac{\partial L}{\partial a} = 2(a - y)
$$

## Weight Update Rule

The weight update follows $\Delta w = -\eta \delta x$, where $\eta$ is the learning rate, $\delta$ the local error signal and $x$ the input to the layer.

## Numerical Gradient Check

A practical debugging technique is to compare the analytic gradient against a finite-difference approximation:

```python
def numerical_gradient(f, x, eps=1e-5):
    return (f(x + eps) - f(x - eps)) / (2 * eps)
```

## Further Reading

Read [[Automatic Differentiation]] for the broader context of reverse-mode differentiation.
"""

BASELINE_MAIN_NOTE = r"""---
tags: [neural-networks, optimization, deep-learning]
---

# Backpropagation

## 1. The Chain Rule Foundation

Backpropagation is the standard algorithm for training neural networks: it measures how much each weight contributed to the prediction error by propagating the loss gradient backwards from the output layer to the input layer, one layer at a time. For a two-layer network the total derivative expands into a product of local factors, computed by applying the chain rule backwards through the composition of layers:

$$
\frac{\partial L}{\partial w_1}
= \frac{\partial L}{\partial a}\,\frac{\partial a}{\partial z}\,\frac{\partial z}{\partial w_1}
$$

where L is the scalar loss, a the activation of the output unit, z the pre-activation and w_1 a first-layer weight. The beauty of the formulation is that each factor is a local computation available inside its own layer, which is what makes the algorithm cheap to run.

### 1.1 Derivation Step by Step

First write the squared loss for one example as $L = (a - y)^2$ where y is the target value. Second, differentiate the outer function with respect to the activation:

$$
\frac{\partial L}{\partial a} = 2(a - y)
$$

The same loss-gradient equation is used everywhere in the course material.

Third, differentiate the sigmoid activation with respect to its pre-activation, which yields the classic self-gated form:

$$
\frac{\partial a}{\partial z} = \sigma(z)(1 - \sigma(z))
$$

Fourth, fold the factors into the gradient descent update rule for a single timestep, where the timestep superscript keeps training iterations distinct:

$$
\Delta w^{(t)} = -\eta \,\delta^{(t)}\,x^{(t)}
$$

The simpler untimed form $\Delta w = -\eta \delta x$ from the course notes follows the same rule with the iteration superscripts dropped: $\eta$ is the learning rate, $\delta$ the local error signal and $x$ the input to the layer.

## 2. Project Caveats From the 2022 Warehouse Forecast

In the 2022 warehouse-demand forecasting project the team discovered that backpropagation silently produced NaN gradients whenever the learning rate exceeded 0.5 on the unnormalized inventory features. The post-mortem recommended always running a numerical gradient check before trusting a new architecture, and logging the gradient norm per batch. This lesson cost three debugging days and is recorded here so it is not repeated.

## 3. Rare Historical Note on Priority

Seppo Linnainmaa first coded the reverse mode of automatic differentiation in his 1970 master's thesis at the University of Helsinki, sixteen years before Rumelhart, Hinton and Williams popularized backpropagation in 1986. Most course material omits this priority question entirely, which is why it is recorded here. The course notes attribute the popularization of backpropagation to Parker's 1985 report, a chronology that differs from the deeper vault's account and is worth recording explicitly; both accounts are retained and the discrepancy is recorded rather than silently resolved, with the deep notes following the conventional 1986 attribution to Rumelhart, Hinton and Williams.

## 4. Version Distinction: PyTorch 1.x vs 2.0

In PyTorch 1.x, calling .backward() twice on the same graph without retain_graph=True raised a RuntimeError about freeing the graph buffers; since PyTorch 2.0 the same double call still raises but the error message explicitly names the intermediate buffers being released. Code that parsed the 1.x message text broke when upgrading, so the distinction matters for regression tests.

## 5. Reference Implementation

The reference implementation below shows the backward pass for a single dense layer, computing the local delta from the upstream gradient before accumulating the weight update; it mirrors the derivation in section 1.1:

```python
def backward_pass(grad_output, layer):
    delta = grad_output * layer.activation_derivative(layer.z)
    layer.dW = delta @ layer.x.T
    return delta @ layer.W.T
```

## 6. Numerical Gradient Check

A practical debugging technique is to compare the analytic gradient produced by backpropagation against an independent finite-difference approximation evaluated at the same point; the two estimates should agree to several decimal places whenever the implementation is correct:

```python
def numerical_gradient(f, x, eps=1e-5):
    return (f(x + eps) - f(x - eps)) / (2 * eps)
```

## 7. Further Reading

See also [[Gradient Descent]] for the optimization side, [[Chain Rule Refresher]] for the calculus background, and [[Automatic Differentiation]] for the broader context of reverse-mode differentiation in general; read them in that order.
"""

BASELINE_STUB_NOTES: dict[str, str] = {
    "Neural Networks/Gradient Descent.md": """---
tags: [optimization]
---

# Gradient Descent

## 1. Overview

Gradient descent is the iterative optimization procedure that underlies network training: every step moves the parameters against the current gradient of the objective, by an amount fixed by a scalar hyperparameter.

## 2. See Also

Related notes in this vault: [[Backpropagation]].
""",
    "Neural Networks/Chain Rule Refresher.md": """---
tags: [calculus]
---

# Chain Rule Refresher

## 1. Overview

The chain rule differentiates a composition of functions by multiplying the derivatives of the inner and outer functions; it is the calculus fact that makes backward computation of gradients possible.

## 2. See Also

Related notes in this vault: [[Backpropagation]].
""",
    "Neural Networks/Automatic Differentiation.md": """---
tags: [calculus, automatic-differentiation]
---

# Automatic Differentiation

## 1. Overview

Automatic differentiation computes derivatives of programs by applying elementary differentiation rules to each primitive operation, in reverse mode for efficiency.

## 2. See Also

Related notes in this vault: [[Backpropagation]].
""",
}

MAIN_NOTE_RELPATH = "Neural Networks/Backpropagation.md"

# section specs: (source key, heading text, unit_type, disposition, overlap,
#                 destination heading or None to reuse source heading)
_VAULT_A_SECTIONS = [
    ("intro", "1. The Chain Rule Foundation", "theory", "Preserved", None, None),
    (
        "derivation",
        "1.1 Derivation Step by Step",
        "derivation",
        "Preserved",
        None,
        None,
    ),
    (
        "caveat",
        "2. Project Caveats From the 2022 Warehouse Forecast",
        "project-caveat",
        "Preserved",
        None,
        None,
    ),
    (
        "history",
        "3. Rare Historical Note on Priority",
        "historical-note",
        "Contextualized",
        "Conflict or Historical Difference",
        None,
    ),
    (
        "version",
        "4. Version Distinction: PyTorch 1.x vs 2.0",
        "version-note",
        "Preserved",
        None,
        None,
    ),
    (
        "implementation",
        "5. Reference Implementation",
        "code",
        "Preserved",
        None,
        None,
    ),
]

_VAULT_B_SECTIONS = [
    (
        "overview",
        "Overview",
        "theory",
        "Consolidated",
        "Semantic Duplicate",
        "1. The Chain Rule Foundation",
    ),
    (
        "equation",
        "Loss Gradient Equation",
        "equation",
        "Consolidated",
        "Exact Duplicate",
        "1.1 Derivation Step by Step",
    ),
    (
        "update",
        "Weight Update Rule",
        "claim",
        "Consolidated",
        "Partial Overlap",
        "1.1 Derivation Step by Step",
    ),
    (
        "numerical",
        "Numerical Gradient Check",
        "code",
        "Preserved",
        "Complementary Content",
        "6. Numerical Gradient Check",
    ),
    (
        "further",
        "Further Reading",
        "reference",
        "Preserved",
        "Complementary Content",
        "7. Further Reading",
    ),
]

# extra destinations for vault-b KUs whose evidence also lands elsewhere
_VAULT_B_EXTRA_DESTINATIONS = {
    "overview": "3. Rare Historical Note on Priority",
}


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def json_dumps(obj) -> str:
    """Canonical JSON for fixture files (sorted keys, UTF-8, trailing newline)."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n"


def _write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _section_span(lines: list[str], headings: list[dict], heading_text: str) -> tuple[int, int, list[str]]:
    """Return (start_line, end_line, heading_path) for the section under
    *heading_text* (1-based, body only, excluding the heading line itself).

    The section ends right before the next heading of any level, which is
    the KU segmentation convention used by this fixture.
    """
    target = None
    for heading in headings:
        if heading["text"] == heading_text:
            target = heading
            break
    if target is None:
        raise ValueError(f"heading not found in fixture note: {heading_text!r}")
    next_line = len(lines) + 1
    for heading in headings:
        if heading["line"] > target["line"]:
            next_line = heading["line"]
            break
    body_start = target["line"] + 1
    body_end = next_line - 1
    while body_end >= body_start and not lines[body_end - 1].strip():
        body_end -= 1
    hpath = heading_path(headings, target["line"])
    return body_start, body_end, hpath


def build_fixture(dest_root: str | Path, *, protected_roots: list | None = None) -> dict:
    """Create the synthetic omission-pilot fixture under *dest_root*.

    Layout produced::

        <dest>/sources/vault-a/backpropagation.md
        <dest>/sources/vault-b/backpropagation.md
        <dest>/output-baseline/Neural Networks/*.md
        <dest>/ku-batch.jsonl
        <dest>/accepted-manifest.jsonl
        <dest>/fixture-manifest.json

    The destination is refused when it lies inside a protected root.
    """
    dest = ensure_dest_safe(dest_root, protected_roots or [])
    dest = Path(dest)
    sources_root = dest / "sources"
    output_root = dest / "output-baseline"
    ku_batch_path = dest / "ku-batch.jsonl"
    accepted_manifest_path = dest / "accepted-manifest.jsonl"

    _write_file(sources_root / "vault-a" / "backpropagation.md", VAULT_A_NOTE)
    _write_file(sources_root / "vault-b" / "backpropagation.md", VAULT_B_NOTE)
    _write_file(output_root / MAIN_NOTE_RELPATH, BASELINE_MAIN_NOTE)
    for relpath, text in BASELINE_STUB_NOTES.items():
        _write_file(output_root / relpath, text)

    # ---- mint KU records with stable, content-derived IDs ----
    records: list[dict] = []
    for source_id, relpath, note_text, sections, vault_dir in (
        (
            "SRC-FIXTURE-VA",
            "sources/vault-a/backpropagation.md",
            VAULT_A_NOTE,
            _VAULT_A_SECTIONS,
            "vault-a",
        ),
        (
            "SRC-FIXTURE-VB",
            "sources/vault-b/backpropagation.md",
            VAULT_B_NOTE,
            _VAULT_B_SECTIONS,
            "vault-b",
        ),
    ):
        lines = note_text.splitlines()
        structure = extract_structure(sources_root / vault_dir / "backpropagation.md")
        file_hash = _sha256_text(note_text)
        for key, heading_text, unit_type, disposition, overlap, dest_heading in sections:
            start, end, hpath = _section_span(lines, structure["headings"], heading_text)
            excerpt = "\n".join(lines[start - 1 : end])
            record = {
                "knowledge_unit_id": "",
                "source_id": source_id,
                "source_path": relpath,
                "source_file_hash": file_hash,
                "source_format": "markdown",
                "heading_path": hpath,
                "line_start": start,
                "line_end": end,
                "excerpt": excerpt,
                "unit_type": unit_type,
                "concept_ids": ["backpropagation"],
                "disposition": disposition,
                "destinations": [
                    {"path": MAIN_NOTE_RELPATH, "heading": dest_heading or heading_text}
                ],
                "verification_status": {
                    "extraction": "fixture-builder",
                    "semantic": "pending",
                },
            }
            if overlap:
                record["overlap_type"] = overlap
            record["knowledge_unit_id"] = mint_ku_id(record)
            records.append(record)

    # extra destinations + supporting-unit links (provenance richness)
    by_key: dict[tuple[str, str], dict] = {}
    for record in records:
        vault_key = "vault-a" if record["source_id"] == "SRC-FIXTURE-VA" else "vault-b"
        for key, heading_text, *_ in (_VAULT_A_SECTIONS if vault_key == "vault-a" else _VAULT_B_SECTIONS):
            if record["heading_path"][-1] == heading_text:
                by_key[(vault_key, key)] = record
    for b_key, extra_heading in _VAULT_B_EXTRA_DESTINATIONS.items():
        record = by_key.get(("vault-b", b_key))
        if record:
            record["destinations"].append({"path": MAIN_NOTE_RELPATH, "heading": extra_heading})
    for b_key, a_key in (("equation", "derivation"), ("update", "derivation"), ("overview", "intro")):
        b_record = by_key.get(("vault-b", b_key))
        a_record = by_key.get(("vault-a", a_key))
        if b_record and a_record:
            b_record["supporting_unit_ids"] = [a_record["knowledge_unit_id"]]

    with open(ku_batch_path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json_dumps(record))
    # accepted manifest of the baseline output (post-acceptance snapshot)
    scan = scan_root(output_root)
    write_manifest(accepted_manifest_path, manifest_records(scan))

    fixture_manifest = {
        "sources_root": str(sources_root),
        "output_root": str(output_root),
        "ku_batch_path": str(ku_batch_path),
        "accepted_manifest_path": str(accepted_manifest_path),
        "source_files": {
            "vault-a": _sha256_text(VAULT_A_NOTE),
            "vault-b": _sha256_text(VAULT_B_NOTE),
        },
        "ku_records": len(records),
        "ku_ids": sorted(r["knowledge_unit_id"] for r in records),
        "output_files": sorted(
            rec["relpath"] for rec in manifest_records(scan_root(output_root))
        ),
    }
    _write_file(dest / "fixture-manifest.json", json_dumps(fixture_manifest))
    return fixture_manifest


# ---------------------------------------------------------------------------
# marker machinery: deterministic fingerprints used by the retention checks
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*")
_FENCE_RE = re.compile(r"```[^\n]*\n.*?```", re.S)
_FENCE_BODY_RE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
_DISPLAY_MATH_RE = re.compile(r"\$\$(.+?)\$\$", re.S)
_INLINE_MATH_RE = re.compile(r"(?<!\$)\$([^$\n]+?)\$(?!\$)")
_NUMBERED_HEADING_RE = re.compile(r"^(\d+(?:\.\d+)*)[.)]?\s+\S")
_LIST_LINE_RE = re.compile(r"^(?:[-*+]\s|\d+[.)]\s)")

RARE_TERM_MAX_COUNT = 4  # a term occurring <= this often in the source corpus is a marker
MIN_PROSE_WORDS = 30  # sections receiving KU destinations must carry at least this much prose

DEFAULT_KU_SCHEMA = Path(__file__).resolve().parents[2] / "schemas" / "knowledge-unit.schema.json"


def _norm_ws(text: str) -> str:
    return " ".join(text.split())


def _strip_fences(text: str) -> str:
    return _FENCE_RE.sub("", text)


def _math_markers(text: str) -> list[str]:
    """Normalized display ($$...$$) and inline ($...$) math strings."""
    visible = _strip_fences(text)
    markers = [_norm_ws(m) for m in _DISPLAY_MATH_RE.findall(visible)]
    for line in visible.splitlines():
        markers.extend(_norm_ws(m) for m in _INLINE_MATH_RE.findall(line))
    return [m for m in markers if m]


def _code_bodies(text: str) -> list[str]:
    """Normalized fenced-code bodies (trailing whitespace stripped per line)."""
    bodies = []
    for body in _FENCE_BODY_RE.findall(text):
        normalized = "\n".join(line.rstrip() for line in body.split("\n")).strip("\n")
        if normalized:
            bodies.append(normalized)
    return bodies


def _clean_token(token: str) -> str:
    return token.strip(".-")


def _term_tokens(text: str) -> list[str]:
    tokens = (_clean_token(tok) for tok in _TOKEN_RE.findall(text))
    return [tok.casefold() for tok in tokens if len(_clean_token(tok)) >= 4]


def _term_frequency(source_texts: list[str]) -> dict[str, int]:
    freq: dict[str, int] = {}
    for text in source_texts:
        for token in _term_tokens(text):
            freq[token] = freq.get(token, 0) + 1
    return freq


def markers_for_record(record: dict, freq: dict[str, int], *, max_count: int = RARE_TERM_MAX_COUNT) -> dict:
    """Markers a KU excerpt contributes to the retention checks.

    - ``terms``: casefolded tokens that are rare in the source corpus;
    - ``math``: normalized equation strings (LaTeX preserved, whitespace collapsed);
    - ``code``: normalized fenced-code bodies.
    """
    excerpt = record.get("excerpt") or ""
    terms = sorted({t for t in _term_tokens(excerpt) if freq.get(t, 0) <= max_count})
    return {"terms": terms, "math": _math_markers(excerpt), "code": _code_bodies(excerpt)}


def _term_present(term: str, output_token_set: set[str]) -> bool:
    """Token-exact presence: the output corpus is tokenized with the same
    tokenizer as marker extraction, so 'value' matches 'value.' (end of
    sentence) but not 'values'."""
    return term in output_token_set


def _iter_markdown_files(root: str | Path):
    root_path = Path(root)
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", ".obsidian"))
        for name in sorted(filenames):
            if name.lower().endswith(".md"):
                abs_path = Path(dirpath) / name
                yield abs_path.relative_to(root_path).as_posix(), abs_path


def _heading_number_stripped(text: str) -> str:
    return _NUMBERED_HEADING_RE.sub("", text).strip().casefold()


def _note_sections(text: str, headings: list[dict]) -> list[tuple[str, list[str]]]:
    """(heading_text, body_lines) pairs; body excludes the heading line."""
    lines = text.splitlines()
    sections: list[tuple[str, list[str]]] = []
    for index, heading in enumerate(headings):
        start = heading["line"]  # 1-based
        end = headings[index + 1]["line"] - 1 if index + 1 < len(headings) else len(lines)
        sections.append((heading["text"], lines[start:end]))
    return sections


def _prose_word_count(body_lines: list[str]) -> int:
    words = 0
    in_fence = False
    in_math = False
    for line in body_lines:
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped == "$$":
            in_math = not in_math
            continue
        if in_math:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith((">", "|")) or _LIST_LINE_RE.match(stripped):
            continue
        words += len(stripped.split())
    return words


# ---------------------------------------------------------------------------
# planted defects (each mutates a *copy* of the baseline output)
# ---------------------------------------------------------------------------

def _read_main(root: Path) -> tuple[Path, str]:
    path = Path(root) / MAIN_NOTE_RELPATH
    return path, path.read_text(encoding="utf-8")


def _require_anchor(text: str, fragment: str, count: int = 1) -> None:
    found = text.count(fragment)
    if found != count:
        raise ValueError(
            f"mutation anchor not found {count}x (found {found}): {fragment[:70]!r}"
        )


def _mut_unique_detail(root: Path) -> str:
    """D01: delete the rare-fact sentence (Linnainmaa priority note)."""
    path, text = _read_main(root)
    fragment = (
        "Seppo Linnainmaa first coded the reverse mode of automatic "
        "differentiation in his 1970 master's thesis at the University of "
        "Helsinki, sixteen years before Rumelhart, Hinton and Williams "
        "popularized backpropagation in 1986. Most course material omits "
        "this priority question entirely, which is why it is recorded here. "
    )
    _require_anchor(text, fragment)
    path.write_text(text.replace(fragment, ""), encoding="utf-8")
    return "removed the Linnainmaa rare-fact sentences from section 3"


def _mut_equation_omission(root: Path) -> str:
    """D02: delete the final update-rule equation block."""
    path, text = _read_main(root)
    fragment = "$$\n\\Delta w^{(t)} = -\\eta \\,\\delta^{(t)}\\,x^{(t)}\n$$\n\n"
    _require_anchor(text, fragment)
    path.write_text(text.replace(fragment, ""), encoding="utf-8")
    return "removed the timestep update-rule display equation from section 1.1"


def _mut_derivation_step(root: Path) -> str:
    """D03: delete one intermediate derivation equation."""
    path, text = _read_main(root)
    fragment = "$$\n\\frac{\\partial a}{\\partial z} = \\sigma(z)(1 - \\sigma(z))\n$$\n\n"
    _require_anchor(text, fragment)
    path.write_text(text.replace(fragment, ""), encoding="utf-8")
    return "removed the intermediate sigmoid-derivative equation from section 1.1"


def _mut_caveat_omission(root: Path) -> str:
    """D04: drop the project caveat paragraph, keep a one-line stub."""
    path, text = _read_main(root)
    fragment = (
        "In the 2022 warehouse-demand forecasting project the team discovered "
        "that backpropagation silently produced NaN gradients whenever the "
        "learning rate exceeded 0.5 on the unnormalized inventory features. "
        "The post-mortem recommended always running a numerical gradient check "
        "before trusting a new architecture, and logging the gradient norm per "
        "batch. This lesson cost three debugging days and is recorded here so "
        "it is not repeated."
    )
    _require_anchor(text, fragment)
    path.write_text(text.replace(fragment, "See the project log for details."), encoding="utf-8")
    return "replaced the 2022 warehouse-forecast caveat paragraph with a stub sentence"


def _mut_sign_alteration(root: Path) -> str:
    """D05: flip a sign inside an equation (2(a - y) -> 2(a + y))."""
    path, text = _read_main(root)
    old = "$$\n\\frac{\\partial L}{\\partial a} = 2(a - y)\n$$"
    new = "$$\n\\frac{\\partial L}{\\partial a} = 2(a + y)\n$$"
    _require_anchor(text, old)
    path.write_text(text.replace(old, new), encoding="utf-8")
    return "flipped the sign in the loss-gradient equation (a - y -> a + y)"


def _mut_obscure_concept(root: Path) -> str:
    """D06: remove the entire one-off Numerical Gradient Check section."""
    path, text = _read_main(root)
    start_marker = "## 6. Numerical Gradient Check"
    end_marker = "## 7. Further Reading"
    _require_anchor(text, start_marker)
    _require_anchor(text, end_marker)
    start = text.index(start_marker)
    end = text.index(end_marker)
    path.write_text(text[:start] + text[end:], encoding="utf-8")
    return "deleted the whole Numerical Gradient Check section (one-file concept)"


def _mut_link_break(root: Path) -> str:
    """D07: retarget an internal wikilink to a non-existent note."""
    path, text = _read_main(root)
    old = "[[Chain Rule Refresher]]"
    new = "[[Chain Rule Basics]]"
    _require_anchor(text, old)
    path.write_text(text.replace(old, new), encoding="utf-8")
    return "retargeted the Chain Rule Refresher wikilink to a missing note"


def _mut_heading_convention(root: Path) -> str:
    """D08: strip the number from one heading inside a numbered note."""
    path, text = _read_main(root)
    old = "## 4. Version Distinction: PyTorch 1.x vs 2.0"
    new = "## Version Distinction: PyTorch 1.x vs 2.0"
    _require_anchor(text, old)
    path.write_text(text.replace(old, new), encoding="utf-8")
    return "dropped the numbering of heading 4, breaking the section convention"


def _mut_prose_degradation(root: Path) -> str:
    """D09: replace section 1 prose with terse bullet fragments."""
    path, text = _read_main(root)
    para_one = (
        "Backpropagation is the standard algorithm for training neural "
        "networks: it measures how much each weight contributed to the "
        "prediction error by propagating the loss gradient backwards from the "
        "output layer to the input layer, one layer at a time. For a two-layer "
        "network the total derivative expands into a product of local factors, "
        "computed by applying the chain rule backwards through the composition "
        "of layers:"
    )
    para_two = (
        "where L is the scalar loss, a the activation of the output unit, z "
        "the pre-activation and w_1 a first-layer weight. The beauty of the "
        "formulation is that each factor is a local computation available "
        "inside its own layer, which is what makes the algorithm cheap to run."
    )
    _require_anchor(text, para_one)
    _require_anchor(text, para_two)
    degraded = (
        "- computes the loss gradient per weight\n"
        "- chain rule applied backwards\n"
        "- every factor is local to its layer\n"
    )
    text = text.replace(para_one, degraded.rstrip("\n"))
    text = text.replace(para_two, "- L is the loss, a the activation, z the pre-activation")
    path.write_text(text, encoding="utf-8")
    return "degraded section 1 prose into bullet-only fragments"


def _mut_version_loss(root: Path) -> str:
    """D10: silently resolve the version distinction away."""
    path, text = _read_main(root)
    fragment = (
        "In PyTorch 1.x, calling .backward() twice on the same graph without "
        "retain_graph=True raised a RuntimeError about freeing the graph "
        "buffers; since PyTorch 2.0 the same double call still raises but the "
        "error message explicitly names the intermediate buffers being "
        "released. Code that parsed the 1.x message text broke when "
        "upgrading, so the distinction matters for regression tests."
    )
    _require_anchor(text, fragment)
    path.write_text(
        text.replace(fragment, "Calling .backward() twice on the same graph raises a RuntimeError."),
        encoding="utf-8",
    )
    return "collapsed the PyTorch 1.x vs 2.0 distinction into one unversioned claim"


def _mut_output_drift(root: Path) -> str:
    """D11: alter an accepted note after its manifest was recorded."""
    path, text = _read_main(root)
    path.write_text(text + "\nTODO: revisit this derivation before the next release.\n", encoding="utf-8")
    return "appended a TODO line to the accepted synthesis note"


def _mut_code_parameter(root: Path) -> str:
    """D12: delete an implementation parameter from a code block."""
    path, text = _read_main(root)
    old = "def numerical_gradient(f, x, eps=1e-5):"
    new = "def numerical_gradient(f, x):"
    _require_anchor(text, old)
    path.write_text(text.replace(old, new), encoding="utf-8")
    return "deleted the eps=1e-5 parameter from numerical_gradient"


DEFECTS: list[dict] = [
    {
        "defect_id": "D01",
        "category": "unique-detail-omission",
        "expected_detector": "marker-retention (rare terms)",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Rare Historical Note on Priority"),
        "mutate": _mut_unique_detail,
    },
    {
        "defect_id": "D02",
        "category": "equation-omission",
        "expected_detector": "marker-retention (equation fingerprint)",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Derivation Step by Step"),
        "mutate": _mut_equation_omission,
    },
    {
        "defect_id": "D03",
        "category": "derivation-step-omission",
        "expected_detector": "marker-retention (equation fingerprint)",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Derivation Step by Step"),
        "mutate": _mut_derivation_step,
    },
    {
        "defect_id": "D04",
        "category": "caveat-omission",
        "expected_detector": "marker-retention + prose-quality",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Project Caveats"),
        "mutate": _mut_caveat_omission,
    },
    {
        "defect_id": "D05",
        "category": "equation-sign-alteration",
        "expected_detector": "marker-retention (equation fingerprint)",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Derivation Step by Step"),
        "mutate": _mut_sign_alteration,
    },
    {
        "defect_id": "D06",
        "category": "obscure-concept-omission",
        "expected_detector": "marker-retention + destination-anchor",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VB", "Numerical Gradient Check"),
        "mutate": _mut_obscure_concept,
    },
    {
        "defect_id": "D07",
        "category": "link-break",
        "expected_detector": "link-integrity",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Reference Implementation"),
        "mutate": _mut_link_break,
    },
    {
        "defect_id": "D08",
        "category": "heading-convention-change",
        "expected_detector": "heading-convention + destination-anchor",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Version Distinction"),
        "mutate": _mut_heading_convention,
    },
    {
        "defect_id": "D09",
        "category": "prose-degradation",
        "expected_detector": "prose-quality + marker-retention",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Chain Rule Foundation"),
        "mutate": _mut_prose_degradation,
    },
    {
        "defect_id": "D10",
        "category": "version-distinction-loss",
        "expected_detector": "marker-retention (rare terms)",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Version Distinction"),
        "mutate": _mut_version_loss,
    },
    {
        "defect_id": "D11",
        "category": "accepted-output-drift",
        "expected_detector": "output-manifest regression",
        "regression": True,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VA", "Chain Rule Foundation"),
        "mutate": _mut_output_drift,
    },
    {
        "defect_id": "D12",
        "category": "code-parameter-deletion",
        "expected_detector": "marker-retention (code fingerprint)",
        "regression": False,
        "expected_note": MAIN_NOTE_RELPATH,
        "expected_ku": ("SRC-FIXTURE-VB", "Numerical Gradient Check"),
        "mutate": _mut_code_parameter,
    },
]

DEFECT_IDS = [d["defect_id"] for d in DEFECTS]


def apply_mutation(baseline_output_root: str | Path, mutated_output_root: str | Path, defect_id: str) -> str:
    """Copy the baseline output to *mutated_output_root* and plant one defect.

    Returns the human description of the applied change. Unknown defect ids
    raise ``ValueError``; the baseline tree is never touched.
    """
    defect = next((d for d in DEFECTS if d["defect_id"] == defect_id), None)
    if defect is None:
        raise ValueError(f"unknown defect id: {defect_id!r}")
    source = Path(baseline_output_root)
    dest = Path(mutated_output_root)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(source, dest)
    return defect["mutate"](dest)


# ---------------------------------------------------------------------------
# the reusable audit pipeline (this is what real synthesis batches must pass)
# ---------------------------------------------------------------------------

AUDIT_LIMITATIONS = [
    "term markers are frequency-based (rare in the source corpus): claims carried only by "
    "common vocabulary are not covered by term markers; equation/code fingerprints, "
    "destination anchors, link and lint checks provide the remaining nets",
    "no stemming and no grammar-level matching: legitimately reworded claims are caught only "
    "through shared distinctive vocabulary; semantic verification remains a separate, "
    "human/AI evidence class (VERIFICATION_SPECIFICATION.md section 5)",
    "equation matching compares normalized LaTeX source strings; mathematically equivalent "
    "reformatting (e.g. \\frac vs \\dfrac) counts as a different marker",
    "the heading-convention check detects mixed numbered/unnumbered schemes per note; it does "
    "not validate numbering sequences or cross-note ordering",
    "prose-quality is a word-count heuristic for bullet-only degradation; it cannot judge "
    "argument quality or depth",
    "drift detection requires an accepted manifest; pre-acceptance changes rely on the content "
    "checks above",
    "link findings attribute KU ownership by destination note plus wikilink presence in the "
    "excerpt, which is broader than the exact originating link",
]


class AuditError(Exception):
    """Raised for unusable audit inputs (missing roots, unreadable batches)."""


def _finding_key(finding: dict) -> tuple:
    """Stable identity used to diff findings between audit runs."""
    return (
        finding["check"],
        finding["category"],
        tuple(finding["ku_ids"]),
        finding["destination"]["path"],
        finding["destination"].get("heading"),
        finding["expected"],
    )


def audit_output(
    source_root: str | Path,
    output_root: str | Path,
    ku_batch_path: str | Path,
    *,
    accepted_manifest_path: str | Path | None = None,
    ku_schema_path: str | Path | None = None,
    rare_term_max_count: int = RARE_TERM_MAX_COUNT,
) -> dict:
    """Run the full omission/corruption audit pipeline over one output vault.

    Checks (in execution order):

    1. ``ku-batch``        - the KU batch validates against the schema and
                             cross-record rules (CAP-006/011 machinery);
    2. ``output-drift``    - output inventory vs the accepted manifest (when
                             given): added/removed/changed files;
    3. ``ku-accounting``   - no ``Unaccounted`` disposition; Preserved/
                             Consolidated/Contextualized units need destinations;
    4. ``destination``      - every destination file exists and every anchor
                             heading exists in that note;
    5. ``marker-retention``- rare-term, equation and code fingerprints of every
                             KU excerpt must be present in the output;
    6. ``link-integrity``  - wikilinks/embeds resolve (CAP-004);
    7. ``heading-convention`` - no mixed numbered/unnumbered heading schemes;
    8. ``prose-quality``  - sections receiving KU destinations are not
                             bullet-only.

    Findings carry stable KU IDs, destination locators, expected/observed
    evidence and a repair hint. ``valid`` is False when any critical or major
    finding exists; minor findings (warnings) do not block.
    """
    source_root = Path(source_root)
    output_root = Path(output_root)
    ku_batch_path = Path(ku_batch_path)
    if not source_root.is_dir():
        raise AuditError(f"source root is not a directory: {source_root}")
    if not output_root.is_dir():
        raise AuditError(f"output root is not a directory: {output_root}")
    if not ku_batch_path.is_file():
        raise AuditError(f"KU batch file not found: {ku_batch_path}")
    schema_path = Path(ku_schema_path) if ku_schema_path else DEFAULT_KU_SCHEMA

    findings: list[dict] = []
    stats: dict[str, object] = {}

    def _add(check, category, severity, ku_ids, destination, expected, observed, evidence=None, repair_hint=None):
        finding = {
            "finding_id": f"AF-{len(findings) + 1:03d}",
            "check": check,
            "category": category,
            "severity": severity,
            "ku_ids": sorted(set(ku_ids)),
            "destination": destination,
            "expected": expected,
            "observed": observed,
            "evidence": evidence or {},
            "repair_hint": repair_hint or "restore the missing/corrupted material at the destination",
        }
        findings.append(finding)
        return finding

    # ---- 1. KU batch validation ----
    batch_report = validate_ku_file(ku_batch_path, schema_path)
    records: list[dict] = []
    if not batch_report.get("valid"):
        for error in batch_report.get("errors", []):
            _add(
                "ku-batch",
                "ku-batch-invalid",
                "critical",
                [error.get("knowledge_unit_id")] if error.get("knowledge_unit_id") else [],
                {"path": str(ku_batch_path), "heading": None},
                "KU batch validates against the schema and cross-record rules",
                f"validation error: {error}",
                evidence={"error": error},
                repair_hint="fix the KU batch records before auditing output",
            )
    else:
        entries, _parse = load_jsonl_records(ku_batch_path)
        records = [entry["record"] for entry in entries]
    stats["kus_total"] = len(records)

    def _kus_for_note(relpath: str) -> list[str]:
        return [
            r["knowledge_unit_id"]
            for r in records
            if any(d.get("path") == relpath for d in r.get("destinations", []))
        ]

    # ---- 2. output drift vs accepted manifest ----
    scan = scan_root(output_root)
    current = {rec["relpath"]: rec.get("sha256") for rec in manifest_records(scan)}
    stats["output_files_total"] = len(current)
    if accepted_manifest_path is not None:
        accepted_path = Path(accepted_manifest_path)
        if not accepted_path.is_file():
            raise AuditError(f"accepted manifest not found: {accepted_path}")
        before = {rec["relpath"]: rec.get("sha256") for rec in load_manifest(accepted_path)}
        for relpath in sorted(set(before) - set(current)):
            _add(
                "output-drift",
                "accepted-file-removed",
                "critical",
                _kus_for_note(relpath),
                {"path": relpath, "heading": None},
                "accepted output file still present",
                "file missing from current output",
                evidence={"accepted_sha256": before[relpath]},
            )
        for relpath in sorted(set(current) - set(before)):
            _add(
                "output-drift",
                "unexpected-file-added",
                "minor",
                _kus_for_note(relpath),
                {"path": relpath, "heading": None},
                "no unaccounted additions to the accepted output",
                "file not present in the accepted manifest",
            )
        for relpath in sorted(set(before) & set(current)):
            if before[relpath] != current[relpath]:
                _add(
                    "output-drift",
                    "accepted-file-changed",
                    "critical",
                    _kus_for_note(relpath),
                    {"path": relpath, "heading": None},
                    "accepted output file unchanged after acceptance",
                    "content hash differs from the accepted manifest",
                    evidence={
                        "accepted_sha256": before[relpath],
                        "current_sha256": current[relpath],
                    },
                    repair_hint="re-audit the change through a bounded repair task or revert it",
                )

    if not records:
        stats["findings_total"] = len(findings)
        return _finish_audit(findings, stats, early=True)

    # ---- 3. KU accounting ----
    for record in records:
        ku = record["knowledge_unit_id"]
        disposition = record.get("disposition")
        if disposition == "Unaccounted":
            _add(
                "ku-accounting",
                "unaccounted-unit",
                "critical",
                [ku],
                record.get("destinations", [{}])[0] if record.get("destinations") else {"path": None, "heading": None},
                "every KU has a disposition and a defensible destination or documented state",
                "disposition is 'Unaccounted'",
                evidence={"source_path": record.get("source_path")},
                repair_hint="assign a disposition and destination (or 'Needs review' with a finding)",
            )
        if disposition in ("Preserved", "Consolidated", "Contextualized") and not record.get("destinations"):
            _add(
                "ku-accounting",
                "destination-missing",
                "major",
                [ku],
                {"path": None, "heading": None},
                f"{disposition} units carry at least one destination",
                "no destinations recorded",
                evidence={"source_path": record.get("source_path")},
            )

    # ---- 4. destination existence + anchor ----
    headings_by_file: dict[str, set[str]] = {}
    structures: dict[str, dict] = {}
    for relpath, abs_path in _iter_markdown_files(output_root):
        structure = extract_structure(abs_path)
        structures[relpath] = structure
        headings_by_file[relpath] = {h["text"] for h in structure["headings"]}
    for record in records:
        ku = record["knowledge_unit_id"]
        for dest in record.get("destinations", []):
            relpath = dest.get("path")
            if relpath not in headings_by_file:
                _add(
                    "destination",
                    "destination-file-missing",
                    "critical",
                    [ku],
                    dest,
                    "destination file exists in the output vault",
                    "file not found",
                    evidence={"source_path": record.get("source_path")},
                )
                continue
            heading = dest.get("heading")
            if heading and heading not in headings_by_file[relpath]:
                _add(
                    "destination",
                    "destination-heading-missing",
                    "major",
                    [ku],
                    dest,
                    "destination anchor heading exists in the destination note",
                    "heading not found in destination note",
                    evidence={
                        "source_path": record.get("source_path"),
                        "note_headings": sorted(headings_by_file[relpath]),
                    },
                    repair_hint="restore the heading or update the KU destination after review",
                )

    # ---- 5. marker retention ----
    source_texts = [
        abs_path.read_text(encoding="utf-8") for _, abs_path in _iter_markdown_files(source_root)
    ]
    freq = _term_frequency(source_texts)
    output_texts = {
        relpath: abs_path.read_text(encoding="utf-8")
        for relpath, abs_path in _iter_markdown_files(output_root)
    }
    normalized_corpus = unicodedata.normalize(
        "NFKC", "\n".join(output_texts.values())
    ).casefold()
    output_tokens = set(_term_tokens(normalized_corpus))
    output_math = set()
    output_code = set()
    for text in output_texts.values():
        output_math.update(_math_markers(text))
        output_code.update(_code_bodies(text))
    stats["markers"] = {"terms": 0, "math": 0, "code": 0, "missing_terms": 0, "missing_math": 0, "missing_code": 0}
    for record in records:
        ku = record["knowledge_unit_id"]
        excerpt = record.get("excerpt")
        destination = (record.get("destinations") or [{}])[0]
        destination = {"path": destination.get("path"), "heading": destination.get("heading")}
        if not excerpt:
            _add(
                "marker-retention",
                "no-markers-possible",
                "minor",
                [ku],
                destination,
                "KU excerpts carry extractable markers",
                "excerpt missing: no retention check was possible for this unit",
                evidence={"source_path": record.get("source_path")},
                repair_hint="extract an excerpt for this unit so retention can be checked",
            )
            continue
        markers = markers_for_record(record, freq, max_count=rare_term_max_count)
        stats["markers"]["terms"] += len(markers["terms"])
        stats["markers"]["math"] += len(markers["math"])
        stats["markers"]["code"] += len(markers["code"])
        for term in markers["terms"]:
            if not _term_present(term, output_tokens):
                stats["markers"]["missing_terms"] += 1
                _add(
                    "marker-retention",
                    "unique-detail-omission",
                    "major",
                    [ku],
                    destination,
                    f"rare source term '{term}' retained in the output",
                    "term not found anywhere in the output vault",
                    evidence={
                        "marker_type": "term",
                        "term": term,
                        "source_path": record.get("source_path"),
                        "source_lines": [record.get("line_start"), record.get("line_end")],
                    },
                )
        for math in markers["math"]:
            if math not in output_math:
                stats["markers"]["missing_math"] += 1
                _add(
                    "marker-retention",
                    "equation-omission",
                    "critical",
                    [ku],
                    destination,
                    "equation fingerprint retained verbatim in the output",
                    "equation not found (omitted or altered)",
                    evidence={
                        "marker_type": "math",
                        "math": math,
                        "source_path": record.get("source_path"),
                        "source_lines": [record.get("line_start"), record.get("line_end")],
                    },
                )
        for code in markers["code"]:
            if code not in output_code:
                stats["markers"]["missing_code"] += 1
                _add(
                    "marker-retention",
                    "code-omission",
                    "critical",
                    [ku],
                    destination,
                    "code block fingerprint retained in the output",
                    "code block not found (omitted or altered)",
                    evidence={
                        "marker_type": "code",
                        "code_head": code.splitlines()[0] if code else "",
                        "source_path": record.get("source_path"),
                        "source_lines": [record.get("line_start"), record.get("line_end")],
                    },
                )

    # ---- 6. link integrity ----
    link_report = check_links(output_root)
    for problem in link_report.get("problems", []):
        relpath = problem.get("file")
        if problem.get("type") == "broken":
            ku_ids = [
                r["knowledge_unit_id"]
                for r in records
                if any(d.get("path") == relpath for d in r.get("destinations", []))
                and "[[" in (r.get("excerpt") or "")
            ]
        else:
            ku_ids = _kus_for_note(relpath)
        _add(
            "link-integrity",
            f"link-{problem.get('type', 'problem')}",
            "major" if problem.get("type") == "broken" else "minor",
            ku_ids,
            {"path": relpath, "heading": None},
            "all output links resolve",
            f"link problem: {problem.get('type')} ({problem.get('target', problem.get('detail', ''))})",
            evidence={"line": problem.get("line"), "problem": problem},
        )
    stats["links_checked"] = link_report.get("checked_links", 0)
    stats["links_broken"] = len(
        [p for p in link_report.get("problems", []) if p.get("type") == "broken"]
    )

    # ---- 7. heading convention ----
    for relpath in sorted(structures):
        section_headings = [h for h in structures[relpath]["headings"] if h["level"] >= 2]
        if len(section_headings) < 2:
            continue
        numbered = [h for h in section_headings if _NUMBERED_HEADING_RE.match(h["text"])]
        unnumbered = [h for h in section_headings if not _NUMBERED_HEADING_RE.match(h["text"])]
        if numbered and unnumbered:
            for heading in unnumbered:
                ku_ids = [
                    r["knowledge_unit_id"]
                    for r in records
                    if any(
                        d.get("path") == relpath
                        and _heading_number_stripped(d.get("heading") or "") == _heading_number_stripped(heading["text"])
                        for d in r.get("destinations", [])
                    )
                ]
                _add(
                    "heading-convention",
                    "mixed-numbering-scheme",
                    "major",
                    ku_ids,
                    {"path": relpath, "heading": heading["text"]},
                    "one consistent heading-numbering scheme per note",
                    "unnumbered heading mixed into a numbered note",
                    evidence={"line": heading["line"]},
                    repair_hint="restore the heading numbering or adopt one scheme for the whole note",
                )

    # ---- 8. prose quality ----
    for relpath in sorted(output_texts):
        structure = structures.get(relpath)
        if structure is None:
            continue
        for heading_text, body_lines in _note_sections(output_texts[relpath], structure["headings"]):
            targeted = [
                r["knowledge_unit_id"]
                for r in records
                if any(
                    d.get("path") == relpath and d.get("heading") == heading_text
                    for d in r.get("destinations", [])
                )
            ]
            if not targeted:
                continue
            prose_words = _prose_word_count(body_lines)
            if prose_words < MIN_PROSE_WORDS:
                _add(
                    "prose-quality",
                    "prose-degradation",
                    "major",
                    targeted,
                    {"path": relpath, "heading": heading_text},
                    f"sections receiving KU destinations carry at least {MIN_PROSE_WORDS} prose words",
                    f"only {prose_words} prose words outside lists/code/math",
                    evidence={"prose_words": prose_words},
                    repair_hint="rewrite the section as full prose preserving the source knowledge",
                )

    return _finish_audit(findings, stats)


def _finish_audit(findings: list[dict], stats: dict, *, early: bool = False) -> dict:
    blocking = [f for f in findings if f["severity"] in ("critical", "major")]
    stats["findings_total"] = len(findings)
    stats["findings_blocking"] = len(blocking)
    stats["findings_by_severity"] = {
        severity: len([f for f in findings if f["severity"] == severity])
        for severity in ("critical", "major", "minor")
    }
    stats["findings_by_check"] = {}
    for finding in findings:
        stats["findings_by_check"][finding["check"]] = (
            stats["findings_by_check"].get(finding["check"], 0) + 1
        )
    return {
        "valid": not blocking,
        "checks_run": [] if early else [
            "ku-batch",
            "output-drift" ,
            "ku-accounting",
            "destination",
            "marker-retention",
            "link-integrity",
            "heading-convention",
            "prose-quality",
        ],
        "findings": findings,
        "stats": stats,
        "limitations": AUDIT_LIMITATIONS,
    }


# ---------------------------------------------------------------------------
# pilot orchestration
# ---------------------------------------------------------------------------

PILOT_LIMITATIONS = [
    "the fixture is deliberately small; corpus-scale marker noise and performance must be "
    "re-measured on real extraction batches (CAP-014 coverage reports)",
    "detection here proves the deterministic checks fire on the declared defect classes; it is "
    "not proof of semantic preservation (separate evidence class)",
    "reworded-but-preserved claims are not a defect class here; the auditor only guarantees "
    "fingerprint/vocabulary retention, and the fixture baseline models the editorial discipline "
    "of retaining distinctive vocabulary during consolidation",
    "the twelve defect categories cover the taxonomy of VERIFICATION_SPECIFICATION.md "
    "'Deliberate omission tests' plus section 6; new defect classes require new pilot entries",
]


def _resolve_expected_kus(records: list[dict], selector: tuple[str, str]) -> list[str]:
    source_id, heading_fragment = selector
    matched = [
        r["knowledge_unit_id"]
        for r in records
        if r.get("source_id") == source_id
        and any(
            heading_fragment in (d.get("heading") or "")
            for d in r.get("destinations", [])
        )
    ]
    if not matched:
        raise ValueError(f"pilot defect selector matched no KU: {selector!r}")
    return matched


def run_pilot(
    dest_root: str | Path,
    *,
    protected_roots: list | None = None,
    keep_mutations: bool = False,
    ku_schema_path: str | Path | None = None,
) -> dict:
    """Execute the omission-detection pilot and return its full report.

    Pass criteria (all must hold, AGENTS.md 7.5 / TOOLING_FRAMEWORK.md 9):
    1. the clean baseline audits with zero findings (no false positives);
    2. every planted defect is detected (new findings appear);
    3. every planted defect is localized to its expected KU and note;
    4. fixture sources are byte-identical before and after the run.
    """
    dest = Path(ensure_dest_safe(dest_root, protected_roots or []))
    fixture = build_fixture(dest, protected_roots=[])
    sources_root = Path(fixture["sources_root"])
    output_root = Path(fixture["output_root"])
    ku_batch_path = Path(fixture["ku_batch_path"])
    accepted_manifest_path = Path(fixture["accepted_manifest_path"])

    entries, _parse = load_jsonl_records(ku_batch_path)
    records = [entry["record"] for entry in entries]

    baseline_audit = audit_output(
        sources_root,
        output_root,
        ku_batch_path,
        accepted_manifest_path=accepted_manifest_path,
        ku_schema_path=ku_schema_path,
    )
    baseline_keys = {_finding_key(f) for f in baseline_audit["findings"]}
    false_positives = baseline_audit["findings"]

    results: list[dict] = []
    mutated_parent = dest / "mutated"
    for defect in DEFECTS:
        defect_result: dict = {
            "defect_id": defect["defect_id"],
            "category": defect["category"],
            "expected_detector": defect["expected_detector"],
            "regression_scenario": defect["regression"],
            "expected_note": defect["expected_note"],
            "applied_mutation": None,
            "audit_error": None,
            "detected": False,
            "localized_ku": False,
            "localized_note": False,
            "findings": [],
        }
        try:
            mutated_root = mutated_parent / defect["defect_id"] / "output"
            defect_result["applied_mutation"] = apply_mutation(
                output_root, mutated_root, defect["defect_id"]
            )
            audit = audit_output(
                sources_root,
                mutated_root,
                ku_batch_path,
                accepted_manifest_path=accepted_manifest_path if defect["regression"] else None,
                ku_schema_path=ku_schema_path,
            )
            new_findings = [f for f in audit["findings"] if _finding_key(f) not in baseline_keys]
            expected_kus = _resolve_expected_kus(records, defect["expected_ku"])
            defect_result["expected_ku_ids"] = expected_kus
            defect_result["detected"] = bool(new_findings)
            defect_result["localized_ku"] = any(
                set(f["ku_ids"]) & set(expected_kus) for f in new_findings
            )
            defect_result["localized_note"] = any(
                f["destination"]["path"] == defect["expected_note"] for f in new_findings
            )
            defect_result["findings"] = [
                {
                    "finding_id": f["finding_id"],
                    "check": f["check"],
                    "category": f["category"],
                    "severity": f["severity"],
                    "ku_ids": f["ku_ids"],
                    "destination": f["destination"],
                    "observed": f["observed"],
                }
                for f in new_findings
            ]
        except Exception as exc:  # auditor or mutator failure = honest miss
            defect_result["audit_error"] = f"{type(exc).__name__}: {exc}"
        results.append(defect_result)

    # fixture-source immutability inside the pilot run
    source_after = {
        "vault-a": _sha256_text((sources_root / "vault-a" / "backpropagation.md").read_text(encoding="utf-8")),
        "vault-b": _sha256_text((sources_root / "vault-b" / "backpropagation.md").read_text(encoding="utf-8")),
    }
    sources_unchanged = source_after == fixture["source_files"]

    if not keep_mutations and mutated_parent.exists():
        shutil.rmtree(mutated_parent)

    detected = [r["defect_id"] for r in results if r["detected"]]
    missed = [r["defect_id"] for r in results if not r["detected"]]
    not_localized = [
        r["defect_id"] for r in results if r["detected"] and not (r["localized_ku"] and r["localized_note"])
    ]
    failed_criteria = []
    if false_positives:
        failed_criteria.append(
            f"clean baseline produced {len(false_positives)} finding(s) (false positives)"
        )
    if missed:
        failed_criteria.append(f"defects not detected: {missed}")
    if not_localized:
        failed_criteria.append(f"defects detected without correct localization: {not_localized}")
    if not sources_unchanged:
        failed_criteria.append("fixture sources changed during the pilot")

    report = {
        "pilot_schema_version": "1.0",
        "fixture": {
            "sources_root": str(sources_root),
            "output_root": str(output_root),
            "ku_batch_path": str(ku_batch_path),
            "accepted_manifest_path": str(accepted_manifest_path),
            "ku_records": fixture["ku_records"],
            "ku_ids": fixture["ku_ids"],
            "output_files": fixture["output_files"],
            "source_files": fixture["source_files"],
            "defects_declared": len(DEFECTS),
        },
        "baseline_audit": {
            "finding_count": len(false_positives),
            "findings": [
                {k: f[k] for k in ("finding_id", "check", "category", "severity", "expected", "observed")}
                for f in false_positives
            ],
            "false_positive_count": len(false_positives),
        },
        "defect_results": results,
        "summary": {
            "defects_total": len(DEFECTS),
            "defects_detected": len(detected),
            "defects_missed": missed,
            "defects_not_localized": not_localized,
            "detection_rate": f"{len(detected)}/{len(DEFECTS)}",
            "localization_rate": f"{len(DEFECTS) - len(not_localized)}/{len(DEFECTS)}",
            "false_negatives": missed,
            "false_positives_on_clean_baseline": len(false_positives),
        },
        "source_immutability": {
            "sources_unchanged_during_pilot": sources_unchanged,
            "source_hashes_before": fixture["source_files"],
            "source_hashes_after": source_after,
        },
        "verdict": {
            "pass": not failed_criteria,
            "failed_criteria": failed_criteria,
        },
        "limitations": PILOT_LIMITATIONS,
    }
    return report

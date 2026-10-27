"""DISC-001 tests: emergent concept discovery + knowledge-gap detection.

Fixture scenarios mandated by docs/EMERGENT_CONCEPT_DISCOVERY.md (Acceptance
tests) and docs/PHASE_ZERO_REBASELINE_AND_FRAMEWORK_REFACTOR.md (Required
synthetic tests):

1.  concept used in several notes, never adequately defined -> detected +
    localized (chain rule, the canonical example);
2.  concept already explained well elsewhere -> NOT a false confirmed gap
    (softmax; status already_covered);
3.  fragmented derivation across notes -> connected evidence;
4.  rare but essential concept appearing once -> candidate without any
    frequency threshold (log-sum-exp trick);
5.  copied passages -> NOT independent recurrence (weight decay);
6.  homonyms in different contexts -> flagged, not merged (attention);
7.  contradictions -> surfaced, not silently resolved (bias init);
8.  unprocessed corpus region -> provisional, never confirmed (coverage gate,
    including refusal inside discovery-decide);
9.  merge / split decisions preserve provenance history;
10. section-vs-standalone destination recommendation;
11. deterministic repeat runs (byte-identical outputs);
12. precision/recall measured against the fixture label manifest.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import discovery as disc  # noqa: E402
from vault_unification.discovery import (  # noqa: E402
    apply_decisions,
    discover_candidates,
    validate_candidates,
)
from vault_unification.kuregistry import mint_ku_id  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
KUS_SCHEMA = REPO / "schemas" / "knowledge-unit.schema.json"
CAND_SCHEMA = REPO / "schemas" / "concept-candidate.schema.json"


def _ku(vault: str, path: str, text: str, *, unit_type: str = "prose",
        line_start: int = 1, heading: str | None = None) -> dict:
    """Build one schema-valid KU record with a content-derived stable id."""
    record = {
        "source_id": f"{vault}:{path}",
        "source_path": path,
        "source_file_hash": hashlib.sha256(f"{vault}:{path}".encode()).hexdigest(),
        "source_format": "markdown",
        "heading_path": [heading] if heading else [],
        "line_start": line_start,
        "line_end": line_start + len(text.splitlines()) - 1,
        "excerpt": text,
        "excerpt_hash": hashlib.sha256(text.encode()).hexdigest(),
        "unit_type": unit_type,
        "disposition": "Unaccounted",
        "verification_status": {
            "extraction": "machine-segmented",
            "accounting": "pending",
            "semantic": "pending",
            "technical": "pending",
            "editorial": "pending",
        },
    }
    record["knowledge_unit_id"] = mint_ku_id(record)
    return record


# ---------------------------------------------------------------------------
# the synthetic corpus (scenario -> files)

def build_corpus() -> list[dict]:
    """All fixture KUs. Every note is small and purpose-built for one scenario."""
    kus = [
        # --- 1. chain rule: used in 3 independent files, never defined ---
        _ku("notes", "backprop.md",
            "Recall the chain rule when computing gradients of the loss.",
            heading="Backpropagation"),
        _ku("notes", "cnn.md",
            "By the chain rule, dL/dw = dL/da * da/dw for each convolution weight.",
            heading="CNN gradients"),
        _ku("notes", "optim.md",
            "The Jacobian entries follow from the chain rule applied layerwise.",
            heading="Optimization"),
        # --- 2. softmax: defined well in a dedicated note, used elsewhere ---
        _ku("notes", "softmax-basics.md",
            "Softmax is a function that maps logits to a probability distribution.",
            heading="Softmax"),
        _ku("notes", "classifier.md",
            "The classifier head applies softmax to produce class probabilities.",
            heading="Classifier"),
        _ku("notes", "sampling.md",
            "Temperature scaling of softmax sharpens the output distribution.",
            heading="Sampling"),
        # --- 3. fragmented derivation: xavier initialization across 2 files ---
        _ku("notes", "init-part1.md",
            "For Xavier initialization the variance constraint starts the derivation:\n"
            "$$\n\\mathrm{Var}(W) = 2 / (n_{in} + n_{out})\n$$",
            heading="Init derivation part 1"),
        _ku("notes", "init-part2.md",
            "Substituting the Xavier initialization variance into the gradient scale\n"
            "therefore yields stable dL/da magnitudes.",
            heading="Init derivation part 2"),
        # --- 4. rare essential: log-sum-exp trick appears once ---
        _ku("notes", "stable-softmax.md",
            "Using the log-sum-exp trick stabilizes the softmax computation.",
            heading="Stable softmax"),
        # --- 5. copied passage: identical sentence (assumed position) x2 files ---
        _ku("notes", "reg-copy-a.md",
            "Recall the weight decay schedule from the previous run, the same sentence repeated."),
        _ku("notes", "reg-copy-b.md",
            "Recall the weight decay schedule from the previous run, the same sentence repeated."),
        # --- 6. homonym: attention (mechanism) vs attention (classroom) ---
        _ku("notes", "transformer.md",
            "The attention mechanism computes softmax over query and key products.",
            heading="Transformer"),
        _ku("notes", "study-tips.md",
            "Students pay attention during the lecture to pass the exam.",
            heading="Study tips"),
        # --- 7. contradiction: bias init numbers differ across definitions ---
        _ku("notes", "bias-def-a.md",
            "The default bias initialization is 0.",
            heading="Bias init A"),
        _ku("notes", "bias-def-b.md",
            "The default bias initialization is drawn from U(-1/sqrt(fan_in), 1/sqrt(fan_in)).",
            heading="Bias init B"),
        # --- 10. section-vs-note: two plain usages, no definition ---
        _ku("notes", "training-run.md",
            "We applied early stopping after five stagnant epochs.",
            heading="Training run"),
        _ku("notes", "eval-run.md",
            "The team mentions early stopping in every evaluation meeting.",
            heading="Eval run"),
    ]
    return kus


def write_batch(tmp_path: Path, records: list[dict], name: str = "batch.jsonl") -> Path:
    path = tmp_path / name
    with open(path, "w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    return path


def write_manifest(tmp_path: Path, vault: str, files: list[str],
                   name: str = "manifest.jsonl") -> Path:
    path = tmp_path / name
    with open(path, "w", encoding="utf-8") as handle:
        for f in files:
            handle.write(json.dumps({"relpath": f, "size": 1, "sha256": "x" * 64}) + "\n")
    return path


ALL_FILES = sorted({ku["source_path"] for ku in build_corpus()})


@pytest.fixture()
def corpus_env(tmp_path: Path) -> dict:
    """Full-coverage environment: every corpus file declared in the manifest."""
    batch = write_batch(tmp_path, build_corpus())
    manifest = write_manifest(tmp_path, "notes", ALL_FILES)
    return {"batch": batch, "manifest": manifest, "manifests": {"notes": manifest}}


@pytest.fixture()
def partial_env(tmp_path: Path) -> dict:
    """Partial-coverage environment: one file deliberately unprocessed."""
    batch = write_batch(tmp_path, build_corpus())
    partial_files = [f for f in ALL_FILES if f != "study-tips.md"]
    manifest = write_manifest(tmp_path, "notes", partial_files, name="partial.jsonl")
    return {"batch": batch, "manifest": manifest, "manifests": {"notes": manifest}}


def run(env: dict) -> dict:
    return discover_candidates([env["batch"]], KUS_SCHEMA, env["manifests"])


def by_term(result: dict) -> dict[str, dict]:
    return {c["term"]: c for c in result["candidates"]}


# ---------------------------------------------------------------------------
# fixture label manifest (scenario 12: precision/recall)

LABELS = {
    # term -> (kind, status)
    "chain rule": ("unexplained_prerequisite", "provisional_candidate"),
    "softmax": ("concept_sighting", "already_covered"),
    "xavier initialization": ("fragmented_derivation", "provisional_candidate"),
    "log-sum-exp trick": ("rare_essential", "provisional_candidate"),
    "attention": ("unexplained_prerequisite", "provisional_candidate"),
    "early stopping": ("unexplained_prerequisite", "provisional_candidate"),
}


class TestCoreScenarios:
    def test_chain_rule_detected_as_unexplained_prerequisite(self, corpus_env):
        result = run(corpus_env)
        cand = by_term(result)["chain rule"]
        assert cand["kind"] == "unexplained_prerequisite"
        assert cand["status"] == "provisional_candidate"
        assert cand["independent_contexts"] == 3
        assert cand["definition_evidence"] == []
        assert cand["destination_recommendation"] == "standalone_note_candidate"
        # localization: 3 distinct source files, exact line numbers
        files = sorted({e["source_path"] for e in cand["evidence"]})
        assert files == ["backprop.md", "cnn.md", "optim.md"]
        for ev in cand["evidence"]:
            assert ev["line_start"] >= 1 and ev["line_end"] >= ev["line_start"]
            assert "chain rule" in ev["quote"].casefold()

    def test_explained_elsewhere_is_not_a_gap(self, corpus_env):
        """Fixture 5/1: no false confirmed gap for a concept defined elsewhere."""
        result = run(corpus_env)
        cand = by_term(result)["softmax"]
        assert cand["status"] == "already_covered"
        assert cand["kind"] == "concept_sighting"
        assert cand["destination_recommendation"] == "no_gap"
        assert len(cand["definition_evidence"]) >= 1
        # and it must never be a provisional/confirmed gap
        assert "provisional_candidate" != cand["status"]
        assert "confirmed_gap" != cand["status"]

    def test_fragmented_derivation_connected(self, corpus_env):
        result = run(corpus_env)
        cand = by_term(result)["xavier initialization"]
        assert cand["kind"] == "fragmented_derivation"
        files = {e["source_path"] for e in cand["evidence"]}
        assert files == {"init-part1.md", "init-part2.md"}
        derivation_usages = cand["confidence"]["signals"]["derivation_usages"]
        assert derivation_usages >= 2

    def test_rare_essential_single_occurrence_no_frequency_threshold(self, corpus_env):
        result = run(corpus_env)
        cand = by_term(result)["log-sum-exp trick"]
        assert cand["kind"] == "rare_essential"
        assert cand["independent_contexts"] == 1
        assert cand["destination_recommendation"] == "section_candidate"

    def test_copied_passages_not_independent(self, corpus_env):
        """Fixture 5: a repeated passage across two files counts ONCE."""
        result = run(corpus_env)
        cands = by_term(result)
        # the term appears in both copied files with identical passage text:
        # collapsed to ONE independent context -> rare_essential, never a
        # multi-context prerequisite
        cand = cands.get("weight decay")
        assert cand is not None, "copied-passage term must still be a candidate"
        assert cand["independent_contexts"] == 1
        assert cand["copied_passage"] is True
        assert cand["kind"] == "rare_essential"

    def test_homonym_flagged_not_merged(self, corpus_env):
        result = run(corpus_env)
        cand = by_term(result)["attention"]
        assert cand["homonym_suspect"] is True
        assert len(cand["homonym_clusters"]) == 2
        cluster_files = [sorted(c["context_files"]) for c in cand["homonym_clusters"]]
        assert ["transformer.md"] in cluster_files
        assert ["study-tips.md"] in cluster_files
        # signatures must be disjoint
        sigs = [set(c["signature_terms"]) for c in cand["homonym_clusters"]]
        assert not (sigs[0] & sigs[1])

    def test_contradiction_surfaced_not_resolved(self, corpus_env):
        result = run(corpus_env)
        cand = by_term(result)["bias initialization"]
        assert cand["contradiction_suspect"] is True
        assert cand["contradictions"], "expected at least one contradiction pair"
        pair = cand["contradictions"][0]
        assert {pair["a_ku_id"], pair["b_ku_id"]} == {
            e["ku_id"] for e in cand["definition_evidence"]
        }

    def test_section_vs_standalone_recommendation(self, corpus_env):
        result = run(corpus_env)
        cand = by_term(result)["early stopping"]
        assert cand["kind"] == "unexplained_prerequisite"
        assert cand["independent_contexts"] == 2
        assert cand["destination_recommendation"] == "section_candidate"


class TestCoverageGate:
    """Fixture 9: unprocessed regions can never yield confirmed gaps."""

    def test_partial_coverage_keeps_everything_provisional(self, partial_env):
        result = run(partial_env)
        assert result["report"]["coverage"]["coverage_complete"] is False
        statuses = {c["status"] for c in result["candidates"]}
        assert "confirmed_gap" not in statuses
        gap = [c for c in result["candidates"] if c["kind"] != "concept_sighting"]
        assert gap, "gap candidates exist"
        assert all(c["status"] == "provisional_candidate" for c in gap)
        assert all(c["coverage"]["coverage_complete"] is False for c in gap)

    def test_full_coverage_still_provisional_pending_review(self, corpus_env):
        # deterministic tool never confirms by itself; review confirms
        result = run(corpus_env)
        statuses = {c["status"] for c in result["candidates"]}
        assert statuses <= {"provisional_candidate", "already_covered"}

    def test_discovery_decide_refuses_confirm_gap_under_partial_coverage(
        self, partial_env, tmp_path
    ):
        result = run(partial_env)
        cands_path = write_batch(tmp_path, result["candidates"], name="cands.jsonl")
        target = next(
            c for c in result["candidates"] if c["status"] == "provisional_candidate"
        )
        decisions = tmp_path / "dec.jsonl"
        decisions.write_text(
            json.dumps({
                "candidate_id": target["candidate_id"],
                "decision_id": "D-001",
                "action": "confirm_gap",
                "rationale": "should be REFUSED: coverage incomplete",
                "reviewer": "test",
            }) + "\n",
            encoding="utf-8",
        )
        outcome = apply_decisions(
            cands_path, decisions, CAND_SCHEMA, decided_utc="2026-10-27T00:00:00+00:00"
        )
        assert outcome["ok"] is False
        assert any("REFUSED confirm_gap" in e for e in outcome["errors"])
        # the candidate status must be untouched
        unchanged = next(
            r for r in outcome["records"] if r["candidate_id"] == target["candidate_id"]
        )
        assert unchanged["status"] == "provisional_candidate"

    def test_confirm_gap_allowed_at_full_coverage(self, corpus_env, tmp_path):
        result = run(corpus_env)
        cands_path = write_batch(tmp_path, result["candidates"], name="cands.jsonl")
        target = by_term(result)["chain rule"]
        decisions = tmp_path / "dec.jsonl"
        decisions.write_text(
            json.dumps({
                "candidate_id": target["candidate_id"],
                "decision_id": "D-001",
                "action": "confirm_gap",
                "rationale": "corpus fully processed; no definition exists",
                "reviewer": "review-agent",
            }) + "\n",
            encoding="utf-8",
        )
        outcome = apply_decisions(
            cands_path, decisions, CAND_SCHEMA, decided_utc="2026-10-27T00:00:00+00:00"
        )
        assert outcome["ok"] is True, outcome["errors"]
        confirmed = next(
            r for r in outcome["records"] if r["candidate_id"] == target["candidate_id"]
        )
        assert confirmed["status"] == "confirmed_gap"
        assert confirmed["decision_history"][-1]["reviewer"] == "review-agent"


class TestDecisionsAndHistory:
    def test_merge_preserves_provenance_both_sides(self, corpus_env, tmp_path):
        result = run(corpus_env)
        cands_path = write_batch(tmp_path, result["candidates"], name="cands.jsonl")
        # merge the copied-passage candidate into the chain-rule candidate
        source = by_term(result)["weight decay"]
        target = by_term(result)["chain rule"]
        decisions = tmp_path / "dec.jsonl"
        decisions.write_text(
            json.dumps({
                "candidate_id": source["candidate_id"],
                "decision_id": "D-010",
                "action": "merge",
                "rationale": "both are regularization-adjacent gaps; unify",
                "reviewer": "review-agent",
                "merge_into": target["candidate_id"],
            }) + "\n",
            encoding="utf-8",
        )
        outcome = apply_decisions(
            cands_path, decisions, CAND_SCHEMA, decided_utc="2026-10-27T01:00:00+00:00"
        )
        assert outcome["ok"] is True, outcome["errors"]
        merged = next(
            r for r in outcome["records"] if r["candidate_id"] == source["candidate_id"]
        )
        absorbed = next(
            r for r in outcome["records"] if r["candidate_id"] == target["candidate_id"]
        )
        assert merged["status"] == "merged"
        assert merged["decision_history"][-1]["merge_into"] == target["candidate_id"]
        # original evidence preserved on the merged record
        assert merged["evidence"], "provenance preserved on merged record"
        # reverse provenance note on the target
        assert any(
            h["action"] == "merge" and "absorbed" in h["rationale"]
            for h in absorbed["decision_history"]
        )

    def test_split_with_new_candidates_preserves_history(self, corpus_env, tmp_path):
        result = run(corpus_env)
        cands_path = write_batch(tmp_path, result["candidates"], name="cands.jsonl")
        homonym = by_term(result)["attention"]
        # reviewer splits the homonym into two sense-specific candidates
        new_a = json.loads(json.dumps(homonym))
        new_a.update({
            "candidate_id": "CG-aaaaaa000001",
            "term": "attention (mechanism sense)",
            "proposed_title": "Attention (Mechanism Sense)",
            "decision_history": [],
        })
        new_b = json.loads(json.dumps(homonym))
        new_b.update({
            "candidate_id": "CG-aaaaaa000002",
            "term": "attention (classroom sense)",
            "proposed_title": "Attention (Classroom Sense)",
            "decision_history": [],
        })
        decisions = tmp_path / "dec.jsonl"
        decisions.write_text(
            json.dumps({
                "candidate_id": homonym["candidate_id"],
                "decision_id": "D-020",
                "action": "split",
                "rationale": "homonym confirmed; two distinct concepts",
                "reviewer": "review-agent",
                "split_into": [new_a["candidate_id"], new_b["candidate_id"]],
                "new_candidates": [new_a, new_b],
            }) + "\n",
            encoding="utf-8",
        )
        outcome = apply_decisions(
            cands_path, decisions, CAND_SCHEMA, decided_utc="2026-10-27T02:00:00+00:00"
        )
        assert outcome["ok"] is True, outcome["errors"]
        split_rec = next(
            r for r in outcome["records"] if r["candidate_id"] == homonym["candidate_id"]
        )
        assert split_rec["status"] == "split"
        assert split_rec["decision_history"][-1]["split_into"] == [
            "CG-aaaaaa000001", "CG-aaaaaa000002"
        ]
        ids = {r["candidate_id"] for r in outcome["records"]}
        assert {"CG-aaaaaa000001", "CG-aaaaaa000002"} <= ids
        # new records carry their own (empty) history and valid schema shape
        na = next(r for r in outcome["records"] if r["candidate_id"] == "CG-aaaaaa000001")
        assert na["decision_history"] == []

    def test_reject_and_defer_and_accept_transitions(self, corpus_env, tmp_path):
        result = run(corpus_env)
        cands_path = write_batch(tmp_path, result["candidates"], name="cands.jsonl")
        terms = by_term(result)
        decisions = tmp_path / "dec.jsonl"
        rows = [
            {"candidate_id": terms["early stopping"]["candidate_id"],
             "decision_id": "D-030", "action": "reject",
             "rationale": "too generic; not a concept", "reviewer": "r"},
            {"candidate_id": terms["log-sum-exp trick"]["candidate_id"],
             "decision_id": "D-031", "action": "defer",
             "rationale": "wait for the numerics domain batch", "reviewer": "r"},
            {"candidate_id": terms["xavier initialization"]["candidate_id"],
             "decision_id": "D-032", "action": "accept",
             "rationale": "genuine fragmented derivation; add to dossier plan",
             "reviewer": "r"},
        ]
        decisions.write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
        )
        outcome = apply_decisions(
            cands_path, decisions, CAND_SCHEMA, decided_utc="2026-10-27T03:00:00+00:00"
        )
        assert outcome["ok"] is True, outcome["errors"]
        by_id = {r["candidate_id"]: r for r in outcome["records"]}
        assert by_id[terms["early stopping"]["candidate_id"]]["status"] == "rejected"
        assert by_id[terms["log-sum-exp trick"]["candidate_id"]]["status"] == "deferred"
        assert by_id[terms["xavier initialization"]["candidate_id"]]["status"] == "accepted"

    def test_invalid_transition_rejected(self, corpus_env, tmp_path):
        result = run(corpus_env)
        cands_path = write_batch(tmp_path, result["candidates"], name="cands.jsonl")
        covered = by_term(result)["softmax"]  # already_covered
        decisions = tmp_path / "dec.jsonl"
        decisions.write_text(
            json.dumps({
                "candidate_id": covered["candidate_id"],
                "decision_id": "D-040",
                "action": "accept",
                "rationale": "illegal from already_covered",
                "reviewer": "r",
            }) + "\n",
            encoding="utf-8",
        )
        outcome = apply_decisions(
            cands_path, decisions, CAND_SCHEMA, decided_utc="2026-10-27T04:00:00+00:00"
        )
        assert outcome["ok"] is False
        assert any("not allowed" in e for e in outcome["errors"])


class TestDeterminismAndValidation:
    def test_identical_inputs_produce_byte_identical_output(self, corpus_env, tmp_path):
        r1 = run(corpus_env)
        r2 = run(corpus_env)
        b1 = "".join(
            json.dumps(c, sort_keys=True, ensure_ascii=False) + "\n"
            for c in r1["candidates"]
        )
        b2 = "".join(
            json.dumps(c, sort_keys=True, ensure_ascii=False) + "\n"
            for c in r2["candidates"]
        )
        assert b1 == b2
        # stable content-derived ids
        assert {c["candidate_id"] for c in r1["candidates"]} == {
            c["candidate_id"] for c in r2["candidates"]
        }

    def test_candidates_schema_valid_and_cross_checked(self, corpus_env, tmp_path):
        result = run(corpus_env)
        cands_path = write_batch(tmp_path, result["candidates"], name="cands.jsonl")
        v = validate_candidates(
            cands_path, CAND_SCHEMA, ku_batches=[corpus_env["batch"]], kus_schema=KUS_SCHEMA
        )
        assert v["valid"] is True, v["errors"]
        assert v["records_total"] == len(result["candidates"])

    def test_validate_catches_confirmed_gap_under_incomplete_coverage(
        self, partial_env, tmp_path
    ):
        # forge an illegal record: provisional + coverage_complete forced false
        result = run(partial_env)
        forged = json.loads(json.dumps(result["candidates"]))
        target = next(c for c in forged if c["status"] == "provisional_candidate")
        target["status"] = "confirmed_gap"
        cands_path = write_batch(tmp_path, forged, name="forged.jsonl")
        v = validate_candidates(
            cands_path, CAND_SCHEMA, ku_batches=[partial_env["batch"]], kus_schema=KUS_SCHEMA
        )
        assert v["valid"] is False
        assert any("confirmed_gap" in e for e in v["errors"])

    def test_validate_catches_unknown_evidence_ku(self, corpus_env, tmp_path):
        result = run(corpus_env)
        forged = json.loads(json.dumps(result["candidates"]))
        forged[0]["evidence"][0]["ku_id"] = "KU-doesnotexist"
        cands_path = write_batch(tmp_path, forged, name="forged2.jsonl")
        v = validate_candidates(
            cands_path, CAND_SCHEMA, ku_batches=[corpus_env["batch"]], kus_schema=KUS_SCHEMA
        )
        assert v["valid"] is False
        assert any("not found in provided batches" in e for e in v["errors"])


class TestPrecisionRecall:
    """Scenario 12: measured against the fixture label manifest."""

    def test_recall_and_precision_against_labels(self, corpus_env):
        result = run(corpus_env)
        cands = by_term(result)
        found = 0
        for term, (kind, status) in LABELS.items():
            if term in cands and cands[term]["kind"] == kind and cands[term]["status"] == status:
                found += 1
        recall = found / len(LABELS)
        assert recall == 1.0, (
            f"recall {recall:.2f}; missing: "
            f"{[t for t in LABELS if t not in cands or (cands[t]['kind'], cands[t]['status']) != LABELS[t]]}"
        )
        # false positives: labeled-covered terms must NEVER be gap candidates
        covered_labels = [t for t, (k, s) in LABELS.items() if s == "already_covered"]
        false_positives = [
            t for t in covered_labels
            if t in cands and cands[t]["status"] in ("provisional_candidate", "confirmed_gap")
        ]
        assert false_positives == []
        # report the full emission inventory for transparency
        print(f"\nfixture emissions: {len(result['candidates'])} candidates")
        print("by kind:", result["report"]["candidates_by_kind"])


class TestNegativePaths:
    def test_undeclared_vault_rejected(self, tmp_path):
        batch = write_batch(tmp_path, build_corpus())
        manifest = write_manifest(tmp_path, "other-vault", ALL_FILES)
        with pytest.raises(disc.DiscoveryError, match="not declared"):
            discover_candidates([batch], KUS_SCHEMA, {"other-vault": manifest})

    def test_missing_manifest_rejected(self, tmp_path):
        batch = write_batch(tmp_path, build_corpus())
        with pytest.raises(disc.DiscoveryError, match="cannot read manifest"):
            discover_candidates([batch], KUS_SCHEMA, {"notes": tmp_path / "nope.jsonl"})

    def test_empty_batch_rejected(self, tmp_path):
        empty = write_batch(tmp_path, [], name="empty.jsonl")
        manifest = write_manifest(tmp_path, "notes", ALL_FILES)
        from vault_unification.overlap import OverlapError
        with pytest.raises(OverlapError, match="no records"):
            discover_candidates([empty], KUS_SCHEMA, {"notes": manifest})

    def test_duplicate_ku_ids_rejected(self, tmp_path):
        kus = build_corpus()
        dup = write_batch(tmp_path, kus + [kus[0]], name="dup.jsonl")
        manifest = write_manifest(tmp_path, "notes", ALL_FILES)
        from vault_unification.overlap import OverlapError
        with pytest.raises(OverlapError, match="duplicate knowledge_unit_id"):
            discover_candidates([dup], KUS_SCHEMA, {"notes": manifest})


class TestOptimizationEquivalence:
    """DISC-002 performance hardening: the optimized helpers must return
    EXACTLY what the reference implementations return (the full-corpus run
    relies on them; byte-identical output was additionally verified on the
    real 14-batch subset, sha256 1322e74c...)."""

    REL_TEXTS = [
        "the chain rule is a fundamental result of differential calculus",
        "chain rule is defined as the composition of derivatives",
        "softmax refers to a normalized exponential distribution",
        "recall that the chain rule gives us dL/dx through dz",
        "using the chain rule we obtain the gradient of the loss",
        "by the fundamental theorem of calculus the integral evaluates",
        "we derive: substitute the expression, therefore the loss follows",
        "the optimizer applies gradient clipping during training",
        "the loss is 0.5 times the squared error term",
        "attention: a mechanism that weighs inputs",
        "called residual connections, these shortcuts help",
        "define dropout as randomly zeroing units",
        "the learning rate :",
        "adam is an adaptive optimizer variant",
        "output",
        "",
    ]

    @pytest.mark.parametrize("term", ["chain rule", "softmax", "attention", "adam", "loss", "dropout"])
    @pytest.mark.parametrize("heading_declared", [False, True])
    def test_compiled_relationship_matches_reference(
        self, term, heading_declared
    ):
        from vault_unification.locators import _normalize

        def_pattern, assumed_pattern = disc._compile_relationship_patterns(term)
        for text in self.REL_TEXTS:
            norm = _normalize(text)
            expected = disc._match_relationship(term, norm, heading_declared)
            got = disc._match_relationship_compiled(
                def_pattern,
                assumed_pattern,
                norm,
                heading_declared,
                bool(disc._DERIVATION_MARKERS.search(norm)),
            )
            assert got == expected, (term, heading_declared, text, got, expected)

    def test_prepared_ku_first_offsets_equal_excerpt_find(self):
        excerpt = "alpha line\n\nbeta line\nalpha line\n\ngamma tail"
        ku = {"excerpt": excerpt, "heading_path": ["Head A", "Head B"], "line_start": 7}
        prep = disc._prepare_ku(ku)
        lines = excerpt.splitlines()
        assert prep["lines"] == lines
        for i, line in enumerate(lines):
            assert prep["first_offsets"][i] == (excerpt.find(line) if line else 0)
        # normalized excerpt is the normalize() of the whole excerpt
        from vault_unification.locators import _normalize
        assert prep["norm_excerpt"] == _normalize(excerpt)
        # heading normalization identical to the reference expression
        assert prep["norm_headings"] == [
            _normalize(h) if h else h for h in ku["heading_path"]
        ]

    def test_locate_with_precomputed_matches_reference(self):
        excerpt = "The chain rule appears here.\nSecond line mentions softmax.\n\nchain rule again"
        ku = {"excerpt": excerpt, "heading_path": [], "line_start": 3}
        pattern = disc.boundary_pattern("chain rule")
        prep = disc._prepare_ku(ku)
        for term in ["chain rule", "softmax", "second line", "missing term"]:
            expected = disc._locate_in_ku(dict(ku), term)
            got = disc._locate_in_ku(
                dict(ku), term, pattern=disc.boundary_pattern(term), prepared=prep
            )
            assert got == expected, (term, got, expected)

    def test_signature_from_ranking_matches_reference(self):
        ku = {
            "excerpt": (
                "gradient descent minimizes the loss. gradient descent uses "
                "learning rates; the loss surface and gradient descent "
                "converge under conditions on the learning rate and loss."
            ),
            "heading_path": [],
        }
        ranking = disc._gram_ranking(ku)
        for term in ["gradient descent", "loss", "learning rate", "conditions", "zzz"]:
            expected = disc._signature_terms(term, ku)
            got = disc._signature_from_ranking(ranking, term)
            assert got == expected, (term, got, expected)

    def test_cluster_contexts_merges_intersecting_signatures(self):
        ctx = [
            {"vault": "a", "source_path": "p1", "signature": ["x", "y"]},
            {"vault": "a", "source_path": "p2", "signature": ["y", "z"]},
            {"vault": "a", "source_path": "p3", "signature": ["q", "r"]},
            {"vault": "a", "source_path": "p4", "signature": []},
        ]
        clusters = disc._cluster_contexts(ctx)
        # p1 and p2 merge (shared "y"); p3 and p4 stay separate
        members = [sorted(c["source_path"] for c in cl) for cl in clusters]
        assert ["p1", "p2"] in members
        assert ["p3"] in members
        assert ["p4"] in members

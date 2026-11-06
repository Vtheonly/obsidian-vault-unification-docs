"""Unit/integration tests for the integration-campaign machinery (INTEG-001;
sessions 31-45; docs/INTEGRATION_CAMPAIGN_PLAN.md)."""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import integration as ig  # noqa: E402
from vault_unification import cli  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]

# A miniature taxonomy exercising every documented parse rule: two project
# clusters with Repository:/context lines, sections/subsections, bullet items
# (incl. an alias form and a British-spelling duplicate of an American item),
# a carrier line, a group label, the transcript-noise block, the restarted
# second-half numbering, a Medical NLP cluster and a master index with
# tab-separated table rows.
MINI_TAXONOMY = """\
Understood. You want a complete AI concept taxonomy.
1. SynPath — Protein-Based Molecular Generation
Repository: 3d-syntree / 3d-synV2
1.1 Geometric Deep Learning
- Geometric Deep Learning
- Message Passing Neural Networks
- Colour Histogram Normalisation
1.2 Attention Mechanisms
- Scaled Dot-Product Attention
- Long Short-Term Memory (LSTM)
- Output Projection (\\(W^O\\))
Some free-text annotation constraining later integration.
2. Medical NLP — Unified Medical Knowledge Architecture
Open Medical-NLP-Reconstructed · Master Index
Named medical vocabularies and databases:
- ICD-10
- SNOMED CT
Drugs: Aspirin, Metformin
3. Consolidated master index
This is the list of the principal AI fields, without repeating every sub-concept.
#\tMain AI field\tPrincipal concepts
1\tGeometric Deep Learning\tGNNs, Message Passing Neural Networks
2\tAttention Mechanisms\tLSTM
TAHT ISNTA some transcript noise line
status: uploading...
url: https://example.invalid/progress
You're right. I missed two major project folders. Here are the named concepts.
4. 2D3D — Computer Vision and 3D Reconstruction
1.1 Feature Extraction
- SIFT
- Colour Histogram Normalisation
- Gaussian Basis Functions (RBF)
"""


def write_taxonomy(tmp_path: Path, text: str = MINI_TAXONOMY) -> Path:
    p = tmp_path / "taxonomy.txt"
    p.write_text(text, encoding="utf-8")
    return p


def vault_note(vault: Path, rel: str, text: str) -> Path:
    p = vault / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def dir_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(root)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


# ---------------------------------------------------------------------------
# parse_integration_list


class TestParseIntegrationList:
    def test_mini_taxonomy_structure(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        assert [c["cluster_id"] for c in inv["clusters"]] == [
            "SYNPATH",
            "MEDNLP",
            "MASTER-INDEX",
            "2D3D",
        ]
        assert inv["clusters"][0]["repository"] == "3d-syntree / 3d-synV2"
        # noise block located
        assert inv["noise_block"]["start_line"] == 24
        assert inv["noise_block"]["end_line"] == 27

    def test_items_dedupe_across_clusters_and_spelling(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        names = {i["name"] for i in inv["items"]}
        # British/American spelling folds onto one item, first occurrence wins
        assert "Colour Histogram Normalisation" in names
        assert "Color Histogram Normalization" not in names
        dupes = [i for i in inv["items"] if i["name"] == "Colour Histogram Normalisation"]
        assert len(dupes) == 1
        assert set(dupes[0]["clusters"]) == {"SYNPATH", "2D3D"}
        assert len(dupes[0]["occurrences"]) == 2

    def test_alias_splitting_plain_and_latex(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        by_name = {i["name"]: i for i in inv["items"]}
        assert by_name["Long Short-Term Memory"]["alias"] == "LSTM"
        assert by_name["Output Projection"]["alias"] == "W^O"

    def test_carrier_line_typed_entities(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        by_name = {i["name"]: i for i in inv["items"]}
        assert "Aspirin" in by_name
        assert by_name["Aspirin"].get("entity_types") == ["drugs"]
        assert by_name["Metformin"].get("entity_types") == ["drugs"]

    def test_group_label_attached(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        by_name = {i["name"]: i for i in inv["items"]}
        assert by_name["ICD-10"]["group_labels"] == [
            "Named medical vocabularies and databases"
        ]

    def test_master_index_rows_and_principal_refs(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        by_name = {i["name"]: i for i in inv["items"]}
        # the field column creates the item; principal concepts resolve to
        # existing item ids where a surface form matches, never create items
        gdl = by_name["Geometric Deep Learning"]
        assert {"SYNPATH", "MASTER-INDEX"} <= set(gdl["clusters"])
        refs = {r["concept"]: r["item_id"] for r in gdl["principal_refs"]}
        assert refs["Message Passing Neural Networks"] == by_name[
            "Message Passing Neural Networks"
        ]["item_id"]
        # LSTM resolves through the alias
        att = by_name["Attention Mechanisms"]
        att_refs = {r["concept"]: r["item_id"] for r in att["principal_refs"]}
        assert att_refs["LSTM"] == by_name["Long Short-Term Memory"]["item_id"]

    def test_noise_block_excluded_with_reasons(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        reasons = {e["reason"] for e in inv["excluded_lines"]}
        assert "transcript-noise-block" in reasons
        assert "context-before-any-cluster" in reasons
        noise_lines = [e for e in inv["excluded_lines"] if e["reason"] == "transcript-noise-block"]
        assert len(noise_lines) == 4  # lines 25-28 inclusive
        # noise-block content never becomes items
        names = {i["name"] for i in inv["items"]}
        assert "some transcript noise line" not in names
        assert "status: uploading..." not in names

    def test_context_records_retained(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        synpath = inv["clusters"][0]
        texts = [c["text"] for c in synpath["context"]]
        assert any(t.startswith("Repository:") for t in texts)
        assert any("free-text annotation" in t for t in texts)

    def test_determinism_same_input_same_output(self, tmp_path):
        p = write_taxonomy(tmp_path)
        inv1 = ig.parse_integration_list(p)
        inv2 = ig.parse_integration_list(p)
        assert inv1["parse_stats"] == inv2["parse_stats"]
        assert inv1["items"] == inv2["items"]
        assert inv1["clusters"] == inv2["clusters"]
        assert inv1["source_sha256"] == inv2["source_sha256"]

    def test_item_ids_first_occurrence_order(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        ids = [i["item_id"] for i in inv["items"]]
        assert ids == [f"INT-{n:04d}" for n in range(1, len(ids) + 1)]
        assert inv["items"][0]["name"] == "Geometric Deep Learning"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(ig.IntegrationError):
            ig.parse_integration_list(tmp_path / "nope.txt")

    def test_empty_file_raises(self, tmp_path):
        p = tmp_path / "empty.txt"
        p.write_text("\n \n", encoding="utf-8")
        with pytest.raises(ig.IntegrationError):
            ig.parse_integration_list(p)

    def test_no_cluster_raises(self, tmp_path):
        p = tmp_path / "no-clusters.txt"
        p.write_text("TAHT ISNTA noise\nYou're right. I missed two major project folders. rest\n- orphan item\n", encoding="utf-8")
        with pytest.raises(ig.IntegrationError, match="no cluster"):
            ig.parse_integration_list(p)

    def test_missing_noise_markers_raise(self, tmp_path):
        p = tmp_path / "no-noise.txt"
        p.write_text("1. SynPath — test\n- Geometric Deep Learning\n", encoding="utf-8")
        with pytest.raises(ig.IntegrationError, match="noise"):
            ig.parse_integration_list(p)

    def test_real_taxonomy_regression_pin(self):
        """The immutable input (commit 77cf6cf) parses to pinned stats.

        A failure here means the taxonomy file changed or the parser
        regressed; both require explicit re-validation, never a silent
        re-baseline.
        """
        real = REPO_ROOT / "index of the missing things.txt"
        if not real.is_file():
            pytest.skip("real taxonomy file not present")
        inv = ig.parse_integration_list(real)
        stats = inv["parse_stats"]
        assert stats["clusters_total"] == 9
        assert stats["sections_total"] == 81
        assert stats["raw_item_lines"] == 1283
        assert stats["unique_items"] == 1233
        assert stats["items_with_alias"] == 66
        assert stats["names_in_multiple_sections"] == 39
        assert stats["excluded_lines_total"] == 85
        assert stats["principal_concepts_crossrefs"] == 81
        assert inv["noise_block"] == {"start_line": 719, "end_line": 802}
        cluster_ids = [c["cluster_id"] for c in inv["clusters"]]
        assert cluster_ids == [
            "SYNPATH",
            "MAPDIG",
            "MATHSOLVER",
            "WEATHER",
            "NLME",
            "VAULTX",
            "MASTER-INDEX",
            "MEDNLP",
            "2D3D",
        ]


# ---------------------------------------------------------------------------
# build_coverage


class TestBuildCoverage:
    def test_title_band_exact(self, tmp_path):
        vault = tmp_path / "vault"
        vault_note(vault, "K-Nearest Neighbors.md", "# K-Nearest Neighbors\n\nBody text.\n")
        items = [{"item_id": "INT-0001", "name": "K-Nearest Neighbors", "alias": None, "clusters": ["T"]}]
        cov = ig.build_coverage(items, vault)
        assert cov["items"][0]["band"] == "title"
        assert cov["aggregate"]["band_counts"]["title"] == 1

    def test_frontmatter_alias_counts_as_title(self, tmp_path):
        vault = tmp_path / "vault"
        vault_note(
            vault,
            "Attention.md",
            "---\naliases: [Scaled Dot-Product Attention]\n---\n# Attention\n\nBody.\n",
        )
        items = [{"item_id": "INT-0001", "name": "Scaled Dot-Product Attention", "alias": None, "clusters": ["T"]}]
        cov = ig.build_coverage(items, vault)
        assert cov["items"][0]["band"] == "title"
        m = cov["items"][0]["title_matches"][0]
        assert m["via"] == "frontmatter-alias"

    def test_heading_band_numbering_stripped(self, tmp_path):
        vault = tmp_path / "vault"
        vault_note(vault, "Optimizers.md", "# Optimizers\n\n## 3.2 Adam Optimizer\n\nBody.\n")
        items = [{"item_id": "INT-0001", "name": "Adam Optimizer", "alias": None, "clusters": ["T"]}]
        cov = ig.build_coverage(items, vault)
        assert cov["items"][0]["band"] == "heading"

    def test_partial_band_substring_title(self, tmp_path):
        vault = tmp_path / "vault"
        vault_note(vault, "Graph Neural Networks.md", "# Graph Neural Networks\n\nBody.\n")
        items = [{"item_id": "INT-0001", "name": "Graph Neural Networks Survey", "alias": None, "clusters": ["T"]}]
        cov = ig.build_coverage(items, vault)
        assert cov["items"][0]["band"] == "partial"

    def test_body_bands_and_british_american_plural(self, tmp_path):
        vault = tmp_path / "vault"
        vault_note(
            vault,
            "Matching Methods.md",
            "# Overview\n\nWe apply K-nearest-neighbor matching, then k-nearest-neighbor matching again.\n",
        )
        items = [
            {"item_id": "INT-0001", "name": "K-Nearest Neighbour Matching", "alias": None, "clusters": ["T"]},
            {"item_id": "INT-0002", "name": "Gaussian Basis Functions", "alias": None, "clusters": ["T"]},
            {"item_id": "INT-0003", "name": "Contrastive Divergence", "alias": None, "clusters": ["T"]},
        ]
        vault_note(vault, "RBF.md", "# RBF\n\nA Gaussian Basis Function expansion is used.\n")
        cov = ig.build_coverage(items, vault)
        bands = {c["item_id"]: c["band"] for c in cov["items"]}
        assert bands["INT-0001"] == "body-multi"  # Brit surface, US body, x2
        assert bands["INT-0002"] == "body-single"  # plural surface, singular body
        assert bands["INT-0003"] == "none"

    def test_alias_surface_used_for_matching(self, tmp_path):
        vault = tmp_path / "vault"
        vault_note(vault, "LSTM.md", "# Long Short-Term Memory\n\nThe LSTM cell.\nThe LSTM cell again.\n")
        items = [{"item_id": "INT-0001", "name": "Long Short-Term Memory", "alias": "LSTM", "clusters": ["T"]}]
        cov = ig.build_coverage(items, vault)
        rec = cov["items"][0]
        assert rec["band"] == "title"
        assert rec["body"]["occurrences"] >= 2

    def test_cluster_bands_aggregate(self, tmp_path):
        vault = tmp_path / "vault"
        vault_note(vault, "A Note.md", "# Overview\n\nAlpha content.\n")
        items = [
            {"item_id": "INT-0001", "name": "A Note", "alias": None, "clusters": ["CL1"]},
            {"item_id": "INT-0002", "name": "Missing Concept", "alias": None, "clusters": ["CL2"]},
        ]
        cov = ig.build_coverage(items, vault)
        assert cov["aggregate"]["cluster_bands"] == {"CL1": {"title": 1}, "CL2": {"none": 1}}

    def test_vault_read_only(self, tmp_path):
        vault = tmp_path / "vault"
        vault_note(vault, "Note.md", "# Note\n\nBody.\n")
        before = dir_hash(vault)
        items = [{"item_id": "INT-0001", "name": "Note", "alias": None, "clusters": ["T"]}]
        ig.build_coverage(items, vault)
        assert dir_hash(vault) == before

    def test_missing_vault_dir_raises(self, tmp_path):
        items = [{"item_id": "INT-0001", "name": "X", "alias": None, "clusters": ["T"]}]
        with pytest.raises(ig.IntegrationError):
            ig.build_coverage(items, tmp_path / "missing")

    def test_empty_vault_raises(self, tmp_path):
        (tmp_path / "empty-vault").mkdir()
        items = [{"item_id": "INT-0001", "name": "X", "alias": None, "clusters": ["T"]}]
        with pytest.raises(ig.IntegrationError, match="no markdown notes"):
            ig.build_coverage(items, tmp_path / "empty-vault")


# ---------------------------------------------------------------------------
# load_inventory_items


class TestLoadInventoryItems:
    def test_roundtrip(self, tmp_path):
        inv = ig.parse_integration_list(write_taxonomy(tmp_path))
        p = tmp_path / "items.jsonl"
        p.write_text("\n".join(ig.inventory_items_jsonl(inv)) + "\n", encoding="utf-8")
        loaded = ig.load_inventory_items(p)
        assert len(loaded) == len(inv["items"])
        assert loaded[0]["item_id"] == "INT-0001"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(ig.IntegrationError):
            ig.load_inventory_items(tmp_path / "nope.jsonl")

    def test_malformed_line_raises(self, tmp_path):
        p = tmp_path / "bad.jsonl"
        p.write_text(
            '{"item_id": "INT-0001", "name": "A"}\nnot json\n',
            encoding="utf-8",
        )
        with pytest.raises(ig.IntegrationError, match="line 2"):
            ig.load_inventory_items(p)

    def test_record_missing_name_raises(self, tmp_path):
        p = tmp_path / "bad.jsonl"
        p.write_text('{"item_id": "INT-0001"}\n', encoding="utf-8")
        with pytest.raises(ig.IntegrationError, match="item_id and name"):
            ig.load_inventory_items(p)

    def test_duplicate_ids_raise(self, tmp_path):
        p = tmp_path / "dup.jsonl"
        p.write_text(
            '{"item_id": "INT-0001", "name": "A"}\n{"item_id": "INT-0001", "name": "B"}\n',
            encoding="utf-8",
        )
        with pytest.raises(ig.IntegrationError, match="duplicate"):
            ig.load_inventory_items(p)

    def test_empty_inventory_raises(self, tmp_path):
        p = tmp_path / "empty.jsonl"
        p.write_text("\n\n", encoding="utf-8")
        with pytest.raises(ig.IntegrationError, match="no item records"):
            ig.load_inventory_items(p)


# ---------------------------------------------------------------------------
# CLI end-to-end


class TestCliCommands:
    def test_integ_inventory_end_to_end(self, tmp_path):
        tax = write_taxonomy(tmp_path)
        items = tmp_path / "out" / "items.jsonl"
        clusters = tmp_path / "out" / "clusters.json"
        report = tmp_path / "out" / "report.json"
        rc = cli.main(
            [
                "integ-inventory",
                "--list-file", str(tax),
                "--items-out", str(items),
                "--clusters-out", str(clusters),
                "--report", str(report),
            ]
        )
        assert rc == 0
        recs = [json.loads(ln) for ln in items.read_text(encoding="utf-8").splitlines()]
        assert recs and all(r.get("item_id") and r.get("name") for r in recs)
        cl = json.loads(clusters.read_text(encoding="utf-8"))
        assert cl["source_sha256"]
        assert "noise_block" in cl and "parse_stats" in cl
        rep = json.loads(report.read_text(encoding="utf-8"))
        assert rep["command"] == "integ-inventory"
        assert rep["result"]["parse_stats"]["unique_items"] == len(recs)

    def test_integ_coverage_end_to_end(self, tmp_path):
        tax = write_taxonomy(tmp_path)
        items_out = tmp_path / "out" / "items.jsonl"
        clusters = tmp_path / "out" / "clusters.json"
        assert cli.main(
            [
                "integ-inventory",
                "--list-file", str(tax),
                "--items-out", str(items_out),
                "--clusters-out", str(clusters),
            ]
        ) == 0
        vault = tmp_path / "vault"
        vault_note(vault, "Geometric Deep Learning.md", "# Geometric Deep Learning\n\nBody.\n")
        cov_out = tmp_path / "out" / "coverage.jsonl"
        report = tmp_path / "out" / "cov-report.json"
        rc = cli.main(
            [
                "integ-coverage",
                "--inventory", str(items_out),
                "--vault-root", str(vault),
                "--items-out", str(cov_out),
                "--report", str(report),
            ]
        )
        assert rc == 0
        recs = [json.loads(ln) for ln in cov_out.read_text(encoding="utf-8").splitlines()]
        by_id = {r["item_id"]: r for r in recs}
        assert by_id["INT-0001"]["band"] == "title"
        rep = json.loads(report.read_text(encoding="utf-8"))
        assert rep["command"] == "integ-coverage"
        assert rep["result"]["aggregate"]["items_total"] == len(recs)

    def test_integ_inventory_bad_list_file_exit_1(self, tmp_path, capsys):
        rc = cli.main(
            [
                "integ-inventory",
                "--list-file", str(tmp_path / "nope.txt"),
                "--items-out", str(tmp_path / "items.jsonl"),
                "--clusters-out", str(tmp_path / "clusters.json"),
            ]
        )
        assert rc == 1
        assert "error" in capsys.readouterr().err

    def test_integ_coverage_bad_inventory_exit_1(self, tmp_path, capsys):
        vault = tmp_path / "vault"
        vault_note(vault, "A.md", "# A\n")
        rc = cli.main(
            [
                "integ-coverage",
                "--inventory", str(tmp_path / "missing.jsonl"),
                "--vault-root", str(vault),
                "--items-out", str(tmp_path / "cov.jsonl"),
            ]
        )
        assert rc == 1
        assert "error" in capsys.readouterr().err

    def test_integ_inventory_refuses_write_into_source_roots(self, tmp_path, capsys, monkeypatch):
        # simulate the default protected root layout: source-vaults/<x>
        protected = tmp_path / "source-vaults" / "AI "
        protected.mkdir(parents=True)
        monkeypatch.setattr(cli, "REPO_ROOT", tmp_path)
        tax = write_taxonomy(tmp_path)
        rc = cli.main(
            [
                "integ-inventory",
                "--list-file", str(tax),
                "--items-out", str(protected / "items.jsonl"),
                "--clusters-out", str(tmp_path / "clusters.json"),
            ]
        )
        assert rc == 1
        assert "protected" in capsys.readouterr().err

    def test_integ_coverage_refuses_write_into_vault(self, tmp_path, capsys):
        tax = write_taxonomy(tmp_path)
        items_out = tmp_path / "items.jsonl"
        assert cli.main(
            [
                "integ-inventory",
                "--list-file", str(tax),
                "--items-out", str(items_out),
                "--clusters-out", str(tmp_path / "clusters.json"),
            ]
        ) == 0
        vault = tmp_path / "vault"
        vault_note(vault, "A.md", "# A\n")
        rc = cli.main(
            [
                "integ-coverage",
                "--inventory", str(items_out),
                "--vault-root", str(vault),
                "--items-out", str(vault / "inside-vault.jsonl"),
            ]
        )
        assert rc == 1
        assert "protected" in capsys.readouterr().err

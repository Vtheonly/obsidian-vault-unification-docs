"""Unit/integration tests for the duplicate-phrase/block scan
(AUDIT-013; closes the F-0037/F-0038 remaining risk)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import dupscan as ds  # noqa: E402


def write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / "vault" / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


class TestStutterDetection:
    def test_f0037_regression_shape_detected(self, tmp_path):
        write(
            tmp_path,
            "stutter.md",
            "# S\n\na fascinating mathematical coincidence: a fascinating mathematical coincidence: a fascinating mathematical coincidence: the derivatives match.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        assert report["results"]["findings_total"] == 1
        f = report["findings"][0]
        assert f["class"] == "stutter"
        assert f["repeat_count"] == 3
        assert "mathematical coincidence" in f["phrase"]
        assert f["severity"] == "medium"

    def test_double_stutter_detected_low(self, tmp_path):
        write(
            tmp_path,
            "double.md",
            "# D\n\nthe model is trained on data the model is trained on data and then evaluated.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        stutters = [f for f in report["findings"] if f["class"] == "stutter"]
        assert len(stutters) == 1
        assert stutters[0]["repeat_count"] == 2

    def test_clean_prose_not_flagged(self, tmp_path):
        write(
            tmp_path,
            "clean.md",
            "# C\n\nThe gradient is computed and the gradient is applied. Repetition across sentences is fine.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        assert report["results"]["findings_total"] == 0

    def test_math_row_repeat_excluded(self, tmp_path):
        write(
            tmp_path,
            "math.md",
            "# M\n\nThe kernel matrix is:\n\n$$\n\\begin{bmatrix} 1 & 0 & -1 \\\\ 1 & 0 & -1 \\\\ \\end{bmatrix}\n$$\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        assert report["results"]["findings_total"] == 0

    def test_pipeline_arrow_repeat_excluded(self, tmp_path):
        write(
            tmp_path,
            "pipe.md",
            "# P\n\nThe block is Linear → ReLU → Dropout → Linear → ReLU → Dropout → stacked twice.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        assert report["results"]["findings_total"] == 0

    def test_enumeration_comma_repeat_excluded(self, tmp_path):
        write(
            tmp_path,
            "enum.md",
            "# E\n\nLearning rates tried: 0.01, 0.01, 0.01, and 0.001.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        assert report["results"]["findings_total"] == 0

    def test_code_fence_not_scanned(self, tmp_path):
        write(
            tmp_path,
            "fence.md",
            "# F\n\n```python\nprint('hello') print('hello') print('hello')\n```\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        assert report["results"]["findings_total"] == 0

    def test_table_rows_not_scanned(self, tmp_path):
        write(
            tmp_path,
            "table.md",
            "# T\n\n| a | b |\n| a | b |\n| a | b |\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        assert report["results"]["findings_total"] == 0

    def test_frontmatter_not_scanned(self, tmp_path):
        write(
            tmp_path,
            "fm.md",
            "---\naliases: [dup dup dup dup, x]\n---\n\n# FM\n\nBody is clean.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        assert report["results"]["findings_total"] == 0


class TestTandemBlockDetection:
    def test_f0038_regression_shape_detected(self, tmp_path):
        para = "The original course material wrote the same definition with French condition labels."
        write(
            tmp_path,
            "tandem.md",
            "# T\n\n"
            + (para + "\n\n$$\\delta(|e| - \\delta/2)$$\n\n- si: si la condition\n- sinon: sinon\n\n") * 3
            + "Closing prose.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        tandems = [f for f in report["findings"] if f["class"] == "tandem_block"]
        assert len(tandems) == 1
        f = tandems[0]
        assert f["span_blocks"] == 3
        assert f["repeat_count"] == 3
        assert f["severity"] == "medium"

    def test_single_block_doubled_detected(self, tmp_path):
        write(
            tmp_path,
            "dbl.md",
            "# D\n\nSame paragraph twice in a row.\n\nSame paragraph twice in a row.\n\nOther text.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        tandems = [f for f in report["findings"] if f["class"] == "tandem_block"]
        assert len(tandems) == 1
        assert tandems[0]["span_blocks"] == 1
        assert tandems[0]["repeat_count"] == 2

    def test_fence_atomic_in_tandem(self, tmp_path):
        write(
            tmp_path,
            "tf.md",
            "# TF\n\nIntro.\n\n```python\nx = 1\n\ny = 2\n```\n\n```python\nx = 1\n\ny = 2\n```\n\nOutro.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        tandems = [f for f in report["findings"] if f["class"] == "tandem_block"]
        assert len(tandems) == 1
        assert tandems[0]["span_blocks"] == 1

    def test_nonconsecutive_blocks_not_flagged(self, tmp_path):
        write(
            tmp_path,
            "nc.md",
            "# N\n\nA paragraph.\n\nDifferent middle.\n\nA paragraph.\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        assert report["results"]["findings_total"] == 0

    def test_headings_do_not_break_blocks_silently(self, tmp_path):
        # consecutive identical list groups are a tandem block too
        write(
            tmp_path,
            "lg.md",
            "# L\n\n- item one\n- item two\n\n- item one\n- item two\n",
        )
        report = ds.dup_scan(tmp_path / "vault")
        tandems = [f for f in report["findings"] if f["class"] == "tandem_block"]
        assert len(tandems) == 1


class TestDeterminismAndCLI:
    def test_deterministic(self, tmp_path):
        write(
            tmp_path,
            "d.md",
            "# D\n\nstutter stutter stutter x\n\nA.\n\nA.\n",
        )
        a = ds.dup_scan(tmp_path / "vault")
        b = ds.dup_scan(tmp_path / "vault")
        assert a == b

    def test_root_not_mutated(self, tmp_path):
        write(tmp_path, "r.md", "# R\n\nstutter stutter stutter x\n")
        root = tmp_path / "vault"

        def digest():
            return {
                str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(root.rglob("*"))
                if p.is_file()
            }

        before = digest()
        ds.dup_scan(root)
        assert digest() == before

    def test_cli_exit_one_with_findings(self, tmp_path):
        write(
            tmp_path,
            "c.md",
            "# C\n\nthe same phrase repeats here the same phrase repeats here again.\n",
        )
        report_path = tmp_path / "report.json"
        proc = subprocess.run(
            [
                sys.executable, "-m", "vault_unification", "dup-scan",
                "--root", str(tmp_path / "vault"),
                "--report", str(report_path),
            ],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parents[1]),
        )
        assert proc.returncode == 1
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        assert payload["result"]["results"]["findings_total"] >= 1

    def test_cli_exit_zero_clean(self, tmp_path):
        write(tmp_path, "ok.md", "# OK\n\nClean prose with no duplication at all.\n")
        proc = subprocess.run(
            [
                sys.executable, "-m", "vault_unification", "dup-scan",
                "--root", str(tmp_path / "vault"),
            ],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parents[1]),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr

    def test_unreadable_file_reported_not_raised(self, tmp_path):
        write(tmp_path, "bad.md", "# B\n")
        p = tmp_path / "vault" / "bad.md"
        p.chmod(0o000)
        try:
            import os

            if os.access(p, os.R_OK):  # running as root: skip
                return
            report = ds.dup_scan(tmp_path / "vault")
            assert report["scope"]["unreadable"]
        finally:
            p.chmod(0o644)

    def test_denominators_present(self, tmp_path):
        write(tmp_path, "den.md", "# Den\n\nOne line.\n\nTwo line.\n")
        report = ds.dup_scan(tmp_path / "vault")
        assert report["scope"]["notes_scanned"] == 1
        assert report["scope"]["lines_scanned_excl_fences_tables"] >= 3
        assert report["scope"]["blocks_scanned"] >= 3

"""BOOT-001: formal source-location and repository-state record.

Produces reports/bootstrap/boot-001-source-location.json containing:
- exact source vault paths (including the trailing-space parent, F-0001);
- fresh file counts, per-class counts, and byte totals from a live scan;
- immutability evidence (fresh scan vs. baseline manifest diff);
- git state (HEAD commit, branch, working tree, remote slug, source commit);
- top-level repository structure and per-vault top-level structure;
- backup/recovery note (git history + manifests + remote).

All counts are computed by code (inventory.scan_root), not by model
attention, per the framework-first protocol.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from vault_unification import inventory as inv  # noqa: E402
from vault_unification import reporting  # noqa: E402

VAULTS = [
    {
        "name": "Master AI",
        "root": "source-vaults/AI /Master AI",
        "manifest": "state/manifests/master-ai.jsonl",
    },
    {
        "name": "AI Course",
        "root": "source-vaults/AI /AI Course",
        "manifest": "state/manifests/ai-course.jsonl",
    },
]


def git_output(*args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=30,
        check=False,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def du_bytes(path: Path) -> int | None:
    result = subprocess.run(
        ["du", "-sb", str(path)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode == 0:
        try:
            return int(result.stdout.split()[0])
        except (IndexError, ValueError):
            return None
    return None


def top_level(root: Path) -> dict:
    dirs, files = [], []
    for entry in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if entry.is_dir():
            dirs.append(entry.name)
        else:
            files.append(entry.name)
    return {"directories": dirs, "files": files}


def main() -> int:
    vault_records = []
    for spec in VAULTS:
        root_path = REPO_ROOT / spec["root"]
        scan = inv.scan_root(root_path)
        baseline = inv.load_manifest(REPO_ROOT / spec["manifest"])
        diff = inv.diff_manifests(baseline, inv.manifest_records(scan))
        manifest_bytes = sum(rec["size"] or 0 for rec in scan["files"])
        record = {
            "name": spec["name"],
            "root_exact": spec["root"],
            "root_exists": root_path.is_dir(),
            "path_note": (
                "parent directory 'source-vaults/AI ' contains a trailing "
                "space (finding F-0001); every consumer must pass the literal "
                "quoted path"
            ),
            "file_counts": scan["counts"],
            "total_files": scan["total_files"],
            "unreadable_files": [
                {k: rec.get(k) for k in ("relpath", "error", "note")}
                for rec in scan["errors"]
            ],
            "manifested_files": len(baseline),
            "manifest_bytes": manifest_bytes,
            "on_disk_bytes_du": du_bytes(root_path),
            "baseline_manifest": spec["manifest"],
            "immutability_vs_baseline": {
                "added": diff["added"],
                "removed": diff["removed"],
                "changed": diff["changed"],
                "unchanged_count": len(diff["unchanged"]),
                "source_unchanged": not (diff["added"] or diff["removed"] or diff["changed"]),
            },
            "symlinks_present": any(rec["is_symlink"] for rec in scan["files"] + scan["errors"]),
            "top_level": top_level(root_path),
        }
        vault_records.append(record)

    porcelain = git_output("status", "--porcelain") or ""
    remote_url = git_output("remote", "get-url", "origin") or ""
    # Sanitize credentials from the remote URL; keep only the slug.
    remote_slug = remote_url
    if "@" in remote_slug:
        remote_slug = remote_slug.split("@", 1)[1]
    remote_slug = remote_slug.replace("https://", "").replace("git@", "").replace(".git", "")

    repo_structure = {
        "top_level_directories": sorted(
            p.name for p in REPO_ROOT.iterdir() if p.is_dir() and p.name != ".git"
        ),
        "top_level_files": sorted(
            p.name for p in REPO_ROOT.iterdir() if p.is_file()
        ),
    }

    payload = {
        "purpose": (
            "BOOT-001 formal record: both source vaults located, inventoried "
            "at file level, and confirmed unchanged against baseline "
            "manifests; git and repository structure recorded. No source "
            "files modified (evidence below)."
        ),
        "git_state": {
            "head_commit": git_output("rev-parse", "HEAD"),
            "branch": git_output("branch", "--show-current"),
            "working_tree_clean": porcelain == "",
            "porcelain_output": porcelain[:2000] if porcelain else "",
            "origin_slug": remote_slug,
            "source_vaults_introduced_in_commit": git_output(
                "rev-list", "--max-parents=0", "HEAD"
            ),
        },
        "repository_structure": repo_structure,
        "source_vaults": vault_records,
        "backup_and_recovery": {
            "strategy": (
                "Both source vaults are committed to git (first commit) and "
                "pushed to the origin remote; git history plus the SHA-256 "
                "baseline manifests (state/manifests/) provide the "
                "recoverable snapshot required by docs/SOURCE_POLICY.md."
            ),
            "baseline_manifests": [v["baseline_manifest"] for v in vault_records],
            "verification_command": (
                "PYTHONPATH=src python3 -m vault_unification verify-manifest "
                "--root <vault root> --manifest <manifest>"
            ),
        },
        "limitations": [
            "File-level inventory only: no content, semantic, or knowledge-"
            "unit claims are made by this record (BOOT-002+).",
            "Counts and hashes are lexical evidence, not semantic coverage.",
        ],
    }

    out_path = REPO_ROOT / "reports" / "bootstrap" / "boot-001-source-location.json"
    reporting.write_json_report(
        out_path,
        command="boot-001-record",
        payload=payload,
        args={"roots": [spec["root"] for spec in VAULTS]},
        repo_root=REPO_ROOT,
    )

    summary = {
        "report": str(out_path.relative_to(REPO_ROOT)),
        "head_commit": payload["git_state"]["head_commit"],
        "working_tree_clean": payload["git_state"]["working_tree_clean"],
    }
    for v in vault_records:
        summary[v["name"]] = {
            "files": v["total_files"],
            "unchanged_vs_baseline": v["immutability_vs_baseline"]["source_unchanged"],
            "bytes_manifest": v["manifest_bytes"],
        }
    print(__import__("json").dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

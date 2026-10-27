"""Recursive inventory, SHA-256 hashing, manifests and change detection.

Inventories are content-based: a manifest record identifies a file by its
repository-relative path and SHA-256 hash. Modification times are recorded for
information only and are never used in comparisons.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

from .pathsafety import atomic_write_text

_EXTENSION_CLASSES: dict[str, str] = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".txt": "text",
    ".rst": "text",
    ".csv": "text",
    ".json": "text",
    ".yml": "text",
    ".yaml": "text",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".bmp": "image",
    ".svg": "image",
    ".webp": "image",
    ".pdf": "pdf",
    ".py": "code",
    ".ipynb": "code",
    ".js": "code",
    ".ts": "code",
    ".sh": "code",
}

KNOWN_CLASSES = {"markdown", "text", "image", "pdf", "code", "other"}


def classify_extension(ext: str) -> str:
    """Map a file extension to a coarse content class."""
    return _EXTENSION_CLASSES.get(ext.lower(), "other")


def _sha256_file(path: Path, chunk_size: int = 1 << 20) -> tuple[str | None, str | None]:
    """Hash *path*; return (sha256_hex, error_message). Exactly one is None."""
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            while True:
                chunk = handle.read(chunk_size)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest(), None
    except OSError as exc:  # unreadable, permission, vanished mid-scan
        return None, f"{type(exc).__name__}: {exc}"


def scan_root(root: str | os.PathLike, *, follow_symlinks: bool = False) -> dict:
    """Recursively inventory *root*.

    Returns a dict with:
    - ``files``: list of per-file records sorted by repository-relative path;
    - ``errors``: list of records for unreadable/unhashable files;
    - ``counts``: totals by class, plus unreadable count;
    - ``root``: the requested root.

    Every discovered file receives a record in exactly one of the two lists;
    nothing is silently skipped. Symlinked files are recorded with
    ``is_symlink`` unless *follow_symlinks* is set, in which case the link
    targets are hashed instead (still recorded explicitly).
    """
    root_path = Path(root)
    if not root_path.is_dir():
        raise NotADirectoryError(f"inventory root is not a directory: {root_path}")

    files: list[dict] = []
    errors: list[dict] = []

    for dirpath, dirnames, filenames in os.walk(root_path, followlinks=follow_symlinks):
        dirnames.sort()
        for name in sorted(filenames):
            abs_path = Path(dirpath) / name
            relpath = abs_path.relative_to(root_path).as_posix()
            is_link = abs_path.is_symlink()
            record: dict[str, Any] = {
                "relpath": relpath,
                "class": classify_extension(abs_path.suffix),
                "extension": abs_path.suffix.lower(),
                "is_symlink": is_link,
            }
            if is_link and not follow_symlinks:
                record["size"] = None
                record["sha256"] = None
                record["note"] = "symlink not followed; use --follow-symlinks to hash targets"
                errors.append(record)
                continue
            try:
                stat = abs_path.stat()
                record["size"] = stat.st_size
            except OSError as exc:
                record["size"] = None
                record["sha256"] = None
                record["error"] = f"stat failed: {type(exc).__name__}: {exc}"
                errors.append(record)
                continue
            sha, err = _sha256_file(abs_path)
            if err is not None:
                record["sha256"] = None
                record["error"] = f"hash failed: {err}"
                errors.append(record)
                continue
            record["sha256"] = sha
            files.append(record)

    counts: dict[str, int] = {cls: 0 for cls in sorted(KNOWN_CLASSES)}
    for rec in files:
        counts[rec["class"]] = counts.get(rec["class"], 0) + 1
    counts["unreadable"] = len(errors)

    return {
        "root": str(root_path),
        "files": files,
        "errors": errors,
        "counts": counts,
        "total_files": len(files) + len(errors),
    }


def manifest_records(scan: dict) -> list[dict]:
    """Content-identity records for a scan (used for immutability checks)."""
    return [
        {"relpath": rec["relpath"], "size": rec["size"], "sha256": rec["sha256"]}
        for rec in scan["files"]
    ]


def write_manifest(path: str | os.PathLike, records: Iterable[dict]) -> int:
    """Write manifest records as JSONL atomically (L-08). Returns count."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(json.dumps(rec, sort_keys=True) + "\n" for rec in records)
    atomic_write_text(path, payload)
    return payload.count("\n")


def load_manifest(path: str | os.PathLike) -> list[dict]:
    """Load a JSONL manifest; raises ValueError on any malformed line."""
    records: list[dict] = []
    with open(path, encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"manifest line {lineno} is not valid JSON: {exc}") from exc
            if not isinstance(rec, dict) or "relpath" not in rec or "sha256" not in rec:
                raise ValueError(
                    f"manifest line {lineno} lacks required 'relpath'/'sha256' fields"
                )
            records.append(rec)
    return records


def diff_manifests(
    before: list[dict], after: list[dict]
) -> dict:
    """Compare two manifests (lists of {relpath,size,sha256} records)."""
    before_map = {rec["relpath"]: rec for rec in before}
    after_map = {rec["relpath"]: rec for rec in after}
    added = sorted(set(after_map) - set(before_map))
    removed = sorted(set(before_map) - set(after_map))
    changed = sorted(
        path
        for path in set(before_map) & set(after_map)
        if before_map[path].get("sha256") != after_map[path].get("sha256")
    )
    unchanged = sorted(
        path
        for path in set(before_map) & set(after_map)
        if before_map[path].get("sha256") == after_map[path].get("sha256")
    )
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
        "counts": {
            "before": len(before_map),
            "after": len(after_map),
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "unchanged": len(unchanged),
        },
    }

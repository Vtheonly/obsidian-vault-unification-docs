"""Path safety enforcement.

Every command that touches files must go through these checks. Source vaults
are read-only by default; writes require an explicit destination that cannot
overlap any protected root.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class PathSafetyError(Exception):
    """Raised when a requested path operation is unsafe."""


@dataclass(frozen=True)
class RootValidation:
    """Result of validating a pair of source/output roots."""

    source: str
    output: str | None
    ok: bool
    problems: list[str]

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "output": self.output,
            "ok": self.ok,
            "problems": list(self.problems),
        }


def _resolved_parts(path: Path) -> tuple[Path, list[str]]:
    """Resolve *path* as far as possible and report symlink components.

    Returns (resolved_path, symlink_component_strings). Missing leaf components
    are tolerated (an output root may not exist yet) but missing parents and
    symlinked components are hazards that must be reported.
    """
    start = Path(os.path.abspath(path))
    resolved = Path(os.path.realpath(start))
    symlinks: list[str] = []
    # Walk the original chain and note any component that is a symlink.
    current = start
    while True:
        if current.is_symlink():
            symlinks.append(str(current))
        parent = current.parent
        if current == parent:
            break
        current = parent
    return resolved, symlinks


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_roots(source: str | os.PathLike, output: str | os.PathLike | None = None) -> RootValidation:
    """Validate that *source* exists and that *output* does not overlap it.

    Rules enforced:
    - the source root must exist and be a directory;
    - the output root must not contain the source, nor be contained by it;
    - symlink components anywhere in either chain are reported as hazards;
    - identical roots are rejected.
    """
    problems: list[str] = []
    src_path = Path(source)
    if not src_path.exists():
        problems.append(f"source root does not exist: {src_path}")
    elif not src_path.is_dir():
        problems.append(f"source root is not a directory: {src_path}")

    src_resolved, src_symlinks = _resolved_parts(src_path)
    if src_symlinks:
        problems.append(f"source root path contains symlink components: {src_symlinks}")

    out_resolved = None
    if output is not None:
        out_path = Path(output)
        out_resolved, out_symlinks = _resolved_parts(out_path)
        if out_symlinks:
            problems.append(f"output root path contains symlink components: {out_symlinks}")
        if out_resolved == src_resolved:
            problems.append("output root is identical to source root")
        elif _is_relative_to(src_resolved, out_resolved):
            problems.append(f"source root is inside the output root: {src_resolved} under {out_resolved}")
        elif _is_relative_to(out_resolved, src_resolved):
            problems.append(f"output root is inside the source root: {out_resolved} under {src_resolved}")

    return RootValidation(
        source=str(src_path),
        output=str(output) if output is not None else None,
        ok=not problems,
        problems=problems,
    )


def ensure_dest_safe(dest: str | os.PathLike, protected_roots: list[str | os.PathLike]) -> Path:
    """Return the resolved destination path after safety checks.

    Raises PathSafetyError when *dest* is inside any protected (source) root or
    equals one. This is the write-side guard: framework commands must call it
    before creating any output file.
    """
    dest_resolved, dest_symlinks = _resolved_parts(Path(dest))
    if dest_symlinks:
        raise PathSafetyError(
            f"destination path contains symlink components: {dest_symlinks}"
        )
    for root in protected_roots:
        root_resolved, _ = _resolved_parts(Path(root))
        if dest_resolved == root_resolved or _is_relative_to(dest_resolved, root_resolved):
            raise PathSafetyError(
                f"refusing to write into protected (source) root: {dest_resolved} "
                f"is inside {root_resolved}"
            )
    return dest_resolved


def assert_source_immutable(manifest_before: list[dict], manifest_after: list[dict]) -> dict:
    """Compare two inventory manifests and report any source mutation.

    Both manifests are lists of file records as produced by
    ``inventory.load_manifest``. Returns a report dict; ``changed_files`` is
    non-empty only if the source changed between the two snapshots.
    """
    before = {rec["relpath"]: rec for rec in manifest_before}
    after = {rec["relpath"]: rec for rec in manifest_after}
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(
        path
        for path in set(before) & set(after)
        if before[path].get("sha256") != after[path].get("sha256")
        or before[path].get("size") != after[path].get("size")
    )
    return {
        "source_unchanged": not (added or removed or changed),
        "added": added,
        "removed": removed,
        "changed": changed,
        "files_before": len(before),
        "files_after": len(after),
    }

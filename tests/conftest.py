"""Shared fixtures: a synthetic Obsidian-like vault in a temp directory.

The fixture deliberately contains both well-formed and malformed content so
negative paths are exercised: broken links, ambiguous basenames, unclosed
code fences, invalid frontmatter YAML, an empty file and binary assets.
"""

from __future__ import annotations

import hashlib
import textwrap
from pathlib import Path

import pytest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def fixture_vault(tmp_path: Path) -> dict:
    """Build a small synthetic vault; returns a dict of interesting paths."""
    vault = tmp_path / "fixture-vault"

    _write(
        vault / "note-a.md",
        textwrap.dedent(
            """\
            ---
            title: Note A
            tags:
              - alpha
              - beta
            ---

            # Note A Title

            Intro paragraph with a #inline tag and math $E = mc^2$ inline.

            ## Section One

            Wikilink to [[note-b]] and aliased [[note-b|display name]].

            Embed: ![[image.png]]

            Markdown link to [internal](note-b) and [external](https://example.com/docs).

            ```python
            def f(x):
                return x + 1
            ```

            $$
            \\int_0^1 f(x)\\,dx
            $$

            ### Subsection

            See [[note-b#Deep Heading]] and block [[note-b^blockref]].
            """
        ),
    )

    _write(
        vault / "note-b.md",
        textwrap.dedent(
            """\
            # Note B

            ## Deep Heading

            Target content with a block.

            Some text ^blockref

            Nothing else.
            """
        ),
    )

    _write(
        vault / "sub" / "note-c.md",
        textwrap.dedent(
            """\
            # Note C

            Broken link: [[missing-note]] and broken anchor [[note-a#No Such Heading]].

            Link to [docs](https://docs.example.com/) and relative [x](../note-b).

            Ambiguous link: [[duplicate]]
            """
        ),
    )

    # two files with the same basename -> ambiguous resolution
    _write(vault / "duplicate.md", "# Duplicate Root\n\nContent one.\n")
    _write(vault / "sub" / "duplicate.md", "# Duplicate Sub\n\nContent two.\n")

    # malformed: unclosed code fence
    _write(
        vault / "broken-fence.md",
        textwrap.dedent(
            """\
            # Broken Fence

            ```python
            def unclosed():
                pass
            """
        ),
    )

    # malformed: invalid frontmatter YAML
    _write(
        vault / "malformed-frontmatter.md",
        textwrap.dedent(
            """\
            ---
            title: [unclosed
            ---
            # After Bad Frontmatter
            """
        ),
    )

    # empty file
    (vault / "empty.md").parent.mkdir(parents=True, exist_ok=True)
    (vault / "empty.md").write_bytes(b"")

    # binary-ish assets
    (vault / "image.png").parent.mkdir(parents=True, exist_ok=True)
    (vault / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00binary")
    (vault / "doc.pdf").parent.mkdir(parents=True, exist_ok=True)
    (vault / "doc.pdf").write_bytes(b"%PDF-1.4 fake")

    return {
        "root": vault,
        "note_a": vault / "note-a.md",
        "note_b": vault / "note-b.md",
        "note_c": vault / "sub" / "note-c.md",
        "broken_fence": vault / "broken-fence.md",
        "malformed_frontmatter": vault / "malformed-frontmatter.md",
        "empty": vault / "empty.md",
        "image": vault / "image.png",
        "pdf": vault / "doc.pdf",
    }


@pytest.fixture()
def binary_file(tmp_path: Path) -> Path:
    path = tmp_path / "blob.bin"
    path.write_bytes(b"\x00\x01\x02\x03binary\xff\xfe")
    return path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

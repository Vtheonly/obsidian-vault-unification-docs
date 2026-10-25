"""Environment diagnostics and framework self-test.

Checks the runtime the framework can rely on and reports anything missing
explicitly. Exit status semantics: mandatory failures make the self-test
fail; optional dependencies produce warnings and degraded-capability notes.
"""

from __future__ import annotations

import importlib.util
import platform
import sys


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def run_selftest() -> dict:
    """Collect environment diagnostics."""
    checks: list[dict] = []

    checks.append(
        {
            "name": "python_version",
            "required": True,
            "ok": sys.version_info >= (3, 10),
            "detail": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "requirement": ">=3.10",
        }
    )

    # core package import
    from . import __version__  # noqa: F401

    checks.append(
        {
            "name": "framework_import",
            "required": True,
            "ok": True,
            "detail": f"vault_unification {__version__} imported",
        }
    )

    optional_modules = [
        ("jsonschema", "registry validation (validate-registry)"),
        ("yaml", "frontmatter parsing (structure)"),
        ("pytest", "test runner (run-tests, capabilities --verify)"),
        ("pytest_jsonreport", "machine-readable test reports (run-tests)"),
    ]
    for module, purpose in optional_modules:
        available = _module_available(module)
        checks.append(
            {
                "name": f"optional:{module}",
                "required": False,
                "ok": available,
                "detail": purpose if available else f"MISSING - {purpose} degraded",
            }
        )

    platform_info = {
        "python": sys.version.split()[0],
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "executable": sys.executable,
    }

    mandatory_ok = all(check["ok"] for check in checks if check["required"])
    optional_missing = [
        check["name"].split(":", 1)[1] for check in checks if not check["ok"] and not check["required"]
    ]
    return {
        "ok": mandatory_ok,
        "mandatory_checks_passed": mandatory_ok,
        "optional_missing": optional_missing,
        "checks": checks,
        "platform": platform_info,
    }

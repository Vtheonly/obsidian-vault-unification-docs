"""Allow ``python -m vault_unification`` execution."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())

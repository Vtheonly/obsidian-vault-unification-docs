# Original Source Vaults

Place the two original Obsidian vaults in this directory before running the project.

Suggested layout:

```text
source-vaults/
  README.md
  vault-1/
    .obsidian/          # include only if useful and safe to version
    ...
  vault-2/
    .obsidian/
    ...
```

You may use the vaults' real names instead of `vault-1` and `vault-2`. If you do, record the exact paths in the project state and source inventory.

## Rules

- Treat both original vaults as immutable inputs. Do not edit, rename, reorganize, or delete their contents during processing.
- Inventory and hash the source files before synthesis.
- Generate the unified vault separately under `output/Unified-Vault/`.
- Do not nest one vault inside the other.
- Keep source `.obsidian` configuration only if needed; inspect it for machine-specific settings or sensitive data before committing.
- Check repository size limits and privacy/licensing considerations before uploading attachments or large binary files to GitHub. If the vaults are too large or should not be public, use a private repository or a documented external storage arrangement.
- Do not assume the source vaults have been supplied until the files are actually present and verified.

The initial agent must update `state/current-state.json` and the inventory records with the actual source paths. This README is only a placement guide, not evidence that the vaults have been inspected.

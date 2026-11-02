#!/usr/bin/env bash
# S22/SYNTH-001 baseline: rebuild the derived registry exactly as the
# session-20/21 checkpoints record (kureg-init + kureg-load x71 +
# kureg-apply-dispositions + kureg-validate). Idempotent: --force re-creates.
set -euo pipefail
cd "$(dirname "$0")/.."

DB=scratch/s22-registry.db
vu kureg-init --db "$DB" --force --report reports/synthesis/s22-kureg-init.json
for batch in state/knowledge-units/*.jsonl; do
  vu kureg-load --db "$DB" --kus "$batch" > /dev/null
done
vu kureg-apply-dispositions --db "$DB" \
  --dispositions state/dispositions/001-disp001-rule-driven.jsonl \
  --report reports/synthesis/s22-kureg-apply-dispositions.json
vu kureg-validate --db "$DB" --report reports/synthesis/s22-kureg-validate.json
echo "REGISTRY REBUILD DONE"

# Session Handoff Contract

Use one canonical handoff file, updated at the end of every session. Do not create a new competing handoff document for every session unless the project explicitly retains an append-only archive.

## Required handoff template

```markdown
# Next Agent Handoff

## Project state
- Current milestone:
- Current task ID:
- Current Git commit:
- Working tree status:
- Registry/checkpoint version:

## Verified completed work
- Exact paths changed:
- Outputs created:
- Source units/files covered:
- Evidence of completion:

## Tests actually run
| Command/test | Result | Evidence/report | Limitations |
|---|---|---|---|

## Findings and unresolved work
- Open finding IDs:
- Blockers:
- Unverified claims:
- Extraction or tool limitations:

## Decisions and configuration
- Decisions made and linked records:
- Tool/model/dependency changes:
- Risks introduced:

## Next task
- Task ID and title:
- Why it is next:
- Dependencies:
- Exact inputs:
- Expected outputs:
- Acceptance criteria:
- Forbidden side effects:

## Resume procedure
1. ...
2. ...
3. ...

## Explicit non-claims
State what has not been verified and do not imply completion beyond evidence.
```

## Handoff validation

A new session must compare this handoff with the actual task queue, registry, Git history, files, reports, and test outputs. If they disagree, the repository evidence takes precedence; correct the handoff and record the discrepancy. The handoff is a navigation aid, not the sole source of truth.

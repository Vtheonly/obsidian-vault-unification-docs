---
title: Vault Management README
type: reference
aliases: [Vault Management, 00 — Vault Management]
tags: [vault-management, readme, project-context]
sources:
  - "README"
created_index: 16
---

This note is the archived introduction to the vault's project-state layer — the management folder that every build iteration read first and updated last. It explains why that layer exists, lists the records it holds together with their purpose and update cadence, and fixes the reading order and editing rules for any future iteration. It was last maintained at iteration 12, and it is preserved here as the entry point to the collection's management records.

> [!info] This folder is the project-state layer of the vault. It is the **first thing every iteration reads** and the **last thing every iteration updates**.

## Purpose

The vault is built iteratively, following a written build protocol. To allow any future iteration to recover state cleanly, this folder maintains a persistent record of:

- What the vault should eventually contain (the roadmap — [[Master Roadmap]]).
- What the current state is (status snapshot — [[Vault Status Log]]).
- What has been completed (historical log — [[Completed Work Log]]).
- What remains to be done (prioritized backlog — [[Remaining Work Log]]).
- What the current and next iterations are doing (handoff — [[Current Iteration Log]], [[Next Iteration Log]]).
- Why structural decisions were made (ADR log — [[Architecture Decisions Log]]).
- How well the vault covers the master prompt (audit — [[Coverage Audit Log]]).
- What research is still open (research queue — [[Research Queue]]).

## Files

The layer consists of ten records, each with a defined purpose and update cadence:

| Record | Purpose | Updated when |
| --- | --- | --- |
| [[Vault Management README]] | This file. | Rarely. |
| [[Master Roadmap]] | The complete intended vault. Source of truth for structure and scope. | When roadmap changes. |
| [[Vault Status Log]] | Concise current-state snapshot. | Every iteration. |
| [[Completed Work Log]] | Historical log of what each iteration produced. | Every iteration. |
| [[Remaining Work Log]] | Prioritized backlog. | Every iteration. |
| [[Current Iteration Log]] | What the current iteration is doing. | Start and end of every iteration. |
| [[Next Iteration Log]] | Handoff for the next iteration. | End of every iteration. |
| [[Architecture Decisions Log]] | ADR log — append-only record of structural choices. | When a structural decision is made. |
| [[Coverage Audit Log]] | Periodic audit against the master prompt. | End of every iteration (or periodically). |
| [[Research Queue]] | Open research questions and unresolved factual claims. | Whenever research items are identified. |

## Reading order for a new iteration

A new iteration reads the state files in this order before touching any content:

1. [[Next Iteration Log]]
2. [[Vault Status Log]]
3. [[Master Roadmap]]
4. [[Remaining Work Log]]
5. [[Coverage Audit Log]]
6. [[Research Queue]]
7. [[Architecture Decisions Log]]
8. [[Completed Work Log]] (skim — for context)
9. Then up one level to the top-level [[Master AI MOC]] and [[Master AI README]].

## Editing rules

The editing rules are strict about state-file hygiene:

- **Never delete completed work** — supersede it with a new entry that links back.
- **Never silently renumber top-level domains** — see [[Architecture Decisions Log]] ADR-001.
- **Always update the [[Vault Status Log]] before stopping an iteration.**
- **Always prepare the [[Next Iteration Log]] before stopping an iteration.**
- **Always record structural changes in the [[Architecture Decisions Log]].**

## See also

- [[Master AI README]] — the top-level vault README.
- [[Master AI MOC]] — the master map of content.
- [[Master AI Index]]
- [[Master Roadmap]]
- [[Learning Roadmap]]
- [[Reading Orders]]

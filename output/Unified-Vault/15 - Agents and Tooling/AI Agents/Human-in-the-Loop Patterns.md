---
title: Human-in-the-Loop Patterns
type: concept
aliases: [Human-in-the-Loop, HiTL, Human Oversight, Approval Patterns]
tags: [agents, human-in-the-loop, hitl, oversight, approval]
sources: ["09 - Human-in-the-Loop Patterns"]
created_index: 5
---

Human-in-the-loop (HiTL) patterns add human oversight to autonomous agents at critical points: before destructive actions, when confidence is low, when novel situations arise, or when value judgments are required. The four main patterns are approval gates (pause for a human yes/no before an action), interactive refinement (a human edits the agent's output before it's used), escalation (the agent autonomously decides to ask for help), and supervision (a human monitors and intervenes at will). HiTL is essential for production agents that touch production systems, send communications, or make irreversible changes; most agent frameworks support some form of it, and LangGraph's `interrupt_before` is the canonical implementation.

> [!info] TL;DR
> Human-in-the-loop (HiTL) patterns add human oversight to autonomous agents at critical points: before destructive actions, when confidence is low, when novel situations arise, or when value judgments are required. The four main patterns are **approval gates** (pause for human yes/no before an action), **interactive refinement** (human edits the agent's output before it's used), **escalation** (agent autonomously decides to ask for help), and **supervision** (human monitors and intervenes at will). HiTL is essential for production agents that touch production systems, send communications, or make irreversible changes. LangGraph's `interrupt_before` is the canonical implementation; most agent frameworks support some form of HiTL.

## Why human-in-the-loop

Autonomous agents are powerful but unreliable. LLMs hallucinate, misunderstand intent, and make wrong decisions. For low-stakes actions (search the web, read a file), this is fine — the cost of an error is small. For high-stakes actions (send an email, deploy code, delete data, transfer money), an error can be catastrophic.

HiTL inserts human judgment at the points where errors are most costly. The human doesn't review every action — that would defeat the purpose of automation. Instead, the human reviews:

- **Irreversible actions**: anything that can't be undone.
- **High-impact actions**: anything with significant consequences.
- **Novel situations**: anything the agent hasn't seen before.
- **Low-confidence actions**: anything the agent is unsure about.
- **Value judgments**: anything requiring human values (e.g., is this content appropriate?).

The result: most actions are automated (fast, cheap); critical actions are reviewed (safe). This is the production sweet spot for agent systems.

## The four HiTL patterns

### Approval gates

The agent pauses before a critical action and asks a human for approval. The human can approve, reject, or modify the action.

```python
def execute_with_approval(action, require_approval_for=None):
    """Execute an action, asking for approval if it's in the critical list."""
    if require_approval_for and action.type in require_approval_for:
        approval = request_human_approval(action)
        if approval.status == "rejected":
            return ActionResult(success=False, reason="Human rejected")
        if approval.status == "modified":
            action = approval.modified_action

    return action.execute()
```

The human interface is typically a chat message ("I'm about to send this email to alice@example.com. Approve?"), a web UI card showing the proposed action with Approve / Reject / Modify buttons, or an IDE integration popup in the editor.

Approval gates are the most common HiTL pattern. They're simple to implement and catch the majority of dangerous actions.

### Interactive refinement

The agent produces a draft output; the human edits it before it's used. This is appropriate when the output is a deliverable (email, document, code) where the agent's draft is a starting point but human polish is needed.

```python
def draft_and_refine(task):
    draft = agent.draft(task)
    edited = human_edit(draft)
    final = agent.finalize(edited)  # apply any post-processing
    return final
```

The human interface is a rich text editor with the draft pre-loaded. The human edits directly; the agent doesn't see the edits until finalize.

Interactive refinement is used in email drafting (the agent writes the draft; the human edits before sending), code generation (the agent writes code; the human reviews and edits in the IDE), and content creation (the agent writes the article; the human edits and publishes).

### Escalation

The agent autonomously decides to ask for help. This is appropriate when the agent encounters:

- **Ambiguity**: the request has multiple interpretations.
- **Missing information**: the agent needs data it doesn't have.
- **Low confidence**: the agent's confidence in its answer is below a threshold.
- **Out-of-scope**: the request is outside the agent's domain.

```python
def answer_with_escalation(question):
    response = agent.answer(question)
    if response.confidence < CONFIDENCE_THRESHOLD:
        return escalate_to_human(question, response, reason="low confidence")
    if response.out_of_scope:
        return escalate_to_human(question, response, reason="out of scope")
    return response
```

Escalation is more sophisticated than approval gates — the agent itself decides when to ask for help. This requires the agent to have reliable confidence estimates, which is an active research area.

### Supervision

A human monitors the agent's activity in real-time and can intervene at will. Unlike approval gates (which pause at predefined points), supervision allows intervention at any point.

Implementation rests on four pieces: an activity feed (a stream of the agent's actions, visible to the human), a pause button (the human can pause the agent at any time), an override (the human can override the agent's decisions), and direct chat (the human can message the agent with corrections).

Supervision is appropriate for high-stakes deployments (where any error is unacceptable), new agents (during initial deployment, before trust is established), and complex tasks (where the agent may need guidance).

## Implementation in LangGraph

[[LangGraph]] has first-class HiTL support via `interrupt_before`:

```python
from langgraph.graph import StateGraph, END

graph = StateGraph(AgentState)
graph.add_node("plan", plan_node)
graph.add_node("execute", execute_node)
graph.add_node("send_email", send_email_node)  # critical action

graph.set_entry_point("plan")
graph.add_edge("plan", "execute")
graph.add_edge("execute", "send_email")
graph.add_edge("send_email", END)

# Compile with interrupt before the critical node
app = graph.compile(
    interrupt_before=["send_email"],
    checkpointer=postgres_checkpointer,
)

# Run until the interrupt
result = app.invoke(input, config={"configurable": {"thread_id": "1"}})
# Agent has planned and executed, but paused before send_email

# Show the proposed email to the human
proposed_email = result["messages"][-1].content
approval = ask_human(proposed_email)

if approval:
    # Resume execution
    result = app.invoke(None, config={"configurable": {"thread_id": "1"}})
else:
    # Reject; agent doesn't send
    print("Email not sent")
```

The `checkpointer` persists state across the pause, so the agent can resume exactly where it left off. The `thread_id` identifies the conversation, so multiple users can have independent HiTL sessions.

## The HiTL decision framework

When designing an agent, decide for each action which pattern (if any) applies:

| Action Type                    | HiTL Pattern             |
|--------------------------------|--------------------------|
| Read-only (search, get)        | None                     |
| Reversible write (edit file)   | None (or supervision)    |
| Irreversible local (delete file)| Approval gate           |
| External communication (email) | Approval gate            |
| Production deployment          | Approval gate + supervision |
| High-value transaction          | Approval gate + second approver |
| Creative content               | Interactive refinement   |
| Ambiguous requests             | Escalation               |

The framework balances automation (speed, cost) with safety (oversight). Most actions are automated; the few that matter get human review.

## Production patterns

### Make pauses fast

When the agent pauses for approval, the human should be able to approve or reject in seconds. Long pauses (waiting for an email response) are frustrating and slow. Use push notifications (notify the human via Slack, mobile push, etc.), an inline UI (show the proposed action in the user's current context — chat, IDE), and quick actions (Approve / Reject buttons accessible in one click).

### Provide context

The human needs to understand what they're approving. Show what the agent will do (the action and its parameters), why (the agent's reasoning — chain-of-thought), what happens if rejected (what the agent will do instead), and the source data (the data the action is based on). Without context, the human is just clicking "Approve" without understanding — which provides no safety benefit.

### Allow modification

Binary approve/reject is limiting. Often the human wants to modify the action ("yes, but change the recipient to bob@"). Support modification of parameters (change the action's inputs), of output (change the agent's draft — interactive refinement), and redirection (tell the agent to do something different).

### Set timeouts on pauses

A pause that waits forever is a stuck agent. Set timeouts: a short timeout (5 minutes) rejects automatically and tells the user; a long timeout (24 hours) terminates the agent and reschedules. The right timeout depends on the use case — real-time chat needs short timeouts; batch processing can wait longer.

### Audit all HiTL decisions

Log every approval, rejection, and modification: who approved or rejected, what they approved or rejected, when they decided, and why (if they provided a reason). This is essential for compliance (especially in regulated industries) and for improving the agent — patterns of rejection reveal what the agent does wrong.

### Calibrate approval thresholds

Over time, analyze which approvals are routinely approved vs. rejected. If an action is approved 99% of the time, remove the approval gate (it's just friction). If an action is rejected 50% of the time, the agent is making bad proposals — improve the agent. This calibration is the key to scaling HiTL: start with many approval gates, then remove them as the agent earns trust.

### Support multiple approvers

For high-stakes actions (production deploys, large transactions), require approval from multiple humans. Sequential approval uses a first approver, then a second; parallel approval lets any of N approvers approve; a quorum requires K of N approvers. Multi-approver patterns add friction but reduce single-point-of-failure risk.

## Common pitfalls

### Approval fatigue

If every action requires approval, humans start rubber-stamping. They click "Approve" without reading, which provides no safety benefit. The solution is to minimize approval gates — only require approval for genuinely critical actions — and calibrate thresholds over time.

### Stale approvals

The agent pauses for approval; the human approves 3 days later. In the meantime, the situation has changed — the approved action is now wrong. The solution is to invalidate approvals after a timeout and re-evaluate the situation before executing.

### No audit trail

Without logging, you can't tell what was approved, by whom, or why. This is a compliance nightmare in regulated industries. The solution is to log everything — audit logs are non-negotiable for production HiTL.

### HiTL as a crutch

If the agent is so unreliable that every action needs approval, the agent isn't production-ready. HiTL should catch rare errors, not compensate for systematic unreliability. The solution is to improve the agent: HiTL is a safety net, not a substitute for capability.

### Friction in the wrong places

Requiring approval for read-only actions (search, get) adds friction without safety benefit. Reserve HiTL for actions that actually need it. Audit your approval gates and remove any that don't catch real errors.

## When to use each pattern

| Pattern | Use for | Don't use for |
|---|---|---|
| Approval gates | Irreversible actions, external communications, production changes | Read-only actions, reversible writes, low-stakes decisions |
| Interactive refinement | Creative content (emails, documents, code) where human polish adds value | Structured data extraction, classification, routing |
| Escalation | Ambiguous requests, low-confidence situations, out-of-scope queries | Clear, in-scope, high-confidence requests |
| Supervision | New agent deployments, high-stakes environments, complex tasks | Mature, well-tested agents doing routine work |

Most production agents combine approval gates for critical actions with supervision for new deployments.

## Interview questions

These distinctions come up frequently in interviews; the short-form answers are worth knowing cold.

**What are the four HiTL patterns and when do you use each?** (1) **Approval gates** — pause before critical actions (irreversible, external communication). (2) **Interactive refinement** — human edits the agent's draft (creative content, emails, code). (3) **Escalation** — agent autonomously asks for help (ambiguity, low confidence, out-of-scope). (4) **Supervision** — human monitors and intervenes at will (new deployments, high-stakes). Most production agents use approval gates for critical actions and supervision for new deployments.

**What is approval fatigue and how do you prevent it?** If every action requires approval, humans start rubber-stamping — clicking "Approve" without reading, which provides no safety benefit. Prevent it by minimizing approval gates (only for genuinely critical actions), calibrating thresholds (if an action is approved 99% of the time, remove the gate), and providing context (show what, why, and consequences so the human can make an informed decision).

**How does LangGraph implement HiTL?** Via `interrupt_before` — compile the graph with a list of nodes that should pause before execution. When the agent reaches an interrupt node, it pauses and persists state via the checkpointer. The human reviews the proposed action and resumes (approve) or stops (reject). The `thread_id` identifies the conversation, so multiple users can have independent HiTL sessions. The checkpointer ensures state survives across the pause.

**How do you calibrate approval thresholds over time?** Track approval/rejection rates per action type. If an action is approved 99% of the time, remove the approval gate (it's just friction). If rejected 50% of the time, the agent is making bad proposals — improve the agent. This calibration is the key to scaling HiTL: start with many gates, remove them as the agent earns trust. The goal is to approve only the actions that genuinely need human judgment.

**What is the difference between escalation and approval gates?** Approval gates: the agent always pauses at predefined points (before critical actions); the human knows when to expect a pause. Escalation: the agent autonomously decides to ask for help (when confidence is low, the request is ambiguous, or the situation is out-of-scope); the human doesn't know when the agent will escalate. Escalation is more sophisticated — it requires the agent to have reliable confidence estimates.

**Why is audit logging essential for HiTL?** Log every approval, rejection, and modification: who, what, when, why. This is essential for compliance (regulated industries require audit trails), improvement (patterns of rejection reveal what the agent does wrong), and accountability (if something goes wrong, you need to know who approved it). Without logging, HiTL is a black box — you can't tell if it's working or if humans are rubber-stamping.

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[Autonomous Agent Lifecycles]] — how HiTL fits into the agent lifecycle.
- [[Planner-Executor Pattern]] — planner-executor with HiTL gates.
- [[ReAct Pattern]] — the agent loop that approval gates guard.
- [[LangGraph]] — first-class HiTL support via `interrupt_before`.
- [[AutoGen]] — multi-agent systems with HiTL.
- [[CrewAI]] — HiTL via split runs.
- [[Reflection]] — agents that self-critique, reducing HiTL need.
- [[LLM Security and Prompt Injection]] — HiTL as a security measure.
- [[Gateway and Router Patterns]] — approval gates as middleware.

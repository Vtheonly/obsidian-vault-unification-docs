---
title: MCP Enterprise Integration
type: concept
aliases: [Enterprise MCP, MCP Gateway, Enterprise MCP Deployment]
tags: [mcp, enterprise, integration, production, gateway, multi-tenancy, audit-logging]
sources: ["04 - MCP Enterprise Integration"]
created_index: 32
---

Enterprise MCP deployments are not just "run an MCP server" — they require an MCP gateway that handles authentication, authorization, audit logging, multi-tenancy, policy enforcement, and server management. The reference architecture places the gateway between LLM clients and a fleet of curated MCP servers, providing a single control point for security and observability. Around that core sit server lifecycle management, integration with enterprise identity, SIEM and observability systems, and deployment patterns ranging from cloud-hosted to on-premises and hybrid.

> [!info] TL;DR
> Enterprise MCP deployments are not just "run an MCP server." They require an MCP gateway that handles authentication, authorization, audit logging, multi-tenancy, policy enforcement, and server management. The reference architecture places the gateway between LLM clients and a fleet of curated MCP servers, providing a single control point for security and observability.

## Why enterprise MCP is different

The basic MCP deployment model — a user runs an MCP server locally, the LLM client connects via stdio — works for individuals and small teams. It does not work for enterprises, for five compounding reasons:

- **No central control**: each user installs and configures their own MCP servers. Security teams cannot audit or restrict what's running.
- **No authentication**: local MCP servers run as the user, with full user privileges. No way to enforce least privilege.
- **No audit trail**: tool calls happen on the user's machine, with no central log. Incidents cannot be investigated.
- **No multi-tenancy**: each user has their own MCP server instances, with no shared state, caching, or rate limiting.
- **No policy enforcement**: no way to enforce "users in department X cannot call tool Y" or "PII cannot be sent to MCP server Z".

Enterprise integration requires an **MCP gateway** — a central service that sits between clients and servers, providing the missing controls.

## The reference architecture

```mermaid
graph TD
  subgraph Clients
    C1[User Client 1]
    C2[User Client 2]
    C3[Service Client]
  end
  subgraph MCP Gateway
    Auth[Auth: OAuth, SSO]
    Policy[Policy Engine]
    Audit[Audit Log]
    Router[Server Router]
    Cache[Response Cache]
    RateLimit[Rate Limiter]
  end
  subgraph MCP Server Fleet
    S1[Jira MCP Server]
    S2[GitHub MCP Server]
    S3[Internal DB MCP Server]
    S4[Custom Domain MCP Server]
  end
  C1 --> Gateway[Gateway]
  C2 --> Gateway
  C3 --> Gateway
  Gateway --> S1
  Gateway --> S2
  Gateway --> S3
  Gateway --> S4
```

### The gateway

The MCP gateway is the single entry point for all MCP traffic. It authenticates clients (OAuth 2.0, SSO integration), enforces policies (per-user, per-tenant, per-tool), logs every tool call for audit, routes requests to the appropriate MCP server, caches responses where safe, and rate-limits to prevent abuse.

### The server fleet

MCP servers run as separate processes (or containers), managed by the gateway. The fleet includes **curated third-party servers** (vetted, signed, and version-pinned), **internal servers** (built for internal systems such as proprietary databases and internal APIs), and **domain-specific servers** for specific use cases (e.g., a medical-records MCP server for a healthcare company). Servers are deployed, monitored, and updated by a platform team — not by individual users.

## Gateway components

### Authentication

The gateway's authentication component integrates with enterprise SSO (Okta, Azure AD, Google Workspace), issues short-lived tokens (OAuth 2.0 access tokens, typically 1-hour TTL), validates tokens on every request, and supports service-to-service authentication for non-user clients.

### Policy engine

The policy engine enforces rules like: "Users in the finance department can call the `accounting` MCP server's tools, but only during business hours"; "PII fields (SSN, credit card numbers) must be redacted before being sent to third-party MCP servers"; "Tool calls that modify production data require manager approval"; and "Rate limit: 100 tool calls per user per hour for high-risk tools." The policy engine is consulted on every request, and policies are versioned and auditable.

### Audit log

The audit log is an immutable record of who (user, client, IP), when (timestamp), what (server, tool, arguments, result), and why (the conversation context — optional but valuable). Audit logs are sent to a SIEM (Splunk, Datadog, Elastic Security) for retention and alerting, and are required for compliance in most regulated industries.

### Server router

The server router routes requests to the appropriate MCP server based on the tool being called (each tool belongs to a specific server), the user's permissions (some users may only access certain servers), the server's health (route around failed servers), and geographic location (for data residency requirements).

### Response cache

Some MCP tool calls are idempotent and cacheable: `read_file` (the file content doesn't change between calls, within a session), `list_issues` (the issue list is reasonably stable), and `search` (same query, same results, within a TTL). Caching reduces latency and load on backend systems. The cache must be per-user (or per-tenant) to prevent data leakage.

### Rate limiter

The rate limiter applies per-user, per-tool, per-server rate limits. This prevents abuse (a compromised account making thousands of calls), runaway agents (a prompt-injected model calling a tool in a loop), and backend overload (too many concurrent calls to a fragile legacy system).

## Multi-tenancy

For SaaS applications embedding MCP, multi-tenancy is critical. Each tenant has their own MCP server instances (or virtual partitions), tenant data is isolated at the database level, and rate limits, quotas, and audit logs are all per-tenant. There are three implementation options:

- **Server-per-tenant**: each tenant gets dedicated MCP server processes. Strongest isolation, highest overhead.
- **Shared servers with tenant filtering**: all tenants share server processes, but every tool call is filtered by tenant ID. Lower overhead, weaker isolation.
- **Hybrid**: small tenants share; large tenants get dedicated servers.

## Server lifecycle management

### Server onboarding

New MCP servers go through a defined onboarding process: (1) **security review** — code audit, vulnerability scan; (2) **policy definition** — what tools does it expose, who can use them, what are the rate limits; (3) **test deployment** — deploy in staging, run integration tests; (4) **production deployment** — deploy with monitoring, alerting, and rollback procedures.

### Server versioning

Servers are versioned with semver. New versions go through the same onboarding process as new servers, old versions remain available during a transition period, and breaking changes require migration plans.

### Server health monitoring

The platform tracks latency, error rate, and throughput per server, with automatic failover to healthy instances and alerting on degradation.

### Server decommissioning

Decommissioning a server means notifying users in advance, providing a migration path (alternative servers or direct API access), and archiving audit logs.

## Integration with enterprise systems

### Identity provider

The gateway integrates with the enterprise IdP (Okta, Azure AD) for SSO. Users authenticate with their enterprise credentials; there are no separate MCP accounts.

### SIEM

Audit logs are streamed to the SIEM (Splunk, Elastic, Datadog) for security monitoring and compliance retention.

### Observability stack

Metrics (Prometheus, Datadog) cover per-server and per-tool latency and error rates; traces (OpenTelemetry) provide end-to-end request tracing across the gateway and servers; logs (Loki, ELK) are structured with trace IDs.

### Policy engine integration

For complex policy enforcement, the gateway integrates with a dedicated policy engine: **OPA (Open Policy Agent)** with rego-based policies integrated as a sidecar, **Cedar** (Amazon), a policy language designed for authorization, or a **custom** engine — many enterprises build custom policy engines tailored to their compliance requirements.

### API gateway

The MCP gateway may sit behind (or alongside) a general-purpose API gateway (Kong, Apigee, AWS API Gateway) that handles TLS termination, WAF, and rate limiting for all enterprise APIs. The MCP gateway is a specialization of the broader [[Gateway and Router Patterns|gateway and router]] pattern.

## Deployment patterns

### Cloud-hosted

The MCP gateway and server fleet run in the cloud (AWS, GCP, Azure); clients connect over HTTPS. Pro: scalable, managed, easy to update. Con: data leaves the enterprise network, a compliance concern for some industries.

### On-premises

The MCP gateway and servers run on enterprise infrastructure; clients connect via internal network or VPN. Pro: data stays in the enterprise with full control. Con: scaling is the enterprise's responsibility, and updates are slower.

### Hybrid

The gateway runs in the cloud; some servers are on-premises (for sensitive systems) and some in the cloud (for SaaS integrations). Pro: balances control and convenience. Con: more complex to operate.

## Common pitfalls

### No central gateway

Each user runs their own MCP servers — no audit, no policy enforcement, no central control. This is fine for individuals but unacceptable for enterprises.

### No server vetting

Users install arbitrary third-party MCP servers. A malicious server can exfiltrate data or execute arbitrary code. Always vet and approve servers centrally.

### No audit log

Tool calls happen with no record. Incidents cannot be investigated; compliance is violated. Always log centrally.

### No rate limiting

A compromised or runaway agent calls tools thousands of times per second and backend systems fail. Always rate-limit.

### No multi-tenant isolation

Tenant A's data leaks to Tenant B because the gateway doesn't enforce tenant scoping. Use row-level security or per-tenant server instances.

### Trusting client-side security

Security enforced in the client (e.g., the LLM application) can be bypassed by a modified client. Always enforce security in the gateway.

## The state of enterprise MCP (2025–2026)

Enterprise MCP is an emerging product category. Several vendors offer managed MCP gateways (Cloudflare, Stripe, and others have announced MCP-related products); open-source gateways such as `mcp-gateway` provide self-hosted alternatives; the MCP spec continues to add enterprise features (server discovery, OAuth flows, structured permissions); and large enterprises are piloting MCP for internal tool integration, with production deployments still rare but growing.

For AI engineers in 2026, enterprise MCP is a "watch this space" technology. The patterns are clear, but the tooling is still maturing. Most production deployments today are custom-built on top of open-source MCP servers, with the gateway implemented internally.

## Modern developments (2025–2026)

### Enterprise MCP gateways become a product category

What was a "watch this space" in 2024 became a real product category in 2025–2026:

- **Cloudflare AI Gateway with MCP support** — global edge-deployed gateway with built-in caching, rate limiting, auth, and observability for MCP tool calls.
- **AWS Bedrock Agent Gateway** — managed gateway for Bedrock agents, integrating with IAM, CloudTrail, and VPC policies.
- **Pulumi MCP Hub** — multi-cloud registry with policy-as-code (Pulumi program) for tool authorization.
- **Microsoft Azure AI Foundry MCP Gateway** — enterprise-grade gateway with Entra ID integration.
- **Kong AI Gateway MCP plugin** — adds MCP support to Kong's existing API gateway, letting teams reuse their API management infrastructure.

These gateways share a common pattern: a **reverse proxy** in front of MCP servers that adds auth, policy, observability, and caching without modifying the servers themselves.

### MCP-as-a-service offerings

Major SaaS vendors now ship hosted MCP servers for their products: **GitHub MCP Server** (hosted by GitHub — read repos, issues, PRs; write issues with policy), **Slack MCP Server** (hosted by Slack — search messages, send messages with audit log), **Notion MCP Server** (hosted by Notion — query databases, create pages), **Salesforce MCP Server** (hosted by Salesforce — query CRM records with row-level security), and **ServiceNow MCP Server** (hosted by ServiceNow — query incidents, create tickets). This shifts the burden of running servers from the enterprise to the vendor, who already maintains the underlying API. Enterprise customers connect to these via the MCP gateway with their existing SSO.

### Spec evolution — 2025-06 and 2025-11 revisions

Key enterprise-relevant spec changes include **OAuth 2.1 + PKCE** standardized for auth (replacing ad-hoc per-server schemes), a **server discovery protocol** (clients can fetch a manifest of available servers from a registry; the gateway returns the list dynamically based on the user's role), **resource subscriptions** (push notifications enable real-time collaboration patterns), a **composability spec (2025-11)** with formal declaration of inter-server dependencies, **structured audit log fields** (every tool call emits SIEM-compatible events), and **elicitation** (servers can request information from users mid-operation, e.g., a 2FA code or confirmation). These revisions closed most enterprise gaps; the 2026 spec roadmap focuses on **streaming tool results**, **batch tool calls**, and **multi-region failover**.

### Multi-region and DR patterns

Global enterprises need MCP infrastructure that survives region failures. The pattern: deploy MCP gateways in 3+ regions (us-east, eu-west, ap-southeast); use **anycast routing** (Cloudflare, AWS Global Accelerator) to route users to the nearest healthy region; rely on MCP servers in each region replicating state via the underlying service (e.g., the Slack API is already multi-region); for stateful MCP servers (rare — most are stateless proxies), use **active-active with eventual consistency** or **active-passive with DNS failover**; and replicate audit logs globally to a single SIEM rather than depending on regional SIEMs.

### Private MCP registries

Enterprises don't want to rely on public marketplaces for security reasons. The pattern is a **private registry** (often built on Artifactory or Harbor) that hosts vetted MCP server binaries and Docker images, requires code review plus a security scan before publishing, pins versions (no auto-update from upstream), publishes an SBOM with every release, and integrates with the corporate SSO for read access. Internal developers install MCP servers from the private registry only; the gateway refuses connections to non-registry servers.

### Cost allocation and chargeback

For enterprises running MCP at scale, cost attribution matters. The gateway tags every tool call with `user_id`, `tenant_id`, and `team_id` (from SSO groups), a `cost_usd` estimate based on the LLM tokens consumed by the call (if sampling was used) plus the underlying API cost, and a `project_id` that is user-declared at session start. Chargeback reports allocate costs to teams monthly. This pattern is essential for cost-sensitive enterprises (banks, healthcare) where MCP usage can balloon if unmonitored.

## Reference architecture — enterprise MCP deployment

```mermaid
graph TD
    User[End User Browser] -->|HTTPS+OAuth| Gateway[MCP Gateway<br/>Cloudflare/AWS/Pulumi]
    Gateway -->|AuthN| SSO[Entra ID / Okta]
    Gateway -->|Policy| PEP[Policy Engine<br/>OPA/Cedar]
    Gateway -->|Audit| SIEM[Splunk / Datadog]
    Gateway -->|Cache| Redis[(Redis Cluster)]
    Gateway --> S1[GitHub MCP<br/>hosted by GitHub]
    Gateway --> S2[Slack MCP<br/>hosted by Slack]
    Gateway --> S3[Internal CRM MCP<br/>on-prem]
    Gateway --> S4[Internal Docs MCP<br/>on-prem]
    S3 -->|VPC peering| CRMDB[(CRM DB)]
    S4 -->|mTLS| DocsDB[(Docs DB)]
    Gateway -->|Metrics| Prom[Prometheus]
    User -->|LLM calls| LLM[LLM Provider<br/>OpenAI/Anthropic]
```

The key components of this architecture: the **gateway** is the single ingress point — all tool calls flow through it; **SSO** handles authentication (no per-server auth); the **policy engine** (OPA or AWS Cedar) makes per-call authorization decisions; the **SIEM** ingests structured audit logs for compliance and anomaly detection; **Redis** caches tool results (TTL-based) to reduce load on upstream servers; **internal MCP servers** connect via VPC peering or mTLS and are never exposed to the public internet; **hosted MCP servers** (GitHub, Slack) are accessed over the public internet with OAuth; and the **LLM provider** is separate from MCP infrastructure — the gateway is LLM-agnostic.

## Worked example — multi-tenant gateway policy

The following example combines a declarative Cedar policy with the gateway request handler that enforces it:

```python
# Cedar policy for MCP authorization
CEDAR_POLICY = """
// Engineers can call read tools on their own team's resources
permit (
    principal in Role::"engineer",
    action == Action::"tool_call",
    resource == Resource::"github__get_issue"
)
when {
    principal.team == resource.args.owner_team
};

// Senior engineers can create issues in their team's repos
permit (
    principal in Role::"senior_engineer",
    action == Action::"tool_call",
    resource == Resource::"github__create_issue"
)
when {
    principal.team == resource.args.repo_team
};

// No one can delete repos via MCP
forbid (
    principal,
    action == Action::"tool_call",
    resource == Resource::"github__delete_repo"
);

// Cross-team slack messages require approval
permit (
    principal,
    action == Action::"tool_call",
    resource == Resource::"slack__send_message"
)
when {
    principal.team != resource.args.channel_team
}
unless {
    context.has_approval
};
"""

# Gateway integration
from cedar import Authorizer

auth = Authorizer(policy=CEDAR_POLICY)

async def gateway_handler(request):
    user = await sso.authenticate(request.headers['Authorization'])
    tool = request.json['tool']
    args = request.json['args']

    decision = auth.evaluate(
        principal=user.to_cedar(),
        action="tool_call",
        resource={"id": tool, "args": args},
        context={"has_approval": await check_approval(user, tool, args)},
    )

    if decision == 'forbid':
        audit_log(user, tool, args, effect='deny')
        return JSONResponse({'error': 'denied'}, status=403)

    if decision == 'needs_approval':
        approval = await request_user_approval(user, tool, args)
        if not approval.granted:
            return JSONResponse({'error': 'approval denied'}, status=403)
        audit_log(user, tool, args, effect='approved', approver=approval.approver)

    # Cache check
    cache_key = f"{user.tenant}:{tool}:{hash_args(args)}"
    cached = await redis.get(cache_key)
    if cached and tool.startswith('get_'):
        audit_log(user, tool, args, effect='cache_hit')
        return JSONResponse(cached)

    # Forward to upstream
    result = await forward_to_upstream(tool, args, user)
    await redis.setex(cache_key, ttl=300, value=result)

    audit_log(user, tool, args, effect='ok',
              cost_usd=estimate_cost(result), duration_ms=...)
    return JSONResponse(result)
```

This example demonstrates: (1) declarative policy in Cedar (readable, auditable, version-controlled); (2) SSO-based user identity; (3) per-call authorization with approval escalation; (4) caching for read-only tools; (5) cost and duration tracking for chargeback.

## Common failure modes

| Symptom                                | Likely Cause                                  | Fix                                                          |
|----------------------------------------|-----------------------------------------------|--------------------------------------------------------------|
| Tool latency 10x in production         | No caching; every call hits upstream          | Cache GET-style tools in Redis with TTL                      |
| Cost spikes at month-end               | No per-team cost attribution                  | Tag every call with team_id; weekly chargeback reports       |
| Cannot revoke access quickly            | Tokens cached too long; no revocation flow    | Short token TTL (15min); revocation list checked every call  |
| Compliance audit fails                 | Audit logs missing user_id or args_hash       | Mandatory structured logging; CI test for required fields    |
| Single region goes down, all users fail| Single-region gateway; no failover            | Multi-region gateway with anycast routing; health checks     |
| Tool call volume 100x expected         | LLM loops on a failing tool                   | Per-user-per-tool rate limit; circuit breaker on failures    |
| Internal server unreachable from cloud | No VPC peering; public-only connectivity      | PrivateLink / VPC peering; mTLS for internal MCP servers     |
| New MCP server takes weeks to deploy   | Manual security review bottleneck             | Automated SAST + SBOM in CI; pre-approved server templates   |
| Cross-tenant data exposure             | Cache key omits tenant_id                     | Cache key MUST include tenant_id + user_id                   |
| Vendor outage breaks all agents        | Synchronous dependency on vendor MCP          | Fallback to cached results; degrade gracefully               |

## Interview questions

These distinctions come up frequently in interviews; the short-form answers are worth knowing cold.

**Walk me through the architecture of an enterprise MCP deployment.** Five layers: (1) **end user** accesses via SSO-authenticated browser/desktop client; (2) **MCP gateway** (Cloudflare, AWS, Pulumi) is the single ingress — handles auth, policy, caching, audit; (3) **SSO provider** (Entra ID, Okta) authenticates users and provides identity claims; (4) **policy engine** (OPA, Cedar) evaluates per-call authorization based on user role, tool, and args; (5) **MCP servers** (hosted by SaaS vendors or internal) execute the actual tool calls. Audit logs flow to a SIEM; metrics flow to Prometheus. Internal servers connect via VPC peering; external servers via OAuth over the public internet.

**How do you handle multi-tenant isolation in MCP?** Four layers: (1) **auth-time** — every user authenticates via SSO which establishes their `tenant_id`; (2) **policy-time** — Cedar/OPA policies check `principal.tenant == resource.args.tenant` for every tool call; (3) **runtime** — cache keys include `tenant_id`; upstream API calls include an `X-Tenant-ID` header; (4) **audit-time** — every audit log entry includes `tenant_id`; SIEM queries can detect cross-tenant access attempts. Defense in depth: even if one layer fails, others catch the leak.

**How would you migrate from direct-API-access to MCP-based tool calling?** Phased rollout: (1) **inventory existing tool integrations** — what tools, what auth, what volumes; (2) **stand up the MCP gateway** in parallel with the existing integration; (3) **wrap existing APIs as MCP servers** (the "shim" pattern — minimal logic, just protocol translation); (4) **pilot with one team** — route their agents through MCP; compare latency, error rates, cost; (5) **gradually migrate** — per-team cutover with rollback capability; (6) **decommission the old integration** once 100% on MCP. Expect 3–6 months for a mid-size enterprise. The MCP gateway pays for itself in observability and policy gains even before full migration.

**What's the cost model for enterprise MCP?** Three cost components: (1) **gateway infrastructure** — gateway servers, Redis cache, SIEM ingestion; typically \$5–20k/month for mid-size; (2) **MCP server execution** — most are free (hosted by the SaaS vendor) but internal servers cost compute plus the underlying API cost; (3) **LLM cost** — only if sampling is used; otherwise LLM cost sits in the agent layer, not the gateway. Chargeback pattern: tag every call with `team_id`, generate monthly reports, allocate costs. Most enterprises find MCP cost is 5–10% of total LLM cost — the dominant cost is always the LLM.

**How do you handle MCP server outages?** Layered resilience: (1) **circuit breaker** — if a server fails >5% in 1 min, stop sending traffic for 30s; (2) **cached results** — for read-only tools, serve stale cached data with a `stale=true` flag; (3) **fallback tools** — if `slack__send_message` is down, queue the message and notify the user; (4) **multi-region** — the gateway routes to healthy regions; (5) **vendor SLAs** — for hosted servers, hold vendors to SLAs (99.9% typical); (6) **degraded mode** — the agent should detect tool outage and switch to a no-tool workflow (e.g., "I can't access Slack right now; let me draft the message for you to send manually"). The agent's prompt should include fallback behavior.

**How do you ensure MCP compliance with regulations like SOX, HIPAA, GDPR?** Per-regulation patterns: (1) **SOX** — every financial-data tool call must produce an immutable audit log retained 7 years; quarterly review of access patterns. (2) **HIPAA** — PHI must not leave the covered entity's network; internal MCP servers only; PHI in tool args must be encrypted at rest and in transit; a BAA is required with any SaaS MCP vendor. (3) **GDPR** — every memory/tool call tagged with `user_id`; right-to-be-forgotten requests cascade through all MCP audit logs (delete or anonymize); data residency — EU users' tool calls stay in EU regions. The gateway's structured audit logs are the compliance backbone; without them, MCP is unusable in regulated industries.

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[MCP Overview]] — the architecture being integrated.
- [[MCP Components]] — what gets deployed at scale.
- [[MCP Security]] — security underlies every enterprise pattern.
- [[Enterprise Multi-Agent Architectures]] — multi-agent plus MCP at enterprise scale.
- [[Autonomous Agent Lifecycles]] — agents with MCP tools over long lifecycles.
- [[Human-in-the-Loop Patterns]] — approval escalation for policy-gated tool calls.
- [[Gateway and Router Patterns]] — the MCP gateway is a specialization of the API gateway pattern.
- [[Guardrails]] — gateway-level guardrails complement MCP policies.
- [[Reference Production Architectures]] — where MCP fits in the production stack.
- [[Production Monitoring]] — observability for MCP tool calls.
- [[Cost Optimization]] — chargeback and cost allocation.
- [[Build an MCP Server]] — implementing the servers the gateway fronts.
- [[Production AI Stack]]
- [[Inference and Production MOC]]

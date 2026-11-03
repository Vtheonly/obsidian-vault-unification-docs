---
title: MCP Overview
type: concept
aliases: [MCP, Model Context Protocol, MCP Protocol]
tags: [mcp, model-context-protocol, tools, anthropic, agentic, json-rpc, client-server]
sources: ["01 - MCP Overview"]
created_index: 33
---

MCP (Anthropic, 2024) is an open protocol for connecting LLMs to external tools, data sources, and services, standardizing tool/function calling across models and applications. It defines a client-server architecture in which host applications embed MCP clients that talk to MCP servers over JSON-RPC 2.0, with servers exposing three capability types: tools, resources, and prompts. By 2026 it is increasingly the standard for agentic tool integration, supported by Claude Desktop, Cursor, Cline, Continue, and major agent frameworks.

> [!info] TL;DR
> MCP (Anthropic, 2024) is an open protocol for connecting LLMs to external tools, data sources, and services. Standardizes "tool/function calling" across models and applications. Increasingly the standard for agentic tool integration in 2026. This note covers the problem MCP solves, the architecture, the three resource types (tools, resources, prompts), the protocol details, transports, security model, lifecycle, comparison to function calling, production patterns, and the broader ecosystem.

## The problem MCP solves

Before MCP, every LLM application that needed tools wrote custom integrations: custom OpenAI function calling schemas, custom Anthropic tool use, custom local LLM tool formats, and custom RAG pipeline connections. This produced an N×M integration problem: N LLM clients × M tools = N×M custom integrations. Each new model required rewriting tool integrations for every tool. Each new tool required integration code for every model.

The result was that tools couldn't be shared across applications, switching LLM providers required rewriting tool integrations, each new tool needed app-specific code, tool developers had to support multiple formats, and application developers had to maintain many integrations.

MCP defines a standard protocol so any MCP-compatible tool can be used by any MCP-compatible client. This reduces N×M to N+M: each tool implements MCP once; each client implements MCP once. The protocol is the bridge.

## The MCP architecture

```mermaid
graph TB
  Host[Host Application<br/>Claude Desktop, Cursor, etc.]
  Host --> Client1[MCP Client 1]
  Host --> Client2[MCP Client 2]
  Host --> Client3[MCP Client 3]
  
  Client1 -.->|stdio<br/>JSON-RPC| Server1[MCP Server: GitHub]
  Client2 -.->|stdio<br/>JSON-RPC| Server2[MCP Server: Filesystem]
  Client3 -.->|HTTP/SSE<br/>JSON-RPC| Server3[MCP Server: Database<br/>remote]
  
  Server1 --> API1[GitHub API]
  Server2 --> FS[Local filesystem]
  Server3 --> DB[(Postgres)]
  
  Host --> LLM[LLM<br/>Claude, GPT, etc.]
  LLM -.->|tool calls| Host
```

### Components

The architecture has four components. The **host** is the application (Claude Desktop, Cursor, a custom app); it contains one or more MCP clients and an LLM. The **client** lives in the host and connects to one server — each client manages one server connection, and the host may have multiple clients (one per server). The **server** is a process exposing tools/resources/prompts via MCP; servers can be local (a subprocess of the host) or remote (an HTTP service). The **LLM** is the model that decides when to call tools — the LLM doesn't directly talk to MCP; it talks to the host, which routes tool calls to the appropriate client.

### Communication pattern

The message flow is: (1) the host starts an MCP server (or connects to a remote one); (2) the client sends an `initialize` request to negotiate capabilities; (3) the client calls `list_tools`, `list_resources`, `list_prompts` to discover what the server offers; (4) the host aggregates tools from all servers and presents them to the LLM; (5) when the LLM emits a tool call, the host routes it to the appropriate client; (6) the client sends `call_tool` to the server, which executes and returns the result; (7) the host passes the result back to the LLM as a tool response.

This decoupling means servers are model-agnostic (they don't care which LLM is calling), hosts are tool-agnostic (they don't care which server provides a tool), and LLMs are transport-agnostic (they don't care if a tool is local or remote).

## The three resource types

MCP defines three types of capabilities a server can expose — tools, resources, and prompts — and each serves a different purpose.

### Tools

Tools are functions the LLM can call — like [[Function Calling|function calling]], but standardized:

```json
{
  "name": "search_issues",
  "description": "Search GitHub issues in a repo",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo": {"type": "string", "description": "owner/repo format"},
      "query": {"type": "string", "description": "search query"},
      "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"}
    },
    "required": ["repo"]
  }
}
```

Tools are the primary way MCP extends LLM capabilities; the LLM decides when to call a tool, based on the tool's name and description. Their key characteristics:

- **Model-invoked**: the LLM chooses to call the tool (vs. resources, which are user/developer-invoked).
- **Side-effecting**: tools can modify state (write a file, send an email, deploy code).
- **Asynchronous**: tool calls return results; the LLM waits for the response.
- **Schema-validated**: the input schema is JSON Schema; the server validates inputs.

### Resources

Resources are read-only data sources the LLM can access: file contents, database rows, API responses, and logs, metrics, configuration. Resources have URIs (`file:///path/to/file`, `github://repo/issue/123`, `db://users/42`); the client can list available resources and read specific ones by URI.

Their key characteristics: **user/developer-invoked** (resources are typically attached to the conversation by the user, e.g., "analyze this file", or programmatically by the host), **read-only** (resources don't have side effects, vs. tools, which can), **URI-addressable** (each resource has a unique URI; clients can read by URI), and **subscribable** (clients can subscribe to resource changes, e.g., a log file that updates).

Resources are useful for providing context without explicit tool calls. For example, a file system MCP server exposes `file:///path/to/file` resources; the host can attach relevant files to the conversation automatically.

### Prompts

Prompts are pre-defined prompt templates the user can invoke, like slash commands: `/summarize_issue` (fetches an issue, summarizes it), `/review_pr` (fetches a PR, reviews it), and `/explain_error` (reads an error log, explains the cause). Prompts are parameterized templates — when the user invokes a prompt, the server fills in the template (possibly using tools to fetch data) and returns a complete message for the LLM.

Their key characteristics: **user-invoked** (prompts are triggered by the user, e.g., typing `/summarize_issue 123`), **templated** (prompts have arguments, e.g., issue number, file path), **server-side composition** (the server can use its tools internally to compose the prompt, e.g., fetch the issue, then format the prompt with its content), and **reusable** (prompts codify workflows that users invoke repeatedly).

Prompts bridge the gap between tools (LLM-invoked) and resources (developer-invoked). They let users trigger complex workflows with a single command.

## Protocol details

MCP uses JSON-RPC 2.0 as the message format. Messages are request/response or notification.

### Message format

A request looks like:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_issues",
    "arguments": {"repo": "anthropics/anthropic-sdk-python", "query": "bug"}
  }
}
```

And its response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {"type": "text", "text": "Found 3 issues:\n1. ..."}
    ]
  }
}
```

### Core methods

| Method                  | Direction         | Purpose                                |
|-------------------------|-------------------|----------------------------------------|
| `initialize`            | Client → Server   | Negotiate capabilities, exchange info  |
| `initialized`           | Client → Server   | Notification: initialization complete  |
| `tools/list`            | Client → Server   | List available tools                   |
| `tools/call`            | Client → Server   | Call a specific tool                   |
| `resources/list`        | Client → Server   | List available resources               |
| `resources/read`        | Client → Server   | Read a resource by URI                 |
| `resources/subscribe`   | Client → Server   | Subscribe to resource changes          |
| `prompts/list`          | Client → Server   | List available prompts                 |
| `prompts/get`           | Client → Server   | Get a specific prompt with arguments   |
| `notifications/*`       | Server → Client   | Server-initiated notifications         |

### Capability negotiation

During initialization, client and server exchange capabilities. The client's `initialize` request:

```json
{
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "experimental": {},
      "sampling": {},
      "roots": {"listChanged": true}
    },
    "clientInfo": {"name": "Claude Desktop", "version": "1.0.0"}
  }
}
```

The server responds with its capabilities:

```json
{
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "tools": {"listChanged": true},
      "resources": {"subscribe": true, "listChanged": true},
      "prompts": {"listChanged": true}
    },
    "serverInfo": {"name": "github-mcp-server", "version": "1.2.0"}
  }
}
```

This negotiation lets clients and servers with different feature sets interoperate. A server that doesn't support resource subscriptions simply doesn't advertise that capability; the client knows not to use it.

## Transports

MCP supports multiple transports.

### stdio (local)

The server is a subprocess of the host. Communication is via stdin/stdout (JSON-RPC messages). This is the default for local tools. Pros: simple, fast, no network overhead. Cons: the server must run on the same machine as the host. Use cases: local file system, local databases, local development tools.

### HTTP + SSE (remote)

The server is a remote HTTP service. Communication is via HTTP POST for requests and Server-Sent Events (SSE) for responses/notifications. Pros: the server can run anywhere; multiple hosts can share a server. Cons: adds network latency; needs authentication. Use cases: shared enterprise tools, cloud services, multi-user environments.

### WebSocket (future)

The spec includes WebSocket as a transport, useful for bidirectional real-time communication. Less commonly implemented in 2026.

### Transport-agnostic protocol

The protocol is transport-agnostic: the same JSON-RPC messages work over stdio, HTTP+SSE, or WebSocket. This lets servers be deployed locally or remotely without changing the tool implementation.

## Security model

MCP servers can execute arbitrary code, access files, and make network calls — security is critical. The full treatment lives in [[MCP Security]]; the core model is summarized here.

### Trust model

Local servers (stdio) are trusted by default — the user installed them — but you should still validate inputs and outputs. Remote servers (HTTP) are untrusted by default and require authentication (OAuth 2.1) and HTTPS.

### Authentication

For remote servers, MCP supports OAuth 2.1: the server exposes an OAuth endpoint; the client obtains an access token (via a user consent flow); the client includes the token in the `Authorization: Bearer ...` header; and the server validates the token before processing requests. For local servers, authentication is typically implicit — the user running the host is the user accessing the server.

### Permissions

MCP supports per-tool permissions. The host can prompt the user before calling a tool with side effects, restrict which tools the LLM can see (filtering `list_tools` results), and log all tool calls for audit. This is especially important for tools that modify state (write files, send emails, deploy code) — see [[Human-in-the-Loop Patterns]] for the approval gate pattern.

### Sandboxing

For untrusted servers, run in a sandbox: a Docker container with restricted filesystem and network, a separate user account with limited permissions, or AppArmor / SELinux profiles.

### Tool code execution

Tools that execute LLM-generated code (e.g., a Python REPL tool) are especially dangerous. Use Docker containers with resource limits (CPU, memory, network), no access to the host filesystem, no access to host environment variables, and timeouts to prevent infinite loops.

## Lifecycle

The MCP lifecycle has distinct phases.

### Discovery

The host discovers available MCP servers. This may be via a configuration file (Claude Desktop's `claude_desktop_config.json`), dynamic discovery (mDNS, service registry), or user-installed extensions.

### Initialization

For each server, the host creates a client and sends `initialize`. They negotiate protocol version and capabilities.

### Capability listing

The client calls `tools/list`, `resources/list`, `prompts/list` to discover what the server offers. The host aggregates these across all servers.

### Tool presentation

The host presents aggregated tools to the LLM (as function definitions). The LLM decides when to call tools.

### Tool execution

When the LLM emits a tool call: the host routes it to the appropriate client (based on tool name); the client sends `tools/call` to the server; the server executes and returns the result; the host passes the result to the LLM.

### Resource and prompt invocation

For resources and prompts, the user or host triggers invocation (not the LLM). The server returns content that's added to the conversation.

### Shutdown

When the host exits or the user removes a server: the client sends a shutdown notification; the server cleans up resources; for stdio the subprocess terminates; for HTTP the connection closes.

## MCP vs function calling

[[Function Calling|Function calling]] (OpenAI, Anthropic) and MCP solve related but distinct problems:

| Aspect              | Function Calling                  | MCP                                |
|---------------------|-----------------------------------|------------------------------------|
| Scope               | Per-request, per-app              | Cross-app, cross-model             |
| Standard            | Vendor-specific                   | Open protocol                      |
| Tool discovery      | App provides at request time      | Server advertises; client discovers|
| Tool execution      | App executes                      | Server executes                    |
| State               | Stateless                         | Server can be stateful             |
| Cross-app reuse     | No                                | Yes                                |
| Resources/prompts   | No (just tools)                   | Yes                                |
| Transport           | N/A (in-process)                  | stdio, HTTP+SSE, WebSocket         |

MCP doesn't replace function calling — it standardizes how tools are exposed and discovered. Under the hood, MCP servers receive function-call requests and execute them; the host translates between the LLM's function-calling format and MCP's `tools/call`.

### When to use which

Use function calling directly when you have a small, app-specific set of tools; you don't need cross-app reuse; and you want maximum control. Use MCP when you want tools reusable across apps; you're building an ecosystem of tools; you want to support multiple LLM providers; or you need resources or prompts (not just tools). Most production agent systems will use both: MCP for reusable tools, function calling for app-specific tools.

## Worked example — an MCP server

```python
from mcp.server import Server
from mcp.types import Tool, Resource, Prompt
import json

server = Server("github-mcp-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_issues",
            description="Search GitHub issues in a repo",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "owner/repo format"},
                    "query": {"type": "string"},
                    "state": {"type": "string", "enum": ["open", "closed", "all"], "default": "open"}
                },
                "required": ["repo"]
            }
        ),
        Tool(
            name="create_issue",
            description="Create a new GitHub issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo": {"type": "string"},
                    "title": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["repo", "title"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "search_issues":
        result = await github_search_issues(**arguments)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    elif name == "create_issue":
        # This is a side-effecting tool — host may want approval
        result = await github_create_issue(**arguments)
        return {"content": [{"type": "text", "text": f"Created issue #{result['number']}"}]}

@server.list_resources()
async def list_resources():
    return [
        Resource(
            uri="github://anthropics/anthropic-sdk-python/issues",
            name="Open issues for anthropic-sdk-python",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri):
    if uri.startswith("github://"):
        # Parse repo and resource type from URI
        parts = uri[len("github://"):].split("/")
        repo = "/".join(parts[:2])
        resource_type = parts[2] if len(parts) > 2 else None
        if resource_type == "issues":
            issues = await github_list_issues(repo)
            return json.dumps(issues)
    raise ValueError(f"Unknown URI: {uri}")

@server.list_prompts()
async def list_prompts():
    return [
        Prompt(
            name="summarize_issue",
            description="Fetch and summarize a GitHub issue",
            arguments=[
                {"name": "repo", "description": "owner/repo", "required": True},
                {"name": "issue_number", "description": "Issue number", "required": True}
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name, arguments):
    if name == "summarize_issue":
        repo = arguments["repo"]
        issue_num = arguments["issue_number"]
        issue = await github_get_issue(repo, issue_num)
        return {
            "description": f"Summarize issue #{issue_num} in {repo}",
            "messages": [
                {"role": "user", "content": f"Please summarize this GitHub issue:\n\nTitle: {issue['title']}\nBody: {issue['body']}"}
            ]
        }

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    async def main():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    asyncio.run(main())
```

This server exposes 2 tools (`search_issues`, `create_issue`), 1 resource (`github://...issues`), and 1 prompt (`/summarize_issue`). A step-by-step build of a server like this is covered in [[Build an MCP Server]].

## MCP clients

Any application can be an MCP client: **Claude Desktop** (Anthropic, first-party support), **Cursor** (AI code editor, MCP for tools), **Cline**, **Continue**, and **Roo Code** (code assistants with MCP), **LangGraph / LangChain** (MCP integration for agents), and **custom applications** built on the MCP SDK (Python, TypeScript, Rust, Go). The MCP SDK handles the protocol details — JSON-RPC, capability negotiation, transport — so application developers focus on tool implementation.

## Why this matters for AI

MCP is becoming **the** standard for agentic tool integration; major AI apps (Claude, Cursor, Cline) support it. For tool builders, MCP means **write once, run in any MCP-compatible app** — no per-app integrations. For AI engineers, MCP provides a clean separation: your agent code talks to MCP servers; the servers handle tool execution. The protocol is open and vendor-neutral, avoiding lock-in. MCP enables an ecosystem of reusable tools — a GitHub MCP server can be used by Claude, Cursor, and any other MCP-compatible app without modification. And resources and prompts (beyond just tools) enable richer interactions: context attachment and workflow automation.

## Production implications

For tool builders: expose your tool as an MCP server so any MCP-compatible client can use it. For agent builders: use MCP clients to consume tools rather than writing custom tool integrations. On **security**, MCP servers can run arbitrary code — only run servers you trust, sandbox untrusted ones, and use OAuth for remote servers. On **authentication**, MCP supports OAuth for remote servers; use it for any sensitive tool. On **performance**, local (stdio) MCP servers are fast while remote (HTTP) add latency — cache where possible. On **tool versioning**, when you update a tool's schema, old clients may break; version your server and document breaking changes. On **tool selection**, don't expose 100 tools to the LLM — it gets confused; expose the relevant subset, or use a tool router. On **audit logging**, log all tool calls (name, arguments, result, timestamp) for compliance and debugging. On **rate limiting**, rate-limit shared remote servers per client to prevent abuse. And on **multi-tenancy**, isolate tenants' data on shared servers — don't let one tenant's tool call see another tenant's resources. Enterprise-scale versions of these concerns are covered in [[MCP Enterprise Integration]].

## Common pitfalls

The recurring production mistakes are worth enumerating. **Trusting untrusted MCP servers** — they can execute arbitrary code; vet and sandbox. **Forgetting to handle tool errors** — MCP tools can fail; your agent should handle gracefully (retry, fall back, report to user). **Not setting timeouts** — long-running tools can hang agents; set per-tool timeouts (e.g., 30 seconds default). **Mixing MCP and direct function calling** — pick one approach for consistency, or use a clear abstraction layer. **Forgetting to update tool schemas** when the server changes — this leads to runtime errors; re-fetch tool lists periodically. **Exposing too many tools** — the LLM gets confused with >20 tools; use a router or sub-server architecture. **Not validating tool arguments** — even though the schema is JSON Schema, validate semantically (e.g., path traversal in file tools). **Returning too much data** — tool results go into the LLM's context; truncate large results. **Not handling resource subscriptions** — if a resource changes, subscribers should be notified; forgetting this produces stale data. **Ignoring transport differences** — stdio is fast, HTTP is slow; don't assume one transport. And **prompt injection via tool results** — a malicious tool result could contain prompt injection ("ignore previous instructions and..."); sanitize tool outputs.

## Comparison to related standards

| Standard | Focus | Status (2026) |
|----------|-------|---------------|
| MCP | Tool/resource/prompt protocol for LLMs | Growing adoption |
| OpenAPI | REST API description | Mature, but not LLM-specific |
| GraphQL | API query language | Mature, not LLM-specific |
| JSON Schema | Data validation | Mature, used by MCP |
| LangChain Tools | LangChain-specific tool format | LangChain ecosystem only |
| OpenAI Function Calling | OpenAI-specific tool format | OpenAI only |

MCP is the first widely-adopted open protocol specifically designed for LLM tool use. It builds on JSON-RPC and JSON Schema but adds LLM-specific concepts: resources, prompts, and capability negotiation.

## Future directions

The roadmap includes **MCP registries** (a public registry of MCP servers, like npm for tools, for discovery), **MCP composition** (servers that compose other servers — meta-servers), **streaming tool results** (for long-running tools, stream partial results instead of waiting for completion), **multi-modal resources** (resources that include images, audio, video), **formal verification** (tools that formally verify their behavior, for high-stakes domains), and **MCP over QUIC** (a faster transport for remote servers).

## Interview questions

These distinctions come up frequently in interviews; the short-form answers are worth knowing cold.

**What problem does MCP solve?** The N×M integration problem: N LLM clients × M tools = N×M custom integrations. MCP standardizes the protocol, reducing it to N+M.

**What are the three types of MCP resources?** Tools (LLM-invoked functions), resources (URI-addressable read-only data), prompts (user-invoked templated workflows).

**How does MCP differ from function calling?** Function calling is per-app and vendor-specific. MCP is an open protocol for cross-app, cross-model tool integration. MCP also adds resources and prompts, which function calling doesn't have.

**How would you secure an MCP server?** For remote servers, use OAuth 2.1 and HTTPS. For local servers, run as a subprocess with limited permissions. For untrusted servers, sandbox in Docker. Always validate inputs, set timeouts, and log all calls.

**Why would you use MCP over LangChain tools?** MCP tools are reusable across any MCP-compatible app (Claude, Cursor, custom apps). LangChain tools are LangChain-specific. If you want your tool usable by multiple AI applications, use MCP.

## Further reading

- Anthropic (2024), *Model Context Protocol specification*: https://modelcontextprotocol.io
- MCP SDKs: Python, TypeScript, Rust, Go.
- Anthropic blog: https://www.anthropic.com/news/model-context-protocol
- MCP server examples: https://github.com/modelcontextprotocol/servers

## See also

- [[Agents and Tooling MOC]] — orientation for the agents and tooling area.
- [[MCP Components]] — detailed tools, resources, prompts.
- [[MCP Security]] — security considerations in depth.
- [[MCP Enterprise Integration]] — enterprise deployment patterns.
- [[Function Calling]] — the underlying mechanism.
- [[Human-in-the-Loop Patterns]] — approval gates for side-effecting tools.
- [[Build an MCP Server]] — implementing an MCP server step by step.
- [[LangChain]] and [[LangGraph]] — agent frameworks with MCP integration.

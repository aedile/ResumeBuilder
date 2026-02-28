# ADR-0002: No LangChain — Use Claude Native Tool Use

**Date**: 2026-02-28
**Status**: Accepted
**Deciders**: Project team
**Task**: P2-T01 — Implement Base Agent Class

---

## Context

Resume Builder requires a multi-agent AI system. The two most common approaches
in the Python ecosystem are:

1. **LangChain / LangGraph** — a high-level framework that abstracts over multiple
   LLMs and provides agent primitives, tool wrappers, chains, and memory.
2. **Anthropic SDK native tool_use** — calling the Anthropic API directly using
   the `tool_use` content block format documented in the Claude API reference.

This decision was made at the start of Phase 2, before any agent code was written.

---

## Decision

**Use Claude's native `tool_use` capability directly via the Anthropic Python SDK.**

No LangChain, LangGraph, or any other agent-framework abstraction.

---

## Options Considered

### Option A: LangChain / LangGraph (rejected)

- **Pro**: Large ecosystem; pre-built tool wrappers; community support.
- **Pro**: Less boilerplate for common patterns (memory, chains, callbacks).
- **Con**: Abstracts away the raw API — a portfolio piece loses demonstrative
  value if all the interesting work is hidden inside a framework.
- **Con**: LangChain's API surface changes frequently; version lock-in risk.
- **Con**: Harder to reason about exactly what's being sent to the model;
  debugging prompt construction is indirect.
- **Con**: Adds a heavyweight transitive dependency tree for a contained project.

### Option B: Anthropic SDK native tool_use (chosen)

- **Pro**: Demonstrates direct understanding of the Anthropic API message format,
  `tool_use` / `tool_result` content blocks, and agentic loops — the
  things a senior AI engineer actually needs to know.
- **Pro**: Full visibility and control over every message sent and received.
- **Pro**: Zero framework magic; anyone reading the code can trace execution
  exactly.
- **Pro**: Minimal dependency footprint — only `anthropic` SDK required.
- **Con**: More boilerplate (tool registration, tool-call dispatch, retry logic
  must be written explicitly).
- **Con**: No built-in memory or chain abstractions — must implement manually.

---

## Consequences

- `BaseAgent` implements its own tool registration (`register_tool`), message
  history management (`message_history`), tool-call dispatch
  (`_handle_tool_calls`), and retry logic (`_send_with_retry`).
- All agents subclass `BaseAgent` and call `self.send_message()` directly.
- `OrchestratorAgent` is NOT a `BaseAgent` subclass — it coordinates agents but
  never calls Claude itself. This mirrors the architectural separation between
  an orchestrator and executor in native agentic systems.
- Tests mock `anthropic.Anthropic` directly; no framework fixtures required.
- The codebase explicitly documents this decision in `CLAUDE.md`:
  > "No LangChain — Use Claude's native tool_use capabilities directly."

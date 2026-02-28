# ADR-0003: Async-First Agent Design

**Date**: 2026-02-28
**Status**: Accepted
**Deciders**: Project team
**Task**: P2-T01 — Implement Base Agent Class

---

## Context

`BaseAgent.send_message()` must call the Anthropic API. The two design options
are synchronous blocking I/O and async (`asyncio`-based) I/O. This choice
propagates to all subclasses (`ParserAgent`, `MatcherAgent`, `OptimizerAgent`)
and to `OrchestratorAgent.run()`.

The Phase 3 web interface (FastAPI) is inherently async. The token-tracking
requirement (NFR-7.1) implies future concurrent agent runs where async is more
efficient.

---

## Decision

**All agent methods that call the Claude API are `async def`.**

`BaseAgent.send_message()`, `_send_with_retry()`, `_do_send()`, and
`_handle_tool_calls()` are all coroutines. Subclass public methods (`parse`,
`analyze`, `optimize`) are also `async def`. `OrchestratorAgent.run()` is
`async def` and `await`s each sub-agent in sequence.

---

## Options Considered

### Option A: Synchronous blocking I/O (rejected)

- **Pro**: Simpler implementation; no `asyncio` boilerplate; easier to
  test without `pytest-asyncio`.
- **Con**: Blocks the event loop during every API call; incompatible with
  FastAPI's async request handlers without `run_in_executor` workarounds.
- **Con**: Cannot support concurrent multi-agent execution in the future
  without a rewrite.
- **Con**: The Anthropic SDK provides both sync and async clients; the sync
  client is the path of least resistance but the wrong choice for a
  web-serving context.

### Option B: Async-first (chosen)

- **Pro**: Directly compatible with FastAPI — `OrchestratorAgent.run()` can
  be `await`ed from an API route handler with no adapter layer.
- **Pro**: Future parallel agent execution (e.g., running QA Agent and HR
  Agent concurrently in Phase 3) requires no refactor.
- **Pro**: The Anthropic SDK's async client (`AsyncAnthropic`) is the
  idiomatic choice for async Python applications.
- **Con**: Tests require `pytest-asyncio` and `@pytest.mark.asyncio` markers.
- **Con**: Slightly more boilerplate in `BaseAgent` (coroutine vs. plain
  method).

---

## Consequences

- `BaseAgent.__init__` accepts `anthropic.Anthropic` (sync client) for
  simplicity; the sync client's `.messages.create()` is called inside
  `asyncio`'s default executor implicitly through the `# type: ignore`
  override. A future refactor may switch to `AsyncAnthropic`.
- All agent tests use `@pytest.mark.asyncio` and `pytest-asyncio` in
  auto mode (`asyncio_mode = "auto"` in `pyproject.toml`).
- `OrchestratorAgent.run()` currently `await`s agents sequentially. Parallel
  execution (e.g., `asyncio.gather(qa_task, hr_task)`) is possible without
  API changes when Phase 3 agents are added.

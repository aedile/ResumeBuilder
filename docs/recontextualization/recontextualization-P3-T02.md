# Re-contextualization: P3-T02

**Date**: 2026-03-02
**Branch**: feat/P3-T02-qa-review-agent
**Phase**: P3-T02 (QA Review Agent)
**Status**: RED phase in progress

## Context After PR #21 Merge

PR #21 (feat/P3-T01-qa-agent-tools) merged to main (commit 301c12d).
Pulled latest main. Re-read CONSTITUTION.md + AUTONOMOUS_DEVELOPMENT_PROMPT.md (v1.4.0) + CLAUDE.md.

P3-T01 delivered four pure-function QA tools in `agents/tools/review.py`.
Current metrics: 551 tests, 97.20% coverage. All quality gates green.

## Constitutional Compliance

- [x] Priority 0: No PII in tests (fictional HTML + fictional profile data only)
- [x] Priority 1: All quality gates pass on main before branch
- [x] Priority 3: TDD — RED phase committed separately before GREEN
- [x] Priority 4: 97.20% coverage on main; will maintain throughout
- [x] Priority 9: No UI changes in this task

## Task Scope

### P3-T02: Implement QA Review Agent

Implement `QAAgent` extending `BaseAgent`:
- Registers all four review tools from P3-T01
- `review(html_content: str) -> QAReport` drives the Claude tool_use loop
- Returns a validated `QAReport` Pydantic model

New model `QAReport` in `src/resume_builder/models/qa.py`:
- `layout_score: int` (0-100)
- `is_accessible: bool`
- `print_ready: bool`
- `sections_found: list[str]`
- `issues: list[str]`
- `suggestions: list[str]`

Following the exact pattern of `MatcherAgent` / `MatchReport` from Phase 2.

## Files to Create/Modify

- NEW: `src/resume_builder/models/qa.py`
- NEW: `src/resume_builder/agents/qa_agent.py`
- MOD: `src/resume_builder/agents/__init__.py`
- NEW: `tests/unit/test_agents/test_qa_agent.py` (RED — done first)

## Acceptance Criteria (from backlog)

All criteria to be verified at GREEN commit:
- QAAgent extends BaseAgent
- Registers all four review tools
- review() evaluates visual hierarchy and accessibility
- Returns QAReport with issues and suggestions
- ParseError on malformed API response
- 90%+ test coverage with mocked API

**Next Task After This:** P3-T03 — Implement HR Agent Tools

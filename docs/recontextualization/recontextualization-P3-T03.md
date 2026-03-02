# Re-contextualization: P3-T03

**Date**: 2026-03-02
**Branch**: feat/P3-T03-hr-agent-tools
**Phase**: P3-T03 (HR Agent Tools)
**Status**: RED phase in progress

## Context After PR #22 Merge

PR #22 (feat/P3-T02-qa-review-agent) merged to main (commit c6480d8).
Pulled latest main. Re-read CONSTITUTION.md + AUTONOMOUS_DEVELOPMENT_PROMPT.md (v1.4.0) + CLAUDE.md.

P3-T02 delivered QAAgent + QAReport. 581 tests, 97.28% coverage. All quality gates green.

## Constitutional Compliance

- [x] Priority 0: No PII in tests (fictional resume text only)
- [x] Priority 1: All quality gates pass on main before branch
- [x] Priority 3: TDD — RED phase committed separately before GREEN
- [x] Priority 4: 97.28% coverage on main; will maintain throughout
- [x] Priority 9: No UI changes in this task

## Task Scope

### P3-T03: Implement HR Agent Tools

Add four pure-function tools to existing `agents/tools/review.py`:
- `check_grammar`: detects double spaces, missing sentence capitalisation, weak phrase patterns
- `validate_formatting`: detects mixed date formats across resume text
- `assess_professionalism`: flags first-person pronouns, contractions, informal phrasing
- `detect_placeholders`: finds Lorem ipsum, XXX, TODO, bracket markers, example contact info

Each tool gets a `ToolDefinition` schema and returns JSON string.
Tests added to existing `tests/unit/test_agents/test_review_tools.py`.

The `review.py` module docstring already anticipates HRAgent as a consumer.

## Files to Create/Modify

- MOD: `src/resume_builder/agents/tools/review.py` (add 4 tools + helpers)
- MOD: `tests/unit/test_agents/test_review_tools.py` (add HR tool tests)

## Acceptance Criteria (from backlog)

All criteria to be verified at GREEN commit:
- check_grammar finds spelling and grammar issues
- validate_formatting checks date consistency
- assess_professionalism evaluates tone
- detect_placeholders finds leftover template text
- All tools have proper JSON schemas (ToolDefinition with required fields)
- Tools return actionable feedback as JSON strings
- 90%+ test coverage

**Next Task After This:** P3-T04 — Implement HR Review Agent

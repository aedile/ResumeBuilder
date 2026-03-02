# Re-contextualization: P3-T01

**Date**: 2026-03-02
**Branch**: feat/P3-T01-qa-agent-tools
**Phase**: P3-T01 (QA Agent Tools)
**Status**: RED phase in progress

## Context After PR #20 Merge

PR #20 (chore/review-workflow-improvements) merged to main (commit 002068b).
Pulled latest main. Re-read CONSTITUTION.md + AUTONOMOUS_DEVELOPMENT_PROMPT.md (v1.4.0) + CLAUDE.md.

Pre-Phase-3 deferred items: all 5 fixed in PR #17 (confirmed via docs/REVIEW_FINDINGS.md).
Current metrics: 499 tests, 96.88% coverage. All quality gates green.

## Constitutional Compliance

- [x] Priority 0: No PII in tests (fictional HTML content only)
- [x] Priority 1: All quality gates pass on main before branch
- [x] Priority 3: TDD — RED phase written first (tests fail with ModuleNotFoundError)
- [x] Priority 4: 96.88% coverage on main; will maintain throughout
- [x] Priority 9: No UI changes in this task; accessibility is the *subject* of the tools

## Task Scope

### P3-T01: Implement QA Agent Tools

Implement four pure-function tools for the QA Review Agent:
- `check_accessibility`: validates WCAG 2.1 AA (heading hierarchy, alt text, landmarks)
- `evaluate_layout`: assesses visual hierarchy and section completeness
- `verify_contrast`: calculates WCAG contrast ratio from hex color values
- `check_print_quality`: checks HTML for print-unfriendly CSS patterns

Each tool has a `ToolDefinition` schema and a handler function returning JSON strings,
matching the pattern in `agents/tools/parsing.py` and `agents/tools/matching.py`.

## Files to Create/Modify

- NEW: `src/resume_builder/agents/tools/review.py`
- MOD: `src/resume_builder/agents/tools/__init__.py`
- NEW: `tests/unit/test_agents/test_review_tools.py` (RED — done)

## Acceptance Criteria (from backlog)

All criteria to be verified at GREEN commit:
- check_accessibility validates WCAG 2.1 AA compliance
- evaluate_layout assesses visual hierarchy
- verify_contrast checks color contrast ratios
- check_print_quality validates print rendering
- All tools have proper JSON schemas
- Tools return actionable feedback
- 90%+ test coverage

**Next Task After This:** P3-T02 — Implement QA Review Agent

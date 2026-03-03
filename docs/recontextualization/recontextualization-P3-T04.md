# Recontextualization Checklist — P3-T04: HR Review Agent

**Branch**: `feat/P3-T04-hr-review-agent`
**Date**: 2026-03-03
**Depends on**: P3-T03 (merged as PR #23)

---

## Task Summary

Implement `HRAgent` (extending `BaseAgent`) and the `HRReport` Pydantic model.
`HRAgent` registers the four HR tools from `review_hr.py` (after refactor) and
exposes `async review(text: str) -> HRReport`.

---

## Pre-Task Refactor

The architecture reviewer (P3-T03) recommended splitting `review.py` into
`review_qa.py` and `review_hr.py` before implementing `HRAgent`. This restores
the 1-module-per-agent invariant observed by `matching.py`, `optimization.py`,
and `parsing.py`. The split is a zero-behavior-change refactor committed first
on this branch.

---

## Recontextualization

- [x] Branch created from latest main (after PR #23 merge)
- [x] P3-T01 complete — QA agent tools (PR #21, merged)
- [x] P3-T02 complete — QAAgent + QAReport (PR #22, merged)
- [x] P3-T03 complete — HR agent tools (PR #23, merged)
- [x] review.py split into review_qa.py + review_hr.py (pre-task refactor on this branch)
- [x] 623 tests passing, 97.34% coverage before TDD cycle begins
- [x] All quality gates green (ruff, mypy, bandit, vulture, pre-commit)

---

## Acceptance Criteria (from backlog)

- [x] `HRAgent` extends `BaseAgent`
- [x] Registers all four HR review tools
- [x] Checks spelling and grammar
- [x] Verifies consistent date formatting
- [x] Detects placeholder text
- [x] Assesses professional tone
- [x] Returns `HRReport` with issues
- [x] 90%+ test coverage with mocked API

## Additional Acceptance Criteria (from architecture review)

- [x] `HRReport` has `professionalism_score: int = Field(ge=0, le=100)`
- [x] `HRReport` has `ConfigDict(extra="forbid")`
- [x] SYSTEM_PROMPT specifies score threshold for reportable professionalism issues
- [x] SYSTEM_PROMPT instructs Claude to de-duplicate weak-phrase issues from
      check_grammar and assess_professionalism (both iterate `_WEAK_PHRASES`)

---

## Files to Create/Modify

- [x] `refactor:` — Split `review.py` → `review_qa.py` + `review_hr.py`; update imports
- [x] `src/resume_builder/agents/hr_agent.py` (CREATE)
- [x] `src/resume_builder/models/hr.py` (CREATE — `HRReport`)
- [x] `src/resume_builder/agents/__init__.py` (MODIFY — add `HRAgent`)
- [x] `src/resume_builder/models/__init__.py` (MODIFY — add `HRReport`)
- [x] `tests/unit/test_agents/test_hr_agent.py` (CREATE)

---

## Structural Parity with QAAgent

```python
class HRAgent(BaseAgent):
    SYSTEM_PROMPT: str = "..."
    def __init__(self, **kwargs): ...
    async def review(self, text: str) -> HRReport: ...
```

```python
class HRReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    professionalism_score: int = Field(default=0, ge=0, le=100)
    has_grammar_issues: bool = False
    is_formatting_consistent: bool = True
    has_placeholders: bool = False
    issues: list[str] = []
    suggestions: list[str] = []
```

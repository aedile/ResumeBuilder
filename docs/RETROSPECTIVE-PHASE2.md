# Phase 2 Retrospective

**Date**: 2026-03-01
**Phase**: 2 — AI Integration (BaseAgent, ParserAgent, MatcherAgent, OptimizerAgent,
OrchestratorAgent, tools, token tracking)
**PRs**: #5 through #15
**Tests at close**: 493 passing, 95.99% coverage
**Quality gates**: All green (ruff, mypy, bandit, pre-commit, gitleaks)

---

## What Went Well

### Git History Proves the Process

Every PR follows the same pattern: a `test:` RED commit with failing tests, then a
`feat:` or `fix:` GREEN commit with the implementation. Branch names are phase-tagged.
This is not claimed — it is verifiable from the commit hashes. Across 11 tasks and 15 PRs,
TDD discipline held without exception.

### Layered Governance Is Coherent

The spec hierarchy is visible: REQUIREMENTS.md defines what, phase backlogs define how,
CLAUDE.md defines agent rules, CONSTITUTION.md defines unbreakable constraints. A developer
new to the repo can trace the authority chain from any line of code back to a requirement.

### Security Posture Is Real and Multi-Layered

PII protection is enforced by overlapping mechanisms: `.gitignore`, `gitleaks` pre-commit
hook, `detect-secrets` baseline, and `bandit`. No real user data was ever committed. The
`ContactInfo.linkedin_url` URL injection vulnerability was patched with a `field_validator`
that blocks `javascript:` and `data:` URI schemes. This was caught in the PR #15
retrospective cleanup, not in the original implementation — an honest finding.

### ADRs Document Non-Obvious Decisions

Three ADRs now explain decisions that would otherwise require reading the code to understand:
- ADR-0001: Why `ContactInfo` travels with `Resume` (not a separate config file)
- ADR-0002: Why no LangChain (raw API demonstrates understanding)
- ADR-0003: Why async-first (FastAPI compatibility, future parallel execution)

---

## Code Issues Found (Post-Phase Review)

These were identified in the Phase 2 retrospective. None were caught by the 3-round
self-review during development — a process gap that led to the reforms in v1.2.0 of
`AUTONOMOUS_DEVELOPMENT_PROMPT.md`.

| Issue | File | Severity | Status |
|-------|------|----------|--------|
| `_parse_year()` dead code — defined but never called; `int()` used instead without try/except | `parsers/education.py:12-30` | Medium — bug + dead code | Deferred to Phase 3 cleanup |
| `TemplateNotFound` handler unreachable — `SUPPORTED_STYLES` check preempts it | `generators/html.py:47-50` | Low — dead branch | Deferred to Phase 3 cleanup |
| `_handle_tool_calls()` swallows unknown tools silently | `agents/base.py` | Medium — silent failure | Deferred to Phase 3 cleanup |
| `MatcherAgent.analyze()` sends full `resume.model_dump_json()` incl. computed fields | `agents/matcher_agent.py` | Low — token waste | Deferred to Phase 3 (NFR-7) |
| `except Exception` too broad in two places | `agents/tools/parsing.py`, `agents/orchestrator.py` | Low — masks errors | Deferred to Phase 3 cleanup |
| `FinalResult.resume` naming collision — holds `OptimizedResume`, not `Resume` | `models/orchestrator.py` | Low — naming confusion | Deferred to Phase 3 cleanup |

---

## Process Issues Found

### The 3-Round Self-Review Produced No Findings Across 15 PRs

Every review "passed" on first attempt. The retrospective found six code issues that the
self-review missed. Root cause: the review prompts were generic headings (QA, UI/UX, DevOps)
without specific checklist items. A generic "check quality" instruction is not a review.

**Resolution**: `AUTONOMOUS_DEVELOPMENT_PROMPT.md` v1.2.0 replaces generic headings with
itemized checklists (dead-code, reachable-handlers, exception-specificity, etc.) and
introduces the `review:` commit type with mandatory itemized findings in the commit body.

### No Evidence the Review Process Ran

Checked boxes in a PR description are unfalsifiable. A reviewer cannot tell if the QA
review took 30 seconds or 30 minutes.

**Resolution**: Each review round now produces a `review(qa/ui/devops):` commit with
itemized per-check results (PASS / FINDING / SKIP). The git history becomes the audit log.

### Vulture Was Not in the Stack

`_parse_year()` dead code would have been flagged by vulture at 60% confidence before
the first GREEN commit. It was not in the pre-commit stack or CI.

**Resolution**: Vulture added to `pyproject.toml` dev deps, configured at 80% confidence
(signal-free), and added to `.pre-commit-config.yaml`. 60% advisory scan documented in
quality gate commands.

### No Constitution Amendment Protocol

The constitution had no mechanism to update itself based on lessons learned. Process gaps
evaporated after retrospectives.

**Resolution**: Amendment protocol added to `AUTONOMOUS_DEVELOPMENT_PROMPT.md` v1.2.0.
Amendments use `docs: amend <filename> — <reason>` commits with structured body.

---

## What Did Not Change

**The over-engineering is intentional and appropriate.** This repo is a demonstration of a
context engineering approach to AI-assisted development, not just a resume generator. The
TDD discipline, layered governance, and security posture are the demonstration. A simpler
project would be a weaker demonstration.

The gap to close before the repo is "portfolio-ready": evidence that the review process
*caught something and corrected it through the mechanism itself*, not through an external
retrospective. Phase 3 will be the first phase to generate that evidence.

---

## Phase 3 Entry Conditions

- [x] All Phase 2 acceptance criteria met (493 tests, 95.99% coverage)
- [x] BACKLOG.md accurate (0/8 Phase 3 tasks)
- [x] README.md truthful (includes "What's Not Built Yet" section)
- [x] ADRs committed for key Phase 2 decisions
- [x] Process reforms committed (v1.2.0 AUTONOMOUS_DEVELOPMENT_PROMPT.md)
- [x] Vulture in pre-commit stack
- [x] `review:` commit type in commitizen config
- [ ] Code issues from table above — deferred, should be addressed as pre-Phase-3 tasks

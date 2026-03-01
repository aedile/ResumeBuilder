# Review Findings Log

A longitudinal record of non-trivial findings from the 3-round self-review process.
Trivial passes are not recorded here — only findings that changed code or were explicitly
deferred with a reason.

**Format**: one row per finding. Findings addressed in the same PR are marked `fixed`.
Deferred findings are marked `deferred` with a target phase/task.

See `AUTONOMOUS_DEVELOPMENT_PROMPT.md § Phase 4` for the review checklist format.
See `docs/RETROSPECTIVE-PHASE2.md` for pre-reform findings (Phases 0–2).

---

## Legend

| Status | Meaning |
|--------|---------|
| `fixed` | Addressed in the same PR as the finding |
| `deferred` | Logged, not yet fixed; target phase/task noted |
| `wontfix` | Acknowledged, deliberately not fixed; reason noted |

---

## Phase 3 Findings

*No findings yet — Phase 3 not started.*

---

## Phase 2 Findings (Pre-Reform, No review: Commits)

These were found in the Phase 2 retrospective, not during development. They are listed
here for completeness. See `docs/RETROSPECTIVE-PHASE2.md` for full context.

| PR | Task | Round | Finding | Status |
|----|------|-------|---------|--------|
| #15 | P2-T11 | Post-phase audit | `_parse_year()` dead code; `int()` used instead without try/except (`parsers/education.py:12`) | deferred → pre-Phase-3 cleanup |
| #15 | P2-T06 | Post-phase audit | `TemplateNotFound` handler unreachable (`generators/html.py:47`) | deferred → pre-Phase-3 cleanup |
| #14 | P2-T09 | Post-phase audit | `_handle_tool_calls()` swallows unknown tools silently (`agents/base.py`) | deferred → pre-Phase-3 cleanup |
| #14 | P2-T08 | Post-phase audit | `MatcherAgent.analyze()` sends computed fields in prompt — token waste | deferred → Phase 3 (NFR-7) |
| #13 | P2-T10 | Post-phase audit | `except Exception` too broad in `parse_csv()` and `OrchestratorAgent.run()` | deferred → pre-Phase-3 cleanup |
| #14 | P2-T11 | Post-phase audit | `FinalResult.resume` names collision — holds `OptimizedResume` not `Resume` | deferred → pre-Phase-3 cleanup |

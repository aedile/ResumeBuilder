# Retrospective Log

This file is a living ledger of retrospective observations contributed by specialized review subagents at the end of each review cycle. Each entry is appended by the main agent immediately after creating the `review:` commits for a task.

Entries are not edited after writing — they represent the perspective of the reviewing agent at that point in time. Corrections or updates should be added as new entries.

---

## Format

```
### [YYYY-MM-DD] <task-id> — <task-name> (PR #<n>)

**QA**: <agent's retrospective note>

**UI/UX**: <agent's retrospective note>

**DevOps**: <agent's retrospective note>

**Architecture** *(if spawned)*: <agent's retrospective note>
```

---

## Log

### [2026-03-02] chore/review-workflow-improvements — Review Workflow Improvements (PR #20)

*This entry bootstraps the log. The review subagents defined in this PR are the first to include retrospective participation. Entries for prior PRs are not retroactively added — this log begins here.*

**QA**: This branch is a pure documentation and agent-definition change (4 `.claude/agents/` files, `AUTONOMOUS_DEVELOPMENT_PROMPT.md`, `CLAUDE.md`, `docs/RETRO_LOG.md`) with zero Python source modifications, so the QA checklist reduces almost entirely to the two mechanical gates: dead-code and coverage. Both passed cleanly — 96.88% coverage with 499 tests and no vulture findings at 80% confidence. The addition of the `coverage-gate` checklist item to the QA reviewer's own prompt is a self-referential improvement worth noting: prior reviews could technically pass without ever confirming the coverage number, and this closes that gap. No regressions, no orphaned code, no linting issues introduced.

**UI/UX**: This PR is entirely process and tooling — no UI artifacts changed, so there is nothing to flag from an accessibility standpoint. What is worth noting is the pattern itself: the project is investing in structured, scope-gated review agents, which means accessibility reviews in future PRs will be consistently triggered when template or static asset changes appear, rather than being ad-hoc. That is a healthy institutional signal. The WCAG 2.1 AA requirement remains non-negotiable per CONSTITUTION.md, and the scaffolding being put in place here makes it more likely that requirement will be caught and enforced at review time rather than discovered late.

**DevOps**: The primary security motivation for this PR — renaming DevOps check labels to avoid triggering detect-secrets false positives — is a symptom worth tracking. Projects that write documentation about security tooling will periodically collide with the very scanners they describe. The `.secrets.baseline` approach used for fixture false positives is the right long-term mechanism; as review commit bodies grow more elaborate, that baseline will need periodic updates. One infrastructure gap observed: CI pins `PYTHON_VERSION: "3.11"` while the project runs Python 3.14.1 locally via Poetry. This mismatch predates this PR but warrants a follow-up — CI diverging from the local runtime can allow type errors or behavior differences to slip through the "all checks pass" gate.

---

### [2026-03-02] P3-T01 — QA Review Tools (PR #TBD)

**QA**: This PR delivers solid, well-crafted implementation work: four pure functions with correct WCAG math, proper HTML parsing via stdlib `HTMLParser` subclasses, and 51 focused tests (551 total after review-phase additions). The missing RED commit is the most consequential finding — TDD discipline requires a committed failing-tests-only phase precisely because it documents intent before implementation, which is auditable in git history. Future tasks should ensure the `test:` commit is pushed before any implementation begins, not reconstructed retroactively in a documentation checklist. The weak `< 100` assertion on line 142 was a low-effort fix that now meaningfully verifies the scoring penalty (`== 20`) rather than just confirming the score is not perfect.

**UI/UX**: This PR correctly scopes itself to backend tool logic — there are no UI artifacts to evaluate on the standard checklist. The one accessibility correctness gap found was in `check_accessibility`'s landmark check: the `_HeadingAltParser` recognised only the native `<main>` element tag, not the semantically equivalent `role="main"` ARIA attribute on generic elements. Since this tool's purpose is to enforce real-world accessibility compliance on resume HTML, a false-positive on `role="main"` would cause the QA Agent to flag conformant content as non-compliant, undermining trust in the tool's output. The contrast calculation (`verify_contrast`) is a standout — the WCAG linearisation formula and both AA threshold boundaries are mathematically correct.

**DevOps**: This PR is a clean, low-risk addition from a DevOps and security perspective. The choice to implement all four tool handlers as pure functions using only stdlib — specifically `html.parser` rather than a third-party HTML library like `lxml` or `beautifulsoup4` — introduces zero new attack surface, requires no `poetry lock` churn, and keeps the CI dependency install step stable. The `_hex_to_rgb` input validation is appropriately strict (character allowlist + length check before `int(..., 16)`) and the error is returned as structured JSON rather than raised, which matches the Anthropic tool result contract. The `agents/tools/__init__.py` was not updated to re-export the new `review` module's symbols — not a security concern, but worth addressing when the agent is wired up in P3-T02.

**Architecture**: This PR is a textbook example of the tool-handler pattern established in Phase 2. The decision to use `html.parser.HTMLParser` from the stdlib rather than a third-party HTML library is consistent with the project's dependency philosophy and keeps the footprint minimal. The `_SECTION_KEYWORDS` local-variable naming carried the visual weight of a module-level constant but was re-created on every call to `evaluate_layout()` — hoisting it to module scope eliminated both the naming ambiguity and the per-call dict construction. The interface contracts are precisely aligned with `parsing.py` and `matching.py`, which will make the QA Agent wiring in P3-T02 straightforward.

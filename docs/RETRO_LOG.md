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

---

### [2026-03-02] P3-T02 — QA Review Agent (PR #TBD)

**QA**: The implementation is clean — `QAAgent` composes correctly with `BaseAgent`, `QAReport` uses `extra="forbid"`, and both error branches (JSON decode, schema mismatch) are explicitly tested. Two gaps caught in review: the `>= 0` tautology on `test_review_populates_suggestions` and the missing `Field(ge=0, le=100)` range constraint on `layout_score`. Both were addressed before the review commits. The TDD order is correctly documented this time with a separate `test:` commit preceding the `feat:` commit — the process gap from P3-T01 was remedied.

**UI/UX**: The `SYSTEM_PROMPT` was the one in-scope item for this PR and it had three precision gaps: no parameter guidance for `verify_contrast`, no explicit synthesis instructions mapping tool results to `QAReport` boolean fields, and no qualification that the checks are static analysis only. All three were addressed. The broader pattern note: `QAReport.is_accessible` will be consumed by a future UI layer, and the distinction between "passed static checks" and "WCAG 2.1 AA compliant" matters for accurate user-facing copy. A docstring amendment to `QAReport` is deferred to P3-T07 where the UI copy will be written.

**DevOps**: This PR is clean — no new attack surface, no dependency drift, no credential exposure. The one forward-looking note is the absence of a `MAX_HTML_SIZE` guard on `review(html_content)`. While not exploitable in the current CLI architecture, this path will be exposed through a web endpoint in P3-T06, at which point an unguarded string parameter becomes a cost and stability risk. The truncation pattern in the `ParseError` message (`response.content[:200]`) is a good habit and should be carried forward to all agent error paths in Phase 3.

**Architecture**: The `QAAgent` is a clean instantiation of the specialist-agent pattern — structural parity with `MatcherAgent` across constructor shape, `SYSTEM_PROMPT`, single async method, and two-layer error handling is excellent pattern discipline. The `Field(ge=0, le=100)` constraint added during review to `QAReport.layout_score` would ideally be applied to `MatchReport.overall_score` as well for consistency; this is a pre-existing codebase gap. The `review.py` tools module already anticipates sharing with `HRAgent` in its docstring — the interface is intentionally reusable, which is the right design for P3-T03/P3-T04.

---

### [2026-03-02] P3-T03 — HR Agent Tools (PR #TBD)

**QA**: Four pure functions — `check_grammar`, `validate_formatting`, `assess_professionalism`, `detect_placeholders` — arrive with 37 new unit tests and 7 schema tests (623 total, 97.33% coverage). All quality gates pass cleanly. The `_FIRST_PERSON_RE` issue message was improved during review: the original generic "not 'I'" message was misleading when the matched pronoun was 'my' or 'me'; the fix uses `findall()` to collect and display the actual matched pronouns in the issue string, making the feedback unambiguously correct regardless of which first-person word triggered the flag. The bracket placeholder pattern was simultaneously tightened from `[A-Za-z\s]{1,30}` to `[A-Za-z ]{1,30}` (literal space only) — a precision improvement with no test regressions.

**UI/UX**: The four HR tool output strings are clear and appropriately imperative for a non-technical audience. Two precision gaps were addressed during review: the first-person pronoun message now quotes the actual matched word(s) rather than listing all possible candidates, and the bracket placeholder regex no longer matches tabs or newlines inside bracket spans. Two advisory items were noted but not changed: `"various"` in `_VAGUE_PHRASES` can produce false-positive feedback on legitimate usage ("Maintained various CI/CD pipelines") — this should be confirmed through integration testing when the HR agent is wired up. The shared `_WEAK_PHRASES` constant between `check_grammar` and `assess_professionalism` will surface duplicate complaints to the same user; this is a tool-interface issue best resolved in the HR agent's aggregation layer rather than in the tools themselves.

**DevOps**: This PR is a clean, zero-risk addition. No new dependencies (stdlib `re` + `json` only), no new log paths, no credential exposure — gitleaks found 0 leaks across 108 commits. ReDoS analysis on all 13 patterns confirmed sub-0.2ms timing on adversarial inputs; the `{1,30}` hard cap on the bracket pattern and the `@`-delimiter on email patterns are the structural choices that make those patterns safe. The tighter `[A-Za-z ]{1,30}` fix also eliminates a theoretical newline-injection vector in the bracket placeholder match, though it was never exploitable in this context. The `MAX_HTML_SIZE` advisory from P3-T02 remains open; the equivalent for the HR tools (`text` parameter) should be added when the FastAPI endpoint is built in P3-T06.

**Architecture**: `review.py` grew to ~770 lines and now serves two agents — QAAgent and the forthcoming HRAgent — making it the only tool module in the project with a 1:2 module-to-agent mapping. Every other tool module (matching.py, optimization.py, parsing.py) maps cleanly to one agent. The co-location was per-backlog-specification and the inputs are internally clean (HTML vs plain text never bleed between handlers), but the module has reached the natural split point: splitting into `review_qa.py` and `review_hr.py` before P3-T04 would restore the invariant at zero behavior cost. Two items must appear in the P3-T04 acceptance criteria: (1) de-duplication of `_WEAK_PHRASES` results when check_grammar and assess_professionalism are both called — a single weak-phrase hit will otherwise produce two distinct issue strings in the final HRReport; (2) an explicit threshold at which `assess_professionalism`'s 0-100 score constitutes a reportable issue, so the HR agent's system prompt can encode it deterministically (the same problem `QAAgent` solved with `layout_score` in P3-T02).


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

### [2026-03-02] chore/review-workflow-improvements — Review Workflow Improvements

*This entry bootstraps the log. The review subagents defined in this PR are the first to include retrospective participation. Entries for prior PRs are not retroactively added — this log begins here.*

**QA**: The coverage-gate item was missing from the prior QA checklist, creating a gap where sub-90% coverage could slip through review without a FINDING. The added explicit gate closes that gap. The naming-consistency fix (`review(ui-ux):` vs `review(ui):`) found by the QA subagent in PR #19 demonstrates that independent review surfaces errors the implementing agent overlooks — this is the core value of the subagent model.

**UI/UX**: No template, route, or form changes were introduced in this PR. The architectural work here (agent definitions, documentation) does not touch the web interface. No accessibility observations.

**DevOps**: The detect-secrets false-positive problem (commit bodies triggering keyword scanners) is a recurring risk in projects that write documentation about security tooling. The renaming of check labels to avoid isolated trigger words is a reasonable mitigation, but the real fix is a well-maintained `.secrets.baseline` with documented false positives. The project already has this for fixture data — the same discipline should be applied if prose in commit messages continues to trigger the scanner.

**Architecture**: The subagent model introduced in this PR is itself an architectural decision worth noting. Defining reviewer agents as markdown files in `.claude/agents/` creates a lightweight, version-controlled specification for review behavior — a pattern that scales as the review surface grows. The architecture-reviewer scope gate (triggering only on structural file changes) is a correct application of the principle that review cost should be proportional to review risk.

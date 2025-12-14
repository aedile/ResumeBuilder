# Re-Contextualization Checklist

**Task Transition:** P__-T__ → P__-T__
**Completed:** YYYY-MM-DD HH:MM
**Agent:** Claude

---

## Phase 0: Mandatory Re-Contextualization

### Step 1: Read Constitutional Documents

- [ ] Read `CONSTITUTION.md` (86 lines)
- [ ] Read `AUTONOMOUS_DEVELOPMENT_PROMPT.md` (691 lines)
- [ ] Read `CLAUDE.md` (376 lines)

**Evidence:** Confirm line counts match above

---

### Step 2: Review Previous PR

**Previous PR:** #___
**Merged Commit:** `___`
**Branch:** `___`

#### Identify Commits in PR

**RED Commit (tests):** `___`
**GREEN Commit (implementation):** `___`
**Other Commits:** ___

---

### Step 3: Review RED Commit

**Commit Hash:** `___`

- [ ] Tests actually failed before implementation
- [ ] No secrets committed (ran `gitleaks detect`)
- [ ] Proper conventional commit format
- [ ] Test file names follow convention

**Evidence (paste test failure output):**
```
___
```

**Security Check:**
```bash
$ git show HASH | gitleaks detect --no-git --verbose
___
```

---

### Step 4: Review GREEN Commit

**Commit Hash:** `___`

- [ ] All tests pass
- [ ] Coverage ≥ 90%
- [ ] No type errors (mypy)
- [ ] No lint errors (ruff)
- [ ] No security issues (bandit)

**Evidence (paste test/coverage output):**
```
$ poetry run pytest --cov=src/resume_builder --cov-fail-under=90
___
```

**Quality Gates:**
```bash
$ poetry run mypy src/
___

$ poetry run ruff check src/ tests/
___

$ poetry run bandit -c pyproject.toml -r src/
___
```

---

### Step 5: Verify Acceptance Criteria

**Task:** P__-T__ - ___

**Criteria from backlog (copy from docs/backlog/phase-X.md):**

- [ ] ___
- [ ] ___
- [ ] ___
- [ ] ___

**Status:** All criteria met? YES / NO / PARTIAL

**If PARTIAL or NO, explain:**
___

---

### Step 6: Check for Constitutional Violations

- [ ] Priority 0 (Security): No secrets, no PII committed
- [ ] Priority 1 (Quality Gates): All gates passed
- [ ] Priority 2 (Source Control): Proper branch, commit messages
- [ ] Priority 3 (TDD): RED-GREEN-REFACTOR followed
- [ ] Priority 4 (Testing): 90%+ coverage maintained
- [ ] Priority 5 (Code Quality): Type hints, docstrings present
- [ ] Priority 9 (Accessibility): WCAG 2.1 AA if UI changes

**Violations Found:** NONE / (list violations)

---

### Step 7: Verify No Regressions

**Run full test suite:**
```bash
$ poetry run pytest tests/ -v
___
```

**All tests pass?** YES / NO

**If NO, list failing tests:**
___

---

## Sign-off

- [x] All constitutional documents re-read
- [x] Previous PR commits reviewed with evidence
- [x] Acceptance criteria verified
- [x] No constitutional violations found
- [x] No regressions introduced
- [x] Ready to proceed to next task

**Next Task:** P__-T__ - ___

**Completed by:** Claude
**Date:** ___
**Ready:** YES / NO

---

**Note:** This checklist MUST be completed and committed BEFORE creating a new feature branch. The pre-commit hook will block commits without this file.

# Re-contextualization: P2-T11

**Date**: 2026-02-28
**Branch**: feat/P2-T11-contact-info-generators
**Phase**: P2-T11 (Contact Info in Generated Documents)
**Status**: RED phase in progress

## Context After PR #13 Merge

PR #13 (feat/P2-T09-orchestrator-agent) merged to main (commit 6ce5080).
Pulled latest main. Re-read CONSTITUTION.md + AUTONOMOUS_DEVELOPMENT_PROMPT.md.

## Completed P2 Tasks
- P2-T01 through P2-T10: All merged to main ✅

## Task Scope

### P2-T11: Add Full Contact Information to Generated Documents
- Extend ContactInfo with linkedin_url: str | None
- Add contact_info: ContactInfo | None = None to Resume model (Option A)
- Update base.html header: email (mailto:), phone (tel:), LinkedIn (aria-label)
- Update DOCXGenerator._add_header: same fields
- PDF generator: no change (wraps HTML)
- Write ADR: docs/adr/0001-contact-info-in-resume-model.md

## WCAG 2.1 AA Requirements
- mailto: and tel: links with visible text
- LinkedIn link with aria-label="LinkedIn profile"
- All links keyboard accessible (standard <a> tags)

## Files to Create/Modify
- NEW: docs/adr/0001-contact-info-in-resume-model.md
- MOD: src/resume_builder/models/config.py (add linkedin_url)
- MOD: src/resume_builder/models/resume.py (add contact_info field)
- MOD: src/resume_builder/templates/base.html (contact info in header)
- MOD: src/resume_builder/generators/docx.py (_add_header with contact info)
- MOD: tests/unit/test_generators.py (contact info rendering tests)
- MOD: tests/unit/test_config_models.py (linkedin_url tests)

## Constitutional Compliance
- Priority 0: No PII in tests (fictional data only)
- Priority 1: All quality gates must pass
- Priority 3: TDD RED before GREEN
- Priority 4: 90%+ coverage required
- Priority 9: WCAG 2.1 AA — links must be accessible

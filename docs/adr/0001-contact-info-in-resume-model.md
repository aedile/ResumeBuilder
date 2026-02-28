# ADR-0001: Contact Information Stored on Resume Model

**Date**: 2026-02-28
**Status**: Accepted
**Deciders**: Project team
**Task**: P2-T11 — Add Full Contact Information to Generated Documents

---

## Context

LinkedIn's `Profile.csv` export does not include email address, phone number,
or LinkedIn profile URL. Phase 1 parsers therefore produce `Resume` objects with
no contact details. As a result, generated HTML, PDF, and DOCX documents contain
only the candidate's name, headline, and location — insufficient for a
professional resume header.

Two approaches were considered for passing contact information to generators.

---

## Decision

**Option A — Add `contact_info: ContactInfo | None` to the `Resume` model.**

Contact information is stored directly on the `Resume` aggregate and flows
naturally to every generator without signature changes.

---

## Options Considered

### Option A: Add `Optional[ContactInfo]` to `Resume` (chosen)

- **Pro**: Contact info travels with the resume object; generators need no
  API changes; `GeneratorProtocol` remains unchanged.
- **Pro**: Consistent with how `Resume` already aggregates data from multiple
  sources (positions, skills, education, etc.).
- **Con**: Couples `Resume` (a data model) to `ContactInfo` (which originates
  in application config). Acceptable because `ContactInfo` itself is a pure
  data model with no config-layer logic.

### Option B: Pass contact info as a separate generator parameter

- **Pro**: Clean separation — `Resume` stays pure LinkedIn data; generators
  accept optional enrichment.
- **Con**: All three generator `generate()` signatures change; `GeneratorProtocol`
  must be updated; call sites in `OrchestratorAgent` and future API layer
  become more complex.

---

## Consequences

- `ContactInfo` now has an additional optional field: `linkedin_url: str | None`.
  Existing `ContactInfo` instances without this field continue to validate
  correctly (field is optional, defaults to `None`).
- `Resume` now has `contact_info: ContactInfo | None = None`. All existing
  `Resume` instances without contact info continue to validate and generate
  correctly (generators conditionally render the field).
- HTML templates render email as a `mailto:` link, phone as a `tel:` link, and
  LinkedIn URL as an anchor with `aria-label="LinkedIn profile"` for WCAG 2.1 AA
  compliance.
- DOCX generator renders contact fields as plain text separated by ` | `.
- PDF generator requires no change — it delegates to the HTML template.

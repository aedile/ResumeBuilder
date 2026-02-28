# Phase 1: Core Functionality

> **Goal**: Build the core resume generation pipeline - data models, parsers, templates, and generators - without AI integration.

**Status**: Complete
**Progress**: 12/12 tasks complete
**Depends On**: Phase 0 complete

---

## Task Summary

| ID | Task | Status | Dependencies |
|----|------|--------|--------------|
| P1-T01 | Implement Resume Data Models | Not Started | Phase 0 |
| P1-T02 | Implement Job Description Models | Not Started | Phase 0 |
| P1-T03 | Implement Configuration Models | Not Started | Phase 0 |
| P1-T04 | Implement Profile CSV Parser | Not Started | P1-T01 |
| P1-T05 | Implement Positions CSV Parser | Not Started | P1-T01 |
| P1-T06 | Implement Skills CSV Parser | Not Started | P1-T01 |
| P1-T07 | Implement Remaining CSV Parsers | Not Started | P1-T01 |
| P1-T08 | Implement LinkedIn Parser Orchestrator | Not Started | P1-T04 through P1-T07 |
| P1-T09 | Implement Base HTML Template | Not Started | P1-T01 |
| P1-T10 | Implement Style Templates | Not Started | P1-T09 |
| P1-T11 | Implement HTML Generator | Not Started | P1-T09, P1-T10 |
| P1-T12 | Implement PDF and DOCX Generators | Not Started | P1-T11 |

---

## P1-T01: Implement Resume Data Models

**Description**: Implement the Pydantic models for all resume sections (Profile, Position, Education, Skill, Certification, Project, Publication, Language, Volunteer, Honor) and the aggregate Resume model. Tests already exist in RED state.

**Status**: Not Started

### User Story

As a developer, I need well-defined data models so that resume data is validated, typed, and consistent throughout the application.

### Acceptance Criteria

- [ ] All models from `tests/unit/test_models.py` are implemented
- [ ] All existing tests pass (GREEN state)
- [ ] Models use Pydantic v2 syntax
- [ ] All fields have type hints
- [ ] Optional fields have sensible defaults
- [ ] Computed properties work (full_name, is_current, duration, sorted_positions)
- [ ] Models are JSON serializable
- [ ] 90%+ test coverage

### Implementation Steps

1. Review existing tests in `tests/unit/test_models.py` (RED)
2. Implement models in `src/resume_builder/models/resume.py`:
   - `Profile` - name, headline, summary, location, industry
   - `Position` - company, title, dates, description, location
   - `Education` - school, degree, dates, activities
   - `Skill` - name, category
   - `Certification` - name, authority, dates, url
   - `Project` - title, description, url, dates
   - `Publication` - title, publisher, date, url
   - `Language` - name, proficiency
   - `Volunteer` - organization, role, cause, dates
   - `Honor` - title, issuer, date, description
   - `Resume` - aggregate model with all sections
3. Run tests: `pytest tests/unit/test_models.py -v`
4. Ensure all tests pass (GREEN)
5. Run coverage check

### Test Expectations

**Existing tests in** `tests/unit/test_models.py`:
- Tests already written (RED state)
- Run `pytest tests/unit/test_models.py` - should FAIL before implementation
- After implementation, all tests should PASS

**Additional tests to add:**
```python
def test_profile_json_serialization():
    """Profile can be serialized to JSON."""

def test_resume_model_validation():
    """Resume validates nested models correctly."""

def test_language_model():
    """Language model with name and proficiency."""

def test_volunteer_model():
    """Volunteer experience model."""

def test_honor_model():
    """Awards/honors model."""
```

### Files to Create/Modify

- Create: `src/resume_builder/models/resume.py`
- Modify: `src/resume_builder/models/__init__.py` (export models)
- Modify: `tests/unit/test_models.py` (add missing model tests)

### Commit Messages

**RED phase (if adding new tests):**
```
test: add tests for Language, Volunteer, Honor models
```

**GREEN phase:**
```
feat: implement resume data models

- Add Profile, Position, Education, Skill models
- Add Certification, Project, Publication models
- Add Language, Volunteer, Honor models
- Add aggregate Resume model with sorting
- All models use Pydantic v2 with full type hints
```

### Model Specifications

```python
class Profile(BaseModel):
    first_name: str
    last_name: str
    headline: str
    summary: str | None = None
    industry: str | None = None
    location: str | None = None

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Position(BaseModel):
    company: str
    title: str
    start_date: date
    end_date: date | None = None
    description: str | None = None
    location: str | None = None

    @computed_field
    @property
    def is_current(self) -> bool:
        return self.end_date is None

    @computed_field
    @property
    def duration(self) -> str:
        # Calculate human-readable duration
        ...
```

---

## P1-T02: Implement Job Description Models

**Description**: Implement Pydantic models for job descriptions including extracted requirements, skill categories, and match scoring structures.

**Status**: Not Started

### User Story

As a developer, I need job description models so that job requirements can be structured, compared against resumes, and scored.

### Acceptance Criteria

- [ ] `JobDescription` model captures raw job posting data
- [ ] `JobRequirements` model structures extracted requirements
- [ ] `MatchScore` model represents scoring results
- [ ] `SkillGap` model represents missing skills
- [ ] All models have validation and type hints
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement models in `src/resume_builder/models/job.py`:
   - `JobDescription` - title, company, raw_text, url
   - `JobRequirements` - required_skills, preferred_skills, experience_years, education
   - `MatchScore` - overall_score, section_scores, confidence
   - `SkillGap` - skill_name, importance, suggestion
3. Run tests (GREEN)
4. Refactor if needed

### Test Expectations

**File**: `tests/unit/test_job_models.py`

```python
def test_job_description_creation():
    """JobDescription can be created with required fields."""

def test_job_requirements_skill_lists():
    """JobRequirements separates required and preferred skills."""

def test_match_score_validation():
    """MatchScore validates score is 0-100."""

def test_skill_gap_model():
    """SkillGap captures missing skill info."""
```

### Files to Create/Modify

- Create: `src/resume_builder/models/job.py`
- Modify: `src/resume_builder/models/__init__.py`
- Create: `tests/unit/test_job_models.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for job description models
```

**GREEN phase:**
```
feat: implement job description and matching models

- Add JobDescription for raw posting data
- Add JobRequirements for structured extraction
- Add MatchScore for scoring results
- Add SkillGap for gap analysis
```

---

## P1-T03: Implement Configuration Models

**Description**: Implement Pydantic models for application configuration including contact info, user preferences, and job targets. Include JSON schema generation.

**Status**: Not Started

### User Story

As a user, I need a configuration system so that my contact information and preferences are stored securely and validated.

### Acceptance Criteria

- [ ] `ContactInfo` model for user contact details
- [ ] `UserPreferences` model for resume preferences
- [ ] `JobTarget` model for saved job targets
- [ ] `AppConfig` model aggregating all config
- [ ] Config loads from `config.local.json`
- [ ] Validation errors provide helpful messages
- [ ] Schema can be exported for IDE support
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement models in `src/resume_builder/models/config.py`:
   - `ContactInfo` - email, phone, urls, location
   - `UserPreferences` - default_style, default_length, accent_color, sections
   - `JobTarget` - id, title, company, description_file
   - `AppConfig` - contact, preferences, job_targets
3. Implement `src/resume_builder/config.py`:
   - `load_config(path: Path) -> AppConfig`
   - `save_config(config: AppConfig, path: Path)`
4. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_config_models.py`

```python
def test_contact_info_email_validation():
    """ContactInfo validates email format."""

def test_user_preferences_defaults():
    """UserPreferences has sensible defaults."""

def test_app_config_from_json():
    """AppConfig can load from JSON file."""

def test_config_validation_error_messages():
    """Invalid config produces helpful error messages."""
```

### Files to Create/Modify

- Create: `src/resume_builder/models/config.py`
- Create: `src/resume_builder/config.py`
- Modify: `src/resume_builder/models/__init__.py`
- Create: `tests/unit/test_config_models.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for configuration models
```

**GREEN phase:**
```
feat: implement configuration models and loading

- Add ContactInfo, UserPreferences, JobTarget models
- Add AppConfig aggregate model
- Implement config loading from JSON
- Add email and URL validation
```

---

## P1-T04: Implement Profile CSV Parser

**Description**: Implement parser for LinkedIn `Profile.csv` that extracts name, headline, summary, industry, and location fields.

**Status**: Not Started

### User Story

As a user, I need my LinkedIn profile data parsed so that my name, headline, and summary appear correctly on my resume.

### Acceptance Criteria

- [ ] Parses valid `Profile.csv` into `Profile` model
- [ ] Handles missing optional fields gracefully
- [ ] Returns helpful errors for malformed CSV
- [ ] Works with fixture data from `tests/fixtures/linkedin/`
- [ ] Logs warnings for unexpected columns
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests using fixtures (RED)
2. Implement `src/resume_builder/parsers/csv_handlers.py`:
   - `parse_profile_csv(path: Path) -> Profile`
3. Handle edge cases: empty file, missing columns, extra columns
4. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_parsers.py`

```python
def test_parse_valid_profile(valid_profile_fixture):
    """Parses valid Profile.csv correctly."""

def test_parse_profile_missing_optional_fields():
    """Handles missing summary, industry gracefully."""

def test_parse_profile_malformed_csv():
    """Returns error for invalid CSV format."""

def test_parse_profile_logs_unknown_columns(caplog):
    """Logs warning for unexpected columns."""
```

### Files to Create/Modify

- Create: `src/resume_builder/parsers/csv_handlers.py`
- Modify: `src/resume_builder/parsers/__init__.py`
- Create: `tests/unit/test_parsers.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for profile CSV parser
```

**GREEN phase:**
```
feat: implement Profile.csv parser

- Parse LinkedIn profile export
- Handle missing optional fields
- Log warnings for unknown columns
- Validate required fields
```

---

## P1-T05: Implement Positions CSV Parser

**Description**: Implement parser for LinkedIn `Positions.csv` that extracts work history with proper date parsing and description handling.

**Status**: Not Started

### User Story

As a user, I need my work history parsed so that all my positions appear correctly with proper dates and descriptions.

### Acceptance Criteria

- [ ] Parses valid `Positions.csv` into list of `Position` models
- [ ] Correctly parses LinkedIn date formats
- [ ] Handles current positions (no end date)
- [ ] Preserves multi-line descriptions
- [ ] Sorts positions by start date (newest first)
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement in `src/resume_builder/parsers/csv_handlers.py`:
   - `parse_positions_csv(path: Path) -> list[Position]`
   - `_parse_linkedin_date(date_str: str) -> date | None`
3. Handle edge cases: empty positions, bad dates
4. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_parsers.py` (add to existing)

```python
def test_parse_valid_positions(valid_positions_fixture):
    """Parses Positions.csv correctly."""

def test_parse_positions_date_formats():
    """Handles various LinkedIn date formats."""

def test_parse_current_position():
    """Current position has no end_date."""

def test_parse_positions_sorted():
    """Positions are sorted newest first."""

def test_parse_positions_multiline_description():
    """Preserves line breaks in descriptions."""
```

### Files to Create/Modify

- Modify: `src/resume_builder/parsers/csv_handlers.py`
- Modify: `tests/unit/test_parsers.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for positions CSV parser
```

**GREEN phase:**
```
feat: implement Positions.csv parser

- Parse LinkedIn work history
- Handle various date formats
- Support current positions (no end date)
- Sort positions by date descending
```

---

## P1-T06: Implement Skills CSV Parser

**Description**: Implement parser for LinkedIn `Skills.csv` with optional skill categorization logic.

**Status**: Not Started

### User Story

As a user, I need my skills parsed and optionally categorized so that they display organized on my resume.

### Acceptance Criteria

- [ ] Parses valid `Skills.csv` into list of `Skill` models
- [ ] Handles skills without categories
- [ ] Optional: auto-categorize common skills (languages, frameworks, tools)
- [ ] Removes duplicates
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement in `src/resume_builder/parsers/csv_handlers.py`:
   - `parse_skills_csv(path: Path, categorize: bool = False) -> list[Skill]`
   - `_categorize_skill(skill_name: str) -> str | None`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_parsers.py` (add to existing)

```python
def test_parse_valid_skills(valid_skills_fixture):
    """Parses Skills.csv correctly."""

def test_parse_skills_no_duplicates():
    """Removes duplicate skills."""

def test_categorize_programming_languages():
    """Categorizes Python, Java, etc. as languages."""

def test_categorize_frameworks():
    """Categorizes React, Django, etc. as frameworks."""
```

### Files to Create/Modify

- Modify: `src/resume_builder/parsers/csv_handlers.py`
- Modify: `tests/unit/test_parsers.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for skills CSV parser
```

**GREEN phase:**
```
feat: implement Skills.csv parser with categorization

- Parse LinkedIn skills export
- Remove duplicate skills
- Optional auto-categorization for common skills
```

---

## P1-T07: Implement Remaining CSV Parsers

**Description**: Implement parsers for Education, Certifications, Projects, Publications, Languages, Honors, and Volunteer CSVs.

**Status**: Not Started

### User Story

As a user, I need all my LinkedIn data parsed so that my complete professional history is available for resume generation.

### Acceptance Criteria

- [ ] `parse_education_csv` → list of `Education`
- [ ] `parse_certifications_csv` → list of `Certification`
- [ ] `parse_projects_csv` → list of `Project`
- [ ] `parse_publications_csv` → list of `Publication`
- [ ] `parse_languages_csv` → list of `Language`
- [ ] `parse_honors_csv` → list of `Honor`
- [ ] `parse_volunteer_csv` → list of `Volunteer`
- [ ] All parsers handle missing files gracefully (return empty list)
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests for each parser (RED)
2. Implement each parser in `csv_handlers.py`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_parsers.py` (add to existing)

```python
def test_parse_education_csv():
    """Parses Education.csv correctly."""

def test_parse_certifications_csv():
    """Parses Certifications.csv correctly."""

def test_parse_missing_csv_returns_empty():
    """Missing CSV file returns empty list, not error."""

# ... similar for other parsers
```

### Files to Create/Modify

- Modify: `src/resume_builder/parsers/csv_handlers.py`
- Modify: `tests/unit/test_parsers.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for remaining CSV parsers
```

**GREEN phase:**
```
feat: implement remaining LinkedIn CSV parsers

- Add Education, Certifications parsers
- Add Projects, Publications parsers
- Add Languages, Honors, Volunteer parsers
- Handle missing files gracefully
```

---

## P1-T08: Implement LinkedIn Parser Orchestrator

**Description**: Implement the main LinkedIn parser that coordinates all CSV parsers and assembles a complete Resume object from a LinkedIn data export.

**Status**: Not Started

### User Story

As a user, I need to upload my LinkedIn export and get a complete Resume object so that I can generate my resume.

### Acceptance Criteria

- [ ] Accepts path to LinkedIn export directory or ZIP file
- [ ] Coordinates all individual CSV parsers
- [ ] Assembles complete `Resume` object
- [ ] Reports which files were found/missing
- [ ] Handles partial exports (some CSVs missing)
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/parsers/linkedin.py`:
   - `parse_linkedin_export(path: Path) -> Resume`
   - `_extract_zip(zip_path: Path) -> Path` (if ZIP)
   - `_discover_csv_files(dir_path: Path) -> dict[str, Path]`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_linkedin_parser.py`

```python
def test_parse_complete_export(sample_data_dir):
    """Parses complete LinkedIn export to Resume."""

def test_parse_partial_export():
    """Handles missing optional CSV files."""

def test_parse_zip_export():
    """Extracts and parses ZIP file."""

def test_parse_reports_found_files():
    """Returns info about which files were processed."""
```

### Files to Create/Modify

- Create: `src/resume_builder/parsers/linkedin.py`
- Modify: `src/resume_builder/parsers/__init__.py`
- Create: `tests/unit/test_linkedin_parser.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for LinkedIn parser orchestrator
```

**GREEN phase:**
```
feat: implement LinkedIn export parser orchestrator

- Coordinate all CSV parsers
- Support directory or ZIP input
- Assemble complete Resume object
- Handle partial exports gracefully
```

---

## P1-T09: Implement Base HTML Template

**Description**: Create the base Jinja2 HTML template with semantic structure, accessibility features, and CSS hooks for styling.

**Status**: Not Started

### User Story

As a user, I need an accessible HTML resume template so that my resume looks professional and works with screen readers.

### Acceptance Criteria

- [ ] `templates/base.html` with semantic HTML5 structure
- [ ] Proper heading hierarchy (h1 for name, h2 for sections)
- [ ] ARIA landmarks for navigation
- [ ] Print-friendly CSS media queries
- [ ] CSS custom properties for theming
- [ ] Passes automated accessibility checks
- [ ] Test renders without errors

### Implementation Steps

1. Write failing tests for template rendering (RED)
2. Create `src/resume_builder/templates/base.html`:
   - Header section (name, title, contact)
   - Main content sections with proper headings
   - Print stylesheet
   - CSS custom property hooks
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_templates.py`

```python
def test_base_template_renders(sample_resume):
    """Base template renders without Jinja errors."""

def test_template_has_proper_headings():
    """Template has correct heading hierarchy."""

def test_template_has_aria_landmarks():
    """Template includes ARIA landmarks."""

def test_template_has_print_styles():
    """Template includes print media queries."""
```

### Files to Create/Modify

- Create: `src/resume_builder/templates/base.html`
- Create: `src/resume_builder/static/css/base.css`
- Create: `tests/unit/test_templates.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for base HTML template
```

**GREEN phase:**
```
feat: implement accessible base HTML template

- Add semantic HTML5 structure
- Include ARIA landmarks
- Add print-friendly styles
- Support CSS custom properties for theming
```

---

## P1-T10: Implement Style Templates

**Description**: Create the four style variant templates (Classic, Modern, Tech-Forward, ATS-Optimized) extending the base template.

**Status**: Not Started

### User Story

As a user, I need multiple style options so that I can choose the resume appearance that best fits my target industry.

### Acceptance Criteria

- [ ] `templates/classic.html` - serif fonts, conservative
- [ ] `templates/modern.html` - sans-serif, whitespace
- [ ] `templates/tech.html` - color sidebar, modern
- [ ] `templates/ats.html` - plain, ATS-optimized
- [ ] Each style has matching CSS file
- [ ] All styles meet contrast requirements (4.5:1)
- [ ] All styles render consistently
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests for each style (RED)
2. Create style templates extending base.html
3. Create corresponding CSS files
4. Verify contrast ratios
5. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_templates.py` (add to existing)

```python
@pytest.mark.parametrize("style", ["classic", "modern", "tech", "ats"])
def test_style_template_renders(style, sample_resume):
    """Each style template renders correctly."""

def test_classic_uses_serif_font():
    """Classic template uses serif font family."""

def test_ats_has_no_colors():
    """ATS template has black text only."""

def test_all_styles_meet_contrast_ratio():
    """All styles have 4.5:1 contrast minimum."""
```

### Files to Create/Modify

- Create: `src/resume_builder/templates/classic.html`
- Create: `src/resume_builder/templates/modern.html`
- Create: `src/resume_builder/templates/tech.html`
- Create: `src/resume_builder/templates/ats.html`
- Create: `src/resume_builder/static/css/classic.css`
- Create: `src/resume_builder/static/css/modern.css`
- Create: `src/resume_builder/static/css/tech.css`
- Create: `src/resume_builder/static/css/ats.css`
- Modify: `tests/unit/test_templates.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for style templates
```

**GREEN phase:**
```
feat: implement four resume style templates

- Add Classic style (serif, conservative)
- Add Modern style (sans-serif, whitespace)
- Add Tech-Forward style (color sidebar)
- Add ATS-Optimized style (plain text)
- All styles meet WCAG contrast requirements
```

---

## P1-T11: Implement HTML Generator

**Description**: Implement the HTML generator that renders Resume objects to HTML using Jinja2 templates with style selection.

**Status**: Not Started

### User Story

As a user, I need to generate HTML resumes so that I can view, print, or convert them to other formats.

### Acceptance Criteria

- [ ] `generate_html(resume, style, length) -> str`
- [ ] Renders using correct style template
- [ ] Respects length setting (1-page, 2-page, CV)
- [ ] Generated HTML is valid
- [ ] Generated HTML is accessible
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/generators/html.py`:
   - `HTMLGenerator` class
   - `generate(resume: Resume, style: str, length: str) -> str`
   - Template loading and rendering
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_generators.py`

```python
def test_generate_html_classic(sample_resume):
    """Generates valid HTML with classic style."""

def test_generate_html_respects_length():
    """1-page output has fewer sections than CV."""

def test_generated_html_is_valid():
    """Output is valid HTML5."""

def test_generate_html_unknown_style_raises():
    """Unknown style raises ValueError."""
```

### Files to Create/Modify

- Create: `src/resume_builder/generators/html.py`
- Modify: `src/resume_builder/generators/__init__.py`
- Create: `tests/unit/test_generators.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for HTML generator
```

**GREEN phase:**
```
feat: implement HTML resume generator

- Add HTMLGenerator class
- Support style selection
- Support length configuration
- Render using Jinja2 templates
```

---

## P1-T12: Implement PDF and DOCX Generators

**Description**: Implement PDF generation using WeasyPrint and DOCX generation using python-docx, maintaining visual consistency with HTML output.

**Status**: Not Started

### User Story

As a user, I need to export my resume as PDF and DOCX so that I can submit it to job applications in standard formats.

### Acceptance Criteria

- [ ] `generate_pdf(resume, style, length) -> bytes`
- [ ] `generate_docx(resume, style, length) -> bytes`
- [ ] PDF output matches HTML visually
- [ ] DOCX is properly formatted Word document
- [ ] Both handle special characters correctly
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/generators/pdf.py`:
   - Uses WeasyPrint to convert HTML to PDF
3. Implement `src/resume_builder/generators/docx.py`:
   - Uses python-docx to build Word document
4. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_generators.py` (add to existing)

```python
def test_generate_pdf(sample_resume):
    """Generates valid PDF bytes."""

def test_pdf_is_valid_pdf(sample_resume):
    """Output bytes are valid PDF format."""

def test_generate_docx(sample_resume):
    """Generates valid DOCX bytes."""

def test_docx_is_valid_docx(sample_resume):
    """Output bytes are valid DOCX format."""
```

### Files to Create/Modify

- Create: `src/resume_builder/generators/pdf.py`
- Create: `src/resume_builder/generators/docx.py`
- Modify: `src/resume_builder/generators/__init__.py`
- Modify: `tests/unit/test_generators.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for PDF and DOCX generators
```

**GREEN phase:**
```
feat: implement PDF and DOCX generators

- Add PDF generation via WeasyPrint
- Add DOCX generation via python-docx
- Maintain visual consistency with HTML
- Handle special characters correctly
```

---

## Phase Completion Criteria

- [ ] All resume models implemented with 90%+ coverage
- [ ] All CSV parsers handle valid and malformed input
- [ ] LinkedIn orchestrator assembles complete Resume objects
- [ ] All 4 style templates render correctly
- [ ] HTML, PDF, and DOCX outputs are visually consistent
- [ ] No PII in any committed code or tests
- [ ] All pre-commit hooks pass

---

## Phase 1 Completion Checklist

Before moving to Phase 2, verify:

```bash
# All tests pass
pytest tests/unit/ -v --cov=src/resume_builder --cov-fail-under=90

# Can parse sample data
python -c "from resume_builder.parsers.linkedin import parse_linkedin_export; print(parse_linkedin_export('sample_data/'))"

# Can generate HTML
python -c "from resume_builder.generators.html import HTMLGenerator; ..."

# All hooks pass
pre-commit run --all-files
```

# Phase 3: Review & Polish

> **Goal**: Implement the QA and HR review agents, ensure accessibility compliance, and build the web interface.

**Status**: Not Started
**Progress**: 0/8 tasks complete
**Depends On**: Phase 1 complete (can run parallel to Phase 2)

---

## Task Summary

| ID | Task | Status | Dependencies |
|----|------|--------|--------------|
| P3-T01 | Implement QA Agent Tools | Not Started | Phase 1, P2-T01 |
| P3-T02 | Implement QA Review Agent | Not Started | P3-T01 |
| P3-T03 | Implement HR Agent Tools | Not Started | Phase 1, P2-T01 |
| P3-T04 | Implement HR Review Agent | Not Started | P3-T03 |
| P3-T05 | Implement Accessibility Validation | Not Started | P1-T11 |
| P3-T06 | Implement FastAPI Application | Not Started | Phase 1 |
| P3-T07 | Implement Web Interface | Not Started | P3-T06 |
| P3-T08 | Implement Progress Indicators | Not Started | P3-T06, P2-T09 |

---

## P3-T01: Implement QA Agent Tools

**Description**: Implement the custom tools for the QA Review Agent: `check_accessibility`, `evaluate_layout`, `verify_contrast`, `check_print_quality`.

**Status**: Not Started

### User Story

As a QA Agent, I need tools to evaluate resume quality so that I can ensure accessibility and visual consistency.

### Acceptance Criteria

- [ ] `check_accessibility` validates WCAG 2.1 AA compliance
- [ ] `evaluate_layout` assesses visual hierarchy
- [ ] `verify_contrast` checks color contrast ratios
- [ ] `check_print_quality` validates print rendering
- [ ] All tools have proper JSON schemas
- [ ] Tools return actionable feedback
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement tools in `src/resume_builder/agents/tools/review.py`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_review_tools.py`

```python
def test_check_accessibility_heading_hierarchy():
    """check_accessibility validates heading order."""

def test_check_accessibility_alt_text():
    """check_accessibility verifies image alt text."""

def test_verify_contrast_ratio():
    """verify_contrast calculates and validates ratios."""

def test_evaluate_layout_whitespace():
    """evaluate_layout checks for adequate whitespace."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/tools/review.py`
- Create: `tests/unit/test_agents/test_review_tools.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for QA agent tools
```

**GREEN phase:**
```
feat: implement QA agent review tools

- Add check_accessibility for WCAG validation
- Add evaluate_layout for visual hierarchy
- Add verify_contrast for color checking
- Add check_print_quality for print validation
```

---

## P3-T02: Implement QA Review Agent

**Description**: Implement the QA Review Agent that evaluates visual hierarchy, checks WCAG 2.1 AA compliance, and verifies print/PDF rendering quality.

**Status**: Not Started

### User Story

As a user, I need QA review so that my resume meets accessibility standards and looks professional.

### Acceptance Criteria

- [ ] `QAAgent` extends `BaseAgent`
- [ ] Registers review tools
- [ ] Evaluates visual hierarchy and balance
- [ ] Checks WCAG 2.1 AA compliance
- [ ] Verifies contrast ratios (4.5:1 minimum)
- [ ] Assesses print rendering quality
- [ ] Returns `QAReport` with issues and suggestions
- [ ] 90%+ test coverage with mocked API

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/agents/qa_agent.py`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_qa_agent.py`

```python
def test_qa_agent_checks_accessibility(mock_anthropic):
    """QA agent validates accessibility requirements."""

def test_qa_agent_evaluates_layout(mock_anthropic):
    """QA agent assesses visual hierarchy."""

def test_qa_agent_returns_report(mock_anthropic):
    """QA agent returns structured QAReport."""

def test_qa_agent_flags_contrast_issues(mock_anthropic):
    """QA agent catches low contrast colors."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/qa_agent.py`
- Modify: `src/resume_builder/agents/__init__.py`
- Create: `tests/unit/test_agents/test_qa_agent.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for QA review agent
```

**GREEN phase:**
```
feat: implement QA review agent

- Add QAAgent extending BaseAgent
- Evaluate visual hierarchy and layout
- Check WCAG 2.1 AA compliance
- Verify contrast ratios
- Generate structured QA report
```

---

## P3-T03: Implement HR Agent Tools

**Description**: Implement the custom tools for the HR Review Agent: `check_grammar`, `validate_formatting`, `assess_professionalism`, `detect_placeholders`.

**Status**: Not Started

### User Story

As an HR Agent, I need tools to check resume quality from an HR perspective so that I can catch common issues.

### Acceptance Criteria

- [ ] `check_grammar` finds spelling and grammar issues
- [ ] `validate_formatting` checks date consistency
- [ ] `assess_professionalism` evaluates tone
- [ ] `detect_placeholders` finds leftover template text
- [ ] All tools have proper JSON schemas
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement tools in `src/resume_builder/agents/tools/review.py` (add to existing)
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_review_tools.py` (add to existing)

```python
def test_check_grammar_finds_errors():
    """check_grammar catches spelling mistakes."""

def test_validate_formatting_date_consistency():
    """validate_formatting catches inconsistent date formats."""

def test_detect_placeholders_finds_lorem():
    """detect_placeholders catches Lorem ipsum."""

def test_detect_placeholders_finds_xxx():
    """detect_placeholders catches XXX markers."""
```

### Files to Create/Modify

- Modify: `src/resume_builder/agents/tools/review.py`
- Modify: `tests/unit/test_agents/test_review_tools.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for HR agent tools
```

**GREEN phase:**
```
feat: implement HR agent review tools

- Add check_grammar for spelling/grammar
- Add validate_formatting for consistency
- Add assess_professionalism for tone
- Add detect_placeholders for template text
```

---

## P3-T04: Implement HR Review Agent

**Description**: Implement the HR Review Agent that checks spelling/grammar, verifies consistent formatting, ensures proper capitalization, and flags inconsistencies.

**Status**: Not Started

### User Story

As a user, I need HR review so that my resume doesn't have embarrassing typos or formatting issues.

### Acceptance Criteria

- [ ] `HRAgent` extends `BaseAgent`
- [ ] Registers HR review tools
- [ ] Checks spelling and grammar
- [ ] Verifies consistent date formatting
- [ ] Ensures proper capitalization
- [ ] Detects placeholder text
- [ ] Assesses professional tone
- [ ] Returns `HRReport` with issues
- [ ] 90%+ test coverage with mocked API

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/agents/hr_agent.py`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_hr_agent.py`

```python
def test_hr_agent_checks_grammar(mock_anthropic):
    """HR agent finds spelling errors."""

def test_hr_agent_validates_dates(mock_anthropic):
    """HR agent catches inconsistent date formats."""

def test_hr_agent_detects_placeholders(mock_anthropic):
    """HR agent finds leftover template text."""

def test_hr_agent_returns_report(mock_anthropic):
    """HR agent returns structured HRReport."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/hr_agent.py`
- Modify: `src/resume_builder/agents/__init__.py`
- Create: `tests/unit/test_agents/test_hr_agent.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for HR review agent
```

**GREEN phase:**
```
feat: implement HR review agent

- Add HRAgent extending BaseAgent
- Check spelling and grammar
- Validate date formatting consistency
- Detect placeholder text
- Generate structured HR report
```

---

## P3-T05: Implement Accessibility Validation

**Description**: Implement automated accessibility validation for generated HTML including contrast checking, semantic structure validation, and ARIA attribute verification.

**Status**: Not Started

### User Story

As a developer, I need automated accessibility validation so that generated resumes meet WCAG standards without manual checking.

### Acceptance Criteria

- [ ] `AccessibilityValidator` class
- [ ] Validates heading hierarchy (h1 → h2 → h3)
- [ ] Checks color contrast (4.5:1 for normal, 3:1 for large)
- [ ] Verifies ARIA landmarks present
- [ ] Checks form labels associated correctly
- [ ] Returns structured validation report
- [ ] Can be run independently or via QA agent
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/utils/accessibility.py`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_accessibility.py`

```python
def test_validate_heading_hierarchy_valid():
    """Valid heading hierarchy passes."""

def test_validate_heading_hierarchy_skip():
    """Skipped heading level fails (h1 to h3)."""

def test_validate_contrast_passes():
    """Good contrast ratio passes."""

def test_validate_contrast_fails():
    """Low contrast ratio fails."""

def test_validate_aria_landmarks():
    """Required ARIA landmarks are present."""
```

### Files to Create/Modify

- Create: `src/resume_builder/utils/accessibility.py`
- Modify: `src/resume_builder/utils/__init__.py`
- Create: `tests/unit/test_accessibility.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for accessibility validation
```

**GREEN phase:**
```
feat: implement accessibility validation

- Add AccessibilityValidator class
- Check heading hierarchy
- Validate color contrast ratios
- Verify ARIA landmarks
- Generate validation report
```

---

## P3-T06: Implement FastAPI Application

**Description**: Implement the FastAPI application with routes for file upload, resume generation, and health checks. Include proper error handling and validation.

**Status**: Not Started

### User Story

As a user, I need a web API so that I can upload my data and generate resumes through a browser.

### Acceptance Criteria

- [ ] `POST /api/upload` accepts LinkedIn data files
- [ ] `POST /api/generate` generates resume with options
- [ ] `GET /api/health` returns health status
- [ ] `GET /docs` shows OpenAPI documentation
- [ ] File upload validates size and type
- [ ] Proper error responses (4xx, 5xx)
- [ ] CORS configured for local development
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/api/routes.py`
3. Implement `src/resume_builder/main.py` (FastAPI app)
4. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_api.py`

```python
def test_health_endpoint():
    """Health endpoint returns 200."""

def test_upload_valid_file(client, valid_csv):
    """Upload accepts valid CSV."""

def test_upload_invalid_file_type(client):
    """Upload rejects non-CSV files."""

def test_upload_file_too_large(client, large_file):
    """Upload rejects files over limit."""

def test_generate_returns_html(client, uploaded_data):
    """Generate returns HTML resume."""
```

### Files to Create/Modify

- Create: `src/resume_builder/api/__init__.py`
- Create: `src/resume_builder/api/routes.py`
- Create: `src/resume_builder/api/dependencies.py`
- Modify: `src/resume_builder/main.py`
- Create: `tests/unit/test_api.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for FastAPI application
```

**GREEN phase:**
```
feat: implement FastAPI application

- Add upload, generate, and health endpoints
- Implement file validation
- Add proper error handling
- Configure CORS and OpenAPI docs
```

---

## P3-T07: Implement Web Interface

**Description**: Implement the web interface with accessible forms for LinkedIn data upload, job description input, style selection, and resume preview.

**Status**: Not Started

### User Story

As a user, I need a web interface so that I can easily upload my data and generate resumes without using the API directly.

### Acceptance Criteria

- [ ] File upload form with drag-and-drop
- [ ] Job description text input
- [ ] Style selector (4 options)
- [ ] Length selector (1-page, 2-page, CV)
- [ ] Live preview of generated resume
- [ ] Download buttons for HTML, PDF, DOCX
- [ ] All forms are keyboard accessible
- [ ] Screen reader compatible
- [ ] 90%+ test coverage for JS (if any)

### Implementation Steps

1. Write failing tests (RED) - accessibility tests
2. Create HTML templates in `src/resume_builder/templates/`
3. Create CSS in `src/resume_builder/static/css/`
4. Create JS in `src/resume_builder/static/js/` (minimal, vanilla)
5. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_web_interface.py`

```python
def test_index_page_loads(client):
    """Index page returns 200."""

def test_form_has_labels(client):
    """All form inputs have associated labels."""

def test_form_keyboard_accessible(client):
    """Forms can be submitted via keyboard."""

def test_style_selector_options(client):
    """Style selector has 4 options."""
```

### Files to Create/Modify

- Create: `src/resume_builder/templates/index.html`
- Create: `src/resume_builder/templates/preview.html`
- Create: `src/resume_builder/static/css/app.css`
- Create: `src/resume_builder/static/js/app.js`
- Modify: `tests/unit/test_web_interface.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for web interface accessibility
```

**GREEN phase:**
```
feat: implement accessible web interface

- Add file upload with drag-and-drop
- Add job description input
- Add style and length selectors
- Add resume preview
- Ensure keyboard and screen reader accessibility
```

---

## P3-T08: Implement Progress Indicators

**Description**: Implement real-time progress indicators showing agent processing stages during resume generation.

**Status**: Not Started

### User Story

As a user, I need progress feedback so that I know the system is working during resume generation.

### Acceptance Criteria

- [ ] Progress bar or step indicator UI
- [ ] Shows current agent/stage name
- [ ] Updates in real-time during processing
- [ ] Graceful handling of long operations
- [ ] Error state display
- [ ] Works with async/SSE or polling
- [ ] Accessible progress announcements
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement SSE endpoint or polling mechanism
3. Create progress UI component
4. Integrate with orchestrator progress callback
5. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_progress.py`

```python
def test_progress_endpoint_streams(client):
    """Progress endpoint streams updates."""

def test_progress_shows_stage_names():
    """Progress includes stage name."""

def test_progress_accessible_announcements():
    """Progress updates are announced to screen readers."""
```

### Files to Create/Modify

- Modify: `src/resume_builder/api/routes.py` (add progress endpoint)
- Modify: `src/resume_builder/static/js/app.js`
- Modify: `src/resume_builder/templates/index.html`
- Create: `tests/unit/test_progress.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for progress indicators
```

**GREEN phase:**
```
feat: implement progress indicators

- Add SSE endpoint for progress updates
- Create progress UI component
- Show current processing stage
- Ensure accessible announcements
```

---

## Phase Completion Criteria

- [ ] QA Agent validates accessibility and layout
- [ ] HR Agent checks grammar and formatting
- [ ] Accessibility validation catches WCAG violations
- [ ] FastAPI application handles all endpoints
- [ ] Web interface is accessible (keyboard nav, screen reader)
- [ ] Progress indicators show agent stages
- [ ] All forms have proper labels and error handling
- [ ] 90%+ test coverage maintained

---

## Phase 3 Completion Checklist

Before moving to Phase 4, verify:

```bash
# All tests pass
pytest tests/unit/ -v --cov=src/resume_builder --cov-fail-under=90

# API works
curl http://localhost:8000/api/health

# Web interface loads
open http://localhost:8000/

# Accessibility check passes
# (manual verification with screen reader)

# All hooks pass
pre-commit run --all-files
```

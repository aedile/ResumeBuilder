# Phase 0: Foundation

> **Goal**: Establish a clean, secure, fully-equipped development environment before writing any application code.

**Status**: Complete
**Progress**: 8/8 tasks complete

---

## Task Summary

| ID | Task | Status | Dependencies |
|----|------|--------|--------------|
| P0-T01 | Verify and Install Pre-commit Hooks | Complete | None |
| P0-T02 | Create Secrets Baseline | Complete | P0-T01 |
| P0-T03 | Setup Test Directory Structure | Complete | P0-T01 |
| P0-T04 | Create Sample LinkedIn Data | Complete | P0-T03 |
| P0-T05 | Create Test Fixtures | Complete | P0-T03, P0-T04 |
| P0-T06 | Setup Logging Configuration | Complete | P0-T01 |
| P0-T07 | Update Environment Configuration | Complete | P0-T01 |
| P0-T08 | Verify CI Pipeline | Complete | P0-T01 through P0-T07 |

---

## P0-T01: Verify and Install Pre-commit Hooks

**Description**: Ensure pre-commit hooks are properly installed and all hooks pass on the existing codebase. This establishes the security and quality foundation for all future work.

**Status**: Not Started

### User Story

As a developer, I need pre-commit hooks installed and working so that every commit is automatically checked for code quality, security issues, and secrets before it enters the repository.

### Acceptance Criteria

- [ ] `pre-commit --version` returns valid version
- [ ] `pre-commit install` completes without error
- [ ] `pre-commit install --hook-type commit-msg` installs commitizen hook
- [ ] `pre-commit run --all-files` passes (or only has expected failures in stub files)
- [ ] Running `git commit` triggers the hooks automatically
- [ ] All security hooks are active: gitleaks, detect-secrets, bandit

### Implementation Steps

1. Verify Python virtual environment is active
2. Install pre-commit: `pip install pre-commit`
3. Install hooks: `pre-commit install && pre-commit install --hook-type commit-msg`
4. Run all hooks: `pre-commit run --all-files`
5. Fix any failures in existing files (formatting, linting)
6. Verify hooks trigger on commit attempt

### Test Expectations

This is a tooling task - no pytest tests required. Verification is manual:
- `pre-commit run --all-files` exits with code 0

### Files to Create/Modify

- None (hooks already configured in `.pre-commit-config.yaml`)
- May need to fix existing files to pass hooks

### Commit Message

```
chore: verify and install pre-commit hooks

- Install pre-commit and all hook types
- Fix any existing files that fail hooks
- Verify security scanning is active
```

### Notes

- If mypy fails on stub `__init__.py` files, that's expected until models are implemented
- gitleaks may need gitleaks binary installed: `brew install gitleaks`
- detect-secrets may fail until baseline is created (P0-T02)

---

## P0-T02: Create Secrets Baseline

**Description**: Initialize the detect-secrets baseline file (`.secrets.baseline`) so the secret detection hook can track known false positives and detect new secrets.

**Status**: Not Started

### User Story

As a developer, I need a secrets baseline so that detect-secrets can distinguish between known safe patterns and actual leaked secrets.

### Acceptance Criteria

- [ ] `.secrets.baseline` file exists in repository root
- [ ] Baseline is generated from current codebase
- [ ] `detect-secrets scan` runs without errors
- [ ] Pre-commit detect-secrets hook passes
- [ ] `.secrets.baseline` is committed to repository

### Implementation Steps

1. Install detect-secrets: `pip install detect-secrets` <!-- pragma: allowlist secret -->
2. Generate baseline: `detect-secrets scan > .secrets.baseline`
3. Audit baseline: `detect-secrets audit .secrets.baseline`
4. Mark any false positives as safe
5. Run pre-commit to verify: `pre-commit run detect-secrets --all-files`

### Test Expectations

No pytest tests. Verification:
- `pre-commit run detect-secrets --all-files` exits with code 0

### Files to Create/Modify

- Create: `.secrets.baseline`

### Commit Message

```
chore: create detect-secrets baseline

- Generate initial secrets baseline
- Audit and mark false positives
- Enable secret detection in pre-commit
```

### Notes

- The `.secrets.baseline` file IS committed (not gitignored)
- Audit carefully - don't mark real secrets as false positives
- Sample data should not contain anything that looks like secrets

---

## P0-T03: Setup Test Directory Structure

**Description**: Create the proper test directory structure with unit/, integration/, and fixtures/ subdirectories. Move existing test file to proper location.

**Status**: Not Started

### User Story

As a developer, I need a well-organized test directory so that tests are easy to find, run selectively, and maintain.

### Acceptance Criteria

- [ ] `tests/unit/` directory exists
- [ ] `tests/integration/` directory exists
- [ ] `tests/fixtures/` directory exists with subdirectories
- [ ] `tests/fixtures/linkedin/` directory exists
- [ ] `tests/fixtures/jobs/` directory exists
- [ ] `tests/fixtures/api_responses/` directory exists
- [ ] Existing `test_models.py` moved to `tests/unit/test_models.py`
- [ ] `tests/__init__.py` exists
- [ ] `tests/unit/__init__.py` exists
- [ ] `tests/integration/__init__.py` exists
- [ ] `pytest tests/` runs without import errors

### Implementation Steps

1. Create directory structure:
   ```
   tests/
   ├── __init__.py
   ├── conftest.py (already exists)
   ├── unit/
   │   ├── __init__.py
   │   └── test_models.py (moved from tests/)
   ├── integration/
   │   └── __init__.py
   └── fixtures/
       ├── linkedin/
       ├── jobs/
       └── api_responses/
   ```
2. Move `tests/test_models.py` to `tests/unit/test_models.py`
3. Create `__init__.py` files
4. Update `conftest.py` fixture paths if needed
5. Run pytest to verify

### Test Expectations

Run: `pytest tests/ --collect-only`
- Should discover tests in `tests/unit/test_models.py`
- No import errors

### Files to Create/Modify

- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/integration/__init__.py`
- Move: `tests/test_models.py` → `tests/unit/test_models.py`
- Create directories: `tests/fixtures/linkedin/`, `tests/fixtures/jobs/`, `tests/fixtures/api_responses/`

### Commit Message

```
chore: setup test directory structure

- Create unit/, integration/, fixtures/ directories
- Move test_models.py to unit/
- Add __init__.py files for proper imports
- Organize fixtures by type
```

### Notes

- Keep `conftest.py` at `tests/` level for shared fixtures
- Fixture directories don't need `__init__.py` (not Python packages)

---

## P0-T04: Create Sample LinkedIn Data

**Description**: Create fictional but realistic LinkedIn export CSV files in `sample_data/` for the "Alex Chen" persona defined in requirements.

**Status**: Not Started

### User Story

As a developer or user, I need realistic sample LinkedIn data so I can test the application without using real personal information.

### Acceptance Criteria

- [ ] `sample_data/README.md` explains the sample data
- [ ] `sample_data/Profile.csv` with Alex Chen's profile
- [ ] `sample_data/Positions.csv` with 4 positions
- [ ] `sample_data/Skills.csv` with 25 skills
- [ ] `sample_data/Education.csv` with 2 degrees
- [ ] `sample_data/Certifications.csv` with 3 certifications
- [ ] `sample_data/Projects.csv` with 2 projects
- [ ] `sample_data/Publications.csv` with 1 publication
- [ ] `sample_data/Languages.csv` with 2 languages
- [ ] All data is clearly fictional (no real people/companies)
- [ ] CSV column headers match LinkedIn export format

### Implementation Steps

1. Create `sample_data/README.md` explaining the data
2. Research LinkedIn CSV export column headers
3. Create each CSV file with realistic but fictional data
4. Ensure dates are consistent and logical
5. Verify all files are valid CSV format

### Test Expectations

No pytest tests for sample data. Verification:
- All CSV files parse correctly with Python's csv module
- Column headers match expected LinkedIn format

### Files to Create/Modify

- Create: `sample_data/README.md`
- Create: `sample_data/Profile.csv`
- Create: `sample_data/Positions.csv`
- Create: `sample_data/Skills.csv`
- Create: `sample_data/Education.csv`
- Create: `sample_data/Certifications.csv`
- Create: `sample_data/Projects.csv`
- Create: `sample_data/Publications.csv`
- Create: `sample_data/Languages.csv`

### Commit Message

```
chore: create sample LinkedIn data for Alex Chen

- Add fictional ML engineer profile
- Include all CSV types from LinkedIn export
- Document sample data in README
```

### Sample Data Spec: Alex Chen

**Profile**:
- Name: Alex Chen
- Headline: Staff Machine Learning Engineer
- Location: San Francisco, CA
- Industry: Technology
- Summary: 12+ years building ML systems at scale...

**Positions** (4 total):
1. Staff ML Engineer @ TechVision AI (2021-present)
2. Senior ML Engineer @ DataFlow Inc (2018-2021)
3. ML Engineer @ CloudScale Systems (2015-2018)
4. Software Engineer @ StartupXYZ (2012-2015)

**Skills** (25): Python, PyTorch, TensorFlow, Kubernetes, AWS, etc.

**Education**:
1. MS Computer Science, Stanford University (2010-2012)
2. BS Mathematics, UC Berkeley (2006-2010)

---

## P0-T05: Create Test Fixtures

**Description**: Create test fixture files in `tests/fixtures/` including sample LinkedIn CSVs, job descriptions, and mocked API responses for agent testing.

**Status**: Not Started

### User Story

As a developer writing tests, I need reusable test fixtures so that tests are consistent, isolated, and don't require external dependencies.

### Acceptance Criteria

- [ ] `tests/fixtures/linkedin/` contains minimal valid CSV samples
- [ ] `tests/fixtures/linkedin/` contains malformed CSV samples for error testing
- [ ] `tests/fixtures/jobs/` contains sample job descriptions
- [ ] `tests/fixtures/api_responses/` contains mocked Claude API responses
- [ ] Fixtures are smaller/simpler than sample_data (for fast tests)
- [ ] `conftest.py` updated with fixture loading helpers

### Implementation Steps

1. Create minimal valid LinkedIn CSVs (1-2 records each)
2. Create malformed CSVs (missing columns, bad dates, etc.)
3. Create 2-3 sample job descriptions (ML Engineer roles)
4. Create mocked Claude API response JSON files
5. Update `conftest.py` with fixtures for loading these files

### Test Expectations

After this task:
- `pytest tests/ --collect-only` still works
- Fixture functions in conftest.py are discoverable

### Files to Create/Modify

**Create:**
- `tests/fixtures/linkedin/valid_profile.csv`
- `tests/fixtures/linkedin/valid_positions.csv`
- `tests/fixtures/linkedin/valid_skills.csv`
- `tests/fixtures/linkedin/malformed_dates.csv`
- `tests/fixtures/linkedin/missing_columns.csv`
- `tests/fixtures/jobs/ml_engineer_job.txt`
- `tests/fixtures/jobs/senior_swe_job.txt`
- `tests/fixtures/api_responses/parser_response.json`
- `tests/fixtures/api_responses/matcher_response.json`

**Modify:**
- `tests/conftest.py` - add fixture loading functions

### Commit Message

```
chore: create test fixtures

- Add minimal LinkedIn CSV fixtures
- Add malformed CSV fixtures for error testing
- Add sample job descriptions
- Add mocked Claude API response fixtures
- Update conftest.py with fixture loaders
```

### Notes

- Test fixtures should be minimal - just enough to test functionality
- Include edge cases: empty files, unicode characters, very long text
- API response fixtures should match Anthropic's actual response format

---

## P0-T06: Setup Logging Configuration

**Description**: Implement the logging utility module with structured JSON logging, log levels, and PII filtering as specified in NFR-8.

**Status**: Not Started

### User Story

As a developer, I need structured logging so that I can debug issues, trace agent decisions, and ensure no PII is accidentally logged.

### Acceptance Criteria

- [ ] `src/resume_builder/utils/logging.py` exists
- [ ] Logging outputs structured JSON format
- [ ] Log levels (DEBUG, INFO, WARNING, ERROR) work correctly
- [ ] PII filter prevents logging of emails, phones, names
- [ ] Logs write to `logs/` directory (gitignored)
- [ ] Correlation ID support for request tracing
- [ ] 90%+ test coverage for logging module

### Implementation Steps

1. Write failing tests for logging module (RED)
2. Implement `src/resume_builder/utils/logging.py`:
   - `setup_logging(level: str) -> Logger`
   - `get_logger(name: str) -> Logger`
   - `PIIFilter` class to redact sensitive data
   - JSON formatter for structured output
3. Ensure tests pass (GREEN)
4. Refactor if needed

### Test Expectations

**File**: `tests/unit/test_logging.py`

```python
def test_setup_logging_creates_logger():
    """Logger is created with correct level."""

def test_json_format_output():
    """Log output is valid JSON."""

def test_pii_filter_redacts_email():
    """Emails are replaced with [REDACTED]."""

def test_pii_filter_redacts_phone():
    """Phone numbers are replaced with [REDACTED]."""

def test_correlation_id_included():
    """Correlation ID appears in log output."""
```

### Files to Create/Modify

- Create: `src/resume_builder/utils/__init__.py`
- Create: `src/resume_builder/utils/logging.py`
- Create: `tests/unit/test_logging.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for logging configuration
```

**GREEN phase:**
```
feat: implement structured JSON logging with PII filter

- Add setup_logging and get_logger functions
- Implement PIIFilter to redact sensitive data
- Output logs as structured JSON
- Support correlation IDs for tracing
```

### Notes

- Use Python's built-in `logging` module as base
- Consider `structlog` for JSON formatting (already in requirements)
- PII patterns to filter: email regex, phone regex, common name patterns

---

## P0-T07: Update Environment Configuration

**Description**: Create complete `.env.example` file with all required and optional environment variables documented. Create config schema file.

**Status**: Not Started

### User Story

As a developer, I need clear documentation of all environment variables so I can configure the application correctly without guessing.

### Acceptance Criteria

- [ ] `.env.example` contains all variables from REQUIREMENTS.md
- [ ] Each variable has a comment explaining its purpose
- [ ] Required vs optional is clearly marked
- [ ] Default values are documented
- [ ] `config.schema.json` exists for config.local.json validation
- [ ] `.env.example` is committed (safe, no real values)

### Implementation Steps

1. Review REQUIREMENTS.md for all environment variables
2. Update `.env.example` with full documentation
3. Create `config.schema.json` for config.local.json
4. Verify schema validates the example config structure

### Test Expectations

No pytest tests. Verification:
- `.env.example` exists and is well-documented
- `config.schema.json` is valid JSON Schema

### Files to Create/Modify

- Modify: `.env.example` (expand with all variables)
- Create: `config.schema.json`

### Commit Message

```
chore: complete environment configuration documentation

- Document all environment variables in .env.example
- Add config.schema.json for config validation
- Mark required vs optional variables
```

### Environment Variables to Document

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx  # Claude API key

# Optional (with defaults)
LOG_LEVEL=INFO                # DEBUG, INFO, WARNING, ERROR
MAX_UPLOAD_SIZE_MB=10         # Maximum file upload size
API_TIMEOUT_SECONDS=30        # Claude API request timeout
ENABLE_CACHE=true             # Enable response caching
```

---

## P0-T08: Verify CI Pipeline

**Description**: Run the full CI pipeline locally and ensure all checks pass. Fix any issues with the GitHub Actions workflow.

**Status**: Not Started

### User Story

As a developer, I need the CI pipeline working so that all code changes are automatically validated before merge.

### Acceptance Criteria

- [ ] All local quality checks pass:
  - [ ] `ruff check src/ tests/`
  - [ ] `ruff format --check src/ tests/`
  - [ ] `mypy src/`
  - [ ] `pytest tests/`
  - [ ] `bandit -c pyproject.toml -r src/`
  - [ ] `pre-commit run --all-files`
- [ ] Docker build succeeds: `docker build -t resume-builder:test .`
- [ ] GitHub Actions workflow is correctly configured
- [ ] No errors or warnings in CI configuration

### Implementation Steps

1. Run each CI step locally and fix failures
2. Build Docker image and verify it starts
3. Review `.github/workflows/ci.yml` for any issues
4. Create test commit to verify GitHub Actions (optional)

### Test Expectations

All commands exit with code 0:
```bash
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/
pytest tests/ -v
bandit -c pyproject.toml -r src/
pre-commit run --all-files
docker build -t resume-builder:test .
```

### Files to Create/Modify

- May need to fix: Various source files to pass checks
- May need to update: `.github/workflows/ci.yml` if issues found

### Commit Message

```
chore: verify CI pipeline passes all checks

- Fix any linting or type errors
- Ensure Docker build succeeds
- Verify all pre-commit hooks pass
```

### Notes

- mypy may fail on stub files until models are implemented (P1-T01)
- If mypy fails, add minimal type stubs or `py.typed` markers
- Docker build requires WeasyPrint dependencies - may need adjustments

---

## Phase Completion Criteria

- [ ] `pre-commit run --all-files` passes
- [ ] `.secrets.baseline` exists and is committed
- [ ] Test directory structure matches REQUIREMENTS.md
- [ ] Sample data for "Alex Chen" exists in `sample_data/`
- [ ] Test fixtures exist in `tests/fixtures/`
- [ ] Logging utility implemented and tested
- [ ] `.env.example` is complete
- [ ] CI pipeline passes (simulated locally)

---

## Phase 0 Completion Checklist

Before moving to Phase 1, verify:

```bash
# All hooks pass
pre-commit run --all-files

# Tests run (even if some fail due to unimplemented code)
pytest tests/ --collect-only

# Linting passes
ruff check src/ tests/
ruff format --check src/ tests/

# Docker builds
docker build -t resume-builder:test .

# Sample data exists
ls sample_data/*.csv

# Fixtures exist
ls tests/fixtures/linkedin/
ls tests/fixtures/jobs/
```

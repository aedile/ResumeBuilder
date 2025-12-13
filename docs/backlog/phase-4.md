# Phase 4: Production Ready

> **Goal**: Complete integration testing, documentation, and production optimization for deployment.

**Status**: Not Started
**Progress**: 0/6 tasks complete
**Depends On**: Phase 2 and Phase 3 complete

---

## Task Summary

| ID | Task | Status | Dependencies |
|----|------|--------|--------------|
| P4-T01 | Implement Full Integration Tests | Not Started | Phase 2, Phase 3 |
| P4-T02 | Implement Agent Evaluation Framework | Not Started | P2-T09 |
| P4-T03 | Implement Cost Estimation Feature | Not Started | P2-T10 |
| P4-T04 | Complete README Documentation | Not Started | All prior phases |
| P4-T05 | Create Architecture Decision Records | Not Started | All prior phases |
| P4-T06 | Optimize Docker Production Build | Not Started | P4-T01 |

---

## P4-T01: Implement Full Integration Tests

**Description**: Create comprehensive integration tests that exercise the complete workflow from LinkedIn data upload through resume generation, using real (mocked) agent interactions.

**Status**: Not Started

### User Story

As a developer, I need integration tests so that I can verify the complete system works end-to-end before deployment.

### Acceptance Criteria

- [ ] Test uploads LinkedIn data via API
- [ ] Test parses data through Parser Agent (mocked)
- [ ] Test matches against job description (mocked)
- [ ] Test optimizes content (mocked)
- [ ] Test runs QA and HR review (mocked)
- [ ] Test generates HTML, PDF, DOCX outputs
- [ ] Tests cover happy path and error scenarios
- [ ] Tests marked with `@pytest.mark.integration`
- [ ] All integration tests pass

### Implementation Steps

1. Write failing integration tests (RED)
2. Fix any integration issues discovered
3. Ensure all tests pass (GREEN)

### Test Expectations

**File**: `tests/integration/test_full_workflow.py`

```python
@pytest.mark.integration
def test_complete_workflow_happy_path(client, sample_linkedin_data, sample_job):
    """Complete workflow from upload to download."""

@pytest.mark.integration
def test_workflow_handles_partial_linkedin_data(client):
    """Workflow succeeds with missing optional CSVs."""

@pytest.mark.integration
def test_workflow_reports_errors_gracefully(client, malformed_data):
    """Workflow returns helpful errors for bad data."""

@pytest.mark.integration
def test_all_output_formats_generated(client, valid_data):
    """HTML, PDF, and DOCX all generate successfully."""

@pytest.mark.integration
def test_workflow_tracks_progress(client, valid_data):
    """Progress updates are sent during workflow."""
```

### Files to Create/Modify

- Create: `tests/integration/test_full_workflow.py`
- Create: `tests/integration/test_api_integration.py`
- Modify: `tests/conftest.py` (add integration fixtures)

### Commit Messages

**RED phase:**
```
test: add failing integration tests for full workflow
```

**GREEN phase:**
```
test: integration tests pass for complete workflow

- Add end-to-end workflow tests
- Test all output formats
- Test error handling scenarios
- Test progress tracking
```

---

## P4-T02: Implement Agent Evaluation Framework

**Description**: Implement the evaluation framework for assessing agent outputs against golden datasets, including A/B comparison capabilities and reproducible runs.

**Status**: Not Started

### User Story

As a developer, I need an evaluation framework so that I can measure and improve agent quality over time.

### Acceptance Criteria

- [ ] `AgentEvaluator` class for running evaluations
- [ ] Golden dataset loading from fixtures
- [ ] Comparison of agent output vs expected output
- [ ] Quality metrics (accuracy, consistency, etc.)
- [ ] A/B comparison of different prompts/configurations
- [ ] Reproducible runs via seed/snapshot
- [ ] Structured evaluation reports
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/agents/evaluation.py`
3. Create golden dataset fixtures
4. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_evaluation.py`

```python
def test_evaluator_loads_golden_dataset():
    """Evaluator loads expected outputs from fixtures."""

def test_evaluator_compares_outputs():
    """Evaluator produces comparison metrics."""

def test_evaluator_reproducible_runs():
    """Same seed produces same results."""

def test_evaluator_generates_report():
    """Evaluator produces structured report."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/evaluation.py`
- Create: `tests/fixtures/golden/` (golden datasets)
- Create: `tests/unit/test_evaluation.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for agent evaluation framework
```

**GREEN phase:**
```
feat: implement agent evaluation framework

- Add AgentEvaluator class
- Load golden datasets for comparison
- Generate quality metrics
- Support reproducible runs
```

---

## P4-T03: Implement Cost Estimation Feature

**Description**: Implement cost estimation that predicts token usage before generation and requests user confirmation for generations exceeding $0.10.

**Status**: Not Started

### User Story

As a user, I need cost estimation so that I don't accidentally spend more than expected on API calls.

### Acceptance Criteria

- [ ] Estimates tokens based on input size
- [ ] Calculates estimated cost using current pricing
- [ ] Displays estimate before generation
- [ ] Prompts for confirmation if > $0.10
- [ ] Tracks actual vs estimated for calibration
- [ ] Updates estimates based on historical data
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement estimation in `src/resume_builder/agents/orchestrator.py`
3. Add UI component for cost display
4. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_cost_estimation.py`

```python
def test_estimate_tokens_from_input_size():
    """Estimation correlates with input size."""

def test_calculate_cost_from_tokens():
    """Cost calculation uses current pricing."""

def test_confirmation_threshold():
    """Confirmation required for high-cost runs."""

def test_actual_vs_estimated_tracking():
    """System tracks estimation accuracy."""
```

### Files to Create/Modify

- Modify: `src/resume_builder/agents/orchestrator.py`
- Modify: `src/resume_builder/api/routes.py`
- Modify: `src/resume_builder/templates/index.html`
- Create: `tests/unit/test_cost_estimation.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for cost estimation
```

**GREEN phase:**
```
feat: implement cost estimation feature

- Estimate tokens from input size
- Calculate costs using Claude pricing
- Add confirmation for expensive runs
- Track estimation accuracy
```

---

## P4-T04: Complete README Documentation

**Description**: Write comprehensive README.md with project overview, quick start guide, installation instructions, usage examples, and contribution guidelines.

**Status**: Not Started

### User Story

As a new user or contributor, I need clear documentation so that I can quickly understand and use the project.

### Acceptance Criteria

- [ ] Project overview and purpose
- [ ] Features list with screenshots
- [ ] Quick start (5-minute setup)
- [ ] Detailed installation instructions
- [ ] Usage examples with code
- [ ] Configuration reference
- [ ] Development setup guide
- [ ] Contribution guidelines
- [ ] License information
- [ ] Links to further documentation

### Implementation Steps

1. Draft README structure
2. Write each section
3. Add screenshots/diagrams
4. Review for clarity and completeness

### Content Outline

```markdown
# Resume Builder

> Transform LinkedIn exports into polished, AI-optimized resumes

## Features
- LinkedIn data import
- AI-powered content optimization
- 4 professional styles
- WCAG 2.1 AA accessible

## Quick Start
1. Clone repository
2. Install dependencies
3. Set API key
4. Run application

## Installation
[Detailed instructions]

## Usage
[Examples with screenshots]

## Configuration
[Environment variables, config.local.json]

## Development
[Setup, testing, contributing]

## License
MIT
```

### Files to Create/Modify

- Modify: `README.md` (complete rewrite)

### Commit Message

```
docs: complete README documentation

- Add project overview and features
- Add quick start and installation guides
- Add usage examples with screenshots
- Add configuration reference
- Add development and contribution guides
```

---

## P4-T05: Create Architecture Decision Records

**Description**: Document key architectural decisions in ADR format including Claude native tools choice, agent architecture, and technology selections.

**Status**: Not Started

### User Story

As a developer, I need ADRs so that I understand why certain architectural decisions were made.

### Acceptance Criteria

- [ ] ADR-0001: Use Claude Native Tools (not LangChain)
- [ ] ADR-0002: Multi-Agent Architecture
- [ ] ADR-0003: Pydantic for Data Models
- [ ] ADR-0004: WeasyPrint for PDF Generation
- [ ] ADR-0005: TDD and 90% Coverage Requirement
- [ ] ADRs follow standard format (context, decision, consequences)
- [ ] ADRs linked from main documentation

### ADR Template

```markdown
# ADR-XXXX: Title

## Status
Accepted / Proposed / Deprecated

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
```

### Implementation Steps

1. Create ADR template
2. Write each ADR
3. Link from README and docs

### Files to Create/Modify

- Create: `docs/adr/0001-use-claude-native-tools.md`
- Create: `docs/adr/0002-multi-agent-architecture.md`
- Create: `docs/adr/0003-pydantic-data-models.md`
- Create: `docs/adr/0004-weasyprint-pdf-generation.md`
- Create: `docs/adr/0005-tdd-coverage-requirement.md`
- Create: `docs/adr/README.md` (index)

### Commit Message

```
docs: create architecture decision records

- ADR-0001: Claude native tools over LangChain
- ADR-0002: Multi-agent architecture
- ADR-0003: Pydantic for validation
- ADR-0004: WeasyPrint for PDF
- ADR-0005: TDD with 90% coverage
```

---

## P4-T06: Optimize Docker Production Build

**Description**: Optimize the Docker build for production including minimal image size, proper caching, security hardening, and health check configuration.

**Status**: Not Started

### User Story

As an operator, I need an optimized Docker image so that deployments are fast, secure, and reliable.

### Acceptance Criteria

- [ ] Multi-stage build (builder + runtime)
- [ ] Minimal runtime image (python-slim based)
- [ ] Non-root user in container
- [ ] Health check endpoint configured
- [ ] Proper layer caching for dependencies
- [ ] No dev dependencies in production image
- [ ] Image size < 500MB
- [ ] Security scan passes (no critical vulnerabilities)

### Implementation Steps

1. Review current Dockerfile
2. Optimize layer ordering for caching
3. Reduce image size
4. Add security hardening
5. Configure health checks
6. Run security scan

### Test Expectations

```bash
# Image builds successfully
docker build -t resume-builder:prod .

# Image size is reasonable
docker images resume-builder:prod  # < 500MB

# Container runs as non-root
docker run resume-builder:prod whoami  # Not root

# Health check works
docker run -d resume-builder:prod
docker inspect --format='{{.State.Health.Status}}'  # healthy

# Security scan passes
docker scout cves resume-builder:prod  # No critical
```

### Files to Create/Modify

- Modify: `Dockerfile`
- Modify: `docker-compose.yml` (production profile)
- Create: `docker-compose.prod.yml` (if needed)

### Commit Message

```
chore: optimize Docker production build

- Use multi-stage build for smaller image
- Run as non-root user
- Add health check configuration
- Optimize layer caching
- Remove dev dependencies from production
```

### Dockerfile Optimization Example

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir build && \
    pip wheel --no-cache-dir --wheel-dir /wheels .

# Production stage
FROM python:3.11-slim as production
WORKDIR /app

# Security: non-root user
RUN useradd --create-home appuser
USER appuser

# Install from wheels
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl

# Copy application
COPY --chown=appuser:appuser src/ ./src/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

EXPOSE 8000
CMD ["uvicorn", "resume_builder.main:app", "--host", "0.0.0.0"]
```

---

## Phase Completion Criteria

- [ ] Integration tests cover complete user workflow
- [ ] Agent evaluation framework produces quality metrics
- [ ] Cost estimation accurately predicts token usage
- [ ] README provides clear setup and usage instructions
- [ ] ADRs document all significant decisions
- [ ] Docker image is optimized and secure
- [ ] All CI checks pass
- [ ] Ready for production deployment

---

## Phase 4 Completion Checklist

Before declaring production ready:

```bash
# All tests pass (unit + integration)
pytest tests/ -v --cov=src/resume_builder --cov-fail-under=90

# Integration tests specifically
pytest tests/integration/ -v -m integration

# Docker builds and runs
docker build -t resume-builder:prod .
docker run -p 8000:8000 resume-builder:prod

# Security scan passes
docker scout cves resume-builder:prod

# Documentation complete
# - README is comprehensive
# - ADRs are written
# - API docs generate (/docs)

# All hooks pass
pre-commit run --all-files

# Manual smoke test
# - Upload sample data
# - Generate resume in each style
# - Download HTML, PDF, DOCX
# - Verify accessibility with screen reader
```

---

## Final Deployment Checklist

```
[ ] All phases complete (0-4)
[ ] 90%+ test coverage across all modules
[ ] No critical security vulnerabilities
[ ] Documentation complete and reviewed
[ ] Docker image optimized and tested
[ ] Environment variables documented
[ ] Secrets properly managed
[ ] CI/CD pipeline passing
[ ] Manual QA completed
[ ] Ready for production traffic
```

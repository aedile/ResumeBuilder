# Resume Builder

AI-powered resume builder using Claude's native tool_use — transforms LinkedIn data exports into polished, job-tailored resumes.

## Overview

Resume Builder is a Python application that uses Claude's multi-agent system to parse LinkedIn profile data, score it against a target job description, optimize the content, and generate professional resumes in HTML, PDF, and DOCX formats. The project also serves as a portfolio demonstration of context engineering, TDD methodology, and security-conscious AI development.

> **This project is intentionally over-engineered.** It exists as a showcase for agentic development principles — strict TDD, multi-agent coordination, constitutional governance, parallel review cycles — not as a practical tool anyone should use to build a resume. The process is the product. If you came here looking for a real resume builder, you want something else.

## Current Status

| Phase | Description | Status |
|-------|-------------|--------|
| Phase 0 | Foundation (tooling, pre-commit, sample data) | ✅ Complete |
| Phase 1 | Core (models, parsers, generators, templates) | ✅ Complete |
| Phase 2 | AI Integration (multi-agent system, orchestration) | ✅ Complete |
| Phase 3 | Review & Polish (QA/HR agents, web interface) | 🔜 Next |
| Phase 4 | Production Ready (integration tests, Docker, CI/CD) | 🔜 Planned |

**487 tests · 96%+ coverage · all quality gates green**

## What's Built

- **LinkedIn CSV parsers** — parse all LinkedIn export files gracefully (Profile, Positions, Skills, Education, Certifications, Projects, Publications, Languages, Honors, Volunteer)
- **Resume generators** — HTML (4 styles), PDF (WeasyPrint), DOCX (python-docx)
- **Multi-agent system** using Claude native tool_use:
  - `ParserAgent` — structures LinkedIn data into a typed `Resume` object
  - `MatcherAgent` — scores resume sections against a job description (0–100)
  - `OptimizerAgent` — rewrites bullets and tailors summaries
  - `OrchestratorAgent` — coordinates the pipeline, handles failures, tracks tokens
- **PII protection** — structured JSON logging with PIIFilter, gitignored `data/` and `output/`
- **Security** — gitleaks, detect-secrets, bandit, pre-commit enforced on every commit

## What's Not Built Yet

- FastAPI web application (Phase 3)
- Web UI (Phase 3)
- QA and HR review agents (Phase 3)
- Docker / docker-compose (Phase 4)
- GitHub Actions CI (Phase 4)
- Integration tests (Phase 4)

## Prerequisites

- Python 3.11+
- Poetry (dependency management)
- Anthropic API key (for Claude integration)

## Installation

```bash
git clone https://github.com/aedile/ResumeBuilder.git
cd ResumeBuilder

# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Running Tests

```bash
# All unit tests
poetry run python -m pytest tests/unit/ -v

# With coverage
poetry run python -m pytest tests/unit/ --cov=src/resume_builder --cov-fail-under=90 -q
```

## Quality Checks

```bash
poetry run python -m ruff check src/ tests/
poetry run python -m ruff format --check src/ tests/
poetry run python -m mypy src/
poetry run python -m bandit -c pyproject.toml -r src/ -q
pre-commit run --all-files
```

## Project Structure

```
src/resume_builder/
├── models/         # Pydantic data models (resume, job, agent, config)
├── parsers/        # LinkedIn CSV parsers (one file per export type)
├── generators/     # Resume generators (html, pdf, docx) + Jinja2 templates
├── agents/         # Multi-agent system (base, parser, matcher, optimizer, orchestrator)
│   └── tools/      # Claude tool definitions for each agent
├── utils/          # Structured JSON logging with PII filtering
└── templates/      # Jinja2 resume templates (base, classic, modern, tech, ats)

tests/
├── unit/           # 487 unit tests (pytest-asyncio, mocked Claude API)
├── integration/    # Planned — Phase 4
└── fixtures/       # Fictional test data (LinkedIn CSVs, job descriptions, API responses)
```

## Architecture

No LangChain. All agents use Claude's native `tool_use` capability directly via the Anthropic SDK. See `docs/adr/` for architectural decisions.

## Development Workflow

This project follows a strict TDD + constitutional governance process:

1. Feature branch: `feat/P<phase>-T<task>-<description>`
2. RED phase: write failing tests, commit `test: ...`
3. GREEN phase: minimal implementation, commit `feat: ...`
4. All quality gates must pass before PR
5. PR reviewed and merged by human; agent never self-merges

See [CLAUDE.md](CLAUDE.md) and [AUTONOMOUS_DEVELOPMENT_PROMPT.md](AUTONOMOUS_DEVELOPMENT_PROMPT.md) for full agent directives.

## Security

- Never commit real LinkedIn data or PII — `data/` and `output/` are gitignored
- Use `.env` for API keys (gitignored; see `.env.example`)
- Pre-commit hooks enforce secret scanning on every commit
- See [CONSTITUTION.md](CONSTITUTION.md) for security requirements (Priority 0)

## License

MIT License

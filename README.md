# Resume Builder

AI-powered resume builder using Claude with LinkedIn data import.

## Overview

Resume Builder is a Python application that uses Claude's AI capabilities to transform LinkedIn profile data into tailored, professional resumes. The system follows a test-driven development approach with comprehensive quality gates.

## Features

- **LinkedIn Data Import**: Parse exported LinkedIn profile data (CSV format)
- **AI-Powered Generation**: Claude-based resume optimization and tailoring
- **PDF Export**: WeasyPrint-based PDF generation
- **PII Protection**: Built-in safeguards for sensitive information
- **Comprehensive Testing**: 90%+ test coverage requirement
- **Quality Gates**: Automated linting, type checking, and security scanning

## Prerequisites

- Python 3.11+
- Poetry (dependency management)
- Docker (optional, for containerized deployment)
- Anthropic API key (for Claude integration)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/JesseCastro/ResumeBuilder.git
   cd ResumeBuilder
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

## Usage

```bash
# Run the application
poetry run uvicorn resume_builder.main:app --reload

# Run tests
poetry run pytest

# Run quality checks
poetry run ruff check src/ tests/
poetry run mypy src/
poetry run bandit -c pyproject.toml -r src/
```

## Development

This project follows strict TDD and quality standards:

- **Test-Driven Development**: All features developed RED→GREEN→REFACTOR
- **Type Safety**: Full type hints with mypy strict mode
- **Code Quality**: Ruff linting and formatting
- **Security**: Bandit, gitleaks, detect-secrets scanning
- **Coverage**: Minimum 90% test coverage

See [CLAUDE.md](CLAUDE.md) for detailed development guidelines.

## Project Structure

```
src/resume_builder/
├── models/         # Pydantic data models
├── parsers/        # LinkedIn data parsers
├── generators/     # Resume generators
├── agents/         # Claude AI agents
├── api/            # FastAPI routes
├── utils/          # Utilities (logging, config)
└── templates/      # Resume templates

tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── fixtures/       # Test data (fictional)
```

## License

MIT License - see LICENSE file for details.

## Contributing

This project follows the development workflow defined in [AUTONOMOUS_DEVELOPMENT_PROMPT.md](AUTONOMOUS_DEVELOPMENT_PROMPT.md).

1. Create a feature branch
2. Follow TDD (RED→GREEN→REFACTOR)
3. Ensure all quality gates pass
4. Submit a pull request

## Security

- Never commit real LinkedIn data or PII
- Use `.env` for secrets (gitignored)
- Run pre-commit hooks on every commit
- See [CONSTITUTION.md](CONSTITUTION.md) for security requirements

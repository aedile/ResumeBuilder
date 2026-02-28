# Phase 2: AI Integration

> **Goal**: Implement the multi-agent system using Claude's native tool_use capabilities for intelligent resume optimization.

**Status**: Complete
**Progress**: 11/11 tasks complete (P2-T11 added during Phase 1 review)
**Depends On**: Phase 1 complete

---

## Task Summary

| ID | Task | Status | Dependencies |
|----|------|--------|--------------|
| P2-T01 | Implement Base Agent Class | Complete | Phase 1 |
| P2-T02 | Implement Agent Message Models | Complete | P2-T01 |
| P2-T03 | Implement Parser Agent Tools | Complete | P2-T01 |
| P2-T04 | Implement Parser Agent | Complete | P2-T02, P2-T03 |
| P2-T05 | Implement Matcher Agent Tools | Complete | P2-T01 |
| P2-T06 | Implement Matcher Agent | Complete | P2-T02, P2-T05 |
| P2-T07 | Implement Optimizer Agent Tools | Complete | P2-T01 |
| P2-T08 | Implement Optimizer Agent | Complete | P2-T02, P2-T07 |
| P2-T09 | Implement Orchestrator Agent | Complete | P2-T04, P2-T06, P2-T08 |
| P2-T10 | Implement Token Tracking | Complete | P2-T01 |
| P2-T11 | Add Full Contact Information to Generated Documents | Complete | Phase 1 |

---

## P2-T01: Implement Base Agent Class

**Description**: Create the base Agent class with Claude API integration, tool registration, message handling, and error recovery. This is the foundation for all specialized agents.

**Status**: Not Started

### User Story

As a developer, I need a base agent class so that all specialized agents have consistent API interaction, error handling, and tool registration.

### Acceptance Criteria

- [ ] `BaseAgent` class with Claude API client
- [ ] Tool registration via decorators or method
- [ ] Message history management
- [ ] Retry logic with exponential backoff
- [ ] Timeout handling (configurable, default 30s)
- [ ] Graceful error recovery
- [ ] Async support for concurrent operations
- [ ] 90%+ test coverage with mocked API

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/agents/base.py`:
   - `BaseAgent` class with Anthropic client
   - `register_tool(name, schema, handler)` method
   - `send_message(content: str) -> AgentResponse`
   - `_handle_tool_calls(tool_calls) -> list[ToolResult]`
   - `_retry_with_backoff(func, max_retries=3)`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_base_agent.py`

```python
def test_base_agent_creation():
    """BaseAgent initializes with API client."""

def test_register_tool():
    """Tools can be registered with schema."""

def test_send_message_returns_response(mock_anthropic):
    """send_message returns AgentResponse."""

def test_retry_on_rate_limit(mock_anthropic_rate_limit):
    """Agent retries on rate limit with backoff."""

def test_timeout_handling(mock_anthropic_slow):
    """Agent handles timeout gracefully."""

def test_tool_call_execution(mock_anthropic_tool_call):
    """Agent executes tool calls and returns results."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/__init__.py`
- Create: `src/resume_builder/agents/base.py`
- Create: `tests/unit/test_agents/__init__.py`
- Create: `tests/unit/test_agents/test_base_agent.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for base agent class
```

**GREEN phase:**
```
feat: implement base agent class with Claude API

- Add BaseAgent with Anthropic client integration
- Implement tool registration and execution
- Add retry logic with exponential backoff
- Support configurable timeouts
- Handle API errors gracefully
```

### Implementation Notes

```python
class BaseAgent:
    def __init__(
        self,
        client: Anthropic | None = None,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 4096,
        timeout: float = 30.0,
    ):
        self.client = client or Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.tools: list[dict] = []
        self.message_history: list[dict] = []
        self.token_usage: TokenUsage = TokenUsage()

    def register_tool(self, tool_def: ToolDefinition) -> None:
        """Register a tool for the agent to use."""
        ...

    async def send_message(self, content: str) -> AgentResponse:
        """Send message and handle response/tool calls."""
        ...
```

---

## P2-T02: Implement Agent Message Models

**Description**: Implement Pydantic models for agent state, messages, tool calls, and tool results following Anthropic's message format.

**Status**: Not Started

### User Story

As a developer, I need typed message models so that agent communication is validated, consistent, and easy to debug.

### Acceptance Criteria

- [ ] `ToolDefinition` model for tool schemas
- [ ] `ToolCall` model for incoming tool requests
- [ ] `ToolResult` model for tool execution results
- [ ] `AgentMessage` model for conversation messages
- [ ] `AgentResponse` model for agent outputs
- [ ] `AgentState` model for workflow state
- [ ] `TokenUsage` model for tracking API usage
- [ ] All models match Anthropic's API format
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement models in `src/resume_builder/models/agent.py`:
   - Study Anthropic's API message format
   - Create matching Pydantic models
   - Add serialization/deserialization helpers
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agent_models.py`

```python
def test_tool_definition_schema():
    """ToolDefinition produces valid JSON schema."""

def test_tool_call_from_api_response():
    """ToolCall parses from Anthropic API format."""

def test_tool_result_serialization():
    """ToolResult serializes to API format."""

def test_agent_state_tracks_workflow():
    """AgentState tracks current step and history."""

def test_token_usage_accumulation():
    """TokenUsage accumulates across calls."""
```

### Files to Create/Modify

- Create: `src/resume_builder/models/agent.py`
- Modify: `src/resume_builder/models/__init__.py`
- Create: `tests/unit/test_agent_models.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for agent message models
```

**GREEN phase:**
```
feat: implement agent message and state models

- Add ToolDefinition, ToolCall, ToolResult models
- Add AgentMessage and AgentResponse models
- Add AgentState for workflow tracking
- Add TokenUsage for API cost tracking
- Match Anthropic API message format
```

### Model Specifications

```python
class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]

class ToolCall(BaseModel):
    id: str
    name: str
    input: dict[str, Any]

class ToolResult(BaseModel):
    tool_use_id: str
    content: str | list[dict]
    is_error: bool = False

class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0

    def add(self, other: "TokenUsage") -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def estimated_cost(self) -> float:
        # Based on Claude pricing
        ...
```

---

## P2-T03: Implement Parser Agent Tools

**Description**: Implement the custom tools for the Parser Agent: `parse_csv`, `normalize_dates`, `extract_implicit_skills`, `validate_data`.

**Status**: Not Started

### User Story

As a Parser Agent, I need tools to parse and normalize LinkedIn data so that I can structure it correctly for resume generation.

### Acceptance Criteria

- [ ] `parse_csv` tool reads CSV and returns structured data
- [ ] `normalize_dates` tool standardizes date formats
- [ ] `extract_implicit_skills` tool finds skills in job descriptions
- [ ] `validate_data` tool checks data completeness
- [ ] All tools have proper JSON schemas
- [ ] Tools handle errors gracefully
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement tools in `src/resume_builder/agents/tools/parsing.py`:
   - Each tool as a function with type hints
   - Tool schema definitions
   - Error handling for each tool
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_parsing_tools.py`

```python
def test_parse_csv_tool_valid_input():
    """parse_csv returns structured data for valid CSV."""

def test_parse_csv_tool_handles_errors():
    """parse_csv returns error for invalid input."""

def test_normalize_dates_various_formats():
    """normalize_dates handles LinkedIn date formats."""

def test_extract_implicit_skills():
    """extract_implicit_skills finds Python, AWS, etc. in text."""

def test_validate_data_missing_required():
    """validate_data flags missing required fields."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/tools/__init__.py`
- Create: `src/resume_builder/agents/tools/parsing.py`
- Create: `tests/unit/test_agents/test_parsing_tools.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for parser agent tools
```

**GREEN phase:**
```
feat: implement parser agent tools

- Add parse_csv tool for CSV reading
- Add normalize_dates for date standardization
- Add extract_implicit_skills for skill extraction
- Add validate_data for completeness checking
```

### Tool Definitions

```python
PARSE_CSV_TOOL = ToolDefinition(
    name="parse_csv",
    description="Parse a CSV file and return structured data",
    input_schema={
        "type": "object",
        "properties": {
            "csv_content": {"type": "string", "description": "CSV content to parse"},
            "csv_type": {"type": "string", "enum": ["profile", "positions", "skills", ...]}
        },
        "required": ["csv_content", "csv_type"]
    }
)
```

---

## P2-T04: Implement Parser Agent

**Description**: Implement the Parser Agent that uses Claude to intelligently categorize and structure LinkedIn data, handling ambiguous or malformed data gracefully.

**Status**: Not Started

### User Story

As a user, I need an intelligent parser so that my LinkedIn data is correctly interpreted even when it contains ambiguities or formatting issues.

### Acceptance Criteria

- [ ] `ParserAgent` extends `BaseAgent`
- [ ] Registers parsing tools on initialization
- [ ] System prompt guides intelligent parsing
- [ ] Handles ambiguous company names, titles
- [ ] Extracts implicit skills from descriptions
- [ ] Returns structured `Resume` object
- [ ] Graceful degradation for malformed data
- [ ] 90%+ test coverage with mocked API

### Implementation Steps

1. Write failing tests with mocked API (RED)
2. Implement `src/resume_builder/agents/parser_agent.py`:
   - `ParserAgent(BaseAgent)` class
   - System prompt for parsing guidance
   - `parse(linkedin_data: dict) -> Resume` method
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_parser_agent.py`

```python
def test_parser_agent_creates_resume(mock_anthropic):
    """Parser agent produces Resume from LinkedIn data."""

def test_parser_handles_ambiguous_data(mock_anthropic):
    """Parser makes reasonable choices for ambiguous data."""

def test_parser_extracts_implicit_skills(mock_anthropic):
    """Parser finds skills mentioned in job descriptions."""

def test_parser_graceful_degradation(mock_anthropic):
    """Parser returns partial result for malformed data."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/parser_agent.py`
- Modify: `src/resume_builder/agents/__init__.py`
- Create: `tests/unit/test_agents/test_parser_agent.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for parser agent
```

**GREEN phase:**
```
feat: implement parser agent for LinkedIn data

- Add ParserAgent extending BaseAgent
- Implement intelligent data parsing
- Extract implicit skills from descriptions
- Handle ambiguous and malformed data
```

---

## P2-T05: Implement Matcher Agent Tools

**Description**: Implement the custom tools for the Job Matcher Agent: `extract_requirements`, `score_match`, `identify_gaps`, `rank_experience`.

**Status**: Not Started

### User Story

As a Matcher Agent, I need tools to analyze job descriptions and score resume fit so that I can provide accurate matching information.

### Acceptance Criteria

- [ ] `extract_requirements` parses job descriptions
- [ ] `score_match` calculates 0-100 match scores
- [ ] `identify_gaps` finds missing skills/experience
- [ ] `rank_experience` orders positions by relevance
- [ ] All tools have proper JSON schemas
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement tools in `src/resume_builder/agents/tools/matching.py`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_matching_tools.py`

```python
def test_extract_requirements_from_job():
    """extract_requirements parses required skills, years, etc."""

def test_score_match_returns_0_100():
    """score_match returns score in valid range."""

def test_identify_gaps_finds_missing_skills():
    """identify_gaps lists skills in job but not resume."""

def test_rank_experience_by_relevance():
    """rank_experience orders positions by job fit."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/tools/matching.py`
- Create: `tests/unit/test_agents/test_matching_tools.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for matcher agent tools
```

**GREEN phase:**
```
feat: implement matcher agent tools

- Add extract_requirements for job parsing
- Add score_match for fit calculation
- Add identify_gaps for gap analysis
- Add rank_experience for relevance ranking
```

---

## P2-T06: Implement Matcher Agent

**Description**: Implement the Job Matcher Agent that analyzes job descriptions, scores resume sections against requirements, and identifies skill gaps.

**Status**: Not Started

### User Story

As a user, I need job matching analysis so that I know how well my resume fits a target position and what gaps I should address.

### Acceptance Criteria

- [ ] `MatcherAgent` extends `BaseAgent`
- [ ] Registers matching tools on initialization
- [ ] Analyzes job description structure
- [ ] Scores each resume section (0-100)
- [ ] Identifies skill gaps with suggestions
- [ ] Ranks positions by relevance
- [ ] Returns `MatchReport` with all analysis
- [ ] 90%+ test coverage with mocked API

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/agents/matcher_agent.py`:
   - `MatcherAgent(BaseAgent)` class
   - `analyze(resume: Resume, job: JobDescription) -> MatchReport`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_matcher_agent.py`

```python
def test_matcher_produces_scores(mock_anthropic):
    """Matcher returns scores for each section."""

def test_matcher_identifies_gaps(mock_anthropic):
    """Matcher lists skills missing from resume."""

def test_matcher_ranks_positions(mock_anthropic):
    """Matcher orders positions by job relevance."""

def test_matcher_overall_score(mock_anthropic):
    """Matcher provides overall match percentage."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/matcher_agent.py`
- Modify: `src/resume_builder/agents/__init__.py`
- Create: `tests/unit/test_agents/test_matcher_agent.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for matcher agent
```

**GREEN phase:**
```
feat: implement job matcher agent

- Add MatcherAgent extending BaseAgent
- Score resume sections against job requirements
- Identify skill gaps with suggestions
- Rank positions by relevance
```

---

## P2-T07: Implement Optimizer Agent Tools

**Description**: Implement the custom tools for the Content Optimizer Agent: `rewrite_bullet`, `generate_summary`, `suggest_edits`, `verify_facts`.

**Status**: Not Started

### User Story

As an Optimizer Agent, I need tools to improve resume content so that bullet points are impactful and summaries are tailored.

### Acceptance Criteria

- [ ] `rewrite_bullet` improves individual bullet points
- [ ] `generate_summary` creates tailored professional summary
- [ ] `suggest_edits` proposes content changes
- [ ] `verify_facts` checks claims against source data
- [ ] Tools preserve factual accuracy
- [ ] Tools maintain authentic voice
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement tools in `src/resume_builder/agents/tools/optimization.py`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_optimization_tools.py`

```python
def test_rewrite_bullet_adds_metrics():
    """rewrite_bullet suggests quantifiable improvements."""

def test_rewrite_bullet_uses_action_verbs():
    """rewrite_bullet starts with strong action verbs."""

def test_generate_summary_includes_keywords():
    """generate_summary incorporates job keywords."""

def test_verify_facts_catches_fabrication():
    """verify_facts rejects claims not in source data."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/tools/optimization.py`
- Create: `tests/unit/test_agents/test_optimization_tools.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for optimizer agent tools
```

**GREEN phase:**
```
feat: implement optimizer agent tools

- Add rewrite_bullet for impact improvement
- Add generate_summary for tailored summaries
- Add suggest_edits for content recommendations
- Add verify_facts for accuracy checking
```

---

## P2-T08: Implement Optimizer Agent

**Description**: Implement the Content Optimizer Agent that rewrites bullet points for impact, tailors summaries, and suggests improvements while maintaining authentic voice.

**Status**: Not Started

### User Story

As a user, I need content optimization so that my resume is more impactful while still sounding like me.

### Acceptance Criteria

- [ ] `OptimizerAgent` extends `BaseAgent`
- [ ] Registers optimization tools
- [ ] Rewrites bullets with action verbs and metrics
- [ ] Tailors summary to target job
- [ ] Preserves factual accuracy (never fabricates)
- [ ] Maintains user's authentic voice
- [ ] Returns optimized content with change tracking
- [ ] 90%+ test coverage with mocked API

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/agents/optimizer_agent.py`:
   - `OptimizerAgent(BaseAgent)` class
   - `optimize(resume: Resume, job: JobDescription, match: MatchReport) -> OptimizedResume`
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_optimizer_agent.py`

```python
def test_optimizer_improves_bullets(mock_anthropic):
    """Optimizer returns improved bullet points."""

def test_optimizer_tailors_summary(mock_anthropic):
    """Optimizer creates job-specific summary."""

def test_optimizer_never_fabricates(mock_anthropic):
    """Optimizer only uses facts from source resume."""

def test_optimizer_tracks_changes(mock_anthropic):
    """Optimizer returns diff of changes made."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/optimizer_agent.py`
- Modify: `src/resume_builder/agents/__init__.py`
- Create: `tests/unit/test_agents/test_optimizer_agent.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for optimizer agent
```

**GREEN phase:**
```
feat: implement content optimizer agent

- Add OptimizerAgent extending BaseAgent
- Rewrite bullets for impact
- Tailor professional summary
- Preserve facts and authentic voice
- Track all content changes
```

---

## P2-T09: Implement Orchestrator Agent

**Description**: Implement the Orchestrator Agent that coordinates the multi-agent workflow, manages shared state, handles failures gracefully, and provides progress updates.

**Status**: Not Started

### User Story

As a user, I need automated workflow coordination so that all agents work together seamlessly to produce my optimized resume.

### Acceptance Criteria

- [ ] `OrchestratorAgent` coordinates Parser, Matcher, Optimizer
- [ ] Manages shared state across agents
- [ ] Handles partial failures with fallback
- [ ] Provides progress updates via callback
- [ ] Supports human-in-the-loop approval
- [ ] Checkpoints state for recovery
- [ ] Returns complete optimized resume
- [ ] 90%+ test coverage with mocked agents

### Implementation Steps

1. Write failing tests (RED)
2. Implement `src/resume_builder/agents/orchestrator.py`:
   - `OrchestratorAgent` class
   - `run(linkedin_data, job_description, on_progress) -> FinalResult`
   - State management and checkpointing
   - Error recovery logic
3. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_orchestrator.py`

```python
def test_orchestrator_full_workflow(mock_agents):
    """Orchestrator runs complete workflow."""

def test_orchestrator_handles_parser_failure(mock_agents):
    """Orchestrator falls back on parser failure."""

def test_orchestrator_progress_updates(mock_agents):
    """Orchestrator calls progress callback at each step."""

def test_orchestrator_checkpoints_state(mock_agents):
    """Orchestrator saves state for recovery."""

def test_orchestrator_human_approval(mock_agents):
    """Orchestrator pauses for human approval when configured."""
```

### Files to Create/Modify

- Create: `src/resume_builder/agents/orchestrator.py`
- Modify: `src/resume_builder/agents/__init__.py`
- Create: `tests/unit/test_agents/test_orchestrator.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for orchestrator agent
```

**GREEN phase:**
```
feat: implement orchestrator agent

- Add OrchestratorAgent for workflow coordination
- Manage shared state across agents
- Handle failures with graceful fallback
- Provide progress updates
- Support checkpointing for recovery
```

### Workflow Sequence

```
1. Parser Agent: LinkedIn data → Resume object
2. Matcher Agent: Resume + Job → MatchReport
3. Optimizer Agent: Resume + Job + Match → OptimizedResume
4. (Phase 3) QA Agent: OptimizedResume → QAReport
5. (Phase 3) HR Agent: OptimizedResume → HRReport
6. Final assembly and output generation
```

---

## P2-T10: Implement Token Tracking

**Description**: Implement token usage tracking across all agents with per-agent and per-run reporting as required by NFR-7.

**Status**: Not Started

### User Story

As a user, I need to see token usage so that I understand the cost of generating my resume.

### Acceptance Criteria

- [ ] Track input/output tokens per API call
- [ ] Aggregate tokens per agent
- [ ] Aggregate tokens per full run
- [ ] Calculate estimated cost
- [ ] Provide usage breakdown report
- [ ] Support cost estimation before run
- [ ] 90%+ test coverage

### Implementation Steps

1. Write failing tests (RED)
2. Implement tracking in `src/resume_builder/agents/base.py`:
   - Update `TokenUsage` model
   - Track in `send_message` method
   - Add `get_usage_report()` method
3. Implement cost estimation in `src/resume_builder/agents/orchestrator.py`:
   - `estimate_cost(resume_size, job_length) -> CostEstimate`
4. Run tests (GREEN)

### Test Expectations

**File**: `tests/unit/test_agents/test_token_tracking.py`

```python
def test_track_tokens_per_call(mock_anthropic):
    """Each API call updates token count."""

def test_aggregate_tokens_per_agent(mock_anthropic):
    """Agent totals tokens across multiple calls."""

def test_usage_report_format():
    """Usage report includes breakdown by agent."""

def test_cost_estimation():
    """Cost estimation is reasonably accurate."""
```

### Files to Create/Modify

- Modify: `src/resume_builder/agents/base.py`
- Modify: `src/resume_builder/models/agent.py`
- Create: `tests/unit/test_agents/test_token_tracking.py`

### Commit Messages

**RED phase:**
```
test: add failing tests for token tracking
```

**GREEN phase:**
```
feat: implement token usage tracking

- Track input/output tokens per API call
- Aggregate usage per agent and run
- Calculate estimated cost
- Generate usage breakdown report
```

---

## Phase Completion Criteria

- [ ] Base agent class handles Claude API calls correctly
- [ ] All agent tools are implemented and tested with mocks
- [ ] Parser Agent correctly structures LinkedIn data
- [ ] Matcher Agent produces relevance scores 0-100
- [ ] Optimizer Agent improves content while preserving facts
- [ ] Orchestrator coordinates full workflow
- [ ] Token usage is tracked and reportable
- [ ] All tests use mocked API responses (no real API calls)
- [ ] 90%+ test coverage maintained

---

## Phase 2 Completion Checklist

Before moving to Phase 3, verify:

```bash
# All agent tests pass
pytest tests/unit/test_agents/ -v --cov=src/resume_builder/agents --cov-fail-under=90

# Can run orchestrator with mocks
python -c "from resume_builder.agents import OrchestratorAgent; ..."

# Token tracking works
python -c "from resume_builder.models.agent import TokenUsage; ..."

# All hooks pass
pre-commit run --all-files
```

---

## Testing Strategy for AI Components

All agent tests MUST use mocked API responses:

```python
@pytest.fixture
def mock_anthropic(mocker):
    """Mock Anthropic client for testing."""
    mock = mocker.patch("resume_builder.agents.base.Anthropic")
    mock.return_value.messages.create.return_value = MockMessage(
        content=[{"type": "text", "text": "..."}],
        usage={"input_tokens": 100, "output_tokens": 50}
    )
    return mock
```

---

## P2-T11: Add Full Contact Information to Generated Documents

**Description**: Extend all resume generators (HTML, PDF, DOCX) to render email address, phone number, and LinkedIn profile URL in the document header alongside the existing name, headline, and location fields. Phase 1 parsers only populate `Profile` from LinkedIn's `Profile.csv`, which does not include contact details. This task requires a design decision on how contact info flows into generators.

**Status**: Not Started

**Added**: 2026-02-27 (identified during Phase 1 review)

### Design Options

Two viable approaches — choose one before implementation:

**Option A: Add `Optional[ContactInfo]` to `Resume` model**
- Pro: Contact info travels with the resume object; generators need no API changes
- Con: Couples `Resume` (a data model) to `ContactInfo` (a config concern)
- Implementation: Add `contact_info: Optional[ContactInfo] = None` to `Resume`; parsers populate it from `config.local.json` via `AppConfig`

**Option B: Pass contact info as a separate generator parameter**
- Pro: Clean separation — `Resume` stays pure LinkedIn data; generators accept optional enrichment
- Con: All generator signatures change; `GeneratorProtocol` must be updated
- Implementation: `generate(resume, style, contact_info=None)`; update `GeneratorProtocol`

**Recommendation**: Option A — simpler call sites, protocol unchanged, consistent with how `Resume` already aggregates data from multiple sources.

### Acceptance Criteria

- [ ] Design decision documented in an ADR (`docs/adr/`)
- [ ] `ContactInfo` model (or equivalent) accessible to generators
- [ ] `base.html` renders email, phone, LinkedIn URL in header (conditional on presence)
- [ ] `DOCXGenerator._add_header` renders email, phone, LinkedIn URL (conditional)
- [ ] All new fields are optional — generators must not break when absent
- [ ] XSS protection: email/phone/URL escaped in HTML (Jinja2 autoescape covers this)
- [ ] Existing tests continue to pass (no regressions)
- [ ] New tests: location + contact info rendered when present, absent when None
- [ ] 90%+ coverage maintained

### Dependencies

- Phase 1 complete ✅
- `AppConfig` / `ContactInfo` model (exists in `src/resume_builder/models/config.py`)

Use fixtures from `tests/fixtures/api_responses/` for realistic mock responses.

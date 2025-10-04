# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📁 File Naming Conventions

**All files in this project follow consistent naming standards:**

### Documentation Files (UPPERCASE)
- `README.md` - Project overview and setup instructions
- `CLAUDE.md` - This file, guidance for Claude Code
- `.gitignore` - Git configuration
- `.env.example` - Environment variable template

### Project Documentation (lowercase_with_underscores)
- `plan.md` - Implementation plan and progress tracker
- `code_review_20241004.md` - Code review from Gemini
- `code_review_actions_20241004.md` - Action plan from code review
- `project_status_20241003.md` - Current project status summary
- `sample_report.md` - Example analytics report output

### Source Code (lowercase_with_underscores)
- `config.py` - Configuration module
- `main.py` - Main entry point
- `src/api_client.py` - API client module
- `src/extractors.py` - Export extraction module
- `src/analytics.py` - Analytics engine
- `src/report_builder.py` - Report generation module
- `tests/test_*.py` - Unit test files

### Configuration Files (lowercase or standard names)
- `requirements.txt` - Python dependencies
- `pytest.ini` - Pytest configuration
- `.env` - Environment variables (gitignored)

**Rule:**
- Documentation/config in root → UPPERCASE (README, CLAUDE)
- User-created docs → lowercase_with_underscores
- All code → lowercase_with_underscores
- Never mix camelCase or PascalCase in filenames

---

## 🎯 Implementation Workflow

**IMPORTANT:** Always follow [plan.md](plan.md) as the primary implementation guide.

[plan.md](plan.md) contains:
- ✅ Phase-by-phase checklist with detailed tasks
- ✅ Progress tracking (completed vs. pending tasks)
- ✅ Code examples and test commands for each phase
- ✅ Time estimates and success criteria
- ✅ Current implementation status

**Before implementing any feature:**
1. Check [plan.md](plan.md) for the current phase and tasks
2. Review the checklist for that phase
3. Implement according to the detailed requirements
4. Update checkboxes in [plan.md](plan.md) as tasks are completed
5. Run the test commands provided in the phase
6. Move to the next phase only when all tasks are checked

## Project Overview

**NotionUsageInsights** is a Notion workspace analytics tool designed to generate comprehensive usage reports for organizations using Notion. The tool analyzes workspace data to provide insights on content creation, user engagement, collaboration patterns, cost efficiency, and knowledge risk.

**Current Status:** ✅ Phases 0-3 Complete + Unit Tests + Code Review (see [plan.md](plan.md) for details)
- ✅ Phase 0: Project Setup
- ✅ Phase 1: Environment Setup
- ✅ Phase 2: Configuration Module
- ✅ Phase 3: API Client Module
- ✅ Phase 8.1: Unit Tests (23 tests, all passing)
- ✅ Code Review Completed (see [code_review_20241004.md](code_review_20241004.md))
- 🟡 Phase 3.5: Code Quality Improvements (next)
- ⏳ Phase 4: Export Extractor (pending)

## Target Output

The tool aims to generate reports with these sections:

1. **Growth & Velocity** - Content creation trends, quarterly/monthly breakdowns, growth forecasts
2. **User Engagement** - Creator segmentation, top contributors, activity distribution
3. **Content Health** - Staleness analysis, abandoned pages, archive activity
4. **Collaboration** - Individual collaboration patterns, cross-functional work, single-owner vs multi-touch pages
5. **Structural Insights** - Content types, database usage, template adoption
6. **Cost Analysis** - Seat utilization, waste identification, ROI calculations
7. **Knowledge Risk** - Ownership concentration, bus factor, single-point-of-failure analysis

## Key Metrics to Implement

- **Pages created/edited over time** (daily, monthly, quarterly, yearly)
- **User activity segmentation** (Power, Active, Occasional, Minimal, Non-creators)
- **Staleness tracking** (last edit timestamps)
- **Collaboration scores** (ratio of others' pages edited to pages created)
- **Ownership concentration** (Gini coefficient, bus factor)
- **Template usage detection** (pattern matching on titles)
- **Cost per active user** calculations
- **Database vs. freeform page** classification

## Collaboration Metrics Definition

**Important:** The Notion API only provides `created_by` and `last_edited_by` for each page (not full edit history).

### Collaboration Score Formula
```python
collaboration_score = (others_pages_edited / pages_created) × 100
```

Where:
- `pages_created` = count of pages where user is `created_by`
- `others_pages_edited` = count of pages where user is `last_edited_by` BUT NOT `created_by`

**Interpretation:** For every 100 pages a user creates, how many pages created by others do they edit?
- **61%** = High collaborator (edits 61 others' pages per 100 created)
- **45%** = Moderate collaborator
- **<30%** = Low collaboration, more siloed

### Page-Level Collaboration
- **Single-owner page:** `created_by == last_edited_by` (only creator touched it)
- **Multi-touch page:** `created_by != last_edited_by` (at least 2 people involved)
- **Unique editors per page:** Either 1 (single-owner) or 2 (multi-touch)

### Implementation Example
```python
# Calculate user collaboration score
pages_created = df[df['created_by'] == user_id]
others_pages = df[
    (df['last_edited_by'] == user_id) &
    (df['created_by'] != user_id)
]
score = (len(others_pages) / len(pages_created)) * 100

# Identify multi-touch pages
df['is_collaborated'] = df['created_by'] != df['last_edited_by']
df['unique_editors'] = df['is_collaborated'].map({True: 2, False: 1})
```

## Architecture (To Be Implemented)

The tool will need to:

1. **Data Collection**
   - Authenticate with Notion API
   - Retrieve all page metadata (creation dates, edit dates, creators, editors)
   - Handle pagination for large workspaces
   - Support workspace exports as alternative data source

2. **Analysis Engine**
   - Time-series analysis for growth trends
   - User activity classification
   - Content freshness calculations
   - Collaboration graph analysis
   - Statistical metrics (Gini coefficient, concentration ratios)

3. **Report Generation**
   - Markdown formatting with tables and insights
   - Actionable recommendations based on thresholds
   - Visualization data preparation (for future charts/graphs)

## Implementation Considerations

### API Requirements
- Notion API access with read permissions for all pages
- Rate limiting handling (Notion API: 3 requests/second)
- Pagination support for workspaces with 10,000+ pages
- Incremental updates vs. full workspace scans

### API Limitations & Workarounds
**What the API provides per page:**
- `created_time`, `created_by` (user ID)
- `last_edited_time`, `last_edited_by` (user ID)
- `archived` (boolean)

**What the API does NOT provide:**
- Full edit history (only first and last editor)
- All contributors to a page (max 2: creator and last editor)
- Number of edits or edit frequency
- Page view counts or search analytics

**Workaround:** Use simplified collaboration metrics based on creator vs. last editor comparison (see Collaboration Metrics Definition above)

### Data Privacy
- API keys must never be committed to the repository
- User data should be anonymizable for demos/samples
- Consider GDPR/privacy requirements for user activity tracking

### Performance
- Large workspaces (20,000+ pages) will require efficient data processing
- Consider caching mechanisms for repeated analyses
- Incremental updates to avoid re-fetching entire workspace

### Output Format
- Primary: Markdown reports (like [sample_report.md](sample_report.md))
- Future: JSON/CSV exports for integration with BI tools
- Future: Interactive dashboards

## Technology Stack (Per Implementation Plan)

**Chosen stack:** Python 3.9+ with pandas/numpy for analytics

### Core Dependencies
- `notion-client` - Notion API wrapper
- `pandas`, `numpy` - Data processing and analytics
- `openpyxl`, `xlsxwriter` - Excel report generation
- `python-dotenv` - Environment configuration
- `tqdm` - Progress tracking

### Architecture Components
1. **API Client** (`src/api_client.py`) - Rate-limited Notion API calls with caching
2. **Export Extractor** (`src/extractors.py`) - Extract page IDs from workspace export
3. **Analytics Engine** (`src/analytics.py`) - All metric calculations
4. **Report Builder** (`src/report_builder.py`) - Excel report generation
5. **Main Orchestrator** (`main.py`) - Execution pipeline

See [plan.md](plan.md) for detailed implementation guide.

## Report Customization

Reports should support:
- **Date range selection** (e.g., "Last 90 days", "Q4 2024", "FY2024")
- **Threshold configuration** (e.g., staleness = 12 months vs. 6 months)
- **User segmentation rules** (e.g., "Power Creator" = 100+ pages vs. 50+ pages)
- **Cost parameters** (seat price, blended hourly rate)
- **Anonymization options** (mask user names in output)

## Development Workflow

**Follow these steps for any implementation work:**

### 1. Check Current Phase
Open [plan.md](plan.md) and find the current phase status:
- Look for phases marked 🟡 **IN PROGRESS** or ⬜ **TODO**
- Review all tasks in that phase

### 2. Implement According to Plan
- Each phase has detailed subtasks with checkboxes
- Each task includes specific requirements and code examples
- Follow the implementation order (don't skip phases)

### 3. Test Your Implementation
- Each phase includes test commands
- Run tests to verify implementation works
- Example: `python -c "from config import Config; Config.validate()"`

### 4. Update Progress
- Mark completed tasks with `[x]` in [plan.md](plan.md)
- Update phase status (⬜ → 🟡 → ✅)
- Add any notes or observations to the "Notes & Observations" section

### 5. Move to Next Phase
- Only proceed when ALL tasks in current phase are complete
- Update "Last Updated" timestamp in [plan.md](plan.md)

## Quick Start for Claude Code

When asked to implement a feature:
1. **First:** Open [plan.md](plan.md) and identify which phase it belongs to
2. **Then:** Check if prerequisite phases are complete
3. **Next:** Implement according to the phase checklist
4. **Finally:** Update [plan.md](plan.md) progress and run tests

**Example workflow:**
```
User: "Build the API client"
Claude:
1. Opens plan.md → Finds Phase 3: API Client Module
2. Checks Phase 2 is complete ✅
3. Implements following Phase 3.1 and 3.2 checklists
4. Updates plan.md checkboxes as tasks complete
5. Runs test command from Phase 3
```

## Testing Approach

**Unit tests are created alongside implementation:**
- Each major module should have corresponding test file in `tests/`
- Tests use pytest framework with custom markers (`@pytest.mark.slow`)
- Fast tests run in <1 second; slow tests (API integration) are skipped by default

**Current test coverage:**
```
tests/test_config.py       - 12 tests (Config module)
tests/test_api_client.py   - 11 tests (API client + 2 slow integration tests)
pytest.ini                 - Pytest configuration
```

**Test commands:**
```bash
pytest tests/              # Run all fast tests (default)
pytest tests/ -v           # Verbose output
pytest tests/ -m slow      # Run slow integration tests
pytest tests/test_config.py  # Run specific module
```

**When implementing new modules:**
1. Write the implementation first (following plan.md)
2. Create corresponding test file (e.g., `test_extractors.py`)
3. Test critical functions (validation, data processing, error handling)
4. Mark slow tests with `@pytest.mark.slow`
5. Update plan.md Phase 8.1 checklist

## Code Quality Standards

**Based on code review (code_review_20241004.md), all new code must follow these standards:**

### 1. Type Hints (Required)
```python
# ✅ Good - specific types
from typing import Dict, List, Optional, Any

def get_all_users(self, use_cache: bool = True) -> Dict[str, Dict[str, Any]]:
    """Fetch all workspace users"""
    pass

# ❌ Bad - generic 'any' or missing types
def get_all_users(self, use_cache=True):  # Missing return type
    pass

def _load_cache(self, cache_name: str) -> Optional[any]:  # Too generic
    pass
```

### 2. Logging Instead of Print
```python
# ✅ Good - use logging
import logging
logger = logging.getLogger(__name__)

def fetch_data():
    logger.info("Fetching data from API")
    logger.error(f"Failed to fetch: {error}")

# ❌ Bad - use print
def fetch_data():
    print("Fetching data from API")
    print(f"Error: {error}")
```

### 3. API Mocking in Tests
```python
# ✅ Good - mock API calls
def test_get_users_mocked(client, mocker):
    mock_response = {'results': [...], 'has_more': False}
    mocker.patch.object(client.client.users, 'list', return_value=mock_response)

    users = client.get_all_users(use_cache=False)
    assert len(users) > 0

# ❌ Bad - real API calls in unit tests
def test_get_users(client):
    users = client.get_all_users(use_cache=False)  # Makes real API call!
    assert len(users) > 0
```

### 4. Pure Functions for Analytics
```python
# ✅ Good - pure function, no I/O
def calculate_gini_coefficient(page_counts: List[int]) -> float:
    """Calculate Gini coefficient from page counts"""
    # Only calculations, no file/API access
    return coefficient

# ❌ Bad - mixed I/O and logic
def calculate_gini_coefficient(dataframe_path: str) -> float:
    df = pd.read_csv(dataframe_path)  # I/O mixed with calculation
    return coefficient
```

### 5. Error Handling with Retry
```python
# ✅ Good - retry logic for API calls (Phase 8.2)
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=10))
def get_page_details(self, page_id: str) -> Optional[Dict]:
    """Get page metadata with retry logic"""
    try:
        return self.client.pages.retrieve(page_id)
    except Exception as e:
        logger.error(f"Error fetching page {page_id}: {e}")
        raise

# ❌ Bad - no retry, silent failures
def get_page_details(self, page_id: str):
    try:
        return self.client.pages.retrieve(page_id)
    except:
        return None  # Silent failure
```

### 6. Module Purity Guidelines

**Analytics Module (`analytics.py`):**
- ✅ Accept DataFrames/dicts as input
- ✅ Return calculated results
- ❌ NO file I/O
- ❌ NO API calls

**Report Builder (`report_builder.py`):**
- ✅ Accept pre-calculated analytics data
- ✅ Focus on formatting and Excel generation
- ❌ NO data fetching
- ❌ NO calculations

**API Client (`api_client.py`):**
- ✅ Handle API interactions
- ✅ Manage caching
- ❌ NO analytics calculations
- ❌ NO report generation

### Type Checking

Run mypy before committing:
```bash
mypy src/ --ignore-missing-imports
```

### Pre-Commit Checklist

Before committing code:
1. ✅ All type hints added
2. ✅ Logging used instead of print
3. ✅ Tests written with mocks
4. ✅ mypy passes
5. ✅ pytest passes (fast tests)
6. ✅ No I/O in analytics functions
7. ✅ plan.md updated with progress

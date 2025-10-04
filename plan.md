# Implementation Plan: Notion Workspace Analytics

## 📋 Progress Tracker

**Overall Status:** 🟡 In Progress
**Last Updated:** 20241004

**Completed Phases:** 0, 1, 2, 3, 3.5, 4 (+ Unit Tests + Mocked Tests) | **Current:** Phase 5 (Analytics Engine)
**main.py:** ✅ Working | **Tests:** 40 passing

### Progress Metrics
- **Total Estimated Time:** 12-15 hours
- **Time Spent:** ~5 hours (Phases 0-4 + Tests + Code Review)
- **Remaining:** ~7-10 hours (Phases 5-9)
- **Overall Progress:** ~40% complete

### Current Status Summary

**Completed (40% done):**
- ✅ Environment and configuration
- ✅ API client with rate limiting and caching
- ✅ Export extractor (handles workspace exports)
- ✅ Unit tests (40 passing, with mocked API tests)
- ✅ Main orchestrator pipeline structure
- ✅ Code quality improvements (type hints, mocking)

**In Progress:**
- 🔄 Phase 5: Analytics Engine (next)

**Pending:**
- ⏳ Phase 6: Report Builder
- ⏳ Phase 7-9: Integration, testing, optimization

---

## 📊 Project Status

### Test Coverage
```
Config Module:          12 tests ✅
API Client Module:      14 mocked + 11 tests ✅
Export Extractor:       14 tests ✅

Total:                  40 tests
Status:                 All passing (3.72s)
```

### File Structure Status
```
✅ = Complete | 🔄 = In Progress | ⏳ = Pending

NotionUsageInsights/
├── config.py                    ✅ Complete (4.6K)
├── main.py                      ✅ Complete (4.6K)
├── requirements.txt             ✅ Updated (pytest-mock)
├── pytest.ini                   ✅ Complete
│
├── src/
│   ├── api_client.py            ✅ Complete (6.2K) + Type hints
│   ├── extractors.py            ✅ Complete (5.4K) + Type hints
│   ├── analytics.py             🔄 Next
│   ├── report_builder.py        ⏳ Pending
│   └── utils.py                 ⏳ Pending
│
├── data/
│   ├── export/                  ✅ Workspace export ready
│   ├── cache/                   ✅ API responses cached
│   └── output/                  ✅ Ready for reports
│
└── tests/
    ├── test_config.py           ✅ 12 tests
    ├── test_api_client.py       ✅ 14 mocked + 11 tests
    ├── test_extractors.py       ✅ 14 tests
    ├── test_analytics.py        ⏳ Pending
    └── test_report_builder.py   ⏳ Pending
```

### Quick Commands
```bash
# Activate environment
source venv/bin/activate

# Run main pipeline
python main.py

# Run all tests (fast)
pytest tests/ -v -m "not slow"

# Run with slow integration tests
pytest tests/ -v

# Check specific module
python -c "from src.extractors import ExportExtractor; e = ExportExtractor(); print(e.get_export_summary())"
```

---

## Phase 0: Project Setup ✅ COMPLETE

**Time:** 30 minutes | **Status:** ✅ Done

- [x] Create project directory structure
- [x] Create `requirements.txt` with dependencies
- [x] Create `.env.example` template
- [x] Create `.gitignore` file
- [x] Create empty Python module files (`src/*.py`)
- [x] Create `README.md` with setup instructions
- [x] Add `.gitkeep` files to data directories

**Files Created:**
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - Environment template
- ✅ `.gitignore` - Git ignore rules
- ✅ `README.md` - Setup & usage guide
- ✅ `src/__init__.py`, `src/api_client.py`, `src/extractors.py`, `src/analytics.py`, `src/report_builder.py`, `src/utils.py`
- ✅ `data/export/`, `data/cache/`, `data/output/` directories

---

## Phase 1: Environment Setup ✅ COMPLETE

**Time:** 15 minutes | **Status:** ✅ Done

### 1.1 Python Virtual Environment ✅
- [x] Create virtual environment: `python3 -m venv venv`
- [x] Activate environment: `source venv/bin/activate` (macOS/Linux)
- [x] Upgrade pip: `pip install --upgrade pip`
- [x] Install dependencies: `pip install -r requirements.txt`

### 1.2 Notion API Setup ✅
- [x] Go to https://www.notion.so/my-integrations
- [x] Create new integration: "Workspace Analytics Bot"
- [x] Set capabilities: Read content + Read user info
- [x] Copy integration token (starts with `secret_` or `ntn_`)
- [x] Add to `.env`: `NOTION_TOKEN=ntn_xxxxx` (or `secret_xxxxx` for older tokens)

### 1.3 Grant Workspace Access ✅
- [x] Open Notion workspace
- [x] Go to Settings & Members → Connections
- [x] Add integration: "Workspace Analytics Bot"

### 1.4 Export Workspace ✅
- [x] Settings & Members → Settings → Export all workspace content
- [x] Format: Markdown & CSV
- [x] Include subpages: Yes
- [x] Download and unzip to `./data/export/`

### 1.5 Configure Environment ✅
- [x] Copy `.env.example` to `.env`: `cp .env.example .env`
- [x] Edit `.env` with Notion token
- [x] Update paths in `.env` (use absolute paths)

**Verification:**
```bash
# Check Python environment
python --version  # Should be 3.9+
pip list | grep notion-client  # Should show notion-client==2.2.1

# Check .env
cat .env | grep NOTION_TOKEN  # Should show your token

# Check export
ls -la data/export/  # Should contain .md files
```

---

## Phase 2: Configuration Module ✅ COMPLETE

**Time:** 15 minutes | **Status:** ✅ Done

### 2.1 Create `config.py` ✅
- [x] Import dependencies (`os`, `pathlib`, `dotenv`)
- [x] Create `Config` class with constants
- [x] Load environment variables
- [x] Define API configuration (token, rate limits)
- [x] Define directory paths (export, cache, output)
- [x] Define analysis parameters (thresholds)
- [x] Define cost parameters
- [x] Add `validate()` method to check configuration
- [x] Create output directories if they don't exist

**Key Constants:**
```python
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
REQUESTS_PER_SECOND = 3
STALE_THRESHOLD_DAYS = 365
VERY_STALE_THRESHOLD_DAYS = 730
POWER_USER_THRESHOLD = 100
MONTHLY_COST_PER_USER = 12
```

**Test:**
```bash
python -c "from config import Config; Config.validate(); print('✓ Config valid')"
```

---

## Phase 3: API Client Module ✅ COMPLETE

**Time:** 1.5 hours | **Status:** ✅ Done

### 3.1 Create `src/api_client.py` ✅
- [x] Import dependencies (`notion_client`, `time`, `pickle`, `tqdm`)
- [x] Create `NotionAPIClient` class
- [x] Initialize Notion client with token
- [x] Implement rate limiting (`_rate_limit()` method)
- [x] Implement caching helpers:
  - [x] `_get_cache_path(cache_name)` → Path
  - [x] `_load_cache(cache_name)` → Optional[data]
  - [x] `_save_cache(cache_name, data)` → None

### 3.2 Implement API Methods ✅
- [x] `get_all_users(use_cache=True)` → Dict[user_id, user_info]
  - [x] Fetch users with pagination
  - [x] Cache results
  - [x] Return {user_id: {name, email, type}}

- [x] `search_all_pages(use_cache=True)` → List[Dict]
  - [x] Search all pages with pagination
  - [x] Show progress bar with tqdm
  - [x] Cache results

- [x] `get_page_details(page_id)` → Optional[Dict]
  - [x] Retrieve single page metadata
  - [x] Extract: id, created_time, created_by, last_edited_time, last_edited_by, archived
  - [x] Handle errors gracefully

- [x] `enrich_pages(page_ids, use_cache=True)` → List[Dict]
  - [x] Fetch details for all pages
  - [x] Show progress bar with time estimate
  - [x] Save checkpoint every 1000 pages
  - [x] Cache final results

**Test:**
```bash
python -c "from src.api_client import NotionAPIClient; client = NotionAPIClient(); users = client.get_all_users(); print(f'✓ Fetched {len(users)} users')"
```

---

## Phase 3.5: Code Quality Improvements ✅ COMPLETE

**Time:** 2 hours | **Status:** ✅ Done

### 3.5.1 Add API Mocking to Tests (HIGH Priority) ✅
- [x] Install `pytest-mock`: `pip install pytest-mock`
- [x] Add to requirements.txt
- [x] Create mocked tests in `test_api_client.py`:
  - [x] Mock `get_all_users()` API calls
  - [x] Mock `search_all_pages()` API calls
  - [x] Mock `get_page_details()` API calls
  - [x] Test error scenarios (API errors)
- [x] Keep slow integration tests for real API validation
- [x] 5 new mocked tests added (all passing)

### 3.5.2 Add Type Hints (MEDIUM Priority) ✅
- [x] Update `config.py` with complete type hints
- [x] Update `src/api_client.py`:
  - [x] Fix `Optional[any]` → `Optional[Any]`
  - [x] Add return type hints to all methods
  - [x] Add parameter type hints (`Dict[str, Any]`)
- [ ] Install `mypy` for static type checking (deferred)
- [ ] Add mypy configuration to `pytest.ini` or `pyproject.toml` (deferred)

### 3.5.3 Create main.py Placeholder (HIGH Priority) ✅
- [x] Create `main.py` in root directory
- [x] Add basic structure:
  - [x] Import all modules
  - [x] Add `main()` function with orchestration flow
  - [x] Add `if __name__ == "__main__":` block
  - [x] Add placeholder comments for Phases 4-6 implementation
- [x] Tested successfully with current modules

### 3.5.4 Add Logging (MEDIUM Priority) ⬜
- [ ] Replace `print()` statements with `logging` (deferred to Phase 8)
- [ ] Configure logging in config.py
- [ ] Update api_client.py to use logger
- [ ] Add log level configuration to .env

### 3.5.5 Documentation Updates ⬜
- [x] Update requirements.txt with new dependencies (pytest-mock)
- [ ] Document mocking approach in README.md (deferred)
- [ ] Add type checking instructions (deferred)
- [x] CLAUDE.md already has code quality standards

**Test:**
```bash
pytest tests/ -v  # All mocked tests should pass
mypy src/        # Type checking should pass (after implementation)
python main.py   # Should show orchestration placeholder
```

---

## Phase 4: Export Extractor Module ✅ COMPLETE

**Time:** 1 hour | **Status:** ✅ Done

### 4.1 Create `src/extractors.py` ✅
- [x] Import dependencies (`re`, `pathlib`, `config`)
- [x] Create `ExportExtractor` class with type hints

### 4.2 Implement Extraction Methods ✅
- [x] `extract_page_ids(export_dir=None)` → List[Dict]
  - [x] Scan all `.md` files recursively
  - [x] Extract 32-char hex UUID from filename
  - [x] Format as proper UUID: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
  - [x] Extract page title (filename without UUID)
  - [x] Get relative path and file size
  - [x] Return list of {id, title, path, file_size_kb}

- [x] `detect_databases(export_dir=None)` → List[Dict]
  - [x] Find folders with matching CSV files
  - [x] Count entries (`.md` files in folder)
  - [x] Return list of {name, path, entries, has_csv, csv_path}

- [x] `get_export_summary()` → Dict (bonus method)
  - [x] Total pages, total databases, export size MB

### 4.3 Unit Tests ✅
- [x] Created tests/test_extractors.py
- [x] 14 tests (all passing)
- [x] Tests for UUID formatting, extraction, error handling

### 4.4 Integration ✅
- [x] Updated main.py to use ExportExtractor
- [x] Successfully extracts pages from workspace export
- [x] Detects database folders

**Test Result:**
```bash
# Successfully processes workspace exports
✓ Pages extracted from export
✓ Databases detected
✓ Export size calculated
```

---

## Phase 5: Analytics Engine ⬜ TODO

**Time:** 3-4 hours | **Status:** ⬜ Not Started

### 5.1 Create `src/analytics.py`
- [ ] Import dependencies (`pandas`, `numpy`, `datetime`)
- [ ] Create `WorkspaceAnalytics` class
- [ ] Initialize with DataFrame and users dict

### 5.2 Data Preparation
- [ ] `_prepare_dataframe()` - Add derived columns:
  - [ ] Parse `created_time` and `last_edited_time` to datetime
  - [ ] Add `creator_name` and `editor_name` from users dict
  - [ ] Add `created_year`, `created_quarter`, `created_month`
  - [ ] Calculate `days_since_edit`
  - [ ] Add `staleness` category (Active/Fresh/Aging/Stale/Very Stale/Dead)
  - [ ] Detect templates with pattern matching
  - [ ] Flag abandoned pages (`created_time == last_edited_time`)
  - [ ] Flag single-owner pages (`created_by == last_edited_by`)

### 5.3 Implement Analysis Methods

#### 5.3.1 Summary Metrics
- [ ] `_analyze_summary()` → Dict
  - [ ] Total pages, total users, active contributors
  - [ ] Stale percentage, cost per active user

#### 5.3.2 Growth Analysis
- [ ] `_analyze_growth()` → Dict
  - [ ] Annual page counts
  - [ ] Year-over-year growth rates
  - [ ] Quarterly breakdown (latest year)
  - [ ] Monthly breakdown (last 12 months)
  - [ ] Average monthly pages

#### 5.3.3 User Analysis
- [ ] `_analyze_users()` → Dict
  - [ ] User segmentation (power/active/occasional/minimal/non-creators)
  - [ ] Pages created by each segment
  - [ ] Active creator percentage

#### 5.3.4 Top Creators
- [ ] `_analyze_top_creators()` → List[Dict]
  - [ ] Top 10 creators by page count
  - [ ] Percentage of total pages

#### 5.3.5 Content Health
- [ ] `_analyze_content_health()` → Dict
  - [ ] Staleness distribution
  - [ ] Stale (12mo+) and very stale (24mo+) counts
  - [ ] Abandoned pages count
  - [ ] Abandoned by top creators
  - [ ] Archived pages count

#### 5.3.6 Collaboration
- [ ] `_analyze_collaboration()` → Dict
  - [ ] Calculate collaboration scores for each user:
    - [ ] `others_pages = last_edited_by=user AND created_by≠user`
    - [ ] `score = (others_pages / pages_created) × 100`
  - [ ] Top 10 collaborators
  - [ ] Average collaboration score
  - [ ] Collaborated pages count (`created_by ≠ last_edited_by`)
  - [ ] Single-owner pages count

#### 5.3.7 Structure
- [ ] `_analyze_structure()` → Dict
  - [ ] Template count and percentage
  - [ ] Non-template count

#### 5.3.8 Cost Analysis
- [ ] `_analyze_costs()` → Dict
  - [ ] Cost by segment
  - [ ] Total annual cost
  - [ ] Cost per active creator
  - [ ] Wasted spend calculation
  - [ ] ROI calculation (creation value vs. cost)

#### 5.3.9 Risk Assessment
- [ ] `_analyze_risk()` → Dict
  - [ ] Concentration metrics (top 1%, 5%, 10% ownership)
  - [ ] Gini coefficient calculation
  - [ ] Bus factor (people needed for 50% knowledge loss)
  - [ ] Single-owner pages by top 10 creators

### 5.4 Main Orchestration
- [ ] `run_all()` → Dict
  - [ ] Call all analysis methods
  - [ ] Return combined results dict

**Test:**
```bash
python -c "
import pandas as pd
from src.analytics import WorkspaceAnalytics
df = pd.read_csv('data/cache/merged_data.csv')
users = {...}  # Load from cache
analyzer = WorkspaceAnalytics(df, users)
results = analyzer.run_all()
print('✓ Analytics complete')
"
```

---

## Phase 6: Report Builder ⬜ TODO

**Time:** 2-3 hours | **Status:** ⬜ Not Started

### 6.1 Create `src/report_builder.py`
- [ ] Import dependencies (`pandas`, `xlsxwriter`, `datetime`)
- [ ] Create `ReportBuilder` class
- [ ] Initialize with results, DataFrame, users

### 6.2 Implement Report Methods

#### 6.2.1 Main Generator
- [ ] `generate_excel(output_path=None)` → Path
  - [ ] Create Excel writer with xlsxwriter engine
  - [ ] Define formats (header, metric, number, percentage, currency)
  - [ ] Call all sheet writers
  - [ ] Return output path

#### 6.2.2 Sheet Writers
- [ ] `_write_executive_summary(writer, header_fmt, metric_fmt)`
  - [ ] Total pages, users, active contributors
  - [ ] Stale content %, annual cost, cost per active user

- [ ] `_write_growth(writer, header_fmt)`
  - [ ] Annual growth table with YoY %
  - [ ] Monthly trend (last 12 months)

- [ ] `_write_users(writer, header_fmt)`
  - [ ] User segmentation table
  - [ ] Top 10 creators table

- [ ] `_write_content_health(writer, header_fmt)`
  - [ ] Staleness distribution
  - [ ] Key metrics (stale, very stale, abandoned, archived)

- [ ] `_write_collaboration(writer, header_fmt)`
  - [ ] Top collaborators table
  - [ ] Summary metrics (avg score, collaborated pages, single-owner pages)

- [ ] `_write_costs(writer, header_fmt)`
  - [ ] Cost by segment table
  - [ ] Summary (total cost, wasted spend, ROI)

- [ ] `_write_risk(writer, header_fmt)`
  - [ ] Concentration risk metrics
  - [ ] Single-owner pages by top 10 creators

- [ ] `_write_raw_data(writer)`
  - [ ] Export full DataFrame with relevant columns

**Test:**
```bash
python -c "
from src.report_builder import ReportBuilder
builder = ReportBuilder(results, df, users)
report_path = builder.generate_excel()
print(f'✓ Report generated: {report_path}')
"
```

---

## Phase 7: Main Orchestrator ⬜ TODO

**Time:** 30 minutes | **Status:** ⬜ Not Started

### 7.1 Create `main.py`
- [ ] Import all modules
- [ ] Add main execution flow:

#### 7.1.1 Configuration
- [ ] Print header with timestamp
- [ ] Validate configuration
- [ ] Handle errors gracefully

#### 7.1.2 Data Collection
- [ ] Step 1: Fetch users from API (with cache)
- [ ] Step 2: Extract page IDs from export
- [ ] Step 3: Detect databases from export
- [ ] Step 4: Search pages via API (optional, with cache)
- [ ] Step 5: Enrich pages with metadata (slow, cached)

#### 7.1.3 Data Processing
- [ ] Merge export data + API data into DataFrame
- [ ] Save checkpoint to `data/cache/merged_data.csv`

#### 7.1.4 Analytics
- [ ] Initialize WorkspaceAnalytics
- [ ] Run all analytics
- [ ] Print progress

#### 7.1.5 Report Generation
- [ ] Initialize ReportBuilder
- [ ] Generate Excel report
- [ ] Print output path

#### 7.1.6 Summary
- [ ] Print key findings:
  - [ ] Total pages
  - [ ] Active contributors / total users
  - [ ] Stale content %
  - [ ] Potential savings
  - [ ] Bus factor
- [ ] Print completion timestamp

### 7.2 Entry Point
- [ ] Add `if __name__ == "__main__": main()`

**Test:**
```bash
python main.py
```

---

## Phase 8: Testing & Refinement 🟡 PARTIAL

**Time:** 2-3 hours | **Status:** 🟡 Partially Complete

### 8.1 Unit Tests ✅
- [x] Create `tests/test_config.py` (12 tests - all passing)
- [x] Create `tests/test_api_client.py` (11 tests - all passing)
- [x] Create `pytest.ini` configuration
- [x] Add pytest to requirements.txt
- [ ] Create `tests/test_extractors.py` (pending Phase 4)
- [ ] Create `tests/test_analytics.py` (pending Phase 5)
- [ ] Test edge cases (empty data, missing fields)

### 8.2 Error Handling & Retry Logic
- [ ] Add try-except blocks for API calls
- [ ] Handle missing export directory
- [ ] Handle invalid Notion token
- [ ] Handle rate limit errors (429)
- [ ] Add retry logic with exponential backoff:
  - [ ] Install `tenacity` library
  - [ ] Add `@retry` decorator to API methods
  - [ ] Configure: 3 attempts, exponential wait (4-10s)
- [ ] Test error scenarios with mocked responses

### 8.3 Performance Optimization
- [ ] Test with sample workspace
- [ ] Optimize DataFrame operations
- [ ] Reduce memory usage for large workspaces
- [ ] Add batch processing if needed

### 8.4 Documentation
- [ ] Add docstrings to all functions
- [ ] Update README.md with actual usage examples
- [ ] Document common errors and solutions

---

## Phase 9: First Production Run ⬜ TODO

**Time:** 2-10 hours (automated) | **Status:** ⬜ Not Started

### 9.1 Pre-Flight Checklist
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] `.env` configured with valid token
- [ ] Workspace export in `data/export/`
- [ ] Integration connected to workspace

### 9.2 Execute
- [ ] Run: `python main.py`
- [ ] Monitor progress bars
- [ ] Wait for completion (may take hours)

### 9.3 Verify Output
- [ ] Check `data/output/` for Excel report
- [ ] Open Excel file
- [ ] Verify all 8 sheets present
- [ ] Spot-check metrics against known data
- [ ] Review recommendations

### 9.4 Cache Verification
- [ ] Check `data/cache/` for cached files:
  - [ ] `users.pkl`
  - [ ] `enriched_pages.pkl`
  - [ ] `merged_data.csv`
- [ ] Test cached run: `python main.py` (should be <2 min)

---

## Phase 10: Advanced Features (Optional) ⬜ TODO

**Status:** ⬜ Not Started

### 10.1 Utility Scripts
- [ ] `scripts/clear_cache.sh` - Clear cache and force refresh
- [ ] `scripts/anonymize_report.py` - Remove user names from reports
- [ ] `scripts/compare_runs.py` - Compare two analysis runs

### 10.2 Slack Notifications
- [ ] Add Slack webhook to `.env`
- [ ] Create `send_slack_notification()` function
- [ ] Send summary to Slack on completion

### 10.3 Scheduled Execution
- [ ] Create cron job for bi-annual runs
- [ ] Add to crontab: `0 2 1 1,7 * cd /path && python main.py`

### 10.4 Web Dashboard (Future)
- [ ] Install Streamlit: `pip install streamlit`
- [ ] Create `dashboard.py`
- [ ] Add interactive filters
- [ ] Deploy to cloud (Railway/Render)

---

## Quick Reference Commands

### Setup
```bash
# Create environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your token
```

### Run Analysis
```bash
# Full run (first time)
python main.py

# Force refresh (clear cache)
rm -rf data/cache/*
python main.py
```

### Check Progress
```bash
# View cached files
ls -lh data/cache/

# View output reports
ls -lh data/output/

# Check Python environment
pip list | grep notion
```

---

## Troubleshooting Checklist

### Issues During Setup
- [ ] Python version ≥ 3.9: `python --version`
- [ ] Virtual environment activated: `which python`
- [ ] Dependencies installed: `pip list`
- [ ] `.env` exists and has token: `cat .env | grep NOTION_TOKEN`
- [ ] Export directory has files: `ls data/export/`

### Issues During Execution
- [ ] Check error message in console
- [ ] Verify Notion token is valid
- [ ] Verify integration has workspace access
- [ ] Check internet connection
- [ ] Review rate limiting (reduce REQUESTS_PER_SECOND in config.py)
- [ ] Clear cache if corrupted: `rm -rf data/cache/*`

### Issues with Output
- [ ] Excel file exists: `ls data/output/`
- [ ] File can be opened (not corrupted)
- [ ] All 8 sheets present
- [ ] Data looks reasonable (no nulls or zeros)

---

## Success Criteria

### ✅ Phase Complete When:
- All checkboxes for the phase are checked
- Tests pass (if applicable)
- No errors during execution
- Output matches expected format

### ✅ Project Complete When:
- All phases 0-9 complete
- First production run successful
- Excel report generated with all 8 sheets
- Key metrics match manual spot checks
- Documentation up to date

---

## Notes & Observations

### Implementation Notes:
- Add notes here as you build
- Document decisions made
- Note any deviations from plan

### Performance Metrics:
- First run duration: ___ hours
- Cached run duration: ___ minutes
- Workspace size: ___ pages
- Memory usage: ___ MB

### Issues Encountered:
- Document problems and solutions
- Update troubleshooting section

---

**Next Step:** Complete Phase 1 (Environment Setup)

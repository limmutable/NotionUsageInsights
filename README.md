# Notion Workspace Analytics

Automated analytics system for Notion workspaces. Generates comprehensive reports on usage, content health, collaboration patterns, and cost optimization.

## Features

- 📊 **Growth & Velocity** - Content creation trends, quarterly/monthly breakdowns, growth forecasts
- 👥 **User Engagement** - Creator segmentation, top contributors, activity distribution
- 🔍 **Content Health** - Staleness analysis, abandoned pages, archive activity
- 🤝 **Collaboration** - Individual collaboration patterns, cross-functional work analysis
- 📁 **Structural Insights** - Content types, database usage, template adoption
- 💰 **Cost Analysis** - Seat utilization, waste identification, ROI calculations
- ⚠️ **Knowledge Risk** - Ownership concentration, bus factor, single-point-of-failure analysis

## Prerequisites

- Python 3.9 or higher
- Notion workspace admin access
- Notion integration token (API access)
- Notion workspace export (Markdown & CSV format)

## Installation

### 1. Clone or Download Repository

```bash
cd ~/Projects/NotionUsageInsights
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# - Add your Notion integration token
# - Update directory paths if needed
```

## Setup Notion Integration

### 1. Create Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click **"New integration"**
3. Settings:
   - **Name:** `Workspace Analytics Bot`
   - **Associated workspace:** [Your workspace]
   - **Capabilities:**
     - ✅ Read content
     - ✅ Read user information (without email addresses)
     - ❌ No write permissions needed
   - **Type:** Internal integration
4. Click **Submit**
5. Copy the **Internal Integration Token** (starts with `ntn_` or `secret_`)
6. Add to `.env` file: `NOTION_TOKEN=ntn_xxxxxx...` (or `secret_xxxxx...` for older tokens)

### 2. Share Workspace with Integration

1. Open your Notion workspace
2. Go to **Settings & Members** → **Connections**
3. Find and add your integration: `Workspace Analytics Bot`
4. This grants access to all pages in the workspace

### 3. Export Workspace

1. **Settings & Members** → **Settings** → **Export all workspace content**
2. Export format: **Markdown & CSV**
3. Include subpages: ✅ **Yes**
4. Click **Export**
5. Download and unzip the export
6. Move contents to `./data/export/` directory

```bash
# Example
unzip ~/Downloads/Export-xxxxx.zip -d ./data/export/
```

## Usage

### Run Analysis

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run analysis
python main.py
```

### First Run (2-10 hours)
- Fetches all workspace data via API
- Rate-limited to 3 requests/second (Notion API limit)
- For 23,450 pages: ~2 hours
- Progress bars show status
- Results are cached

### Subsequent Runs (~2 minutes)
- Uses cached data
- Near-instant results
- No API calls needed

### Force Refresh

```bash
# Clear cache to fetch fresh data
rm -rf data/cache/*
python main.py
```

## Output

### Excel Report
Generated at: `./data/output/workspace_analytics_TIMESTAMP.xlsx`

**8 Sheets:**
1. **Executive Summary** - Key metrics overview
2. **Growth & Velocity** - Annual, quarterly, monthly trends
3. **User Analytics** - Segmentation and top creators
4. **Content Health** - Staleness, abandoned pages, archives
5. **Collaboration** - Individual scores and patterns
6. **Cost Analysis** - Utilization, waste, ROI
7. **Risk Assessment** - Concentration, bus factor
8. **Raw Data** - Full dataset for custom analysis

### Console Output
```
============================================================
NOTION WORKSPACE ANALYTICS
============================================================
Started: 2024-01-15 14:30:00

✓ Configuration validated
✓ Fetched 285 users
✓ Extracted 23,450 pages from export
✓ Enriched 23,450 pages
✓ Analytics complete

📊 Key Findings:
  Total Pages: 23,450
  Active Contributors: 156 / 285
  Stale Content: 42.0%
  Potential Savings: $15,984/year
  Knowledge Risk (Bus Factor): 3 people

📁 Report: ./data/output/workspace_analytics_20240115_163045.xlsx
```

## Configuration

Edit `config.py` or `.env` to customize:

### Analysis Parameters
- `STALE_THRESHOLD_DAYS` - Days before page considered stale (default: 365)
- `VERY_STALE_THRESHOLD_DAYS` - Days before very stale (default: 730)
- `POWER_USER_THRESHOLD` - Pages/year for "Power Creator" (default: 100)
- `ACTIVE_USER_THRESHOLD` - Pages/year for "Active" (default: 20)
- `OCCASIONAL_USER_THRESHOLD` - Pages/year for "Occasional" (default: 5)

### Cost Parameters
- `MONTHLY_COST_PER_USER` - Notion seat cost (default: $12)
- `BLENDED_HOURLY_RATE` - For ROI calculations (default: $48)

## Project Structure

```
notion-analytics/
├── main.py                  # Main execution script (TBD)
├── config.py               # Configuration and constants ✅
├── requirements.txt        # Python dependencies ✅
├── pytest.ini             # Pytest configuration ✅
├── .env                   # Environment variables (gitignored) ✅
├── .env.example          # Template for .env ✅
│
├── src/
│   ├── api_client.py      # Notion API wrapper ✅
│   ├── extractors.py      # Export file parsing (TBD)
│   ├── analytics.py       # Analytics calculations (TBD)
│   ├── report_builder.py  # Excel report generation (TBD)
│   └── utils.py          # Helper functions
│
├── data/
│   ├── export/           # Notion workspace export ✅
│   ├── cache/            # Cached API responses ✅
│   └── output/           # Generated reports ✅
│
└── tests/               # Unit tests ✅
    ├── test_config.py      # Config module tests (12 tests)
    └── test_api_client.py  # API client tests (11 tests)
```

**Implementation Status:**
- ✅ Phase 0: Project Setup (Complete)
- ✅ Phase 1: Environment Setup (Complete)
- ✅ Phase 2: Configuration Module (Complete)
- ✅ Phase 3: API Client Module (Complete)
- ✅ Phase 8.1: Unit Tests for Phases 0-3 (Complete)
- 🔄 Phase 3.5: Code Quality Improvements (Next - based on code review)
  - API mocking, type hints, logging, main.py placeholder
- ⏳ Phase 4: Export Extractor (Pending)

See [plan.md](plan.md) for detailed progress tracking.
See [code_review_20241004.md](code_review_20241004.md) for code review recommendations.

## Testing

### Run Unit Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all fast tests (recommended)
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py

# Run slow integration tests (requires API calls)
pytest tests/ -m slow
```

### Test Coverage

**Config Module** (`test_config.py`) - 12 tests
- Token validation and format checking
- Directory path verification
- Threshold and cost parameter validation
- Config validation logic

**API Client Module** (`test_api_client.py`) - 11 tests
- Client initialization and rate limiting
- Cache save/load functionality
- User fetching and data structure validation
- Error handling for invalid page IDs

**Test Results:**
```
21 passed, 2 deselected in 0.63s
```

All essential functionality is tested and verified!

### Code Quality Standards

**Type Checking (coming in Phase 3.5):**
```bash
# Install mypy
pip install mypy

# Run type checker
mypy src/
```

**Test Coverage Best Practices:**
- Fast unit tests use mocks for API calls
- Slow integration tests marked with `@pytest.mark.slow`
- Run fast tests during development, slow tests before commits

**Code Review:**
A comprehensive code review was conducted (see [code_review_20241004.md](code_review_20241004.md)). Key improvements planned:
- ✅ API mocking for faster, more reliable tests
- ✅ Type hints for better code clarity and IDE support
- ✅ Logging instead of print statements
- ✅ Retry logic for resilient API calls

## Troubleshooting

### Error: "NOTION_TOKEN not set"
```bash
# Check .env file exists and has token
cat .env | grep NOTION_TOKEN
```

### Error: "Export directory not found"
```bash
# Verify export path and contents
ls -la ./data/export/
# Should contain .md files
```

### Error: "Rate limit exceeded"
```python
# In config.py, reduce requests per second
REQUESTS_PER_SECOND = 2  # Slower but safer
```

### Memory Issues (Large Workspaces)
Process in batches - modify `api_client.py`:
```python
# Process 5000 pages at a time instead of all at once
```

### Cache Corruption
```bash
# Clear cache and re-run
rm -rf data/cache/*
python main.py
```

## Performance

- **Workspace Size:** Tested up to 50,000 pages
- **First Run:** 2-10 hours (depends on page count)
- **Cached Runs:** ~2 minutes
- **API Rate Limit:** 3 requests/second (Notion limit)
- **Memory Usage:** ~500MB for 25,000 pages

## Development

See [plan.md](plan.md) for detailed implementation guide.

See [CLAUDE.md](CLAUDE.md) for project architecture and collaboration metrics definitions.

## License

MIT

## Support

For issues or questions, refer to:
- [plan.md](plan.md) - Implementation details
- [sample_report.md](sample_report.md) - Example output
- [CLAUDE.md](CLAUDE.md) - Technical documentation

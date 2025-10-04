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

### Markdown Report
Generated at: `./data/output/workspace_analytics_TIMESTAMP.md`

**Report Sections:**
1. **Executive Summary** - Key metrics overview with visual indicators
2. **Growth & Velocity** - Annual, quarterly, monthly trends in tables
3. **User Analytics** - Segmentation and top creators ranked
4. **Content Health** - Staleness distribution, abandoned pages
5. **Collaboration** - Individual scores and patterns
6. **Cost Analysis** - Utilization, waste, ROI calculations
7. **Risk Assessment** - Concentration metrics, bus factor
8. **Detailed Tables** - Full dataset tables for deeper analysis

The Markdown format allows you to:
- Import directly into Notion
- Convert to HTML/PDF with pandoc
- View in any Markdown viewer
- Edit and customize easily

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

📁 Report: ./data/output/workspace_analytics_20240115_163045.md
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
├── main.py                  # Main execution script
├── config.py               # Configuration and constants
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (gitignored)
├── .env.example          # Template for .env
│
├── src/
│   ├── api_client.py      # Notion API wrapper with caching
│   ├── extractors.py      # Export file parsing
│   ├── analytics.py       # Analytics calculations
│   ├── report_builder.py  # Markdown report generation
│   └── utils.py          # Helper functions
│
├── data/
│   ├── export/           # Notion workspace export
│   ├── cache/            # Cached API responses
│   └── output/           # Generated reports
│
└── tests/               # Unit tests (40 passing tests)
    ├── test_config.py
    ├── test_api_client.py
    └── test_extractors.py
```

## Development Status

This project is under active development. See [plan.md](plan.md) for detailed implementation progress.

**Current Status:**
- ✅ Core infrastructure (config, API client, export parsing)
- ✅ Comprehensive test suite (40 passing tests)
- 🔄 Analytics engine (in progress)
- ⏳ Report generation (planned)

**Future Enhancements:**
- Advanced collaboration metrics
- Interactive dashboard
- Scheduled report generation
- Multi-workspace support

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

The project includes comprehensive unit tests with mocked API calls to avoid network dependencies.

```bash
# Test results
40 passed, 2 deselected (slow integration tests)

# Modules tested:
- Configuration (12 tests)
- API Client (14 mocked + 11 tests)
- Export Extractor (14 tests)
```

### Code Quality

The project follows Python best practices:
- Type hints for all function signatures
- Comprehensive unit tests with mocked API calls
- Separation of concerns (config, API, extraction, analytics)
- Error handling and validation throughout

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

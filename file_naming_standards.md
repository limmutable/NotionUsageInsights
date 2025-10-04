# File Naming Standards

**Last Updated:** 20241003

## 📋 Naming Convention Rules

### 1. Root Documentation Files → UPPERCASE
Standard documentation files use UPPERCASE for visibility and recognition.

**Examples:**
- `README.md` - Project overview and setup
- `CLAUDE.md` - Claude Code implementation guidelines
- `.gitignore` - Git ignore configuration
- `.env.example` - Environment variable template

**Why:** Industry standard for important project documentation files.

---

### 2. User-Created Documentation → lowercase_with_underscores
All other documentation uses lowercase with underscores for word separation.

**Living Documents (no datetime):**
- `plan.md` - Implementation plan (continuously updated)
- `sample_report.md` - Example template
- `file_naming_standards.md` - Project conventions

**Point-in-Time Snapshots (with datetime suffix):**
- `code_review_20241004.md` - Code review from Oct 4, 2024
- `code_review_actions_20241004.md` - Action plan from review
- `project_status_20241003.md` - Status snapshot from Oct 3, 2024

**Datetime Format:** `YYYYMMDD` (Compact date format)
- Allows chronological sorting
- No separators needed
- Example: `meeting_notes_20241215.md`

**Why:** Consistent with Python source code naming, allows version history, easier to type.

---

### 3. Source Code → lowercase_with_underscores
All Python source code follows PEP 8 style guide.

**Examples:**
- `config.py` - Configuration module
- `main.py` - Main entry point
- `src/api_client.py` - API client module
- `src/extractors.py` - Export extraction module
- `src/analytics.py` - Analytics engine
- `src/report_builder.py` - Report generation module
- `tests/test_config.py` - Config tests
- `tests/test_api_client.py` - API client tests

**Why:** Python PEP 8 style guide, standard practice.

---

### 4. Configuration Files → standard names
Configuration files use lowercase and standard naming conventions.

**Examples:**
- `requirements.txt` - Python dependencies
- `pytest.ini` - Pytest configuration
- `.env` - Environment variables (gitignored)
- `pyproject.toml` - Python project configuration (if needed)

**Why:** Standard convention recognized by tools.

---

### 5. Output Files → lowercase_with_datetime
Generated reports and outputs should include datetime stamps for tracking.

**Format:** `{type}_{description}_YYYYMMDDHHMMSS.{ext}`

**Examples:**
- `workspace_analytics_20241015143052.xlsx` - Excel report
- `cache_checkpoint_20241015120000.pkl` - Cache checkpoint
- `export_summary_20241015.json` - Export summary

**Why:**
- Easy to identify when report was generated
- Allows keeping multiple versions
- Prevents overwriting previous runs
- Chronological sorting

---

## ❌ What NOT to Use

### Never Use:
- ❌ **camelCase** (e.g., `apiClient.py`, `codeReview.md`)
- ❌ **PascalCase** (e.g., `ApiClient.py`, `CodeReview.md`)
- ❌ **Mixed conventions** (e.g., `Code_Review.md`, `API_client.py`)
- ❌ **Spaces** (e.g., `code review.md`, `api client.py`)
- ❌ **Hyphens in Python files** (e.g., `api-client.py` - cannot import)

### Why These Are Bad:
- Inconsistent with team standards
- Harder to remember which format
- PascalCase suggests class names (confusing)
- Spaces break command-line tools
- Hyphens cannot be imported in Python

---

## 📁 Complete File Listing (Current)

```
NotionUsageInsights/
├── README.md                      # UPPERCASE - standard doc
├── CLAUDE.md                      # UPPERCASE - standard doc
├── .gitignore                     # UPPERCASE - standard config
├── .env.example                   # UPPERCASE - standard config
│
├── plan.md                        # lowercase - user doc
├── code_review_20241004.md                   # lowercase - user doc
├── code_review_actions_20241004.md           # lowercase - user doc
├── project_status_20241003.md                # lowercase - user doc
├── sample_report.md               # lowercase - user doc
│
├── config.py                      # lowercase - source code
├── main.py                        # lowercase - source code
├── requirements.txt               # lowercase - standard config
├── pytest.ini                     # lowercase - standard config
│
├── src/
│   ├── api_client.py              # lowercase - source code
│   ├── extractors.py              # lowercase - source code
│   ├── analytics.py               # lowercase - source code
│   ├── report_builder.py          # lowercase - source code
│   └── utils.py                   # lowercase - source code
│
└── tests/
    ├── test_config.py             # lowercase - source code
    └── test_api_client.py         # lowercase - source code
```

---

## 🔄 Changes Made (20241003)

### Renamed for Consistency:
1. `codereview.md` → `code_review_20241004.md`
2. `CODE_REVIEW_ACTIONS.md` → `code_review_actions_20241004.md`
3. `PROJECT_STATUS.md` → `project_status_20241003.md`

### References Updated In:
- ✅ CLAUDE.md
- ✅ README.md
- ✅ plan.md
- ✅ project_status_20241003.md
- ✅ code_review_20241004.md
- ✅ code_review_actions_20241004.md
- ✅ sample_report.md

---

## ✅ Quick Reference

**When creating new files:**

| File Type | Convention | Example |
|-----------|------------|---------|
| Standard doc | UPPERCASE | `README.md`, `LICENSE` |
| Living doc | lowercase_underscore | `plan.md`, `sample_report.md` |
| Snapshot doc | lowercase_YYYYMMDD | `code_review_20241004.md` |
| Python source | lowercase_underscore | `my_module.py` |
| Python test | test_lowercase_underscore | `test_my_module.py` |
| Config file | lowercase | `requirements.txt` |
| Output file | lowercase_YYYYMMDDHHMMSS | `report_20241015143052.xlsx` |

**Datetime Decision Tree:**
1. Is it continuously updated? → **NO datetime** (e.g., `plan.md`)
2. Is it a point-in-time snapshot? → **Add datetime** (e.g., `status_20241003.md`)
3. Is it generated output? → **Add datetime + time** (e.g., `report_20241015143052.xlsx`)

---

## 📝 Enforcement

**Before creating any new file:**
1. Check this document for the correct convention
2. Follow the pattern for similar existing files
3. Never mix conventions within a file type

**During code review:**
- Flag any files that don't follow conventions
- Request renaming before merge

---

**Reference:** This standard is documented in [CLAUDE.md](CLAUDE.md) under "File Naming Conventions"

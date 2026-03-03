# Repository Hygiene Report

**Date**: 2026-03-03  
**Status**: Ready for GitHub upload  
**Action Required**: Apply `.gitignore` and review recommendations

---

## 1. Audit Summary

### Large Files (>100 KB)

| File | Size | Type | Status |
|------|------|------|--------|
| `01_data/kwic_exports/cases_raw_v1.csv` | 126 MB | Data (intermediate) | ⚠️ EXCLUDE |
| `01_data/kwic_exports/cases_raw_v2.csv` | 122 MB | Data (intermediate) | ⚠️ EXCLUDE |
| `01_data/kwic_exports/cases_raw.csv` | 122 MB | Data (intermediate) | ⚠️ EXCLUDE |
| `04_outputs/tables/units_enriched.csv` | 5.8 MB | Data (intermediate) | ⚠️ EXCLUDE |
| `01_data/text/units.csv` | 5.8 MB | Data (intermediate) | ⚠️ EXCLUDE |
| `03_analysis/cases/emigrante_kwic_cases.csv` | 500 KB | Data (analysis) | ⚠️ EXCLUDE |
| `04_outputs/tables/case_rankings_enriched.csv` | 490 KB | Data (intermediate) | ⚠️ EXCLUDE |
| `04_outputs/tables/case_rankings.csv` | 385 KB | Data (intermediate) | ⚠️ EXCLUDE |

**Total Raw Data**: ~371 MB (not including PDFs, TEI-XML)

### PDF Inventory

- **Total PDFs**: 150 files
- **Type**: All publication-ready figures (PNG exports to PDF format)
- **Location**: `04_outputs/figures/static/` and `05_freeze/v1.0.2-lite/figures/`
- **Status**: ✅ KEEP (project-generated, no copyright issues)
- **Examples**: `fig_emigrant_by_format_es.pdf`, `fig_production_timeline.pdf`, etc.

### Cache & Temporary Directories Found

| Directory | Count | Status | Action |
|-----------|-------|--------|--------|
| `.venv/` | ~500,000 files | 🚫 EXCLUDE | Add to `.gitignore` |
| `__pycache__/` | ~200 locations | 🚫 EXCLUDE | Add to `.gitignore` |
| `.DS_Store` | 4 files | 🚫 EXCLUDE | Add to `.gitignore` |

### macOS/System Files

| File | Count | Status |
|------|-------|--------|
| `.DS_Store` | 4 | ❌ Remove before commit |
| `.git/COMMIT_EDITMSG`, etc. | (if repo exists) | ❌ Already in `.git/` |

---

## 2. Files to EXCLUDE from GitHub

### A. Virtual Environments & Package Cache

```
.venv/                   # Python virtual environment
venv/
env/
__pycache__/            # Python bytecode cache
*.pyc
*.pyo
*.egg-info/
.pytest_cache/
```

**Size Impact**: ~1GB+ (mostly from `.venv/lib/`)  
**Reason**: Environment-specific, recreatable via `requirements.txt`

### B. Large Intermediate Data Files

```
01_data/kwic_exports/   # Raw KWIC output (370 MB total)
  - cases_raw.csv       # 122 MB
  - cases_raw_v1.csv    # 126 MB
  - cases_raw_v2.csv    # 122 MB

04_outputs/tables/      # Intermediate analysis outputs
  - units_enriched.csv  # 5.8 MB
  - case_rankings_enriched.csv
  - case_rankings.csv
  
01_data/text/
  - units.csv           # 5.8 MB
```

**Reason**: Regenerable from source TEI corpus and scripts  
**GitHub Size Limit**: Soft limit ~100 MB per repo; hard limit ~2 GB

### C. Version Control & IDE Files

```
.git/                   # Already .git/; don't track this
.vscode/settings.json   # IDE user settings (keep locally)
.idea/                  # JetBrains IDE cache
*.swp *.swo            # Vim temporary files
```

### D. macOS System Files

```
.DS_Store              # macOS folder metadata
.AppleDouble/
__MACOSX/
.Spotlight-V100/
.Trashes/
```

### E. Documentation/Zenodo Artifacts (Temporary)

```
zenodo/                # Zenodo deposit package (local-only)
                       # Upload directly to Zenodo, don't version
ZENODO_PACKAGE_SUMMARY.md  # Generated summary (for reference only)
```

**Reason**: This is deployment artifact, not source code

---

## 3. Files to KEEP in GitHub

### ✅ Essential for Reproducibility

```
02_methods/scripts_core/           # Core analysis scripts
02_methods/scripts_viz/            # Visualization scripts
02_methods/scripts_metadata/       # Metadata extraction
02_methods/patterns/               # Lexicon (YAML config)
  - emigrante_markers.yml         # 35-marker detection lexicon
  
00_docs/                           # All documentation
  - README_PROJECT.md             # Project overview
  - METHODOLOGY.md                # Methods section
  - PAPER_METHOD_SUMMARY.md       # Paper-ready sections
  - PACK_V2_METHOD.md             # Pack documentation
  - FREEZE_LITE.md                # Freeze-lite docs
  - DATA_DICTIONARY.md            # Column definitions
  
05_freeze/v1.0.2-lite/            # PUBLISHED freeze-lite bundle
  - figures/                      # All bilingual figures
  - tables/                       # Final analysis tables
  - reports/                      # Reports
  - manifests/                    # Integrity verification

04_outputs/case_cards/            # Case studies
  - case_negative_v2.md
  - case_positive_*.md
  - positive_cases_summary.csv
```

### ✅ Configuration & Build

```
README.md                          # Main repo README
.gitignore                         # (will create)
RELEASE_CHECKLIST.md              # Release instructions
CONFIG_ANALISIS.yml               # Configuration (document in README where to get it)
requirements.txt                  # Python dependencies
Makefile                          # Build targets (if exists)
```

### ✅ Small Metadata CSVs

```
04_outputs/tables/
  - corpus_master_table_v2tokens.csv    # ✅ ~300 KB (keep)
  - emigrant_by_decade_v2tokens.csv      # ✅ ~50 KB (keep)
  - emigrant_by_author_v2tokens.csv      # ✅ ~50 KB (keep)
  - emigrant_by_format_v2tokens.csv      # ✅ ~30 KB (keep)
  - token_mismatch_audit.csv             # ✅ ~20 KB (keep)
```

**Reason**: Corpus metadata and QA results essential for reproducibility

### ✅ TEI Sample (Optional)

```
01_data/tei/sample/                # Small sample for testing
                                   # Full corpus in 01_data/tei/source/
                                   # is too large; documented separately
```

---

## 4. .gitignore Template

Create `.gitignore` in repo root with:

```gitignore
# Virtual Environments
.venv/
venv/
env/
ENV/
*.venv

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/
.pytest_cache/
.coverage

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store
.AppleDouble
__MACOSX/
.Spotlight-V100
.Trashes

# Large Data (regenerable from source)
01_data/kwic_exports/
01_data/text/
04_outputs/tables/*
!04_outputs/tables/corpus_master_table_v2tokens.csv
!04_outputs/tables/emigrant_by_*.csv
!04_outputs/tables/token_mismatch_audit.csv

# Zenodo (deployment artifact, not source)
zenodo/
ZENODO_PACKAGE_SUMMARY.md

# R (if applicable)
.Rhistory
.RData
renv/
renv.lock

# R environment (if applicable)
.Renviron
```

**Notes:**:
- Lines with `!` are **exceptions** (whitelist)
- `.gitignore` prevents large files from being committed
- Small, essential CSVs are explicitly whitelisted

---

## 5. Recommended Directory Structure for GitHub

```
corpus-etnografico-galicia/
├── README.md                           ← Main repo README
├── RELEASE_CHECKLIST.md               ← Release instructions
├── REPO_HYGIENE_REPORT.md             ← This file
├── .gitignore                         ← Git ignore rules
├── requirements.txt                   ← Python dependencies
├── LICENSE                            ← Project license
├── Makefile                           ← Build commands (if exists)
│
├── 00_docs/                           ← Documentation (ALL PUBLIC)
│   ├── README_PROJECT.md
│   ├── METHODOLOGY.md
│   ├── PAPER_METHOD_SUMMARY.md
│   ├── PACK_V2_METHOD.md
│   ├── FREEZE_LITE.md
│   ├── DATA_DICTIONARY.md
│   └── ...
│
├── 02_methods/                        ← All scripts (PUBLIC)
│   ├── patterns/
│   │   └── emigrante_markers.yml      ← Detection lexicon
│   ├── scripts_core/
│   ├── scripts_viz/
│   ├── scripts_metadata/
│   └── ...
│
├── 04_outputs/                        ← Case studies + small metadata
│   ├── case_cards/
│   │   ├── case_negative_v2.md
│   │   ├── case_positive_*.md
│   │   └── positive_cases_summary.csv
│   │
│   └── tables/
│       ├── corpus_master_table_v2tokens.csv  ✅ KEEP
│       ├── emigrant_by_*.csv                 ✅ KEEP
│       └── token_mismatch_audit.csv          ✅ KEEP
│
├── 05_freeze/v1.0.2-lite/            ← Published freeze-lite (PUBLIC)
│   ├── figures/
│   ├── tables/
│   ├── reports/
│   └── manifests/
│
├── 01_data/                           ← Source data (PRIVATE/LOCAL ONLY)
│   ├── tei/
│   │   ├── source/                    → NOT IN GIT (copyright)
│   │   └── sample/                    → Optional small sample
│   └── (other data)
│
└── 99_archive/                        ← Legacy/archive (EXCLUDE)
    └── legacy_dirs/
```

---

## 6. Git Hygiene Checklist

Before first GitHub push:

- [ ] Create `.gitignore` (use template above)
- [ ] Remove `.DS_Store` files: `find . -name ".DS_Store" -delete`
- [ ] Remove `__pycache__`: `find . -type d -name "__pycache__" -exec rm -rf {} +`
- [ ] Move large data to `outputs_local/` or similar (LOCAL ONLY)
- [ ] `git status` shows NO large files, only scripts + docs + small CSVs
- [ ] Check `.git/config` for correct remote URL
- [ ] Verify `zenodo/` is in `.gitignore` before adding

---

## 7. Size Estimates

### GitHub Repo (After Cleanup)

| Item | Size | Status |
|------|------|--------|
| Source Code (scripts) | ~5 MB | ✅ Include |
| Documentation (Markdown) | ~2 MB | ✅ Include |
| Freeze-lite figures | ~30 MB | ✅ Include |
| Freeze-lite tables | ~1 MB | ✅ Include |
| Metadata CSVs | ~500 KB | ✅ Include |
| Case cards | ~50 KB | ✅ Include |
| **Total for GitHub** | **~39 MB** | ✅ GOOD |

### Excluded (Local or Zenodo Only)

| Item | Size | Where |
|------|------|-------|
| Full KWIC exports | 370 MB | Zenodo dataset |
| Large intermediate tables | ~12 MB | Zenodo dataset |
| Full TEI-XML corpus | ~90 MB | GitHub NOT required |
| `.venv/` | ~1 GB | Local only |
| **Total Excluded** | **~1.5 GB** | N/A |

---

## 8. Files Requiring Special Decision

### `CONFIG_ANALISIS.yml`

- **Status**: Configuration file with paths/parameters
- **Recommendation**: 
  - INCLUDE in repo (document in README)
  - OR create `CONFIG_ANALISIS.example.yml` template
  - Document any paths that need local adjustment

### `01_data/tei/source/`

- **Status**: Full TEI-XML corpus (~90 MB)
- **Recommendation**:
  - NOT in GitHub (copyright/size)
  - Link to source in README (e.g., "Download from [source repository]")
  - Include small sample in `01_data/tei/sample/` if helpful

---

## 9. Summary: "What Gets Uploaded to GitHub"

### ✅ YES (Include in GitHub)
- All scripts (`02_methods/`)
- All documentation (`00_docs/`)
- Freeze-lite deliverables (`05_freeze/v1.0.2-lite/`)
- Case studies (`04_outputs/case_cards/`)
- Small metadata tables (`corpus_master_table_v2tokens.csv`, etc.)
- Configuration files (`CONFIG_ANALISIS.yml`)
- License and build files

### ❌ NO (Exclude from GitHub)
- Large intermediate data (`01_data/kwic_exports/*.csv`, `01_data/text/units.csv`)
- Full TEI-XML corpus (`01_data/tei/source/`)
- Virtual environment (`.venv/`)
- Cache files (`__pycache__/`, `.pytest_cache/`)
- System files (`.DS_Store`, `.Spotlight-*`)
- Deployments (`zenodo/`)

### 📦 Separate Deposit (Zenodo)
- Freeze-lite figures and tables (36.5 MB)
- Methodology documentation
- Case studies
- Link from GitHub README to Zenodo DOI

---

## 10. Next Steps

1. **Create `.gitignore`** from template above
2. **Remove system files**: `find . -name ".DS_Store" -delete`
3. **Verify with**: `git status` (should be empty after `.gitignore` creation)
4. **Initialize Git**: `git init` (if not already)
5. **First commit**: `git add . && git commit -m "Initial commit: reproducible workflow + documentation"`
6. **Create GitHub repo**: Use `gh` CLI or GitHub web interface
7. **Push**: `git push -u origin main`
8. **Update README**: Add GitHub URL and Zenodo DOI link

---

**Report Generated**: 2026-03-03  
**Status**: Ready to proceed with GitHub upload

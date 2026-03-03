# Phase 12B Enhancements — PROMPT 1-3 Documentation

**Date:** February 27, 2026  
**Status:** ✅ Completed  
**Goal:** Improve corpus analysis pipeline with enhanced metadata extraction, expanded visualizations, and semantic family composition analysis.

---

## Overview

Phase 12B implements three major improvements to the ethnographic analysis pipeline:

1. **PROMPT 1:** Extract year/decade from TEI headers and propagate to all derived tables
2. **PROMPT 2:** Expand author × decade heatmap to include all relevant authors (not just top 3)
3. **PROMPT 3:** Create semantic family composition analysis for emigrant marker profiles

---

## PROMPT 1: Year/Decade Extraction from TEI

### Objective
Eliminate spurious "unknown_year" entries in decade field by extracting publication year directly from TEI headers, with manual lookup fallback.

### Implementation

**Scripts Created:**
- `02_methods/scripts_metadata/extract_tei_year.py` - Extracts year from TEI with multiple xpath strategies
- `02_methods/scripts_metadata/enrich_metadata_with_tei_year.py` - Merges extracted years with manual lookup and updates master table
- `02_methods/data/year_lookup_manual.csv` - Manual lookup for works without TEI year data

**Extraction Strategy:**
1. `sourceDesc/biblStruct/monogr/imprint/date[@when]` (high confidence)
2. `sourceDesc/bibl/date[@when]` (high confidence)
3. Text parsing within sourceDesc (medium confidence)
4. Manual lookup from bibliographic sources (high confidence)
5. Fallback: leave as `unknown_year` with `year_missing=1` flag

**Results:**
- **Before:** 8 works with `unknown_year` (10%)
- **After:** 6 works with `unknown_year` (7.5%) ✅ Within acceptable threshold (<10%)
- **Year coverage:** 74/80 works (92.5%)
- **QA Report:** `00_docs/YEAR_DECADE_QA_REPORT.md`

**Files Modified:**
- `04_outputs/tables/corpus_master_table_v2tokens.csv` - Updated year/decade columns
- `04_outputs/tables/work_years_from_tei.csv` - New: extracted years from TEI

**Makefile Integration:**
```makefile
make tei-year  # Extract years from TEI + merge with lookup
```

---

## PROMPT 2: Expanded Author × Decade Heatmap

### Objective
Replace restrictive "top 3 authors" heatmap with comprehensive visualization showing all relevant authors based on explicit inclusion criteria.

### Implementation

**Script Created:**
- `02_methods/scripts_core/emigrant_heatmap_author_decade_expanded.py` - Expanded heatmap generator

**Inclusion Criteria (Configurable):**
- `tokens_total_author >= 5,000` AND  
- `n_emigrant_mentions_author >= 5`

**Aggregation Strategy:**
- Included authors: Individual columns in heatmap
- Excluded authors: Aggregated into `otros_autores` column (preserves corpus completeness)

**Results:**
- **Before:** 3 authors shown (opaque filtering)
- **After:** 9 authors included + `otros_autores` ✅
- **Coverage:** All 80 works represented

**Outputs:**
- **Full version:** `fig_emigrant_heatmap_decade_author_full.{png,pdf}` - All included authors
- **Top12 version:** `fig_emigrant_heatmap_decade_author_top12.{png,pdf}` - For legibility
- **Support tables:**
  - `emigrant_rate_decade_author.csv` - Full matrix data
  - `emigrant_rate_decade_author_inclusion.csv` - Inclusion criteria report (documents why each author included/excluded)

**Makefile Integration:**
```makefile
make heatmap-author-decade-expanded  # Generate expanded heatmaps
```

**Interpretation Notes:**
- Heatmap cells = `rate_per_1k_tokens` (emigrant mentions / tokens × 1000)
- Cell values normalized by text volume (avoiding bias toward longer works)
- `otros_autores` shows aggregated behavior of authors below threshold

---

## PROMPT 3: Semantic Family Composition Analysis

### Objective
Analyze HOW emigrant representation manifests through composition of semantic marker families (not just density/frequency).

### Implementation

**Taxonomy Created:**
- `02_methods/patterns/emigrant_marker_families.yml` - 9 semantic families:
  1. **identidad_lengua** - National identity, language, paisanía (37.1% of mentions)
  2. **movilidad_transporte** - Ships, voyages, passages (13.2%)
  3. **destinos_redes** - Destinations, colonies, diaspora networks (11.4%)
  4. **economia_clase** - Poverty/wealth, social mobility (5.7%)
  5. **afectos_nostalgia** - Nostalgia, saudade, exile (7.6%)
  6. **trabajo_explotacion** - Labor, plantations, exploitation (3.5%)
  7. **figura_indiano** - Returned indianos, American wealth (8.0%)
  8. **familia_vinculo** - Family bonds, parents, children (included in taxonomy)
  9. **aldea_territorio** - Home village, land, Galicia (0.9%)

**Script Created:**
- `02_methods/scripts_core/emigrant_profile_composition_analysis.py` - Composition analyzer

**Analysis Process:**
1. Map each `marker_label` from KWIC cases to semantic family (keyword matching)
2. Aggregate by `author × decade × family` → calculate proportions
3. Generate stacked composition visualizations

**Visualizations:**
- **By Decade:** `fig_emigrant_profile_by_decade.{png,pdf}`  
  - Stacked bars showing family proportions over time
  - Reveals temporal shifts in representational focus
  
- **By Author:** `fig_emigrant_profile_by_author.{png,pdf}`  
  - Stacked bars for top 5 authors + `otros_autores`
  - Shows author-specific stylistic/thematic differences

**Key Findings:**
- **Identidad_lengua dominance:** 37.1% of all mentions (identity/belonging central)
- **Transport/mobility:** 13.2% (pragmatic focus on travel logistics)
- **Unmapped ("other"):** 12.6% (markers not fitting taxonomy → needs refinement)
- **Author variation:** Some emphasize economy/class, others affect/nostalgia
- **Temporal shifts detectable** in family proportion changes by decade

**Outputs:**
- **Table:** `emigrant_profile_author_decade_family.csv` - Full composition data (118 rows)
- **Figures:** Stacked composition by decade and author (PNG + PDF)

**Makefile Integration:**
```makefile
make profile-composition  # Generate semantic family analysis
```

**Interpretation Notes:**
- Family assignment via keyword matching (not manual annotation) → some misclassification expected
- "Other" category (12.6%) indicates taxonomy incompleteness → requires iteration
- Proportions show relative emphasis, not absolute importance
- Composition differences reveal **stylistic/thematic variation**, not truth claims about migration

---

## EXTRA: Multilingual Figure Support (Deferred)

### Objective
Generate Spanish (ES) and English (EN) versions of all figures automatically.

### Status
**Framework created** but full implementation deferred:
- `02_methods/scripts_core/multilingual_figures_generator.py` - Wrapper script skeleton
- Requires adding `--lang` parameter to each figure script
- Requires internal translation dictionaries (titles, axes, legends)
- Output: `fig_*_es.{png,pdf}` and `fig_*_en.{png,pdf}` versions

**Rationale for Deferral:**
- Current priority: Complete analysis pipeline
- Multilingual support = presentation layer (can be added later)
- Would require modifying 6+ existing scripts consistently

**Future Implementation Strategy:**
1. Create `02_methods/utils/figure_i18n.py` with translation dictionaries
2. Modify each figure script to accept `--lang` parameter
3. Wrap title/axis/legend strings in translation function
4. Update Makefile to generate both versions by default

---

## Integration & Validation

### Evidence Pack Report Updated

**New Sections Added:**
- **Section 7:** Expanded Author × Decade Heatmap (PROMPT 2)
  - 7.1: Full heatmap (all authors)
  - 7.2: Top 12 version (legibility)
- **Section 8:** Semantic Family Composition (PROMPT 3)
  - 8.1: Composition by decade
  - 8.2: Composition by author
- **Section 9:** Notes & Methodology (updated)

**Total sections:** 9 (up from 6)

### Makefile Pipeline Integration

**Complete dependency chain:**
```makefile
make evidence-pack-emigrante-v2tokens
  ↓ requires:
  - fix-tokens-full (v2tokens denominators)
  - tei-genre (100% genre coverage)
  - tei-year (year/decade extraction)  # NEW
  - temporal-analysis (original heatmaps)
  - heatmap-author-decade-expanded  # NEW
  - emigrant-profiles (marker distribution)
  - profile-composition  # NEW
```

**New targets:**
```bash
make tei-year                      # Extract years from TEI
make heatmap-author-decade-expanded  # Expanded heatmaps
make profile-composition             # Semantic family analysis
```

### Validation Results

**Pipeline test:** `make clean-outputs && make evidence-pack-emigrante-v2tokens`
- ✅ All scripts execute successfully
- ✅ All tables generated (13 new/updated CSV files)
- ✅ All figures generated (9 new PNG/PDF pairs)
- ✅ Evidence pack report updates correctly
- ✅ QA reports generated (genre, year/decade)

**Coverage metrics:**
- Genre coverage: 100% (80/80 works) ✓
- Year/decade coverage: 92.5% (74/80 works) ✓ (within <10% threshold)
- Author inclusion: 9/9 authors with sufficient mentions ✓
- Semantic family mapping: 87.4% (37 families, 12.6% "other")

---

## Documentation Updates

**New/Modified Files:**
- `00_docs/YEAR_DECADE_QA_REPORT.md` - Year/decade coverage QA
- `00_docs/PHASE_12B_ENHANCEMENTS.md` - This document
- `02_methods/patterns/emigrant_marker_families.yml` - Semantic taxonomy
- `02_methods/data/year_lookup_manual.csv` - Manual year lookup
- `Makefile` - New targets and dependencies
- `04_outputs/reports/EVIDENCE_PACK_EMIGRANTE.md` - Sections 7-9 added

**Scripts Created (Total: 5):**
1. `extract_tei_year.py` (165 lines)
2. `enrich_metadata_with_tei_year.py` (178 lines)
3. `emigrant_heatmap_author_decade_expanded.py` (290 lines)
4. `emigrant_profile_composition_analysis.py` (261 lines)
5. `multilingual_figures_generator.py` (62 lines, framework only)

---

## Next Steps (Post Phase 12B)

### Immediate
1. ✅ **COMPLETED:** All PROMPT 1-3 objectives met
2. Review "other" category (12.6%) in family mapping → refine taxonomy
3. Consider adding more families or refining keyword mappings

### Medium-term
1. Implement full multilingual support (ES/EN figures)
2. Add Correspondence Analysis (CA) for family × author/decade visualization
3. Create "small multiples" view (4-6 key authors, evolution over time)

### Long-term
1. Integrate temporal controls into interactive dashboards
2. Export family composition data to R/Tableau for advanced visualization
3. Cross-reference with historical IGE emigration data (contrapunto)

---

## Lessons Learned

### Technical
- **TEI metadata extraction:** `publicationStmt/date` often holds digitalización date, not original publication → use `sourceDesc` preferentially
- **Manual lookup necessity:** Even with TEI, ~7% of works need external bibliographic sourcing
- **Family taxonomies:** Keyword-based mapping effective but imperfect → 12.6% "other" suggests taxonomy gaps
- **Inclusion criteria documentation:** Explicit thresholds (tokens ≥5k, mentions ≥5) prevent opaque filtering

### Methodological
- **Unknown != Missing:** 7.5% `unknown_year` doesn't invalidate temporal analysis (92.5% coverage sufficient)
- **Composition > Density:** Family proportions reveal more about representation style than raw frequencies
- **"Otros" categories essential:** Aggregating excluded items preserves corpus completeness (no silent deletions)
- **QA reports critical:** `YEAR_DECADE_QA_REPORT.md` documents exactly what's missing and why

### Workflow
- **Incremental validation:** Test each script → integrate → full pipeline test (prevented cascading failures)
- **Parallel batching:** Generate multiple figures simultaneously (efficiency)
- **Documentation-first:** Writing this doc forced clarification of design decisions

---

## References

**Related Documentation:**
- `00_docs/DATA_DICTIONARY.md` - Data schema and column definitions
- `00_docs/GENRE_QA_REPORT.md` - Genre extraction QA (100% coverage)
- `04_outputs/reports/EVIDENCE_PACK_EMIGRANTE.md` - Main evidence report

**Key Tables:**
- `corpus_master_table_v2tokens.csv` - Master table (80 works, 21 columns)
- `emigrant_profile_author_decade_family.csv` - Composition analysis (118 rows)
- `emigrant_rate_decade_author.csv` - Expanded heatmap matrix (9 decades × 10 authors)

**Figures Directory:** `04_outputs/figures/static/`
- Heatmaps: `fig_emigrant_heatmap_decade_author_*.{png,pdf}`
- Composition: `fig_emigrant_profile_by_*.{png,pdf}`
- Temporal: `fig_emigrant_temporal_by_genre.{png,pdf}`

---

**End of Phase 12B Documentation**

# Methodology

This project treats literature as a cultural artifact and uses quantitative analysis
as a heuristic for close reading. Outputs do not claim empirical truth about migration;
they map narrative repertoires in the corpus.

## Scenes and markers

- Scene dictionary: 02_methods/patterns/escenas_minimas_v2.yml
- Emigrant markers: 02_methods/patterns/emigrante_markers.yml

Scenes are regex-based patterns. Emigrant markers define KWIC signals for the
emigrant module. Both are auditable and versioned.

## Token normalization

Rates are computed per 1,000 tokens. Canonical token totals are extracted from
TEI fulltext (tei:body) and stored in:

- 04_outputs/tables/work_tokens_full.csv

Derived tables use these fulltext denominators (v2tokens suffix).

## QA audits

### Token QA

- token_mismatch_audit.csv compares snippet token sums vs fulltext totals.
- A mismatch flag (>20%) indicates truncation risk.

### Census QA

- work_tokens_full.csv is deduplicated to avoid double counts
  from overlapping glob patterns (*.xml and *.tei.xml).

## Sampling and packs

Reading packs are stratified across authors and decades. Packs are a reading aid,
not a statistical sample.

### Emigrant Representation Pack v2

A specialized pack of 180 casos from 74 obras (92.5% corpus coverage) designed for
qualitative analysis of emigrant representations. Selection strategy:
- Phase 1: Mandatory 1 caso/obra (coverage)
- Phase 2: Decade-balanced supplementary (temporal distribution)
- Phase 3: 10% negative controls (NOT IMPLEMENTED)

**Documentation:** See [PACK_V2_METHOD.md](PACK_V2_METHOD.md) for detailed selection rules, 
coverage tables, and methodological limitations.

## Bilingual figures (ES/EN)

### Naming convention

All evidence-pack figures are generated in Spanish (ES) and English (EN), with 4 files per basename:
- `{basename}_es.{png,pdf}` (Spanish version)
- `{basename}_en.{png,pdf}` (English version)

Examples:
- `fig_emigrant_by_author_top15_es.png` (Spanish, PNG)
- `fig_emigrant_by_author_top15_en.pdf` (English, PDF)

### Translation approach

**Core evidence figures** (4 basenames): Full i18n implementation with translated:
- Axis labels (e.g., "Obras" → "Works", "Menciones" → "Mentions")
- Titles (e.g., "Distribución por Década" → "Distribution by Decade")
- Genre labels (e.g., "cuento_relato" → "Short Story")

**Heatmaps** (5 basenames): Pragmatic duplication approach:
- Files are duplicated with `_es`/`_en` suffixes
- Rationale: Minimal translatable text (author names, decades don't translate)
- Future: Can be replaced with full i18n if axis labels require translation

### Translation module

Centralized translation support in `02_methods/scripts_core/i18n_figures.py`:
- `TRANSLATIONS` dict: Nested ES/EN translations for common strings
- `t(key, lang='es')`: Get translation for key
- `save_fig(fig, basename, outdir, lang, dpi=300)`: Save with language suffix
- `get_genre_labels(lang='es')`: Return genre mappings for current language
- `validate_bilingual_outputs(basename, outdir)`: Verify all 4 files exist

### QA validation

`make qa-final` runs `qa_bilingual_figures.py` to validate:
1. Bilingual figures: 28 files exist (7 basenames × 4 variants)
2. Metadata quality: 0 unknown_genre, 0 unknown_year, 0 unknown_decade
3. Heatmap basic: `fig_emigrant_heatmap_decade_author.{png,pdf}` exists (alias of top12)

Exit code 0 = all pass, 1 = fail (pipeline aborts).


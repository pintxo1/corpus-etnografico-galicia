# Changelog

## v1.0.2 - 2026-02-26

- **Multilingual Figures**: All evidence-pack figures now available in ES/EN (4 files per figure: _{es,en}.{png,pdf}).
- **Heatmap Fix**: Eliminated legacy 3-author heatmap; `fig_emigrant_heatmap_decade_author` is now an alias of top12 version (9+ authors).
- **Metadata Quality**: 100% coverage of genre/year/decade (0 unknowns) via external corpus enrichment (`metadata-external` target).
- **Translation Infrastructure**: New `i18n_figures.py` module for centralized ES/EN translation support.
- **QA Validation**: Added `qa-final` target to validate bilingual figures (28 files), metadata quality, and heatmap existence.
- **Bilingual Heatmaps**: 5 heatmaps duplicated with `_es`/`_en` suffixes (pragmatic solution for minimal translatable text).

- Token QA: fulltext TEI tokens used as canonical denominators (v2tokens).
- work_tokens_full.csv deduplicated to avoid double counting .tei.xml.
- Token mismatch audit added (token_mismatch_audit.csv).
- Freeze-lite packaging added for paper-ready artifacts.

## v1.0.0 - 2026-02-25

- Baseline corpus pipeline and emigrant module.
- Evidence pack generated (tables, figures, report, reading pack).
- Castelao normalized as canonical author.

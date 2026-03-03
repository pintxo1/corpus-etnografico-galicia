# Data Dictionary (final CSVs)

## corpus_master_table_v2tokens.csv

- obra_id: canonical work identifier
- title: work title
- author_normalized: canonical author name
- year: publication year (if known)
- decade: decade bucket
- genre_norm: normalized genre (cuento_relato, novela, poesia_poemario, teatro, ensayo_cronica, otro, unknown)
- genre_raw: raw genre value from TEI `<classCode scheme="genero">`
- genre_confidence: extraction confidence (high, medium, low, error)
- format: format for grouping (derived from genre_norm or override)
- tokens_total_old: snippet token count (legacy)
- tokens_total_full: TEI fulltext tokens
- tokens_total: canonical tokens used for rates
- n_emigrant_mentions: total emigrant marker hits
- emigrant_rate_per_1k_tokens: normalized rate
- genre_missing_flag: 1 if genre_norm=unknown
- token_mismatch_flag: 1 if mismatch_pct > 0.20

## corpus_master_table_v2tokens_meta.csv

Meta-fixed version of the master table (override applied).

- year_source: source of year (tei, override, inferred)
- genre_source: source of genre (tei, override, inferred)
- year_estimated: 1 if year is estimated in override
- format: normalized format for figures and tables
- year_missing: 1 if year is missing
- format_missing: 1 if format is missing or unknown

## emigrant_by_author_v2tokens.csv

- author_normalized
- n_obras
- tokens_total
- n_emigrant_mentions
- emigrant_rate_per_1k_tokens

## emigrant_by_decade_v2tokens.csv

- decade
- n_obras
- tokens_total
- n_emigrant_mentions
- emigrant_rate_per_1k_tokens

## emigrant_by_format_v2tokens.csv

- format: normalized format (genre_norm or override-derived)
- n_obras
- tokens_total
- n_emigrant_mentions
- emigrant_rate_per_1k_tokens

## work_genre_from_tei.csv (Phase 12B: Genre Extraction)

- obra_id: canonical work identifier
- genre_raw: raw genre value from TEI header (e.g., "teatro", "novela")
- genre_norm: normalized genre (cuento_relato, novela, poesia_poemario, teatro, ensayo_cronica, otro, unknown)
- genre_confidence: extraction confidence (high=from `<classCode>`, medium=from `<keywords>`, low=fallback)
- genre_source_xpath: XPath location where genre was extracted (for transparency)
- genre_missing_flag: 1 if genre_norm=unknown, 0 otherwise

## work_tokens_full.csv

- obra_id
- tokens_total_full
- chars_total_full
- tokens_source

## token_mismatch_audit.csv

- obra_id
- tokens_snippet
- tokens_full
- mismatch_abs
- mismatch_pct
- n_units
- avg_unit_chars
- flag_20pct
- flag_10pct

## emigrant_decade_author_matrix.csv (PROMPT 2: Temporal Analysis)

- rows: decades (1860s-1950s, chronological order)
- columns: authors (with ≥3 works)
- values: emigrant_rate_per_1k_tokens (weighted average for decade × author cell)
- NA: author did not publish in that decade
- Purpose: Heatmap visualization of temporal composition

## author_scene_matrix_rates.csv (if generated)

- rows: authors
- columns: escena_tipo
- values: rate_per_1k_tokens

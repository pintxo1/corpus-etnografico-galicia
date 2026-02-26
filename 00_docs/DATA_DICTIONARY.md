# Data Dictionary (final CSVs)

## corpus_master_table_v2tokens.csv

- obra_id: canonical work identifier
- title: work title
- author_normalized: canonical author name
- year: publication year (if known)
- decade: decade bucket
- tokens_total_old: snippet token count (legacy)
- tokens_total_full: TEI fulltext tokens
- tokens_total: canonical tokens used for rates
- n_emigrant_mentions: total emigrant marker hits
- emigrant_rate_per_1k_tokens: normalized rate
- token_mismatch_flag: 1 if mismatch_pct > 0.20

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

- format
- n_obras
- tokens_total
- n_emigrant_mentions
- emigrant_rate_per_1k_tokens

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

## author_scene_matrix_rates.csv (if generated)

- rows: authors
- columns: escena_tipo
- values: rate_per_1k_tokens

# METADATA_EXTERNAL_QA Report

Generated: 2026-02-27T10:17:19.442672

## Executive Summary

- Total works: 80
- Matched with external corpus: 80 (100.0%)
- Year coverage: 100.0% (0 unknown)
- Genre coverage: 100.0% (0 unknown)
- Decade coverage: 100.0% (0 unknown)

## Validation Status

✅ Matching 80/80: PASS
✅ Unknown genre ≤ 2: PASS (0 unknown)
✅ Unknown year ≤ 2: PASS (0 unknown)

## Methodology


- **ID Matching**: Normalized both obra_id (master) and doc_id (external) using:
  1. Remove extensions (.tei, .xml, etc.)
  2. Unicode NFKD normalization + diacritic removal
  3. Lowercase + non-alphanumeric → underscore
  4. Strip known suffixes (_tei_v2, _tei, _001, etc.)
- **Year Enrichment**: Filled NaN/unknown_year with year_first_pub from external corpus
- **Genre Enrichment**: Filled unknown with genre_macro_normalizado from external corpus  
- **Decade Enrichment**: Computed from year where available, or filled from external decade column
- **Trazability**: Flags added (year_source, genre_source, decade_source) to track enrichment provenance
- **Data Integrity**: TEI XML headers never modified; enrichment is overlay only (reversible)

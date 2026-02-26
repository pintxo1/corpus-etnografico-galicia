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

## Reproducibility

All scripts used by Makefile are in 02_methods/ and can regenerate outputs from TEI.
Freeze-lite packages only final artifacts with SHA256 manifests.

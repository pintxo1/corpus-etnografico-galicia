# EVIDENCE_PACK_EMIGRANTE

**Generated:** 2026-02-27 10:17:34
**Denominators:** tokens_full (TEI fulltext, v2tokens)

---

## 1. Corpus summary

- Works: 80
- Tokens (fulltext): 1,018,420
- Emigrant mentions: 2,101

## 2. Emigrant by author (top 5)

| Author | Works | Tokens | Mentions | Rate/1k |
|---|---:|---:|---:|---:|
| Antonio, Manuel | 1 | 5,176 | 36 | 6.96 |
| Castelao, Alfonso Rodríguez | 5 | 213,524 | 897 | 4.20 |
| Curros Enríquez, Manuel | 1 | 33,832 | 82 | 2.42 |
| Rodríguez López, Xesús | 1 | 56,526 | 99 | 1.75 |
| Castro, Rosalía de | 2 | 60,653 | 97 | 1.60 |

## 3. Emigrant by decade

| Decade | Works | Tokens | Mentions | Rate/1k |
|---|---:|---:|---:|---:|
| 1860s | 1 | 32,372 | 40 | 1.24 |
| 1880s | 7 | 453,323 | 591 | 1.30 |
| 1890s | 32 | 80,736 | 223 | 2.76 |
| 1900s | 17 | 47,308 | 96 | 2.03 |
| 1910s | 8 | 25,262 | 26 | 1.03 |
| 1920s | 7 | 21,012 | 33 | 1.57 |
| 1930s | 2 | 26,194 | 78 | 2.98 |
| 1940s | 5 | 323,588 | 1,007 | 3.11 |
| 1950s | 1 | 8,625 | 7 | 0.81 |

## 4. Emigrant by format

| Format | Works | Tokens | Mentions | Rate/1k |
|---|---:|---:|---:|---:|
| ensayo_cronica | 3 | 232,292 | 918 | 3.95 |
| teatro | 3 | 2,031 | 6 | 2.95 |
| cuento_relato | 61 | 152,672 | 417 | 2.73 |
| poesia_poemario | 6 | 131,942 | 279 | 2.11 |
| novela | 7 | 499,483 | 481 | 0.96 |

## 5. Temporal Composition Analysis (PROMPT 2)

### 5.1. Decade × Author Heatmap

Heatmap showing emigrant representation rates (per 1k tokens) by decade and author:

![Decade × Author Heatmap](../figures/static/fig_emigrant_heatmap_decade_author.png)

**Key observations:**
- Temporal distribution of emigrant representation across authors
- Variation in rates by decade for each major author
- Authors with ≥3 works included

### 5.2. Temporal Evolution by Genre

Evolution of emigrant representation and literary production by genre:

![Temporal by Genre](../figures/static/fig_emigrant_temporal_by_genre.png)

**Key observations:**
- Upper panel: emigrant rate per 1k tokens by genre over time
- Lower panel: number of works published by genre per decade
- Genres with ≥5 total works included

### 5.3. Production Timeline

Corpus production timeline showing works, authors, and emigrant representation:

![Production Timeline](../figures/static/fig_production_timeline.png)

**Key observations:**
- Number of works per decade
- Number of active authors per decade
- Emigrant representation rate per decade

## 6. Emigrant Profile Analysis (PROMPT 3)

### 6.1. Marker Distribution by Author

Distribution of top emigrant markers across top 5 authors:

![Markers by Author](../figures/static/fig_emigrant_markers_profile_by_author.png)

**Key observations:**
- Top 15 emigrant markers (semantic labels) by frequency
- Variation in marker usage across authors
- Authors with highest number of emigrant mentions included

### 6.2. Marker Distribution by Genre

Distribution of emigrant markers across literary genres:

![Markers by Genre](../figures/static/fig_emigrant_markers_profile_by_genre.png)

**Key observations:**
- Top 15 emigrant markers by genre
- Genre-specific patterns in emigrant representation
- Genres with ≥5 works included

### 6.3. Mediation Scenes

Mediation scenes = text units with ≥3 emigrant mentions (high density contexts):

![Mediation Density](../figures/static/fig_emigrant_mediation_density.png)

**Key statistics:**
- Total mediation scenes identified: 72
- Total emigrant mentions: 2,101
- Mediation scene rate: 0.90 scenes/work

**Top authors by mediation scenes:**
- Pardo Bazán, Emilia: 43 scenes
- Curros Enríquez, Manuel: 11 scenes
- Castelao, Alfonso Rodríguez: 9 scenes
- Castro, Rosalía de: 2 scenes
- Dieste, Rafael: 2 scenes

## 7. Expanded Author × Decade Heatmap (PROMPT 2)

### 7.1. Full Heatmap (All Relevant Authors)

Expanded heatmap with all authors meeting inclusion criteria (tokens ≥5k, mentions ≥5):

![Heatmap Full](../figures/static/fig_emigrant_heatmap_decade_author_full.png)

**Key observations:**
- All relevant authors included (not just top 3)
- 'otros_autores' category aggregates excluded authors
- Clear patterns of temporal concentration per author

### 7.2. Top 12 Authors (Legibility)

Focused version with top 12 authors for enhanced legibility:

![Heatmap Top12](../figures/static/fig_emigrant_heatmap_decade_author_top12.png)

## 8. Semantic Family Composition (PROMPT 3)

### 8.1. Composition by Decade

Stacked composition of emigrant marker families over time:

![Profile by Decade](../figures/static/fig_emigrant_profile_by_decade.png)

**Key observations:**
- 9 semantic families identified (identity, mobility, destinations, economy, etc.)
- Temporal shifts in family prominence
- 'Identidad_lengua' consistently dominant (~37% of mentions)

### 8.2. Composition by Author

Author-specific semantic profiles (top 5 authors + others):

![Profile by Author](../figures/static/fig_emigrant_profile_by_author.png)

**Key observations:**
- Author-specific variation in family usage
- Some authors emphasize economy/class, others nostalgia/affect
- Composition analysis reveals stylistic/thematic differences

## 9. Notes & Methodology

- Rates are normalized per 1,000 fulltext tokens (TEI body extraction).
- This report is consistent with v2tokens denominators.
- Temporal analysis includes only works with known publication decade (74/80 works, 7.5% unknown).
- Marker labels represent semantic categories of emigrant markers.
- Mediation scenes identify text units with high emigrant mention density (≥3 mentions).
- Semantic families mapped from emigrant_marker_families.yml taxonomy.
- Inclusion criteria for expanded heatmap: tokens ≥5k AND mentions ≥5.

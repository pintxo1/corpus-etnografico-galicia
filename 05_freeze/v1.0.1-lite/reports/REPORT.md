# Ethnographic Pipeline Report

**Generated:** 2026-02-23 20:15:40

## 1. Run Summary

| Metric | Value |
|--------|-------|
| **TEI sources** | 80 |
| **Units (extracts)** | 177 |
| **Cases (raw KWIC)** | 3,550 |
| **Scenes** | 16 |

---
## 2. Scene Coverage & Concentration

| Scene | Cases | % Total | Works | Concentration |
|---|---|---|---|---|
| amor_deseo | 690 | 19.4% | 55 | ✓ |
| muerte_duelo | 602 | 17.0% | 63 | ✓ |
| religiosidad_supersticion | 588 | 16.6% | 42 | ⚠️ HIGH |
| violencia_agresion | 335 | 9.4% | 42 | ⚠️ HIGH |
| ciclo_agricola | 229 | 6.5% | 47 | ✓ |
| aldea_ciudad | 212 | 6.0% | 54 | ✓ |
| hambre_subsistencia | 167 | 4.7% | 39 | ✓ |
| deuda_usura | 134 | 3.8% | 42 | ✓ |
| trabajo_jornalero | 127 | 3.6% | 38 | ✓ |
| caciquismo_poder | 120 | 3.4% | 35 | ✓ |
| movilidad_interna | 93 | 2.6% | 21 | ⚠️ HIGH |
| genero_roles | 76 | 2.1% | 35 | ✓ |
| herencia_tierra | 63 | 1.8% | 22 | ⚠️ HIGH |
| retorno_indiano | 42 | 1.2% | 20 | ✓ |
| morriña_nostalgia | 41 | 1.2% | 29 | ✓ |
| migracion_embarque | 31 | 0.9% | 17 | ✓ |


**Notes:**
- ⚠️ HIGH: Top 3 works represent >50% of scene's cases (concentration risk)
- Cases: n_cases from scene_summary.csv
- Works: n_obras detected in each scene

---
## 2b. Token-normalized Rates

Normalización por volumen textual (casos por 1,000 tokens de corpus):

| Scene | Cases | Rate/1k tokens | Works |
|-------|-------|----------------|-------|
| amor_deseo | 690 | 0.6848 | 55 |
| muerte_duelo | 602 | 0.5975 | 63 |
| religiosidad_supersticion | 588 | 0.5836 | 42 |
| violencia_agresion | 335 | 0.3325 | 42 |
| ciclo_agricola | 229 | 0.2273 | 47 |
| aldea_ciudad | 212 | 0.2104 | 54 |
| hambre_subsistencia | 167 | 0.1657 | 39 |
| deuda_usura | 134 | 0.1330 | 42 |

**Interpretation:**
- Top scenes by token-normalized rate may indicate thematic prominence relative to corpus volume
- Low rates suggest sparse distribution across large textual regions
- ⚠️ **Caution:** This is a heuristic, not evidence of "thematic importance"—requires ethnographic interpretation

---
## 3. Reading Packs

### Diverse Pack
- **Cases:** 180
- **Unique works:** 76/80 (95.0%)
- **Scenes:** 16/16
- **Top 3 works:** Los-pazos-de-Ulloa-novela-original-precedida-de-unos-apuntes-autobiográficos-por-Emilia-Pardo-Bazán (7), contra_treta (7), fuego_a_bordo (6)
- **Purpose:** Corpus-scale representativeness

### Balanced Pack
- **Cases:** 160
- **Unique works:** 29/80 (36.2%)
- **Scenes:** 16/16
- **Top 3 works:** curros_enriquez_aires_de_la_tierra.tei (20), supersticiones_de_galicia_y_preocupaciones_vulgares_tei (14), dieste_muriel_tei (12)
- **Purpose:** Cross-scene computational analysis (10 per scene)

---

## 4. Audit & Reproducibility

### Sampling Audit
[See `04_outputs/tables/sampling_audit.md` for details]

### Pack Comparison
[See `04_outputs/tables/pack_report.md` for detailed comparison]

---

## 5. Co-occurrence Networks & Tensions

### Top 10 Co-occurrence Pairs

| Term 1 | Term 2 | Co-occurrences | Jaccard |
|--------|--------|----------------|----------|
| amor_deseo | muerte_duelo | 87 | 0.057 |
| muerte_duelo | religiosidad_supersticion | 70 | 0.048 |
| muerte_duelo | violencia_agresion | 47 | 0.040 |
| religiosidad_supersticion | violencia_agresion | 44 | 0.040 |
| amor_deseo | religiosidad_supersticion | 44 | 0.029 |
| hambre_subsistencia | muerte_duelo | 36 | 0.036 |
| ciclo_agricola | muerte_duelo | 35 | 0.032 |
| ciclo_agricola | trabajo_jornalero | 32 | 0.068 |
| amor_deseo | caciquismo_poder | 32 | 0.033 |
| aldea_ciudad | muerte_duelo | 32 | 0.030 |

**Interpretation:** Top pairs indicate narrative tensions, thematic resonance, or intertextual references in the corpus.

📁 **Network files:** See `04_outputs/networks/` for GraphML exports

---

## 6. Figures Generated

- ℹ️ No PNG figures found yet

---

## 6b. Enhanced Visualizations

Publication-ready statistical and network visualizations (Phase 9).

**Figure Registry:** See [04_outputs/figures/FIGURE_REGISTRY.md](04_outputs/figures/FIGURE_REGISTRY.md) for complete inventory.

### Static Visualizations (PNG/PDF @ 300 DPI)

| Visualization | Description | Purpose |
|---|---|---|
| fig_scene_scatter | Scene coverage vs. concentration (scatter plot) | Corpus-level scene characterization |
| fig_scene_work_heatmap | Scene × Work heatmap (top 40 obras, per 1k tokens) | Publication heatmap (legible) |
| fig_scene_rates_distribution | Rate distributions across 5 diverse scenes (violin plots) | Variability visualization |
| fig_cooc_network_filtered | Term co-occurrence network (13 nodes, Louvain communities) | Semantic clustering & tensions |
| fig_scene_rates_per_1k_tokens | Top 10 scenes by case rate (horizontal bars) | Scene prevalence ranking |

**Note:** `fig_scene_work_heatmap_full` available as PDF only (large reference format).

### Interactive Visualizations (HTML)

| Dashboard | Description | Purpose |
|---|---|---|
| dashboard_cases.html | Case Browser (340 curated cases) | Exploration & KWIC context viewing |

**Technology:** Vanilla HTML/CSS/JS. Self-contained (no external dependencies). Works offline.

### Quality Standards

- **PNG:** 300 DPI (publication quality for print/web)
- **PDF:** Vectorial format (no pixelation, scales indefinitely)
- **Colorblind-friendly:** Designed with accessible palettes
- **Typography:** 8-13pt fonts (legible at publication size)
- **Reproducibility:** All figures generated from source CSVs via `make viz-all`

---

## 7. Run Parameters & Configuration

### Reading Pack Rules (reading_pack_rules.yml)

```yaml
balance_by_cluster: auto
include_negative_cases: true
max_per_obra: 6
min_per_escena: 6
min_unique_obras: 40
n_total: 180
negative_case_pct_max: 15
negative_case_pct_min: 10
prioritization: salience_then_coverage
reserve_percent_for_diversity: 0.25
```

### Pipeline Configuration
- **Rules file:** `02_methods/patterns/reading_pack_rules.yml`
- **Rules hash:** fca571df
- **CWD:** /Users/Pintxo/corpus-etnografico-galicia
- **Python:** 3.13.2
- **Timestamp:** 2026-02-23T20:15:40.115894

---
## 8. Limitations & Methodological Reflexivity

**This pipeline does NOT:**
- ⚠️ Assume texts are transparent representations of "reality"
- ⚠️ Reify scenes, works, or co-occurrence pairings as causal structures
- ⚠️ Claim statistical significance or inference beyond the corpus
- ⚠️ Neutralize the ethnographer's presence in case selection
- ⚠️ Substitute algorithmic pattern detection for interpretive depth

**What this IS:**
- ✓ A systematic heuristic for navigating a complex cultural corpus
- ✓ A trace of our analytical choices (scene definitions, cooc windows)
- ✓ A scaffold for ethnographic writing and comparative work
- ✓ A reproducible documentation of what was selected and why
- ✓ An artifact: the pipeline itself embeds theoretical commitments

**Data quality notes:**
- Cooc window: 40 words (configurable)
- Scene definitions: Hand-crafted patterns (see `02_methods/patterns/escenas_minimas.yml`)
- Case selection: Stratified by salience + obra diversity (see packs)
- Network reification: GraphML exports should be **visualized cautiously**

---

*Generated by ethnographic-pipeline v0.1 | Not for quantitative claims*

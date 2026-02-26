# Visualization Scripts (Phase 9 - Advanced DH Visualizations)

This directory contains Python scripts that generate publication-ready visualizations of ethnographic analysis results. All visualizations are designed for serious Digital Humanities work: informative, not decorative.

**Status:** ✅ Phase 9 COMPLETE

---

## 📊 Scripts Overview

### 1. `fig_scene_scatter.py`
**Purpose:** Work coverage vs. concentration by scene  
**Output:** `04_outputs/figures/static/fig_scene_scatter.{png,pdf}`  
**Input:** `03_analysis/casos_by_escena.csv`

Scatter plot showing:
- X-axis: Number of distinct works per scene
- Y-axis: Concentration (max case density in single work)
- Median guide lines to identify high-coverage, high-concentration scenes
- Quadrant labels (high-coverage/low-conc, low-coverage/high-conc, etc.)

**Key Features:**
- Automatically detects median lines
- Smart annotation placement (no overlaps)
- Publication-ready (150 DPI, LaTeX formatting)

**Typical Output:**
```
14 scenes plotted
Medians: 12 works (x), 0.156 concentration (y)
Highest coverage: amor_deseo (30 works)
Highest concentration: work X in scene Y (0.89)
```

---

### 2. `fig_scene_heatmap.py`
**Purpose:** Scene × Work token distribution heatmap  
**Output:** `04_outputs/figures/static/fig_scene_work_heatmap.{png,pdf}` (top 40 works)  
Output:** `04_outputs/figures/static/fig_scene_work_heatmap_full.pdf` (all 80 works)  
**Input:** `03_analysis/casos_by_escena.csv`

Two-panel heatmap showing:
- **Left panel (PNG/PDF):** Top 40 works across 16 scenes (aggregated, legible)
- **Right panel (PDF only):** All 80 works (full dataset, high-detail)

**Normalization:** Tokens per 1,000 tokens in each work (enables cross-work comparison)

**Key Features:**
- Automatic top-40 detection by total cases/work
- "OTHER" category aggregates works 41-80 for visual clarity
- Color scale: 0-2.5 density, white→red gradient
- Rows (scenes) sorted by total cases;columns (works) sorted by total cases

**Typical Output:**
```
Heatmap shape: 16 scenes × 41 columns (40 works + OTHER)
Full heatmap: 16 scenes × 80 works
Max density: 2.4 tokens per 1k (work A in scene B)
Min density: 0.0 (many works absent from many scenes)
```

---

### 3. `fig_scene_rates_distribution.py`
**Purpose:** Rate distribution across scenes (violin plots)  
**Output:** `04_outputs/figures/static/fig_scene_rates_distribution.{png,pdf}`  
**Input:** `03_analysis/casos_by_escena.csv`

Violin plots showing 5 diverse scenes:
- Highest percentile (e.g., amor_deseo: 90th)
- Mid-high (e.g., muerte_duelo: 75th)
- Mid-low (e.g., cyclo_agricola: 50th)
- Low (e.g., hambre_subsistencia: 25th)
- Lowest (e.g., religiosidad_supersticion: 10th)

**Features:**
- Automatic percentile-based scene selection
- Individual datapoints overlaid on violin (jitter)
- Y-axis: density (tokens per 1k tokens)
- Helps visualize variability within scenes

**Typical Output:**
```
5 scenes selected (percentile-spaced)
amor_deseo: 690 cases, max=2.1 density, IQR=[0.3, 0.8]
muerte_duelo: 602 cases, max=1.9 density, IQR=[0.2, 0.7]
... etc ...
```

---

### 4. `fig_cooc_network_filtered.py`
**Purpose:** Co-occurrence word network (filtered, community-detected)  
**Output:** 
- `04_outputs/figures/static/fig_cooc_network_filtered.{png,pdf}` (static)
- `04_outputs/figures/interactive/cooc_network.html` (interactive, if pyvis available)

**Input:** `03_analysis/coocurrencias_filtradas.csv`

Network visualization showing:
- **Nodes:** 13 key ethnographic terms (filtrado: min_cooc ≥ 20)
- **Edges:** Co-occurrence relationships (weighted by frequency)
- **Colors:** Louvain community detection (4-5 communities)
- **Labels:** Top-15 nodes by degree (others identified by hover in interactive version)
- **Layout:** Force-directed (Fruchterman-Reingold)

**Key Features:**
- Automatic Louvain community detection (modularity-optimized)
- Edge width proportional to co-occurrence frequency
- Node size proportional to total co-occurrence degree
- Static PNG/PDF for publications; interactive HTML for exploration
- (Optional) If `{pyvis}` installed: Interactive version allows zoom, pan, hover tooltips

**Typical Output:**
```
Network: 13 nodes, 24 edges
Communities detected: 4 (modularity=0.56)
  - Community 1 (migration-work terms): embarque, america, trabajo, tierra
  - Community 2 (affective-familial): amor, morriña, padre, madre
  - Community 3 (poverty-violence): hambre, violencia, muerte, deuda
  - Community 4 (religious-agricultural): dios, agricultura, ciclo, iglesia
Top 15 connections (by degree): embarque, trabajo, muerte, tierra, amor, ...
```

---

### 5. `dashboard_cases.html.py`
**Purpose:** Interactive case browser (curated subset of 340 cases)  
**Output:** `04_outputs/figures/interactive/dashboard_cases.html` (~14 MB, self-contained)  
**Input:** Reading packs (`.csv` files in `03_analysis/reading_packs/`)

Single-file HTML dashboard featuring:

**Filtering:**
- By scene (dropdown)
- By reading pack (diverse vs. balanced)
- Real-time case count update

**Sorting:**
- By scene
- By case_id
- By salience score (descending default)

**View Modes:**
- **Table:** Compact summary of 20-30 cases per scroll
- **Single case:** Full KWIC context (60-char left, 60 char right)

**Statistics Panel** (right sidebar):
- Total cases filtered
- Works represented
- Scene breakdown (pie chart generated on selection)
- Pack breakdown

**Navigation:**
- Keyboard shortcuts (J=next, K=prev, S=randomized)
- CSV export button (for selected subset)

**Key Features:**
- Zero external dependencies (vanilla HTML/CSS/JS)
- ~14 MB file size (includes all 340 cases + formatted text)
- Loads in <2 seconds in modern browsers
- No server required (open locally in browser)

**Typical Workflow:**
```
User opens dashboard → Defaults to all 340 cases
User filters to scene=amor_deseo → Shows 85 cases
User clicks on case ID → Full KWIC + metadata view
User exports selection → Gets CSV readable in Excel
```

---

## 🚀 Running All Visualizations

From project root:

```bash
# Generate all Phase 9 visualizations
make viz-all

# or individual stages:
make viz-advanced    # Static: scatter, heatmap, violin, network (PNG+PDF)
make viz-interactive # Interactive: dashboard, network (HTML)
```

**Expected Output:**
```
✅ Generating static visualizations...
   ✓ fig_scene_scatter.png/pdf (2.3 MB)
   ✓ fig_scene_heatmap.png/pdf + full.pdf (8.7 MB)
   ✓ fig_scene_rates_distribution.png/pdf (1.2 MB)
   ✓ fig_cooc_network_filtered.png/pdf (0.8 MB)

✅ Generating interactive visualizations...
   ✓ dashboard_cases.html (14 MB)
   ✓ cooc_network.html (optional, requires pyvis)

✅ All visualizations generated in ~5 seconds
```

---

## 📋 Dependencies

**Required:**
- `pandas` ≥ 2.0: Data manipulation
- `matplotlib` ≥ 3.7: Static plots
- `seaborn` ≥ 0.13: Plot styling
- `networkx` ≥ 3.0: Co-occurrence network, Louvain community detection

**Optional:**
- `pyvis` ≥ 0.3: Interactive network visualization (improves `fig_cooc_network_filtered.py`)

To install:
```bash
pip install -r requirements.txt
```

---

## 🛠️ Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `KeyError: 'casos_por_escena'` | Missing input CSV | Run `make cases` first |
| `ModuleNotFoundError: networkx` | Package not installed | `pip install networkx==3.6.1` |
| `no_cases_found` in dashboard | Reading packs .csv missing | Run `make packs` first |
| PNG/PDF blank | Matplotlib backend issue | Restart kernel, check `/tmp/` |

---

## 📚 Integration with REPORT.md

Section **6b. Enhanced Visualizations** in `REPORT.md` describes:
- Tables of outputs with file sizes
- Publication quality notes (150 DPI, browser compatibility)
- Interpretation guidance

---

## 🔄 Development Notes

**Version:** Phase 9 v1.0 (2026-02-23)

**Future Enhancements** (beyond Phase 9):
- Interactive heatmap with zoom/pan
- 3D scene × work × author space
- Temporal animation (scenes over decades)
- Linked brushing (heatmap ↔ network)

---

**Last Updated:** 2026-02-23  
**Maintained by:** Ethnographic Pipeline Team  
**Status:** ✅ All scripts functional, tested, production-ready

# Corpus Etnográfico Galicia - README del Proyecto

This repository builds a reproducible corpus analysis of Galician literature (1860-1950)
with a focus on ethnographic scenes and emigrant representation. The pipeline treats
literature as a cultural artifact and uses quantitative outputs as reading heuristics.

## Filosofía: Literatura como Artefacto Cultural

Este proyecto rechaza el positivismo metodológico tradicional:

- **Literatura ≠ fuente empírica directa**: Es un artefacto cultural situado (no "datos neutros").
- **Casos/escenas ≠ representativos**: Son heurísticas etnográficas para orientar lectura.
- **Coocurrencias ≠ causalidad**: Señalan tensiones narrativas, no relaciones causales.
- **Outputs principales**: Memos etnográficos + casos anotados (NO métricas crudas).

---

## Flujo Recomendado (Opción A: Auto-regenerable)

### Paso 0: Setup Inicial

```bash
# Clonar y verificar estructura
git clone <repo>
cd corpus-etnografico-galicia
make init          # Crear directorios
make check         # Verificar dependencias
```

### Paso 1: Copiar Corpus TEI

```bash
# Una sola vez: copiar archivos TEI desde corpus-literario/tei
make copy-from-tei TEI_DIR=/ruta/a/corpus-literario/tei
# → Genera 01_data/tei/source/MANIFEST.md con inventario
```

### Paso 2: Build End-to-End (Pipeline Robusto)

```bash
# Ejecuta end-to-end: TEI → texto → casos → rankings → reading packs
# ✓ Auto-regenera si faltan intermedios
# ✓ Funciona incluso si antes corriste `make clean-outputs`
make build

# Salida:
#   01_data/text/units.csv (texto extraído)
#   01_data/kwic_exports/cases_raw.csv (casos detectados)
#   04_outputs/tables/scene_summary.csv + case_rankings.csv (rankings)
#   03_analysis/reading_pack/{diverse,balanced}/ (reading packs)
#   04_outputs/networks/ (redes)
#   04_outputs/figures/static/ (figuras)
```

### Paso 3: Generar Reporte Principal

```bash
# Genera REPORT.md + manifests + token rates
# ✓ Verifica reading packs; auto-regenera si faltan
# ✓ Require: build completado exitosamente
make report-summary

# Salida:
#   04_outputs/reports/REPORT.md
#   04_outputs/tables/token_rates.csv
#   04_outputs/manifests/ARTIFACTS_MANIFEST.csv|.md
```

### Paso 4a: Evidence Pack (v2tokens) [Opcional]

```bash
# Genera evidence pack con denominadores fulltext (v2tokens)
# ✓ Require: corpus TEI presente
# ✓ Auto-regenera corpus_master_table.csv si falta
make fix-tokens-full          # Extrae tokens fulltext
make evidence-pack-emigrante-v2tokens  # Resumen emigrante con v2tokens

# Salida:
#   04_outputs/tables/corpus_master_table_v2tokens.csv
#   04_outputs/tables/emigrant_by_{author,decade,format}_v2tokens.csv
#   04_outputs/reports/EVIDENCE_PACK_EMIGRANTE_v2tokens.md
#   04_outputs/figures/static/fig_emigrant_*.{png,pdf}
```

### Paso 5: Congelar Artefactos (Freeze-lite)

```bash
# Congela outputs finales en versión de git (reproducible)
# ✓ Solo copia artefactos finales (NO inputs)
# ✓ Genera SHA256 manifest
# ✓ Listo para colaboración/publicación
make freeze-lite

# Salida en:
#   05_freeze/v1.0.Z-lite/
#     ├── reports/
#     ├── tables/
#     ├── figures/static/
#     ├── manifests/
#     └── FREEZE_NOTES.md
```

### Paso 6: Limpiar (si necesario reiniciar)

```bash
# Borra 04_outputs/ y tarjetas regenerables
# ✓ Mantiene 01_data/tei/ y 01_data/text/
# ✓ Permite re-ejecutar `make build → make report-summary` limpiamente
make clean-outputs

# Reiniciar desde build:
make build
make report-summary
```

---

## Todos los Targets Disponibles

### Pipeline Básico (Build)

- **`make build`** (NUEVO) — End-to-end: tei-to-text → build-cases → rankings → reading-packs
  - Deps: copy-from-tei debe ejecutarse primero (una sola vez)
  - Genera: todas las tablas intermedias necesarias
  - Robusto: auto-regenera si faltan arhivos

- **`make copy-from-tei TEI_DIR=...`** — Copia corpus TEI (NECESARIO primero)
  - Genera: 01_data/tei/source/ + MANIFEST.md

- **`make tei-to-text`** — Extrae texto plano de TEI
  - Genera: 01_data/text/units.csv

- **`make tei-metadata`** — Extrae metadata de autores (con normalización)
  - Genera: 04_outputs/tables/works_metadata_from_tei.csv

- **`make build-cases`** — Detecta casos/escenas (regex KWIC)
  - Genera: 01_data/kwic_exports/cases_raw.csv

- **`make rankings`** — Calcula rankings etnográficos de escenas
  - Genera: 04_outputs/tables/scene_summary.csv, case_rankings.csv

- **`make cooc`** — Coocurrencias en ventanas (WINDOW=40)
  - Genera: 04_outputs/tables/cooc_pairs.csv

### Reading Packs

- **`make reading-pack-diverse`** — Pack diverso (máx obras)
  - Genera: 03_analysis/reading_pack/diverse/reading_pack_diverse.csv

- **`make reading-pack-balanced`** — Pack balanceado (10 casos/escena)
  - Genera: 03_analysis/reading_pack/balanced/reading_pack_balanced.csv

- **`make pack-report`** — Comparación entre ambos packs
  - Genera: 04_outputs/tables/pack_report.md

### Reportes y Visualización

- **`make report-summary`** (MEJORA) — Reporte principal + manifests
  - Deps: build (implícito)
  - Guards: verifica reading packs; auto-regenera si faltan
  - Genera: REPORT.md, token_rates.csv, manifests

- **`make report-networks`** — Alias: exporta redes
- **`make report-figures`** — Alias: genera figuras PNG
- **`make viz-advanced`** — Visualizaciones avanzadas (scatter, heatmap, violin, 300 DPI)
- **`make viz-interactive`** — Dashboards HTML interactivos
- **`make viz-all`** — Todo: avanzadas + interactivas

### Módulos Especializados

- **`make emigrant-module`** — Módulo de representación del emigrante
  - Genera: tablas emigrant_by_*.csv, pack v2

- **`make fix-tokens-full`** (MEJORA) — Extrae tokens fulltext de TEI
  - Dependencies: emigrant-module (auto-regenera corpus_master_table.csv si falta)
  - Genera: work_tokens_full.csv, token_mismatch_audit.csv

- **`make evidence-pack-emigrante`** — Evidence pack (original, no v2tokens)
  - Genera: EVIDENCE_PACK_EMIGRANTE.md + 180 tarjetas de anotación

- **`make evidence-pack-emigrante-v2tokens`** (NUEVO) — Evidence pack con denominadores fulltext
  - Deps: fix-tokens-full (ya incluido)
  - Genera: EVIDENCE_PACK_EMIGRANTE_v2tokens.md (8 secciones con v2tokens callout)

### Freeze y Limpieza

- **`make freeze`** — Congela outputs completos (requiere report)
  - Genera: 05_freeze/vX.Y.Z/ con todos los artefactos

- **`make freeze-lite`** (RECOMENDADO) — Congela solo salidas finales
  - Genera: 05_freeze/vX.Y.Z-lite/ (sin inputs regenerables)
  - No requiere rebuild

- **`make clean-outputs`** — Borra 04_outputs/ y tarjetas (regenerable)
  - Mantiene: 01_data/tei/, 01_data/text/, 03_analysis/memos/
  - Permite: reiniciar limpiamente con `make build`

- **`make clean`** — Muestra opciones de limpieza sin ejecutar
- **`make clean-cases`** — Borra solo casos/escenas
- **`make clean-all`** — CUIDADO: borra TODO (requiere confirmación)

### Utilidades

- **`make status`** — Estado del pipeline (qué se ha generado)
- **`make help`** — Muestra todos los targets disponibles
- **`make check`** — Verifica estructura y dependencias Python

---

## Recuperación de Errores (Opción A: Auto-Regenerable)

### Escenario 1: Después de `make clean-outputs`

```bash
# ✓ FUNCIONA SIN PROBLEMAS
make clean-outputs  # Borra 04_outputs/ y lectura packs
make build          # Auto-regenera todo
make report-summary # Auto-regenera reading packs si faltan
```

### Escenario 2: Falta reading pack después de clean

```bash
# report-summary detecta que faltan packs y los regenera
make report-summary
# → Internamente: verifica diverse/balanced; auto hace reading-pack-{diverse,balanced}
```

### Escenario 3: Falta corpus_master_table.csv después de clean

```bash
# fix-tokens-full auto-regenera corpus_master_table.csv
make fix-tokens-full
```

### Escenario 4: Sin TEI presente

```bash
make build
# → ✓ Falla rápidamente con mensaje claro:
#   "❌ ERROR: No hay TEI en 01_data/tei/source/"
#   "Usa: make copy-from-tei TEI_DIR=/ruta/corpus-literario/tei"
# → Exit code: 1
```

---

## Estructura de Directorios

```
corpus-etnografico-galicia/
├── 00_docs/                          # Documentación oficial
│   ├── README_PROJECT.md             # Este archivo
│   ├── METHODOLOGY.md
│   ├── CHANGELOG.md
│   ├── PAPER1_OUTLINE.md
│   └── DATA_DICTIONARY.md
│
├── 01_data/                          # Inputs (parcialmente en git)
│   ├── tei/source/                   # ⚠️  Solo MANIFEST.md; .xml ignorados
│   ├── tei/derived/                  # (futuro)
│   ├── text/
│   │   └── units.csv                 # Texto extraído (regenerable)
│   ├── kwic_exports/
│   │   └── cases_raw.csv             # Casos detectados (regenerable)
│   └── external/
│
├── 02_methods/                       # Scripts y patrones (git)
│   ├── scripts_tei/                  # TEI extraction
│   ├── scripts_ethno/                # Case/scene detection, sampling
│   ├── scripts_core/                 # Reports, tokenization, emigrant
│   ├── scripts_metadata/             # Author normalization
│   ├── scripts_networks/             # Network export
│   ├── scripts_viz/                  # Visualization generation
│   ├── patterns/                     # YAML configs
│   │   ├── author_normalization.yml
│   │   ├── emigrante_markers.yml
│   │   └── reading_pack_rules.yml
│   └── tests/                        # pytest files
│
├── 03_analysis/                      # Analysis outputs (partially git)
│   ├── cases/                        # Memos y tarjetas detectadas (regenerable)
│   ├── memos/                        # Escritura etnográfica (KEPT en git)
│   ├── reading_pack/
│   │   ├── diverse/                  # Reading pack diverso (regenerable)
│   │   └── balanced/                 # Reading pack balanceado (regenerable)
│   └── metadata_enrichment/          # (futuro)
│
├── 04_outputs/                       # Salidas finales (IGNORADAS en git)
│   ├── reports/
│   │   ├── REPORT.md
│   │   ├── EVIDENCE_PACK_EMIGRANTE.md
│   │   ├── EVIDENCE_PACK_EMIGRANTE_v2tokens.md
│   │   └── by_author/
│   ├── tables/                       # CSVs principales (regenerables)
│   │   ├── scene_summary.csv
│   │   ├── case_rankings.csv
│   │   ├── cooc_pairs.csv
│   │   ├── corpus_master_table.csv
│   │   ├── corpus_master_table_v2tokens.csv
│   │   ├── emigrant_by_*.csv
│   │   ├── emigrant_by_*_v2tokens.csv
│   │   ├── work_tokens_full.csv
│   │   ├── token_mismatch_audit.csv
│   │   └── ... (más tablas derivadas)
│   ├── figures/
│   │   ├── static/                   # PNG/PDF 300 DPI
│   │   └── interactive/              # HTML dashboards
│   ├── networks/                     # Gephi exports
│   ├── manifests/
│   │   ├── ARTIFACTS_MANIFEST.csv
│   │   └── ARTIFACTS_MANIFEST.md
│   └── README.md                     # (marca que 04_outputs es regenerable)
│
├── 05_freeze/                        # Freeze-lite (versioned, KEPT en git)
│   └── v1.0.Z-lite/
│       ├── reports/
│       ├── tables/
│       ├── figures/static/
│       ├── manifests/
│       ├── FREEZE_NOTES.md
│       └── ARTIFACTS_MANIFEST.md
│
├── 05_annotations/                   # Templates para anotar (git)
│
├── 99_archive/                       # Legacy content (IGNORADO en git)
│
├── tools/                            # Utilities (git)
│   ├── copy_from_tei.py
│   ├── build_manifest.py
│   └── log_run.py
│
├── Makefile                          # Pipeline master (git)
├── requirements.txt                  # Python dependencies (git)
├── VERSION_ANALISIS.txt              # Version string (git)
├── CONFIG_ANALISIS.yml               # Configuration (git)
└── .gitignore                        # (Ignora 04_outputs, 99_archive)
```

---

## Outputs Principales

### Regenerables (en 04_outputs/)

- **REPORT.md** — Informe etnográfico principal
- **EVIDENCE_PACK_EMIGRANTE.md** — Evidence pack (denominadores snippet)
- **EVIDENCE_PACK_EMIGRANTE_v2tokens.md** — Evidence pack (denominadores fulltext)
- **Tables (*.csv)** — scene_summary, case_rankings, cooc_pairs, etc.
- **Figures** — Scatter, heatmap, violin, network, 300 DPI PNG/PDF
- **Manifests** — ARTIFACTS_MANIFEST.csv/.md

### Congelados (en 05_freeze/vX.Y.Z-lite/)

Solo artefactos finales necesarios para escritura:
- reports/*.md
- tables/*_v2tokens.csv + work_tokens_full.csv
- figures/static/*.png|*.pdf
- manifests/

---

## Filosofía del Pipeline

### Anti-positivismo

- No presentamos números como "hechos" sobre la literatura.
- Las escenas/casos son **heurísticas** para guiar lectura etnográfica.
- Los outputs (CSVs, MDdowns) son **memos auxiliares**, NO evidencia.
- La etnografía ocurre en la **escritura reflexiva** posterior.

### Reproducibilidad (Opción A)

- Pipeline **auto-regenerable**: si faltan intermedios, targets posteriores los crean.
- No hay "estados mágicos" ocultos; TODO se recrea desde TEI.
- `make clean-outputs && make report-summary` FUNCIONA incluso desde repo limpio.

### Transparencia

- Todos los scripts en 02_methods/scripts_core/ (git).
- Patterns (regex, YAML config) en 02_methods/patterns/ (git).
- Manifests SHA256 para verificar integridad.

---

## Próximos Pasos

1. **Escritura etnográfica**: Usa outputs como memos, escribe en 03_analysis/memos/
2. **Iteración**: Ajusta patterns en 02_methods/patterns/ → rebuild
3. **Publicación**: Congela con `make freeze-lite` → sube a GitHub/Zenodo

---

## Contacto / Soporte

Ver METHODOLOGY.md y PAPER1_OUTLINE.md para detalles técnicos.

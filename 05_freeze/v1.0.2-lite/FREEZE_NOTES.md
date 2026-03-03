# Freeze Notes (lite)

- Timestamp: 2026-02-27 10:18:58
- Version: v1.0.2
- Git commit: 8947a9bdd29c3e958b3236725d832d4d1959329f

## Commands
- make fix-tokens-full
- make evidence-pack-emigrante
- make freeze-lite

## Config
# Configuración del Análisis Etnográfico - Versión Baseline
# Frozen: 2026-02-25

scenes_yaml: escenas_minimas_v2.yml
author_normalization: author_normalization.yml

# Parámetros de análisis
cooc_min_weight: 20
token_unit: 1000
window_token_size: 40

# Datasets core
datasets:
  - name: "cases_raw"
    source: "01_data/kwic_exports/cases_raw.csv"
    description: "Casos/escenas detectados mediante KWIC regex"
  
  - name: "units"
    source: "01_data/text/units.csv"
    description: "Unidades narrativas (capítulos, cuent os)"
  
  - name: "works_metadata_from_tei"
    source: "04_outputs/tables/works_metadata_from_tei.csv"
    description: "Metadata canónica de autores extraída desde TEI"

# Reading packs
reading_packs:
  - name: "diverse"
    target: 180
    criteria: "Maximizar cobertura de obras y escenas"
  
  - name: "balanced"
    target: 160
    criteria: "10 casos por escena mínimo"

# Representación del emigrante (módulo experimental)
emigrant_markers:
  source: "02_methods/patterns/emigrante_markers.yml"
  targets_density: "cases/1k_tokens"
  pack_strategy: "one_per_work_if_exists"

# Notas metodológicas
methodology:
  author_grouping: "author_normalized (forma canónica desde TEI)"
  author_confidence: "high/medium/low_inferred + why_missing"
  cooc_semantics: "Tensiones narrativas (NO causalidad)"
  literature_ontology: "Artefacto cultural situado (NO fuente empírica)"


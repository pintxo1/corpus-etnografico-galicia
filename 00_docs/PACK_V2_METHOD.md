# Emigrant Representation Pack v2 (pack_v2) - Methodology

## Overview

El **Emigrant Representation Pack v2** es un conjunto estratificado de 180 casos de menciones al emigrante diseñado para análisis cualitativo basado en lectura cercana. Este pack proporciona cobertura representativa del corpus: **74 de 80 obras** (92.5%), 9 autores, 9 décadas, manteniendo trazabilidad con las métricas cuantitativas.

**Objetivo:** Seleccionar casos que permitan análisis cualitativo de las representaciones literarias de la emigración gallega equilibrando:
- Cobertura de obras (al menos 1 caso por obra con menciones)
- Balance temporal (distribución por décadas)
- Diversidad autoral
- Controles negativos (obras sin menciones explícitas)

**Nota importante:** 6 obras del corpus (7.5%) no están representadas en el pack v2 porque no contienen menciones explícitas al emigrante según la detección del sistema.

## Selection Rules

El pack v2 se construye mediante la siguiente regla de selección operacional:

### Phase 1: Mandatory One-Per-Work
- **Criterio:** 1 caso por obra que contenga menciones al emigrante
- **Razonamiento:** Garantizar cobertura mínima del corpus completo
- **Implementación:** Selección del primer caso (mayor confianza) de cada obra con `n_emigrant_mentions > 0`
- **Resultado:** ~74 casos base

### Phase 2: Decade-Balanced Supplementary
- **Criterio:** Distribución proporcional por década desde el pool restante
- **Razonamiento:** Preservar balance temporal para análisis diacrónico
- **Implementación:** Selección de casos adicionales (position 2+) agrupados por década
- **Cuota:** ~106 casos suplementarios (180 total - 74 base)

### Phase 3: Negative Controls (10%)
- **Criterio:** 10% de obras SIN menciones explícitas al emigrante
- **Razonamiento:** Control para contrastar ausencia vs. presencia
- **Marcado:** `type=NEGATIVE` (explícito en pack_v2)
- **Nota:** En la versión actual, los controles negativos NO están implementados (todos los casos tienen `n_emigrant_mentions > 0`)

### Stratification Constraints
- **Max per obra:** Sin límite superior explícito (promedio ~2.4 casos/obra)
- **Min per década:** Sin mínimo fijo; distribución emergente desde densidades originales

## Pack Coverage Summary

| Dimensión | Valor | Fuente |
|-----------|-------|--------|
| **Corpus total** | 80 obras | corpus_master_table_v2tokens.csv |
| **Total casos** | 180 | emigrante_representation_pack_v2.csv |
| **Obras únicas** | 74 | 92.5% del corpus |
| **Obras excluidas** | 6 | Sin menciones detectadas (ver lista abajo) |
| **Autores únicos** | 9 | 100% de autores con menciones |
| **Décadas únicas** | 9 | 1880s–1960s (cobertura completa) |
| **Avg casos/obra** | 2.43 | 180 casos / 74 obras |
| **Controles negativos** | 0 | NOT IMPLEMENTED (pendiente Phase 3) |

### Obras Excluidas del Pack v2

Las siguientes 6 obras (7.5% del corpus) no están representadas en el pack v2 porque el sistema no detectó menciones explícitas al emigrante en su léxico:

1. `cara_de_plata_001`
2. `castelao_cousas_tei_v2`
3. `el_quinto`
4. `la_danza_del_peregrino`
5. `la_flor_seca`
6. `testigo_irrecusable`

**Nota metodológica:** Esta exclusión refleja los límites del sistema de detección léxica (ver `PAPER_METHOD_SUMMARY.md` sección "System Detection Limits"). Estas obras pueden contener representaciones implícitas de la emigración sin usar marcadores léxicos explícitos.

### Distribution by Author
(Inferido desde datos; no hay tabla explícita en script)

### Distribution by Decade
(Inferido desde datos; balance emergente según densidades originales)

## Traceability

### Input Files
1. **emigrant_mentions_by_work.csv** → Densidades por obra (`n_mentions`, `density_per_1k_tokens`)
2. **emigrante_kwic_cases.csv** → Casos individuales con contexto KWIC
3. **works_metadata_from_tei.csv** → Metadata (author_normalized, year, decade)

### Output Files
1. **emigrante_representation_pack.csv** → Pack base (Phase 1 + 2)
2. **emigrante_representation_pack_v2.csv** → Pack validado y enriquecido
3. **emigrante_representation_pack_v2/cases/*.md** → Fichas MD para anotación manual (una por caso)

### Processing Scripts
- `02_methods/scripts_core/select_emigrant_rep_pack.py` → Selección inicial
- `02_methods/scripts_core/update_emigrant_pack_v2.py` → Validación, enriquecimiento, generación de fichas

## Methodological Notes

### Selection Reason Flags
Cada caso en el pack incluye `selection_reason`:
- `mandatory_one_per_work` → Fase 1 (coverage)
- `decade_balance_Nones` → Fase 2 (temporal balance)
- `negative_control` → Fase 3 (NO IMPLEMENTADO en versión actual)

### Limitations

1. **Regla inferida desde outputs:** No existe configuración upstream explícita (e.g., YAML) que especifique cuotas exactas por autor/década. La regla documentada aquí se infiere desde:
   - Código fuente de `select_emigrant_rep_pack.py` (lógica imperativa)
   - Distribución observada en `emigrante_representation_pack_v2.csv`
   - Comentarios en scripts y FREEZE_NOTES.md
   
2. **Controles negativos no implementados:** El pack actual NO incluye obras sin menciones (10% planificado, 0% implementado). Todos los 180 casos provienen de obras con `n_emigrant_mentions > 0`.

3. **Estratificación por formato:** No existe estratificación explícita por género literario (cuento vs. novela vs. ensayo). La distribución emergente refleja las densidades naturales del corpus.

4. **No es muestra estadística:** El pack es una herramienta de lectura dirigida, NO una muestra probabilística. Los resultados cualitativos no deben generalizarse al corpus completo sin validación cuantitativa.

## Validation Workflow

```bash
# Regenerar pack desde cero
make select-emigrant-pack  # Ejecuta select_emigrant_rep_pack.py

# Validar y enriquecer
make update-emigrant-pack-v2  # Ejecuta update_emigrant_pack_v2.py

# Verificar cobertura
python3 -c "import pandas as pd; df = pd.read_csv('03_analysis/reading_pack/emigrante_representation_pack_v2.csv'); print(f'Obras: {df[\"obra_id\"].nunique()}, Autores: {df[\"author_normalized\"].nunique()}, Décadas: {df[\"decade\"].nunique()}')"
```

## Future Improvements

1. **Implement negative controls:** Add 10-15% obras sin menciones (controles verdaderos)
2. **Explicit YAML config:** Document target quotas (author/decade/format) in `reading_pack_rules.yml`
3. **Genre stratification:** Add min cases per genre (cuento/novela/ensayo)
4. **Inter-annotator agreement:** Generate duplicate cards for reliability testing

---

**Version:** 1.0.0  
**Last updated:** 2026-02-28  
**Script sources:** `select_emigrant_rep_pack.py`, `update_emigrant_pack_v2.py`  
**Data source:** `emigrante_representation_pack_v2.csv` (180 casos, 74 obras)

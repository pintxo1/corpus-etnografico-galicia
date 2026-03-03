# TOKEN QA REPORT — v2tokens

**Fecha:** 2026-02-28 11:43:22
**Propósito:** Auditar discrepancias entre tokens snippet (units_enriched) y tokens fulltext (TEI)

---

## 1. RESUMEN EJECUTIVO

**Total obras auditadas:** 80
**Obras con mismatch >20%:** 1 ⚠️
**Obras con mismatch >10%:** 1
**Mismatch promedio (todas):** 1.17%
**Mismatch máximo:** 93.89% (en castelao_cousas_tei_v2)

**→ CONCLUSIÓN:** Solo 1 obra(s) tienen mismatch >20%. Caso aislado, no indica bugfix estructural.

---

## 2. TOP 15 MISMATCHES

| Obra ID | Tokens Snippet | Tokens Full | Mismatch % | N Unidades | Avg Unit Chars |
|---------|----------------|-------------|-----------|-----------|---|
| castelao_cousas_tei_v2 ⚠️ | 707 | 11,564 | 93.89% | 3 | 1299 |
| curros_enriquez_aires_de_la_tierra.tei  | 33,835 | 33,832 | 0.01% | 51 | 3635 |
| la_danza_del_peregrino  | 1,723 | 1,723 | 0.00% | 1 | 10308 |
| la_mayorazga_de_bouzas  | 3,731 | 3,731 | 0.00% | 1 | 21676 |
| la_hoz  | 2,037 | 2,037 | 0.00% | 1 | 12144 |
| la_flor_seca  | 1,523 | 1,523 | 0.00% | 1 | 9101 |
| la_flor_de_la_salud  | 1,673 | 1,673 | 0.00% | 1 | 9792 |
| la_expiacion  | 2,318 | 2,318 | 0.00% | 1 | 13850 |
| la_exangüe  | 1,414 | 1,414 | 0.00% | 1 | 8411 |
| la_estrella_blanca  | 2,150 | 2,150 | 0.00% | 1 | 12940 |
| la_emparedada  | 1,205 | 1,205 | 0.00% | 1 | 6960 |
| Los-pazos-de-Ulloa-novela-original-precedida-de-unos-apuntes-autobiográficos-por-Emilia-Pardo-Bazán  | 262,479 | 262,479 | 0.00% | 1 | 1541943 |
| la_señorita_aglae  | 1,728 | 1,728 | 0.00% | 1 | 9873 |
| la_corpana  | 1,355 | 1,355 | 0.00% | 1 | 7894 |
| la_charca  | 1,578 | 1,578 | 0.00% | 1 | 9448 |

---

## 3. OBRAS PEQUEÑAS (≤3 unidades) CON MISMATCH >10%

| Obra ID | Tokens Snippet | Tokens Full | Mismatch % | N Unidades |
|---------|----------------|-------------|-----------|---|
| castelao_cousas_tei_v2 | 707 | 11,564 | 93.89% | 3 |

---

## 4. DIAGNÓSTICO POR PATRÓN

### Patrón A: Truncamiento por snippet

**Característica:** tokens_snippet << tokens_full (10% a 40%+ diferencia)
**Causa probable:** units_enriched contiene preview truncado (snippet_text limitado a N caracteres)
**Identificación:** mismatch_pct > 10%

**Obras identificadas (1):**

  - **castelao_cousas_tei_v2**: 707 snippet → 11,564 full (pérdida 93.9%)


### Patrón B: TEI con body muy corto (legítimo)

**Característica:** tokens_full < 1000 tokens

**Causa probable:** Obra pequeña, poema corto, fragmento genuino
**Identificación:** tokens_full < 1000 Y mismatch_pct < 10%

**Obras identificadas (4):**

  - **romance_de_lobos_001**: 617 tokens (pequeña legítima)
  - **aguila_de_blason_001**: 586 tokens (pequeña legítima)
  - **el_lorito_real**: 835 tokens (pequeña legítima)
  - **cara_de_plata_001**: 828 tokens (pequeña legítima)


### Patrón C: Tokenización/limpieza inconsistente

**Característica:** mismatch_pct 2% a 9% (pequeño pero consistente)

**Causa probable:** Diferencia en reglas split() (spaces, punctuation) o limpieza de whitespace
**Identificación:** 0.02 < mismatch_pct < 0.10

No hay obras con este patrón en esta ejecución.


---

## 5. RECOMENDACIONES

✅ **DOCUMENTAR COMO CASO AISLADO**

Solo 1 obra con mismatch >20%: **castelao_cousas_tei_v2**

Acciones sugeridas:
  1. Marcar con token_mismatch_flag=1 en corpus_master (✓ ya existe)
  2. Añadir nota en VERSION_ANALISIS sobre esta obra
  3. Mantener *_v2tokens como canonical (tokens_full)

---

## APÉNDICE: DEFINICIONES

- **tokens_snippet**: Suma de n_tokens de todas las unidades en units_enriched.csv por obra
- **tokens_full**: tokens_total_full de work_tokens_full.csv (extracción directa tei:body)
- **mismatch_abs**: |tokens_full - tokens_snippet|
- **mismatch_pct**: mismatch_abs / tokens_full (fracción de pérdida)
- **flag_20pct**: 1 si mismatch_pct > 0.20 (significativo)
- **flag_10pct**: 1 si mismatch_pct > 0.10 (notable)

**Generated:** 2026-02-28T11:43:22.302853
**Source data:** units_enriched.csv, work_tokens_full.csv, corpus_master_table_v2tokens.csv
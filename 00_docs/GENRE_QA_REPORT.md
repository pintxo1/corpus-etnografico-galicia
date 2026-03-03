# GENRE QA REPORT

**Fecha generación:** 2026-02-27 10:17
**Corpus:** 80 obras

---

## 1. Executive Summary

- **Total obras analizadas:** 80
- **Género identificado (no unknown):** 80 obras (100.0%)
- **Género unknown:** 0 obras (0.0%)

**✅ COBERTURA EXCELENTE:** 100% de obras con género identificado desde TEI headers.

---

## 2. Confidence Breakdown

| Confidence | Count | Percent |
|------------|-------|---------|
| high | 80 | 100.0% |
| medium | 0 | 0.0% |
| low | 0 | 0.0% |
| error | 0 | 0.0% |
| **TOTAL** | **80** | **100.0%** |

**Interpretación:** Excelente calidad de extracción. La mayoría de géneros provienen directamente de `<classCode scheme='genero'>` en TEI headers.

---

## 3. Genre Distribution

| Genre | Count | Percent |
|-------|-------|---------|
| cuento_relato | 61 | 76.2% |
| novela | 7 | 8.8% |
| poesia_poemario | 6 | 7.5% |
| teatro | 3 | 3.8% |
| ensayo_cronica | 3 | 3.8% |
| **TOTAL** | **80** | **100.0%** |

---

## 4. Top genre_raw → genre_norm Mappings

Valores extraídos de TEI (`genre_raw`) y su normalización (`genre_norm`):

| genre_raw | genre_norm | Count |
|-----------|------------|-------|
| cuento | cuento_relato | 61 |
| novela | novela | 7 |
| poesia | poesia_poemario | 6 |
| ensayo | ensayo_cronica | 3 |
| teatro | teatro | 3 |

---

## 5. Obras con genre_norm=unknown

✅ **Ninguna obra con género unknown.** Todos los géneros se extrajeron correctamente de TEI headers.

---

## 6. Validation Summary

- ✅ Extracción de género desde TEI: **80 obras procesadas**
- ✅ Tasa de éxito: **100.0%**
- ✅ Confidence high: **80/80 obras** (100.0%)
- ✅ **Ninguna obra requiere corrección de TEI**

**Conclusión:** Genre extraction completado exitosamente. Corpus listo para análisis por formato/género.

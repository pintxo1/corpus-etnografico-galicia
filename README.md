# Etnografía Digital Gallega — Literatura como Artefacto Cultural (1860-1950)

**Nota:** La documentacion oficial esta en 00_docs/README_PROJECT.md.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-experimental-orange.svg)]()

Etnografía digital reflexiva que **sitúa** la literatura gallega (1860-1950) como **producción de imaginario** sobre migración, arraigo y movilidad. No buscamos "reflejar" realidad ni "medir" contexto social, sino **mapear repertorios narrativos**, identificar **disonancias** entre géneros/autores/décadas, y establecer **contrapuntos** con archivos históricos para iluminar las condiciones de producción del discurso migratorio.

---

## 🎯 Propósito del Proyecto

**Pregunta orientadora:**  
¿Cómo se **fabrica** el imaginario migratorio gallego en la literatura (1860-1950)? ¿Qué **escenas**, **afectos** y **normatividades** circulan en los textos? ¿Qué **silencios** estructuran el corpus?

**Marco teórico:**  
Los textos literarios son **artefactos culturales** situados: producidos por autores con posición social, género, circuito editorial y audiencias específicas. No "capturan" estructuras sociales transparentemente, sino que **participan** en la producción de sentido sobre qué es emigrar, quedarse, pertenecer o moverse. Usamos cuantificación como **heurística de muestreo**, no como prueba de realidad.

**Metodología:**  
- **Análisis de "casos/escenas"**: Extracción de concordancias KWIC (keyword-in-context) como unidades etnográficas mínimas
- **Muestreo estratificado**: PCA/clustering como heurística para diversificar corpus, no para clasificar "tipos" naturales
- **Contrapunto documental**: Archivos históricos (IGE, catastros, prensa) como contexto, no como validación
- **Reflexividad**: Atentos a posición de autores, género literario, voz narrativa, omisiones

**Output central:**  
Un dataset de **casos/escenas** (`cases_sampled.csv`) + memos etnográficos reflexivos. No generamos "métricas de realidad" sino un **repertorio analizable** de cómo se narrativiza migración, pertenencia y movilidad.

---

## 📊 Enfoque Etnográfico (anti-positivista)

### Reglas de Evidencia y Reflexividad

Este proyecto adopta un enfoque etnográfico digital **reflexivo**. No tratamos clusters, densidades o coocurrencias como "hechos naturales". Reglas operativas:

1. **Anti-cherry-picking**: Usamos algoritmos para muestrear sistemáticamente, pero reconocemos que los patrones regex ya son **teoría encarnada** (presuponen qué importa buscar).

2. **No reificar clusters**: Si PCA separa k=4 grupos de obras, esto **no significa** que existan "4 tipos de literatura migratoria". Es un artefacto de nuestras variables y método. Los usamos solo para **estratificar muestreo** (asegurar diversidad de obras analizadas).

3. **Escenas como heurísticas**: Un match regex de "embarcar + América" no es "evidencia de emigración real". Es una **escena textual** que requiere lectura situada: ¿quién narra? ¿en qué género (cuento/novela/poema)? ¿con qué tono (épico, melancólico, irónico)?

4. **Atención a género literario**: Novela realista ≠ cuento fantástico ≠ poesía lírica. Los géneros tienen **contratos de veridicción** distintos. No mezclamos densidades sin ponderar estas diferencias.

5. **Atención a posición de autor/a**: Pardo Bazán (aristócrata, cosmopolita, mujer) produce imaginario distinto que Valle-Inclán (bohemio, carlista, masculino). Las voces no son intercambiables.

6. **Límites de la cuantificación**: Contar frecuencias revela **superficie léxica**, no semántica profunda. Un texto con baja densidad de "América" puede estar estructurado enteramente por ausencia migratoria (silencio ≠ inexistencia).

7. **Triangulación como contrapunto**: Cuando comparamos literatura con datos IGE de emigración, **no validamos** si la literatura "dice verdad". Buscamos **disonancias**: ¿qué años la literatura habla mucho de migración pero IGE muestra pocas salidas? ¿Por qué?

8. **Reflexividad sobre corpus**: Nuestro corpus es archivo heredado (Biblioteca Virtual Cervantes, Internet Archive). Está sesgado hacia autores canónicos y castellanohablantes. ¿Qué literatura popular, gallego-oral, femenina-no-publicada queda fuera?

### ¿Por qué cuantificar entonces?

No para "probar" nada, sino como **tecnología de lectura distante** (Moretti):  
- **Exhaustividad relativa**: Procesamos 80 obras, no 3 favoritas del investigador  
- **Muestreo diversificado**: Algoritmos garantizan que no sobre-representamos un autor/década  
- **Transparencia**: Los patrones regex y scripts son auditables (vs. interpretación cerrada)  
- **Generación de preguntas**: Anomalías estadísticas (outliers, coocurrencias inesperadas) guían lectura cercana etnográfica

---

## 📂 Arquitectura de Datos y Métodos

### Datos (sin symlinks, autónomo)

```
01_data/
├── tei/
│   ├── source/              # Corpus TEI-XML copiado (con MANIFEST.md)
│   └── derived/             # TEI transformados/anotados (si aplicable)
├── text/
│   └── units.csv            # Unidades textuales extraídas (obra_id, unidad_id, text, n_tokens)
├── kwic_exports/
│   └── cases_raw.csv        # Todos los casos/escenas detectados
└── external/                # Archivos históricos (IGE, catastros, prensa)
    └── SOURCES.md           # Registro de fuentes y limitaciones
```

### Métodos

```
02_methods/
├── patterns/
│   ├── escenas_minimas.yml  # Patrones regex por tipo de escena
│   └── reading_pack_rules.yml  # Reglas para sampling estratificado
├── scripts_tei/
│   ├── tei_to_text.py       # TEI → units.csv
│   └── README_tei_scripts.md
├── scripts_ethno/
│   ├── build_kwic_cases.py  # units.csv + patterns → cases_raw.csv
│   ├── sampling_by_profile.py  # Muestreo estratificado (diverse/balanced packs)
│   ├── cooc_scene_windows.py   # Coocurrencias como "tensión"
│   └── README_ethno.md
├── scripts_reports/
│   ├── build_report.py      # REPORT.md integrado (8 secciones + 6b visualizaciones)
│   └── token_rates.py       # Token-normalized rates per 1k tokens
├── scripts_viz/
│   ├── fig_scene_scatter.py          # Scatter: coverage vs concentration
│   ├── fig_scene_heatmap.py          # Heatmap: escena × obra
│   ├── fig_scene_rates_distribution.py  # Violin plots: distribuciones
│   ├── fig_cooc_network_filtered.py  # Network: términos + Louvain communities
│   └── dashboard_cases.html.py       # Interactive case browser (HTML)
└── tests/
    └── test_*.py            # Pytest mínimos
```

### Análisis y Outputs

```
03_analysis/
├── cases/
│   ├── cases_sampled.csv    # Casos seleccionados para lectura
│   ├── {case_id}.md         # Markdown por caso (contexto + memo)
│   └── README_cases.md
├── reading_pack/
│   ├── diverse/             # Diverse pack: 180 casos × 76 works (stratified)
│   │   └── reading_pack_diverse.csv
│   └── balanced/            # Balanced pack: 160 casos × 10 per scene
│       └── reading_pack_balanced.csv
└── memos/
    ├── MEMO_template.md
    └── {tema}.md            # Memos temáticos transversales

04_outputs/
├── tables/
│   ├── scene_summary.csv           # 16 escenas with coverage & concentration
│   ├── case_rankings.csv           # 3,550 cases with salience_z scores
│   ├── scene_rates_per_1k_tokens.csv  # Token-normalized rates
│   ├── cooc_pairs.csv              # Coocurrencias (103 pares, min_cooc)
│   ├── token_totals.csv            # Token counts per unidad
│   ├── pack_report.csv/md          # Diverse vs balanced comparison
│   └── sampling_audit.csv/md       # Audit trail y reglas aplicadas
├── reports/
│   ├── REPORT.md                   # Main report (8 sections + 6b visualizations)
│   └── README_reports.md
├── manifests/
│   ├── ARTIFACTS_MANIFEST.csv      # Complete output inventory
│   └── ARTIFACTS_MANIFEST.md
└── figures/
    ├── static/                     # Publication-ready PNG/PDF (150 DPI)
    │   ├── fig_scene_scatter.*
    │   ├── fig_scene_work_heatmap.*
    │   ├── fig_scene_rates_distribution.*
    │   └── fig_cooc_network_filtered.*
    ├── interactive/                # Interactive HTML dashboards
    │   └── dashboard_cases.html    # 340 curated cases browser
    ├── 00_README_FIRST.md
    ├── VISUALIZATIONS_README.md
    └── PHASE_9_COMPLETION_SUMMARY.md
```

**Nota:** Carpetas heredadas del pipeline anterior (data/, outputs/, datasets_historicos/, scripts/, stats_analysis/) quedan como legado y no se usan en el flujo etnográfico actual.

---

## 📚 Fundamentos Teórico-Metodológicos

### Literatura como Artefacto Situado

Los textos **no reflejan** realidad social transparentemente. Son:

1. **Productos de posiciones**: Pardo Bazán escribe desde aristocracia cosmopolita; sus "campesinos" son constructos mediados por su clase y género.
2. **Géneros con lógicas propias**: Novela realista pretende verosimilitud; poesía lírica trabaja con afectos; fantástico subvierte referencia.  
3. **Circulación desigual**: Textos publicados en Madrid ≠ literatura oral gallega no archivada.  
4. **Performatividad**: Al narrar emigración, los textos **producen** imaginario migratorio (aspiracional, melancólico, heroico), no solo lo documentan.

### Cuantificación como Heurística (no como Prueba)

- **Distant reading** (Moretti): Patrones a escala corpus (outline) guían **close reading** etnográfico (detalle)
- **PCA/clustering**: Herramientas de **muestreo diversificado**, no taxonomías ontológicas
- **Coocurrencias**: Señalan "densidades narrativas" donde múltiples tensiones convergen (hambre+violencia, tierra+herencia), pero **no implican causalidad** social real

### Contrapunto Documental (no Validación)

Archivos históricos (IGE, catastros, prensa) no "verifican" si literatura "dice verdad". Funcionan como **contrapunto**:

- **Convergencias**: ¿Literatura y datos IGE coinciden en picos migratorios 1880-1920? → Preguntar por **condiciones compartidas** de producción discursiva (crisis agraria genera tanto emigración como narrativas de éxodo)
- **Disonancias**: ¿Literatura habla mucho de "retorno indiano" (1890s) pero IGE muestra pocas vueltas? → Explorar **aspiración vs. prácticica**: retorno como fantasía cultural, no realidad mayoritaria
- **Silencios**: ¿Qué NO aparece en literatura pero sí en archivos? (Ej: documentos notariales de deudas femeninas; literatura enfoca deuda masculina)

---

## 📦 Escenas Etnográficas (versión mínima)

16 tipos de escenas etnográficas (no "variables independientes") definidos en:
[02_methods/patterns/escenas_minimas.yml](02_methods/patterns/escenas_minimas.yml)

**Tipos actuales:**
1. **migracion_embarque**: Embarque/partida a América
2. **retorno_indiano**: Retorno de indianos
3. **herencia_tierra**: Disputa de herencias/propiedad
4. **hambre_subsistencia**: Hambre y crisis de subsistencia
5. **trabajo_jornalero**: Jornales, criados, trabajo asalariado
6. **deuda_usura**: Deudas, usura, embargos
7. **caciquismo_poder**: Caciques, autoridad local, clientelismo
8. **violencia_agresion**: Violencia física, agresiones
9. **genero_roles**: Roles de género, trabajo femenino
10. **muerte_duelo**: Muerte, entierro, duelo
11. **religiosidad_supersticion**: Religiosidad popular, supersticiones
12. **ciclo_agricola**: Siembra, cosecha, trabajo agrícola
13. **aldea_ciudad**: Contraste rural-urbano
14. **movilidad_interna**: Movilidad interna, caminos, siega
15. **morriña_nostalgia**: Morriña, nostalgia
16. **amor_deseo**: Afectos, deseo, relaciones

**Nota crítica**: Estas escenas ya son **teoría** (presuponen qué importa: migración, género, economía). Un corpus enfocado en "afectos" o "infancia" requeriría categorías distintas. Reconocemos este sesgo inicial.

---

## ⚙️ Instalación y Requisitos

### Requisitos

- **Python:** 3.10+ (probado con 3.13)
- **Git:** Para clonar repositorio
- **Dependencias Python:** matplotlib, pandas, numpy, networkx, lxml, pyyaml, pytest
- **(Opcional) R:** 4.4+ para visualizaciones exploratorias
- **(Opcional) pyvis:** Para visualizaciones interactivas avanzadas de redes

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/corpus-etnografico-galicia.git
cd corpus-etnografico-galicia

# Crear entorno virtual (recomendado)
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias Python
pip install -r requirements.txt

# Instalar dependencias opcionales (para visualizaciones avanzadas)
pip install pyvis  # Para redes interactivas (opcional)
```

### Tests

```bash
make test
# o directamente:
.venv/bin/python -m pytest 02_methods/tests
```

### Estado de dependencias

- **Requeridas:** matplotlib, pandas, numpy, networkx, lxml, pyyaml, pytest
- **Opcionales:** pyvis (para HTML interactivo de redes)
- **Notas:** Si PyYAML falta, algunos scripts degeneran gracefully sin error
```

---

## 🚀 Uso Rápido (Pipeline Completo)

### Pipeline End-to-End (Recomendado):

```bash
# Ejecutar el pipeline TEI → visualizaciones → reporte integrado
make report

# Esto ejecuta automáticamente:
# 1. init (crear estructura)
# 2. copy-from-tei (importar TEI con MANIFEST)
# 3. tei-to-text (units.csv)
# 4. build-cases (cases_raw.csv)
# 5. rankings (scene_summary, case_rankings)
# 6. cooc (coocurrencias)
# 7. audit-sampling (verificación)
# 8. reading-pack-diverse + reading-pack-balanced (muestreo dual)
# 9. viz-all (visualizaciones avanzadas: scatter, heatmap, violin, network, dashboard)
# 10. report-summary (REPORT.md integrado con sección 6b)
```

### Etapas Individuales:

```bash
# 1. Importar TEI
make copy-from-tei TEI_DIR=/ruta/a/tei/

# 2. Extraer texto
make tei-to-text

# 3. Detectar casos/escenas
make build-cases

# 4. Análisis inicial
make rankings              # Scene summaries + token rates
make cooc WINDOW=40        # Coocurrencias
make audit-sampling        # Auditoria de reglas

# 5. Muestreo estratificado (dos enfoques)
make reading-pack-diverse   # 180 casos × 76 works (máxima diversidad)
make reading-pack-balanced  # 160 casos × 10 per scene (comparable)

# 6. Visualizaciones
make viz-advanced          # Static PNG/PDF (scatter, heatmap, violin, network)
make viz-interactive       # Interactive HTML (dashboard + optional network)
make viz-all              # Ambas

# 7. Reportes finales
make report-summary        # REPORT.md + manifest + token rates
```

### Acceso a Resultados:

```bash
# Visualizaciones estáticas (publication-ready)
open 04_outputs/figures/static/fig_scene_scatter.pdf

# Dashboard interactivo (en navegador)
open 04_outputs/figures/interactive/dashboard_cases.html

# Reporte integrado con links
open 04_outputs/reports/REPORT.md

# Ver casos muestreados
ls -1 03_analysis/cases/*.md | head -10
```

---

## 📈 Outputs Principales

### 1. Dataset de Casos/Escenas Totales

**`01_data/kwic_exports/cases_raw.csv`** (3,550 casos totales)

```csv
case_id,obra_id,unidad_id,escena_tipo,kwic,ventana_texto,start_idx,end_idx,match_term
1,pazos_ulloa,cap_12,migracion_embarque,"...decidió **embarcar**...","...contexto ampliado...",1250,1260,embarcar
2,flor_santidad,div_03,herencia_tierra,"...la **tierra** que **heredó**...","...contexto ampliado...",820,834,heredó
```

### 2. Packs de Lectura Estratificados

**`03_analysis/reading_pack/diverse/reading_pack_diverse.csv`** (180 casos × 76 works)
- Muestreo diversificado: máxima cobertura de obras
- Estratificación por escena + cluster de similitud
- Útil para: exploraciones amplias, patrones corpus-level

**`03_analysis/reading_pack/balanced/reading_pack_balanced.csv`** (160 casos × 10/escena)
- Muestreo balanceado: comparable entre escenas
- 10 casos por escena (16 × 10 = 160)
- Útil para: análisis comparativo escena-a-escena

### 3. Resumen Estadístico por Escena

**`04_outputs/tables/scene_summary.csv`**

```csv
escena_tipo,n_obras,n_casos,coverage_pct,top3_obras_pct
migracion_embarque,5,31,6.25,58.06
amor_deseo,25,690,31.25,27.39
...
```

**Columnas**: Escena, # obras únicas, # casos, cobertura (% del corpus), concentración (% en top 3)

### 4. Rankings de Casos por Escena

**`04_outputs/tables/case_rankings.csv`** (3,550 casos con salience scores)

```csv
case_id,obra_id,escena_tipo,salience_z,rank_in_scene
1,pazos_ulloa,migracion_embarque,-0.523,15
...
```

**salience_z**: Z-score de importancia dentro de escena (positivo = sobrerrepresentado)

### 5. Tasas Token-Normalizadas

**`04_outputs/tables/scene_rates_per_1k_tokens.csv`**

Casos por escena **normalizados por 1,000 tokens** (1,007,566 tokens totales)

```csv
escena_tipo,n_casos,tokens_total,casos_per_1k_tokens
migracion_embarque,31,1007566,0.0308
amor_deseo,690,1007566,0.6850
```

### 6. Coocurrencias como Tensión Narrativa

**`04_outputs/tables/cooc_pairs.csv`** (103 pares, filtered min_cooc≥)

```csv
term_1,term_2,n_cooc,n_term1,n_term2,jaccard,ejemplos_contexto
hambre_subsistencia,violencia_agresion,89,167,335,0.4123,"el hambre los llevó a robar pan..."
herencia_tierra,muerte_duelo,34,63,602,0.0541,"heredó la tierra de su padre muerto..."
```

**Interpretación**: No "hambre causa violencia en la realidad". Sí: en 89 ventanas textuales, **escenas de hambre y violencia aparecen próximas**. Guía lectura etnográfica: ¿cómo se narrativiza? ¿Qué voces la legitiman?

### 7. Visualizaciones Publication-Ready (Phase 9)

**`04_outputs/figures/static/`** — PNG (150 DPI) + PDF (vector)

1. **fig_scene_scatter** (coverage vs concentration): Corpus-level scene overview
2. **fig_scene_work_heatmap** (escena × top 40 works): Scene-source mapping with token normalization
3. **fig_scene_rates_distribution** (violin plots): Rate spread across 5 diverse scenes
4. **fig_cooc_network_filtered** (13 nodes, 24 edges): Term co-occurrence + Louvain communities

**`04_outputs/figures/interactive/`** — HTML (self-contained)

- **dashboard_cases.html** (14 MB): Interactive case browser (340 curated cases from both packs)
  - Filters: Scene, Pack, Salience ranking
  - Real-time statistics
  - KWIC contexto view

### 8. Reporte Integrado

**`04_outputs/reports/REPORT.md`** (9 secciones + subsecciones)

1. Run Summary (80 TEI, 177 units, 3,550 cases, 16 scenes)
2. Scene Coverage & Concentration
3. Reading Packs (Diverse vs Balanced)
4. Audit & Reproducibility
5. Co-occurrence Networks
6. Figures Generated (legacy)
6b. **Enhanced Visualizations (NEW)** — Static + Interactive listings
7. Run Parameters & Configuration
8. Limitations & Methodological Reflexivity

### 9. Manifest Completo

**`04_outputs/manifests/ARTIFACTS_MANIFEST.csv`** (33 artifacts)
- Tipo: output, rules
- Ruta, tamaño, SHA256, descripción
- Trazabilidad completa

---

## 📖 Recursos Metodológicos

### Lecturas Clave

**Etnografía digital y reflexividad:**
- Palmer, C. L., et al. (2009). _Scholarly Information Practices in the Online Environment_  
- Boellstorff, T. (2012). _Ethnography and Virtual Worlds_  
- Pink, S., et al. (2016). _Digital Ethnography: Principles and Practice_

**Lectura distante / Cuantificación textual:**
- Moretti, F. (2013). _Distant Reading_  
- Underwood, T. (2019). _Distant Horizons: Digital Evidence and Literary Change_  
- Da, N. Z. (2019). "The Computational Case against Computational Literary Studies" (_Critical Inquiry_)

**Crítica a positivismo en DH:**
- Liu, A. (2012). "Where is Cultural Criticism in the Digital Humanities?"  
- Drucker, J. (2011). "Humanities Approaches to Graphical Display"  
- D'Ignazio & Klein (2020). _Data Feminism_

### Herramientas y Datos

**Archivos históricos gallegos:**
- **IGE:** https://www.ige.eu/ (Instituto Galego de Estadística)
- **Arquivo Histórico de Galicia:** http://arquivo.xunta.gal/
- **PARES:** http://pares.mcu.es/ (Ministerio de Cultura, listas de pasajeros)
- **Museo da Emigración Galega:** http://www.museodaemigracion.gal/

**Software:**
- **Python:** lxml, pandas, pytest (PyYAML opcional)
- **(Opcional) R:** tidyverse, corrplot para visualizaciones exploratorias
- **(Futuro) Gephi:** Visualización de redes de actores

---

## 🔌 Importación de TEI y autonomía del proyecto

Este repositorio es **autónomo** y funciona sin depender de otros repositorios.
Puede importar TEI desde cualquier ruta local usando:

```
make copy-from-tei TEI_DIR=...
```

La trazabilidad se asegura con `MANIFEST.md` (sha256) y **no se usan symlinks**.
La procedencia del corpus se documenta en `01_data/tei/source/README.md` y en `01_data/tei/source/MANIFEST.md`.
No se asume ningún repositorio externo: el archivo TEI es un **archivo situado** que se integra a este flujo.

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

**Corpus TEI:** Dominio público (autores pre-1950)  
**Código y documentación:** MIT (libre atribución)

---

## 🛠️ Roadmap & Fases Completadas

**Fase 1-4 ✅ COMPLETE:** Etnographic auditing, rule-constrained sampling, state verification  
**Fase 5-6 ✅ COMPLETE:** Dual reading pack system (diverse 180/76, balanced 160/29)  
**Fase 7 ✅ COMPLETE:** Bug fixes + token rates analysis  
**Fase 8 ✅ COMPLETE:** End-to-end verification (make report executable)  
**Fase 9 ✅ COMPLETE:** Advanced DH visualizations (scatter, heatmap, violin, network, dashboard)  

**Próximas fases (en progreso):**
- [ ] Fase 10: Etnographic memo expansion (~30 memos curado)
- [ ] Contrapunto con docs IGE (emigración 1860-1950)
- [ ] Análisis de silencios (¿qué no aparece en literatura?)
- [ ] Mapas culturales (topónimos + densidades)
- [ ] Artículo metodológico + comunicación AIBR (Patrimonios, Cambio y Resistencias)

**Documentation:**
- [x] README.md (updated Phase 9)
- [x] CHANGELOG_PHASE9.md (detailed)
- [x] PHASE_9_EXECUTIVE_SUMMARY.md (user guide)
- [x] VISUALIZATIONS_README.md (technical)
- [x] Section 6b in REPORT.md (integration)

---

## 💬 Contacto y Contribuciones

**Autor:** [Tu Nombre]  
**Email:** tu@email.com  
**GitHub:** [@tu-usuario](https://github.com/tu-usuario)

**Contribuciones**: Bienvenidas vía issues/PRs. Este es un proyecto experimental y abierto a crítica metodológica.

---

## 🙏 Agradecimientos

- Corpus TEI: Biblioteca Virtual Miguel de Cervantes, Internet Archive
- Archivos históricos: IGE, Arquivo de Galicia, PARES
- Inspiración metodológica: Ted Underwood, Lauren Klein, Catherine D'Ignazio, Franco Moretti (con matices críticos)

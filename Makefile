# Makefile - Corpus Etnográfico Galicia
# Pipeline etnográfico: Literatura como artefacto cultural situado

.PHONY: help init check copy-from-tei tei-to-text tei-metadata build-cases sample cooc test audit-sampling log-run writeup-pack networks viz report-lite rankings reading-pack reading-pack-diverse reading-pack-balanced pack-report report-packs report-networks report-figures token-rates build report-summary viz-advanced viz-interactive viz-all report report-min report-by-author emigrant-module evidence-pack-emigrante evidence-pack-emigrante-v2tokens fix-tokens-full freeze freeze-lite clean-outputs clean status

# Python command
PYTHON := /opt/homebrew/bin/python3

# Directorio base
BASE_DIR := $(shell pwd)

# Python de venv (si existe)
VENV_PY := $(BASE_DIR)/.venv/bin/python

# Directorios clave (nueva estructura)
DATA_DIR := $(BASE_DIR)/01_data
METHODS_DIR := $(BASE_DIR)/02_methods
ANALYSIS_DIR := $(BASE_DIR)/03_analysis
OUTPUTS_DIR := $(BASE_DIR)/04_outputs

# Parámetros configurables
TEI_DIR ?= ../corpus-literario/tei
WINDOW ?= 40
SCENES_YAML ?= escenas_minimas_v2.yml

#==============================================================================
# HELP
#==============================================================================

help:
	@echo "================================================================"
	@echo "  CORPUS ETNOGRÁFICO GALICIA - Pipeline Etnográfico"
	@echo "================================================================"
	@echo ""
	@echo "Workflow completo:"
	@echo "  1. make copy-from-tei TEI_DIR=/path/to/tei/"
	@echo "  2. make tei-to-text"
	@echo "  2b. make tei-metadata"
	@echo "  3. make build-cases"
	@echo "  4. make sample"
	@echo "  5. make cooc WINDOW=40"
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@echo "  make init            - Inicializar estructura de proyecto"
	@echo "  make check           - Verificar estructura y dependencias"
	@echo "  make copy-from-tei   - Copiar corpus TEI con MANIFEST (requiere TEI_DIR=...)"
	@echo "  make tei-to-text     - Extraer texto plano de TEI → units.csv"
	@echo "  make tei-metadata    - Extraer autores canónicos desde TEI headers"
	@echo "  make build-cases     - Detectar casos/escenas (regex KWIC)"
	@echo "  make sample          - Muestrear casos estratificadamente"
	@echo "  make cooc            - Coocurrencias en ventanas (WINDOW=40)"
	@echo "  make test            - Ejecutar tests con pytest"
	@echo "  make audit-sampling  - Auditar sesgos del muestreo"
	@echo "  make log-run         - Registrar ejecucion en cuaderno metodologico"
	@echo "  make writeup-pack    - Generar paquete de escritura"
	@echo "  make networks             - Exportar redes para Gephi"
	@echo "  make viz                 - Generar figuras PNG"
	@echo "  make report-lite         - networks + viz"
	@echo "  make rankings            - Generar scene_summary.csv y case_rankings.csv"
	@echo "  make reading-pack-diverse    - Pack diverso (180 casos, 76 obras)"
	@echo "  make reading-pack-balanced   - Pack balanceado (160 casos, 10/escena)"
	@echo "  make pack-report             - Comparación diverso vs. balanceado"
	@echo "  make report-packs           - Generar ambos packs + reporte"
	@echo "  make report-networks        - Alias: exportar redes"
	@echo "  make report-figures         - Alias: generar figuras"
	@echo "  make viz-advanced           - Generar visualizaciones avanzadas (PNG/PDF)"
	@echo "  make viz-interactive        - Generar dashboards/redes interactivos (HTML)"
	@echo "  make viz-all                - Todo: avanzadas + interactivas"
	@echo "  make report-summary         - Generar REPORT.md + manifest + token rates"
	@echo "  make report                 - Pipeline completo (TEI→análisis→visualización→informes)"
	@echo "  make report                 - Pipeline completo (TEI→análisis→informes)"
	@echo "  make report-min             - rankings + reading-pack legado"
	@echo "  make emigrant-module        - Módulo representación del emigrante (tablas + pack)"
	@echo "  make evidence-pack-emigrante - PHASE 11: Evidence Pack (tablas+figuras+pack v2+informe)"
	@echo "  make evidence-pack-emigrante-v2tokens - Evidence Pack con denominadores fulltext (v2tokens)"
	@echo "  make fix-tokens-full        - BUGFIX: Corrigir tokens con fulltext TEI"
	@echo "  make freeze                 - Congelar outputs del análisis (05_freeze/) [requiere report completo]"
	@echo "  make freeze-lite            - Congelar outputs existentes (05_freeze/) [SIN regenerar]"
	@echo "  make clean-outputs          - Limpiar 04_outputs/ y tarjetas regenerables"
	@echo "  make status          - Ver estado del pipeline"
	@echo "  make clean           - Limpiar outputs intermedios"
	@echo ""
	@echo "Filosofía anti-positivista:"
	@echo "  • Literatura = artefacto cultural (NO fuente empírica directa)"
	@echo "  • Casos/escenas = heurísticas (NO datasets representativos)"
	@echo "  • Coocurrencias = tensiones narrativas (NO causalidad)"
	@echo "  • Output principal: memos etnográficos + casos (NO métricas)"
	@echo ""
	@echo "================================================================"
	@echo ""

#==============================================================================
# INICIALIZACIÓN
#==============================================================================


init:
	@echo "🚀 Inicializando estructura de proyecto..."
	@mkdir -p $(DATA_DIR)/tei/source $(DATA_DIR)/tei/derived $(DATA_DIR)/text $(DATA_DIR)/kwic_exports $(DATA_DIR)/external
	@mkdir -p $(METHODS_DIR)/patterns $(METHODS_DIR)/scripts_tei $(METHODS_DIR)/scripts_ethno $(METHODS_DIR)/tests
	@mkdir -p $(METHODS_DIR)/scripts_core $(METHODS_DIR)/scripts_experiments
	@mkdir -p $(ANALYSIS_DIR)/cases $(ANALYSIS_DIR)/memos
	@mkdir -p $(OUTPUTS_DIR)/tables $(OUTPUTS_DIR)/figures
	@mkdir -p 05_freeze 05_annotations
	@mkdir -p tools
	@echo "✓ Estructura creada"
	@echo ""

#==============================================================================
# VERIFICACIÓN
#==============================================================================

check:
	@echo "🔍 Verificando estructura del proyecto..."
	@echo ""
	@echo "1. Verificando directorios principales..."
	@test -d $(DATA_DIR) || (echo "❌ ERROR: 01_data/ no existe" && exit 1)
	@test -d $(METHODS_DIR) || (echo "❌ ERROR: 02_methods/ no existe" && exit 1)
	@test -d $(ANALYSIS_DIR) || (echo "❌ ERROR: 03_analysis/ no existe" && exit 1)
	@test -d $(OUTPUTS_DIR) || (echo "❌ ERROR: 04_outputs/ no existe" && exit 1)
	@echo "   ✓ Directorios principales OK"
	@echo ""
	@echo "2. Verificando scripts clave..."
	@test -f tools/copy_from_tei.py || (echo "⚠️  tools/copy_from_tei.py faltante (ejecutar: make init)" && exit 1)
	@echo "   ✓ tools/copy_from_tei.py OK"
	@echo ""
	@echo "3. Verificando dependencias Python..."
	@$(PYTHON) -c "import lxml" 2>/dev/null || (echo "❌ ERROR: lxml no instalado (pip install lxml)" && exit 1)
	@$(PYTHON) -c "import pandas" 2>/dev/null || (echo "❌ ERROR: pandas no instalado (pip install pandas)" && exit 1)
	@echo "   ✓ Dependencias Python OK (lxml, pandas)"
	@echo ""
	@echo "✅ Estructura del proyecto verificada correctamente"
	@echo ""

#==============================================================================
# PIPELINE ETNOGRÁFICO
#==============================================================================

# 1. COPIAR CORPUS TEI
copy-from-tei:
	@echo "📁 Copiando corpus TEI desde $(TEI_DIR)..."
	@echo ""
	@test -d $(TEI_DIR) || (echo "❌ ERROR: TEI_DIR no existe: $(TEI_DIR)" && \
		echo "Uso: make copy-from-tei TEI_DIR=/ruta/corpus-literario/tei/" && exit 1)
	$(PYTHON) tools/copy_from_tei.py --source $(TEI_DIR) --output $(DATA_DIR)/tei/source
	@echo ""
	@echo "✅ Corpus TEI copiado con MANIFEST"
	@echo "   Ver: $(DATA_DIR)/tei/source/MANIFEST.md"
	@echo ""

# 2. EXTRAER TEXTO DE TEI
tei-to-text:
	@echo "📄 Extrayendo texto plano de TEI..."
	@echo ""
	@test -d $(DATA_DIR)/tei/source || (echo "❌ ERROR: Ejecuta primero 'make copy-from-tei'" && exit 1)
	@if [ ! -f $(METHODS_DIR)/scripts_tei/tei_to_text.py ]; then \
		echo "⚠️  Script tei_to_text.py aún no creado (PROMPT 3)"; \
		echo "   Por ahora, usa: scripts/extraer_texto_tei.py (versión antigua)"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_tei/tei_to_text.py \
		--input $(DATA_DIR)/tei/source \
		--output $(DATA_DIR)/text/units.csv
	@echo ""
	@echo "✅ Texto extraído: $(DATA_DIR)/text/units.csv"
	@echo ""

# 2b. EXTRAER METADATA DE TEI (Autores canónicos + Normalización)
tei-metadata:
	@echo "📚 Extrayendo metadata de autores desde TEI headers (v2: extendida)..."
	@echo ""
	@test -d $(DATA_DIR)/tei/source || (echo "❌ ERROR: Ejecuta primero 'make copy-from-tei'" && exit 1)
	$(PYTHON) $(METHODS_DIR)/scripts_metadata/extract_tei_metadata_v2.py \
		--tei-dir $(DATA_DIR)/tei/source \
		--output $(OUTPUTS_DIR)/tables/works_metadata_from_tei.csv \
		--normalization $(METHODS_DIR)/patterns/author_normalization.yml
	@echo ""
	@echo "✅ Metadata de autores: $(OUTPUTS_DIR)/tables/works_metadata_from_tei.csv"
	@echo "✅ Con columnas: author_raw, author_normalized, author_norm_key"
	@echo "✅ Transparencia: author_confidence, why_missing"
	@echo ""

# 3. DETECTAR CASOS/ESCENAS
build-cases:
	@echo "🔍 Detectando casos/escenas mediante regex KWIC..."
	@echo ""
	@test -f $(DATA_DIR)/text/units.csv || (echo "❌ ERROR: Ejecuta primero 'make tei-to-text'" && exit 1)
	@if [ ! -f $(METHODS_DIR)/scripts_ethno/build_kwic_cases.py ]; then \
		echo "⚠️  Script build_kwic_cases.py aún no creado (PROMPT 3)"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_ethno/build_kwic_cases.py \
		--units $(DATA_DIR)/text/units.csv \
		--scene-yaml $(METHODS_DIR)/patterns/$(SCENES_YAML) \
		--output $(DATA_DIR)/kwic_exports/cases_raw.csv
	@echo ""
	@echo "✅ Casos detectados: $(DATA_DIR)/kwic_exports/cases_raw.csv"
	@echo ""

# 4. MUESTREAR CASOS ESTRATIFICADAMENTE
sample:
	@echo "🎯 Muestreando casos para lectura etnográfica..."
	@echo ""
	@test -f $(DATA_DIR)/kwic_exports/cases_raw.csv || (echo "❌ ERROR: Ejecuta primero 'make build-cases'" && exit 1)
	@if [ ! -f $(METHODS_DIR)/scripts_ethno/sampling_by_profile.py ]; then \
		echo "⚠️  Script sampling_by_profile.py aún no creado (PROMPT 3)"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_ethno/sampling_by_profile.py \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--output_csv $(ANALYSIS_DIR)/cases/cases_sampled.csv \
		--output_dir $(ANALYSIS_DIR)/cases \
		$$( [ -n "$(RULES)" ] && echo "--rules $(RULES)" )
	@echo ""
	@echo "✅ Casos muestreados:"
	@echo "   • CSV: $(ANALYSIS_DIR)/cases/cases_sampled.csv"
	@echo "   • Markdowns: $(ANALYSIS_DIR)/cases/{case_id}.md"
	@echo ""

# 5. COOCURRENCIAS EN VENTANAS (tensión, NO causalidad)
cooc:
	@echo "🕸️  Calculando coocurrencias en ventanas (WINDOW=$(WINDOW) tokens)..."
	@echo ""
	@test -f $(DATA_DIR)/text/units.csv || (echo "❌ ERROR: Ejecuta primero 'make tei-to-text'" && exit 1)
	@if [ ! -f $(METHODS_DIR)/scripts_ethno/cooc_scene_windows.py ]; then \
		echo "⚠️  Script cooc_scene_windows.py aún no creado (PROMPT 4)"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_ethno/cooc_scene_windows.py \
		--input $(DATA_DIR)/text/units.csv \
		--patterns $(METHODS_DIR)/patterns/escenas_minimas.yml \
		--window $(WINDOW) \
		--output $(OUTPUTS_DIR)/tables/cooc_pairs.csv
	@echo ""
	@echo "✅ Coocurrencias calculadas: $(OUTPUTS_DIR)/tables/cooc_pairs.csv"
	@echo "   (Recordatorio: Coocurrencia ≠ causalidad; señala densidad narrativa)"
	@echo ""

# 6. TESTS
test:
	@echo "🧪 Ejecutando tests con pytest..."
	@echo ""
	@if [ -x $(VENV_PY) ]; then \
		$(VENV_PY) -m pytest 02_methods/tests; \
	else \
		$(PYTHON) -m pytest 02_methods/tests; \
	fi
	@echo ""

# 7. AUDITORIA DE MUESTREO
audit-sampling:
	@echo "🔎 Auditando sesgos del muestreo..."
	@echo ""
	@test -f $(DATA_DIR)/kwic_exports/cases_raw.csv || (echo "❌ ERROR: Ejecuta primero 'make build-cases'" && exit 1)
	@test -f $(ANALYSIS_DIR)/cases/cases_sampled.csv || (echo "❌ ERROR: Ejecuta primero 'make sample'" && exit 1)
	$(PYTHON) $(METHODS_DIR)/scripts_ethno/audit_sampling.py \
		--cases_raw $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--cases_sampled $(ANALYSIS_DIR)/cases/cases_sampled.csv \
		--output_csv $(OUTPUTS_DIR)/tables/sampling_audit.csv \
		--output_md $(OUTPUTS_DIR)/tables/sampling_audit.md
	@echo ""
	@echo "✅ Auditoria generada: $(OUTPUTS_DIR)/tables/sampling_audit.csv"
	@echo "✅ Informe breve: $(OUTPUTS_DIR)/tables/sampling_audit.md"
	@echo ""

# 8. LOG DE EJECUCION
log-run:
	@echo "📝 Registrando ejecucion en cuaderno metodologico..."
	@echo ""
	$(PYTHON) tools/log_run.py
	@echo "✅ Cuaderno actualizado: 00_docs/02_cuaderno_decisiones_metodologicas.md"
	@echo ""

# 9. PAQUETE DE ESCRITURA
writeup-pack:
	@echo "🧾 Generando paquete de escritura..."
	@echo ""
	@if [ ! -f tools/_gen_docs_package.py ]; then \
		echo "❌ ERROR: tools/_gen_docs_package.py no existe"; \
		exit 1; \
	fi
	$(PYTHON) tools/_gen_docs_package.py
	@echo "✅ Paquete de escritura actualizado"
	@echo ""

# 10. REDES PARA GEPHI
networks:
	@echo "🕸️  Exportando redes para Gephi..."
	@echo ""
	@if [ ! -f $(METHODS_DIR)/scripts_networks/export_networks.py ]; then \
		echo "❌ ERROR: export_networks.py no existe"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_networks/export_networks.py \
		--cooc $(OUTPUTS_DIR)/tables/cooc_pairs.csv \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--outdir $(OUTPUTS_DIR)/networks
	@echo "✅ Redes exportadas"
	@echo ""

# 11. FIGURAS PNG
viz:
	@echo "📊 Generando figuras PNG..."
	@echo ""
	@if [ ! -f $(METHODS_DIR)/scripts_viz/make_figures.py ]; then \
		echo "❌ ERROR: make_figures.py no existe"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_viz/make_figures.py \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--cooc $(OUTPUTS_DIR)/tables/cooc_pairs.csv \
		--outdir $(OUTPUTS_DIR)/figures
	@echo "✅ Figuras generadas"
	@echo ""

# 12. REPORTE LIGERO
report-lite: networks viz

# 13. RANKING ETNOGRÁFICO
rankings:
	@echo "🏆 Generando ranking etnográfico de casos..."
	@echo ""
	@if [ ! -f $(METHODS_DIR)/scripts_ethno/scene_salience.py ]; then \
		echo "❌ ERROR: scene_salience.py no existe"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_ethno/scene_salience.py \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--units $(DATA_DIR)/text/units.csv \
		--outdir $(OUTPUTS_DIR)/tables
	@echo "✅ Rankings generados"
	@echo ""

# 14. READING PACK (160 CASOS)
reading-pack: rankings
	@echo "📚 Seleccionando reading pack estratificado..."
	@echo ""
	@if [ ! -f $(METHODS_DIR)/scripts_ethno/select_reading_pack.py ]; then \
		echo "❌ ERROR: select_reading_pack.py no existe"; \
		exit 1; \
	fi
	@if [ ! -f $(METHODS_DIR)/patterns/reading_pack_rules.yml ]; then \
		echo "❌ ERROR: reading_pack_rules.yml no existe"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_ethno/select_reading_pack.py \
		--rankings $(OUTPUTS_DIR)/tables/case_rankings.csv \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--rules $(METHODS_DIR)/patterns/reading_pack_rules.yml \
		--outdir $(ANALYSIS_DIR)/reading_pack
	@echo "✅ Reading pack generado"
	@echo ""

# 14B. READING PACK DIVERSE
reading-pack-diverse: rankings
	@echo "📚 Seleccionando reading pack DIVERSO (máx obras)..."
	@echo ""
	$(PYTHON) $(METHODS_DIR)/scripts_ethno/select_reading_pack.py \
		--rankings $(OUTPUTS_DIR)/tables/case_rankings.csv \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--rules $(METHODS_DIR)/patterns/reading_pack_rules.yml \
		--outdir $(ANALYSIS_DIR)/reading_pack/diverse
	@echo "✅ Reading pack diverso generado"
	@echo ""

# 14C. READING PACK BALANCED
reading-pack-balanced: rankings
	@echo "📊 Seleccionando reading pack BALANCEADO (10 casos/escena)..."
	@echo ""
	@if [ ! -f $(METHODS_DIR)/scripts_ethno/select_balanced_pack.py ]; then \
		echo "❌ ERROR: select_balanced_pack.py no existe"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_ethno/select_balanced_pack.py \
		--rankings $(OUTPUTS_DIR)/tables/case_rankings.csv \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--outdir $(ANALYSIS_DIR)/reading_pack/balanced
	@echo "✅ Reading pack balanceado generado"
	@echo ""

# 14D. REPORTE COMPARATIVO DE PACKS
pack-report: reading-pack-diverse reading-pack-balanced
	@echo "📊 Generando reporte comparativo de packs..."
	@echo ""
	@if [ ! -f $(METHODS_DIR)/scripts_ethno/pack_report.py ]; then \
		echo "❌ ERROR: pack_report.py no existe"; \
		exit 1; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_ethno/pack_report.py \
		--diverse $(ANALYSIS_DIR)/reading_pack/diverse/reading_pack_diverse.csv \
		--balanced $(ANALYSIS_DIR)/reading_pack/balanced/reading_pack_balanced.csv \
		--outdir $(OUTPUTS_DIR)/tables
	@echo "✅ Reporte de packs generado"
	@echo ""

# 14E. AMBOS PACKS + REPORTE
report-packs: pack-report

# 14E'. ALIASES PARA REPORT
report-networks: networks
report-figures: viz

# 14F. TARGET BUILD (Pipeline básico robusto end-to-end)
build: tei-to-text tei-metadata build-cases rankings cooc reading-pack-diverse reading-pack-balanced report-networks report-figures
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "✅ BUILD END-TO-END COMPLETADO (inputs listos para report)"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📊 Artefactos generados:"
	@echo "   📄 Texto extraído: 01_data/text/units.csv"
	@echo "   🔍 Casos detectados: 01_data/kwic_exports/cases_raw.csv"
	@echo "   🏆 Rankings: 04_outputs/tables/scene_summary.csv"
	@echo "   📦 Reading pack diverso: 03_analysis/reading_pack/diverse/"
	@echo "   📦 Reading pack balanceado: 03_analysis/reading_pack/balanced/"
	@echo "   🕸️  Redes: 04_outputs/networks/"
	@echo "   📊 Figuras: 04_outputs/figures/"
	@echo ""
	@echo "Próximo: make report-summary (genera reports finales)"
	@echo ""

# 15. REPORTE RESUMEN (BUILD_REPORT + MANIFEST + TOKEN_RATES) - CON GUARDS
report-summary: build
	@echo "📋 Generando reporte resumen, manifest y token rates..."
	@echo ""
	@echo "[Guard 1/2] Verificando reading packs..."
	@if [ ! -f $(ANALYSIS_DIR)/reading_pack/diverse/reading_pack_diverse.csv ]; then \
		echo "⚠️  Reading pack diverso faltante. Regenerando..."; \
		$(MAKE) reading-pack-diverse; \
	fi
	@if [ ! -f $(ANALYSIS_DIR)/reading_pack/balanced/reading_pack_balanced.csv ]; then \
		echo "⚠️  Reading pack balanceado faltante. Regenerando..."; \
		$(MAKE) reading-pack-balanced; \
	fi
	@echo "✓ Reading packs verificados"
	@echo ""
	@echo "[Guard 2/2] Verificando scripts base..."
	@if [ ! -f $(METHODS_DIR)/scripts_core/build_report.py ]; then \
		echo "❌ ERROR: build_report.py no existe"; \
		exit 1; \
	fi
	@if [ ! -f tools/build_manifest.py ]; then \
		echo "❌ ERROR: tools/build_manifest.py no existe"; \
		exit 1; \
	fi
	@if [ ! -f $(METHODS_DIR)/scripts_core/token_rates.py ]; then \
		echo "❌ ERROR: token_rates.py no existe"; \
		exit 1; \
	fi
	@if [ ! -f $(OUTPUTS_DIR)/tables/scene_summary.csv ]; then \
		echo "❌ ERROR: scene_summary.csv no existe "; \
		exit 1; \
	fi
	@echo "✓ Scripts y tablas verificados"
	@echo ""
	@echo "[1/2] Computando token rates..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/token_rates.py \
		--units 01_data/text/units.csv \
		--scene-summary $(OUTPUTS_DIR)/tables/scene_summary.csv \
		--outdir $(OUTPUTS_DIR)/tables
	@echo ""
	@echo "[2/2] Generando reporte final..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/build_report.py \
		--cases-raw $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--scene-summary $(OUTPUTS_DIR)/tables/scene_summary.csv \
		--case-rankings $(OUTPUTS_DIR)/tables/case_rankings.csv \
		--diverse-pack $(ANALYSIS_DIR)/reading_pack/diverse/reading_pack_diverse.csv \
		--balanced-pack $(ANALYSIS_DIR)/reading_pack/balanced/reading_pack_balanced.csv \
		--cooc-pairs $(OUTPUTS_DIR)/tables/cooc_pairs.csv \
		--pack-report $(OUTPUTS_DIR)/tables/pack_report.md \
		--sampling-audit $(OUTPUTS_DIR)/tables/sampling_audit.md \
		--rules $(METHODS_DIR)/patterns/reading_pack_rules.yml \
		--outdir $(OUTPUTS_DIR)/reports
	@echo ""
	$(PYTHON) tools/build_manifest.py \
		--outputs-dir 04_outputs \
		--patterns-dir 02_methods/patterns \
		--manifest-dir $(OUTPUTS_DIR)/manifests
	@echo "✅ Reporte, token rates y manifest generados"
	@echo ""

# 15B. TOKEN RATES
token-rates:
	@echo "📊 Computando token rates..."
	@echo ""
	$(PYTHON) $(METHODS_DIR)/scripts_core/token_rates.py \
		--units 01_data/text/units.csv \
		--scene-summary $(OUTPUTS_DIR)/tables/scene_summary.csv \
		--outdir $(OUTPUTS_DIR)/tables
	@echo "✅ Token rates computados"
	@echo ""

# 15B. VISUALIZACIONES AVANZADAS (SCATTER, HEATMAP, VIOLIN, NETWORK PNG)
viz-advanced:
	@echo "📊 Generando visualizaciones avanzadas (estáticas PNG/PDF 300 DPI)..."
	@echo ""
	@mkdir -p $(OUTPUTS_DIR)/figures/static
	@if [ ! -f $(OUTPUTS_DIR)/tables/scene_summary.csv ]; then \
		echo "❌ ERROR: scene_summary.csv no existe. Ejecuta: make rankings"; \
		exit 1; \
	fi
	@echo "→ Scatter: coverage vs concentration"
	$(PYTHON) $(METHODS_DIR)/scripts_viz/fig_scene_scatter.py \
		--scene-summary $(OUTPUTS_DIR)/tables/scene_summary.csv \
		--outdir $(OUTPUTS_DIR)/figures/static \
		--dpi 300
	@echo ""
	@echo "→ Heatmap: escena × obra (top 40)"
	$(PYTHON) $(METHODS_DIR)/scripts_viz/fig_scene_heatmap.py \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--scene-summary $(OUTPUTS_DIR)/tables/scene_summary.csv \
		--token-totals $(OUTPUTS_DIR)/tables/token_totals.csv \
		--outdir $(OUTPUTS_DIR)/figures/static \
		--dpi 300
	@echo ""
	@echo "→ Violin: distribuciones de tasas por escena"
	$(PYTHON) $(METHODS_DIR)/scripts_viz/fig_scene_rates_distribution.py \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--token-totals $(OUTPUTS_DIR)/tables/token_totals.csv \
		--outdir $(OUTPUTS_DIR)/figures/static \
		--dpi 300
	@echo ""
	@echo "→ Red de coocurrencias: términos filtrados (min_cooc≥20, PNG)"
	$(PYTHON) $(METHODS_DIR)/scripts_viz/fig_cooc_network_filtered.py \
		--cooc-pairs $(OUTPUTS_DIR)/tables/cooc_pairs.csv \
		--outdir $(OUTPUTS_DIR)/figures/static \
		--dpi 300
	@echo ""
	@echo "→ Ranking de tasas: top 10 escenas por densidad de casos"
	$(PYTHON) $(METHODS_DIR)/scripts_viz/fig_scene_rates_per_1k_tokens.py \
		--rates-csv $(OUTPUTS_DIR)/tables/scene_rates_per_1k_tokens.csv \
		--outdir $(OUTPUTS_DIR)/figures/static \
		--dpi 300
	@echo ""
	@echo "✅ Visualizaciones avanzadas generadas (300 DPI)"
	@echo ""

# 15C. DASHBOARDS INTERACTIVOS (HTML)
viz-interactive:
	@echo "🌐 Generando dashboards interactivos (HTML)..."
	@echo ""
	@mkdir -p $(OUTPUTS_DIR)/figures/interactive
	@if [ ! -d $(ANALYSIS_DIR)/reading_pack ]; then \
		echo "❌ ERROR: reading_pack no existe. Ejecuta: make reading-pack-diverse"; \
		exit 1; \
	fi
	@echo "→ Dashboard de casos: filtro, ordenamiento, visualización"
	$(PYTHON) $(METHODS_DIR)/scripts_viz/dashboard_cases.html.py \
		--packs-dir $(ANALYSIS_DIR)/reading_pack \
		--outdir $(OUTPUTS_DIR)/figures/interactive
	@echo ""
	@echo "→ Red de coocurrencias interactiva (pyvis)"
	$(PYTHON) $(METHODS_DIR)/scripts_viz/fig_cooc_network_filtered.py \
		--cooc-pairs $(OUTPUTS_DIR)/tables/cooc_pairs.csv \
		--outdir $(OUTPUTS_DIR)/figures/interactive
	@echo ""
	@echo "✅ Dashboards interactivos generados"
	@echo ""

# 15D. TODAS LAS VISUALIZACIONES
viz-all: viz-advanced viz-interactive
	@echo "✅ Todas las visualizaciones generadas (estáticas e interactivas)"
	@echo ""

# 15E. PIPELINE COMPLETO (REPORT) - REQUIERE copy-from-tei manual
report: build report-summary
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo "✅ PIPELINE ETNOGRÁFICO COMPLETO"
	@echo "═══════════════════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📊 Outputs generados:"
	@echo "   📋 Informe principal: 04_outputs/reports/REPORT.md"
	@echo "   📦 Manifest de artefactos: 04_outputs/manifests/ARTIFACTS_MANIFEST.csv"
	@echo "   📚 Packs: 03_analysis/reading_pack/{diverse,balanced}/"
	@echo "   🕸️  Redes: 04_outputs/networks/"
	@echo "   📊 Figuras: 04_outputs/figures/"
	@echo "   🏆 Rankings: 04_outputs/tables/scene_summary.csv"
	@echo ""
	@echo "🎯 Próximo paso: Editar informe y escribir etnografía"
	@echo ""

# 16. REPORTE MÍNIMO (RANKING + READING PACK original)
report-min: rankings reading-pack

# 17. REPORTES POR AUTOR (FASE 10 - REFACTORED: NORMALIZACIÓN + TRAZABILIDAD)
report-by-author: tei-metadata
	@echo "📚 Generando reportes individuales por autor (v3: normalizado)..."
	@echo ""
	@test -f $(DATA_DIR)/kwic_exports/cases_raw.csv || (echo "❌ ERROR: Ejecuta primero 'make build-cases'" && exit 1)
	@test -f $(DATA_DIR)/text/units.csv || (echo "❌ ERROR: units.csv no encontrado" && exit 1)
	@test -f $(OUTPUTS_DIR)/tables/works_metadata_from_tei.csv || (echo "❌ ERROR: Ejecuta primero 'make tei-metadata'" && exit 1)
	$(PYTHON) $(METHODS_DIR)/scripts_core/report_by_author_v3.py \
		--cases $(DATA_DIR)/kwic_exports/cases_raw.csv \
		--units $(DATA_DIR)/text/units.csv \
		--works-metadata $(OUTPUTS_DIR)/tables/works_metadata_from_tei.csv \
		--cooc $(OUTPUTS_DIR)/tables/cooc_pairs.csv \
		--output $(OUTPUTS_DIR)/reports/by_author
	@echo ""
	@echo "✅ Reportes por autor generados en: $(OUTPUTS_DIR)/reports/by_author/"
	@echo "✅ Agrupados por author_normalized (forma canónica)"
	@echo "✅ INDEX disponible en: $(OUTPUTS_DIR)/reports/by_author/INDEX.md"
	@echo ""

# 18. MÓDULO REPRESENTACIÓN DEL EMIGRANTE
emigrant-module: tei-metadata token-rates
	@echo "🌍 Generando módulo representación del emigrante..."
	@echo ""
	@test -f $(DATA_DIR)/text/units.csv || (echo "❌ ERROR: Ejecuta primero 'make tei-to-text'" && exit 1)
	@test -f $(OUTPUTS_DIR)/tables/works_metadata_from_tei.csv || (echo "❌ ERROR: Ejecuta primero 'make tei-metadata'" && exit 1)
	$(PYTHON) $(METHODS_DIR)/scripts_core/emigrant_markers_kwic.py \
		--units $(DATA_DIR)/text/units.csv \
		--token-totals $(OUTPUTS_DIR)/tables/token_totals.csv \
		--works-metadata $(OUTPUTS_DIR)/tables/works_metadata_from_tei.csv \
		--markers $(METHODS_DIR)/patterns/emigrante_markers.yml \
		--outdir $(OUTPUTS_DIR)/tables
	@echo ""
	$(PYTHON) $(METHODS_DIR)/scripts_core/select_emigrant_rep_pack.py \
		--mentions $(OUTPUTS_DIR)/tables/emigrant_mentions_by_work.csv \
		--kwic $(OUTPUTS_DIR)/tables/emigrant_kwic_cases.csv \
		--works-metadata $(OUTPUTS_DIR)/tables/works_metadata_from_tei.csv \
		--outdir $(ANALYSIS_DIR)/reading_pack
	@echo "✅ Módulo emigrante generado"
	@echo ""

# 18B. EVIDENCE PACK EMIGRANTE (Fase 11)
evidence-pack-emigrante: tei-metadata token-rates emigrant-module
	@echo "📚 Generando EVIDENCE PACK: Etnografía Digital Computerizada Fase 11..."
	@echo ""
	@echo "[1/4] Enriquecimiento de metadatos con year/decade..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/enrich_with_metadata.py
	@echo ""
	@echo "[2/4] Generando tablas de síntesis (por autor/década/formato)..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/generate_summary_tables.py
	@echo ""
	@echo "[3/4] Generando figuras estáticas (PNG+PDF)..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/generate_evidence_figures.py
	@echo ""
	@echo "[4/4] Actualizando pack v2 con validación y fichas..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/update_emigrant_pack_v2.py
	@echo ""
	@echo "✅ EVIDENCE PACK generado completamente"
	@echo ""
	@echo "Archivos generados:"
	@echo "  Tablas: corpus_master_table.csv, emigrant_by_author.csv, emigrant_by_decade.csv, emigrant_by_format.csv"
	@echo "  Figuras: fig_emigrant_by_author_top15.{png,pdf}, fig_emigrant_by_decade.{png,pdf},"
	@echo "           fig_emigrant_by_format.{png,pdf}, fig_emigrant_markers_top20.{png,pdf}"
	@echo "  Pack: emigrante_representation_pack_v2.csv + 180 fichas MD de anotación"
	@echo "  Informe: EVIDENCE_PACK_EMIGRANTE.md (secciones: corpus, autor, época, formato, pack, codificación)"
	@echo ""
	@echo "Próximo paso: make freeze-lite (para crear v1.0.1-lite del baseline)"
	@echo ""

# 18C. EVIDENCE PACK EMIGRANTE (v2tokens)
evidence-pack-emigrante-v2tokens: fix-tokens-full
	@echo "📚 Generando EVIDENCE PACK v2tokens (fulltext TEI denominators)..."
	@echo ""
	@echo "[Guard] Verificando tablas v2tokens generadas por fix-tokens-full..."
	@if [ ! -f $(OUTPUTS_DIR)/tables/corpus_master_table_v2tokens.csv ]; then \
		echo "❌ ERROR: corpus_master_table_v2tokens.csv no existe"; \
		exit 1; \
	fi
	@echo "✓ corpus_master_table_v2tokens.csv verificado"
	@echo ""
	@echo "[1/4] Generando tablas de síntesis v2tokens (autor/década/formato)..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/generate_summary_tables.py \
		--master-table $(OUTPUTS_DIR)/tables/corpus_master_table_v2tokens.csv \
		--output-suffix v2tokens
	@echo ""
	@echo "[2/4] Generando figuras estáticas (PNG+PDF) desde v2tokens..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/generate_evidence_figures.py \
		--tables-suffix v2tokens
	@echo ""
	@echo "[3/4] Actualizando pack v2 con master v2tokens..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/update_emigrant_pack_v2.py \
		--master-table $(OUTPUTS_DIR)/tables/corpus_master_table_v2tokens.csv
	@echo ""
	@echo "[4/4] Generando informe evidence pack (v2tokens)..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/generate_evidence_report.py \
		--master-table $(OUTPUTS_DIR)/tables/corpus_master_table_v2tokens.csv \
		--by-author $(OUTPUTS_DIR)/tables/emigrant_by_author_v2tokens.csv \
		--by-decade $(OUTPUTS_DIR)/tables/emigrant_by_decade_v2tokens.csv \
		--by-format $(OUTPUTS_DIR)/tables/emigrant_by_format_v2tokens.csv
	@echo ""
	@echo "✅ EVIDENCE PACK v2tokens generado completamente"
	@echo ""
	@echo "Archivos generados:"
	@echo "  Tablas v2tokens: corpus_master_table_v2tokens.csv, emigrant_by_*_v2tokens.csv"
	@echo "  Figuras: fig_emigrant_by_*_v2tokens.{png,pdf}"
	@echo "  Pack: emigrante_representation_pack_v2.csv (con validaciones)"
	@echo "  Informe: EVIDENCE_PACK_EMIGRANTE_v2tokens.md (8 secciones con denominadores v2tokens)"
	@echo ""
	@echo "Próximo: make freeze-lite (congelar artefactos finales)"
	@echo ""

# 19. CONGELAR ANÁLISIS (FREEZE)
freeze: report
	@echo "🧊 Congelando outputs del análisis..."
	@echo ""
	@version=$${VERSION:-$$(cat VERSION_ANALISIS.txt)}; \
	freeze_dir=$(BASE_DIR)/05_freeze/$$version; \
	mkdir -p $$freeze_dir; \
	rm -f $$freeze_dir/MANIFEST_SHA256.txt; \
	cp -R $(OUTPUTS_DIR)/reports $$freeze_dir/; \
	cp -R $(OUTPUTS_DIR)/tables $$freeze_dir/; \
	cp -R $(OUTPUTS_DIR)/figures $$freeze_dir/; \
	cp -R $(OUTPUTS_DIR)/networks $$freeze_dir/; \
	mkdir -p $$freeze_dir/03_analysis; \
	cp -R $(ANALYSIS_DIR)/reading_pack $$freeze_dir/03_analysis/; \
	cd $$freeze_dir && find . -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > MANIFEST_SHA256.txt; \
	commit=$$(git rev-parse HEAD 2>/dev/null || echo "no-git"); \
	timestamp=$$(date "+%Y-%m-%d %H:%M:%S"); \
	echo "# Freeze Notes" > $$freeze_dir/FREEZE_NOTES.md; \
	echo "" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "- Timestamp: $$timestamp" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "- Version: $$version" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "- Git commit: $$commit" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "## Config" >> $$freeze_dir/FREEZE_NOTES.md; \
	cat $(BASE_DIR)/CONFIG_ANALISIS.yml >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "" >> $$freeze_dir/FREEZE_NOTES.md
	@echo "✅ Freeze creado en: 05_freeze/$$(cat VERSION_ANALISIS.txt)/"
	@echo ""

# 19B. CONGELAR ANÁLISIS (SOLO OUTPUTS EXISTENTES - SIN DEPENDENCIAS)
freeze-lite:
	@echo "🧊 Congelando freeze-lite (solo artefactos finales)..."
	@echo ""
	@version=$${VERSION:-$$(cat VERSION_ANALISIS.txt)}; \
	if echo "$$version" | grep -q -- "-lite$$"; then \
		freeze_dir=$(BASE_DIR)/05_freeze/$$version; \
	else \
		freeze_dir=$(BASE_DIR)/05_freeze/$$version-lite; \
	fi; \
	mkdir -p $$freeze_dir/reports $$freeze_dir/tables $$freeze_dir/figures/static $$freeze_dir/manifests; \
	rm -f $$freeze_dir/manifests/MANIFEST_SHA256.txt; \
	[ -f $(OUTPUTS_DIR)/reports/REPORT.md ] && cp $(OUTPUTS_DIR)/reports/REPORT.md $$freeze_dir/reports/ || true; \
	[ -f $(OUTPUTS_DIR)/reports/EVIDENCE_PACK_EMIGRANTE.md ] && cp $(OUTPUTS_DIR)/reports/EVIDENCE_PACK_EMIGRANTE.md $$freeze_dir/reports/ || true; \
	[ -f $(OUTPUTS_DIR)/tables/corpus_master_table_v2tokens.csv ] && cp $(OUTPUTS_DIR)/tables/corpus_master_table_v2tokens.csv $$freeze_dir/tables/ || true; \
	[ -f $(OUTPUTS_DIR)/tables/emigrant_by_author_v2tokens.csv ] && cp $(OUTPUTS_DIR)/tables/emigrant_by_author_v2tokens.csv $$freeze_dir/tables/ || true; \
	[ -f $(OUTPUTS_DIR)/tables/emigrant_by_decade_v2tokens.csv ] && cp $(OUTPUTS_DIR)/tables/emigrant_by_decade_v2tokens.csv $$freeze_dir/tables/ || true; \
	[ -f $(OUTPUTS_DIR)/tables/emigrant_by_format_v2tokens.csv ] && cp $(OUTPUTS_DIR)/tables/emigrant_by_format_v2tokens.csv $$freeze_dir/tables/ || true; \
	[ -f $(OUTPUTS_DIR)/tables/author_scene_matrix_rates.csv ] && cp $(OUTPUTS_DIR)/tables/author_scene_matrix_rates.csv $$freeze_dir/tables/ || true; \
	[ -f $(OUTPUTS_DIR)/tables/work_tokens_full.csv ] && cp $(OUTPUTS_DIR)/tables/work_tokens_full.csv $$freeze_dir/tables/ || true; \
	[ -f $(OUTPUTS_DIR)/tables/token_mismatch_audit.csv ] && cp $(OUTPUTS_DIR)/tables/token_mismatch_audit.csv $$freeze_dir/tables/ || true; \
	[ -d $(OUTPUTS_DIR)/figures/static ] && cp -R $(OUTPUTS_DIR)/figures/static $$freeze_dir/figures/ || true; \
	cd $$freeze_dir && find reports tables figures -type f -print0 | LC_ALL=C sort -z | xargs -0 shasum -a 256 > manifests/MANIFEST_SHA256.txt; \
	awk '{print $$2","$$1}' $$freeze_dir/manifests/MANIFEST_SHA256.txt > $$freeze_dir/manifests/ARTIFACTS_MANIFEST.csv; \
	awk 'BEGIN{print "| path | sha256 |"; print "|---|---|"} {print "| "$$2" | "$$1" |"}' $$freeze_dir/manifests/MANIFEST_SHA256.txt > $$freeze_dir/manifests/ARTIFACTS_MANIFEST.md; \
	commit=$$(git rev-parse HEAD 2>/dev/null || echo "no-git"); \
	timestamp=$$(date "+%Y-%m-%d %H:%M:%S"); \
	echo "# Freeze Notes (lite)" > $$freeze_dir/FREEZE_NOTES.md; \
	echo "" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "- Timestamp: $$timestamp" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "- Version: $$version" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "- Git commit: $$commit" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "## Commands" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "- make fix-tokens-full" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "- make evidence-pack-emigrante" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "- make freeze-lite" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "" >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "## Config" >> $$freeze_dir/FREEZE_NOTES.md; \
	cat $(BASE_DIR)/CONFIG_ANALISIS.yml >> $$freeze_dir/FREEZE_NOTES.md; \
	echo "" >> $$freeze_dir/FREEZE_NOTES.md
	@echo "✅ Freeze-lite creado en: $$freeze_dir/"
	@echo ""

# 20. BUGFIX: Corregir tokenización (usar tokens_full en lugar de tokens_snippet)
fix-tokens-full: emigrant-module
	@echo "🔧 BUGFIX TOKENS: Corrigiendo denominadores con tokens_full..."
	@echo ""
	@test -d $(DATA_DIR)/tei/source || (echo "❌ ERROR: No hay TEI en 01_data/tei/source/ (ejecuta: make copy-from-tei TEI_DIR=...)" && exit 1)
	@echo "[1/2] Extrayendo tokens desde TEI completo (no snippets)..."
	$(PYTHON) $(METHODS_DIR)/scripts_core/compute_work_tokens_full.py
	@echo ""
	@echo "[2/2] Reconstruyendo tablas master con tokens_full..."
	@mkdir -p $(OUTPUTS_DIR)/tables
	@if [ ! -f $(OUTPUTS_DIR)/tables/corpus_master_table.csv ]; then \
		echo "⚠️  corpus_master_table.csv faltante. Regenerando desde evidence-pack..."; \
		$(PYTHON) $(METHODS_DIR)/scripts_core/emigrant_markers_kwic.py \
			--units $(DATA_DIR)/text/units.csv \
			--token-totals $(OUTPUTS_DIR)/tables/token_totals.csv \
			--works-metadata $(OUTPUTS_DIR)/tables/works_metadata_from_tei.csv \
			--markers $(METHODS_DIR)/patterns/emigrante_markers.yml \
			--outdir $(OUTPUTS_DIR)/tables; \
	fi
	$(PYTHON) $(METHODS_DIR)/scripts_core/rebuild_master_with_full_tokens.py
	@echo ""
	@echo "✅ BUGFIX completado"
	@echo ""
	@echo "Nuevas tablas (v2tokens):"
	@echo "  - corpus_master_table_v2tokens.csv"
	@echo "  - emigrant_by_author_v2tokens.csv"
	@echo "  - emigrant_by_decade_v2tokens.csv"
	@echo "  - emigrant_by_format_v2tokens.csv"
	@echo ""
	@echo "Próximo: make evidence-pack-emigrante-v2tokens"
	@echo ""

# 20. LIMPIEZA DE OUTPUTS (SIN TOCAR FREEZE)
clean-outputs:
	@echo "🧹 Limpiando outputs regenerables..."
	@echo ""
	find $(OUTPUTS_DIR) -mindepth 1 ! -name README.md -exec rm -rf {} +
	rm -f $(ANALYSIS_DIR)/cases/*.md
	@echo "✅ 04_outputs/ limpio + tarjetas regenerables eliminadas"
	@echo ""

#==============================================================================
# UTILIDADES
#==============================================================================

status:
	@echo "📊 Estado del pipeline etnográfico:"
	@echo ""
	@echo "1. Corpus TEI:"
	@if [ -f $(DATA_DIR)/tei/source/MANIFEST.md ]; then \
		tei_count=$$(ls -1 $(DATA_DIR)/tei/source/*.xml 2>/dev/null | wc -l | tr -d ' '); \
		echo "   ✓ $$tei_count archivos TEI copiados (ver MANIFEST.md)"; \
	else \
		echo "   ✗ No copiado (ejecuta: make copy-from-tei TEI_DIR=...)"; \
	fi
	@echo ""
	@echo "2. Texto extraído:"
	@if [ -f $(DATA_DIR)/text/units.csv ]; then \
		units_count=$$(tail -n +2 $(DATA_DIR)/text/units.csv 2>/dev/null | wc -l | tr -d ' '); \
		echo "   ✓ units.csv ($$units_count unidades)"; \
	else \
		echo "   ✗ units.csv no generado (ejecuta: make tei-to-text)"; \
	fi
	@echo ""
	@echo "3. Casos/escenas detectados:"
	@if [ -f $(DATA_DIR)/kwic_exports/cases_raw.csv ]; then \
		cases_count=$$(tail -n +2 $(DATA_DIR)/kwic_exports/cases_raw.csv 2>/dev/null | wc -l | tr -d ' '); \
		echo "   ✓ cases_raw.csv ($$cases_count casos detectados)"; \
	else \
		echo "   ✗ cases_raw.csv no generado (ejecuta: make build-cases)"; \
	fi
	@echo ""
	@echo "4. Casos muestreados:"
	@if [ -f $(ANALYSIS_DIR)/cases/cases_sampled.csv ]; then \
		sampled_count=$$(tail -n +2 $(ANALYSIS_DIR)/cases/cases_sampled.csv 2>/dev/null | wc -l | tr -d ' '); \
		md_count=$$(ls -1 $(ANALYSIS_DIR)/cases/*.md 2>/dev/null | wc -l | tr -d ' '); \
		echo "   ✓ cases_sampled.csv ($$sampled_count casos muestreados)"; \
		echo "   ✓ $$md_count markdowns generados"; \
	else \
		echo "   ✗ cases_sampled.csv no generado (ejecuta: make sample)"; \
	fi
	@echo ""
	@echo "5. Coocurrencias:"
	@if [ -f $(OUTPUTS_DIR)/tables/cooc_pairs.csv ]; then \
		cooc_count=$$(tail -n +2 $(OUTPUTS_DIR)/tables/cooc_pairs.csv 2>/dev/null | wc -l | tr -d ' '); \
		echo "   ✓ cooc_pairs.csv ($$cooc_count pares)"; \
	else \
		echo "   ✗ cooc_pairs.csv no generado (ejecuta: make cooc)"; \
	fi
	@echo ""
	@echo "6. Memos etnográficos:"
	@memo_count=$$(ls -1 $(ANALYSIS_DIR)/memos/*.md 2>/dev/null | grep -v MEMO_template | wc -l | tr -d ' '); \
	if [ $$memo_count -gt 0 ]; then \
		echo "   ✓ $$memo_count memos escritos"; \
	else \
		echo "   ⚠️  0 memos escritos (escribir manualmente en 03_analysis/memos/)"; \
	fi
	@echo ""

clean:
	@echo "🧹 Limpiando outputs intermedios..."
	@echo ""
	@echo "¿Qué deseas limpiar?"
	@echo ""
	@echo "  make clean-all       - Limpiar TODO (TEI, texto, casos, outputs)"
	@echo "  make clean-outputs   - Solo outputs finales (04_outputs/)"
	@echo "  make clean-cases     - Solo casos/escenas (01_data/kwic_exports/, 03_analysis/cases/)"
	@echo ""
	@echo "ADVERTENCIA: No ejecutes 'clean-all' sin antes hacer backup."
	@echo ""

clean-cases:
	@echo "🧹 Limpiando casos/escenas detectados..."
	rm -f $(DATA_DIR)/kwic_exports/*.csv
	rm -f $(ANALYSIS_DIR)/cases/*.csv
	rm -f $(ANALYSIS_DIR)/cases/*.md
	@echo "✓ Casos eliminados (memos en 03_analysis/memos/ conservados)"
	@echo ""

clean-all:
	@echo "🧹 Limpiando TODO el pipeline..."
	@echo "⚠️  ADVERTENCIA: Esto eliminará corpus TEI copiado, texto, casos, outputs."
	@echo "   (Cancelar con Ctrl+C en 5s)"
	@sleep 5
	rm -rf $(DATA_DIR)/tei/source/*.xml
	rm -f $(DATA_DIR)/tei/source/MANIFEST.md
	rm -f $(DATA_DIR)/text/*.csv
	rm -f $(DATA_DIR)/kwic_exports/*.csv
	rm -f $(ANALYSIS_DIR)/cases/*.csv
	rm -f $(ANALYSIS_DIR)/cases/*.md
	rm -f $(OUTPUTS_DIR)/tables/*.csv
	rm -f $(OUTPUTS_DIR)/figures/*.png
	@echo "✓ Pipeline limpiado completamente"
	@echo ""
	@echo "Para reiniciar: make copy-from-tei TEI_DIR=..."
	@echo ""

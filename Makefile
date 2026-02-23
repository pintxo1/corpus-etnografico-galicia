# Makefile - Corpus Etnográfico Galicia
# Pipeline para análisis de literatura como fuente etnográfica

.PHONY: all help clean install check analisis coocurrencias status

# Python command
PYTHON := python3

# Directorio base
BASE_DIR := $(shell pwd)

# Directorios clave
SCRIPTS_DIR := $(BASE_DIR)/scripts
OUTPUTS_DIR := $(BASE_DIR)/outputs

#==============================================================================
# HELP
#==============================================================================

help:
	@echo "================================================================"
	@echo "  CORPUS ETNOGRÁFICO GALICIA - Makefile"
	@echo "================================================================"
	@echo ""
	@echo "Comandos disponibles:"
	@echo ""
	@echo "  make install         - Instalar dependencias Python"
	@echo "  make check           - Verificar estructura y datos"
	@echo "  make analisis        - Análisis etnográfico (13 categorías)"
	@echo "  make coocurrencias   - Análisis de coocurrencias sociales"
	@echo "  make all             - Pipeline completo (análisis + coocurrencias)"
	@echo "  make status          - Ver estado de outputs"
	@echo "  make clean           - Limpiar outputs generados"
	@echo ""
	@echo "================================================================"
	@echo ""

#==============================================================================
# INSTALACIÓN
#==============================================================================

install:
	@echo "📦 Instalando dependencias Python..."
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	@echo "✓ Dependencias instaladas"
	@echo ""

#==============================================================================
# VERIFICACIÓN
#==============================================================================

check:
	@echo "🔍 Verificando estructura del proyecto..."
	@echo ""
	@echo "1. Verificando directorios..."
	@test -d $(BASE_DIR)/data/tei || (echo "❌ ERROR: data/tei/ no existe (symlink faltante)" && exit 1)
	@test -f $(BASE_DIR)/data/metadata/corpus.csv || (echo "❌ ERROR: metadata/corpus.csv faltante" && exit 1)
	@echo "   ✓ Directorios OK"
	@echo ""
	@echo "2. Verificando archivos TEI..."
	@tei_count=$$(ls -1 $(BASE_DIR)/data/tei/*.xml 2>/dev/null | wc -l); \
	if [ $$tei_count -eq 0 ]; then \
		echo "❌ ERROR: No se encontraron archivos TEI"; exit 1; \
	else \
		echo "   ✓ $$tei_count archivos TEI encontrados"; \
	fi
	@echo ""
	@echo "3. Verificando scripts..."
	@test -f $(SCRIPTS_DIR)/01_analisis_etnografico.py || (echo "❌ ERROR: 01_analisis_etnografico.py faltante" && exit 1)
	@test -f $(SCRIPTS_DIR)/02_coocurrencias_sociales.py || (echo "❌ ERROR: 02_coocurrencias_sociales.py faltante" && exit 1)
	@echo "   ✓ Scripts OK"
	@echo ""
	@echo "✅ Estructura del proyecto verificada correctamente"
	@echo ""

#==============================================================================
# ANÁLISIS
#==============================================================================

analisis:
	@echo "🔬 Ejecutando análisis etnográfico..."
	@echo ""
	$(PYTHON) $(SCRIPTS_DIR)/01_analisis_etnografico.py
	@echo ""
	@echo "✅ Análisis etnográfico completado"
	@echo ""

coocurrencias:
	@echo "🕸️  Ejecutando análisis de coocurrencias..."
	@echo ""
	@test -f $(OUTPUTS_DIR)/metricas_etnograficas/metricas_etnograficas_completo.csv || \
		(echo "❌ ERROR: Ejecuta primero 'make analisis'" && exit 1)
	$(PYTHON) $(SCRIPTS_DIR)/02_coocurrencias_sociales.py
	@echo ""
	@echo "✅ Análisis de coocurrencias completado"
	@echo ""

#==============================================================================
# PIPELINE COMPLETO
#==============================================================================

all: check analisis coocurrencias
	@echo "================================================================"
	@echo "✅ PIPELINE COMPLETO EJECUTADO"
	@echo "================================================================"
	@echo ""
	@echo "Outputs generados en:"
	@echo "  • outputs/metricas_etnograficas/"
	@echo "  • outputs/coocurrencias/"
	@echo ""

#==============================================================================
# UTILIDADES
#==============================================================================

status:
	@echo "📊 Estado de outputs generados:"
	@echo ""
	@echo "Métricas etnográficas:"
	@if [ -f $(OUTPUTS_DIR)/metricas_etnograficas/metricas_etnograficas_completo.csv ]; then \
		echo "  ✓ metricas_etnograficas_completo.csv"; \
		wc -l $(OUTPUTS_DIR)/metricas_etnograficas/metricas_etnograficas_completo.csv | awk '{print "    ("$$1-1" documentos procesados)"}'; \
	else \
		echo "  ✗ metricas_etnograficas_completo.csv (no generado)"; \
	fi
	@if [ -f $(OUTPUTS_DIR)/metricas_etnograficas/resumen_por_decada.csv ]; then \
		echo "  ✓ resumen_por_decada.csv"; \
	else \
		echo "  ✗ resumen_por_decada.csv"; \
	fi
	@echo ""
	@echo "Coocurrencias:"
	@if [ -f $(OUTPUTS_DIR)/coocurrencias/matriz_coocurrencias.csv ]; then \
		echo "  ✓ matriz_coocurrencias.csv"; \
		wc -l $(OUTPUTS_DIR)/coocurrencias/matriz_coocurrencias.csv | awk '{print "    ("$$1-1" pares analizados)"}'; \
	else \
		echo "  ✗ matriz_coocurrencias.csv (no generado)"; \
	fi
	@echo ""

clean:
	@echo "🧹 Limpiando outputs..."
	rm -rf $(OUTPUTS_DIR)/metricas_etnograficas/*.csv
	rm -rf $(OUTPUTS_DIR)/coocurrencias/*.csv
	@echo "✓ Outputs eliminados"
	@echo ""
	@echo "Para regenerar, ejecuta: make all"
	@echo ""

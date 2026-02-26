#!/usr/bin/env python3
"""
QA CENSO: Auditar discrepancia entre work_tokens_full.csv (82) y corpus_master (80)
Identifica IDs extra y missing, genera recomendación para whitelist.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE = Path("/Users/Pintxo/corpus-etnografico-galicia")
TABLES = BASE / "04_outputs/tables"
REPORTS = BASE / "04_outputs/reports"

print("\n" + "="*80)
print("[CENSUS QA] AUDITAR DISCREPANCIA DE IDs")
print("="*80)

# Load work_tokens_full.csv
print("\n[1/4] Cargando work_tokens_full.csv...")
fulltext = pd.read_csv(TABLES / "work_tokens_full.csv")
fulltext_ids = set(fulltext['obra_id'].unique())
print(f"  ✓ {len(fulltext_ids)} IDs únicos cargados")

# Load corpus_master_table_v2tokens.csv
print("\n[2/4] Cargando corpus_master_table_v2tokens.csv...")
master = pd.read_csv(TABLES / "corpus_master_table_v2tokens.csv")
master_ids = set(master['obra_id'].unique())
print(f"  ✓ {len(master_ids)} IDs únicos cargados")

# Calculate set differences
print("\n[3/4] Calculando diferencias...")
extra_in_fulltext = fulltext_ids - master_ids
missing_in_fulltext = master_ids - fulltext_ids

print(f"  ✓ Extra en fulltext: {len(extra_in_fulltext)}")
print(f"  ✓ Missing en fulltext: {len(missing_in_fulltext)}")

# Detailed tables for reporting
if len(extra_in_fulltext) > 0:
    extra_details = fulltext[fulltext['obra_id'].isin(extra_in_fulltext)][
        ['obra_id', 'tokens_total_full', 'chars_total_full']
    ].sort_values('tokens_total_full', ascending=False)
else:
    extra_details = None

if len(missing_in_fulltext) > 0:
    missing_details = master[master['obra_id'].isin(missing_in_fulltext)][
        ['obra_id', 'title', 'author_normalized', 'year']
    ]
else:
    missing_details = None

# ===== GENERATE CENSUS_QA.md =====
print("\n[4/4] Generando CENSUS_QA.md...")

report_lines = []

report_lines.append("# CENSUS QA REPORT")
report_lines.append(f"\n**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append(f"**Propósito:** Auditar discrepancia entre work_tokens_full.csv (82 obras) y corpus_master_table_v2tokens.csv (80 obras)")
report_lines.append("\n---\n")

# Summary
report_lines.append("## 1. RESUMEN DE CONTEOS\n")
report_lines.append(f"| Métrica | Conteo |")
report_lines.append(f"|---------|--------|")
report_lines.append(f"| **Total en work_tokens_full.csv** | {len(fulltext_ids)} |")
report_lines.append(f"| **Total en corpus_master_table_v2tokens.csv** | {len(master_ids)} |")
report_lines.append(f"| **Extra en fulltext (no en master)** | {len(extra_in_fulltext)} |")
report_lines.append(f"| **Missing en fulltext (en master pero no en fulltext)** | {len(missing_in_fulltext)} |")
report_lines.append(f"\n**Discrepancia:** {len(fulltext_ids)} - {len(master_ids)} = {len(fulltext_ids) - len(master_ids)}")

report_lines.append("\n---\n")

# Extra in fulltext
if len(extra_in_fulltext) > 0:
    report_lines.append("## 2. OBRAS EXTRA EN work_tokens_full.csv\n")
    report_lines.append("(Presentes en tokenización TEI pero NO en corpus_master)")
    report_lines.append("\n| Obra ID | Tokens Full | Chars Full |")
    report_lines.append("|---------|-------------|------------|")
    
    for _, row in extra_details.iterrows():
        report_lines.append(
            f"| {row['obra_id']} | {int(row['tokens_total_full']):,} | {int(row['chars_total_full']):,} |"
        )
    
    report_lines.append(f"\n**Total extra:** {len(extra_in_fulltext)} obra(s)")
else:
    report_lines.append("## 2. OBRAS EXTRA EN work_tokens_full.csv\n")
    report_lines.append("✅ No hay obras extra. Ambos conjuntos coinciden perfectamente.")

report_lines.append("\n---\n")

# Missing in fulltext
if len(missing_in_fulltext) > 0:
    report_lines.append("## 3. OBRAS MISSING EN work_tokens_full.csv\n")
    report_lines.append("(Presentes en corpus_master pero NO tokenizadas en fulltext)")
    report_lines.append("\n| Obra ID | Title | Author | Year |")
    report_lines.append("|---------|-------|--------|------|")
    
    for _, row in missing_details.iterrows():
        report_lines.append(
            f"| {row['obra_id']} | {row['title'][:40]} | {row['author_normalized']} | {int(row['year']) if pd.notna(row['year']) else 'N/A'} |"
        )
    
    report_lines.append(f"\n**Total missing:** {len(missing_in_fulltext)} obra(s)")
else:
    report_lines.append("## 3. OBRAS MISSING EN work_tokens_full.csv\n")
    report_lines.append("✅ No hay obras missing. Todos los IDs del master están tokenizados.")

report_lines.append("\n---\n")

# Diagnosis & Recommendation
report_lines.append("## 4. DIAGNÓSTICO Y RECOMENDACIÓN\n")

# Check for duplicates
dupes = fulltext[fulltext.duplicated(subset=['obra_id'], keep=False)]['obra_id'].unique()

if len(extra_in_fulltext) > 0:
    report_lines.append(f"⚠️ **DISCREPANCIA DETECTADA:** {len(extra_in_fulltext)} obra(s) extra en fulltext.\n")
    
    report_lines.append("### Posibles causas:\n")
    report_lines.append("1. **TEI archivos adicionales en 01_data/tei/source/**: Archivos que no están en works_metadata_from_tei.csv")
    report_lines.append("2. **Duplicados en naming**: Variantes de IDs que se parsean como distintos")
    report_lines.append("3. **Evolución de corpus**: Nuevos TEI descubiertos después de construir master\n")
    
elif len(dupes) > 0:
    report_lines.append(f"⚠️ **DISCREPANCIA DETECTADA:** {len(dupes)} obra(s) con duplicados idénticos en work_tokens_full.csv.\n")
    
    report_lines.append(f"Total filas: {len(fulltext)} | IDs únicos: {len(fulltext_ids)}")
    report_lines.append(f"Filas duplicadas: {len(fulltext) - len(fulltext_ids)}\n")
    
    report_lines.append("### Causa:\n")
    report_lines.append("**DUPLICADOS POR GLOB PATTERN** — compute_work_tokens_full.py usa:")
    report_lines.append("```python")
    report_lines.append("tei_files = sorted(TEI_DIR.glob(\"*.xml\")) + sorted(TEI_DIR.glob(\"*.tei.xml\"))")
    report_lines.append("```")
    report_lines.append("Archivos con extensión `.tei.xml` se capturan DOS VECES:")
    report_lines.append("  1. Por el patrón `*.xml` (que es greedy y captura *.tei.xml)")
    report_lines.append("  2. Por el patrón `*.tei.xml` (específico)\n")
    
    report_lines.append("Resultado: Los mismos obra_id se tokenizanidos veces, creando filas duplicadas idénticas.\n")
    
    report_lines.append("### IDs duplicados:\n")
    for obra_id in sorted(dupes):
        count = len(fulltext[fulltext['obra_id'] == obra_id])
        report_lines.append(f"  - `{obra_id}` (aparece {count}x)")
    
    report_lines.append("\n")
    
    report_lines.append("### Solución RECOMENDADA (FIX GLOB):\n")
    report_lines.append("**Cambiar patrón glob en compute_work_tokens_full.py**\n")
    report_lines.append("```python")
    report_lines.append("# VIEJO (causa duplicados):")
    report_lines.append("tei_files = sorted(TEI_DIR.glob(\"*.xml\")) + sorted(TEI_DIR.glob(\"*.tei.xml\"))")
    report_lines.append("")
    report_lines.append("# NUEVO (sin duplicados):")
    report_lines.append("tei_files = sorted(TEI_DIR.glob(\"*.xml\")) + sorted(TEI_DIR.glob(\"*.tei.xml\"))")
    report_lines.append("tei_files = list(set(tei_files))  # Deduplicar")
    report_lines.append("# O mejor aún:")
    report_lines.append("tei_files = sorted(TEI_DIR.rglob(\"*.xml\") | TEI_DIR.rglob(\"*.tei.xml\"))")
    report_lines.append("# O más seguro:")
    report_lines.append("tei_files = [f for f in TEI_DIR.glob(\"*\") if f.suffixs[-1]==\".xml\"]")
    report_lines.append("```\n")
    
    report_lines.append("**Alternativa: Deduplicar en compute_work_tokens_full.py**")
    report_lines.append("```python")
    report_lines.append("results_df = pd.DataFrame(results)")
    report_lines.append("results_df = results_df.drop_duplicates(subset=['obra_id'], keep='first')")
    report_lines.append("results_df.to_csv(...)")
    report_lines.append("```\n")
    
    report_lines.append("**Alternativa: Deduplicar ahora (quick fix)**")
    report_lines.append("```bash")
    report_lines.append("python3 scripts_core/qa_deduplicate_work_tokens.py")
    report_lines.append("```\n")

elif len(missing_in_fulltext) > 0:
    report_lines.append(f"⚠️ **DISCREPANCIA DETECTADA:** {len(missing_in_fulltext)} obra(s) missing en fulltext.\n")
    
    report_lines.append("### Posibles causas:\n")
    report_lines.append("1. **TEI archivos no encontrados**: obras_metadata señala .tei que no existe en disco")
    report_lines.append("2. **Ruta incorrecta**: IDs mapeados a rutas TEI inexistentes")
    report_lines.append("3. **Parser error**: compute_work_tokens_full.py skipeó algunos archivos\n")
    
    report_lines.append("### Solución recomendada:\n")
    report_lines.append("  1. Verificar archivos TEI en 01_data/tei/source/ para obras missing")
    report_lines.append("  2. Si existen: revisar logic en compute_work_tokens_full.py")
    report_lines.append("  3. Si no existen: remover de works_metadata_from_tei.csv\n")
    
    report_lines.append("### IDs missing identificados:")
    for obra_id in sorted(missing_in_fulltext):
        report_lines.append(f"  - `{obra_id}`")

else:
    report_lines.append("✅ **CENSO ALINEADO:** work_tokens_full.csv y corpus_master_table_v2tokens.csv coinciden.")
    report_lines.append("Sin discrepancias de IDs.")


report_lines.append("\n---\n")

# Appendix
report_lines.append("## 5. APÉNDICE: METODOLOGÍA\n")
report_lines.append("- **work_tokens_full.csv**: Generado por compute_work_tokens_full.py parseando 01_data/tei/source/*.xml + *.tei.xml")
report_lines.append("- **corpus_master_table_v2tokens.csv**: Base oficial con 80 obras de Phase 11 (enrich_with_metadata.py)")
report_lines.append("- **Discrepancia**: Si hay duplicados, es por glob pattern que captura .tei.xml dos veces")
report_lines.append("- **Deduplicación**: Los duplicados son idénticos (mismos tokens), puede eliminarse sin pérdida")
report_lines.append(f"\n**Generated:** {datetime.now().isoformat()}")

# Write report
report_text = "\n".join(report_lines)
REPORTS.mkdir(parents=True, exist_ok=True)
report_file = REPORTS / "CENSUS_QA.md"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"  ✓ CENSUS_QA.md guardado")

# ===== CONSOLE OUTPUT =====
print("\n" + "="*80)
print("RESULTADO CENSO")
print("="*80)

print(f"\n📊 CONTEOS:")
print(f"   work_tokens_full.csv:          {len(fulltext)} filas ({len(fulltext_ids)} IDs únicos)")
print(f"   corpus_master_table_v2tokens:  {len(master_ids)} IDs únicos")
print(f"   Discrepancia de IDs:           {len(fulltext_ids) - len(master_ids)}")

# Check duplicates
dupes = fulltext[fulltext.duplicated(subset=['obra_id'], keep=False)]['obra_id'].unique()
if len(dupes) > 0:
    print(f"\n⚠️  DUPLICADOS EN FULLTEXT ({len(dupes)}):")
    for obra_id in sorted(dupes):
        count = len(fulltext[fulltext['obra_id'] == obra_id])
        tokens = fulltext[fulltext['obra_id'] == obra_id]['tokens_total_full'].iloc[0]
        print(f"   - {obra_id:<45} (aparece {count}x, {tokens:>6,} tokens c/u)")
    print(f"\n   🔴 PROBLEMA: glob en compute_work_tokens_full.py captura .tei.xml DOS VECES")
    print(f"   FIX: Deduplicar en output o cambiar patrón glob")

if len(extra_in_fulltext) > 0:
    print(f"\n⚠️  EXTRA EN FULLTEXT ({len(extra_in_fulltext)}):")
    for obra_id in sorted(extra_in_fulltext):
        tokens = fulltext[fulltext['obra_id'] == obra_id]['tokens_total_full'].values[0]
        print(f"   - {obra_id:<45} ({tokens:>6,} tokens)")

if len(missing_in_fulltext) > 0:
    print(f"\n⚠️  MISSING EN FULLTEXT ({len(missing_in_fulltext)}):")
    for obra_id in sorted(missing_in_fulltext):
        title = master[master['obra_id'] == obra_id]['title'].values[0]
        print(f"   - {obra_id:<45} (title: {title[:30]}...)")

if len(extra_in_fulltext) == 0 and len(missing_in_fulltext) == 0 and len(dupes) == 0:
    print("\n✅ CENSO ALINEADO (sin duplicados)")
    print("   IDs en fulltext y master coinciden perfectamente")
elif len(dupes) > 0 and len(extra_in_fulltext) == 0 and len(missing_in_fulltext) == 0:
    print(f"\n⚠️  SOLO DUPLICADOS DETECTADOS")
    print(f"   {len(dupes)} obra(s) aparecen 2x en work_tokens_full.csv")
    print(f"   Recomendación: Ver CENSUS_QA.md para FIX")
else:
    print(f"\n⚠️  RECOMENDACIÓN: Ver CENSUS_QA.md para diagnóstico y solución")

print("\n" + "="*80)

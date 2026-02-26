#!/usr/bin/env python3
"""
QA TOKENS: Audit de discrepancias snippet vs fulltext
Compara tokens_snippet (units_enriched) vs tokens_full (work_tokens_full)
Genera token_mismatch_audit.csv y TOKEN_QA_REPORT_v2tokens.md
SIN modificar outputs; solo análisis diagnóstico.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Paths
BASE = Path("/Users/Pintxo/corpus-etnografico-galicia")
TABLES = BASE / "04_outputs/tables"
REPORTS = BASE / "04_outputs/reports"

print("\n" + "="*80)
print("[QA] AUDIT DE TOKENS: SNIPPET vs FULLTEXT")
print("="*80)

# 1. Load units_enriched
print("\n[1/5] Cargando units_enriched.csv...")
units = pd.read_csv(TABLES / "units_enriched.csv")
print(f"  ✓ {len(units)} unidades cargadas")

# 2. Load work_tokens_full
print("\n[2/5] Cargando work_tokens_full.csv...")
tokens_full = pd.read_csv(TABLES / "work_tokens_full.csv")
print(f"  ✓ {len(tokens_full)} obras con tokens fulltext")

# 3. Load corpus_master_table_v2tokens for context
print("\n[3/5] Cargando corpus_master_table_v2tokens.csv...")
master_v2 = pd.read_csv(TABLES / "corpus_master_table_v2tokens.csv")
print(f"  ✓ {len(master_v2)} obras en tabla maestra")

# ===== BUILD AUDIT TABLE =====
print("\n[4/5] Construyendo audit table...")

# 4a. Tokens snippet: suma por obra desde units_enriched
tokens_snippet = units.groupby('obra_id').agg({
    'n_tokens': 'sum'
}).reset_index().rename(columns={'n_tokens': 'tokens_snippet'})

# 4b. Merge snippet + fulltext
audit = tokens_full[['obra_id', 'tokens_total_full']].copy()
audit.rename(columns={'tokens_total_full': 'tokens_full'}, inplace=True)

audit = audit.merge(tokens_snippet, on='obra_id', how='outer')

# 4c. Handle missing values
audit['tokens_snippet'] = audit['tokens_snippet'].fillna(0).astype(int)
audit['tokens_full'] = audit['tokens_full'].fillna(0).astype(int)

# 4d. Calculate mismatch metrics
audit['mismatch_abs'] = (audit['tokens_full'] - audit['tokens_snippet']).abs()
# Avoid division by zero
audit['mismatch_pct'] = np.where(
    audit['tokens_full'] > 0,
    (audit['mismatch_abs'] / audit['tokens_full']).round(4),
    0.0
)

# 4e. Add unit counts and avg chars
unit_counts = units.groupby('obra_id').agg({
    'n_tokens': 'count',
    'text': lambda x: x.str.len().mean()
}).reset_index()
unit_counts.rename(columns={
    'n_tokens': 'n_units',
    'text': 'avg_unit_chars'
}, inplace=True)

audit = audit.merge(unit_counts, on='obra_id', how='left')
audit['n_units'] = audit['n_units'].fillna(0).astype(int)
audit['avg_unit_chars'] = audit['avg_unit_chars'].fillna(0).round(1)

# 4f. Add flags
audit['flag_20pct'] = (audit['mismatch_pct'] > 0.20).astype(int)
audit['flag_10pct'] = (audit['mismatch_pct'] > 0.10).astype(int)

# 4g. Sort by mismatch descending
audit = audit.sort_values('mismatch_pct', ascending=False).reset_index(drop=True)

# Save audit table
audit_file = TABLES / "token_mismatch_audit.csv"
audit.to_csv(audit_file, index=False)
print(f"  ✓ token_mismatch_audit.csv guardado ({len(audit)} obras)")

# ===== SUMMARY STATISTICS =====
print("\n[5/5] Generando resumen...")

total_obras = len(audit)
obras_flag_20 = (audit['flag_20pct'] == 1).sum()
obras_flag_10 = (audit['flag_10pct'] == 1).sum()
avg_mismatch = audit['mismatch_pct'].mean()
max_mismatch = audit['mismatch_pct'].max()

print(f"\n  RESUMEN QA:")
print(f"    - Total obras auditadas: {total_obras}")
print(f"    - Obras con mismatch >20%: {obras_flag_20}")
print(f"    - Obras con mismatch >10%: {obras_flag_10}")
print(f"    - Mismatch promedio: {avg_mismatch:.2%}")
print(f"    - Mismatch máximo: {max_mismatch:.2%}")

# ===== GENERATE MARKDOWN REPORT =====
print("\n[REPORT] Generando TOKEN_QA_REPORT_v2tokens.md...")

top_15 = audit.head(15).copy()
top_10 = audit.head(10).copy()

# Obras pequeñas con mismatch >10%
small_units = audit[(audit['n_units'] <= 3) & (audit['flag_10pct'] == 1)].copy()

# Diagnosis patterns
flag_20_pairs = audit[audit['flag_20pct'] == 1][['obra_id', 'tokens_snippet', 'tokens_full', 'n_units']].values
flag_10_pairs = audit[audit['flag_10pct'] == 1] [['obra_id', 'tokens_snippet', 'tokens_full', 'n_units']].values

report_lines = []

# Header
report_lines.append("# TOKEN QA REPORT — v2tokens")
report_lines.append(f"\n**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report_lines.append(f"**Propósito:** Auditar discrepancias entre tokens snippet (units_enriched) y tokens fulltext (TEI)")
report_lines.append(f"\n---\n")

# Summary Section
report_lines.append("## 1. RESUMEN EJECUTIVO\n")
report_lines.append(f"**Total obras auditadas:** {total_obras}")
report_lines.append(f"**Obras con mismatch >20%:** {obras_flag_20} ⚠️")
report_lines.append(f"**Obras con mismatch >10%:** {obras_flag_10}")
report_lines.append(f"**Mismatch promedio (todas):** {avg_mismatch:.2%}")
report_lines.append(f"**Mismatch máximo:** {max_mismatch:.2%} (en {audit.iloc[0]['obra_id']})")

if obras_flag_20 <= 1:
    report_lines.append(f"\n**→ CONCLUSIÓN:** Solo {obras_flag_20} obra(s) tienen mismatch >20%. Caso aislado, no indica bugfix estructural.")
else:
    report_lines.append(f"\n**⚠️ CONCLUSIÓN:** {obras_flag_20} obras con mismatch >20%. Elevar a bugfix estructural.")

report_lines.append("\n---\n")

# Top 15 Mismatches
report_lines.append("## 2. TOP 15 MISMATCHES\n")
report_lines.append("| Obra ID | Tokens Snippet | Tokens Full | Mismatch % | N Unidades | Avg Unit Chars |")
report_lines.append("|---------|----------------|-------------|-----------|-----------|---|")

for _, row in top_15.iterrows():
    flag_str = "⚠️" if row['flag_20pct'] == 1 else ("⚠" if row['flag_10pct'] == 1 else "")
    report_lines.append(
        f"| {row['obra_id']} {flag_str} | {int(row['tokens_snippet']):,} | {int(row['tokens_full']):,} | "
        f"{row['mismatch_pct']:.2%} | {int(row['n_units'])} | {row['avg_unit_chars']:.0f} |"
    )

report_lines.append("\n---\n")

# Works with ≤3 units and >10% mismatch
report_lines.append("## 3. OBRAS PEQUEÑAS (≤3 unidades) CON MISMATCH >10%\n")
if len(small_units) > 0:
    report_lines.append("| Obra ID | Tokens Snippet | Tokens Full | Mismatch % | N Unidades |")
    report_lines.append("|---------|----------------|-------------|-----------|---|")
    for _, row in small_units.iterrows():
        report_lines.append(
            f"| {row['obra_id']} | {int(row['tokens_snippet']):,} | {int(row['tokens_full']):,} | "
            f"{row['mismatch_pct']:.2%} | {int(row['n_units'])} |"
        )
else:
    report_lines.append("No se encontraron obras pequeñas con mismatch >10%.")

report_lines.append("\n---\n")

# Diagnosis
report_lines.append("## 4. DIAGNÓSTICO POR PATRÓN\n")

report_lines.append("### Patrón A: Truncamiento por snippet\n")
report_lines.append("**Característica:** tokens_snippet << tokens_full (10% a 40%+ diferencia)")
report_lines.append("**Causa probable:** units_enriched contiene preview truncado (snippet_text limitado a N caracteres)")
report_lines.append("**Identificación:** mismatch_pct > 10%\n")

pattern_a = audit[audit['mismatch_pct'] > 0.10]
if len(pattern_a) > 0:
    report_lines.append(f"**Obras identificadas ({len(pattern_a)}):**\n")
    for _, row in pattern_a.head(10).iterrows():
        loss_pct = (1 - row['tokens_snippet'] / row['tokens_full']) * 100 if row['tokens_full'] > 0 else 0
        report_lines.append(f"  - **{row['obra_id']}**: {int(row['tokens_snippet']):,} snippet → {int(row['tokens_full']):,} full (pérdida {loss_pct:.1f}%)")
else:
    report_lines.append("No hay obras con este patrón en esta ejecución.")

report_lines.append("\n")

report_lines.append("### Patrón B: TEI con body muy corto (legítimo)\n")
report_lines.append("**Característica:** tokens_full < 1000 tokens\n")
report_lines.append("**Causa probable:** Obra pequeña, poema corto, fragmento genuino")
report_lines.append("**Identificación:** tokens_full < 1000 Y mismatch_pct < 10%\n")

pattern_b = audit[(audit['tokens_full'] < 1000) & (audit['mismatch_pct'] <= 0.10)]
if len(pattern_b) > 0:
    report_lines.append(f"**Obras identificadas ({len(pattern_b)}):**\n")
    for _, row in pattern_b.iterrows():
        report_lines.append(f"  - **{row['obra_id']}**: {int(row['tokens_full']):,} tokens (pequeña legítima)")
else:
    report_lines.append("No hay obras con este patrón en esta ejecución.")

report_lines.append("\n")

report_lines.append("### Patrón C: Tokenización/limpieza inconsistente\n")
report_lines.append("**Característica:** mismatch_pct 2% a 9% (pequeño pero consistente)\n")
report_lines.append("**Causa probable:** Diferencia en reglas split() (spaces, punctuation) o limpieza de whitespace")
report_lines.append("**Identificación:** 0.02 < mismatch_pct < 0.10\n")

pattern_c = audit[(audit['mismatch_pct'] > 0.02) & (audit['mismatch_pct'] <= 0.10)]
if len(pattern_c) > 0:
    report_lines.append(f"**Obras identificadas ({len(pattern_c)}):**")
    report_lines.append("(Estas representan variabilidad normal en split/limpieza — no requieren acción)\n")
else:
    report_lines.append("No hay obras con este patrón en esta ejecución.\n")

report_lines.append("\n---\n")

# Recommendations
report_lines.append("## 5. RECOMENDACIONES\n")

if obras_flag_20 > 3:
    report_lines.append("⚠️ **ELEVAR A BUGFIX ESTRUCTURAL**\n")
    report_lines.append("Más de 3 obras con mismatch >20% indica problema sistemático.\n")
    report_lines.append("Acciones sugeridas:")
    report_lines.append("  1. Revisar parámetros de truncamiento en units.csv")
    report_lines.append("  2. Validar parseo de TEI body")
    report_lines.append("  3. Homogenizar reglas de tokenización")
elif obras_flag_20 == 1:
    report_lines.append("✅ **DOCUMENTAR COMO CASO AISLADO**\n")
    report_lines.append(f"Solo 1 obra con mismatch >20%: **{audit[audit['flag_20pct']==1]['obra_id'].values[0]}**\n")
    report_lines.append("Acciones sugeridas:")
    report_lines.append("  1. Marcar con token_mismatch_flag=1 en corpus_master (✓ ya existe)")
    report_lines.append("  2. Añadir nota en VERSION_ANALISIS sobre esta obra")
    report_lines.append("  3. Mantener *_v2tokens como canonical (tokens_full)")
elif obras_flag_20 == 0 and obras_flag_10 <= 2:
    report_lines.append("✅ **CALIDAD ACEPTABLE**\n")
    report_lines.append("Todas las obras tienen <10% mismatch (excepto legitimamente pequeñas).\n")
    report_lines.append("Acciones sugeridas:")
    report_lines.append("  1. Congelar *_v2tokens como canonical")
    report_lines.append("  2. Marcar v1.0.1 como versión oficial")
    report_lines.append("  3. Archivo units_enriched.csv como legacy (snippets para ref solamente)")

report_lines.append("\n---\n")

# Appendix
report_lines.append("## APÉNDICE: DEFINICIONES\n")
report_lines.append("- **tokens_snippet**: Suma de n_tokens de todas las unidades en units_enriched.csv por obra")
report_lines.append("- **tokens_full**: tokens_total_full de work_tokens_full.csv (extracción directa tei:body)")
report_lines.append("- **mismatch_abs**: |tokens_full - tokens_snippet|")
report_lines.append("- **mismatch_pct**: mismatch_abs / tokens_full (fracción de pérdida)")
report_lines.append("- **flag_20pct**: 1 si mismatch_pct > 0.20 (significativo)")
report_lines.append("- **flag_10pct**: 1 si mismatch_pct > 0.10 (notable)")
report_lines.append(f"\n**Generated:** {datetime.now().isoformat()}")
report_lines.append(f"**Source data:** units_enriched.csv, work_tokens_full.csv, corpus_master_table_v2tokens.csv")

# Write report
report_text = "\n".join(report_lines)
REPORTS.mkdir(parents=True, exist_ok=True)
report_file = REPORTS / "TOKEN_QA_REPORT_v2tokens.md"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"  ✓ TOKEN_QA_REPORT_v2tokens.md guardado ({len(report_lines)} líneas)")

# ===== FINAL EVIDENCE OUTPUT =====
print("\n" + "="*80)
print("TOP 10 TOKEN MISMATCHES")
print("="*80)
print(f"\n{'obra_id':<45} {'Mismatch %':>12} {'N Units':>10}")
print("-" * 70)
for _, row in top_10.iterrows():
    flag = "⚠️ " if row['flag_20pct'] == 1 else ""
    print(f"{flag}{row['obra_id']:<42} {row['mismatch_pct']:>11.2%} {int(row['n_units']):>10}")

print("\n" + "="*80)
print("RESUMEN EJECUTIVO")
print("="*80)
print(f"\nTotal obras auditadas: {total_obras}")
print(f"Obras con mismatch >20%: {obras_flag_20} ⚠️")
print(f"Obras con mismatch >10%: {obras_flag_10}")
print(f"Mismatch promedio: {avg_mismatch:.2%}")
print(f"Mismatch máximo: {max_mismatch:.2%}")

if obras_flag_20 <= 1:
    print(f"\n→ CONCLUSIÓN: Solo {obras_flag_20} obra(s) con >20%. Caso aislado, no bugfix estructural.")
else:
    print(f"\n⚠️ CONCLUSIÓN: {obras_flag_20} obras con >20%. Considerar bugfix estructural.")

print("\n" + "="*80)

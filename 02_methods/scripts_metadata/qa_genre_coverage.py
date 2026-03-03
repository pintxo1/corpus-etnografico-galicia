#!/usr/bin/env python3
"""
qa_genre_coverage.py - QA report de cobertura de género extraído desde TEI.

Genera:
- 04_outputs/tables/genre_coverage_report.csv: tabla con stats por confidence
- 00_docs/GENRE_QA_REPORT.md: reporte legible con recomendaciones

Fase 12B (PROMPT 1): Extracción de género desde TEI headers
"""

import argparse
import pandas as pd
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent.parent
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"
DOCS_DIR = BASE_DIR / "00_docs"

def load_genre_data() -> pd.DataFrame:
    """Carga work_genre_from_tei.csv."""
    genre_file = TABLES_DIR / "work_genre_from_tei.csv"
    if not genre_file.exists():
        raise FileNotFoundError(f"No existe {genre_file}. Ejecuta extract_tei_genre.py primero.")
    
    df = pd.read_csv(genre_file)
    print(f"[genre] Cargados {len(df)} obras con género extraído")
    return df

def load_corpus_master() -> pd.DataFrame:
    """Carga corpus_master_table_v2tokens.csv para contexto."""
    master_file = TABLES_DIR / "corpus_master_table_v2tokens.csv"
    if not master_file.exists():
        master_file = TABLES_DIR / "corpus_master_table.csv"
    
    df = pd.read_csv(master_file)
    print(f"[master] Cargadas {len(df)} obras de tabla maestra")
    return df

def compute_coverage_stats(genre_df: pd.DataFrame) -> dict:
    """Calcula estadísticas de cobertura."""
    total = len(genre_df)
    
    # Por confidence level
    confidence_counts = genre_df['genre_confidence'].value_counts().to_dict()
    
    # Por genre_norm
    genre_counts = genre_df['genre_norm'].value_counts().to_dict()
    
    # Unknown count
    unknown_count = (genre_df['genre_norm'] == 'unknown').sum()
    
    # Top genre_raw values
    raw_to_norm = genre_df.groupby(['genre_raw', 'genre_norm']).size().reset_index(name='count')
    raw_to_norm = raw_to_norm.sort_values('count', ascending=False).head(20)
    
    stats = {
        'total': total,
        'confidence_counts': confidence_counts,
        'genre_counts': genre_counts,
        'unknown_count': unknown_count,
        'unknown_pct': (unknown_count / total * 100) if total > 0 else 0,
        'raw_to_norm_top20': raw_to_norm
    }
    
    return stats

def generate_coverage_table(stats: dict) -> pd.DataFrame:
    """Genera tabla resumen de cobertura."""
    rows = []
    
    # Por confidence
    for conf in ['high', 'medium', 'low', 'error']:
        count = stats['confidence_counts'].get(conf, 0)
        pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
        rows.append({
            'metric': f'confidence_{conf}',
            'count': count,
            'percent': round(pct, 2),
            'description': f'Obras con confidence={conf}'
        })
    
    # Por genre_norm
    for genre, count in stats['genre_counts'].items():
        pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
        rows.append({
            'metric': f'genre_{genre}',
            'count': count,
            'percent': round(pct, 2),
            'description': f'Obras con genre_norm={genre}'
        })
    
    # Unknown
    rows.append({
        'metric': 'genre_unknown',
        'count': stats['unknown_count'],
        'percent': round(stats['unknown_pct'], 2),
        'description': 'Obras sin género identificado'
    })
    
    df = pd.DataFrame(rows)
    return df

def generate_markdown_report(stats: dict, genre_df: pd.DataFrame, master_df: pd.DataFrame) -> list:
    """Genera reporte Markdown con QA findings."""
    lines = []
    
    lines.append("# GENRE QA REPORT")
    lines.append("")
    lines.append("**Fecha generación:** " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"))
    lines.append(f"**Corpus:** {stats['total']} obras")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 1. Executive Summary
    lines.append("## 1. Executive Summary")
    lines.append("")
    lines.append(f"- **Total obras analizadas:** {stats['total']}")
    lines.append(f"- **Género identificado (no unknown):** {stats['total'] - stats['unknown_count']} obras ({100 - stats['unknown_pct']:.1f}%)")
    lines.append(f"- **Género unknown:** {stats['unknown_count']} obras ({stats['unknown_pct']:.1f}%)")
    lines.append("")
    
    # Rating
    if stats['unknown_pct'] == 0:
        lines.append("**✅ COBERTURA EXCELENTE:** 100% de obras con género identificado desde TEI headers.")
    elif stats['unknown_pct'] < 5:
        lines.append(f"**✅ COBERTURA BUENA:** {100 - stats['unknown_pct']:.1f}% de obras con género identificado.")
    elif stats['unknown_pct'] < 20:
        lines.append(f"**⚠️  COBERTURA MEDIA:** {100 - stats['unknown_pct']:.1f}% de obras con género identificado.")
    else:
        lines.append(f"**❌ COBERTURA BAJA:** Solo {100 - stats['unknown_pct']:.1f}% de obras con género identificado.")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 2. Confidence Breakdown
    lines.append("## 2. Confidence Breakdown")
    lines.append("")
    lines.append("| Confidence | Count | Percent |")
    lines.append("|------------|-------|---------|")
    for conf in ['high', 'medium', 'low', 'error']:
        count = stats['confidence_counts'].get(conf, 0)
        pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
        lines.append(f"| {conf} | {count} | {pct:.1f}% |")
    lines.append(f"| **TOTAL** | **{stats['total']}** | **100.0%** |")
    lines.append("")
    
    # Interpretation
    high_pct = (stats['confidence_counts'].get('high', 0) / stats['total'] * 100) if stats['total'] > 0 else 0
    if high_pct >= 90:
        lines.append("**Interpretación:** Excelente calidad de extracción. La mayoría de géneros provienen directamente de `<classCode scheme='genero'>` en TEI headers.")
    elif high_pct >= 70:
        lines.append("**Interpretación:** Buena calidad de extracción. La mayoría de géneros son confiables.")
    else:
        lines.append("**Interpretación:** Calidad mixta. Considerar revisar TEI headers de obras con confidence=low/medium.")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 3. Genre Distribution
    lines.append("## 3. Genre Distribution")
    lines.append("")
    lines.append("| Genre | Count | Percent |")
    lines.append("|-------|-------|---------|")
    for genre, count in sorted(stats['genre_counts'].items(), key=lambda x: -x[1]):
        pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
        lines.append(f"| {genre} | {count} | {pct:.1f}% |")
    lines.append(f"| **TOTAL** | **{stats['total']}** | **100.0%** |")
    lines.append("")
    
    # 4. Top genre_raw → genre_norm mappings
    lines.append("---")
    lines.append("")
    lines.append("## 4. Top genre_raw → genre_norm Mappings")
    lines.append("")
    lines.append("Valores extraídos de TEI (`genre_raw`) y su normalización (`genre_norm`):")
    lines.append("")
    lines.append("| genre_raw | genre_norm | Count |")
    lines.append("|-----------|------------|-------|")
    for _, row in stats['raw_to_norm_top20'].iterrows():
        lines.append(f"| {row['genre_raw']} | {row['genre_norm']} | {row['count']} |")
    lines.append("")
    
    # 5. Obras con genre_norm=unknown
    lines.append("---")
    lines.append("")
    lines.append("## 5. Obras con genre_norm=unknown")
    lines.append("")
    
    if stats['unknown_count'] == 0:
        lines.append("✅ **Ninguna obra con género unknown.** Todos los géneros se extrajeron correctamente de TEI headers.")
    else:
        lines.append(f"⚠️  {stats['unknown_count']} obras ({stats['unknown_pct']:.1f}%) sin género identificado:")
        lines.append("")
        
        unknown_obras = genre_df[genre_df['genre_norm'] == 'unknown'].copy()
        unknown_with_context = unknown_obras.merge(
            master_df[['obra_id', 'title', 'author_normalized']], 
            on='obra_id', 
            how='left'
        )
        
        lines.append("| obra_id | title | author | genre_raw | source_xpath |")
        lines.append("|---------|-------|--------|-----------|--------------|")
        for _, row in unknown_with_context.iterrows():
            title = row.get('title', 'N/A')
            author = row.get('author_normalized', 'N/A')
            genre_raw = row['genre_raw'] if pd.notna(row['genre_raw']) and row['genre_raw'] != '' else '(empty)'
            source = row['genre_source_xpath']
            lines.append(f"| {row['obra_id']} | {title} | {author} | {genre_raw} | {source} |")
        lines.append("")
        
        lines.append("**Recomendación:** Revisar TEI headers de estas obras y añadir:")
        lines.append("```xml")
        lines.append("<tei:textClass>")
        lines.append("  <tei:classCode scheme='genero'>cuento_relato</tei:classCode>  <!-- o: novela, poesia_poemario, teatro, ensayo_cronica -->")
        lines.append("</tei:textClass>")
        lines.append("```")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # 6. Validation Summary
    lines.append("## 6. Validation Summary")
    lines.append("")
    lines.append(f"- ✅ Extracción de género desde TEI: **{stats['total']} obras procesadas**")
    lines.append(f"- ✅ Tasa de éxito: **{100 - stats['unknown_pct']:.1f}%**")
    
    high_count = stats['confidence_counts'].get('high', 0)
    lines.append(f"- ✅ Confidence high: **{high_count}/{stats['total']} obras** ({high_count/stats['total']*100:.1f}%)")
    
    if stats['unknown_count'] == 0:
        lines.append("- ✅ **Ninguna obra requiere corrección de TEI**")
    else:
        lines.append(f"- ⚠️  {stats['unknown_count']} obras requieren añadir `<classCode scheme='genero'>` en TEI headers")
    
    lines.append("")
    lines.append("**Conclusión:** " + (
        "Genre extraction completado exitosamente. Corpus listo para análisis por formato/género."
        if stats['unknown_pct'] < 5 else
        f"Recomendable revisar {stats['unknown_count']} obras sin género identificado antes de publicar."
    ))
    lines.append("")
    
    return lines

def main():
    """Ejecuta QA de cobertura de género."""
    parser = argparse.ArgumentParser(description="QA report de cobertura de género desde TEI")
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("QA_GENRE_COVERAGE: Reporte de cobertura de género")
    print("="*70 + "\n")
    
    # Cargar datos
    genre_df = load_genre_data()
    master_df = load_corpus_master()
    
    # Calcular stats
    stats = compute_coverage_stats(genre_df)
    
    # Generar tabla resumen
    coverage_table = generate_coverage_table(stats)
    coverage_file = TABLES_DIR / "genre_coverage_report.csv"
    coverage_table.to_csv(coverage_file, index=False)
    print(f"✅ genre_coverage_report.csv guardado: {coverage_file}")
    
    # Generar reporte Markdown
    report_lines = generate_markdown_report(stats, genre_df, master_df)
    report_file = DOCS_DIR / "GENRE_QA_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    print(f"✅ GENRE_QA_REPORT.md guardado: {report_file}")
    
    # Mostrar resumen en consola
    print("\n" + "="*70)
    print("RESUMEN DE COBERTURA:")
    print("="*70)
    print(f"  Total obras: {stats['total']}")
    print(f"  Con género (no unknown): {stats['total'] - stats['unknown_count']} ({100 - stats['unknown_pct']:.1f}%)")
    print(f"  Género unknown: {stats['unknown_count']} ({stats['unknown_pct']:.1f}%)")
    print()
    print(f"  Confidence high: {stats['confidence_counts'].get('high', 0)}")
    print(f"  Confidence medium: {stats['confidence_counts'].get('medium', 0)}")
    print(f"  Confidence low: {stats['confidence_counts'].get('low', 0)}")
    print()
    print(f"Top géneros:")
    for genre, count in sorted(stats['genre_counts'].items(), key=lambda x: -x[1])[:5]:
        print(f"  - {genre}: {count}")
    print()
    
    if stats['unknown_count'] > 0:
        print(f"⚠️  {stats['unknown_count']} obras necesitan corrección de TEI headers")
        print(f"   Ver detalles en: {report_file}")
    else:
        print("✅ Todos los géneros extraídos exitosamente desde TEI")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

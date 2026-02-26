#!/usr/bin/env python3
"""
Genera reportes individuales por autor (VERSIÓN 3: CON NORMALIZACIÓN)
- Agrupa por author_normalized (forma canónica)
- Usa author_confidence para transparencia
- Documenta obras con confidence=missing/low_inferred

Output:
  04_outputs/reports/by_author/<author_norm_key>/REPORT.md
  04_outputs/reports/by_author/INDEX.md
"""

import pandas as pd
import networkx as nx
from pathlib import Path
from collections import Counter
import argparse


def load_data(cases_path, units_path, works_metadata_path, cooc_path=None):
    """Carga datos necesarios"""
    cases = pd.read_csv(cases_path)
    units = pd.read_csv(units_path)
    works_metadata = pd.read_csv(works_metadata_path)
    
    cooc = None
    if cooc_path and Path(cooc_path).exists():
        cooc = pd.read_csv(cooc_path)
    
    return cases, units, works_metadata, cooc


def filter_by_author_normalized(cases, units, works_metadata, author_normalized):
    """Filtra casos y unidades para un autor normalizado"""
    
    # Obtener obras con este author_normalized (excluir missing)
    obras_autor_df = works_metadata[
        (works_metadata['author_normalized'] == author_normalized) &
        (works_metadata['author_confidence'] != 'missing')
    ]
    obras_autor = obras_autor_df['obra_id'].tolist()
    
    if len(obras_autor) == 0:
        return pd.DataFrame(), pd.DataFrame(), [], obras_autor_df
    
    cases_autor = cases[cases['obra_id'].isin(obras_autor)].copy()
    units_autor = units[units['obra_id'].isin(obras_autor)].copy()
    
    return cases_autor, units_autor, obras_autor, obras_autor_df


def compute_scene_summary(cases_autor):
    """Calcula scene_summary para un autor"""
    if len(cases_autor) == 0:
        return pd.DataFrame(columns=['escena_tipo', 'n_cases', 'n_obras'])
    
    summary = cases_autor.groupby('escena_tipo').agg({
        'case_id': 'count',
        'obra_id': 'nunique'
    }).reset_index()
    
    summary.columns = ['escena_tipo', 'n_cases', 'n_obras']
    summary = summary.sort_values('n_cases', ascending=False)
    
    return summary


def compute_scene_rates(scene_summary, total_tokens):
    """Calcula tasas por 1k tokens"""
    if total_tokens == 0:
        rates = scene_summary.copy()
        rates['rate_per_1k_tokens'] = 0.0
        return rates
    
    rates = scene_summary.copy()
    rates['rate_per_1k_tokens'] = (rates['n_cases'] / total_tokens) * 1000
    rates['rate_per_1k_tokens'] = rates['rate_per_1k_tokens'].round(2)
    
    return rates


def filter_cooc_network(cooc, cases_autor):
    """Filtra red de coocurrencias a los casos del autor"""
    if cooc is None or len(cases_autor) == 0:
        return None
    
    escenas_autor = set(cases_autor['escena_tipo'].unique())
    if 'escena_i' in cooc.columns and 'escena_j' in cooc.columns:
        cooc_filter = cooc[
            (cooc['escena_i'].isin(escenas_autor)) & 
            (cooc['escena_j'].isin(escenas_autor))
        ]
        if len(cooc_filter) > 0:
            return cooc_filter
    
    return None


def generate_report_md(author_normalized, n_obras, total_tokens, scene_summary, 
                       n_low_inferred, n_high_confidence, output_path):
    """Genera mini REPORT.md para un autor con trazabilidad de confianza"""
    
    top3_escenas = scene_summary.head(3) if len(scene_summary) >= 3 else scene_summary
    confidence_note = ""
    
    if n_low_inferred > 0:
        confidence_note = f"\n**⚠️ Nota de confianza**: {n_low_inferred}/{n_obras} obra(s) con autor inferido desde filename (confidence=low_inferred). {n_high_confidence}/{n_obras} con autor de TEI (high/medium confidence)."
    
    report = f"""# Reporte Etnográfico: {author_normalized}

**Fecha de generación**: 24 de febrero de 2026  
**Corpus**: Literatura gallega (siglos XIX-XX)  
**Diccionario**: escenas_minimas_v2.yml

---

## 📊 Resumen General

- **Número de obras**: {n_obras}
- **Tokens totales**: {total_tokens:,}
- **Casos detectados**: {scene_summary['n_cases'].sum()}
- **Tipos de escena representados**: {len(scene_summary)}
{confidence_note}

---

## 🔝 Top 3 Escenas (por frecuencia)

"""
    
    for idx, row in top3_escenas.iterrows():
        rate = (row['n_cases'] / total_tokens * 1000) if total_tokens > 0 else 0
        report += f"### {idx+1}. {row['escena_tipo']}\n\n"
        report += f"- **Casos**: {int(row['n_cases'])}\n"
        report += f"- **Obras**: {int(row['n_obras'])}\n"
        report += f"- **Tasa**: {rate:.2f} casos por 1k tokens\n\n"
    
    report += """---

## 📈 Datos Completos

Consulta los archivos CSV en los reportes tabulares para análisis detallados.

---

## 🕸️ Redes de Coocurrencia

Ver archivos GraphML para análisis de redes.

---

**Metodología**: Metadata extraída desde TEI headers. Autores agrupados por `author_normalized` (forma canónica). Ver `00_docs/` para detalles de normalización.
"""
    
    # Escribir archivo
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding='utf-8')


def process_author(author_normalized, author_norm_key, cases, units, works_metadata, cooc, output_base):
    """Procesa un autor normalizado y genera outputs"""
    
    print(f"\n📖 Procesando: {author_normalized}")
    
    # Filtrar datos
    cases_autor, units_autor, obras_autor, obras_autor_df = filter_by_author_normalized(
        cases, units, works_metadata, author_normalized
    )
    
    if len(cases_autor) == 0:
        print(f"   ⚠️  Sin casos detectados, omitiendo...")
        return None
    
    n_obras = len(obras_autor)
    total_tokens = units_autor['n_tokens'].sum()
    
    # Contar confianzas
    n_high_confidence = len(obras_autor_df[obras_autor_df['author_confidence'].isin(['high', 'medium'])])
    n_low_inferred = len(obras_autor_df[obras_autor_df['author_confidence'] == 'low_inferred'])
    
    print(f"   Obras: {n_obras} (high/medium: {n_high_confidence}, low_inferred: {n_low_inferred}) | " \
          f"Tokens: {total_tokens:,} | Casos: {len(cases_autor)}")
    
    # 1. Scene summary
    scene_summary = compute_scene_summary(cases_autor)
    
    # 2. Scene rates
    scene_rates = compute_scene_rates(scene_summary, total_tokens)
    
    # 3. Filtrar cooc (si existe)
    cooc_autor = filter_cooc_network(cooc, cases_autor) if cooc is not None else None
    
    # 4. Crear directorio de salida (usar author_norm_key)
    output_dir = output_base / author_norm_key
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 5. Guardar outputs
    scene_summary_path = output_base.parent / 'tables' / 'by_author' / f"{author_norm_key}_scene_summary.csv"
    scene_rates_path = output_base.parent / 'tables' / 'by_author' / f"{author_norm_key}_scene_rates.csv"
    report_path = output_dir / 'REPORT.md'
    
    scene_summary_path.parent.mkdir(parents=True, exist_ok=True)
    scene_summary.to_csv(scene_summary_path, index=False)
    scene_rates.to_csv(scene_rates_path, index=False)
    
    # 6. Generar REPORT.md
    generate_report_md(author_normalized, n_obras, total_tokens, scene_summary, 
                       n_low_inferred, n_high_confidence, report_path)
    
    # 7. Guardar cooc_network (si existe)
    if cooc_autor is not None and len(cooc_autor) > 0:
        network_path = output_base.parent.parent / 'networks' / 'by_author' / f"{author_norm_key}_cooc_network.graphml"
        network_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir a grafo
        G = nx.Graph()
        for _, row in cooc_autor.iterrows():
            if 'escena_i' in row and 'escena_j' in row:
                weight = row.get('weight', 1)
                G.add_edge(row['escena_i'], row['escena_j'], weight=weight)
        
        if G.number_of_nodes() > 0:
            nx.write_graphml(G, str(network_path))
    
    return {
        'author_normalized': author_normalized,
        'author_norm_key': author_norm_key,
        'n_obras': n_obras,
        'n_high_confidence': n_high_confidence,
        'n_low_inferred': n_low_inferred,
        'tokens_total': total_tokens,
        'cases_total': len(cases_autor),
        'top3_escenas': scene_summary.head(3)['escena_tipo'].tolist() if len(scene_summary) >= 3 else []
    }


def generate_index(author_stats, works_metadata, output_path):
    """Genera INDEX.md con tabla resumen de todos los autores normalizados"""
    
    total_obras = len(works_metadata)
    obras_con_autor = works_metadata[works_metadata['author_normalized'].notna()]
    obras_sin_autor = works_metadata[works_metadata['author_confidence'] == 'missing']
    obras_low_inferred = works_metadata[works_metadata['author_confidence'] == 'low_inferred']
    
    index = f"""# Índice de Reportes por Autor (Normalizado)

**Corpus Etnográfico Galicia**  
**Fecha de generación**: 24 de febrero de 2026  
**Diccionario**: escenas_minimas_v2.yml

---

## 📊 Cobertura del Corpus

- **Total obras TEI**: {total_obras}
- **Obras con autor identificado**: {len(obras_con_autor)} ({len(obras_con_autor)/total_obras*100:.1f}%)
  - De TEI (high/medium confidence): {len(obras_con_autor) - len(obras_low_inferred)}
  - Inferidas desde filename (low_inferred): {len(obras_low_inferred)}
- **Obras sin autor (missing)**: {len(obras_sin_autor)} ({len(obras_sin_autor)/total_obras*100:.1f}%)

---

## 📚 Autores Analizados (Normalizados)

| Autor (Normalizado) | N° Obras | Confianza | Tokens Totales | Casos Totales | Top 3 Escenas | Reporte |
|-------|----------|:---:|----------------|---------------|---------------|---------|
"""
    
    for stat in author_stats:
        author_normalized = stat['author_normalized']
        author_norm_key = stat['author_norm_key']
        n_obras = stat['n_obras']
        n_high = stat['n_high_confidence']
        n_low = stat['n_low_inferred']
        tokens = stat['tokens_total']
        cases = stat['cases_total']
        top3 = ', '.join(stat['top3_escenas'][:3]) if stat['top3_escenas'] else 'N/A'
        
        # Mostrar confianza
        if n_low > 0:
            confidence_str = f"{n_high}(H) + {n_low}(L)"
        else:
            confidence_str = f"{n_high}(H)"
        
        link = f"[Ver]({author_norm_key}/REPORT.md)"
        
        index += f"| {author_normalized} | {n_obras} | {confidence_str} | {tokens:,} | {cases} | {top3} | {link} |\n"
    
    index += f"""
---

## ⚠️ Obras sin autor identificado (missing)

Total: {len(obras_sin_autor)} obra(s)

| obra_id | title | why_missing |
|---------|-------|-------------|
"""
    
    if len(obras_sin_autor) > 0:
        for _, row in obras_sin_autor.iterrows():
            index += f"| {row['obra_id']} | {row['title']} | {row['why_missing']} |\n"
    
    index += f"""
---

## 📋 Convenciones de Confianza

- **H (high/medium)**: Autor extraído directamente desde TEI headers
- **L (low_inferred)**: Autor inferido desde filename (confidence=low_inferred)
- **Leyenda**: "3(H) + 1(L)" significa 3 obras de alta confianza + 1 obra inferida

---

**Metodología**: 
- Metadata extraída de TEI headers (`teiHeader/fileDesc/titleStmt/author`)
- Autores normalizados según `02_methods/patterns/author_normalization.yml`
- Clustering por `author_normalized` (forma canónica)
- Transparencia: columnas `author_confidence` y `why_missing` en source CSV
"""
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(index, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='Genera reportes por autor (v3: normalizado)')
    parser.add_argument('--cases', required=True, help='Path a cases_raw.csv')
    parser.add_argument('--units', required=True, help='Path a units.csv')
    parser.add_argument('--works-metadata', required=True, help='Path a works_metadata_from_tei.csv')
    parser.add_argument('--cooc', help='Path a cooc_pairs.csv (opcional)')
    parser.add_argument('--output', required=True, help='Directorio base de output')
    
    args = parser.parse_args()
    
    # Cargar datos
    print("📂 Cargando datos...")
    cases, units, works_metadata, cooc = load_data(
        args.cases, 
        args.units, 
        args.works_metadata,
        args.cooc
    )
    
    output_base = Path(args.output)
    output_base.mkdir(parents=True, exist_ok=True)
    
    # Obtener autores únicos normalizados (excluir missing)
    autores_norm = works_metadata[
        works_metadata['author_normalized'].notna()
    ]['author_normalized'].unique()
    
    print(f"\n🔄 Procesando {len(autores_norm)} autores normalizados...")
    
    author_stats = []
    for author_normalized in sorted(autores_norm):
        # Generar author_norm_key (slug)
        author_norm_key = works_metadata[
            works_metadata['author_normalized'] == author_normalized
        ]['author_norm_key'].iloc[0]
        
        stat = process_author(author_normalized, author_norm_key, cases, units, works_metadata, cooc, output_base)
        if stat:
            author_stats.append(stat)
    
    # Generar INDEX.md
    print(f"\n📝 Generando INDEX.md...")
    index_path = output_base / 'INDEX.md'
    generate_index(author_stats, works_metadata, index_path)
    
    print(f"\n✅ Reportes generados en: {output_base}")
    print(f"✅ INDEX creado en: {index_path}")
    print(f"\n📊 Total procesados: {len(author_stats)} autores normalizados")


if __name__ == '__main__':
    main()

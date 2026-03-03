#!/usr/bin/env python3
"""
rebuild_master_with_full_tokens.py
Reconstruye corpus_master_table y tablas derivadas usando tokens_total_full.
- Carga work_tokens_full.csv
- Mergea con metadatos
- Recalcula densidades (emigrant_rate_per_1k_tokens)
- Detecta mismatches entre tokens_snippet vs tokens_full
- Salva versiones v2tokens

Fase 11.5: BUGFIX Tokens
"""

import pandas as pd
from pathlib import Path

TABLES_DIR = Path(__file__).parent.parent.parent / "04_outputs" / "tables"

def load_work_tokens_full() -> pd.DataFrame:
    """Carga work_tokens_full.csv."""
    df = pd.read_csv(TABLES_DIR / "work_tokens_full.csv")
    print(f"[tokens_full] Cargados {len(df)} obras con tokens completos")
    return df

def load_corpus_master_table() -> pd.DataFrame:
    """Carga tabla maestra (con tokens_total antiguos)."""
    df = pd.read_csv(TABLES_DIR / "corpus_master_table.csv")
    print(f"[master] Cargada tabla maestra original ({len(df)} obras)")
    return df

def detect_mismatches(master: pd.DataFrame, tokens_full: pd.DataFrame) -> pd.DataFrame:
    """Detecta works donde hay mismatch significativo entre tokens_total vs tokens_full."""
    merged = master.merge(
        tokens_full[['obra_id', 'tokens_total_full']],
        on='obra_id',
        how='left'
    )
    
    # Calcular diferencia porcentual (relativa a tokens_full)
    merged['token_diff_pct'] = 0.0
    
    # Evitar división por cero
    mask = merged['tokens_total_full'] > 0
    merged.loc[mask, 'token_diff_pct'] = (
        (merged.loc[mask, 'tokens_total'] - merged.loc[mask, 'tokens_total_full']) / 
        merged.loc[mask, 'tokens_total_full']
    ) * 100
    
    # Flag si diferencia > 20%
    merged['token_mismatch_flag'] = (merged['token_diff_pct'].abs() > 20).astype(int)
    
    return merged

def rebuild_master_table(master: pd.DataFrame, tokens_full: pd.DataFrame) -> pd.DataFrame:
    """Reconstruye tabla maestra con tokens_total_full."""
    # Mergear
    result = master.copy()
    
    # Unir tokens_full
    tokens_for_merge = tokens_full[['obra_id', 'tokens_total_full']].copy()
    result = result.merge(tokens_for_merge, on='obra_id', how='left')
    
    # Reemplazar tokens_total por tokens_total_full
    result['tokens_total_old'] = result['tokens_total']
    result['tokens_total'] = result['tokens_total_full'].fillna(result['tokens_total_old']).astype(int)
    
    # Recalcular emigrant_rate_per_1k_tokens
    result['emigrant_rate_per_1k_tokens'] = (
        result['n_emigrant_mentions'] / result['tokens_total'] * 1000
    ).round(2)
    
    # Detectar mismatches
    result['token_mismatch_flag'] = 0
    mask = result['tokens_total_full'] > 0
    diff_pct = ((result.loc[mask, 'tokens_total_old'] - result.loc[mask, 'tokens_total_full']) / 
                result.loc[mask, 'tokens_total_full'] * 100).abs()
    result.loc[mask, 'token_mismatch_flag'] = (diff_pct > 20).astype(int)
    
    # Reordenar columnas (preservar genre_norm si existe)
    cols_order = [
        'obra_id', 'title', 'author_normalized', 'year', 'decade',
        'genre_norm', 'genre_raw', 'genre_confidence',
        'tokens_total', 'tokens_total_old', 'tokens_total_full',
        'n_cases_total', 'n_emigrant_mentions', 'emigrant_rate_per_1k_tokens',
        'top_3_scenes_by_rate', 'top_3_emigrant_markers',
        'year_missing', 'format_missing', 'genre_missing_flag', 'tokens_low', 'token_mismatch_flag'
    ]
    
    result = result[[c for c in cols_order if c in result.columns]]
    result = result.sort_values(['author_normalized', 'year']).reset_index(drop=True)
    
    print(f"[rebuild] Tabla maestra reconstruida con tokens_full")
    print(f"  - Obras con mismatch >20%: {result['token_mismatch_flag'].sum()}")
    
    return result

def rebuild_summary_tables(master: pd.DataFrame) -> tuple:
    """Reconstruye tablas de síntesis usando tokens_full."""
    
    # by_author
    by_author = master.groupby('author_normalized').agg({
        'obra_id': 'count',
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
    }).reset_index()
    
    by_author = by_author.rename(columns={'obra_id': 'n_obras'})
    by_author['emigrant_rate_per_1k_tokens'] = (
        by_author['n_emigrant_mentions'] / by_author['tokens_total'] * 1000
    ).round(2)
    by_author['top_markers'] = ''
    
    by_author = by_author[[
        'author_normalized', 'n_obras', 'tokens_total',
        'n_emigrant_mentions', 'emigrant_rate_per_1k_tokens', 'top_markers'
    ]].sort_values('emigrant_rate_per_1k_tokens', ascending=False)
    
    print(f"[by_author] {len(by_author)} autores")
    
    # by_decade
    master_with_year = master[master['decade'] != 'unknown_year'].copy()
    
    by_decade = master_with_year.groupby('decade').agg({
        'obra_id': 'count',
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
        'n_cases_total': 'sum'
    }).reset_index()
    
    by_decade = by_decade.rename(columns={'obra_id': 'n_obras'})
    by_decade['emigrant_rate_per_1k_tokens'] = (
        by_decade['n_emigrant_mentions'] / by_decade['tokens_total'] * 1000
    ).round(2)
    by_decade['top_markers'] = ''
    
    decade_order = ['1860s', '1870s', '1880s', '1890s', '1900s', '1910s', '1920s', '1930s', '1940s', '1950s']
    by_decade['decade_sort'] = by_decade['decade'].apply(
        lambda x: decade_order.index(x) if x in decade_order else 999
    )
    by_decade = by_decade.sort_values('decade_sort').drop('decade_sort', axis=1)
    
    print(f"[by_decade] {len(by_decade)} décadas")
    
    # by_format (usar genre_norm si existe, sino inferir)
    master_fmt = master.copy()
    if 'genre_norm' in master_fmt.columns:
        format_col = 'genre_norm'
    else:
        # Fallback: inferir de title (legacy)
        def infer_format(title: str) -> str:
            title_lower = str(title).lower()
            if any(word in title_lower for word in ['novela', 'romance', 'história']):
                return 'novela'
            elif any(word in title_lower for word in ['cantares', 'poema', 'follas']):
                return 'poesía'
            elif any(word in title_lower for word in ['historia', 'crónica', 'relación']):
                return 'crónica'
            else:
                return 'unknown'
        
        master_fmt['inferred_format'] = master_fmt['title'].apply(infer_format)
        format_col = 'inferred_format'
    
    by_format = master_fmt.groupby(format_col).agg({
        'obra_id': 'count',
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
        'n_cases_total': 'sum'
    }).reset_index()
    
    by_format = by_format.rename(columns={
        'obra_id': 'n_obras',
        format_col: 'format'
    })
    
    by_format['emigrant_rate_per_1k_tokens'] = (
        by_format['n_emigrant_mentions'] / by_format['tokens_total'] * 1000
    ).round(2)
    by_format['top_markers'] = ''
    
    by_format = by_format[[
        'format', 'n_obras', 'tokens_total',
        'n_emigrant_mentions', 'emigrant_rate_per_1k_tokens', 'top_markers'
    ]].sort_values('emigrant_rate_per_1k_tokens', ascending=False)
    
    print(f"[by_format] {len(by_format)} formatos")
    
    return by_author, by_decade, by_format

def main():
    """Ejecuta reconstrucción con tokens_full."""
    print("\n" + "="*70)
    print("REBUILD_MASTER_WITH_FULL_TOKENS: Corrección de denominadores")
    print("="*70 + "\n")
    
    # Cargar datos
    tokens_full = load_work_tokens_full()
    master = load_corpus_master_table()
    
    # Reconstruir tabla maestra
    master_v2tokens = rebuild_master_table(master, tokens_full)
    
    # Reconstruir tablas de síntesis
    by_author, by_decade, by_format = rebuild_summary_tables(master_v2tokens)
    
    # Salvar
    master_v2tokens.to_csv(TABLES_DIR / "corpus_master_table_v2tokens.csv", index=False)
    print(f"✅ corpus_master_table_v2tokens.csv guardado")
    
    by_author.to_csv(TABLES_DIR / "emigrant_by_author_v2tokens.csv", index=False)
    print(f"✅ emigrant_by_author_v2tokens.csv guardado")
    
    by_decade.to_csv(TABLES_DIR / "emigrant_by_decade_v2tokens.csv", index=False)
    print(f"✅ emigrant_by_decade_v2tokens.csv guardado")
    
    by_format.to_csv(TABLES_DIR / "emigrant_by_format_v2tokens.csv", index=False)
    print(f"✅ emigrant_by_format_v2tokens.csv guardado")
    
    # Mostrar obras con mismatches
    print("\n" + "="*70)
    print("OBRAS CON MISMATCH DE TOKENS (>20% diferencia):")
    print("="*70)
    mismatches = master_v2tokens[master_v2tokens['token_mismatch_flag'] == 1]
    if len(mismatches) > 0:
        print(mismatches[['obra_id', 'tokens_total_old', 'tokens_total_full', 'tokens_total']].to_string(index=False))
    else:
        print("(Ninguno detectado)")
    
    print("\n" + "="*70)
    print("RESUMEN:")
    print(f"  - Corpus total: {len(master_v2tokens)} obras")
    print(f"  - Tokens totales (nuevo): {master_v2tokens['tokens_total'].sum():,}")
    print(f"  - Tokens totales (antiguo): {master['tokens_total'].sum():,}")
    print(f"  - Diferencia: {(master_v2tokens['tokens_total'].sum() - master['tokens_total'].sum()):,} tokens")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

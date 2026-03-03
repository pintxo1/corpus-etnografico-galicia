#!/usr/bin/env python3
"""
generate_summary_tables.py
Genera tablas de síntesis: por autor, década, formato.
Normaliza por tokens para comparabilidad.

Fase 11: Evidence Pack
"""

import argparse
import pandas as pd
from pathlib import Path

TABLES_DIR = Path(__file__).parent.parent.parent / "04_outputs" / "tables"

def load_master_table(master_file: Path) -> pd.DataFrame:
    """Carga tabla maestra."""
    df = pd.read_csv(master_file)
    print(f"[master] Cargadas {len(df)} obras")
    return df

def generate_by_author(master: pd.DataFrame) -> pd.DataFrame:
    """Tabla por autor_normalized."""
    by_author = master.groupby('author_normalized').agg({
        'obra_id': 'count',
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
        'n_cases_total': 'sum'
    }).reset_index()
    
    by_author = by_author.rename(columns={'obra_id': 'n_obras'})
    
    # Calcular rate per 1k tokens
    by_author['emigrant_rate_per_1k_tokens'] = (
        by_author['n_emigrant_mentions'] / by_author['tokens_total'] * 1000
    ).round(2)
    
    # Agregar top markers (aproximado: contar menciones por autor)
    by_author['top_markers'] = ''  # Se llenará después si hay datos disponibles
    
    # Reordenar
    by_author = by_author[[
        'author_normalized', 'n_obras', 'tokens_total', 
        'n_emigrant_mentions', 'emigrant_rate_per_1k_tokens', 'top_markers'
    ]].sort_values('emigrant_rate_per_1k_tokens', ascending=False)
    
    print(f"[by_author] {len(by_author)} autores")
    return by_author

def generate_by_decade(master: pd.DataFrame) -> pd.DataFrame:
    """Tabla por década."""
    # Filtrar solo años conocidos
    master_with_year = master[master['decade'] != 'unknown_year'].copy()
    
    by_decade = master_with_year.groupby('decade').agg({
        'obra_id': 'count',
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
        'n_cases_total': 'sum'
    }).reset_index()
    
    by_decade = by_decade.rename(columns={'obra_id': 'n_obras'})
    
    # Calcular rate per 1k tokens
    by_decade['emigrant_rate_per_1k_tokens'] = (
        by_decade['n_emigrant_mentions'] / by_decade['tokens_total'] * 1000
    ).round(2)
    
    by_decade['top_markers'] = ''
    
    # Ordenar por década
    decade_order = ['1860s', '1870s', '1880s', '1890s', '1900s', '1910s', '1920s', '1930s', '1940s', '1950s']
    by_decade['decade_sort'] = by_decade['decade'].apply(
        lambda x: decade_order.index(x) if x in decade_order else 999
    )
    by_decade = by_decade.sort_values('decade_sort').drop('decade_sort', axis=1)
    
    print(f"[by_decade] {len(by_decade)} décadas")
    return by_decade

def generate_by_format(master: pd.DataFrame) -> pd.DataFrame:
    """Tabla por formato/género (genre_norm extraído de TEI)."""
    # Preferir columna format si existe; fallback a genre_norm
    if 'format' in master.columns and master['format'].notna().any():
        format_col = 'format'
    elif 'genre_norm' in master.columns:
        format_col = 'genre_norm'
    else:
        # Fallback: inferir de title (legacy)
        def infer_format(title: str) -> str:
            title_lower = str(title).lower()
            if any(word in title_lower for word in ['novela', 'romance', 'historia']):
                return 'novela'
            if any(word in title_lower for word in ['cantares', 'poema', 'follas']):
                return 'poesia'
            if any(word in title_lower for word in ['historia', 'cronica', 'relacion']):
                return 'cronica'
            return 'unknown'
        master = master.copy()
        master['genre_norm'] = master['title'].apply(infer_format)
        format_col = 'genre_norm'
    
    by_format = master.groupby(format_col).agg({
        'obra_id': 'count',
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
        'n_cases_total': 'sum'
    }).reset_index()
    
    by_format = by_format.rename(columns={
        'obra_id': 'n_obras',
        format_col: 'format'
    })
    
    # Calcular rate per 1k tokens
    by_format['emigrant_rate_per_1k_tokens'] = (
        by_format['n_emigrant_mentions'] / by_format['tokens_total'] * 1000
    ).round(2)
    
    by_format['top_markers'] = ''
    
    # Reordenar
    by_format = by_format[[
        'format', 'n_obras', 'tokens_total', 
        'n_emigrant_mentions', 'emigrant_rate_per_1k_tokens', 'top_markers'
    ]].sort_values('emigrant_rate_per_1k_tokens', ascending=False)
    
    print(f"[by_format] {len(by_format)} formatos/géneros")
    return by_format

def main():
    """Genera y salva tablas de síntesis."""
    parser = argparse.ArgumentParser(description="Genera tablas de sintesis (autor/decada/formato)")
    parser.add_argument(
        "--master-table",
        default=str(TABLES_DIR / "corpus_master_table_v2tokens_meta.csv"),
        help="Ruta a tabla maestra (default: corpus_master_table_v2tokens_meta.csv)"
    )
    parser.add_argument(
        "--output-suffix",
        default="",
        help="Sufijo opcional para outputs (ej: v2tokens)"
    )
    args = parser.parse_args()
    suffix = f"_{args.output_suffix}" if args.output_suffix else ""
    print("\n" + "="*70)
    print("GENERATE_SUMMARY_TABLES: Síntesis por autor/década/formato")
    print("="*70 + "\n")
    
    master_path = Path(args.master_table)
    if not master_path.exists():
        fallback = TABLES_DIR / "corpus_master_table_v2tokens.csv"
        master_path = fallback if fallback.exists() else master_path
    master = load_master_table(master_path)
    
    # Generar tablas
    by_author = generate_by_author(master)
    by_decade = generate_by_decade(master)
    by_format = generate_by_format(master)
    
    # Salvar
    by_author_file = TABLES_DIR / f"emigrant_by_author{suffix}.csv"
    by_author.to_csv(by_author_file, index=False)
    print(f"✅ {by_author_file.name} guardado")
    
    by_decade_file = TABLES_DIR / f"emigrant_by_decade{suffix}.csv"
    by_decade.to_csv(by_decade_file, index=False)
    print(f"✅ {by_decade_file.name} guardado")
    
    by_format_file = TABLES_DIR / f"emigrant_by_format{suffix}.csv"
    by_format.to_csv(by_format_file, index=False)
    print(f"✅ {by_format_file.name} guardado")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()

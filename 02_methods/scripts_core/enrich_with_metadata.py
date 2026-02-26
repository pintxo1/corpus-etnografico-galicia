#!/usr/bin/env python3
"""
enrich_with_metadata.py
Enriquece datasets con year/decade a partir de works_metadata_from_tei.csv
y construye tabla maestra del corpus (corpus_master_table.csv).

Fase 11: Evidence Pack Etnografía Digital Computerizada
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import math

# Configuración de rutas
BASE_DIR = Path(__file__).parent.parent.parent
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"
DATA_DIR = BASE_DIR / "01_data"
ANALYSIS_DIR = BASE_DIR / "03_analysis" / "cases"

def year_to_decade(year: float) -> str:
    """Convierte year a decade (1886 -> 1880s), maneja NaN."""
    if pd.isna(year):
        return "unknown_year"
    year_int = int(year)
    decade_start = (year_int // 10) * 10
    return f"{decade_start}s"

def load_metadata() -> pd.DataFrame:
    """Carga works_metadata_from_tei.csv y añade decade."""
    metadata_file = TABLES_DIR / "works_metadata_from_tei.csv"
    df = pd.read_csv(metadata_file)
    
    # Agregar columna decade
    df['decade'] = df['year'].apply(year_to_decade)
    
    # Marcar year_missing
    df['year_missing'] = df['year'].isna().astype(int)
    
    print(f"[metadata] Cargadas {len(df)} obras")
    print(f"  - year disponibles: {(~df['year'].isna()).sum()}/{len(df)}")
    print(f"  - decadas: {sorted(df['decade'].unique())}")
    
    return df

def load_token_totals() -> pd.DataFrame:
    """Carga token_totals.csv."""
    tokens_file = TABLES_DIR / "token_totals.csv"
    df = pd.read_csv(tokens_file)
    print(f"[tokens] Cargados tokens para {len(df)} obras")
    return df

def load_case_rankings() -> pd.DataFrame:
    """Carga case_rankings.csv y cuenta casos por obra/escena."""
    rankings_file = TABLES_DIR / "case_rankings.csv"
    df = pd.read_csv(rankings_file)
    
    # Contar casos totales por obra
    cases_by_obra = df.groupby('obra_id').size().reset_index(name='n_cases_total')
    
    # Contar casos por escena y obra
    cases_by_escena = df.groupby(['obra_id', 'escena_tipo']).size().reset_index(name='n_escena')
    
    # Top 3 escenas por obra (por frecuencia)
    top_scenes = cases_by_escena.sort_values(['obra_id', 'n_escena'], ascending=[True, False])
    top_scenes_grouped = top_scenes.groupby('obra_id').head(3)
    top_scenes_str = top_scenes_grouped.groupby('obra_id').apply(
        lambda x: ' | '.join([f"{row['escena_tipo']}({row['n_escena']})" for _, row in x.iterrows()])
    ).reset_index(name='top_3_scenes_by_rate')
    
    result = cases_by_obra.merge(top_scenes_str, on='obra_id', how='left')
    result['top_3_scenes_by_rate'] = result['top_3_scenes_by_rate'].fillna('')
    
    print(f"[cases] Contabilizados {df.shape[0]} casos en {len(cases_by_obra)} obras")
    return result

def load_emigrant_mentions() -> pd.DataFrame:
    """Carga emigrant_mentions_by_work.csv."""
    emigrant_file = TABLES_DIR / "emigrant_mentions_by_work.csv"
    df = pd.read_csv(emigrant_file)
    
    # Renombrar columnas para claridad
    df = df.rename(columns={
        'n_mentions': 'n_emigrant_mentions',
        'density_per_1k_tokens': 'emigrant_rate_per_1k_tokens'
    })
    
    # Extraer top 3 marcadores por obra (si existe archivo)
    try:
        kwic_file = ANALYSIS_DIR / "emigrante_kwic_cases.csv"
        if kwic_file.exists():
            kwic_df = pd.read_csv(kwic_file)
            # Contar menciones por marcador y obra
            marker_counts = kwic_df.groupby(['obra_id', 'marker']).size().reset_index(name='count')
            top_markers = marker_counts.sort_values(['obra_id', 'count'], ascending=[True, False])
            top_markers_grouped = top_markers.groupby('obra_id').head(3)
            top_markers_str = top_markers_grouped.groupby('obra_id').apply(
                lambda x: ' | '.join([f"{row['marker']}({row['count']})" for _, row in x.iterrows()])
            ).reset_index(name='top_3_emigrant_markers')
            df = df.merge(top_markers_str, on='obra_id', how='left')
            df['top_3_emigrant_markers'] = df['top_3_emigrant_markers'].fillna('')
        else:
            df['top_3_emigrant_markers'] = ''
    except Exception as e:
        print(f"[warning] No se pudo procesar top 3 markers: {e}")
        df['top_3_emigrant_markers'] = ''
    
    print(f"[emigrant] Cargadas menciones para {len(df)} obras")
    return df

def build_master_table(metadata: pd.DataFrame, 
                       tokens: pd.DataFrame,
                       case_counts: pd.DataFrame,
                       emigrant: pd.DataFrame) -> pd.DataFrame:
    """Construye tabla maestra del corpus."""
    
    # Merge todos los datos
    master = metadata[['obra_id', 'title', 'author_normalized', 'year', 'decade', 'year_missing']].copy()
    
    # Agregar tokens
    master = master.merge(tokens[['obra_id', 'tokens_total']], on='obra_id', how='left')
    master['tokens_total'] = master['tokens_total'].fillna(0).astype(int)
    
    # Agregar conteos de casos
    master = master.merge(case_counts[['obra_id', 'n_cases_total', 'top_3_scenes_by_rate']], 
                         on='obra_id', how='left')
    master['n_cases_total'] = master['n_cases_total'].fillna(0).astype(int)
    master['top_3_scenes_by_rate'] = master['top_3_scenes_by_rate'].fillna('')
    
    # Agregar menciones emigrante
    emigrant_cols = ['obra_id', 'n_emigrant_mentions', 'emigrant_rate_per_1k_tokens', 'top_3_emigrant_markers']
    master = master.merge(emigrant[[c for c in emigrant_cols if c in emigrant.columns]], 
                         on='obra_id', how='left')
    master['n_emigrant_mentions'] = master['n_emigrant_mentions'].fillna(0).astype(int)
    master['emigrant_rate_per_1k_tokens'] = master['emigrant_rate_per_1k_tokens'].fillna(0.0)
    master['top_3_emigrant_markers'] = master['top_3_emigrant_markers'].fillna('')
    
    # Flags de calidad
    master['format_missing'] = 1  # Por ahora todos sin formato explícito
    master['tokens_low'] = (master['tokens_total'] < 1000).astype(int)
    
    # Reordenar columnas
    master = master[[
        'obra_id', 'title', 'author_normalized', 'year', 'decade',
        'tokens_total', 'n_cases_total', 'n_emigrant_mentions', 'emigrant_rate_per_1k_tokens',
        'top_3_scenes_by_rate', 'top_3_emigrant_markers',
        'year_missing', 'format_missing', 'tokens_low'
    ]]
    
    master = master.sort_values(['author_normalized', 'year']).reset_index(drop=True)
    
    print(f"[master] Tabla maestra construida: {master.shape[0]} obras x {master.shape[1]} columnas")
    return master

def enrich_existing_files(metadata: pd.DataFrame):
    """Enriquece archivos existentes con year/decade."""
    
    # units.csv
    try:
        units_file = DATA_DIR / "text" / "units.csv"
        units_df = pd.read_csv(units_file)
        units_enrich = units_df.merge(
            metadata[['obra_id', 'year', 'decade']], 
            on='obra_id', 
            how='left'
        )
        units_enrich.to_csv(
            TABLES_DIR / "units_enriched.csv", 
            index=False
        )
        print(f"[enrich] units_enriched.csv guardado ({len(units_enrich)} filas)")
    except Exception as e:
        print(f"[warning] Error enriqueciendo units.csv: {e}")
    
    # case_rankings.csv
    try:
        rankings_file = TABLES_DIR / "case_rankings.csv"
        rankings_df = pd.read_csv(rankings_file)
        rankings_enrich = rankings_df.merge(
            metadata[['obra_id', 'year', 'decade']], 
            on='obra_id', 
            how='left'
        )
        rankings_enrich.to_csv(
            TABLES_DIR / "case_rankings_enriched.csv", 
            index=False
        )
        print(f"[enrich] case_rankings_enriched.csv guardado ({len(rankings_enrich)} filas)")
    except Exception as e:
        print(f"[warning] Error enriqueciendo case_rankings.csv: {e}")
    
    # emigrant_mentions_by_work.csv ya tiene year; agregar decade
    try:
        emigrant_file = TABLES_DIR / "emigrant_mentions_by_work.csv"
        emigrant_df = pd.read_csv(emigrant_file)
        emigrant_df['decade'] = emigrant_df['year'].apply(year_to_decade)
        emigrant_df.to_csv(
            TABLES_DIR / "emigrant_mentions_by_work_enriched.csv", 
            index=False
        )
        print(f"[enrich] emigrant_mentions_by_work_enriched.csv guardado ({len(emigrant_df)} filas)")
    except Exception as e:
        print(f"[warning] Error enriqueciendo emigrant_mentions_by_work.csv: {e}")

def main():
    """Ejecuta enriquecimiento y genera tabla maestra."""
    print("\n" + "="*70)
    print("ENRICH_WITH_METADATA: Enriquecimiento + Tabla Maestra Corpus")
    print("="*70 + "\n")
    
    # Cargar datos
    metadata = load_metadata()
    tokens = load_token_totals()
    case_counts = load_case_rankings()
    emigrant = load_emigrant_mentions()
    
    # Construir tabla maestra
    master_table = build_master_table(metadata, tokens, case_counts, emigrant)
    
    # Salvar tabla maestra
    output_file = TABLES_DIR / "corpus_master_table.csv"
    master_table.to_csv(output_file, index=False)
    print(f"\n✅ corpus_master_table.csv guardado: {output_file}")
    
    # Enriquecer archivos existentes
    print("\n[enrich] Enriqueciendo archivos existentes...")
    enrich_existing_files(metadata)
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN:")
    print(f"  - Corpus total: {len(master_table)} obras")
    print(f"  - Con year: {(~master_table['year'].isna()).sum()}")
    print(f"  - Con menciones emigrante: {(master_table['n_emigrant_mentions'] > 0).sum()}")
    print(f"  - Tokens totales: {master_table['tokens_total'].sum():,}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
emigrant_heatmap_author_decade_expanded.py - Heatmap década × autor CON TODOS
los autores relevantes (según criterios de inclusión), + categoría otros_autores.

PROMPT 2: Arreglar heatmap "solo 3 autores" para mostrar todos los relevantes.

Criterio de inclusión (configurable):
  - tokens_total_author >= MIN_TOKENS
  - n_emigrant_mentions_author >= MIN_MENTIONS

Genera:
  - Versión: top12 (para legibilidad)
  - Versión: full+otros (todos los autores + agregado)
"""

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_export import save_figure_variants

BASE_DIR = Path(__file__).parent.parent.parent
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"
FIGURES_DIR = BASE_DIR / "04_outputs" / "figures" / "static"

# Configuración estética
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

def load_master_table() -> pd.DataFrame:
    """Carga tabla maestra."""
    master_file = TABLES_DIR / "corpus_master_table_v2tokens_meta.csv"
    if not master_file.exists():
        master_file = TABLES_DIR / "corpus_master_table_v2tokens.csv"
    df = pd.read_csv(master_file)
    print(f"[master] Cargadas {len(df)} obras")
    return df

def calculate_author_inclusion(master: pd.DataFrame, min_tokens: int = 10000, min_mentions: int = 10) -> tuple:
    """
    Calcula qué autores incluir según criterios.
    Retorna: (included_df, exclusion_detail)
    """
    # Agregar por autor
    author_stats = master.groupby('author_normalized').agg({
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
    }).reset_index()
    
    author_stats['emigrant_rate_per_1k'] = (
        author_stats['n_emigrant_mentions'] / author_stats['tokens_total'] * 1000
    )
    
    # Aplicar criterios
    author_stats['included'] = (
        (author_stats['tokens_total'] >= min_tokens) &
        (author_stats['n_emigrant_mentions'] >= min_mentions)
    )
    
    author_stats['reason'] = author_stats.apply(
        lambda row: 'included' if row['included'] else
        ('low_tokens' if row['tokens_total'] < min_tokens else 'low_mentions'),
        axis=1
    )
    
    # Retornar incluidos e informe
    included_authors = author_stats[author_stats['included']]['author_normalized'].tolist()
    excluded_detail = author_stats[~author_stats['included']].copy()
    
    print(f"\n[inclusion] Autores a incluir: {len(included_authors)}")
    print(f"[inclusion] Autores excluidos: {len(excluded_detail)}")
    
    if len(excluded_detail) > 0:
        print(f"\n  Exclusion reasons:")
        print(f"    - Low tokens (<{min_tokens}): {(excluded_detail['reason'] == 'low_tokens').sum()}")
        print(f"    - Low mentions (<{min_mentions}): {(excluded_detail['reason'] == 'low_mentions').sum()}")
    
    return included_authors, author_stats

def create_decade_author_matrix(master: pd.DataFrame, included_authors: list) -> pd.DataFrame:
    """
    Crea matriz década × autor con tasas por 1k tokens.
    Includes columna "otros_autores" (sum de excluidos).
    """
    # Filtrar: autores incluidos + todos para "otros"
    master_included = master[master['author_normalized'].isin(included_authors)].copy()
    master_other = master[~master['author_normalized'].isin(included_authors)].copy()
    
    # Agregar por decade x author (incluidos)
    pivot_included = master_included.groupby(['decade', 'author_normalized']).agg({
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
    }).reset_index()
    
    # Agregar otros
    pivot_other = master_other.groupby('decade').agg({
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
    }).reset_index()
    pivot_other['author_normalized'] = 'otros_autores'
    
    # Combinar
    pivot_all = pd.concat([pivot_included, pivot_other], ignore_index=True)
    
    # Calcular tasa por 1k
    pivot_all['rate_per_1k'] = (
        pivot_all['n_emigrant_mentions'] / pivot_all['tokens_total'] * 1000
    )
    
    # Pivot para heatmap
    matrix = pivot_all.pivot_table(
        index='decade',
        columns='author_normalized',
        values='rate_per_1k',
        fill_value=0
    )
    
    # Ordenar décadas cronológicamente
    decade_order = ['1860s', '1880s', '1890s', '1900s', '1910s', '1920s', '1930s', '1950s', 'unknown_year']
    decade_order = [d for d in decade_order if d in matrix.index]
    matrix = matrix.loc[decade_order]
    
    # Reordenar columnas: autores por tokens totales, "otros_autores" al final
    if 'otros_autores' in matrix.columns:
        other_col = matrix.pop('otros_autores')
    else:
        other_col = None
    
    # Ordenar autores por tokens totales
    col_order = pivot_all.groupby('author_normalized')['tokens_total'].sum().sort_values(ascending=False).index.tolist()
    col_order = [c for c in col_order if c in matrix.columns]
    matrix = matrix[col_order]
    
    if other_col is not None:
        matrix['otros_autores'] = other_col
    
    return matrix

def generate_heatmap_full(matrix: pd.DataFrame, output_prefix: str):
    """Genera heatmap full con todos los autores + otros."""
    fig, ax = plt.subplots(figsize=(18, 8))
    
    # Heatmap
    sns.heatmap(
        matrix,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Rate per 1k tokens'},
        ax=ax,
        linewidths=0.5,
        linecolor='gray'
    )
    
    ax.set_title('Emigrant Representation by Decade and Author\n(All relevant authors + others aggregated)',
                fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Author', fontsize=11, fontweight='bold')
    ax.set_ylabel('Decade', fontsize=11, fontweight='bold')
    
    # Rotación de etiquetas
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)
    
    plt.tight_layout()
    
    base_path = FIGURES_DIR / f"{output_prefix}_full"
    save_figure_variants(fig, base_path, dpi=300, save_png=True, save_pdf=True, save_jpeg=True, jpeg_quality=95)
    plt.close()

def generate_heatmap_top12(matrix: pd.DataFrame, output_prefix: str, n_top: int = 12):
    """Genera heatmap top N autores para legibilidad."""
    # Seleccionar top N + otros
    cols_to_keep = list(matrix.columns[:n_top])
    if 'otros_autores' in matrix.columns and 'otros_autores' not in cols_to_keep:
        cols_to_keep.append('otros_autores')
    
    matrix_top = matrix[cols_to_keep]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Heatmap
    sns.heatmap(
        matrix_top,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Rate per 1k tokens'},
        ax=ax,
        linewidths=0.5,
        linecolor='gray'
    )
    
    ax.set_title(f'Emigrant Representation by Decade and Author\n(Top {n_top} authors + others)',
                fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Author', fontsize=11, fontweight='bold')
    ax.set_ylabel('Decade', fontsize=11, fontweight='bold')
    
    # Rotación de etiquetas
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=10)
    
    plt.tight_layout()
    
    base_path = FIGURES_DIR / f"{output_prefix}_top{n_top}"
    save_figure_variants(fig, base_path, dpi=300, save_png=True, save_pdf=True, save_jpeg=True, jpeg_quality=95)
    plt.close()

def save_inclusion_report(author_stats: pd.DataFrame, output_file: Path):
    """Guarda tabla de inclusión de autores."""
    author_stats = author_stats.sort_values('tokens_total', ascending=False)
    author_stats.to_csv(output_file, index=False)
    print(f"  ✓ {output_file.name}")

def main():
    parser = argparse.ArgumentParser(description="Heatmap década × autor expandido (todos los autores relevantes)")
    parser.add_argument('--min-tokens', type=int, default=10000, help='Tokens mínimos para inclusión (default: 10000)')
    parser.add_argument('--min-mentions', type=int, default=10, help='Menciones mínimas para inclusión (default: 10)')
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("EMIGRANT_HEATMAP_AUTHOR_DECADE_EXPANDED (PROMPT 2)")
    print("=" * 70 + "\n")
    
    # Crear directorios
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Cargar datos
    master = load_master_table()
    
    # Calcular inclusión
    included_authors, author_stats = calculate_author_inclusion(
        master,
        min_tokens=args.min_tokens,
        min_mentions=args.min_mentions
    )
    
    if len(included_authors) < 5:
        print(f"\n⚠️  WARNING: Solo {len(included_authors)} autores cumplen criterios (min_tokens={args.min_tokens}, min_mentions={args.min_mentions})")
        print("    Considera reducir umbrales si esto parece demasiado restrictivo.")
    
    # Crear matriz
    print("\n[matrix] Creando matriz década × autor...")
    matrix = create_decade_author_matrix(master, included_authors)
    print(f"  - Autores incluidos: {len(included_authors)}")
    print(f"  - Décadas: {len(matrix)}")
    print(f"  - Matriz shape: {matrix.shape}")
    
    # Guardar tablas de soporte
    print("\n[tables] Guardando tablas de soporte...")
    inclusion_file = TABLES_DIR / "emigrant_rate_decade_author_inclusion.csv"
    save_inclusion_report(author_stats, inclusion_file)
    
    matrix_file = TABLES_DIR / "emigrant_rate_decade_author.csv"
    matrix.to_csv(matrix_file)
    print(f"  ✓ {matrix_file.name}")
    
    # Generar figuras
    print("\n[figures] Generando heatmaps...")
    print("  Versión full (todos los autores):")
    generate_heatmap_full(matrix, "fig_emigrant_heatmap_decade_author")
    
    print("  Versión top12 (para legibilidad):")
    generate_heatmap_top12(matrix, "fig_emigrant_heatmap_decade_author")
    
    print("\n" + "=" * 70)
    print("✅ HEATMAP EXPANDIDO COMPLETADO")
    print("=" * 70)
    print(f"\nArchivos generados:")
    print(f"  Tablas:")
    print(f"    - emigrant_rate_decade_author.csv")
    print(f"    - emigrant_rate_decade_author_inclusion.csv")
    print(f"  Figuras:")
    print(f"    - fig_emigrant_heatmap_decade_author_full.{{png,pdf,jpeg}}")
    print(f"    - fig_emigrant_heatmap_decade_author_top12.{{png,pdf,jpeg}}")
    print()

if __name__ == "__main__":
    main()

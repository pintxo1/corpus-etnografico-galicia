#!/usr/bin/env python3
"""
temporal_composition_analysis.py - Análisis temporal de composición del corpus.

PROMPT 2 (Phase 12B): Controles temporales de composición
- Heatmaps década × autor con emigrant_rate_per_1k_tokens
- Evolución temporal por género
- Distribución de producción literaria por década

Genera:
- 04_outputs/tables/emigrant_decade_author_matrix.csv
- 04_outputs/figures/static/fig_emigrant_heatmap_decade_author.{png,pdf}
- 04_outputs/figures/static/fig_emigrant_temporal_by_genre.{png,pdf}
- 04_outputs/figures/static/fig_production_timeline.{png,pdf}
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

# Orden cronológico de décadas
DECADE_ORDER = ['1860s', '1870s', '1880s', '1890s', '1900s', '1910s', '1920s', '1930s', '1940s', '1950s']

def load_master_table(master_file: Path) -> pd.DataFrame:
    """Carga tabla maestra con metadata temporal."""
    df = pd.read_csv(master_file)
    print(f"[master] Cargadas {len(df)} obras")
    
    # Filtrar unknown_year para análisis temporal
    df_with_year = df[df['decade'] != 'unknown_year'].copy()
    print(f"[master] Obras con decade conocida: {len(df_with_year)}/{len(df)}")
    
    return df_with_year

def generate_decade_author_matrix(master: pd.DataFrame) -> pd.DataFrame:
    """
    Genera matriz década × autor con emigrant_rate_per_1k_tokens.
    
    Estrategia:
    - Filas: décadas (1860s-1950s)
    - Columnas: autores (top 10 por producción)
    - Valores: emigrant_rate_per_1k_tokens promedio en esa célula
    """
    # Filtrar autores con suficiente producción (mínimo 3 obras)
    author_counts = master['author_normalized'].value_counts()
    top_authors = author_counts[author_counts >= 3].index.tolist()
    
    print(f"[matrix] Autores con ≥3 obras: {len(top_authors)}")
    
    # Filtrar master a top autores
    master_filtered = master[master['author_normalized'].isin(top_authors)].copy()
    
    # Agrupar por década × autor, calcular rate medio ponderado por tokens
    pivot = master_filtered.groupby(['decade', 'author_normalized']).apply(
        lambda x: (x['n_emigrant_mentions'].sum() / x['tokens_total'].sum() * 1000) if x['tokens_total'].sum() > 0 else 0
    ).reset_index(name='emigrant_rate_per_1k_tokens')
    
    # Pivot a formato wide (decade × author)
    matrix = pivot.pivot(index='decade', columns='author_normalized', values='emigrant_rate_per_1k_tokens')
    
    # Reordenar filas por orden cronológico
    decades_present = [d for d in DECADE_ORDER if d in matrix.index]
    matrix = matrix.reindex(decades_present)
    
    # Ordenar columnas por rate total descendente
    author_totals = master_filtered.groupby('author_normalized').apply(
        lambda x: (x['n_emigrant_mentions'].sum() / x['tokens_total'].sum() * 1000) if x['tokens_total'].sum() > 0 else 0
    ).sort_values(ascending=False)
    
    matrix = matrix[author_totals.index]
    
    print(f"[matrix] Matriz década × autor: {matrix.shape[0]} décadas × {matrix.shape[1]} autores")
    
    return matrix

def generate_decade_author_heatmap(matrix: pd.DataFrame, output_prefix: str):
    """Genera heatmap década × autor."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Heatmap con seaborn
    sns.heatmap(
        matrix,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        cbar_kws={'label': 'Emigrant mentions per 1k tokens'},
        linewidths=0.5,
        linecolor='white',
        ax=ax,
        vmin=0,
        vmax=matrix.max().max() if matrix.max().max() > 0 else 5,
        mask=matrix.isna()
    )
    
    ax.set_xlabel('Author', fontsize=12, fontweight='bold')
    ax.set_ylabel('Decade', fontsize=12, fontweight='bold')
    ax.set_title('Emigrant Representation: Decade × Author Heatmap\n(Rate per 1k tokens)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    base_path = FIGURES_DIR / output_prefix
    save_figure_variants(fig, base_path, dpi=300, save_png=True, save_pdf=True, save_jpeg=True, jpeg_quality=95)
    plt.close()

def generate_temporal_by_genre(master: pd.DataFrame, output_prefix: str):
    """Genera gráfico de evolución temporal por género."""
    # Agrupar por década × género
    temporal = master.groupby(['decade', 'genre_norm']).apply(
        lambda x: pd.Series({
            'n_obras': len(x),
            'tokens_total': x['tokens_total'].sum(),
            'n_emigrant_mentions': x['n_emigrant_mentions'].sum(),
            'emigrant_rate': (x['n_emigrant_mentions'].sum() / x['tokens_total'].sum() * 1000) if x['tokens_total'].sum() > 0 else 0
        })
    ).reset_index()
    
    # Filtrar géneros principales (>= 5 obras en total)
    genre_counts = master['genre_norm'].value_counts()
    main_genres = genre_counts[genre_counts >= 5].index.tolist()
    temporal = temporal[temporal['genre_norm'].isin(main_genres)]
    
    # Ordenar por década
    temporal['decade_sort'] = temporal['decade'].apply(
        lambda x: DECADE_ORDER.index(x) if x in DECADE_ORDER else 999
    )
    temporal = temporal.sort_values('decade_sort')
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    
    # Panel 1: Rate por género
    for genre in main_genres:
        data = temporal[temporal['genre_norm'] == genre]
        ax1.plot(data['decade'], data['emigrant_rate'], marker='o', label=genre, linewidth=2)
    
    ax1.set_ylabel('Emigrant rate per 1k tokens', fontsize=11, fontweight='bold')
    ax1.set_title('Temporal Evolution of Emigrant Representation by Genre', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.legend(title='Genre', loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: Producción (n_obras) por género
    genre_production = temporal.groupby(['decade', 'genre_norm'])['n_obras'].sum().reset_index()
    decade_labels = sorted(temporal['decade'].unique(), key=lambda x: DECADE_ORDER.index(x) if x in DECADE_ORDER else 999)
    
    x = np.arange(len(decade_labels))
    width = 0.15
    
    for i, genre in enumerate(main_genres):
        data = genre_production[genre_production['genre_norm'] == genre]
        y = [data[data['decade'] == d]['n_obras'].sum() if d in data['decade'].values else 0 for d in decade_labels]
        ax2.bar(x + i * width, y, width, label=genre)
    
    ax2.set_xlabel('Decade', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Number of works', fontsize=11, fontweight='bold')
    ax2.set_title('Literary Production by Genre and Decade', fontsize=13, fontweight='bold', pad=15)
    ax2.set_xticks(x + width * (len(main_genres) - 1) / 2)
    ax2.set_xticklabels(decade_labels, rotation=45, ha='right')
    ax2.legend(title='Genre', loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    base_path = FIGURES_DIR / output_prefix
    save_figure_variants(fig, base_path, dpi=300, save_png=True, save_pdf=True, save_jpeg=True, jpeg_quality=95)
    plt.close()

def generate_production_timeline(master: pd.DataFrame, output_prefix: str):
    """Genera timeline de producción literaria (obras por década)."""
    # Agrupar por década
    production = master.groupby('decade').agg({
        'obra_id': 'count',
        'tokens_total': 'sum',
        'n_emigrant_mentions': 'sum',
        'author_normalized': lambda x: x.nunique()
    }).reset_index()
    
    production = production.rename(columns={
        'obra_id': 'n_obras',
        'author_normalized': 'n_authors'
    })
    
    # Calcular rate
    production['emigrant_rate'] = (production['n_emigrant_mentions'] / production['tokens_total'] * 1000).round(2)
    
    # Ordenar por década
    production['decade_sort'] = production['decade'].apply(
        lambda x: DECADE_ORDER.index(x) if x in DECADE_ORDER else 999
    )
    production = production.sort_values('decade_sort')
    
    # Plot
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    # Panel 1: Número de obras
    ax1.bar(production['decade'], production['n_obras'], color='steelblue', alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Number of works', fontsize=11, fontweight='bold')
    ax1.set_title('Corpus Production Timeline: Works, Authors, and Emigrant Representation', 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Panel 2: Número de autores
    ax2.bar(production['decade'], production['n_authors'], color='darkorange', alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Number of authors', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Panel 3: Emigrant rate
    ax3.plot(production['decade'], production['emigrant_rate'], marker='o', color='crimson', linewidth=2, markersize=8)
    ax3.set_xlabel('Decade', fontsize=11, fontweight='bold')
    ax3.set_ylabel('Emigrant rate per 1k tokens', fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    base_path = FIGURES_DIR / output_prefix
    save_figure_variants(fig, base_path, dpi=300, save_png=True, save_pdf=True, save_jpeg=True, jpeg_quality=95)
    plt.close()

def main():
    """Ejecuta análisis temporal de composición."""
    parser = argparse.ArgumentParser(description="Análisis temporal de composición del corpus")
    parser.add_argument(
        "--master-table",
        type=Path,
        default=TABLES_DIR / "corpus_master_table_v2tokens_meta.csv",
        help="Ruta a tabla maestra"
    )
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("TEMPORAL COMPOSITION ANALYSIS (PROMPT 2)")
    print("="*70 + "\n")
    
    # Crear directorio de figuras
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Cargar datos
    master_path = args.master_table
    if not master_path.exists():
        fallback = TABLES_DIR / "corpus_master_table_v2tokens.csv"
        master_path = fallback if fallback.exists() else master_path
    master = load_master_table(master_path)
    
    print("\n[1/3] Generando matriz década × autor...")
    matrix = generate_decade_author_matrix(master)
    
    # Guardar matriz
    matrix_file = TABLES_DIR / "emigrant_decade_author_matrix.csv"
    matrix.to_csv(matrix_file)
    print(f"  ✓ {matrix_file.name}")
    
    print("\n[2/3] Generando evolución temporal por género...")
    generate_temporal_by_genre(master, "fig_emigrant_temporal_by_genre")
    
    print("\n[3/3] Generando timeline de producción literaria...")
    generate_production_timeline(master, "fig_production_timeline")
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS TEMPORAL COMPLETADO")
    print("="*70)
    print(f"\nArchivos generados:")
    print(f"  - Matriz: emigrant_decade_author_matrix.csv")
    print(f"  - Temporal por género: fig_emigrant_temporal_by_genre.{{png,pdf,jpeg}}")
    print(f"  - Timeline producción: fig_production_timeline.{{png,pdf,jpeg}}")
    print(f"\nNota: El heatmap década×autor se genera en heatmap-author-decade-expanded")
    print()

if __name__ == "__main__":
    main()

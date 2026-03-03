#!/usr/bin/env python3
"""
emigrant_profile_analysis.py - Análisis de perfiles de representación del emigrante.

PROMPT 3 (Phase 12B): Perfiles de marcadores + mediación
- Distribución de marcadores por autor/década/género
- Identificación de escenas de mediación (co-ocurrencia de markers)
- Visualizaciones de perfiles de representación

Genera:
- 04_outputs/tables/emigrant_markers_by_author.csv
- 04_outputs/tables/emigrant_markers_by_decade.csv
- 04_outputs/tables/emigrant_markers_by_genre.csv
- 04_outputs/tables/emigrant_mediation_scenes.csv
- 04_outputs/figures/static/fig_emigrant_markers_profile_*.{png,pdf}
"""

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter

# Import i18n module for bilingual support
from i18n_figures import t, save_fig

BASE_DIR = Path(__file__).parent.parent.parent
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"
FIGURES_DIR = BASE_DIR / "04_outputs" / "figures" / "static"
CASES_DIR = BASE_DIR / "03_analysis" / "cases"

# Configuración estética
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

def load_emigrant_cases() -> pd.DataFrame:
    """Carga casos emigrantes con markers."""
    cases_file = CASES_DIR / "emigrante_kwic_cases.csv"
    df = pd.read_csv(cases_file)
    print(f"[cases] Cargados {len(df)} casos emigrantes")
    
    # Extraer marker base (sin variantes regex)
    df['marker_base'] = df['marker'].str.split('|').str[0]
    
    return df

def load_master_table() -> pd.DataFrame:
    """Carga tabla maestra con género."""
    master_file = TABLES_DIR / "corpus_master_table_v2tokens_meta.csv"
    if not master_file.exists():
        master_file = TABLES_DIR / "corpus_master_table_v2tokens.csv"
    df = pd.read_csv(master_file)
    print(f"[master] Cargadas {len(df)} obras")
    return df

def analyze_markers_by_dimension(cases: pd.DataFrame, master: pd.DataFrame, dimension: str) -> pd.DataFrame:
    """
    Analiza distribución de markers por dimensión (author/decade/genre).
    
    Returns:
        DataFrame con top markers por cada valor de la dimensión
    """
    # Merge casos con master para obtener genre y decade
    cases_enriched = cases.merge(
        master[['obra_id', 'genre_norm', 'decade', 'tokens_total']],
        on='obra_id',
        how='left'
    )
    
    # Filtrar década unknown si dimension=decade
    if dimension == 'decade':
        cases_enriched = cases_enriched[cases_enriched['decade'] != 'unknown_year']
    
    # Agrupar por dimensión y marker_label
    grouped = cases_enriched.groupby([dimension, 'marker_label']).size().reset_index(name='n_mentions')
    
    # Calcular top 10 markers por cada valor de dimensión
    top_markers = (
        grouped.sort_values([dimension, 'n_mentions'], ascending=[True, False])
        .groupby(dimension)
        .head(10)
    )
    
    print(f"[markers_{dimension}] Analizados {len(grouped)} markers únicos por {dimension}")
    
    return top_markers

def identify_mediation_scenes(cases: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica escenas de mediación: unidades con múltiples menciones emigrantes.
    
    Mediación = co-ocurrencia de markers (emigrant + contexto social)
    Threshold: unidades con ≥3 menciones
    """
    # Contar menciones por obra_id + unit_id
    mediation = cases.groupby(['obra_id', 'unit_id']).agg({
        'case_id': 'count',
        'marker_label': lambda x: ' | '.join(sorted(set(x))),
        'author_normalized': 'first',
        'year': 'first'
    }).reset_index()
    
    mediation = mediation.rename(columns={'case_id': 'n_mentions'})
    
    # Filtrar unidades con ≥3 menciones (escenas densas = mediación)
    mediation = mediation[mediation['n_mentions'] >= 3].copy()
    
    # Ordenar por densidad
    mediation = mediation.sort_values('n_mentions', ascending=False).reset_index(drop=True)
    
    print(f"[mediation] Identificadas {len(mediation)} escenas de mediación (≥3 menciones por unidad)")
    
    return mediation

def generate_marker_profile_by_author(cases: pd.DataFrame, master: pd.DataFrame, output_prefix: str, lang: str = 'es'):
    """Genera perfil de markers por autor (top 5 autores)."""
    # Top 5 autores por número de menciones
    top_authors = cases['author_normalized'].value_counts().head(5).index.tolist()
    
    cases_filtered = cases[cases['author_normalized'].isin(top_authors)]
    
    # Top 15 markers globales
    top_markers = cases['marker_label'].value_counts().head(15).index.tolist()
    
    # Pivot: author × marker_label
    pivot = cases_filtered.groupby(['author_normalized', 'marker_label']).size().reset_index(name='n_mentions')
    pivot = pivot[pivot['marker_label'].isin(top_markers)]
    pivot_wide = pivot.pivot(index='author_normalized', columns='marker_label', values='n_mentions').fillna(0)
    
    # Reordenar columnas por frecuencia total
    col_order = pivot.groupby('marker_label')['n_mentions'].sum().sort_values(ascending=False).index
    pivot_wide = pivot_wide[col_order]
    
    # Plot
    fig, ax = plt.subplots(figsize=(16, 8))
    
    x = np.arange(len(pivot_wide.columns))
    width = 0.15
    
    for i, author in enumerate(pivot_wide.index):
        ax.bar(x + i * width, pivot_wide.loc[author], width, label=author)
    
    ax.set_xlabel(f"{t('marker', lang)} ({t('semantic_label', lang)})", fontsize=11, fontweight='bold')
    ax.set_ylabel(t('number_of_mentions', lang), fontsize=11, fontweight='bold')
    ax.set_title(t('marker_profile_by_author_title', lang), 
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x + width * (len(pivot_wide.index) - 1) / 2)
    ax.set_xticklabels(pivot_wide.columns, rotation=45, ha='right', fontsize=8)
    ax.legend(title=t('author', lang), loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save with language suffix
    save_fig(fig, f"{output_prefix}_by_author", FIGURES_DIR, lang, dpi=300)
    plt.close()
    
    print(f"  ✓ {output_prefix}_by_author_{lang}.{{png,pdf}}")

def generate_marker_profile_by_genre(cases: pd.DataFrame, master: pd.DataFrame, output_prefix: str, lang: str = 'es'):
    """Genera perfil de markers por género."""
    # Merge con genre
    cases_enriched = cases.merge(
        master[['obra_id', 'genre_norm']],
        on='obra_id',
        how='left'
    )
    
    # Filtrar géneros principales (≥5 obras)
    genre_counts = master['genre_norm'].value_counts()
    main_genres = genre_counts[genre_counts >= 5].index.tolist()
    
    cases_filtered = cases_enriched[cases_enriched['genre_norm'].isin(main_genres)]
    
    # Top 15 markers globales
    top_markers = cases['marker_label'].value_counts().head(15).index.tolist()
    
    # Pivot: genre × marker_label
    pivot = cases_filtered.groupby(['genre_norm', 'marker_label']).size().reset_index(name='n_mentions')
    pivot = pivot[pivot['marker_label'].isin(top_markers)]
    pivot_wide = pivot.pivot(index='genre_norm', columns='marker_label', values='n_mentions').fillna(0)
    
    # Reordenar columnas por frecuencia total
    col_order = pivot.groupby('marker_label')['n_mentions'].sum().sort_values(ascending=False).index
    pivot_wide = pivot_wide[col_order]
    
    # Plot
    fig, ax = plt.subplots(figsize=(16, 8))
    
    x = np.arange(len(pivot_wide.columns))
    width = 0.15
    
    for i, genre in enumerate(pivot_wide.index):
        ax.bar(x + i * width, pivot_wide.loc[genre], width, label=genre)
    
    ax.set_xlabel(f"{t('marker', lang)} ({t('semantic_label', lang)})", fontsize=11, fontweight='bold')
    ax.set_ylabel(t('number_of_mentions', lang), fontsize=11, fontweight='bold')
    ax.set_title(t('marker_profile_by_genre_title', lang), 
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x + width * (len(pivot_wide.index) - 1) / 2)
    ax.set_xticklabels(pivot_wide.columns, rotation=45, ha='right', fontsize=8)
    ax.legend(title=t('genre', lang), loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save with language suffix
    save_fig(fig, f"{output_prefix}_by_genre", FIGURES_DIR, lang, dpi=300)
    plt.close()
    
    print(f"  ✓ {output_prefix}_by_genre_{lang}.{{png,pdf}}")

def generate_mediation_density_plot(mediation: pd.DataFrame, output_prefix: str, lang: str = 'es'):
    """Genera gráfico de densidad de escenas de mediación."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Panel 1: Histograma de densidad (n_mentions por escena)
    ax1.hist(mediation['n_mentions'], bins=range(3, mediation['n_mentions'].max() + 2), 
             alpha=0.7, color='steelblue', edgecolor='black')
    ax1.set_xlabel(t('emigrant_mentions_per_scene', lang), fontsize=11, fontweight='bold')
    ax1.set_ylabel(t('number_of_scenes', lang), fontsize=11, fontweight='bold')
    ax1.set_title(t('mediation_density_title', lang), 
                  fontsize=13, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Panel 2: Top 10 autores con más escenas de mediación
    author_mediation = mediation['author_normalized'].value_counts().head(10)
    
    ax2.barh(range(len(author_mediation)), author_mediation.values, color='darkorange', alpha=0.7, edgecolor='black')
    ax2.set_yticks(range(len(author_mediation)))
    ax2.set_yticklabels(author_mediation.index, fontsize=9)
    ax2.set_xlabel(t('number_of_mediation_scenes', lang), fontsize=11, fontweight='bold')
    ax2.set_title(t('mediation_top_authors_title', lang), fontsize=13, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, axis='x')
    ax2.invert_yaxis()
    
    plt.tight_layout()
    
    # Save with language suffix
    save_fig(fig, output_prefix, FIGURES_DIR, lang, dpi=300)
    plt.close()
    
    print(f"  ✓ {output_prefix}_{lang}.{{png,pdf}}")

def main():
    """Ejecuta análisis de perfiles de emigrante."""
    parser = argparse.ArgumentParser(description="Análisis de perfiles de representación del emigrante")
    parser.add_argument(
        "--lang",
        type=str,
        choices=['es', 'en', 'both'],
        default='both',
        help="Language for figures: es, en, or both (default: both)"
    )
    args = parser.parse_args()
    
    # Determine languages to generate
    languages = ['es', 'en'] if args.lang == 'both' else [args.lang]
    
    print("\n" + "="*70)
    print("EMIGRANT PROFILE ANALYSIS (PROMPT 3)")
    print("="*70 + "\n")
    
    # Crear directorios
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Cargar datos
    cases = load_emigrant_cases()
    master = load_master_table()
    
    print("\n[1/7] Analizando markers por autor...")
    markers_by_author = analyze_markers_by_dimension(cases, master, 'author_normalized')
    markers_by_author.to_csv(TABLES_DIR / "emigrant_markers_by_author.csv", index=False)
    print(f"  ✓ emigrant_markers_by_author.csv")
    
    print("\n[2/7] Analizando markers por década...")
    markers_by_decade = analyze_markers_by_dimension(cases, master, 'decade')
    markers_by_decade.to_csv(TABLES_DIR / "emigrant_markers_by_decade.csv", index=False)
    print(f"  ✓ emigrant_markers_by_decade.csv")
    
    print("\n[3/7] Analizando markers por género...")
    markers_by_genre = analyze_markers_by_dimension(cases, master, 'genre_norm')
    markers_by_genre.to_csv(TABLES_DIR / "emigrant_markers_by_genre.csv", index=False)
    print(f"  ✓ emigrant_markers_by_genre.csv")
    
    print("\n[4/7] Identificando escenas de mediación...")
    mediation = identify_mediation_scenes(cases)
    mediation.to_csv(TABLES_DIR / "emigrant_mediation_scenes.csv", index=False)
    print(f"  ✓ emigrant_mediation_scenes.csv")
    
    print("\n[5/7] Generando perfil de markers por autor...")
    for lang in languages:
        generate_marker_profile_by_author(cases, master, "fig_emigrant_markers_profile", lang=lang)
    
    print("\n[6/7] Generando perfil de markers por género...")
    for lang in languages:
        generate_marker_profile_by_genre(cases, master, "fig_emigrant_markers_profile", lang=lang)
    
    print("\n[7/7] Generando plot de densidad de mediación...")
    for lang in languages:
        generate_mediation_density_plot(mediation, "fig_emigrant_mediation_density", lang=lang)
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS DE PERFILES COMPLETADO")
    print("="*70)
    print(f"\nArchivos generados:")
    print(f"  Tablas:")
    print(f"    - emigrant_markers_by_author.csv")
    print(f"    - emigrant_markers_by_decade.csv")
    print(f"    - emigrant_markers_by_genre.csv")
    print(f"    - emigrant_mediation_scenes.csv ({len(mediation)} escenas)")
    print(f"  Figuras (bilingües ES/EN):")
    print(f"    - fig_emigrant_markers_profile_by_author_{{es,en}}.{{png,pdf}}")
    print(f"    - fig_emigrant_markers_profile_by_genre_{{es,en}}.{{png,pdf}}")
    print(f"    - fig_emigrant_mediation_density_{{es,en}}.{{png,pdf}}")
    print()

if __name__ == "__main__":
    main()

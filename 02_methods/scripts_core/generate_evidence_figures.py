#!/usr/bin/env python3
"""
generate_evidence_figures.py
Genera figuras estáticas (PNG+PDF) para evidence pack en ES/EN.
- fig_emigrant_by_author_top15_{es,en}.{png,pdf}
- fig_emigrant_by_decade_{es,en}.{png,pdf}
- fig_emigrant_by_format_{es,en}.{png,pdf}
- fig_emigrant_markers_top20_{es,en}.{png,pdf}

Usa matplotlib/seaborn. Normalizado por tokens. Multilingüe.
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
import sys

warnings.filterwarnings('ignore')

# Import i18n module
sys.path.insert(0, str(Path(__file__).parent))
from i18n_figures import t, save_fig, get_genre_labels

# Configuración
TABLES_DIR = Path(__file__).parent.parent.parent / "04_outputs" / "tables"
ANALYSIS_DIR = Path(__file__).parent.parent.parent / "03_analysis" / "cases"
FIGURES_DIR = Path(__file__).parent.parent.parent / "04_outputs" / "figures" / "static"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

def save_figure(fig, name: str, lang: str = 'es'):
    """Salva figura en PNG, PDF y JPEG con sufijo de idioma."""
    save_fig(fig, name, FIGURES_DIR, lang, dpi=300)
    print(f"  ✓ {name}_{lang}.{{png,pdf,jpeg}}")

def fig_emigrant_by_author_top15(by_author_file: Path, lang: str = 'es'):
    """Top 15 autores por density emigrante."""
    print(f"\n[fig_author_top15_{lang}] Generando...")
    
    try:
        df = pd.read_csv(by_author_file).head(15)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Barras horizontales, coloreadas por density
        colors = plt.cm.RdYlGn_r(df['emigrant_rate_per_1k_tokens'] / df['emigrant_rate_per_1k_tokens'].max())
        
        ax.barh(df['author_normalized'], df['emigrant_rate_per_1k_tokens'], color=colors)
        ax.set_xlabel(t('emigrant_rate', lang), fontsize=12, fontweight='bold')
        
        if lang == 'es':
            ax.set_title('Top 15 Autores: Densidad de Representación del Emigrante', fontsize=14, fontweight='bold')
        else:
            ax.set_title('Top 15 Authors: Emigrant Representation Density', fontsize=14, fontweight='bold')
        
        ax.invert_yaxis()
        
        # Agregar valores en barras
        for i, (author, val) in enumerate(zip(df['author_normalized'], df['emigrant_rate_per_1k_tokens'])):
            ax.text(val + 0.1, i, f'{val:.2f}', va='center', fontsize=9)
        
        plt.tight_layout()
        save_figure(fig, "fig_emigrant_by_author_top15", lang)
        plt.close(fig)
    except Exception as e:
        print(f"  ✗ Error: {e}")

def fig_emigrant_by_decade(by_decade_file: Path, lang: str = 'es'):
    """Línea por década."""
    print(f"[fig_decade_{lang}] Generando...")
    
    try:
        df = pd.read_csv(by_decade_file)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        ax.plot(df['decade'], df['emigrant_rate_per_1k_tokens'], 
                marker='o', linewidth=2.5, markersize=8, color='#d62728')
        
        ax.set_xlabel(t('decade', lang), fontsize=12, fontweight='bold')
        ax.set_ylabel(t('emigrant_rate', lang), fontsize=12, fontweight='bold')
        
        if lang == 'es':
            ax.set_title('Densidad de Representación del Emigrante por Década', fontsize=14, fontweight='bold')
        else:
            ax.set_title('Emigrant Representation Density by Decade', fontsize=14, fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas x
        plt.xticks(rotation=45, ha='right')
        
        # Agregar valores en puntos
        for decade, val in zip(df['decade'], df['emigrant_rate_per_1k_tokens']):
            ax.annotate(f'{val:.2f}', xy=(decade, val), xytext=(0, 10), 
                       textcoords='offset points', ha='center', fontsize=9)
        
        plt.tight_layout()
        save_figure(fig, "fig_emigrant_by_decade", lang)
        plt.close(fig)
    except Exception as e:
        print(f"  ✗ Error: {e}")

def fig_emigrant_by_format(by_format_file: Path, lang: str = 'es'):
    """Barras por formato."""
    print(f"[fig_format_{lang}] Generando...")
    
    try:
        df = pd.read_csv(by_format_file).sort_values('emigrant_rate_per_1k_tokens', ascending=False)
        
        # Get genre labels in target language
        genre_labels = get_genre_labels(lang)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors_format = {
            'novela': '#1f77b4',
            'cuento': '#9467bd',
            'cuento_relato': '#9467bd',
            'poesia': '#ff7f0e',
            'poesía': '#ff7f0e',
            'poesia_poemario': '#ff7f0e',
            'teatro': '#2ca02c',
            'ensayo_cronica': '#17becf',
            'cronica': '#17becf',
            'otro': '#8c564b',
            'unknown': '#d62728'
        }
        
        # Use genre_norm if available, fallback to format
        genre_col = 'genre_norm' if 'genre_norm' in df.columns else 'format'
        bar_colors = [colors_format.get(str(fmt), '#808080') for fmt in df[genre_col]]
        
        # Translate genre labels
        x_labels = [genre_labels.get(str(fmt), str(fmt)) for fmt in df[genre_col]]
        
        bars = ax.bar(range(len(df)), df['emigrant_rate_per_1k_tokens'], color=bar_colors, alpha=0.8)
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(x_labels, rotation=15, ha='right')
        
        ax.set_ylabel(t('emigrant_rate', lang), fontsize=12, fontweight='bold')
        
        if lang == 'es':
            ax.set_title('Densidad de Representación del Emigrante por Formato', fontsize=14, fontweight='bold')
        else:
            ax.set_title('Emigrant Representation Density by Genre', fontsize=14, fontweight='bold')
        
        ax.grid(axis='y', alpha=0.3)
        
        # Agregar valores sobre barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        save_figure(fig, "fig_emigrant_by_format", lang)
        plt.close(fig)
    except Exception as e:
        print(f"  ✗ Error: {e}")

def fig_emigrant_markers_top20(lang: str = 'es'):
    """Top 20 marcadores globales."""
    print(f"[fig_markers_top20_{lang}] Generando...")
    
    try:
        kwic_file = ANALYSIS_DIR / "emigrante_kwic_cases.csv"
        if not kwic_file.exists():
            print(f"  ✗ Archivo no encontrado: {kwic_file}")
            return
        
        kwic_df = pd.read_csv(kwic_file)
        marker_counts = kwic_df['marker'].value_counts().head(20)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        colors = plt.cm.Spectral(range(len(marker_counts)))
        ax.barh(marker_counts.index, marker_counts.values, color=colors)
        
        ax.set_xlabel(t('number_of_mentions', lang), fontsize=12, fontweight='bold')
        
        if lang == 'es':
            ax.set_title('Top 20 Marcadores de Emigración (Corpus Total)', fontsize=14, fontweight='bold')
        else:
            ax.set_title('Top 20 Emigration Markers (Full Corpus)', fontsize=14, fontweight='bold')
        
        ax.invert_yaxis()
        
        # Agregar valores en barras
        for i, (marker, val) in enumerate(zip(marker_counts.index, marker_counts.values)):
            ax.text(val + 5, i, f'{val}', va='center', fontsize=9)
        
        plt.tight_layout()
        save_figure(fig, "fig_emigrant_markers_top20", lang)
        plt.close(fig)
    except Exception as e:
        print(f"  ✗ Error: {e}")

def main():
    """Genera todas las figuras en ES/EN."""
    parser = argparse.ArgumentParser(description="Genera figuras estáticas para evidence pack (ES/EN)")
    parser.add_argument(
        "--tables-suffix",
        default="",
        help="Sufijo de tablas (ej: v2tokens)"
    )
    parser.add_argument(
        "--lang",
        choices=['es', 'en', 'both'],
        default="both",
        help="Idioma: es, en o both (default: both)"
    )
    args = parser.parse_args()
    suffix = f"_{args.tables_suffix}" if args.tables_suffix else ""

    by_author_file = TABLES_DIR / f"emigrant_by_author{suffix}.csv"
    by_decade_file = TABLES_DIR / f"emigrant_by_decade{suffix}.csv"
    by_format_file = TABLES_DIR / f"emigrant_by_format{suffix}.csv"

    print("\n" + "="*70)
    print("GENERATE_EVIDENCE_FIGURES: Figuras estáticas para evidence pack (ES/EN)")
    print("="*70)
    
    # Determine languages to generate
    if args.lang == 'both':
        languages = ['es', 'en']
    else:
        languages = [args.lang]
    
    # Generate figures for each language
    for lang in languages:
        print(f"\n🌐 Generando figuras en {lang.upper()}...")
        fig_emigrant_by_author_top15(by_author_file, lang=lang)
        fig_emigrant_by_decade(by_decade_file, lang=lang)
        fig_emigrant_by_format(by_format_file, lang=lang)
        fig_emigrant_markers_top20(lang=lang)
    
    print("\n" + "="*70)
    print(f"✅ Figuras guardadas en: {FIGURES_DIR}")
    print("="*70)
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

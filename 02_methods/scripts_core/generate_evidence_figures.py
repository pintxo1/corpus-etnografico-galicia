#!/usr/bin/env python3
"""
generate_evidence_figures.py
Genera figuras estáticas (PNG+PDF) para evidence pack.
- fig_emigrant_by_author_top15
- fig_emigrant_by_decade
- fig_emigrant_by_format
- fig_emigrant_markers_top20

Usa matplotlib/seaborn. Normalizado por tokens.
"""

import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

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

def save_figure(fig, name: str):
    """Salva figura en PNG y PDF."""
    png_path = FIGURES_DIR / f"{name}.png"
    pdf_path = FIGURES_DIR / f"{name}.pdf"
    
    fig.savefig(png_path, dpi=300, bbox_inches='tight')
    fig.savefig(pdf_path, bbox_inches='tight')
    
    print(f"  ✓ {png_path.name}")
    print(f"  ✓ {pdf_path.name}")

def fig_emigrant_by_author_top15(by_author_file: Path):
    """Top 15 autores por density emigrante."""
    print("\n[fig_author_top15] Generando...")
    
    try:
        df = pd.read_csv(by_author_file).head(15)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Barras horizontales, coloreadas por density
        colors = plt.cm.RdYlGn_r(df['emigrant_rate_per_1k_tokens'] / df['emigrant_rate_per_1k_tokens'].max())
        
        ax.barh(df['author_normalized'], df['emigrant_rate_per_1k_tokens'], color=colors)
        ax.set_xlabel('Menciones de emigrante (por 1000 tokens)', fontsize=12, fontweight='bold')
        ax.set_title('Top 15 Autores: Densidad de Representación del Emigrante', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        
        # Agregar valores en barras
        for i, (author, val) in enumerate(zip(df['author_normalized'], df['emigrant_rate_per_1k_tokens'])):
            ax.text(val + 0.1, i, f'{val:.2f}', va='center', fontsize=9)
        
        plt.tight_layout()
        save_figure(fig, "fig_emigrant_by_author_top15")
        plt.close(fig)
    except Exception as e:
        print(f"  ✗ Error: {e}")

def fig_emigrant_by_decade(by_decade_file: Path):
    """Línea por década."""
    print("[fig_decade] Generando...")
    
    try:
        df = pd.read_csv(by_decade_file)
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        ax.plot(df['decade'], df['emigrant_rate_per_1k_tokens'], 
                marker='o', linewidth=2.5, markersize=8, color='#d62728')
        
        ax.set_xlabel('Década', fontsize=12, fontweight='bold')
        ax.set_ylabel('Menciones de emigrante (por 1000 tokens)', fontsize=12, fontweight='bold')
        ax.set_title('Densidad de Representación del Emigrante por Década', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Rotar etiquetas x
        plt.xticks(rotation=45, ha='right')
        
        # Agregar valores en puntos
        for decade, val in zip(df['decade'], df['emigrant_rate_per_1k_tokens']):
            ax.annotate(f'{val:.2f}', xy=(decade, val), xytext=(0, 10), 
                       textcoords='offset points', ha='center', fontsize=9)
        
        plt.tight_layout()
        save_figure(fig, "fig_emigrant_by_decade")
        plt.close(fig)
    except Exception as e:
        print(f"  ✗ Error: {e}")

def fig_emigrant_by_format(by_format_file: Path):
    """Barras por formato."""
    print("[fig_format] Generando...")
    
    try:
        df = pd.read_csv(by_format_file).sort_values('emigrant_rate_per_1k_tokens', ascending=False)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors_format = {'novela': '#1f77b4', 'poesía': '#ff7f0e', 'crónica': '#2ca02c', 'unknown': '#d62728'}
        bar_colors = [colors_format.get(fmt, '#808080') for fmt in df['format']]
        
        bars = ax.bar(df['format'], df['emigrant_rate_per_1k_tokens'], color=bar_colors, alpha=0.8)
        
        ax.set_ylabel('Menciones de emigrante (por 1000 tokens)', fontsize=12, fontweight='bold')
        ax.set_title('Densidad de Representación del Emigrante por Formato', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Agregar valores sobre barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        save_figure(fig, "fig_emigrant_by_format")
        plt.close(fig)
    except Exception as e:
        print(f"  ✗ Error: {e}")

def fig_emigrant_markers_top20():
    """Top 20 marcadores globales."""
    print("[fig_markers_top20] Generando...")
    
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
        
        ax.set_xlabel('Número de menciones', fontsize=12, fontweight='bold')
        ax.set_title('Top 20 Marcadores de Emigración (Corpus Total)', fontsize=14, fontweight='bold')
        ax.invert_yaxis()
        
        # Agregar valores en barras
        for i, (marker, val) in enumerate(zip(marker_counts.index, marker_counts.values)):
            ax.text(val + 5, i, f'{val}', va='center', fontsize=9)
        
        plt.tight_layout()
        save_figure(fig, "fig_emigrant_markers_top20")
        plt.close(fig)
    except Exception as e:
        print(f"  ✗ Error: {e}")

def main():
    """Genera todas las figuras."""
    parser = argparse.ArgumentParser(description="Genera figuras estaticas para evidence pack")
    parser.add_argument(
        "--tables-suffix",
        default="",
        help="Sufijo de tablas (ej: v2tokens)"
    )
    args = parser.parse_args()
    suffix = f"_{args.tables_suffix}" if args.tables_suffix else ""

    by_author_file = TABLES_DIR / f"emigrant_by_author{suffix}.csv"
    by_decade_file = TABLES_DIR / f"emigrant_by_decade{suffix}.csv"
    by_format_file = TABLES_DIR / f"emigrant_by_format{suffix}.csv"

    print("\n" + "="*70)
    print("GENERATE_EVIDENCE_FIGURES: Figuras estáticas para evidence pack")
    print("="*70)
    
    fig_emigrant_by_author_top15(by_author_file)
    fig_emigrant_by_decade(by_decade_file)
    fig_emigrant_by_format(by_format_file)
    fig_emigrant_markers_top20()
    
    print("\n" + "="*70)
    print(f"✅ Figuras guardadas en: {FIGURES_DIR}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

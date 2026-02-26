#!/usr/bin/env python3
"""
fig_scene_scatter.py - Scatter plot: Coverage vs Concentration
Input: scene_summary.csv
Output: static PNG + PDF
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def scatter_coverage_concentration(scene_summary_path, outdir, dpi=300):
    """
    Scatter plot X=coverage_pct, Y=top3_obras_pct
    """
    
    df = pd.read_csv(scene_summary_path)
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    # Plot points
    ax.scatter(df['coverage_pct'], df['top3_obras_pct'], s=100, alpha=0.6, 
               color='#4c78a8', edgecolors='black', linewidth=0.5)
    
    # Annotate escenas (smart positioning for readability)
    medianx = df['coverage_pct'].median()
    mediany = df['top3_obras_pct'].median()
    
    for _, row in df.iterrows():
        escena = row['escena_tipo']
        x = row['coverage_pct']
        y = row['top3_obras_pct']
        
        # Offset annotation to avoid overlap
        offset_x = 2 if x > medianx else -2
        offset_y = 1.5 if y > mediany else -1.5
        
        ax.annotate(
            escena, 
            xy=(x, y),
            xytext=(offset_x, offset_y),
            textcoords='offset points',
            fontsize=8,
            alpha=0.8,
            ha='center'
        )
    
    # Guide lines
    ax.axhline(mediany, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    ax.axvline(medianx, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    
    # Quadrant labels
    ax.text(medianx + (df['coverage_pct'].max() - medianx) * 0.2, 
            mediany + (df['top3_obras_pct'].max() - mediany) * 0.2,
            'High-coverage\nHigh-concentration', 
            fontsize=9, alpha=0.5, ha='center', style='italic')
    
    ax.text(medianx - (medianx - df['coverage_pct'].min()) * 0.2,
            mediany + (df['top3_obras_pct'].max() - mediany) * 0.2,
            'Low-coverage\nHigh-concentration',
            fontsize=9, alpha=0.5, ha='center', style='italic')
    
    # Labels and title
    ax.set_xlabel('Coverage (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Top-3 Works Concentration (%)', fontsize=11, fontweight='bold')
    ax.set_title('Scene Scatter: Coverage vs. Concentration', fontsize=13, fontweight='bold')
    
    ax.grid(True, alpha=0.2)
    ax.set_xlim(df['coverage_pct'].min() - 5, df['coverage_pct'].max() + 5)
    ax.set_ylim(df['top3_obras_pct'].min() - 5, df['top3_obras_pct'].max() + 5)
    
    plt.tight_layout()
    
    # Save PNG
    png_path = Path(outdir) / "fig_scene_scatter.png"
    plt.savefig(png_path, dpi=dpi, bbox_inches='tight')
    print(f"✅ {png_path} (DPI: {dpi})")
    
    # Save PDF
    pdf_path = Path(outdir) / "fig_scene_scatter.pdf"
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    print(f"✅ {pdf_path}")
    
    plt.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate scene scatter plot')
    parser.add_argument('--scene-summary', required=True)
    parser.add_argument('--outdir', required=True)
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PNG output (default: 300)')
    
    args = parser.parse_args()
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    
    scatter_coverage_concentration(args.scene_summary, args.outdir, dpi=args.dpi)

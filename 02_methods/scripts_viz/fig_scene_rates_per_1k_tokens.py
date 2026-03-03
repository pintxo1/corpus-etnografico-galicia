#!/usr/bin/env python3
"""
fig_scene_rates_per_1k_tokens.py - Bar chart: Top 10 scenes by case rate (per 1k tokens)
Input: scene_rates_per_1k_tokens.csv
Output: static PNG + PDF
"""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_export import save_figure_variants


def draw_scene_rates_barh(rates_csv_path, outdir, dpi=300):
    """
    Horizontal bar chart showing top 10 scenes by rate (cases per 1k tokens)
    """
    
    df = pd.read_csv(rates_csv_path)
    
    # Sort by rate and take top 10
    df_sorted = df.sort_values('cases_per_1k_tokens', ascending=True).tail(10)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Create horizontal bar chart
    bars = ax.barh(
        range(len(df_sorted)),
        df_sorted['cases_per_1k_tokens'],
        color='#4c78a8',
        edgecolor='black',
        linewidth=0.7
    )
    
    # Add value labels on bars
    for i, (idx, row) in enumerate(df_sorted.iterrows()):
        rate = row['cases_per_1k_tokens']
        ax.text(
            rate + 0.01,
            i,
            f"{rate:.4f}",
            va='center',
            fontsize=9,
            fontweight='bold'
        )
    
    # Set labels
    ax.set_yticks(range(len(df_sorted)))
    ax.set_yticklabels(df_sorted['escena_tipo'], fontsize=11)
    ax.set_xlabel('Cases per 1,000 tokens', fontsize=12, fontweight='bold')
    ax.set_ylabel('Scene', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Scenes by Case Rate', fontsize=13, fontweight='bold')
    
    # Add grid
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Set x-axis limit with some padding
    ax.set_xlim(0, df_sorted['cases_per_1k_tokens'].max() * 1.15)
    
    plt.tight_layout()
    
    base_path = Path(outdir) / "fig_scene_rates_per_1k_tokens"
    save_figure_variants(fig, base_path, dpi=dpi, save_png=True, save_pdf=True, save_jpeg=True, jpeg_quality=95)
    
    plt.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate scene rates bar chart')
    parser.add_argument('--rates-csv', required=True, help='Path to scene_rates_per_1k_tokens.csv')
    parser.add_argument('--outdir', required=True, help='Output directory for PNG/PDF')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PNG output (default: 300)')
    
    args = parser.parse_args()
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    
    draw_scene_rates_barh(args.rates_csv, args.outdir, dpi=args.dpi)

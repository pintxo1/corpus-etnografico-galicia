#!/usr/bin/env python3
"""
fig_scene_heatmap.py - Heatmap: Scene x Work (top N) with token normalization
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def heatmap_scene_work(cases_path, scene_summary_path, token_totals_path, outdir, dpi=300):
    """Generate scene x work heatmap (top 40 works + aggregated Others)"""
    
    df_cases = pd.read_csv(cases_path)
    df_scenes = pd.read_csv(scene_summary_path)
    df_tokens = pd.read_csv(token_totals_path)
    
    # Compute total tokens
    total_tokens = df_tokens['tokens_total'].sum()
    
    # Count cases per scene × obra
    scene_work_counts = df_cases.groupby(['escena_tipo', 'obra_id']).size().reset_index(name='n_casos')
    
    # Calculate rate per 1k tokens for each combination
    scene_work_counts['rate_per_1k'] = (
        scene_work_counts['n_casos'] / total_tokens * 1000
    )
    
    # Get top 40 obras by total cases
    top_obras = df_cases['obra_id'].value_counts().head(40).index.tolist()
    
    # Filter and pivot
    df_top = scene_work_counts[scene_work_counts['obra_id'].isin(top_obras)]
    df_others = scene_work_counts[~scene_work_counts['obra_id'].isin(top_obras)]
    
    # Aggregate others
    others_agg = df_others.groupby('escena_tipo')['rate_per_1k'].sum().reset_index()
    others_agg['obra_id'] = '__OTHER__'
    
    df_plot = pd.concat([df_top, others_agg], ignore_index=True)
    
    # Pivot to matrix
    matrix = df_plot.pivot_table(
        index='escena_tipo',
        columns='obra_id',
        values='rate_per_1k',
        fill_value=0
    )
    
    # Reorder columns: top works first + OTHER at end
    cols_ordered = [w for w in top_obras if w in matrix.columns] + ['__OTHER__']
    matrix = matrix[[c for c in cols_ordered if c in matrix.columns]]
    
    # Shorten labels for readability
    matrix.columns = [c.split('_')[0][:15] if c != '__OTHER__' else c for c in matrix.columns]
    
    # Generate heatmap (PNG version - only top 40)
    fig, ax = plt.subplots(figsize=(16, 8))
    
    im = ax.imshow(matrix.values, cmap='YlOrRd', aspect='auto')
    
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_yticks(range(len(matrix.index)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(matrix.index, fontsize=10)
    
    ax.set_xlabel('Works (top 40 + aggregated others)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Scene', fontsize=11, fontweight='bold')
    ax.set_title('Scene × Work Heatmap (normalized per 1k tokens)', fontsize=12, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Cases per 1k tokens', fontsize=10)
    
    # Add grid
    for i in range(len(matrix.index) + 1):
        ax.axhline(i - 0.5, color='white', linewidth=0.5, alpha=0.3)
    for i in range(len(matrix.columns) + 1):
        ax.axvline(i - 0.5, color='white', linewidth=0.5, alpha=0.3)
    
    plt.tight_layout()
    
    png_path = Path(outdir) / "fig_scene_work_heatmap.png"
    plt.savefig(png_path, dpi=dpi, bbox_inches='tight')
    print(f"✅ {png_path} (DPI: {dpi})")
    
    pdf_path = Path(outdir) / "fig_scene_work_heatmap.pdf"
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    print(f"✅ {pdf_path} (heatmap with top 40 works)")
    
    plt.close()
    
    # Generate full heatmap (PDF large - all works)
    all_obras = sorted(df_cases['obra_id'].unique())
    df_full = scene_work_counts.copy()
    matrix_full = df_full.pivot_table(
        index='escena_tipo',
        columns='obra_id',
        values='rate_per_1k',
        fill_value=0
    )
    
    fig, ax = plt.subplots(figsize=(len(all_obras)*0.4, 10))
    # Limit to max reasonable size
    if len(all_obras) > 80:
        matrix_display = matrix_full.iloc[:, :80]
        ax.set_title('Scene × Work Heatmap (ALL 80 works - large format, first 80)', fontsize=12)
    else:
        matrix_display = matrix_full
        ax.set_title(f'Scene × Work Heatmap (ALL {len(all_obras)} works)', fontsize=12)
    
    im = ax.imshow(matrix_display.values, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(range(len(matrix_display.columns)))
    ax.set_yticks(range(len(matrix_display.index)))
    
    # Truncate obra labels
    xticklabels = [c.split('_')[0][:8] for c in matrix_display.columns]
    ax.set_xticklabels(xticklabels, rotation=90, fontsize=7)
    ax.set_yticklabels(matrix_display.index, fontsize=9)
    
    ax.set_xlabel('Works (all 80)', fontsize=10)
    ax.set_ylabel('Scene', fontsize=10)
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('cases/1k tokens', fontsize=9)
    
    pdf_path_full = Path(outdir) / "fig_scene_work_heatmap_full.pdf"
    plt.savefig(pdf_path_full, format='pdf', bbox_inches='tight', dpi=100)
    print(f"✅ {pdf_path_full} (complete heatmap with all {len(all_obras)} works)")
    
    plt.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', required=True)
    parser.add_argument('--scene-summary', required=True)
    parser.add_argument('--token-totals', required=True)
    parser.add_argument('--outdir', required=True)
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PNG output (default: 300)')
    
    args = parser.parse_args()
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    
    heatmap_scene_work(args.cases, args.scene_summary, args.token_totals, args.outdir, dpi=args.dpi)

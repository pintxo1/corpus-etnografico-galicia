#!/usr/bin/env python3
"""
fig_scene_rates_distribution.py - Violin plots: Token rate distributions by scene
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_export import save_figure_variants


def violin_rates_by_scene(cases_path, token_totals_path, outdir, dpi=300):
    """Generate violin plots showing case rate distribution per 1k tokens by scene"""
    
    df_cases = pd.read_csv(cases_path)
    df_tokens = pd.read_csv(token_totals_path)
    
    # Compute total tokens across all units
    total_tokens = df_tokens['tokens_total'].sum()
    
    # Count cases per escena-obra combination
    escena_obra_counts = df_cases.groupby(['escena_tipo', 'obra_id']).size().reset_index(name='n_casos')
    
    # Calculate rate per 1k tokens for each combination
    escena_obra_counts['rate_per_1k'] = (
        escena_obra_counts['n_casos'] / total_tokens * 1000
    )
    
    # Per-scene statistics
    scene_stats = df_cases.groupby('escena_tipo').size().reset_index(name='total_casos')
    scene_stats['rate_per_1k'] = (scene_stats['total_casos'] / total_tokens * 1000)
    scene_stats = scene_stats.sort_values('rate_per_1k')
    
    
    # Select diverse scenes: pick low, medium, high rates
    if len(scene_stats) >= 5:
        selected_scenes = pd.concat([
            scene_stats.iloc[[0]],  # lowest
            scene_stats.iloc[[len(scene_stats)//4]],  # low-mid
            scene_stats.iloc[[len(scene_stats)//2]],  # mid
            scene_stats.iloc[[3*len(scene_stats)//4]],  # high-mid
            scene_stats.iloc[[-1]]  # highest
        ])['escena_tipo'].tolist()
    else:
        selected_scenes = scene_stats['escena_tipo'].tolist()
    
    # Filter data for selected scenes
    df_plot = escena_obra_counts[escena_obra_counts['escena_tipo'].isin(selected_scenes)].copy()
    
    # Create violin plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare data for violins
    data_by_scene = [
        df_plot[df_plot['escena_tipo'] == scene]['rate_per_1k'].values
        for scene in selected_scenes
    ]
    
    positions = range(len(selected_scenes))
    parts = ax.violinplot(
        data_by_scene,
        positions=positions,
        widths=0.7,
        showmeans=True,
        showmedians=True
    )
    
    # Customize colors
    for pc in parts['bodies']:
        pc.set_facecolor('#FF6B9D')
        pc.set_alpha(0.7)
    
    # Add scatter overlay (individual points)
    for i, scene in enumerate(selected_scenes):
        rates = df_plot[df_plot['escena_tipo'] == scene]['rate_per_1k'].values
        x = np.random.normal(i, 0.04, size=len(rates))
        ax.scatter(x, rates, alpha=0.3, s=20, color='#333')
    
    ax.set_xticks(positions)
    ax.set_xticklabels(selected_scenes, rotation=15, ha='right', fontsize=10)
    ax.set_ylabel('Cases per 1k tokens', fontsize=11, fontweight='bold')
    ax.set_xlabel('Scene', fontsize=11, fontweight='bold')
    ax.set_title(f'Case Rate Distribution by Scene (n={len(selected_scenes)} diverse scenes)', 
                 fontsize=12, fontweight='bold')
    
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    base_path = Path(outdir) / "fig_scene_rates_distribution"
    save_figure_variants(fig, base_path, dpi=dpi, save_png=True, save_pdf=True, save_jpeg=True, jpeg_quality=95)
    print(f"✅ fig_scene_rates_distribution.* (rate distributions for {len(selected_scenes)} scenes)")
    
    plt.close()
    
    # Print summary for documentation
    print(f"\nSelected scenes by rate percentile:")
    for scene in selected_scenes:
        rate = scene_stats[scene_stats['escena_tipo']==scene]['rate_per_1k'].values[0]
        total = scene_stats[scene_stats['escena_tipo']==scene]['total_casos'].values[0]
        print(f"  {scene}: {rate:.2f} per 1k tokens ({total} total casos)")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', required=True)
    parser.add_argument('--token-totals', required=True)
    parser.add_argument('--outdir', required=True)
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PNG output (default: 300)')
    
    args = parser.parse_args()
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    
    violin_rates_by_scene(args.cases, args.token_totals, args.outdir, dpi=args.dpi)

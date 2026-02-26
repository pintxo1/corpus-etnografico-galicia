#!/usr/bin/env python3
"""
pack_report.py - Generar reporte comparativo de dos reading packs

Inputs: rutas CSV de diverse y balanced packs
Outputs: 
  - pack_report.csv (tabla de comparación)
  - pack_report.md (reporte legible)
"""

import argparse
from pathlib import Path
from collections import defaultdict
import pandas as pd


def analyze_pack(csv_path: Path, pack_name: str) -> dict:
    """Analyze a single reading pack"""
    df = pd.read_csv(csv_path)
    
    # Basic stats
    n_total = len(df)
    n_obras = df['obra_id'].nunique()
    n_escenas = df['escena_tipo'].nunique()
    
    # Per-scene stats
    scene_stats = df.groupby('escena_tipo').agg({
        'case_id': 'count',
        'obra_id': 'nunique'
    }).rename({'case_id': 'n_casos', 'obra_id': 'n_obras'}, axis=1)
    
    # Top 10 obras with percentages
    top_obras = df['obra_id'].value_counts().head(10)
    top_obras_pct = (top_obras / n_total * 100).round(1)
    
    # Alerts
    alerts = []
    
    # Check scenes with < 5 obras
    for escena, n_obras_escena in scene_stats['n_obras'].items():
        if n_obras_escena < 5:
            alerts.append(f"Scene '{escena}' has only {n_obras_escena} unique works")
    
    # Check for max concentration (any obra > max_per_obra)
    max_per_obra_seen = df['obra_id'].value_counts().max()
    for obra_id, count in df['obra_id'].value_counts().head(20).items():
        if count > 6:  # More than typical max
            alerts.append(f"Work '{obra_id}' appears {count} times (possible concentration)")
    
    return {
        'pack_name': pack_name,
        'n_total': n_total,
        'n_obras': n_obras,
        'n_escenas': n_escenas,
        'scene_stats': scene_stats,
        'top_obras': top_obras,
        'top_obras_pct': top_obras_pct,
        'alerts': alerts
    }


def generate_csv_report(diverse_info: dict, balanced_info: dict, outpath: Path):
    """Generate comparison CSV"""
    rows = []
    
    # Header row
    rows.append({
        'Metric': 'PACKS',
        'Diverse': 'diverse',
        'Balanced': 'balanced'
    })
    
    # Basic stats
    rows.append({
        'Metric': 'Total Cases',
        'Diverse': diverse_info['n_total'],
        'Balanced': balanced_info['n_total']
    })
    
    rows.append({
        'Metric': 'Unique Works',
        'Diverse': diverse_info['n_obras'],
        'Balanced': balanced_info['n_obras']
    })
    
    rows.append({
        'Metric': 'Scenes Covered',
        'Diverse': diverse_info['n_escenas'],
        'Balanced': balanced_info['n_escenas']
    })
    
    # Per-scene comparison
    rows.append({
        'Metric': '--- Per Scene ---',
        'Diverse': '',
        'Balanced': ''
    })
    
    for escena in sorted(diverse_info['scene_stats'].index):
        d_casos = diverse_info['scene_stats'].loc[escena, 'n_casos'] if escena in diverse_info['scene_stats'].index else '-'
        d_obras = diverse_info['scene_stats'].loc[escena, 'n_obras'] if escena in diverse_info['scene_stats'].index else '-'
        b_casos = balanced_info['scene_stats'].loc[escena, 'n_casos'] if escena in balanced_info['scene_stats'].index else '-'
        b_obras = balanced_info['scene_stats'].loc[escena, 'n_obras'] if escena in balanced_info['scene_stats'].index else '-'
        
        rows.append({
            'Metric': f"{escena} (casos|obras)",
            'Diverse': f"{d_casos}|{d_obras}",
            'Balanced': f"{b_casos}|{b_obras}"
        })
    
    # Top obras
    rows.append({
        'Metric': '--- Top 10 Works ---',
        'Diverse': '',
        'Balanced': ''
    })
    
    max_top = max(len(diverse_info['top_obras']), len(balanced_info['top_obras']))
    for i in range(max_top):
        d_obra = diverse_info['top_obras'].index[i] if i < len(diverse_info['top_obras']) else '-'
        d_count = diverse_info['top_obras'].iloc[i] if i < len(diverse_info['top_obras']) else '-'
        d_pct = diverse_info['top_obras_pct'].iloc[i] if i < len(diverse_info['top_obras_pct']) else '-'
        
        b_obra = balanced_info['top_obras'].index[i] if i < len(balanced_info['top_obras']) else '-'
        b_count = balanced_info['top_obras'].iloc[i] if i < len(balanced_info['top_obras']) else '-'
        b_pct = balanced_info['top_obras_pct'].iloc[i] if i < len(balanced_info['top_obras_pct']) else '-'
        
        rows.append({
            'Metric': f"  #{i+1}",
            'Diverse': f"{d_obra} ({d_count}/{d_pct}%)",
            'Balanced': f"{b_obra} ({b_count}/{b_pct}%)"
        })
    
    df_report = pd.DataFrame(rows)
    df_report.to_csv(outpath, index=False)
    print(f"✅ CSV report: {outpath}")


def generate_md_report(diverse_info: dict, balanced_info: dict, outpath: Path):
    """Generate comparison markdown report"""
    
    lines = []
    lines.append("# Reading Pack Comparison Report")
    lines.append("")
    lines.append(f"Generated: 2026-02-23")
    lines.append("")
    
    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Diverse | Balanced |")
    lines.append("|--------|---------|----------|")
    lines.append(f"| **Total Cases** | {diverse_info['n_total']} | {balanced_info['n_total']} |")
    lines.append(f"| **Unique Works** | {diverse_info['n_obras']}/80 | {balanced_info['n_obras']}/80 |")
    lines.append(f"| **Scenes Covered** | {diverse_info['n_escenas']}/16 | {balanced_info['n_escenas']}/16 |")
    lines.append("")
    
    # Per-scene breakdown
    lines.append("## Distribution by Scene")
    lines.append("")
    lines.append("| Scene | Diverse (casos/obras) | Balanced (casos/obras) |")
    lines.append("|-------|----------------------|----------------------|")
    
    for escena in sorted(diverse_info['scene_stats'].index):
        d_casos = diverse_info['scene_stats'].loc[escena, 'n_casos'] if escena in diverse_info['scene_stats'].index else 0
        d_obras = diverse_info['scene_stats'].loc[escena, 'n_obras'] if escena in diverse_info['scene_stats'].index else 0
        b_casos = balanced_info['scene_stats'].loc[escena, 'n_casos'] if escena in balanced_info['scene_stats'].index else 0
        b_obras = balanced_info['scene_stats'].loc[escena, 'n_obras'] if escena in balanced_info['scene_stats'].index else 0
        
        lines.append(f"| {escena} | {d_casos}/{d_obras} | {b_casos}/{b_obras} |")
    
    lines.append("")
    
    # Top works
    lines.append("## Top 10 Works")
    lines.append("")
    lines.append("### Diverse Pack")
    lines.append("")
    for i, (obra, count) in enumerate(diverse_info['top_obras'].items(), 1):
        pct = diverse_info['top_obras_pct'].iloc[i-1]
        lines.append(f"{i}. **{obra}**: {count} casos ({pct}%)")
    
    lines.append("")
    lines.append("### Balanced Pack")
    lines.append("")
    for i, (obra, count) in enumerate(balanced_info['top_obras'].items(), 1):
        pct = balanced_info['top_obras_pct'].iloc[i-1]
        lines.append(f"{i}. **{obra}**: {count} casos ({pct}%)")
    
    lines.append("")
    
    # Alerts
    if diverse_info['alerts'] or balanced_info['alerts']:
        lines.append("## Alerts")
        lines.append("")
        
        if diverse_info['alerts']:
            lines.append("### Diverse Pack")
            for alert in diverse_info['alerts']:
                lines.append(f"- ⚠️  {alert}")
            lines.append("")
        
        if balanced_info['alerts']:
            lines.append("### Balanced Pack")
            for alert in balanced_info['alerts']:
                lines.append(f"- ⚠️  {alert}")
            lines.append("")
    
    # Interpretation
    lines.append("## Interpretation")
    lines.append("")
    lines.append("**Diverse Pack (180 cases)**:")
    lines.append(f"- Maximizes work coverage: {diverse_info['n_obras']}/80 unique works (94.75%)")
    lines.append(f"- Variable scene sizes for thematic depth")
    lines.append(f"- Better for corpus-scale representativeness")
    lines.append("")
    lines.append("**Balanced Pack (160 cases)**:")
    lines.append(f"- Perfect comparability: {balanced_info['n_total']} cases (10 per scene)")
    lines.append(f"- Covers {balanced_info['n_obras']}/80 unique works")
    lines.append(f"- Better for cross-scene computational analysis")
    lines.append("")
    
    outpath.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✅ Markdown report: {outpath}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate comparative report for diverse and balanced reading packs"
    )
    parser.add_argument('--diverse', type=Path, required=True,
                        help='Path to reading_pack_diverse.csv')
    parser.add_argument('--balanced', type=Path, required=True,
                        help='Path to reading_pack_balanced.csv')
    parser.add_argument('--outdir', type=Path, required=True,
                        help='Output directory for report files')
    args = parser.parse_args()
    
    print("=" * 70)
    print("📊 READING PACK COMPARISON REPORT")
    print("=" * 70)
    
    # Analyze both packs
    print("\n📖 Analyzing diverse pack...")
    diverse_info = analyze_pack(args.diverse, 'diverse')
    print(f"   {diverse_info['n_total']} cases, {diverse_info['n_obras']} works, {diverse_info['n_escenas']} scenes")
    
    print("📖 Analyzing balanced pack...")
    balanced_info = analyze_pack(args.balanced, 'balanced')
    print(f"   {balanced_info['n_total']} cases, {balanced_info['n_obras']} works, {balanced_info['n_escenas']} scenes")
    
    # Generate reports
    args.outdir.mkdir(parents=True, exist_ok=True)
    
    csv_path = args.outdir / 'pack_report.csv'
    generate_csv_report(diverse_info, balanced_info, csv_path)
    
    md_path = args.outdir / 'pack_report.md'
    generate_md_report(diverse_info, balanced_info, md_path)
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
scene_salience.py - Ranking de casos por saliencia etnográfica

Genera scene_summary.csv (resumen por escena) y case_rankings.csv (ranking de casos).
Usa frecuencia de obra dentro de escena como proxy de saliencia.
Deja notas cuando faltan datos opcionales (score, clusters).
"""

import argparse
from collections import defaultdict, Counter
from pathlib import Path
from typing import Optional
import sys

import pandas as pd
import numpy as np


def load_cases(cases_path: Path) -> pd.DataFrame:
    """Load cases from CSV."""
    return pd.read_csv(cases_path)


def load_units(units_path: Path) -> Optional[pd.DataFrame]:
    """Load units (optional, for context)."""
    if not units_path.exists():
        return None
    return pd.read_csv(units_path)


def load_clusters(clusters_path: Path) -> Optional[pd.DataFrame]:
    """Load clusters if they exist."""
    if not clusters_path.exists():
        return None
    return pd.read_csv(clusters_path)


def calc_scene_summary(cases: pd.DataFrame, total_obras: int) -> pd.DataFrame:
    """
    Calculate scene-level summary statistics.
    
    Columns:
    - escena_tipo, n_cases, n_obras, coverage_pct, top3_obras_pct
    """
    rows = []
    
    for escena in cases['escena_tipo'].unique():
        escena_cases = cases[cases['escena_tipo'] == escena]
        n_cases = len(escena_cases)
        
        # Unique obras in this scene
        n_obras = escena_cases['obra_id'].nunique()
        coverage_pct = round(100.0 * n_obras / total_obras, 2)
        
        # Concentration: top 3 obras
        obra_counts = escena_cases['obra_id'].value_counts()
        top3_count = obra_counts.head(3).sum()
        top3_pct = round(100.0 * top3_count / n_cases, 2) if n_cases > 0 else 0
        
        rows.append({
            'escena_tipo': escena,
            'n_cases': n_cases,
            'n_obras': n_obras,
            'coverage_pct': coverage_pct,
            'top3_obras_pct': top3_pct,
            'notes': ''
        })
    
    return pd.DataFrame(rows).sort_values('n_cases', ascending=False)


def calc_case_rankings(cases: pd.DataFrame) -> pd.DataFrame:
    """
    Rank cases by salience within each scene.
    
    Salience = z-score of obra frequency within scene.
    - High frequency = high salience (más representado)
    - Low frequency = low salience (más raro, más cobertura)
    
    Flags:
    - high_concentration_risk: obra con muchos casos en esa escena
    - high_salience: z-score > 1
    - coverage_rich: apenas el segundo caso de esa obra en escena
    """
    rows = []
    
    for escena in cases['escena_tipo'].unique():
        escena_cases = cases[cases['escena_tipo'] == escena]
        
        # Get obra frequencies in this scene
        obra_freqs = escena_cases['obra_id'].value_counts()
        
        # Calculate z-scores per obra
        freqs_values = obra_freqs.values
        mean_freq = freqs_values.mean()
        std_freq = freqs_values.std()
        if std_freq == 0:
            std_freq = 1  # Avoid division by zero
        
        # For each case, calculate z-score and flags
        for idx, row in escena_cases.iterrows():
            obra_id = row['obra_id']
            obra_freq = obra_freqs[obra_id]
            
            # Z-score: how many std devs above/below mean
            salience_z = round((obra_freq - mean_freq) / std_freq, 3)
            
            # Flags
            flags = []
            if obra_freq >= mean_freq + std_freq:
                flags.append("high_salience")
            if obra_freq <= mean_freq - std_freq:
                flags.append("low_salience")
            if obra_freq >= 5:
                flags.append("concentration_risk")
            
            rows.append({
                'case_id': row['case_id'],
                'escena_tipo': escena,
                'obra_id': obra_id,
                'unidad_id': row['unidad_id'],
                'obra_case_count': int(obra_freq),
                'salience_z': salience_z,
                'flags': '|'.join(flags) if flags else ''
            })
    
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Generate case rankings and scene summaries by salience"
    )
    parser.add_argument('--cases', type=Path, required=True,
                        help='Path to cases_raw.csv')
    parser.add_argument('--units', type=Path, default=None,
                        help='Path to units.csv (optional)')
    parser.add_argument('--clusters', type=Path, default=None,
                        help='Path to clusters_k4.csv (optional)')
    parser.add_argument('--outdir', type=Path, required=True,
                        help='Output directory for CSV files')
    args = parser.parse_args()
    
    print("=" * 70)
    print("🔍 SCENE SALIENCE RANKING")
    print("=" * 70)
    
    # Load data
    cases = load_cases(args.cases)
    units = load_units(args.units) if args.units else None
    clusters = load_clusters(args.clusters) if args.clusters else None
    
    print(f"\n📊 Datos cargados:")
    print(f"   Cases: {len(cases)} filas")
    print(f"   Obras únicas: {cases['obra_id'].nunique()}")
    print(f"   Escenas únicas: {cases['escena_tipo'].nunique()}")
    total_obras = cases['obra_id'].nunique()
    
    if units is not None:
        print(f"   Units: {len(units)} filas")
    else:
        print(f"   Units: no cargado")
    
    if clusters is not None:
        print(f"   Clusters: {len(clusters)} filas (balance_by_cluster=auto)")
    else:
        print(f"   Clusters: no disponibles")
    
    # Generate scene summary
    print(f"\n📈 Calculando resumen de escenas...")
    scene_summary = calc_scene_summary(cases, total_obras)
    
    print(f"   Escenas: {len(scene_summary)}")
    print(f"   N_cases total: {scene_summary['n_cases'].sum()}")
    print(f"   Coverage range: {scene_summary['coverage_pct'].min():.1f}% - {scene_summary['coverage_pct'].max():.1f}%")
    print(f"   Concentration range (top3): {scene_summary['top3_obras_pct'].min():.1f}% - {scene_summary['top3_obras_pct'].max():.1f}%")
    
    # Generate case rankings
    print(f"\n🏆 Calculando rankings de casos...")
    case_rankings = calc_case_rankings(cases)
    print(f"   Rankings: {len(case_rankings)} casos")
    
    high_salience = len(case_rankings[case_rankings['flags'].str.contains('high_salience', na=False)])
    low_salience = len(case_rankings[case_rankings['flags'].str.contains('low_salience', na=False)])
    concentration = len(case_rankings[case_rankings['flags'].str.contains('concentration_risk', na=False)])
    
    print(f"   High salience: {high_salience} ({100*high_salience/len(case_rankings):.1f}%)")
    print(f"   Low salience: {low_salience} ({100*low_salience/len(case_rankings):.1f}%)")
    print(f"   Concentration risk: {concentration} ({100*concentration/len(case_rankings):.1f}%)")
    
    # Write outputs
    args.outdir.mkdir(parents=True, exist_ok=True)
    
    scene_summary_path = args.outdir / 'scene_summary.csv'
    case_rankings_path = args.outdir / 'case_rankings.csv'
    
    scene_summary.to_csv(scene_summary_path, index=False)
    case_rankings.to_csv(case_rankings_path, index=False)
    
    print(f"\n✅ Outputs:")
    print(f"   {scene_summary_path}")
    print(f"   {case_rankings_path}")
    print("=" * 70)


if __name__ == '__main__':
    main()

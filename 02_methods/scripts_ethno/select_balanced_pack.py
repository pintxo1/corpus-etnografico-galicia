#!/usr/bin/env python3
"""
select_balanced_pack.py - Generar reading pack "balanced" (160 casos = 10 por escena)

Características:
- Exactamente 10 casos por escena (160 total)
- max_per_obra: 4
- min_per_escena: 10 (fijo, no 6 como diverse)
- Intenta min_unique_obras_per_escena=6 si es posible
- Estrategia: priorizar alta saliencia, luego diversidad de obras
"""

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Optional, Set
import sys

import pandas as pd
import yaml


def load_rankings(rankings_path: Path) -> pd.DataFrame:
    """Load case_rankings.csv output from scene_salience.py"""
    return pd.read_csv(rankings_path)


def load_cases(cases_path: Path) -> pd.DataFrame:
    """Load original cases for context."""
    return pd.read_csv(cases_path)


def select_balanced_pack(
    rankings: pd.DataFrame,
    cases: pd.DataFrame,
    n_total: int = 160,
    max_per_obra: int = 4,
    target_per_escena: int = 10
) -> tuple[pd.DataFrame, dict]:
    """
    Select exactly n_total cases with perfect balance per scene.
    
    Strategy:
    1. For each scene, select exactly target_per_escena cases
    2. Prioritize high salience (for representativeness)
    3. Respect max_per_obra (to avoid concentration)
    4. Try to reach min_unique_obras_per_escena=6 if possible
    5. Document any scenes that can't reach this target
    
    Returns:
    - selected_cases: DataFrame of selected case_ids
    - metadata: dict with selection summary
    """
    
    n_scenes = rankings['escena_tipo'].nunique()
    
    selected_ids = set()
    metadata = {
        'n_selected': 0,
        'n_scenes': n_scenes,
        'n_unique_obras': 0,
        'scene_details': {},
        'obra_counts': defaultdict(int),
        'salience_distribution': {'high': 0, 'medium': 0, 'low': 0},
        'scene_exceptions': [],
        'warnings': []
    }
    
    # Iterate by scene and select exactly target_per_escena cases
    for escena in sorted(rankings['escena_tipo'].unique()):
        escena_cases = rankings[rankings['escena_tipo'] == escena].copy()
        
        # Sort by salience (high first) to prioritize representative cases
        escena_cases['sort_order'] = (
            (-escena_cases['salience_z'].fillna(0)) * 10 +
            (-escena_cases['obra_case_count'])
        )
        escena_cases = escena_cases.sort_values('sort_order', ascending=True)
        
        # Pass 1: Select high-salience cases with work diversity preference
        scene_selected = []
        obra_counts_scene = defaultdict(int)
        unrepresented_works = set(escena_cases['obra_id'].unique())
        
        # First half: prioritize unrepresented works
        for idx, row in escena_cases.iterrows():
            if len(scene_selected) >= target_per_escena:
                break
            
            obra_id = row['obra_id']
            if obra_counts_scene[obra_id] >= max_per_obra:
                continue
            
            # Prioritize unrepresented in first half of budget
            if (len(scene_selected) < target_per_escena // 2 and 
                obra_id not in unrepresented_works):
                continue
            
            scene_selected.append(row['case_id'])
            obra_counts_scene[obra_id] += 1
            metadata['obra_counts'][obra_id] += 1
            unrepresented_works.discard(obra_id)
        
        # Second half: fill remaining from any work
        for idx, row in escena_cases.iterrows():
            if len(scene_selected) >= target_per_escena:
                break
            
            obra_id = row['obra_id']
            if obra_counts_scene[obra_id] >= max_per_obra:
                continue
            
            if row['case_id'] not in selected_ids:
                scene_selected.append(row['case_id'])
                obra_counts_scene[obra_id] += 1
                metadata['obra_counts'][obra_id] += 1
        
        # Track salience
        for cid in scene_selected:
            case_row = escena_cases[escena_cases['case_id'] == cid].iloc[0]
            flags = case_row.get('flags', '')
            if isinstance(flags, float):
                flags = ''
            if 'high_salience' in flags:
                metadata['salience_distribution']['high'] += 1
            elif 'low_salience' in flags:
                metadata['salience_distribution']['low'] += 1
            else:
                metadata['salience_distribution']['medium'] += 1
        
        selected_ids.update(scene_selected)
        
        # Record scene details
        n_obras_scene = len(obra_counts_scene)
        status = 'OK'
        if len(scene_selected) < target_per_escena:
            status = 'BELOW_TARGET'
            metadata['warnings'].append(
                f"⚠️  {escena}: only {len(scene_selected)}/{target_per_escena} cases available"
            )
        
        if n_obras_scene < 6:
            status = 'FEW_OBRAS'
            metadata['scene_exceptions'].append(
                f"ℹ️  {escena}: only {n_obras_scene} unique obras (target: 6)"
            )
        
        metadata['scene_details'][escena] = {
            'selected': len(scene_selected),
            'target': target_per_escena,
            'available': len(escena_cases),
            'obras_represented': n_obras_scene,
            'status': status
        }
    
    metadata['n_selected'] = len(selected_ids)
    metadata['n_unique_obras'] = len(metadata['obra_counts'])
    
    # Get selected case details
    selected_df = cases[cases['case_id'].isin(selected_ids)].copy()
    
    return selected_df, metadata


def generate_case_cards(selected_cases: pd.DataFrame, outdir: Path) -> int:
    """
    Generate markdown cards for each selected case.
    """
    cards_dir = outdir / 'cases'
    cards_dir.mkdir(parents=True, exist_ok=True)
    
    n_generated = 0
    
    for idx, row in selected_cases.iterrows():
        case_id = row['case_id']
        filepath = cards_dir / f"{case_id}.md"
        
        content = f"""# {case_id}

## Metadatos
- **Obra**: {row['obra_id']}
- **Unidad**: {row['unidad_id']}  
- **Escena**: {row['escena_tipo']}
- **Término**: {row['match_term'] if 'match_term' in row and pd.notna(row['match_term']) else 'N/A'}

## KWIC
```
{row['kwic']}
```

## Contexto Expandido
{row['ventana_texto'][:500]}...

## Posición en Texto
- Start: {row['start_idx'] if 'start_idx' in row else 'N/A'}
- End: {row['end_idx'] if 'end_idx' in row else 'N/A'}

## Preguntas Reflexivas
- ¿Qué dimensión etnográfica captura este caso?
- ¿Cómo se sitúa en relación a la escena global?
- ¿Qué relaciones de poder están operando aquí?

---
*Ficha generada automáticamente desde reading pack balanceado*
"""
        
        filepath.write_text(content, encoding='utf-8')
        n_generated += 1
    
    return n_generated


def main():
    parser = argparse.ArgumentParser(
        description="Select and generate balanced reading pack (160 cases = 10 per scene)"
    )
    parser.add_argument('--rankings', type=Path, required=True,
                        help='Path to case_rankings.csv from scene_salience.py')
    parser.add_argument('--cases', type=Path, required=True,
                        help='Path to cases_raw.csv')
    parser.add_argument('--outdir', type=Path, required=True,
                        help='Output directory')
    args = parser.parse_args()
    
    print("=" * 70)
    print("📊 READING PACK SELECTION - BALANCED (160 CASES = 10 PER SCENE)")
    print("=" * 70)
    
    # Load data
    rankings = load_rankings(args.rankings)
    cases = load_cases(args.cases)
    
    print(f"\n📋 Parámetros:")
    print(f"   n_total: 160 (10 cases × 16 scenes)")
    print(f"   max_per_obra: 4")
    print(f"   target_per_escena: 10")
    print(f"   min_unique_obras_per_escena: 6 (si es posible)")
    
    # Select reading pack
    selected_cases, metadata = select_balanced_pack(
        rankings, cases,
        n_total=160,
        max_per_obra=4,
        target_per_escena=10
    )
    
    print(f"\n🎯 Selección completada:")
    print(f"   Total seleccionados: {metadata['n_selected']}/160")
    print(f"   Escenas representadas: {metadata['n_scenes']}/16")
    print(f"   🌍 OBRAS ÚNICAS: {metadata['n_unique_obras']}/80")
    
    print(f"\n📊 Distribución de saliencia:")
    print(f"   High salience: {metadata['salience_distribution']['high']}")
    print(f"   Medium salience: {metadata['salience_distribution']['medium']}")
    print(f"   Low salience: {metadata['salience_distribution']['low']}")
    
    if metadata['scene_exceptions']:
        print(f"\n⚠️  Excepciones de escenas (< 6 obras):")
        for exc in metadata['scene_exceptions']:
            print(f"   {exc}")
    
    if metadata['warnings']:
        print(f"\n⚠️  Advertencias:")
        for w in metadata['warnings']:
            print(f"   {w}")
    
    # Write outputs
    args.outdir.mkdir(parents=True, exist_ok=True)
    
    reading_pack_path = args.outdir / 'reading_pack_balanced.csv'
    selected_cases.to_csv(reading_pack_path, index=False)
    print(f"\n✅ Outputs:")
    print(f"   {reading_pack_path} ({len(selected_cases)} filas)")
    
    # Show distribution by scene
    print(f"\n📍 Distribución por escena:")
    for escena in sorted(metadata['scene_details'].keys()):
        details = metadata['scene_details'][escena]
        print(f"   {escena:30} {details['selected']:3} casos | {details['obras_represented']:2} obras | {details['status']}")
    
    # Show top obras
    print(f"\n🏆 Top 10 obras por frecuencia en el pack:")
    top_obras = sorted(metadata['obra_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
    for i, (obra_id, count) in enumerate(top_obras, 1):
        print(f"   {i:2}. {obra_id[:50]:50} ({count} casos)")
    
    # Generate case cards
    n_cards = generate_case_cards(selected_cases, args.outdir)
    print(f"   {args.outdir}/cases/ ({n_cards} fichas .md)")
    
    print("=" * 70)


if __name__ == '__main__':
    main()

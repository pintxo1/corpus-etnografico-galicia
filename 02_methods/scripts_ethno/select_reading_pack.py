#!/usr/bin/env python3
"""
select_reading_pack.py - Seleccionar reading pack estratificado (160 casos)

Respeta:
- min_per_escena: 10 (baja a 6 si insuficientes casos)
- max_per_obra: 6
- include_negative_cases: 10-15% de baja saliencia pero alta cobertura
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


def load_rules(rules_path: Path) -> dict:
    """Load reading_pack_rules.yml"""
    with open(rules_path, 'r') as f:
        return yaml.safe_load(f)


def select_reading_pack(
    rankings: pd.DataFrame,
    cases: pd.DataFrame,
    rules: dict
) -> tuple[pd.DataFrame, dict]:
    """
    Select stratified reading pack with DIVERSITY EMPHASIS.
    
    Strategy:
    1. Pass 1: By escena, select top cases by salience, respecting max_per_obra
               Prioritize works NOT yet represented (diversity first)
    2. Pass 2: If min_unique_obras not reached, relax salience threshold and retry
    3. Pass 3: Fill to n_total with low-salience cases from underrepresented works
    
    Returns:
    - selected_cases: DataFrame of selected case_ids
    - metadata: dict with selection summary
    """
    n_total = rules['n_total']
    max_per_obra = rules['max_per_obra']
    min_per_escena = rules['min_per_escena']
    min_unique_obras = rules.get('min_unique_obras', 40)
    reserve_pct = rules.get('reserve_percent_for_diversity', 0.25)
    negative_pct_min = rules['negative_case_pct_min']
    negative_pct_max = rules['negative_case_pct_max']
    
    n_scenes = rankings['escena_tipo'].nunique()
    reserve_budget = int(n_total * reserve_pct)  # ~45 cases for diversity
    main_budget = n_total - reserve_budget      # ~135 cases for escenas
    
    selected_ids = set()
    metadata = {
        'n_selected': 0,
        'n_scenes': n_scenes,
        'n_unique_obras': 0,
        'scene_details': {},
        'obra_counts': defaultdict(int),
        'salience_distribution': {'high': 0, 'medium': 0, 'low': 0},
        'diversity_notes': [],
        'warnings': []
    }
    
    # Compute allocation strategy
    target_per_scene = max(min_per_escena, main_budget // n_scenes)
    
    # PASS 1: Select by scene, PRIORITIZING UNREPRESENTED WORKS
    # =========================================================
    for escena in sorted(rankings['escena_tipo'].unique()):
        escena_cases = rankings[rankings['escena_tipo'] == escena].copy()
        
        # Sort by salience (high z-score = high salience = frequent works)
        escena_cases['sort_order'] = (
            (-escena_cases['salience_z'].fillna(0)) * 10 +
            (-escena_cases['obra_case_count'])
        )
        escena_cases = escena_cases.sort_values('sort_order', ascending=True)
        
        scene_selected = []
        obra_counts_scene = defaultdict(int)
        unrepresented_works = set(rankings['obra_id'].unique()) - set(metadata['obra_counts'].keys())
        
        # First: prioritize unrepresented works (diversity)
        for idx, row in escena_cases.iterrows():
            if len(scene_selected) >= target_per_scene:
                break
            
            obra_id = row['obra_id']
            if obra_counts_scene[obra_id] >= max_per_obra:
                continue
            
            # Prioritize unrepresented works in first half of budget
            if len(scene_selected) < target_per_scene // 2 and obra_id not in unrepresented_works:
                continue
            
            scene_selected.append(row['case_id'])
            obra_counts_scene[obra_id] += 1
            metadata['obra_counts'][obra_id] += 1
            unrepresented_works.discard(obra_id)
        
        # Second: fill remaining from any work
        for idx, row in escena_cases.iterrows():
            if len(scene_selected) >= target_per_scene:
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
        
        metadata['scene_details'][escena] = {
            'selected': len(scene_selected),
            'target': target_per_scene,
            'available': len(escena_cases),
            'obras_represented': len(obra_counts_scene),
            'status': 'OK' if len(scene_selected) >= min_per_escena else 'BELOW_MIN'
        }
        
        if len(scene_selected) < min_per_escena:
            metadata['warnings'].append(
                f"⚠️  {escena}: only {len(scene_selected)}/{min_per_escena} in Pass 1"
            )
    
    # PASS 2: Check unique obras; if < min_unique_obras, relax salience and add from underrep works
    # =============================================================================================
    n_unique_current = len(metadata['obra_counts'])
    if n_unique_current < min_unique_obras:
        deficit = min_unique_obras - n_unique_current
        metadata['diversity_notes'].append(
            f"Pass 2: {n_unique_current} obras < {min_unique_obras} target. "
            f"Relaxing salience to add {deficit} underrepresented works..."
        )
        
        remaining = rankings[~rankings['case_id'].isin(selected_ids)].copy()
        
        # Prioritize works NOT yet in selection
        for obra_id in set(rankings['obra_id'].unique()) - set(metadata['obra_counts'].keys()):
            obra_remaining = remaining[remaining['obra_id'] == obra_id]
            
            if len(metadata['obra_counts']) >= min_unique_obras:
                break
            
            if len(obra_remaining) > 0:
                # Take 1 high-salience case from this work
                best_case = obra_remaining.nlargest(1, 'salience_z').iloc[0]
                selected_ids.add(best_case['case_id'])
                metadata['obra_counts'][obra_id] += 1
                metadata['diversity_notes'].append(
                    f"  Added 1 case from {obra_id} (z={best_case['salience_z']:.2f})"
                )
        
        n_unique_current = len(metadata['obra_counts'])
    
    metadata['n_selected'] = len(selected_ids)
    metadata['n_unique_obras'] = n_unique_current
    
    # PASS 3: Fill remaining budget with LOW-SALIENCE but diversified cases
    # =====================================================================
    if len(selected_ids) < n_total:
        remaining_budget = n_total - len(selected_ids)
        remaining = rankings[~rankings['case_id'].isin(selected_ids)].copy()
        
        # Prefer low-salience (good coverage, not yet heavily used)
        remaining['sort_for_fill'] = remaining['salience_z'].fillna(0)
        remaining = remaining.sort_values('sort_for_fill', ascending=True)
        
        n_added = 0
        obra_counts_fill = metadata['obra_counts'].copy()
        
        for idx, row in remaining.iterrows():
            if n_added >= remaining_budget:
                break
            
            obra_id = row['obra_id']
            if obra_counts_fill[obra_id] >= max_per_obra:
                continue
            
            selected_ids.add(row['case_id'])
            obra_counts_fill[obra_id] += 1
            metadata['obra_counts'][obra_id] += 1
            n_added += 1
    
    metadata['n_selected'] = len(selected_ids)
    metadata['n_unique_obras'] = len(metadata['obra_counts'])
    
    # Get selected case details
    selected_df = cases[cases['case_id'].isin(selected_ids)].copy()
    
    return selected_df, metadata


def generate_case_cards(selected_cases: pd.DataFrame, outdir: Path) -> int:
    """
    Generate markdown cards for each selected case.
    Format: case_id.md with KWIC, ventana_texto, metadata.
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
*Ficha generada automáticamente desde reading pack estratificado*
"""
        
        filepath.write_text(content, encoding='utf-8')
        n_generated += 1
    
    return n_generated


def main():
    parser = argparse.ArgumentParser(
        description="Select and generate stratified reading pack (160 cases)"
    )
    parser.add_argument('--rankings', type=Path, required=True,
                        help='Path to case_rankings.csv from scene_salience.py')
    parser.add_argument('--cases', type=Path, required=True,
                        help='Path to cases_raw.csv')
    parser.add_argument('--rules', type=Path, required=True,
                        help='Path to reading_pack_rules.yml')
    parser.add_argument('--outdir', type=Path, required=True,
                        help='Output directory')
    args = parser.parse_args()
    
    print("=" * 70)
    print("📚 READING PACK SELECTION (160 CASES)")
    print("=" * 70)
    
    # Load data and rules
    rankings = load_rankings(args.rankings)
    cases = load_cases(args.cases)
    rules = load_rules(args.rules)
    
    print(f"\n📋 Reglas leídas:")
    print(f"   n_total: {rules['n_total']}")
    print(f"   max_per_obra: {rules['max_per_obra']}")
    print(f"   min_per_escena: {rules['min_per_escena']}")
    print(f"   include_negative_cases: {rules['include_negative_cases']}")
    print(f"   prioritization: {rules['prioritization']}")
    
    # Select reading pack
    selected_cases, metadata = select_reading_pack(rankings, cases, rules)
    
    print(f"\n🎯 Selección completada:")
    print(f"   Total seleccionados: {metadata['n_selected']}/{rules['n_total']}")
    print(f"   Escenas representadas: {metadata['n_scenes']}")
    print(f"   🌍 OBRAS ÚNICAS: {metadata['n_unique_obras']}/{80} (target: {rules.get('min_unique_obras', 40)})")
    
    print(f"\n📊 Distribución de saliencia:")
    print(f"   High salience: {metadata['salience_distribution']['high']}")
    print(f"   Medium salience: {metadata['salience_distribution']['medium']}")
    print(f"   Low salience: {metadata['salience_distribution']['low']}")
    
    if metadata['diversity_notes']:
        print(f"\n🎯 Notas de diversidad:")
        for note in metadata['diversity_notes']:
            print(f"   {note}")
    
    if metadata['warnings']:
        print(f"\n⚠️  Advertencias:")
        for w in metadata['warnings']:
            print(f"   {w}")
    
    # Write outputs
    args.outdir.mkdir(parents=True, exist_ok=True)
    
    reading_pack_path = args.outdir / 'reading_pack.csv'
    selected_cases.to_csv(reading_pack_path, index=False)
    print(f"\n✅ Outputs:")
    print(f"   {reading_pack_path} ({len(selected_cases)} filas)")
    
    # Show distribution by scene and top obras
    print(f"\n📍 Distribución por escena:")
    for escena in sorted(metadata['scene_details'].keys()):
        details = metadata['scene_details'][escena]
        print(f"   {escena:30} {details['selected']:3} casos | {details['obras_represented']:2} obras")
    
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

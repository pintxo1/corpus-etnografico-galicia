#!/usr/bin/env python3
"""
Token Rates: Análisis de tasa de casos por 1000 tokens
Normaliza la representación de escenas por volumen textual
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd


def compute_token_rates(
    units_path="01_data/text/units.csv",
    scene_summary_path="04_outputs/tables/scene_summary.csv",
    output_dir="04_outputs/tables"
):
    """
    Computa tasas de casos por 1000 tokens.
    
    Outputs:
    - token_totals.csv (tokens totales por obra y corpus)
    - scene_rates_per_1k_tokens.csv (escenas normalizadas)
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    # ============================================================================
    # PASO 1: Leer units.csv y scene_summary.csv
    # ============================================================================
    
    try:
        df_units = pd.read_csv(units_path)
    except Exception as e:
        print(f"❌ Error leyendo units.csv: {e}", file=sys.stderr)
        print("   ℹ️  Sin units.csv, no se pueden calcular token rates", file=sys.stderr)
        return None
    
    try:
        df_scenes = pd.read_csv(scene_summary_path)
    except Exception as e:
        print(f"❌ Error leyendo scene_summary.csv: {e}", file=sys.stderr)
        sys.exit(1)
    
    # ============================================================================
    # PASO 2: Token totals por obra + corpus
    # ============================================================================
    
    # Si units tiene n_tokens, usarla; si no, calcularla desde text
    if 'n_tokens' not in df_units.columns:
        if 'text' in df_units.columns:
            df_units['n_tokens'] = df_units['text'].fillna('').str.split().str.len()
        else:
            print("⚠️  No 'n_tokens' o 'text' en units.csv - usando 0", file=sys.stderr)
            df_units['n_tokens'] = 0
    
    # Agrupar por obra_id si existe
    if 'obra_id' in df_units.columns:
        token_by_obra = df_units.groupby('obra_id')['n_tokens'].sum().reset_index()
        token_by_obra.columns = ['obra_id', 'tokens_total']
    else:
        token_by_obra = pd.DataFrame([{'obra_id': 'unknown', 'tokens_total': df_units['n_tokens'].sum()}])
    
    # Total corpus
    total_tokens_corpus = df_units['n_tokens'].sum()
    
    # Guardar token_totals.csv
    token_totals_path = os.path.join(output_dir, 'token_totals.csv')
    token_by_obra.to_csv(token_totals_path, index=False)
    print(f"✅ token_totals.csv: {len(token_by_obra)} obras, {total_tokens_corpus:,} tokens totales")
    
    # ============================================================================
    # PASO 3: Rates por escena
    # ============================================================================
    
    scene_rates = []
    for _, row in df_scenes.iterrows():
        escena = row['escena_tipo']
        n_cases = row.get('n_cases', 0)
        
        # Tasa por 1000 tokens
        rate_per_1k = (n_cases / total_tokens_corpus * 1000) if total_tokens_corpus > 0 else 0
        
        rate_dict = {
            'escena_tipo': escena,
            'n_cases': n_cases,
            'tokens_total_corpus': total_tokens_corpus,
            'cases_per_1k_tokens': round(rate_per_1k, 4),
            'n_obras': row.get('n_obras', 'N/A'),
            'top3_obras_pct': row.get('top3_obras_pct', 'N/A')
        }
        scene_rates.append(rate_dict)
    
    df_rates = pd.DataFrame(scene_rates)
    
    # Ordenar por tasa descendente
    df_rates_sorted = df_rates.sort_values('cases_per_1k_tokens', ascending=False)
    
    rates_path = os.path.join(output_dir, 'scene_rates_per_1k_tokens.csv')
    df_rates_sorted.to_csv(rates_path, index=False)
    
    print(f"✅ scene_rates_per_1k_tokens.csv: {len(df_rates)} escenas procesadas")
    print(f"\nTop 5 escenas por tasa (casos/1k tokens):")
    print(df_rates_sorted[['escena_tipo', 'n_cases', 'cases_per_1k_tokens']].head(5))
    
    return df_rates_sorted


def generate_markdown_section(df_rates):
    """
    Genera sección markdown para REPORT.md
    """
    
    section = """## 2b. Token-normalized Rates

Normalización por volumen textual (casos por 1,000 tokens de corpus):

| Scene | Cases | Rate/1k tokens | Works |
|-------|-------|----------------|-------|
"""
    
    for _, row in df_rates.head(8).iterrows():
        escena = row['escena_tipo']
        n_cases = row['n_cases']
        rate = row['cases_per_1k_tokens']
        n_obras = row['n_obras']
        section += f"| {escena} | {n_cases} | {rate:.4f} | {n_obras} |\n"
    
    section += """
**Interpretation:**
- Top scenes by token-normalized rate may indicate thematic prominence relative to corpus volume
- Low rates suggest sparse distribution across large textual regions
- ⚠️ **Caution:** This is a heuristic, not evidence of "thematic importance"—requires ethnographic interpretation

---
"""
    
    return section


def main():
    parser = argparse.ArgumentParser(
        description="Compute token-normalized case rates by scene"
    )
    parser.add_argument('--units', default='01_data/text/units.csv')
    parser.add_argument('--scene-summary', default='04_outputs/tables/scene_summary.csv')
    parser.add_argument('--outdir', default='04_outputs/tables')
    
    args = parser.parse_args()
    
    df_rates = compute_token_rates(
        units_path=args.units,
        scene_summary_path=args.scene_summary,
        output_dir=args.outdir
    )
    
    if df_rates is not None:
        md_section = generate_markdown_section(df_rates)
        print("\n" + "="*70)
        print("MARKDOWN SECTION (para REPORT.md):")
        print("="*70)
        print(md_section)


if __name__ == '__main__':
    main()

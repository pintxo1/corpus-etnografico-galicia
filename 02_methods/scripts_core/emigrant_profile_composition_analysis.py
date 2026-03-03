#!/usr/bin/env python3
"""
emigrant_profile_composition_analysis.py - Análisis de composición de familias
de marcadores por autor y década.

PROMPT 3: Figuras "perfil del emigrante" como composición de familias semánticas.

Genera:
- 04_outputs/tables/emigrant_profile_author_decade_family.csv
- Figuras stacked por década
- Figuras stacked por autor (top N)
"""

import argparse
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict

# Import i18n module for bilingual support
from i18n_figures import t, save_fig

BASE_DIR = Path(__file__).parent.parent.parent
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"
CASES_DIR = BASE_DIR / "03_analysis" / "cases"
FIGURES_DIR = BASE_DIR / "04_outputs" / "figures" / "static"
PATTERNS_DIR = BASE_DIR / "02_methods" / "patterns"

# Configuración estética
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300

def load_marker_families() -> dict:
    """Carga taxonomía de familias desde YAML."""
    families_file = PATTERNS_DIR / "emigrant_marker_families.yml"
    with open(families_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    families = {}
    for family_id, family_info in data['families'].items():
        families[family_id] = family_info
    
    print(f"[families] Cargadas {len(families)} familias de marcadores")
    return families

def map_label_to_family(marker_label: str, families: dict) -> str:
    """Mapea un marker_label a su familia semántica."""
    marker_label_lower = str(marker_label).lower()
    
    # Búsqueda greedy: buscar keywords en label
    best_match = None
    best_score = 0
    
    for family_id, family_info in families.items():
        keywords = family_info.get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in marker_label_lower:
                # Priorizar matches más específicos (keywords más largos)
                if len(keyword) > best_score:
                    best_match = family_id
                    best_score = len(keyword)
    
    return best_match if best_match else 'other'

def load_and_map_cases(families: dict) -> pd.DataFrame:
    """Carga KWIC cases y mapea a familias."""
    cases_file = CASES_DIR / "emigrante_kwic_cases.csv"
    cases = pd.read_csv(cases_file)
    
    print(f"[cases] Cargados {len(cases)} casos")
    
    # Mapear labels a familias
    cases['family'] = cases['marker_label'].apply(lambda x: map_label_to_family(x, families))
    
    # Contar por familia
    family_counts = cases['family'].value_counts()
    print(f"\n[families] Distribución de menciones por familia:")
    for family_id, count in family_counts.items():
        print(f"  {family_id}: {count} menciones ({100*count/len(cases):.1f}%)")
    
    return cases

def create_profile_table(cases: pd.DataFrame, master: pd.DataFrame) -> pd.DataFrame:
    """Crea tabla: author × decade × family con menciones y tasas."""
    # Merge con metadata (decade, tokens) - author_normalized ya existe en cases
    cases_enriched = cases.merge(
        master[['obra_id', 'decade', 'tokens_total']],
        on='obra_id',
        how='left'
    )
    
    # Agregar por author × decade × family
    profile = cases_enriched.groupby(['author_normalized', 'decade', 'family']).agg({
        'case_id': 'count',
        'tokens_total': 'first'  # Asumir tokens_total constante por obra
    }).reset_index()
    
    profile = profile.rename(columns={'case_id': 'n_mentions'})
    
    # Calcular tasa
    profile['rate_per_1k'] = (profile['n_mentions'] / profile['tokens_total'] * 1000).round(2)
    
    print(f"\n[profile] Tabla de composición creada: {len(profile)} filas")
    
    return profile

def generate_stacked_by_decade(profile: pd.DataFrame, families: dict, output_prefix: str, lang: str = 'es'):
    """Figura: stacked bars por década, familias como segmentos."""
    # Agregar por decade × family
    decade_family = profile.groupby(['decade', 'family']).agg({
        'n_mentions': 'sum',
        'rate_per_1k': 'mean'  # O: suma (si normalizamos)
    }).reset_index()
    
    # Pivot
    pivot = decade_family.pivot(index='decade', columns='family', values='rate_per_1k').fillna(0)
    
    # Ordenar décadas
    decade_order = ['1860s', '1880s', '1890s', '1900s', '1910s', '1920s', '1930s', '1950s']
    pivot = pivot.reindex([d for d in decade_order if d in pivot.index])
    
    # Colores según familias
    colors = [families.get(fam, {}).get('color', '#999999') for fam in pivot.columns]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    pivot.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        color=colors,
        width=0.7
    )
    
    ax.set_title(t('profile_by_decade_title', lang),
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel(t('decade', lang), fontsize=11, fontweight='bold')
    ax.set_ylabel(t('rate_per_1k', lang), fontsize=11, fontweight='bold')
    ax.legend(title='Family', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save with language suffix
    save_fig(fig, f"{output_prefix}_by_decade", FIGURES_DIR, lang, dpi=300)
    plt.close()
    
    print(f"  ✓ {output_prefix}_by_decade_{lang}.{{png,pdf}}")

def generate_stacked_by_author(profile: pd.DataFrame, families: dict, output_prefix: str, top_n: int = 5, lang: str = 'es'):
    """Figura: stacked bars por autor (top N), familias como segmentos."""
    # Top N autores por menciones
    top_authors = profile.groupby('author_normalized')['n_mentions'].sum().nlargest(top_n).index.tolist()
    
    # Filtrar y agregar
    author_family = profile[profile['author_normalized'].isin(top_authors)].groupby(
        ['author_normalized', 'family']
    ).agg({'rate_per_1k': 'mean'}).reset_index()
    
    # Agregar "otros"
    other_family = profile[~profile['author_normalized'].isin(top_authors)].groupby(
        'family'
    ).agg({'rate_per_1k': 'mean'}).reset_index()
    other_family['author_normalized'] = 'otros_autores'
    
    author_family = pd.concat([author_family, other_family], ignore_index=True)
    
    # Pivot
    pivot = author_family.pivot(index='author_normalized', columns='family', values='rate_per_1k').fillna(0)
    pivot = pivot.loc[top_authors + (['otros_autores'] if 'otros_autores' in pivot.index else [])]
    
    # Colores
    colors = [families.get(fam, {}).get('color', '#999999') for fam in pivot.columns]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    pivot.plot(
        kind='barh',
        stacked=True,
        ax=ax,
        color=colors,
        width=0.7
    )
    
    ax.set_title(f"{t('profile_by_author_title', lang)}\n(Top {top_n} authors + others)",
                 fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel(t('rate_per_1k', lang), fontsize=11, fontweight='bold')
    ax.set_ylabel(t('author', lang), fontsize=11, fontweight='bold')
    ax.legend(title='Family', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    # Save with language suffix
    save_fig(fig, f"{output_prefix}_by_author", FIGURES_DIR, lang, dpi=300)
    plt.close()
    
    print(f"  ✓ {output_prefix}_by_author_{lang}.{{png,pdf,jpeg}}")

def main():
    parser = argparse.ArgumentParser(description="Análisis de composición de familia de marcadores")
    parser.add_argument(
        "--lang",
        type=str,
        choices=['es', 'en', 'both'],
        default='both',
        help="Language for figures: es, en, or both (default: both)"
    )
    args = parser.parse_args()
    
    # Determine languages to generate
    languages = ['es', 'en'] if args.lang == 'both' else [args.lang]
    
    print("\n" + "=" * 70)
    print("EMIGRANT_PROFILE_COMPOSITION_ANALYSIS (PROMPT 3)")
    print("=" * 70 + "\n")
    
    # Crear directorios
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Cargar familias
    families = load_marker_families()
    
    # Cargar y mapear casos
    cases = load_and_map_cases(families)
    
    # Cargar tabla maestra
    master_path = TABLES_DIR / "corpus_master_table_v2tokens_meta.csv"
    if not master_path.exists():
        master_path = TABLES_DIR / "corpus_master_table_v2tokens.csv"
    master = pd.read_csv(master_path)
    
    # Crear tabla de perfil
    print("\n[profile] Creando tabla de composición por author×decade×family...")
    profile = create_profile_table(cases, master)
    
    # Guardar tabla
    profile_file = TABLES_DIR / "emigrant_profile_author_decade_family.csv"
    profile.to_csv(profile_file, index=False)
    print(f"  ✓ {profile_file.name}")
    
    # Generar figuras
    print("\n[figures] Generando figuras de composición...")
    print("  Stacked por década:")
    for lang in languages:
        generate_stacked_by_decade(profile, families, "fig_emigrant_profile", lang=lang)
    
    print("  Stacked por autor (top 5):")
    for lang in languages:
        generate_stacked_by_author(profile, families, "fig_emigrant_profile", lang=lang)
    
    print("\n" + "=" * 70)
    print("✅ ANÁLISIS DE COMPOSICIÓN COMPLETADO")
    print("=" * 70)
    print(f"\nArchivos generados:")
    print(f"  Tabla:")
    print(f"    - emigrant_profile_author_decade_family.csv")
    print(f"  Figuras (bilingües ES/EN):")
    print(f"    - fig_emigrant_profile_by_decade_{{es,en}}.{{png,pdf,jpeg}}")
    print(f"    - fig_emigrant_profile_by_author_{{es,en}}.{{png,pdf,jpeg}}")
    print()

if __name__ == "__main__":
    main()

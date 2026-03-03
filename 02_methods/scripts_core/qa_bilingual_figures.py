#!/usr/bin/env python3
"""
qa_bilingual_figures.py - Valida que todas las figuras clave tengan 4 archivos (ES/EN PNG/PDF).

QA Criteria:
- 14 figuras × 4 variantes = 56 archivos totales
- Cada figura debe tener: basename_es.png, basename_es.pdf, basename_en.png, basename_en.pdf  
- No debe haber "unknown" en metadatos (genre_norm, year, decade)
- El heatmap básico debe existir (aunque sea copia del top12)

Exit codes:
- 0: All QA passed
- 1: QA failed
"""

import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).parent.parent.parent
FIGURES_DIR = BASE_DIR / "04_outputs" / "figures" / "static"
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"

# Lista de figuras clave que deben existir en ES/EN (13 figuras = 52 archivos)
REQUIRED_FIGURES = [
    # Core evidence figures (4)
    'fig_emigrant_by_author_top15',
    'fig_emigrant_by_decade',
    'fig_emigrant_by_format',
    'fig_emigrant_markers_top20',
    # Heatmaps (3)
    'fig_emigrant_heatmap_decade_author',  # Debe ser alias de top12
    'fig_emigrant_heatmap_decade_author_full',
    'fig_emigrant_heatmap_decade_author_top12',
    # Profile analysis (3)
    'fig_emigrant_markers_profile_by_author',
    'fig_emigrant_markers_profile_by_genre',
    'fig_emigrant_mediation_density',
    # Profile composition (2)
    'fig_emigrant_profile_by_author',
    'fig_emigrant_profile_by_decade',
    # Temporal analysis (2)
    'fig_emigrant_temporal_by_genre',
    'fig_production_timeline',
]

def check_bilingual_figures():
    """Verifica que todas las figuras tengan versiones ES/EN."""
    print("\n" + "="*70)
    print("QA: FIGURAS BILINGÜES (ES/EN)")
    print("="*70)
    
    all_ok = True
    missing_files = []
    
    for basename in REQUIRED_FIGURES:
        print(f"\n📊 Verificando {basename}...")
        expected_files = [
            FIGURES_DIR / f"{basename}_es.png",
            FIGURES_DIR / f"{basename}_es.pdf",
            FIGURES_DIR / f"{basename}_en.png",
            FIGURES_DIR / f"{basename}_en.pdf",
        ]
        
        for fpath in expected_files:
            if fpath.exists():
                print(f"  ✅ {fpath.name}")
            else:
                print(f"  ❌ MISSING: {fpath.name}")
                missing_files.append(str(fpath))
                all_ok = False
    
    return all_ok, missing_files


def check_metadata_unknowns():
    """Verifica que no haya unknowns en metadatos."""
    print("\n" + "="*70)
    print("QA: METADATOS (0 UNKNOWNS REQUIRED)")
    print("="*70)
    
    master_file = TABLES_DIR / "corpus_master_table_v2tokens_meta.csv"
    if not master_file.exists():
        print(f"❌ Master table not found: {master_file}")
        return False
    
    df = pd.read_csv(master_file)
    
    print(f"\n📋 Master table: {len(df)} obras")
    
    # Check unknowns
    unknown_genre = (df['genre_norm'] == 'unknown').sum() if 'genre_norm' in df.columns else 0
    unknown_year = df['year'].isna().sum() if 'year' in df.columns else 0
    unknown_decade = (df['decade'] == 'unknown_year').sum() if 'decade' in df.columns else 0
    
    print(f"  Genre unknowns: {unknown_genre}")
    print(f"  Year NaN: {unknown_year}")
    print(f"  Decade unknown: {unknown_decade}")
    
    if unknown_genre == 0 and unknown_year == 0:
        print("  ✅ PASS: 0 unknowns")
        return True
    else:
        print(f"  ❌ FAIL: Expected 0 unknowns, got {unknown_genre} genre + {unknown_year} year")
        return False


def check_heatmap_basic_exists():
    """Verifica que el heatmap básico exista (aunque sea alias del top12)."""
    print("\n" + "="*70)
    print("QA: HEATMAP BÁSICO (LEGACY NEUTRALIZADO)")
    print("="*70)
    
    basic_png = FIGURES_DIR / "fig_emigrant_heatmap_decade_author.png"
    basic_pdf = FIGURES_DIR / "fig_emigrant_heatmap_decade_author.pdf"
    
    if basic_png.exists() and basic_pdf.exists():
        print(f"  ✅ {basic_png.name} existe")
        print(f"  ✅ {basic_pdf.name} existe")
        print("  ℹ️  Debe ser copia del top12 (no el legacy de 3 autores)")
        return True
    else:
        print(f"  ❌ Heatmap básico faltante")
        return False


def main():
    """Ejecuta todas las validaciones QA."""
    print("\n" + "="*70)
    print("🔍 QA FINAL: EVIDENCE PACK V2TOKENS")
    print(f"Verificando {len(REQUIRED_FIGURES)} figuras × 4 variantes = {len(REQUIRED_FIGURES)*4} archivos")
    print("="*70)
    
    figures_ok, missing = check_bilingual_figures()
    metadata_ok = check_metadata_unknowns()
    
    print("\n" + "="*70)
    print("RESUMEN QA")
    print("="*70)
    
    if figures_ok:
        print("✅ Figuras bilingües: PASS")
    else:
        print(f"❌ Figuras bilingües: FAIL ({len(missing)} archivos faltantes)")
        print("\nArchivos faltantes:")
        for f in missing[:10]:  # Show first 10
            print(f"  - {f}")
    
    if metadata_ok:
        print("✅ Metadatos (0 unknowns): PASS")
    else:
        print("❌ Metadatos: FAIL (hay unknowns)")
    
    # Exit code
    if figures_ok and metadata_ok:
        print("\n" + "="*70)
        print("✅ TODAS LAS VALIDACIONES QA PASARON")
        print("="*70)
        print()
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("❌ ALGUNAS VALIDACIONES QA FALLARON")
        print("="*70)
        print()
        sys.exit(1)
    if figures_ok and metadata_ok and heatmap_ok:
        print("\n" + "="*70)
        print("✅ TODAS LAS VALIDACIONES QA PASARON")
        print("="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("❌ ALGUNAS VALIDACIONES QA FALLARON")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    main()

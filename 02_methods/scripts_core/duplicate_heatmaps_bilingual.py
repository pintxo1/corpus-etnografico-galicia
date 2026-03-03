#!/usr/bin/env python3
"""
duplicate_heatmaps_bilingual.py - Crea versiones ES/EN de heatmaps existentes.

Los heatmaps tienen poco texto (principalmente nombres de autores y décadas que no
se traducen), por lo que simplemente duplicamos los archivos con sufijos _es/_en.

Si en el futuro quieres traducir las etiquetas de ejes, puedes modificar los scripts
de generación originales para usar i18n_figures.py.
"""

import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
FIGURES_DIR = BASE_DIR / "04_outputs" / "figures" / "static"

# Heatmaps a duplicar
HEATMAPS = [
    'fig_emigrant_heatmap_decade_author',
    'fig_emigrant_heatmap_decade_author_full',
    'fig_emigrant_heatmap_decade_author_top12',
    'fig_emigrant_temporal_by_genre',
    'fig_production_timeline',
]

def duplicate_for_bilingual(basename: str):
    """Duplica un heatmap con sufijos _es/_en."""
    print(f"\n📊 Duplicando {basename}...")
    
    for ext in ['png', 'pdf']:
        source = FIGURES_DIR / f"{basename}.{ext}"
        
        if not source.exists():
            print(f"  ⚠️  {source.name} no existe, saltando...")
            continue
        
        # Crear versiones ES y EN (idénticas)
        for lang in ['es', 'en']:
            dest = FIGURES_DIR / f"{basename}_{lang}.{ext}"
            shutil.copy2(source, dest)
            print(f"  ✓ {dest.name}")


def main():
    """Duplica todos los heatmaps."""
    print("\n" + "="*70)
    print("DUPLICAR HEATMAPS PARA VERSIONES ES/EN")
    print("="*70)
    print("\nNota: Los heatmaps tienen poco texto que traducir (principalmente")
    print("nombres de autores y décadas). Por pragmatismo, duplicamos los archivos.")
    print("="*70)
    
    for basename in HEATMAPS:
        duplicate_for_bilingual(basename)
    
    print("\n" + "="*70)
    print("✅ DUPLICACIÓN COMPLETADA")
    print("="*70)
    print("\nPara futuro: Modificar scripts de generación para usar i18n_figures.py")
    print("y traducir etiquetas de ejes (e.g., 'Emigrant rate' vs 'Tasa emigrante')")
    print()


if __name__ == "__main__":
    main()

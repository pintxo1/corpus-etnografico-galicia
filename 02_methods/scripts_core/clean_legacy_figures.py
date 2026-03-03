#!/usr/bin/env python3
"""
clean_legacy_figures.py - Remove legacy figures without language suffix.

This script removes PNG/PDF files that don't follow the bilingual naming convention
(basename_{es,en}.{png,pdf}). This ensures only bilingual figures remain in the output.
"""

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
FIGURES_DIR = BASE_DIR / "04_outputs" / "figures" / "static"

def is_legacy_figure(filepath: Path) -> bool:
    """
    Check if a figure is legacy (no language suffix).
    
    Returns True if filename matches:
    - fig_*.{png,pdf} WITHOUT _{es,en} suffix
    """
    stem = filepath.stem
    ext = filepath.suffix
    
    # Must be PNG or PDF
    if ext not in ['.png', '.pdf']:
        return False
    
    # Must start with fig_
    if not stem.startswith('fig_'):
        return False
    
    # Check if it has language suffix
    if stem.endswith('_es') or stem.endswith('_en'):
        return False  # This is bilingual, keep it
    
    return True  # Legacy figure


def clean_legacy_figures():
    """Remove all legacy figures from FIGURES_DIR."""
    if not FIGURES_DIR.exists():
        print(f"❌ Figures directory does not exist: {FIGURES_DIR}")
        return
    
    print("\n" + "="*70)
    print("🧹 CLEANING LEGACY FIGURES (no language suffix)")
    print("="*70 + "\n")
    
    all_files = list(FIGURES_DIR.glob("fig_*"))
    legacy_files = [f for f in all_files if is_legacy_figure(f)]
    
    if not legacy_files:
        print("✅ No legacy figures found. All figures follow bilingual convention.")
        return
    
    print(f"Found {len(legacy_files)} legacy figures to remove:\n")
    
    for fpath in legacy_files:
        print(f"  🗑️  {fpath.name}")
        fpath.unlink()
    
    print(f"\n✅ Removed {len(legacy_files)} legacy figures")
    print(f"   Kept {len(all_files) - len(legacy_files)} bilingual figures")
    print()


if __name__ == "__main__":
    clean_legacy_figures()

#!/usr/bin/env python3
"""
Internationalization (i18n) module for bilingual figures (ES/EN).

Provides:
- Translation dictionaries for common figure text
- Helper functions for saving figures with language suffixes
- Consistent naming conventions
"""

import matplotlib.pyplot as plt
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from figure_export import save_figure_variants


# Translation dictionaries
TRANSLATIONS = {
    'es': {
        # Axis labels
        'decade': 'Década',
        'author': 'Autor',
        'genre': 'Género',
        'year': 'Año',
        'works': 'Obras',
        'tokens': 'Tokens',
        'mentions': 'Menciones',
        'rate': 'Tasa',
        
        # Common titles
        'emigrant_mentions': 'Menciones de emigrante',
        'emigrant_rate': 'Tasa de emigrante (por 1.000 tokens)',
        'works_distribution': 'Distribución de obras',
        'temporal_evolution': 'Evolución temporal',
        'heatmap_decade_author': 'Mapa de calor: Década × Autor',
        'heatmap_title': 'Tasa de menciones de emigrante por década y autor',
        
        # Labels
        'per_1k_tokens': 'por 1.000 tokens',
        'number_of_works': 'Número de obras',
        'number_of_mentions': 'Número de menciones',
        'top_authors': 'Principales autores',
        'top_markers': 'Principales marcadores',
        'by_author': 'Por autor',
        'by_decade': 'Por década',
        'by_genre': 'Por género',
        
        # Legends
        'emigrant_rate_legend': 'Tasa emigrante\n(menciones/1k tokens)',
        'production_timeline': 'Línea temporal de producción',
        'temporal_by_genre': 'Evolución temporal por género',
        
        # Notes
        'min_threshold': 'Umbral mínimo',
        'inclusion_criteria': 'Criterios de inclusión',
        'tokens_requirement': 'tokens mínimos',
        'mentions_requirement': 'menciones mínimas',
        
        # Profile analysis specific
        'marker': 'Marcador',
        'semantic_label': 'Etiqueta semántica',
        'marker_profile_by_author_title': 'Perfil de Marcadores de Emigrante por Autor (Top 5 autores, Top 15 marcadores)',
        'marker_profile_by_genre_title': 'Perfil de Marcadores de Emigrante por Género (Top 15 marcadores)',
        'mediation_density_title': 'Escenas de Mediación: Distribución de Densidad\n(Escenas con ≥3 menciones de emigrante)',
        'mediation_top_authors_title': 'Top 10 Autores por Escenas de Mediación',
        'number_of_scenes': 'Número de escenas',
        'emigrant_mentions_per_scene': 'Número de menciones de emigrante por escena',
        'number_of_mediation_scenes': 'Número de escenas de mediación',
        
        # Composition analysis specific
        'semantic_families': 'Familias semánticas',
        'composition': 'Composición',
        'profile_by_decade_title': 'Perfil del Emigrante por Década: Composición de Familias Semánticas',
        'profile_by_author_title': 'Perfil del Emigrante por Autor: Composición de Familias Semánticas',
        'rate_per_1k': 'Tasa por 1.000 tokens',
    },
    'en': {
        # Axis labels
        'decade': 'Decade',
        'author': 'Author',
        'genre': 'Genre',
        'year': 'Year',
        'works': 'Works',
        'tokens': 'Tokens',
        'mentions': 'Mentions',
        'rate': 'Rate',
        
        # Common titles
        'emigrant_mentions': 'Emigrant mentions',
        'emigrant_rate': 'Emigrant rate (per 1,000 tokens)',
        'works_distribution': 'Distribution of works',
        'temporal_evolution': 'Temporal evolution',
        'heatmap_decade_author': 'Heatmap: Decade × Author',
        'heatmap_title': 'Emigrant mention rate by decade and author',
        
        # Labels
        'per_1k_tokens': 'per 1,000 tokens',
        'number_of_works': 'Number of works',
        'number_of_mentions': 'Number of mentions',
        'top_authors': 'Top authors',
        'top_markers': 'Top markers',
        'by_author': 'By author',
        'by_decade': 'By decade',
        'by_genre': 'By genre',
        
        # Legends
        'emigrant_rate_legend': 'Emigrant rate\n(mentions/1k tokens)',
        'production_timeline': 'Production timeline',
        'temporal_by_genre': 'Temporal evolution by genre',
        
        # Notes
        'min_threshold': 'Minimum threshold',
        'inclusion_criteria': 'Inclusion criteria',
        'tokens_requirement': 'minimum tokens',
        'mentions_requirement': 'minimum mentions',
        
        # Profile analysis specific
        'marker': 'Marker',
        'semantic_label': 'Semantic label',
        'marker_profile_by_author_title': 'Emigrant Marker Profile by Author (Top 5 authors, Top 15 markers)',
        'marker_profile_by_genre_title': 'Emigrant Marker Profile by Genre (Top 15 markers)',
        'mediation_density_title': 'Mediation Scenes: Density Distribution\n(Scenes with ≥3 emigrant mentions)',
        'mediation_top_authors_title': 'Top 10 Authors by Mediation Scenes',
        'number_of_scenes': 'Number of scenes',
        'emigrant_mentions_per_scene': 'Number of emigrant mentions per scene',
        'number_of_mediation_scenes': 'Number of mediation scenes',
        
        # Composition analysis specific
        'semantic_families': 'Semantic families',
        'composition': 'Composition',
        'profile_by_decade_title': 'Emigrant Profile by Decade: Composition of Semantic Families',
        'profile_by_author_title': 'Emigrant Profile by Author: Composition of Semantic Families',
        'rate_per_1k': 'Rate per 1,000 tokens',
    }
}


def t(key: str, lang: str = 'es') -> str:
    """
    Get translation for a key.
    
    Args:
        key: Translation key
        lang: Language code ('es' or 'en')
    
    Returns:
        Translated string, or key itself if not found
    """
    if lang not in TRANSLATIONS:
        lang = 'es'
    return TRANSLATIONS[lang].get(key, key)


def format_decade_label(decade_value, lang: str = 'es') -> str:
    """
    Format decade label (keep 1890s format, don't translate the 's').
    
    Args:
        decade_value: Decade value (e.g., '1890s', 1890, '1890')
        lang: Language code (unused, kept for API consistency)
    
    Returns:
        Formatted decade string
    """
    decade_str = str(decade_value)
    if not decade_str.endswith('s'):
        # Assume it's a plain year like 1890, convert to "1890s"
        decade_str = f"{decade_str}s"
    return decade_str


def save_figure_bilingual(fig, basename: str, outdir: str = '04_outputs/figures/static', dpi: int = 300):
    """
    Save figure in both ES and EN with standard naming.
    
    This is a placeholder - actual implementation should be in the figure script itself
    which calls save_fig() twice with different language settings.
    
    Args:
        fig: matplotlib figure object
        basename: Base name without language suffix (e.g., 'fig_emigrant_by_author_top15')
        outdir: Output directory
        dpi: DPI for PNG
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    for lang in ['es', 'en']:
        for ext in ['png', 'pdf']:
            fpath = outdir / f"{basename}_{lang}.{ext}"
            if ext == 'png':
                fig.savefig(fpath, dpi=dpi, bbox_inches='tight')
            else:
                fig.savefig(fpath, bbox_inches='tight')
    
    print(f"  ✓ {basename}_{{es,en}}.{{png,pdf}}")


def save_fig(fig, basename: str, outdir: str, lang: str, dpi: int = 300):
    """
    Save a single figure with language suffix.
    
    Args:
        fig: matplotlib figure object
        basename: Base name without extension or language suffix
        outdir: Output directory path
        lang: Language code ('es' or 'en')
        dpi: DPI for PNG output
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    
    base_path = outdir / f"{basename}_{lang}"
    save_figure_variants(fig, base_path, dpi=dpi, save_png=True, save_pdf=True, save_jpeg=True, jpeg_quality=95)


def get_genre_labels(lang: str = 'es') -> dict:
    """
    Get genre labels in specified language.
    
    Args:
        lang: Language code
    
    Returns:
        Dictionary mapping genre codes to labels
    """
    if lang == 'es':
        return {
            'cuento_relato': 'Cuento/Relato',
            'novela': 'Novela',
            'poesia_poemario': 'Poesía/Poemario',
            'ensayo_cronica': 'Ensayo/Crónica',
            'teatro': 'Teatro',
            'unknown': 'Desconocido',
        }
    else:  # en
        return {
            'cuento_relato': 'Short Story',
            'novela': 'Novel',
            'poesia_poemario': 'Poetry',
            'ensayo_cronica': 'Essay/Chronicle',
            'teatro': 'Theatre',
            'unknown': 'Unknown',
        }


def validate_bilingual_outputs(basename: str, outdir: str = '04_outputs/figures/static') -> bool:
    """
    Validate that all 4 expected files exist for a figure.
    
    Args:
        basename: Base name without language suffix
        outdir: Output directory
    
    Returns:
        True if all 4 files exist, False otherwise
    """
    outdir = Path(outdir)
    expected = [
        outdir / f"{basename}_es.png",
        outdir / f"{basename}_es.pdf",
        outdir / f"{basename}_en.png",
        outdir / f"{basename}_en.pdf",
    ]
    
    missing = [f for f in expected if not f.exists()]
    if missing:
        print(f"❌ Missing files for {basename}:")
        for f in missing:
            print(f"   - {f.name}")
        return False
    
    return True

#!/usr/bin/env python3
"""
Enrich master table metadata using external corpus.csv.

Objetivo:
- Hacer matching robusto 80/80 entre obra_id (master) y doc_id (external)
- Rellenar year, decade, genre desde external corpus
- Generar METADATA_EXTERNAL_QA.md y metadata_match_report.csv
- Mantener trazabilidad con flags (year_source, genre_source)

Problema raíz:
- obra_id != doc_id por extensiones (.tei, .xml), sufijos (_001, _tei_v2), tildes, guiones
- Solución: normalizar ambas claves usando normalize_id() y normalize_id2()
"""

import pandas as pd
import unicodedata
import re
from pathlib import Path
from typing import Tuple, Dict, List
import argparse
from datetime import datetime


def normalize_id(s: str) -> str:
    """
    Normalize ID: remove extensions, normalize unicode, lowercase, etc.
    
    Steps:
    1. Remove extensions (.tei, .xml)
    2. Unicode NFKD normalization + remove diacritics
    3. Lowercase
    4. Replace non-alphanumeric with "_"
    5. Collapse "__" -> "_"
    6. Strip "_" from edges
    """
    if not isinstance(s, str):
        return ""
    
    # Step 1: Remove extensions
    s = re.sub(r'\.(tei|xml|xml_v2|xml_v1)$', '', s, flags=re.IGNORECASE)
    
    # Step 2: Unicode normalization (NFKD) + remove diacritics
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    
    # Step 3: Lowercase
    s = s.lower()
    
    # Step 4: Replace non-alphanumeric with "_"
    s = re.sub(r'[^a-z0-9]+', '_', s)
    
    # Step 5: Collapse multiple underscores
    s = re.sub(r'_+', '_', s)
    
    # Step 6: Strip edges
    s = s.strip('_')
    
    return s


def normalize_id2(s: str) -> str:
    """
    Normalize ID with suffix stripping.
    
    Steps:
    1. Apply normalize_id()
    2. Remove known suffixes: _001, _tei_v2, _tei_v1, _tei, _v2, _v1, _001
    """
    s = normalize_id(s)
    
    # Strip known suffixes (ordered by specificity)
    suffixes = [
        r'_tei_v2$',
        r'_tei_v1$',
        r'_tei$',
        r'_001$',
        r'_v2$',
        r'_v1$',
    ]
    
    for suffix in suffixes:
        s = re.sub(suffix, '', s)
    
    # Clean again just in case
    s = s.rstrip('_')
    
    return s


def normalize_genre(genre_str: str) -> str:
    """Normalize genre values to controlled vocabulary."""
    if not isinstance(genre_str, str) or genre_str.lower() in ['nan', '', 'unknown', 'sin_clasificar']:
        return 'unknown'
    
    g = genre_str.strip().lower()
    
    # Map variants to canonical forms
    mappings = {
        'cuento': 'cuento_relato',
        'relato': 'cuento_relato',
        'novela': 'novela',
        'poesia': 'poesia_poemario',
        'poesía': 'poesia_poemario',
        'poemario': 'poesia_poemario',
        'teatro': 'teatro',
        'drama': 'teatro',
        'tragedia': 'teatro',
        'ensayo': 'ensayo_cronica',
        'crónica': 'ensayo_cronica',
        'cronica': 'ensayo_cronica',
        'articulo': 'ensayo_cronica',
        'articulo periodico': 'ensayo_cronica',
    }
    
    for key, canonical in mappings.items():
        if key in g:
            return canonical
    
    # If exact match not found, classify as unknown
    return 'unknown'


def compute_decade(year: int) -> str:
    """Compute decade from year."""
    if pd.isna(year):
        return 'unknown_year'
    try:
        y = int(year)
        decade = (y // 10) * 10
        return f"{decade}s"
    except (ValueError, TypeError):
        return 'unknown_year'


def enrich_metadata(
    master_path: str,
    external_path: str,
    output_master: str = None,
    output_report: str = None,
    output_qa: str = None,
) -> Tuple[pd.DataFrame, Dict, List[str]]:
    """
    Enrich master table with external corpus metadata.
    
    Args:
        master_path: path to corpus_master_table_v2tokens.csv
        external_path: path to corpus.csv
        output_master: path for enriched master (if None, overwrites original)
        output_report: path for metadata_match_report.csv
        output_qa: path for METADATA_EXTERNAL_QA.md
    
    Returns:
        (enriched_master_df, metrics_dict, unmatched_works_list)
    """
    
    # Load data
    master = pd.read_csv(master_path)
    external = pd.read_csv(external_path)
    
    print(f"[INFO] Master table: {master.shape[0]} works")
    print(f"[INFO] External corpus: {external.shape[0]} works")
    
    # Create normalized keys
    master['master_key'] = master['obra_id'].apply(normalize_id2)
    external['lookup_key'] = external['doc_id'].apply(normalize_id2)
    
    # Build lookup index
    lookup_dict = {}
    for idx, row in external.iterrows():
        key = row['lookup_key']
        if key not in lookup_dict:  # Keep first occurrence if duplicates
            lookup_dict[key] = row
    
    print(f"[INFO] Unique lookup keys in external: {len(lookup_dict)}")
    
    # Track matches and updates
    match_results = []
    unmatched_master = []
    
    # Merge and enrich
    for idx, mrow in master.iterrows():
        mkey = mrow['master_key']
        
        # Try to find match
        if mkey in lookup_dict:
            lrow = lookup_dict[mkey]
            matched = True
        else:
            matched = False
            unmatched_master.append(mrow['obra_id'])
        
        # Build match record
        match_record = {
            'obra_id': mrow['obra_id'],
            'master_key': mkey,
            'matched': matched,
            'year_before': mrow.get('year', ''),
            'decade_before': mrow.get('decade', ''),
            'genre_before': mrow.get('genre_norm', ''),
        }
        
        # Update metadata if matched
        if matched:
            # Year enrichment
            year_before = mrow.get('year')
            if pd.isna(year_before) or year_before == 'unknown_year':
                year_src = external
                year_val = lrow.get('year_first_pub')
                if pd.notna(year_val):
                    try:
                        master.at[idx, 'year'] = int(year_val)
                        year_source = 'external'
                    except (ValueError, TypeError):
                        year_source = 'unknown'
                else:
                    year_source = 'unknown'
            else:
                year_source = 'tei'
            
            # Decade enrichment
            decade_before = mrow.get('decade')
            if pd.isna(decade_before) or decade_before == 'unknown_year':
                if pd.notna(lrow.get('year_first_pub')):
                    try:
                        y = int(lrow.get('year_first_pub'))
                        master.at[idx, 'decade'] = compute_decade(y)
                        decade_source = 'external'
                    except (ValueError, TypeError):
                        decade_source = 'computed'
                else:
                    decade_source = 'unknown'
            else:
                decade_source = 'tei'
            
            # Genre enrichment
            genre_before = mrow.get('genre_norm', 'unknown')
            if pd.isna(genre_before) or genre_before == 'unknown':
                # Try genero_macro_normalizado first (better field), fall back to genre
                ext_genre = lrow.get('genero_macro_normalizado') or lrow.get('genre')
                if pd.notna(ext_genre):
                    # Only enrich if external has meaningful value (not sin_clasificar, not unknown)
                    if str(ext_genre).strip().lower() not in ['sin_clasificar', 'unknown', 'nan', '']:
                        normalized_genre = normalize_genre(str(ext_genre))
                        master.at[idx, 'genre_norm'] = normalized_genre
                        genre_source = 'external'
                    else:
                        # External also unknown, keep master unknown
                        genre_source = 'unknown'
                else:
                    genre_source = 'unknown'
            else:
                genre_source = 'tei'
            
            # Add source flags
            master.at[idx, 'year_source'] = year_source
            master.at[idx, 'genre_source'] = genre_source
            master.at[idx, 'decade_source'] = decade_source
            
            match_record.update({
                'year_after': master.at[idx, 'year'],
                'decade_after': master.at[idx, 'decade'],
                'genre_after': master.at[idx, 'genre_norm'],
                'year_source': year_source,
                'genre_source': genre_source,
                'decade_source': decade_source,
            })
        else:
            match_record.update({
                'year_after': '',
                'decade_after': '',
                'genre_after': '',
                'year_source': 'unknown',
                'genre_source': 'unknown',
                'decade_source': 'unknown',
            })
        
        match_results.append(match_record)
    
    # Validate matching
    matched_count = sum(1 for r in match_results if r['matched'])
    print(f"[INFO] Matched: {matched_count}/{len(master)}")
    
    if matched_count != len(master):
        print(f"[ERROR] Not all works matched! Unmatched: {len(unmatched_master)}")
        for work in unmatched_master[:10]:
            print(f"  - {work}")
        if len(unmatched_master) > 10:
            print(f"  ... and {len(unmatched_master) - 10} more")
        raise ValueError(f"Matching failed: {matched_count}/80 matched. Expected 80/80.")
    
    # Compute metrics
    metrics = compute_qa_metrics(master, match_results)
    
    # Save outputs
    if output_master is None:
        output_master = master_path
    
    master.to_csv(output_master, index=False)
    print(f"[OK] Enriched master saved to {output_master}")
    
    if output_report:
        report_df = pd.DataFrame(match_results)
        report_df.to_csv(output_report, index=False)
        print(f"[OK] Match report saved to {output_report}")
    
    if output_qa:
        generate_qa_markdown(output_qa, master, match_results, metrics)
        print(f"[OK] QA markdown saved to {output_qa}")
    
    return master, metrics, unmatched_master


def compute_qa_metrics(master: pd.DataFrame, match_results: List[Dict]) -> Dict:
    """Compute QA metrics."""
    total = len(master)
    
    # Year coverage
    unknown_year = (
        (master['year'].isna()).sum() + 
        (master['year'] == 'unknown_year').sum() +
        (master['year'] == '').sum()
    )
    year_known = total - unknown_year
    year_coverage = (year_known / total * 100) if total > 0 else 0
    
    # Genre coverage
    unknown_genre = (
        (master['genre_norm'].isna()).sum() + 
        (master['genre_norm'] == 'unknown').sum() +
        (master['genre_norm'] == '').sum()
    )
    genre_known = total - unknown_genre
    genre_coverage = (genre_known / total * 100) if total > 0 else 0
    
    # Decade coverage
    unknown_decade = (
        (master['decade'].isna()).sum() + 
        (master['decade'] == 'unknown_year').sum() +
        (master['decade'] == '').sum()
    )
    decade_known = total - unknown_decade
    decade_coverage = (decade_known / total * 100) if total > 0 else 0
    
    # Match count
    matched = sum(1 for r in match_results if r['matched'])
    
    metrics = {
        'total_works': total,
        'matched_works': matched,
        'match_rate': matched / total * 100,
        'unknown_year': unknown_year,
        'year_coverage_pct': year_coverage,
        'unknown_genre': unknown_genre,
        'genre_coverage_pct': genre_coverage,
        'unknown_decade': unknown_decade,
        'decade_coverage_pct': decade_coverage,
    }
    
    return metrics


def generate_qa_markdown(
    output_path: str,
    master: pd.DataFrame,
    match_results: List[Dict],
    metrics: Dict,
):
    """Generate METADATA_EXTERNAL_QA.md."""
    
    lines = []
    lines.append("# METADATA_EXTERNAL_QA Report\n")
    lines.append(f"Generated: {datetime.now().isoformat()}\n")
    lines.append("## Executive Summary\n")
    lines.append(f"- Total works: {metrics['total_works']}")
    lines.append(f"- Matched with external corpus: {metrics['matched_works']} ({metrics['match_rate']:.1f}%)")
    lines.append(f"- Year coverage: {metrics['year_coverage_pct']:.1f}% ({metrics['unknown_year']} unknown)")
    lines.append(f"- Genre coverage: {metrics['genre_coverage_pct']:.1f}% ({metrics['unknown_genre']} unknown)")
    lines.append(f"- Decade coverage: {metrics['decade_coverage_pct']:.1f}% ({metrics['unknown_decade']} unknown)\n")
    
    # Validation result
    lines.append("## Validation Status\n")
    if metrics['matched_works'] == 80:
        lines.append("✅ Matching 80/80: PASS")
    else:
        lines.append(f"❌ Matching {metrics['matched_works']}/80: FAIL")
    
    if metrics['unknown_genre'] <= 2:
        lines.append(f"✅ Unknown genre ≤ 2: PASS ({metrics['unknown_genre']} unknown)")
    else:
        lines.append(f"❌ Unknown genre ≤ 2: FAIL ({metrics['unknown_genre']} unknown)")
    
    if metrics['unknown_year'] <= 2:
        lines.append(f"✅ Unknown year ≤ 2: PASS ({metrics['unknown_year']} unknown)")
    else:
        lines.append(f"❌ Unknown year ≤ 2: FAIL ({metrics['unknown_year']} unknown)\n")
    
    # Works with remaining unknowns
    if metrics['unknown_genre'] > 0 or metrics['unknown_year'] > 0:
        lines.append("## Works with Remaining Unknowns\n")
        
        unknown_works = master[
            ((master['genre_norm'] == 'unknown') | master['genre_norm'].isna()) |
            ((master['year'].isna()) | (master['year'] == 'unknown_year'))
        ]
        
        if len(unknown_works) > 0:
            for _, row in unknown_works.iterrows():
                lines.append(f"- {row['obra_id']}: year={row.get('year', 'NA')}, genre={row.get('genre_norm', 'NA')}")
    
    # Methodology
    lines.append("\n## Methodology\n")
    lines.append("""
- **ID Matching**: Normalized both obra_id (master) and doc_id (external) using:
  1. Remove extensions (.tei, .xml, etc.)
  2. Unicode NFKD normalization + diacritic removal
  3. Lowercase + non-alphanumeric → underscore
  4. Strip known suffixes (_tei_v2, _tei, _001, etc.)
- **Year Enrichment**: Filled NaN/unknown_year with year_first_pub from external corpus
- **Genre Enrichment**: Filled unknown with genre_macro_normalizado from external corpus  
- **Decade Enrichment**: Computed from year where available, or filled from external decade column
- **Trazability**: Flags added (year_source, genre_source, decade_source) to track enrichment provenance
- **Data Integrity**: TEI XML headers never modified; enrichment is overlay only (reversible)
""")
    
    content = '\n'.join(lines)
    Path(output_path).write_text(content)


def main():
    parser = argparse.ArgumentParser(
        description="Enrich corpus metadata from external CSV with robust 80/80 matching"
    )
    parser.add_argument(
        '--master',
        default='04_outputs/tables/corpus_master_table_v2tokens.csv',
        help='Path to master table'
    )
    parser.add_argument(
        '--external',
        default='01_data/external/corpus.csv',
        help='Path to external corpus CSV'
    )
    parser.add_argument(
        '--output-master',
        default=None,
        help='Output path for enriched master (default: overwrite input)'
    )
    parser.add_argument(
        '--output-report',
        default='04_outputs/tables/metadata_match_report.csv',
        help='Output path for match report CSV'
    )
    parser.add_argument(
        '--output-qa',
        default='00_docs/METADATA_EXTERNAL_QA.md',
        help='Output path for QA markdown'
    )
    
    args = parser.parse_args()
    
    try:
        master, metrics, unmatched = enrich_metadata(
            master_path=args.master,
            external_path=args.external,
            output_master=args.output_master if args.output_master else args.master,
            output_report=args.output_report,
            output_qa=args.output_qa,
        )
        
        print("\n[SUCCESS] Enrichment complete!")
        print(f"Match rate: {metrics['match_rate']:.1f}%")
        print(f"Year coverage: {metrics['year_coverage_pct']:.1f}%")
        print(f"Genre coverage: {metrics['genre_coverage_pct']:.1f}%")
        
        # Exit with error if validation fails
        if metrics['matched_works'] != 80 or metrics['unknown_genre'] > 2 or metrics['unknown_year'] > 2:
            print("\n[CRITICAL] QA validation failed!")
            print(f"Required: 80/80 match, unknown_genre ≤ 2, unknown_year ≤ 2")
            print(f"Got: {metrics['matched_works']}/80, {metrics['unknown_genre']} unknown_genre, {metrics['unknown_year']} unknown_year")
            exit(1)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        exit(1)


if __name__ == '__main__':
    main()

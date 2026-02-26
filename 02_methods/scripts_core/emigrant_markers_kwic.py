#!/usr/bin/env python3
"""
Extracción de marcadores migratorios KWIC para análisis de representación emigrante.

Input:
  - 01_data/text/units.csv (chapter/scene text)
  - 01_data/kwic_exports/cases_raw.csv (existing KWIC infrastructure)
  - 04_outputs/tables/works_metadata_from_tei.csv (author + year metadata)
  - 02_methods/patterns/emigrante_markers.yml (40 marcadores KWIC)

Output:
  - 04_outputs/tables/emigrant_mentions_by_work.csv (density per obra)
  - 03_analysis/cases/emigrante_kwic_cases.csv (individual KWIC instances)
  - 04_outputs/reports/emigrant_module_summary.md (human-readable report)

Strategy:
  1. Load markers from YAML
  2. For each work: extract units → tokenize → KWIC search
  3. Aggregate density per work (mentions / tokens * 1000)
  4. Store individual cases with context windows
  5. Report by author_normalized + year (if available)

Author: Etnografía Gallega
Version: 1.0.0
"""

import csv
import re
import sys
import yaml
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

WORK_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = WORK_ROOT / "01_data"
OUTPUTS_DIR = WORK_ROOT / "04_outputs"
ANALYSIS_DIR = WORK_ROOT / "03_analysis"
METHODS_DIR = WORK_ROOT / "02_methods"

UNITS_CSV = DATA_DIR / "text" / "units.csv"
WORKS_METADATA_CSV = OUTPUTS_DIR / "tables" / "works_metadata_from_tei.csv"
MARKERS_YAML = METHODS_DIR / "patterns" / "emigrante_markers.yml"

OUTPUT_MENTIONS_CSV = OUTPUTS_DIR / "tables" / "emigrant_mentions_by_work.csv"
OUTPUT_CASES_CSV = ANALYSIS_DIR / "cases" / "emigrante_kwic_cases.csv"
OUTPUT_SUMMARY_MD = OUTPUTS_DIR / "reports" / "emigrant_module_summary.md"

# Ensure output directories exist
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
(ANALYSIS_DIR / "cases").mkdir(parents=True, exist_ok=True)
(OUTPUTS_DIR / "reports").mkdir(parents=True, exist_ok=True)

# ============================================================================
# MARKER LOADER
# ============================================================================

def load_markers(yaml_path: Path) -> List[Dict]:
    """Load emigrant markers from YAML."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("markers", [])

# Increase CSV field limit for large text fields
csv.field_size_limit(10 ** 7)  # Increase to 10MB

# ============================================================================
# KWIC EXTRACTION
# ============================================================================

def extract_kwic(text: str, marker: Dict, window: int = 6) -> List[Tuple[str, int]]:
    """
    Extract KWIC cases for a marker in text.
    
    Returns:
      List of (kwic_context, position) tuples.
    """
    pattern = marker.get("marker", "")
    if not pattern:
        return []
    
    # Compile regex
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        print(f"ERROR: Invalid regex pattern: {pattern}", file=sys.stderr)
        return []
    
    # Tokenize text
    words = text.split()
    results = []
    
    # Build word-joined text for regex matching
    text_joined = " ".join(words)
    
    # Find matches
    for match in regex.finditer(text_joined):
        match_text = match.group(0)
        match_pos = match.start()
        
        # Find corresponding word position
        left_text = text_joined[:match_pos]
        word_idx = len(left_text.split())
        
        # Extract window
        start_idx = max(0, word_idx - window)
        end_idx = min(len(words), word_idx + window + 1)
        
        kwic = " ".join(words[start_idx:end_idx])
        results.append((kwic, word_idx))
    
    return results

# ============================================================================
# MAIN EXTRACTION
# ============================================================================

def main():
    """Main extraction pipeline."""
    
    # Load markers
    print(f"[emigrant_markers_kwic] Loading markers from {MARKERS_YAML}...")
    markers = load_markers(MARKERS_YAML)
    print(f"[emigrant_markers_kwic] Loaded {len(markers)} markers.")
    
    # Load units (text content) and map to obras
    print(f"[emigrant_markers_kwic] Loading units from {UNITS_CSV}...")
    units_by_work = defaultdict(list)  # obra_id -> list of (unidad_id, text) tuples
    with open(UNITS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            obra_id = row.get("obra_id", "")
            unidad_id = row["unidad_id"]
            text = row["text"]
            units_by_work[obra_id].append((unidad_id, text))
    
    print(f"[emigrant_markers_kwic] Loaded {sum(len(u) for u in units_by_work.values())} units across {len(units_by_work)} works.")
    
    # Load works metadata
    print(f"[emigrant_markers_kwic] Loading works metadata from {WORKS_METADATA_CSV}...")
    works_meta = {}
    with open(WORKS_METADATA_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            works_meta[row["obra_id"]] = row
    print(f"[emigrant_markers_kwic] Loaded metadata for {len(works_meta)} works.")
    
    # Extract KWIC cases per work
    works_mentions = defaultdict(lambda: {"mentions": 0, "cases": []})
    case_id_counter = 0
    
    print(f"[emigrant_markers_kwic] Extracting KWIC cases...")
    
    for obra_id in sorted(works_meta.keys()):
        # Get all units for this work
        if obra_id not in units_by_work:
            continue
        
        work_units = units_by_work[obra_id]
        
        # Count total tokens in work (from units)
        total_tokens = 0
        
        # Extract mentions per marker
        for unidad_id, text in work_units:
            total_tokens += len(text.split())
            
            for marker in markers:
                kwic_cases = extract_kwic(text, marker)
                
                for kwic, pos in kwic_cases:
                    case_id_counter += 1
                    case_id = f"emigrant_{case_id_counter}"
                    
                    works_mentions[obra_id]["mentions"] += 1
                    works_mentions[obra_id]["cases"].append({
                        "case_id": case_id,
                        "obra_id": obra_id,
                        "unit_id": unidad_id,
                        "marker": marker.get("marker", ""),
                        "marker_label": marker.get("context", ""),
                        "kwic": kwic,
                        "position_word": pos,
                    })
        
        # Compute density
        if total_tokens > 0:
            density = (works_mentions[obra_id]["mentions"] / total_tokens) * 1000
        else:
            density = 0.0
        
        works_mentions[obra_id]["total_tokens"] = total_tokens
        works_mentions[obra_id]["density_per_1k"] = density
    
    # ========================================================================
    # WRITE OUTPUT: emigrant_mentions_by_work.csv
    # ========================================================================
    
    print(f"[emigrant_markers_kwic] Writing {OUTPUT_MENTIONS_CSV}...")
    
    with open(OUTPUT_MENTIONS_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "obra_id",
                "author_normalized",
                "year",
                "n_mentions",
                "total_tokens",
                "density_per_1k_tokens"
            ]
        )
        writer.writeheader()
        
        for obra_id in sorted(works_mentions.keys()):
            meta = works_meta.get(obra_id, {})
            row = {
                "obra_id": obra_id,
                "author_normalized": meta.get("author_normalized", ""),
                "year": meta.get("year", ""),
                "n_mentions": works_mentions[obra_id]["mentions"],
                "total_tokens": works_mentions[obra_id]["total_tokens"],
                "density_per_1k_tokens": round(works_mentions[obra_id]["density_per_1k"], 2),
            }
            writer.writerow(row)
    
    print(f"[emigrant_markers_kwic]   ✓ {OUTPUT_MENTIONS_CSV}")
    
    # ========================================================================
    # WRITE OUTPUT: emigrante_kwic_cases.csv
    # ========================================================================
    
    print(f"[emigrant_markers_kwic] Writing {OUTPUT_CASES_CSV}...")
    
    all_cases = []
    for obra_id in works_mentions:
        meta = works_meta.get(obra_id, {})
        for case in works_mentions[obra_id]["cases"]:
            case["author_normalized"] = meta.get("author_normalized", "")
            case["year"] = meta.get("year", "")
            all_cases.append(case)
    
    with open(OUTPUT_CASES_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "case_id",
                "obra_id",
                "author_normalized",
                "year",
                "unit_id",
                "marker",
                "marker_label",
                "kwic",
                "position_word",
            ]
        )
        writer.writeheader()
        writer.writerows(all_cases)
    
    print(f"[emigrant_markers_kwic]   ✓ {OUTPUT_CASES_CSV} ({len(all_cases)} cases)")
    
    # ========================================================================
    # WRITE OUTPUT: emigrant_module_summary.md
    # ========================================================================
    
    print(f"[emigrant_markers_kwic] Writing {OUTPUT_SUMMARY_MD}...")
    
    # Sort works by density
    sorted_works = sorted(
        works_mentions.items(),
        key=lambda x: x[1]["density_per_1k"],
        reverse=True
    )
    
    with open(OUTPUT_SUMMARY_MD, "w", encoding="utf-8") as f:
        f.write("# Módulo de Representación Emigrante\n\n")
        f.write("**Extracción de 40 marcadores KWIC para análisis de figura del emigrante en narrativa gallega XIX-XX**\n\n")
        
        f.write("## Resumen Estadístico\n\n")
        f.write(f"- **Total de obras analizadas**: {len(works_mentions)}\n")
        f.write(f"- **Total de menciones emigrantes**: {sum(w['mentions'] for w in works_mentions.values())}\n")
        f.write(f"- **Total de tokens**: {sum(w['total_tokens'] for w in works_mentions.values())}\n")
        f.write(f"- **Densidad promedio**: {(sum(w['mentions'] for w in works_mentions.values()) / sum(w['total_tokens'] for w in works_mentions.values()) * 1000) if sum(w['total_tokens'] for w in works_mentions.values()) > 0 else 0:.2f} por 1k tokens\n\n")
        
        f.write("## Top 25 Obras por Densidad Emigrante\n\n")
        f.write("| Obra | Autor | Año | Menciones | Densidad (per 1k) |\n")
        f.write("|------|-------|-----|-----------|-------------------|\n")
        
        for obra_id, data in sorted_works[:25]:
            meta = works_meta.get(obra_id, {})
            author = meta.get("author_normalized", "? ")
            year = meta.get("year", "?")
            f.write(f"| {obra_id} | {author} | {year} | {data['mentions']} | {data['density_per_1k']:.2f} |\n")
        
        f.write("\n## Obras sin Menciones Emigrantes (10%)\n\n")
        no_mention_works = [w for w, d in sorted_works if d["mentions"] == 0]
        f.write(f"**Total**: {len(no_mention_works)} obras (esenciales para reading pack control negativo)\n\n")
    
    print(f"[emigrant_markers_kwic]   ✓ {OUTPUT_SUMMARY_MD}")
    
    print(f"\n[emigrant_markers_kwic] ✅ COMPLETADO")
    print(f"[emigrant_markers_kwic]   - emigrant_mentions_by_work.csv: {len(works_mentions)} obras")
    print(f"[emigrant_markers_kwic]   - emigrante_kwic_cases.csv: {len(all_cases)} casos KWIC")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[emigrant_markers_kwic] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

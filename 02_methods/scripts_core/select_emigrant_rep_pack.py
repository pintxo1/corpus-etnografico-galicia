#!/usr/bin/env python3
"""
Selección de reading pack para representación del emigrante.

Input:
  - 04_outputs/tables/emigrant_mentions_by_work.csv (density per work)
  - 03_analysis/cases/emigrante_kwic_cases.csv (individual cases)
  - 04_outputs/tables/works_metadata_from_tei.csv (author + year metadata)

Output:
  - 03_analysis/reading_pack/emigrante_representation_pack.csv
  
Strategy:
  1. Mínimo 1 caso per obra (si existen menciones)
  2. Cuota per década (mantener balance temporal)
  3. 10% de control negativo (obras sin menciones)
  4. Sort by decade + author para trazabilidad
  
Target: ~180 casos (~2.25 casos/obra en promedio)

Author: Etnografía Gallega
Version: 1.0.0
"""

import csv
import sys
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

WORK_ROOT = Path(__file__).parent.parent.parent
OUTPUTS_DIR = WORK_ROOT / "04_outputs"
ANALYSIS_DIR = WORK_ROOT / "03_analysis"

MENTIONS_CSV = OUTPUTS_DIR / "tables" / "emigrant_mentions_by_work.csv"
CASES_CSV = ANALYSIS_DIR / "cases" / "emigrante_kwic_cases.csv"
WORKS_METADATA_CSV = OUTPUTS_DIR / "tables" / "works_metadata_from_tei.csv"

OUTPUT_PACK_CSV = ANALYSIS_DIR / "reading_pack" / "emigrante_representation_pack.csv"

# Ensure output directory exists
OUTPUT_PACK_CSV.parent.mkdir(parents=True, exist_ok=True)

TARGET_PACK_SIZE = 180

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_decade(year: Optional[str]) -> Optional[int]:
    """Extract decade from year string."""
    if not year or year.strip() == "":
        return None
    try:
        year_int = int(year)
        return (year_int // 10) * 10
    except:
        return None

def load_cases() -> Dict[str, List[Dict]]:
    """Load all cases, grouped by obra_id."""
    cases_by_work = defaultdict(list)
    with open(CASES_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases_by_work[row["obra_id"]].append(row)
    return cases_by_work

def load_works_metadata() -> Dict[str, Dict]:
    """Load works metadata."""
    metadata = {}
    with open(WORKS_METADATA_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            metadata[row["obra_id"]] = row
    return metadata

def load_mentions() -> Dict[str, Dict]:
    """Load mention densities per work."""
    mentions = {}
    with open(MENTIONS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mentions[row["obra_id"]] = {
                "n_mentions": int(row["n_mentions"]),
                "density": float(row["density_per_1k_tokens"]),
            }
    return mentions

# ============================================================================
# SELECTION LOGIC
# ============================================================================

def select_reading_pack(
    cases_by_work: Dict[str, List[Dict]],
    works_metadata: Dict[str, Dict],
    mentions: Dict[str, Dict],
    target_size: int = 180,
) -> List[Dict]:
    """
    Select reading pack according to strategy:
    1. Min 1 case per work with mentions
    2. Distribute across decades
    3. Add 10% negative controls (works without mentions)
    """
    
    selected_cases = []
    works_with_mentions = set(mentions.keys())
    works_without_mentions = set(works_metadata.keys()) - works_with_mentions
    
    # ========================================================================
    # PHASE 1: 1 CASE PER OBRA (MANDATORY)
    # ========================================================================
    
    for obra_id in sorted(works_with_mentions):
        if obra_id not in cases_by_work:
            continue
        
        # Select highest-confidence case (first in list)
        case = cases_by_work[obra_id][0]
        case["selection_reason"] = "mandatory_one_per_work"
        selected_cases.append(case)
    
    print(f"[select_emigrant_rep_pack] Phase 1: {len(selected_cases)} cases (mandatory 1/work)")
    
    # ========================================================================
    # PHASE 2: DECADE-BALANCED SUPPLEMENTARY CASES
    # ========================================================================
    
    remaining_quota = target_size - len(selected_cases)
    print(f"[select_emigrant_rep_pack] Phase 2: {remaining_quota} cases remaining for supplementary selection")
    
    if remaining_quota > 0:
        # Group remaining cases by decade
        cases_by_decade = defaultdict(list)
        
        for obra_id in sorted(works_with_mentions):
            if obra_id not in cases_by_work:
                continue
            
            # Already selected 1st case in Phase 1
            remaining_cases = cases_by_work[obra_id][1:]
            
            if not remaining_cases:
                continue
            
            # Get decade from metadata
            meta = works_metadata.get(obra_id, {})
            decade = get_decade(meta.get("year", ""))
            
            cases_by_decade[decade].extend(remaining_cases)
        
        # Distribute remaining_quota across decades proportionally
        decades_sorted = sorted(cases_by_decade.keys())
        
        for decade in decades_sorted:
            if remaining_quota <= 0:
                break
            
            # Get quota for this decade (proportional)
            decade_cases = cases_by_decade[decade]
            quota = min(len(decade_cases), max(1, remaining_quota // len(decades_sorted)))
            
            # Randomly sample from decade
            selected = random.sample(decade_cases, quota)
            for case in selected:
                case["selection_reason"] = f"decade_balance_{decade}s"
                selected_cases.append(case)
            
            remaining_quota -= quota
        
        # Add any remaining quota to most recent decade
        if remaining_quota > 0:
            last_decade_cases = cases_by_decade.get(decades_sorted[-1], [])
            remaining_available = [c for c in last_decade_cases if c not in selected_cases]
            extra = min(len(remaining_available), remaining_quota)
            selected = random.sample(remaining_available, extra)
            for case in selected:
                case["selection_reason"] = "quota_overflow"
                selected_cases.append(case)
    
    print(f"[select_emigrant_rep_pack] Phase 2: {len(selected_cases)} cases total")
    
    # ========================================================================
    # PHASE 3: NEGATIVE CONTROLS (10% of pack size)
    # ========================================================================
    
    n_controls = max(1, target_size // 10)
    
    if works_without_mentions:
        selected_controls = random.sample(
            sorted(works_without_mentions),
            min(len(works_without_mentions), n_controls)
        )
        
        for obra_id in selected_controls:
            meta = works_metadata.get(obra_id, {})
            control_case = {
                "case_id": f"emigrant_control_{obra_id}",
                "obra_id": obra_id,
                "author_normalized": meta.get("author_normalized", ""),
                "year": meta.get("year", ""),
                "unit_id": "",
                "marker": "",
                "marker_label": "NEGATIVE_CONTROL",
                "kwic": "[NO EMIGRANT MARKERS FOUND]",
                "position_word": 0,
                "selection_reason": "negative_control",
            }
            selected_cases.append(control_case)
    
    print(f"[select_emigrant_rep_pack] Phase 3: {len([c for c in selected_cases if c['selection_reason'] == 'negative_control'])} negative controls")
    
    return selected_cases

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main selection pipeline."""
    
    print(f"[select_emigrant_rep_pack] Loading data...")
    
    # Load all data
    cases_by_work = load_cases()
    works_metadata = load_works_metadata()
    mentions = load_mentions()
    
    print(f"[select_emigrant_rep_pack] Cases: {sum(len(c) for c in cases_by_work.values())}")
    print(f"[select_emigrant_rep_pack] Works: {len(works_metadata)}")
    print(f"[select_emigrant_rep_pack] Works with mentions: {len(mentions)}")
    
    # Select reading pack
    selected_cases = select_reading_pack(
        cases_by_work,
        works_metadata,
        mentions,
        target_size=TARGET_PACK_SIZE,
    )
    
    # ========================================================================
    # WRITE OUTPUT
    # ========================================================================
    
    print(f"[select_emigrant_rep_pack] Writing {OUTPUT_PACK_CSV}...")
    
    # Sort by decade (asc) + author (asc) for trazabilidad
    def sort_key(case: Dict) -> Tuple:
        decade = get_decade(case.get("year", ""))
        author = case.get("author_normalized", "")
        return (decade if decade else 9999, author)
    
    selected_cases.sort(key=sort_key)
    
    with open(OUTPUT_PACK_CSV, "w", encoding="utf-8", newline="") as f:
        # Write all fields
        fieldnames = list(selected_cases[0].keys()) if selected_cases else []
        writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(selected_cases)
    
    print(f"[select_emigrant_rep_pack] ✅ COMPLETADO")
    print(f"[select_emigrant_rep_pack]   - Pack size: {len(selected_cases)} casos")
    print(f"[select_emigrant_rep_pack]   - Target: {TARGET_PACK_SIZE}")
    print(f"[select_emigrant_rep_pack]   - Output: {OUTPUT_PACK_CSV}")
    
    # Print summary statistics
    by_reason = defaultdict(int)
    for case in selected_cases:
        by_reason[case.get("selection_reason", "")] += 1
    
    print(f"\n[select_emigrant_rep_pack] Selection breakdown:")
    for reason, count in sorted(by_reason.items()):
        print(f"  - {reason}: {count}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[select_emigrant_rep_pack] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
qa_deduplicate_work_tokens.py
Quick fix: Remove duplicate obra_id rows from work_tokens_full.csv
(Keep first occurrence, discard identical duplicates)
"""
import pandas as pd
from pathlib import Path

BASE = Path("/Users/Pintxo/corpus-etnografico-galicia")
TABLES = BASE / "04_outputs/tables"

print("\n" + "="*80)
print("[DEDUP] Deduplicating work_tokens_full.csv")
print("="*80)

# Load
print("\n[1/3] Cargando work_tokens_full.csv...")
fulltext = pd.read_csv(TABLES / "work_tokens_full.csv")
original_len = len(fulltext)
print(f"  ✓ {original_len} filas")

# Count duplicates
dupes = fulltext[fulltext.duplicated(subset=['obra_id'], keep=False)]
print(f"\n[2/3] Analizando duplicados...")
print(f"  Filas duplicadas encontradas: {len(dupes)}")
if len(dupes) > 0:
    dupe_ids = dupes['obra_id'].unique()
    for obra_id in sorted(dupe_ids):
        count = len(fulltext[fulltext['obra_id'] == obra_id])
        tokens = fulltext[fulltext['obra_id'] == obra_id]['tokens_total_full'].iloc[0]
        print(f"    - {obra_id}: {count}x ({tokens} tokens)")

# Deduplicate
print(f"\n[3/3] Deduplicando (keep='first')...")
fulltext_dedup = fulltext.drop_duplicates(subset=['obra_id'], keep='first').reset_index(drop=True)
final_len = len(fulltext_dedup)

# Save
fulltext_dedup.to_csv(TABLES / "work_tokens_full.csv", index=False)

print(f"\n" + "="*80)
print("RESULTADO DEDUP")
print("="*80)
print(f"\nFilas antes: {original_len}")
print(f"Filas después: {final_len}")
print(f"Filas removidas: {original_len - final_len}")
print(f"IDs únicos: {fulltext_dedup['obra_id'].nunique()}")
print(f"\n✅ work_tokens_full.csv actualizado (deduplicado)")
print("="*80 + "\n")

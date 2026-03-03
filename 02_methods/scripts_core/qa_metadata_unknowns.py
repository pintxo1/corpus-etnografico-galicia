#!/usr/bin/env python3
"""
qa_metadata_unknowns.py
Valida umbrales de metadata en tabla maestra meta-fixed.

Requisitos:
- year conocido >= 95%
- genre conocido >= 95%
- unknown_year <= 4
- unknown_genre <= 2
"""

import argparse
import sys
from pathlib import Path
import pandas as pd

DEFAULT_MASTER = Path(__file__).parent.parent.parent / "04_outputs" / "tables" / "corpus_master_table_v2tokens_meta.csv"


def main():
    parser = argparse.ArgumentParser(description="QA de metadata desconocida")
    parser.add_argument("--master", default=str(DEFAULT_MASTER), help="Tabla maestra meta-fixed")
    parser.add_argument("--min-year-pct", type=float, default=95.0, help="Minimo porcentaje de year conocido")
    parser.add_argument("--min-genre-pct", type=float, default=95.0, help="Minimo porcentaje de genre conocido")
    parser.add_argument("--max-unknown-year", type=int, default=4, help="Maximo unknown_year")
    parser.add_argument("--max-unknown-genre", type=int, default=2, help="Maximo unknown_genre")
    args = parser.parse_args()

    master_path = Path(args.master)
    if not master_path.exists():
        print(f"❌ ERROR: master no encontrado: {master_path}")
        sys.exit(1)

    df = pd.read_csv(master_path)
    total = len(df)

    unknown_year = df['year'].isna().sum()
    unknown_genre = (df['genre_norm'].isna() | (df['genre_norm'].astype(str) == 'unknown')).sum()

    year_known_pct = 100.0 * (total - unknown_year) / total
    genre_known_pct = 100.0 * (total - unknown_genre) / total

    print("\n" + "=" * 70)
    print("QA_METADATA_UNKNOWNS")
    print("=" * 70 + "\n")

    print(f"Total works: {total}")
    print(f"unknown_year count: {unknown_year}")
    print(f"unknown_genre count: {unknown_genre}")
    print(f"year known pct: {year_known_pct:.1f}%")
    print(f"genre known pct: {genre_known_pct:.1f}%")

    missing = df[(df['year'].isna()) | (df['genre_norm'].astype(str) == 'unknown')]
    if not missing.empty:
        print("\nTop 10 works with missing metadata:")
        for _, row in missing.head(10).iterrows():
            print(f"- {row['obra_id']}: year={row['year']} genre={row['genre_norm']}")

    failed = False
    if year_known_pct < args.min_year_pct:
        print(f"\n❌ FAIL: year known pct {year_known_pct:.1f}% < {args.min_year_pct}%")
        failed = True
    if genre_known_pct < args.min_genre_pct:
        print(f"\n❌ FAIL: genre known pct {genre_known_pct:.1f}% < {args.min_genre_pct}%")
        failed = True
    if unknown_year > args.max_unknown_year:
        print(f"\n❌ FAIL: unknown_year {unknown_year} > {args.max_unknown_year}")
        failed = True
    if unknown_genre > args.max_unknown_genre:
        print(f"\n❌ FAIL: unknown_genre {unknown_genre} > {args.max_unknown_genre}")
        failed = True

    if failed:
        print("\n❌ QA FAILED: metadata thresholds not met")
        sys.exit(1)

    print("\n✅ QA PASSED: metadata thresholds met")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Generate EVIDENCE_PACK_EMIGRANTE.md from summary tables.
Supports v2tokens tables via explicit paths.
"""
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd

BASE_DIR = Path(__file__).parent.parent.parent
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"
REPORTS_DIR = BASE_DIR / "04_outputs" / "reports"


def load_table(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing table: {path}")
    return pd.read_csv(path)


def main():
    parser = argparse.ArgumentParser(description="Generate evidence pack report")
    parser.add_argument(
        "--master-table",
        default=str(TABLES_DIR / "corpus_master_table_v2tokens.csv"),
        help="Path to corpus master table"
    )
    parser.add_argument(
        "--by-author",
        default=str(TABLES_DIR / "emigrant_by_author_v2tokens.csv"),
        help="Path to emigrant_by_author table"
    )
    parser.add_argument(
        "--by-decade",
        default=str(TABLES_DIR / "emigrant_by_decade_v2tokens.csv"),
        help="Path to emigrant_by_decade table"
    )
    parser.add_argument(
        "--by-format",
        default=str(TABLES_DIR / "emigrant_by_format_v2tokens.csv"),
        help="Path to emigrant_by_format table"
    )
    parser.add_argument(
        "--output",
        default=str(REPORTS_DIR / "EVIDENCE_PACK_EMIGRANTE.md"),
        help="Output report path"
    )
    args = parser.parse_args()

    master = load_table(Path(args.master_table))
    by_author = load_table(Path(args.by_author))
    by_decade = load_table(Path(args.by_decade))
    by_format = load_table(Path(args.by_format))

    total_works = len(master)
    total_tokens = int(master["tokens_total"].sum())
    total_mentions = int(master["n_emigrant_mentions"].sum())

    top_authors = by_author.head(5)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output)

    lines = []
    lines.append("# EVIDENCE_PACK_EMIGRANTE")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("**Denominators:** tokens_full (TEI fulltext, v2tokens)")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 1. Corpus summary")
    lines.append("")
    lines.append(f"- Works: {total_works}")
    lines.append(f"- Tokens (fulltext): {total_tokens:,}")
    lines.append(f"- Emigrant mentions: {total_mentions:,}")
    lines.append("")

    lines.append("## 2. Emigrant by author (top 5)")
    lines.append("")
    lines.append("| Author | Works | Tokens | Mentions | Rate/1k |")
    lines.append("|---|---:|---:|---:|---:|")
    for _, row in top_authors.iterrows():
        lines.append(
            f"| {row['author_normalized']} | {int(row['n_obras'])} | {int(row['tokens_total']):,} | "
            f"{int(row['n_emigrant_mentions']):,} | {row['emigrant_rate_per_1k_tokens']:.2f} |"
        )
    lines.append("")

    lines.append("## 3. Emigrant by decade")
    lines.append("")
    lines.append("| Decade | Works | Tokens | Mentions | Rate/1k |")
    lines.append("|---|---:|---:|---:|---:|")
    for _, row in by_decade.iterrows():
        lines.append(
            f"| {row['decade']} | {int(row['n_obras'])} | {int(row['tokens_total']):,} | "
            f"{int(row['n_emigrant_mentions']):,} | {row['emigrant_rate_per_1k_tokens']:.2f} |"
        )
    lines.append("")

    lines.append("## 4. Emigrant by format")
    lines.append("")
    lines.append("| Format | Works | Tokens | Mentions | Rate/1k |")
    lines.append("|---|---:|---:|---:|---:|")
    for _, row in by_format.iterrows():
        lines.append(
            f"| {row['format']} | {int(row['n_obras'])} | {int(row['tokens_total']):,} | "
            f"{int(row['n_emigrant_mentions']):,} | {row['emigrant_rate_per_1k_tokens']:.2f} |"
        )
    lines.append("")

    lines.append("## 5. Notes")
    lines.append("")
    lines.append("- Rates are normalized per 1,000 fulltext tokens (TEI body extraction).")
    lines.append("- This report is consistent with v2tokens denominators.")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Report saved: {output_path}")


if __name__ == "__main__":
    main()

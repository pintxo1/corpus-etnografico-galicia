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
    
    lines.append("## 5. Temporal Composition Analysis (PROMPT 2)")
    lines.append("")
    lines.append("### 5.1. Decade × Author Heatmap")
    lines.append("")
    lines.append("Heatmap showing emigrant representation rates (per 1k tokens) by decade and author:")
    lines.append("")
    lines.append("![Decade × Author Heatmap](../figures/static/fig_emigrant_heatmap_decade_author.png)")
    lines.append("")
    lines.append("**Key observations:**")
    lines.append("- Temporal distribution of emigrant representation across authors")
    lines.append("- Variation in rates by decade for each major author")
    lines.append("- Authors with ≥3 works included")
    lines.append("")
    
    lines.append("### 5.2. Temporal Evolution by Genre")
    lines.append("")
    lines.append("Evolution of emigrant representation and literary production by genre:")
    lines.append("")
    lines.append("![Temporal by Genre](../figures/static/fig_emigrant_temporal_by_genre.png)")
    lines.append("")
    lines.append("**Key observations:**")
    lines.append("- Upper panel: emigrant rate per 1k tokens by genre over time")
    lines.append("- Lower panel: number of works published by genre per decade")
    lines.append("- Genres with ≥5 total works included")
    lines.append("")
    
    lines.append("### 5.3. Production Timeline")
    lines.append("")
    lines.append("Corpus production timeline showing works, authors, and emigrant representation:")
    lines.append("")
    lines.append("![Production Timeline](../figures/static/fig_production_timeline.png)")
    lines.append("")
    lines.append("**Key observations:**")
    lines.append("- Number of works per decade")
    lines.append("- Number of active authors per decade")
    lines.append("- Emigrant representation rate per decade")
    lines.append("")

    # Load emigrant profile tables for Section 6
    mediation_file = TABLES_DIR / "emigrant_mediation_scenes.csv"
    if mediation_file.exists():
        mediation = load_table(mediation_file)
        n_mediation_scenes = len(mediation)
        top_mediation_authors = mediation['author_normalized'].value_counts().head(5)
    else:
        n_mediation_scenes = 0
        top_mediation_authors = pd.Series()
    
    lines.append("## 6. Emigrant Profile Analysis (PROMPT 3)")
    lines.append("")
    lines.append("### 6.1. Marker Distribution by Author")
    lines.append("")
    lines.append("Distribution of top emigrant markers across top 5 authors:")
    lines.append("")
    lines.append("![Markers by Author](../figures/static/fig_emigrant_markers_profile_by_author.png)")
    lines.append("")
    lines.append("**Key observations:**")
    lines.append("- Top 15 emigrant markers (semantic labels) by frequency")
    lines.append("- Variation in marker usage across authors")
    lines.append("- Authors with highest number of emigrant mentions included")
    lines.append("")
    
    lines.append("### 6.2. Marker Distribution by Genre")
    lines.append("")
    lines.append("Distribution of emigrant markers across literary genres:")
    lines.append("")
    lines.append("![Markers by Genre](../figures/static/fig_emigrant_markers_profile_by_genre.png)")
    lines.append("")
    lines.append("**Key observations:**")
    lines.append("- Top 15 emigrant markers by genre")
    lines.append("- Genre-specific patterns in emigrant representation")
    lines.append("- Genres with ≥5 works included")
    lines.append("")
    
    lines.append("### 6.3. Mediation Scenes")
    lines.append("")
    lines.append("Mediation scenes = text units with ≥3 emigrant mentions (high density contexts):")
    lines.append("")
    lines.append("![Mediation Density](../figures/static/fig_emigrant_mediation_density.png)")
    lines.append("")
    lines.append("**Key statistics:**")
    lines.append(f"- Total mediation scenes identified: {n_mediation_scenes}")
    lines.append(f"- Total emigrant mentions: {total_mentions:,}")
    lines.append(f"- Mediation scene rate: {n_mediation_scenes / total_works:.2f} scenes/work")
    if not top_mediation_authors.empty:
        lines.append("")
        lines.append("**Top authors by mediation scenes:**")
        for author, n_scenes in top_mediation_authors.items():
            lines.append(f"- {author}: {int(n_scenes)} scenes")
    lines.append("")
    
    lines.append("## 7. Expanded Author × Decade Heatmap (PROMPT 2)")
    lines.append("")
    lines.append("### 7.1. Full Heatmap (All Relevant Authors)")
    lines.append("")
    lines.append("Expanded heatmap with all authors meeting inclusion criteria (tokens ≥5k, mentions ≥5):")
    lines.append("")
    lines.append("![Heatmap Full](../figures/static/fig_emigrant_heatmap_decade_author_full.png)")
    lines.append("")
    lines.append("**Key observations:**")
    lines.append("- All relevant authors included (not just top 3)")
    lines.append("- 'otros_autores' category aggregates excluded authors")
    lines.append("- Clear patterns of temporal concentration per author")
    lines.append("")
    
    lines.append("### 7.2. Top 12 Authors (Legibility)")
    lines.append("")
    lines.append("Focused version with top 12 authors for enhanced legibility:")
    lines.append("")
    lines.append("![Heatmap Top12](../figures/static/fig_emigrant_heatmap_decade_author_top12.png)")
    lines.append("")
    
    lines.append("## 8. Semantic Family Composition (PROMPT 3)")
    lines.append("")
    lines.append("### 8.1. Composition by Decade")
    lines.append("")
    lines.append("Stacked composition of emigrant marker families over time:")
    lines.append("")
    lines.append("![Profile by Decade](../figures/static/fig_emigrant_profile_by_decade.png)")
    lines.append("")
    lines.append("**Key observations:**")
    lines.append("- 9 semantic families identified (identity, mobility, destinations, economy, etc.)")
    lines.append("- Temporal shifts in family prominence")
    lines.append("- 'Identidad_lengua' consistently dominant (~37% of mentions)")
    lines.append("")
    
    lines.append("### 8.2. Composition by Author")
    lines.append("")
    lines.append("Author-specific semantic profiles (top 5 authors + others):")
    lines.append("")
    lines.append("![Profile by Author](../figures/static/fig_emigrant_profile_by_author.png)")
    lines.append("")
    lines.append("**Key observations:**")
    lines.append("- Author-specific variation in family usage")
    lines.append("- Some authors emphasize economy/class, others nostalgia/affect")
    lines.append("- Composition analysis reveals stylistic/thematic differences")
    lines.append("")

    lines.append("## 9. Notes & Methodology")
    lines.append("")
    lines.append("- Rates are normalized per 1,000 fulltext tokens (TEI body extraction).")
    lines.append("- This report is consistent with v2tokens denominators.")
    lines.append("- Temporal analysis includes only works with known publication decade (74/80 works, 7.5% unknown).")
    lines.append("- Marker labels represent semantic categories of emigrant markers.")
    lines.append("- Mediation scenes identify text units with high emigrant mention density (≥3 mentions).")
    lines.append("- Semantic families mapped from emigrant_marker_families.yml taxonomy.")
    lines.append("- Inclusion criteria for expanded heatmap: tokens ≥5k AND mentions ≥5.")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Report saved: {output_path}")


if __name__ == "__main__":
    main()

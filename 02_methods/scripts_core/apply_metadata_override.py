#!/usr/bin/env python3
"""
apply_metadata_override.py
Aplica metadata externa (override) para corregir year/decade/genre/format.

Input:
- 04_outputs/tables/corpus_master_table_v2tokens.csv
- CSV override (por defecto: 00_docs/metadata_override_prev_project.csv o
  /Users/Pintxo/corpus-literario/metadata/corpus.csv si existe)

Output:
- 04_outputs/tables/corpus_master_table_v2tokens_meta.csv
- 00_docs/METADATA_OVERRIDE_QA.md
"""

import argparse
import sys
import unicodedata
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).parent.parent.parent
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"
DOCS_DIR = BASE_DIR / "00_docs"

DEFAULT_OVERRIDE_LOCAL = DOCS_DIR / "metadata_override_prev_project.csv"
DEFAULT_OVERRIDE_EXTERNAL = Path("/Users/Pintxo/corpus-literario/metadata/corpus.csv")

GENRE_MAP = {
    "cuento": "cuento_relato",
    "relato": "cuento_relato",
    "cuento_relato": "cuento_relato",
    "novela": "novela",
    "poesia": "poesia_poemario",
    "poema": "poesia_poemario",
    "poemario": "poesia_poemario",
    "poesia_poemario": "poesia_poemario",
    "teatro": "teatro",
    "ensayo": "ensayo_cronica",
    "cronica": "ensayo_cronica",
    "cronica": "ensayo_cronica",
    "ensayo_cronica": "ensayo_cronica",
    "articulo": "ensayo_cronica",
    "sin_clasificar": "unknown",
    "otro": "otro",
    "unknown": "unknown",
}

FORMAT_MAP = {
    "cuento_relato": "cuento",
    "novela": "novela",
    "poesia_poemario": "poesia",
    "teatro": "teatro",
    "ensayo_cronica": "ensayo_cronica",
    "otro": "otro",
    "unknown": "unknown",
}


def normalize_text(text: str) -> str:
    if text is None:
        return ""
    text = str(text).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.replace("-", "_").replace(" ", "_")
    text = "".join(c for c in text if c.isalnum() or c == "_")
    # Normalizar sufijos comunes de TEI
    for suffix in ["_tei_v2", "_tei", "_xml", "tei"]:
        if text.endswith(suffix):
            text = text[: -len(suffix)]
    return text


def normalize_genre(value: str) -> str:
    val = normalize_text(value)
    return GENRE_MAP.get(val, "unknown")


def normalize_format(genre_norm: str) -> str:
    return FORMAT_MAP.get(genre_norm, "unknown")


def year_to_decade(year) -> str:
    if pd.isna(year):
        return "unknown_year"
    try:
        year_int = int(float(year))
        decade_start = (year_int // 10) * 10
        return f"{decade_start}s"
    except (ValueError, TypeError):
        return "unknown_year"


def resolve_override_path(path_arg: str | None) -> Path:
    if path_arg:
        return Path(path_arg)
    if DEFAULT_OVERRIDE_LOCAL.exists():
        return DEFAULT_OVERRIDE_LOCAL
    if DEFAULT_OVERRIDE_EXTERNAL.exists():
        return DEFAULT_OVERRIDE_EXTERNAL
    return DEFAULT_OVERRIDE_LOCAL


def load_override(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Override CSV no encontrado: {path}")

    df = pd.read_csv(path)

    # Alias de columnas
    col_map = {
        "obra_id": "obra_id",
        "doc_id": "obra_id",
        "archivo": "archivo",
        "tei_file": "tei_file",
        "year": "year",
        "year_first_pub": "year",
        "year_edition": "year_edition",
        "decade": "decade",
        "decada_norm": "decada_norm",
        "genre": "genre",
        "genero_macro_normalizado": "genre_macro",
        "format": "format",
        "year_estimated": "year_estimated",
        "source": "source",
        "notes": "notes",
    }

    df = df.rename(columns={c: col_map[c] for c in df.columns if c in col_map})

    # Normalizar columnas clave
    if "year" not in df.columns and "year_edition" in df.columns:
        df["year"] = df["year_edition"]

    # Completar year con year_edition si year falta
    if "year" in df.columns and "year_edition" in df.columns:
        df["year"] = df["year"].fillna(df["year_edition"])

    # Decada (si viene como numero)
    if "decada_norm" in df.columns and "decade" not in df.columns:
        df["decade"] = df["decada_norm"].apply(lambda x: f"{int(x)}s" if pd.notna(x) else "unknown_year")

    # Normalizar genero
    if "genre" in df.columns:
        df["genre_norm"] = df["genre"].apply(normalize_genre)
    elif "genre_macro" in df.columns:
        df["genre_norm"] = df["genre_macro"].apply(normalize_genre)
    else:
        df["genre_norm"] = "unknown"

    # Format (si no existe, derivar de genre_norm)
    if "format" in df.columns:
        df["format_norm"] = df["format"].apply(normalize_text)
        df["format_norm"] = df["format_norm"].replace({"": "unknown", "na": "unknown"})
    else:
        df["format_norm"] = df["genre_norm"].apply(normalize_format)

    # year_estimated (si no existe, inferir desde notes)
    if "year_estimated" not in df.columns:
        if "notes" in df.columns:
            df["year_estimated"] = df["notes"].astype(str).str.contains("ca\.|circa", case=False, na=False).astype(int)
        else:
            df["year_estimated"] = 0

    return df


def build_override_index(override: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in override.iterrows():
        keys = []
        if "obra_id" in row and pd.notna(row["obra_id"]):
            keys.append(normalize_text(row["obra_id"]))
        if "archivo" in row and pd.notna(row["archivo"]):
            keys.append(normalize_text(row["archivo"]))
        if "tei_file" in row and pd.notna(row["tei_file"]):
            tei_base = Path(str(row["tei_file"])).name
            tei_base = tei_base.replace(".xml", "")
            keys.append(normalize_text(tei_base))

        for key in set(keys):
            rows.append({"override_key": key, **row.to_dict()})

    expanded = pd.DataFrame(rows).drop_duplicates(subset=["override_key"])
    return expanded


def main():
    parser = argparse.ArgumentParser(description="Aplica metadata override a la tabla maestra")
    parser.add_argument(
        "--master",
        default=str(TABLES_DIR / "corpus_master_table_v2tokens.csv"),
        help="Ruta a tabla maestra base"
    )
    parser.add_argument(
        "--override",
        default=None,
        help="Ruta al CSV override"
    )
    parser.add_argument(
        "--output",
        default=str(TABLES_DIR / "corpus_master_table_v2tokens_meta.csv"),
        help="Ruta a tabla maestra meta-fixed"
    )
    args = parser.parse_args()

    master_path = Path(args.master)
    if not master_path.exists():
        print(f"❌ ERROR: master no encontrado: {master_path}")
        sys.exit(1)

    override_path = resolve_override_path(args.override)

    print("\n" + "=" * 70)
    print("APPLY_METADATA_OVERRIDE")
    print("=" * 70 + "\n")
    print(f"[master] {master_path}")
    print(f"[override] {override_path}")

    master = pd.read_csv(master_path)
    override = load_override(override_path)
    override_expanded = build_override_index(override)

    master = master.copy()
    master["_key"] = master["obra_id"].apply(normalize_text)

    merged = master.merge(override_expanded, left_on="_key", right_on="override_key", how="left", suffixes=("", "_ovr"))

    # Defaults
    if "year_source" not in merged.columns:
        merged["year_source"] = "tei"
    if "genre_source" not in merged.columns:
        merged["genre_source"] = "tei"
    if "year_estimated" not in merged.columns:
        merged["year_estimated"] = 0
    if "format" not in merged.columns:
        merged["format"] = ""

    # Apply overrides for year
    year_missing = merged["year"].isna()
    year_override = merged["year"].isna() & merged["year_ovr"].notna()
    merged.loc[year_override, "year"] = merged.loc[year_override, "year_ovr"]
    merged.loc[year_override, "year_source"] = "override"

    # Decade (prefer override decade if year is missing)
    if "decade_ovr" in merged.columns:
        decade_override = (merged["decade"] == "unknown_year") & merged["decade_ovr"].notna() & (merged["decade_ovr"] != "unknown_year")
        merged.loc[decade_override, "decade"] = merged.loc[decade_override, "decade_ovr"]
        merged.loc[decade_override & merged["year"].isna(), "year_source"] = "override_decade"

    merged["decade"] = merged.apply(
        lambda row: row["decade"] if row["decade"] != "unknown_year" else year_to_decade(row["year"]),
        axis=1
    )

    # Apply override genre when unknown
    genre_missing = merged["genre_norm"].isna() | (merged["genre_norm"].astype(str) == "unknown")
    genre_override = genre_missing & merged["genre_norm_ovr"].notna()
    merged.loc[genre_override, "genre_norm"] = merged.loc[genre_override, "genre_norm_ovr"]
    merged.loc[genre_override, "genre_source"] = "override"

    # Format
    format_missing = merged["format"].isna() | (merged["format"].astype(str).str.strip() == "") | (merged["format"].astype(str) == "unknown")
    format_from_override = merged["format_norm"].notna()
    merged.loc[format_missing & format_from_override, "format"] = merged.loc[format_missing & format_from_override, "format_norm"]

    # Fallback: format from genre_norm
    format_missing = merged["format"].isna() | (merged["format"].astype(str).str.strip() == "") | (merged["format"].astype(str) == "unknown")
    merged.loc[format_missing, "format"] = merged.loc[format_missing, "genre_norm"].apply(normalize_format)

    # year_estimated
    if "year_estimated_ovr" in merged.columns:
        merged.loc[merged["year_estimated_ovr"].notna(), "year_estimated"] = merged.loc[merged["year_estimated_ovr"].notna(), "year_estimated_ovr"]

    # Flags
    merged["year_missing"] = merged["year"].isna().astype(int)
    merged["genre_missing_flag"] = merged["genre_norm"].isna().astype(int) | (merged["genre_norm"].astype(str) == "unknown")
    merged["format_missing"] = merged["format"].isna().astype(int) | (merged["format"].astype(str) == "unknown")
    merged["genre_missing_flag"] = merged["genre_missing_flag"].astype(int)
    merged["format_missing"] = merged["format_missing"].astype(int)

    # Clean up
    drop_cols = [c for c in merged.columns if c.endswith("_ovr") or c in ["override_key", "_key", "decada_norm", "year_edition", "genre", "genre_macro", "format_norm", "source", "notes", "archivo", "tei_file", "year_first_pub"]]
    drop_cols = [c for c in drop_cols if c in merged.columns]
    merged = merged.drop(columns=drop_cols)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)

    # Update enriched tables if present
    for fname in ["units_enriched.csv", "case_rankings_enriched.csv", "emigrant_mentions_by_work_enriched.csv"]:
        fpath = TABLES_DIR / fname
        if fpath.exists():
            df = pd.read_csv(fpath)
            df = df.drop(columns=[c for c in ["year", "decade", "genre_norm", "format"] if c in df.columns], errors="ignore")
            df = df.merge(merged[["obra_id", "year", "decade", "genre_norm", "format"]], on="obra_id", how="left")
            df.to_csv(fpath, index=False)

    # QA report
    unknown_year = merged["year"].isna().sum()
    unknown_genre = (merged["genre_norm"].isna() | (merged["genre_norm"].astype(str) == "unknown")).sum()
    unknown_format = (merged["format"].isna() | (merged["format"].astype(str) == "unknown")).sum()

    report = []
    report.append("# METADATA OVERRIDE QA")
    report.append("")
    report.append(f"- Master: {master_path}")
    report.append(f"- Override: {override_path}")
    report.append("")
    report.append("## Summary")
    report.append("")
    report.append(f"- Total works: {len(merged)}")
    report.append(f"- unknown_year count: {unknown_year}")
    report.append(f"- unknown_genre count: {unknown_genre}")
    report.append(f"- unknown_format count: {unknown_format}")
    report.append("")

    missing = merged[(merged["year"].isna()) | (merged["genre_norm"].astype(str) == "unknown")]
    if not missing.empty:
        report.append("## Works still missing metadata")
        report.append("")
        for _, row in missing.head(10).iterrows():
            report.append(f"- {row['obra_id']}: year={row['year']} genre={row['genre_norm']}")
        if len(missing) > 10:
            report.append(f"- ... and {len(missing) - 10} more")
        report.append("")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    qa_path = DOCS_DIR / "METADATA_OVERRIDE_QA.md"
    qa_path.write_text("\n".join(report), encoding="utf-8")

    print(f"✅ Meta-fixed master: {output_path}")
    print(f"✅ QA report: {qa_path}")


if __name__ == "__main__":
    main()

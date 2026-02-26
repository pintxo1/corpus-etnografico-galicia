#!/usr/bin/env python3
"""
log_run.py - Registrar decisiones metodologicas del pipeline

Lee outputs existentes y agrega una entrada al cuaderno metodologico:
00_docs/02_cuaderno_decisiones_metodologicas.md
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List


csv.field_size_limit(2**24)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "01_data"
OUTPUTS_DIR = BASE_DIR / "04_outputs"
DOCS_DIR = BASE_DIR / "00_docs"

CUADERNO_PATH = DOCS_DIR / "02_cuaderno_decisiones_metodologicas.md"
PATTERNS_PATH = BASE_DIR / "02_methods" / "patterns" / "escenas_minimas.yml"


def _parse_patterns_fallback(yaml_path: Path) -> Dict:
    patterns = {}
    current_key = None
    current_obj = {}
    in_desc = False
    desc_lines = []

    with open(yaml_path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.rstrip("\n")
            stripped = raw.strip()

            if not stripped or stripped.startswith("#") or stripped == "---":
                continue

            if not raw.startswith(" ") and stripped.endswith(":"):
                if current_key:
                    if in_desc:
                        current_obj["descripcion"] = " ".join(desc_lines).strip()
                    patterns[current_key] = current_obj
                current_key = stripped[:-1]
                current_obj = {}
                in_desc = False
                desc_lines = []
                continue

            if current_key:
                if ":" in raw and raw.startswith("  "):
                    key, value = raw.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip("'\"")
                    if key == "descripcion" and value.startswith(">"):
                        in_desc = True
                        desc_lines = []
                        continue
                    if in_desc:
                        current_obj["descripcion"] = " ".join(desc_lines).strip()
                        in_desc = False
                        desc_lines = []
                    current_obj[key] = value
                else:
                    if in_desc:
                        desc_lines.append(stripped)

    if current_key:
        if in_desc:
            current_obj["descripcion"] = " ".join(desc_lines).strip()
        patterns[current_key] = current_obj

    return patterns


def load_patterns(yaml_path: Path) -> Dict:
    if not yaml_path.exists():
        return {}
    return _parse_patterns_fallback(yaml_path)


def count_rows(csv_path: Path) -> int:
    if not csv_path.exists():
        return 0
    with open(csv_path, "r", encoding="utf-8") as f:
        return max(0, sum(1 for _ in f) - 1)


def count_tei_files() -> int:
    tei_dir = DATA_DIR / "tei" / "source"
    if not tei_dir.exists():
        return 0
    return len(list(tei_dir.glob("*.xml")))


def top_counts(csv_path: Path, key: str, top_n: int = 3) -> List[str]:
    if not csv_path.exists():
        return []
    counts: Dict[str, int] = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            value = row.get(key, "")
            if not value:
                continue
            counts[value] = counts.get(value, 0) + 1
    top_items = sorted(counts.items(), key=lambda x: -x[1])[:top_n]
    return [f"{k} ({v})" for k, v in top_items]


def get_kwic_windows(patterns: Dict) -> List[str]:
    windows = set()
    for _, cfg in patterns.items():
        ventana = cfg.get("ventana", "")
        if ventana:
            windows.add(str(ventana))
    return sorted(windows, key=lambda x: int(x))


def append_entry(window_cooc: int = 40):
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    tei_count = count_tei_files()
    units_count = count_rows(DATA_DIR / "text" / "units.csv")
    cases_count = count_rows(DATA_DIR / "kwic_exports" / "cases_raw.csv")
    sampled_count = count_rows(BASE_DIR / "03_analysis" / "cases" / "cases_sampled.csv")
    cooc_count = count_rows(OUTPUTS_DIR / "tables" / "cooc_pairs.csv")

    patterns = load_patterns(PATTERNS_PATH)
    escenas_activas = sorted(patterns.keys())
    ventanas_kwic = get_kwic_windows(patterns)

    top_escenas = top_counts(DATA_DIR / "kwic_exports" / "cases_raw.csv", "escena_tipo")
    top_obras = top_counts(BASE_DIR / "03_analysis" / "cases" / "cases_sampled.csv", "obra_id")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = [
        f"### {timestamp}",
        "",
        f"- TEI procesados: {tei_count}",
        f"- Unidades: {units_count}",
        f"- Casos detectados: {cases_count}",
        f"- Casos muestreados: {sampled_count}",
        f"- Pares de coocurrencia: {cooc_count}",
        f"- Parametros clave: WINDOW cooc={window_cooc}; ventanas KWIC={', '.join(ventanas_kwic) if ventanas_kwic else 'N/D'}",
        f"- Escenas activas: {', '.join(escenas_activas) if escenas_activas else 'N/D'}",
        "- Riesgos/sesgos observables:",
        f"  - Escenas dominantes: {', '.join(top_escenas) if top_escenas else 'N/D'}",
        f"  - Obras sobrerrepresentadas en muestra: {', '.join(top_obras) if top_obras else 'N/D'}",
        "",
    ]

    if not CUADERNO_PATH.exists():
        header = [
            "# Cuaderno de Decisiones Metodologicas",
            "",
            "Registro de decisiones y sesgos observables del pipeline.",
            "",
            "## Entradas",
            "",
        ]
        CUADERNO_PATH.write_text("\n".join(header), encoding="utf-8")

    with open(CUADERNO_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + "\n".join(entry))


def main():
    append_entry()


if __name__ == "__main__":
    main()

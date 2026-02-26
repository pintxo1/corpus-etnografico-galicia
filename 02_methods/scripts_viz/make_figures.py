#!/usr/bin/env python3
"""
make_figures.py - Figuras basicas para exploracion

Genera PNG en 04_outputs/figures/ a partir de cases_raw y cooc_pairs.
"""

import argparse
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd


def load_cases(cases_path: Path) -> list[dict]:
    """Load cases using pandas to avoid CSV field size limit issues."""
    df = pd.read_csv(cases_path)
    return df.to_dict('records')


def load_cooc(cooc_path: Path) -> list[dict]:
    """Load cooc pairs using pandas."""
    df = pd.read_csv(cooc_path)
    return df.to_dict('records')


def fig_scene_coverage(cases: list[dict], outdir: Path) -> None:
    obras_por_escena = defaultdict(set)
    for row in cases:
        escena = row.get("escena_tipo", "").strip()
        obra = row.get("obra_id", "").strip()
        if escena and obra:
            obras_por_escena[escena].add(obra)

    escenas = sorted(obras_por_escena.keys())
    counts = [len(obras_por_escena[e]) for e in escenas]

    plt.figure(figsize=(10, 6))
    plt.bar(escenas, counts, color="#4c78a8")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("# obras unicas")
    plt.title("Cobertura por escena (obras unicas)")
    plt.tight_layout()
    plt.savefig(outdir / "fig_scene_coverage.png", dpi=150)
    plt.close()


def fig_scene_concentration(cases: list[dict], outdir: Path) -> None:
    casos_por_escena = defaultdict(list)
    for row in cases:
        escena = row.get("escena_tipo", "").strip()
        obra = row.get("obra_id", "").strip()
        if escena and obra:
            casos_por_escena[escena].append(obra)

    escenas = sorted(casos_por_escena.keys())
    percents = []
    for escena in escenas:
        obras = casos_por_escena[escena]
        total = len(obras)
        top3 = sum(v for _, v in Counter(obras).most_common(3))
        percent = (top3 / total * 100.0) if total else 0.0
        percents.append(percent)

    plt.figure(figsize=(10, 6))
    plt.bar(escenas, percents, color="#f58518")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("% casos en top-3 obras")
    plt.title("Concentracion por escena (top-3 obras)")
    plt.tight_layout()
    plt.savefig(outdir / "fig_scene_concentration.png", dpi=150)
    plt.close()


def fig_cooc_degree(cooc_rows: list[dict], outdir: Path) -> None:
    graph = nx.Graph()
    for row in cooc_rows:
        term_1 = row.get("term_1", "").strip()
        term_2 = row.get("term_2", "").strip()
        if not term_1 or not term_2:
            continue
        try:
            weight = int(row.get("n_cooc", 0))
        except ValueError:
            continue
        graph.add_edge(term_1, term_2, weight=weight)

    degrees = graph.degree(weight="weight")
    top20 = sorted(degrees, key=lambda x: x[1], reverse=True)[:20]
    terms = [t for t, _ in top20]
    weights = [w for _, w in top20]

    plt.figure(figsize=(10, 6))
    plt.bar(terms, weights, color="#54a24b")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("grado ponderado (n_cooc)")
    plt.title("Top 20 terminos por grado en coocurrencias")
    plt.tight_layout()
    plt.savefig(outdir / "fig_cooc_degree.png", dpi=150)
    plt.close()


def fig_case_score_distribution(cases: list[dict], outdir: Path) -> bool:
    if not cases:
        print("⚠️  cases_raw.csv vacio, se omite fig_case_score_distribution")
        return False

    if "score" not in cases[0]:
        print("⚠️  Columna score no existe en cases_raw.csv; se omite fig_case_score_distribution")
        return False

    scores = []
    for row in cases:
        value = row.get("score", "").strip()
        if not value:
            continue
        try:
            scores.append(float(value))
        except ValueError:
            continue

    if not scores:
        print("⚠️  Score vacio o no numerico; se omite fig_case_score_distribution")
        return False

    plt.figure(figsize=(10, 6))
    plt.hist(scores, bins=20, color="#e45756", edgecolor="#222")
    plt.xlabel("score")
    plt.ylabel("frecuencia")
    plt.title("Distribucion de score en casos")
    plt.tight_layout()
    plt.savefig(outdir / "fig_case_score_distribution.png", dpi=150)
    plt.close()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Generar figuras basicas")
    parser.add_argument("--cases", required=True, help="cases_raw.csv")
    parser.add_argument("--cooc", required=True, help="cooc_pairs.csv")
    parser.add_argument("--outdir", required=True, help="Directorio de salida")

    args = parser.parse_args()

    cases_path = Path(args.cases)
    cooc_path = Path(args.cooc)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if not cases_path.exists():
        raise SystemExit(f"cases_raw.csv no existe: {cases_path}")
    if not cooc_path.exists():
        raise SystemExit(f"cooc_pairs.csv no existe: {cooc_path}")

    cases = load_cases(cases_path)
    cooc_rows = load_cooc(cooc_path)

    print("📊 Generando fig_scene_coverage.png...")
    fig_scene_coverage(cases, outdir)

    print("📊 Generando fig_scene_concentration.png...")
    fig_scene_concentration(cases, outdir)

    print("📊 Generando fig_cooc_degree.png...")
    fig_cooc_degree(cooc_rows, outdir)

    print("📊 Generando fig_case_score_distribution.png...")
    fig_case_score_distribution(cases, outdir)

    print("✅ Figuras generadas")


if __name__ == "__main__":
    main()

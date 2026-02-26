#!/usr/bin/env python3
"""
export_networks.py - Exportar redes para Gephi

Outputs:
- cooc_network.graphml (terminos, peso=n_cooc)
- obra_escena_bipartite.graphml (obra_id <-> escena_tipo, peso=#casos)
- README.md en 04_outputs/networks/
"""

import argparse
from collections import Counter
from pathlib import Path

import networkx as nx
import pandas as pd


def load_cooc_edges(cooc_path: Path, min_cooc: int) -> list[tuple[str, str, int]]:
    """Load coocurrence edges from CSV using pandas."""
    edges = []
    df = pd.read_csv(cooc_path)
    for _, row in df.iterrows():
        try:
            n_cooc = int(row.get("n_cooc", 0))
        except (ValueError, TypeError):
            continue
        if n_cooc < min_cooc:
            continue
        term_1 = str(row.get("term_1", "")).strip()
        term_2 = str(row.get("term_2", "")).strip()
        if not term_1 or not term_2:
            continue
        edges.append((term_1, term_2, n_cooc))
    return edges


def build_cooc_graph(edges: list[tuple[str, str, int]]) -> nx.Graph:
    graph = nx.Graph()
    for term_1, term_2, weight in edges:
        graph.add_node(term_1, node_type="term")
        graph.add_node(term_2, node_type="term")
        graph.add_edge(term_1, term_2, weight=weight)
    return graph


def build_obra_escena_graph(cases_path: Path) -> nx.Graph:
    """Build obra-escena bipartite graph using pandas."""
    pairs = Counter()
    df = pd.read_csv(cases_path)
    for _, row in df.iterrows():
        obra = str(row.get("obra_id", "")).strip()
        escena = str(row.get("escena_tipo", "")).strip()
        if not obra or not escena:
            continue
        pairs[(obra, escena)] += 1

    graph = nx.Graph()
    for (obra, escena), weight in pairs.items():
        graph.add_node(obra, node_type="obra")
        graph.add_node(escena, node_type="escena")
        graph.add_edge(obra, escena, weight=weight)
    return graph


def write_readme(outdir: Path, min_cooc: int) -> None:
    readme_path = outdir / "README.md"
    content = """# Redes exportadas (Gephi)

Este directorio contiene redes exportadas en formato GraphML para exploracion en Gephi.

## Archivos

- cooc_network.graphml
  - Nodos: terminos de escena
  - Aristas: coocurrencias (weight = n_cooc)
  - Umbral aplicado: min_cooc = {min_cooc}

- obra_escena_bipartite.graphml
  - Nodos: obra_id y escena_tipo
  - Aristas: casos (weight = numero de casos)
  - Red bipartita (no reificacion de comunidades)

## Como abrir en Gephi

1. Abrir Gephi.
2. File -> Open -> seleccionar el .graphml.
3. Verificar que el atributo "weight" se lee como numerico.
4. Opcional: usar filtros de peso para reducir densidad.

## Limites e interpretacion

- Las redes son heuristicas para lectura situada.
- No representan relaciones causales ni categorias naturales.
- Los pesos reflejan coocurrencias textuales o frecuencia de casos, no realidad social.
""".format(min_cooc=min_cooc)
    readme_path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Exportar redes para Gephi")
    parser.add_argument("--cooc", required=True, help="cooc_pairs.csv")
    parser.add_argument("--cases", required=True, help="cases_raw.csv")
    parser.add_argument("--outdir", required=True, help="Directorio de salida")
    parser.add_argument("--min_cooc", type=int, default=5, help="Umbral minimo de n_cooc")

    args = parser.parse_args()

    cooc_path = Path(args.cooc)
    cases_path = Path(args.cases)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if not cooc_path.exists():
        raise SystemExit(f"cooc_pairs.csv no existe: {cooc_path}")
    if not cases_path.exists():
        raise SystemExit(f"cases_raw.csv no existe: {cases_path}")

    print("🔗 Generando cooc_network.graphml...")
    edges = load_cooc_edges(cooc_path, args.min_cooc)
    cooc_graph = build_cooc_graph(edges)
    nx.write_graphml(cooc_graph, outdir / "cooc_network.graphml")
    print(f"   Nodos: {cooc_graph.number_of_nodes()} | Aristas: {cooc_graph.number_of_edges()}")

    print("🧩 Generando obra_escena_bipartite.graphml...")
    oe_graph = build_obra_escena_graph(cases_path)
    nx.write_graphml(oe_graph, outdir / "obra_escena_bipartite.graphml")
    print(f"   Nodos: {oe_graph.number_of_nodes()} | Aristas: {oe_graph.number_of_edges()}")

    print("📝 Escribiendo README.md...")
    write_readme(outdir, args.min_cooc)

    print("✅ Redes exportadas")


if __name__ == "__main__":
    main()

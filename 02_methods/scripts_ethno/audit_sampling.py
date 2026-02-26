#!/usr/bin/env python3
"""
audit_sampling.py - Auditoria simple del muestreo etnografico

Inputs:
- cases_raw.csv
- cases_sampled.csv

Outputs:
- 04_outputs/tables/sampling_audit.csv
- 04_outputs/tables/sampling_audit.md
"""

import argparse
import csv
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple


csv.field_size_limit(2**24)


BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = BASE_DIR / "04_outputs" / "tables"


def load_csv(path: Path) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pct(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return (part / total) * 100.0


def top_distribution(items: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
    counter = Counter(items)
    return counter.most_common(top_n)


def write_audit_csv(
    output_csv: Path,
    sampled: List[Dict],
    cluster_col: str | None
):
    total = len(sampled)
    obra_counts = top_distribution([r.get("obra_id", "") for r in sampled])
    escena_counts = top_distribution([r.get("escena_tipo", "") for r in sampled])

    rows = []

    for obra, count in obra_counts:
        rows.append({
            "section": "obra",
            "key": obra,
            "count": count,
            "percent": f"{pct(count, total):.2f}",
            "note": "top_10"
        })

    for escena, count in escena_counts:
        rows.append({
            "section": "escena",
            "key": escena,
            "count": count,
            "percent": f"{pct(count, total):.2f}",
            "note": "top_10"
        })

    if cluster_col:
        cluster_counts = top_distribution([r.get(cluster_col, "") for r in sampled])
        for cluster, count in cluster_counts:
            rows.append({
                "section": "cluster_k4",
                "key": cluster,
                "count": count,
                "percent": f"{pct(count, total):.2f}",
                "note": "top"
            })

        # escena x cluster (matriz larga)
        combo_counts = Counter(
            (r.get("escena_tipo", ""), r.get(cluster_col, "")) for r in sampled
        )
        for (escena, cluster), count in combo_counts.most_common():
            rows.append({
                "section": "escena_x_cluster",
                "key": f"{escena} x {cluster}",
                "count": count,
                "percent": f"{pct(count, total):.2f}",
                "note": "full"
            })

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        fieldnames = ["section", "key", "count", "percent", "note"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_audit_md(
    output_md: Path,
    sampled: List[Dict],
    raw: List[Dict],
    cluster_col: str | None
):
    total = len(sampled)
    total_raw = len(raw)

    obra_counts = top_distribution([r.get("obra_id", "") for r in sampled], top_n=3)
    escena_counts = top_distribution([r.get("escena_tipo", "") for r in sampled], top_n=3)

    raw_obra_counts = top_distribution([r.get("obra_id", "") for r in raw], top_n=3)
    raw_escena_counts = top_distribution([r.get("escena_tipo", "") for r in raw], top_n=3)

    obras_raw = len({r.get("obra_id", "") for r in raw if r.get("obra_id", "")})
    escenas_raw = len({r.get("escena_tipo", "") for r in raw if r.get("escena_tipo", "")})
    obras_sample = len({r.get("obra_id", "") for r in sampled if r.get("obra_id", "")})
    escenas_sample = len({r.get("escena_tipo", "") for r in sampled if r.get("escena_tipo", "")})

    lines = []
    lines.append("# Informe breve - Auditoria de muestreo")
    lines.append("")
    lines.append(f"- Casos en bruto: {total_raw} | Casos muestreados: {total}.")
    lines.append(f"- Obras en bruto: {obras_raw} | Obras en muestra: {obras_sample}.")
    lines.append(f"- Escenas en bruto: {escenas_raw} | Escenas en muestra: {escenas_sample}.")

    if obra_counts:
        raw_share = pct(raw_obra_counts[0][1], total_raw) if raw_obra_counts else 0.0
        lines.append(
            f"- Obra mas frecuente en muestra: {obra_counts[0][0]} ({pct(obra_counts[0][1], total):.1f}%; bruto {raw_share:.1f}%)."
        )
        if len(obra_counts) > 1:
            lines.append(
                f"- Siguientes obras en muestra: {obra_counts[1][0]} ({pct(obra_counts[1][1], total):.1f}%), {obra_counts[2][0]} ({pct(obra_counts[2][1], total):.1f}%)."
            )

    if escena_counts:
        raw_share = pct(raw_escena_counts[0][1], total_raw) if raw_escena_counts else 0.0
        lines.append(
            f"- Escena mas frecuente en muestra: {escena_counts[0][0]} ({pct(escena_counts[0][1], total):.1f}%; bruto {raw_share:.1f}%)."
        )
        if len(escena_counts) > 1:
            lines.append(
                f"- Otras escenas dominantes: {escena_counts[1][0]} ({pct(escena_counts[1][1], total):.1f}%), {escena_counts[2][0]} ({pct(escena_counts[2][1], total):.1f}%)."
            )

    if cluster_col:
        cluster_counts = top_distribution([r.get(cluster_col, "") for r in sampled], top_n=2)
        if cluster_counts:
            lines.append(
                f"- Cluster con mayor presencia: {cluster_counts[0][0]} ({pct(cluster_counts[0][1], total):.1f}%)."
            )
    else:
        lines.append("- Cluster_k4 no disponible en muestra (no se reporta distribucion por cluster).")

    lines.append("- Si una obra supera ~25%, considerar max_per_obra en el muestreo.")
    lines.append("- Si una escena supera ~20%, revisar regex o ajustar min_per_escena.")
    lines.append("- Revisar escenas con baja presencia para ampliar patrones de forma minima.")
    lines.append("- El objetivo es diversidad de voces y escenas, no representatividad estadistica.")

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Auditoria simple del muestreo")
    parser.add_argument("--cases_raw", required=True, help="cases_raw.csv")
    parser.add_argument("--cases_sampled", required=True, help="cases_sampled.csv")
    parser.add_argument("--output_csv", required=True, help="sampling_audit.csv")
    parser.add_argument("--output_md", required=True, help="sampling_audit.md")

    args = parser.parse_args()

    print("📥 Cargando casos...")
    raw = load_csv(Path(args.cases_raw))
    sampled = load_csv(Path(args.cases_sampled))
    if not sampled:
        raise SystemExit("cases_sampled.csv esta vacio")

    cluster_col = None
    if sampled and "cluster_k4" in sampled[0]:
        has_cluster = any(r.get("cluster_k4", "").strip() for r in sampled)
        cluster_col = "cluster_k4" if has_cluster else None

    print(f"✅ Casos brutos: {len(raw)} | Casos muestreados: {len(sampled)}")
    if cluster_col:
        print("✅ cluster_k4 detectado en muestra")
    else:
        print("ℹ️  cluster_k4 ausente o vacio en muestra")

    write_audit_csv(Path(args.output_csv), sampled, cluster_col)
    write_audit_md(Path(args.output_md), sampled, raw, cluster_col)


if __name__ == "__main__":
    main()

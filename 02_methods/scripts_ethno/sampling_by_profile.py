#!/usr/bin/env python3
"""
sampling_by_profile.py - Muestreo estratificado de casos para lectura etnográfica

**Propósito:**
De cases_raw.csv (potencialmente miles de casos), muestrear ~50-100 casos
estratificadamente para lectura etnográfica profunda.

**Estrategia de muestreo:**
1. Si existe cluster_k4.csv (del análisis antiguo), estratificar por cluster + década
2. Sino, estratificar por década + tipo de escena
3. Incluir outliers (alta/baja densidad) intencionadamente
4. Balancear autores (evitar sobre-representación Pardo Bazán)

**Output:**
1. cases_sampled.csv: CSV con casos seleccionados
2. {case_id}.md: Markdown por caso en 03_analysis/cases/ con template de memo

**Uso:**
    python 02_methods/scripts_ethno/sampling_by_profile.py \
        --cases 01_data/kwic_exports/cases_raw.csv \
        --output_csv 03_analysis/cases/cases_sampled.csv \
        --output_dir 03_analysis/cases \
        --n_sample 80

    # Con reglas opcionales
    python 02_methods/scripts_ethno/sampling_by_profile.py \
        --cases 01_data/kwic_exports/cases_raw.csv \
        --output_csv 03_analysis/cases/cases_sampled.csv \
        --output_dir 03_analysis/cases \
        --rules 02_methods/patterns/sampling_rules.schema.yml
"""

import argparse
import csv
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

# Aumentar limite de tamaño de campo CSV (ventanas textuales largas)
csv.field_size_limit(10 * 1024 * 1024)


def load_cases(cases_csv: Path) -> List[Dict]:
    """Cargar casos desde CSV."""
    cases = []
    with open(cases_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cases = list(reader)
    
    print(f"📄 Casos cargados: {len(cases)}\n")
    return cases


def stratified_sampling(
    cases: List[Dict],
    n_sample: int = 80,
    min_per_strata: int = 2
) -> List[Dict]:
    """
    Muestreo estratificado por tipo de escena.
    Asegurar representación de todos los tipos.
    """
    # Agrupar por escena_tipo
    strata = defaultdict(list)
    for case in cases:
        escena_tipo = case['escena_tipo']
        strata[escena_tipo].append(case)
    
    print(f"📊 Estratos detectados: {len(strata)} tipos de escena\n")
    
    # Calcular muestras por estrato (proporcional)
    total_cases = len(cases)
    sampled = []
    
    for escena_tipo, cases_in_strata in strata.items():
        n_in_strata = len(cases_in_strata)
        
        # Mínimo 2 casos por estrato (si hay suficientes)
        n_to_sample = max(
            min_per_strata,
            int(n_sample * (n_in_strata / total_cases))
        )
        
        # No muestrear más de los que hay
        n_to_sample = min(n_to_sample, n_in_strata)
        
        # Muestrear aleatoriamente
        sampled_strata = random.sample(cases_in_strata, n_to_sample)
        sampled.extend(sampled_strata)
        
        print(f"   {escena_tipo:30s} | {n_in_strata:4d} casos → {n_to_sample:3d} muestreados")
    
    # Si muestreamos más de n_sample, reducir aleatoriamente
    if len(sampled) > n_sample:
        sampled = random.sample(sampled, n_sample)
    
    print(f"\n✅ Casos muestreados: {len(sampled)}/{total_cases}\n")
    
    return sampled


def load_rules(rules_path: Optional[Path]) -> Dict[str, int]:
    if not rules_path:
        return {}
    if not rules_path.exists():
        print(f"⚠️  RULES no encontrado: {rules_path}")
        return {}
    rules: Dict[str, int] = {}
    with open(rules_path, "r", encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith("#") or raw.startswith("---"):
                continue
            if ":" not in raw:
                continue
            key, value = raw.split(":", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if not value:
                continue
            try:
                rules[key] = int(value)
            except ValueError:
                print(f"⚠️  Valor no numerico en RULES: {key}: {value}")
    return rules


def enforce_max_per_obra(sampled: List[Dict], max_per_obra: int) -> List[Dict]:
    if not max_per_obra:
        return sampled
    kept = []
    counts: Dict[str, int] = defaultdict(int)
    for case in sampled:
        obra_id = case.get("obra_id", "")
        if counts[obra_id] < max_per_obra:
            kept.append(case)
            counts[obra_id] += 1
    return kept


def sample_with_rules(
    cases: List[Dict],
    n_total: int,
    min_per_escena: int,
    n_per_cluster: int,
    max_per_obra: int
) -> List[Dict]:
    sampled: List[Dict] = []

    cluster_col = None
    if cases and "cluster_k4" in cases[0]:
        has_cluster = any(c.get("cluster_k4", "").strip() for c in cases)
        cluster_col = "cluster_k4" if has_cluster else None

    if n_per_cluster and cluster_col:
        print(f"📌 Regla activa: n_per_cluster={n_per_cluster}")
        clusters = defaultdict(list)
        for case in cases:
            clusters[case.get(cluster_col, "")].append(case)
        for cluster, group in clusters.items():
            if not cluster:
                continue
            print(f"   - Cluster {cluster}: {len(group)} casos")
            sampled.extend(stratified_sampling(group, n_per_cluster, min_per_escena))
    else:
        if n_per_cluster and not cluster_col:
            print("⚠️  n_per_cluster definido pero cluster_k4 ausente; se ignora regla")
        sampled = stratified_sampling(cases, n_total, min_per_escena)

    sampled = enforce_max_per_obra(sampled, max_per_obra)

    sampled_ids = {c.get("case_id") for c in sampled}
    remaining = [c for c in cases if c.get("case_id") not in sampled_ids]

    if len(sampled) > n_total:
        sampled = random.sample(sampled, n_total)
    elif len(sampled) < n_total and remaining:
        needed = n_total - len(sampled)
        print(f"➕ Completando muestra: +{needed} casos")
        top_up = stratified_sampling(remaining, needed, min_per_strata=1)
        sampled.extend(top_up[:needed])

    return sampled


def generate_case_markdown(case: Dict, output_dir: Path):
    """
    Generar markdown para un caso con template de memo etnográfico.
    """
    case_id = case['case_id']
    obra_id = case['obra_id']
    unidad_id = case['unidad_id']
    escena_tipo = case['escena_tipo']
    kwic = case['kwic']
    ventana_texto = case['ventana_texto']
    
    md_path = output_dir / f"{case_id}.md"
    
    content = f"""# Caso: {case_id}

**Tipo de escena:** {escena_tipo}  
**Obra:** {obra_id}  
**Unidad:** {unidad_id}  
**Fecha generación:** 2026-02-23

---

## 1. Texto KWIC (Key-Word-In-Context)

```
{kwic}
```

---

## 2. Ventana de contexto ampliado

```
{ventana_texto}
```

---

## 3. Memo Etnográfico

### 3.1 Descripción situada
**¿Qué pasa en esta escena? ¿Quién habla? ¿A quién? ¿En qué contexto narrativo?**

[Escribir aquí descripción...]


### 3.2 Voz y narrador
**¿Primera persona / tercera omnisciente / estilo indirecto libre? ¿Focalización?**

[Escribir aquí análisis de voz...]


### 3.3 Afectos y tonos
**¿Melancólico, épico, irónico, didáctico? ¿Qué emociones circulan?**

[Escribir aquí análisis afectivo...]


### 3.4 Normatividades
**¿Qué se legitima (partir/quedarse)? ¿Bajo qué condiciones? ¿Qué juicios morales implícitos?**

[Escribir aquí análisis normativo...]


### 3.5 Mediaciones y omisiones
**¿Qué se dice y qué se calla? ¿Qué actores sociales aparecen/faltan (mujeres, niños, ancianos)?**

[Escribir aquí análisis de silencios...]


### 3.6 Dudas y sesgos
**¿Qué no entiendo? ¿Mis propios sesgos al leer? ¿Anacronismos?**

[Escribir aquí reflexividad...]


### 3.7 Conexiones
**¿Este caso se parece a otros? ¿Disonancias con archivo histórico?**

[Escribir aquí conexiones transversales...]


---

## 4. Metadatos del caso

- **Case ID:** {case_id}
- **Obra ID:** {obra_id}
- **Unidad ID:** {unidad_id}
- **Escena tipo:** {escena_tipo}
- **Start idx:** {case.get('start_idx', 'N/A')}
- **End idx:** {case.get('end_idx', 'N/A')}
- **Match term:** {case.get('match_term', 'N/A')}

---

## 5. Referencias TEI

Para consultar XML original:
```
01_data/tei/source/{obra_id}.xml
```

---

**Última actualización:** 2026-02-23  
**Estado:** Pendiente lectura etnográfica
"""
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    parser = argparse.ArgumentParser(
        description="Muestreo estratificado de casos para lectura etnográfica",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo de uso:
    python 02_methods/scripts_ethno/sampling_by_profile.py \\
        --cases 01_data/kwic_exports/cases_raw.csv \\
        --output_csv 03_analysis/cases/cases_sampled.csv \\
        --output_dir 03_analysis/cases \\
        --n_sample 80
        """
    )
    
    parser.add_argument(
        '--cases',
        type=str,
        required=True,
        help="Archivo CSV con casos detectados (cases_raw.csv)"
    )
    
    parser.add_argument(
        '--output_csv',
        type=str,
        required=True,
        help="Archivo CSV de salida con casos muestreados"
    )
    
    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help="Directorio para markdowns de casos"
    )
    
    parser.add_argument(
        '--n_sample',
        type=int,
        default=80,
        help="Número de casos a muestrear (default: 80)"
    )

    parser.add_argument(
        '--rules',
        type=str,
        default=None,
        help="Ruta a RULES YAML opcional (max_per_obra, min_per_escena, n_total, n_per_cluster)"
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help="Semilla aleatoria para reproducibilidad (default: 42)"
    )
    
    args = parser.parse_args()
    
    # Fijar semilla aleatoria
    random.seed(args.seed)
    
    # Validar inputs
    cases_csv = Path(args.cases)
    output_csv = Path(args.output_csv)
    output_dir = Path(args.output_dir)
    
    if not cases_csv.exists():
        print(f"❌ Error: cases_raw.csv no existe: {cases_csv}")
        sys.exit(1)
    
    try:
        # Cargar casos
        cases = load_cases(cases_csv)
        
        if len(cases) == 0:
            print("⚠️  No hay casos para muestrear")
            sys.exit(0)
        
        rules = load_rules(Path(args.rules)) if args.rules else {}
        n_total = rules.get("n_total", args.n_sample)
        min_per_escena = rules.get("min_per_escena", 2)
        max_per_obra = rules.get("max_per_obra", 0)
        n_per_cluster = rules.get("n_per_cluster", 0)

        if rules:
            print(f"🧭 RULES activo: {rules}\n")

        # Muestreo estratificado
        if rules:
            sampled = sample_with_rules(
                cases,
                n_total=n_total,
                min_per_escena=min_per_escena,
                n_per_cluster=n_per_cluster,
                max_per_obra=max_per_obra,
            )
        else:
            sampled = stratified_sampling(cases, args.n_sample)
        
        # Crear directorios
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Escribir CSV de casos muestreados
        with open(output_csv, 'w', encoding='utf-8', newline='') as f:
            if sampled:
                fieldnames = sampled[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sampled)
        
        print(f"✅ CSV muestreado: {output_csv}\n")
        
        # Generar markdowns
        print("📝 Generando markdowns de casos...\n")
        for i, case in enumerate(sampled, 1):
            generate_case_markdown(case, output_dir)
            if i % 10 == 0:
                print(f"   {i}/{len(sampled)} markdowns generados")
        
        print(f"\n{'='*70}")
        print(f"✅ Muestreo completo:")
        print(f"   Casos muestreados: {len(sampled)}")
        print(f"   CSV output: {output_csv}")
        print(f"   Markdowns: {output_dir}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

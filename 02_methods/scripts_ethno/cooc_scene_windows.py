#!/usr/bin/env python3
"""
cooc_scene_windows.py - Coocurrencias como tension narrativa (no causalidad)

**Propósito:**
Detectar coocurrencias de escenas etnograficas en ventanas de tokens.
NO busca causalidad. Sirve para identificar zonas de alta densidad narrativa.

**Input:**
- units.csv (01_data/text/units.csv)
- patrones YAML (02_methods/patterns/escenas_minimas.yml)

**Output:**
- cooc_pairs.csv con columnas:
  term_1, term_2, n_cooc, n_term1, n_term2, jaccard, ejemplos_contexto

**Uso:**
    python 02_methods/scripts_ethno/cooc_scene_windows.py \
        --input 01_data/text/units.csv \
        --patterns 02_methods/patterns/escenas_minimas.yml \
        --window 40 \
        --output 04_outputs/tables/cooc_pairs.csv
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# Aumentar limite de campo CSV (textos largos)
csv.field_size_limit(10 * 1024 * 1024)

try:
    import yaml
except ImportError:
    yaml = None


def _parse_value(value: str, key: str):
    value = value.strip()
    if value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    elif value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if key == 'ventana':
        try:
            return int(value)
        except ValueError:
            return None
    return value


def _load_patterns_fallback(yaml_path: Path) -> Dict:
    patterns = {}
    current_key = None
    current_obj = {}
    in_desc = False
    desc_lines = []

    with open(yaml_path, 'r', encoding='utf-8') as f:
        for line in f:
            raw = line.rstrip('\n')
            stripped = raw.strip()

            if not stripped or stripped.startswith('#') or stripped == '---':
                continue

            if not raw.startswith(' ') and stripped.endswith(':'):
                if current_key:
                    if in_desc:
                        current_obj['descripcion'] = ' '.join(desc_lines).strip()
                    patterns[current_key] = current_obj
                current_key = stripped[:-1]
                current_obj = {}
                in_desc = False
                desc_lines = []
                continue

            if current_key:
                if re.match(r'^\s{2,}[^:]+:', raw):
                    key, value = raw.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == 'descripcion' and value.startswith('>'):
                        in_desc = True
                        desc_lines = []
                        continue

                    if in_desc:
                        current_obj['descripcion'] = ' '.join(desc_lines).strip()
                        in_desc = False
                        desc_lines = []

                    current_obj[key] = _parse_value(value, key)
                else:
                    if in_desc:
                        desc_lines.append(stripped)

    if current_key:
        if in_desc:
            current_obj['descripcion'] = ' '.join(desc_lines).strip()
        patterns[current_key] = current_obj

    return patterns


def load_patterns(yaml_path: Path) -> Dict:
    if yaml:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            patterns = yaml.safe_load(f)
    else:
        print("⚠️  PyYAML no disponible. Usando parser YAML simple.")
        patterns = _load_patterns_fallback(yaml_path)

    if not patterns:
        raise ValueError(f"Archivo YAML vacio o invalido: {yaml_path}")

    # Solo necesitamos regex
    simplified = {}
    for escena_tipo, config in patterns.items():
        regex_pattern = config.get('regex', '')
        if regex_pattern:
            simplified[escena_tipo] = regex_pattern

    print(f"📋 Patrones cargados: {len(simplified)} tipos de escena\n")
    return simplified


def find_matches(text: str, patterns: Dict) -> List[Tuple[str, int]]:
    """
    Retorna lista de (escena_tipo, token_index) para matches en el texto.
    """
    matches = []

    for escena_tipo, regex_pattern in patterns.items():
        try:
            regex = re.compile(regex_pattern, re.IGNORECASE)
        except re.error as e:
            print(f"⚠️  Error en regex '{escena_tipo}': {e}")
            continue

        for match in regex.finditer(text):
            match_start = match.start()
            token_index = len(text[:match_start].split())
            matches.append((escena_tipo, token_index))

    return matches


def window_context(tokens: List[str], center_idx: int, window: int) -> str:
    start = max(0, center_idx - window)
    end = min(len(tokens), center_idx + window)
    return ' '.join(tokens[start:end])


def process_units(units_csv: Path, patterns: Dict, window: int) -> Tuple[Dict, Dict, Dict]:
    """
    Procesa unidades y calcula coocurrencias.

    Returns:
        cooc_counts: dict[(term1, term2)] = count
        term_counts: dict[term] = count
        examples: dict[(term1, term2)] = list[str]
    """
    cooc_counts = defaultdict(int)
    term_counts = defaultdict(int)
    examples = defaultdict(list)

    with open(units_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            text = row.get('text', '')
            if not text:
                continue

            tokens = text.split()
            matches = find_matches(text, patterns)

            if not matches:
                continue

            # Indexar por ventana anclada en cada match
            for escena_tipo, token_idx in matches:
                window_start = max(0, token_idx - window)
                window_end = min(len(tokens), token_idx + window)

                # Tipos presentes en esta ventana
                present_terms = set(
                    t for t, idx in matches if window_start <= idx <= window_end
                )

                # Contar presencia de terminos
                for t in present_terms:
                    term_counts[t] += 1

                # Coocurrencias (pares no ordenados)
                present_list = sorted(present_terms)
                for i in range(len(present_list)):
                    for j in range(i + 1, len(present_list)):
                        t1, t2 = present_list[i], present_list[j]
                        cooc_counts[(t1, t2)] += 1

                        # Guardar hasta 2 ejemplos de contexto
                        if len(examples[(t1, t2)]) < 2:
                            examples[(t1, t2)].append(
                                window_context(tokens, token_idx, window)
                            )

    return cooc_counts, term_counts, examples


def compute_jaccard(n_cooc: int, n_term1: int, n_term2: int) -> float:
    denom = n_term1 + n_term2 - n_cooc
    if denom == 0:
        return 0.0
    return n_cooc / denom


def write_output(output_csv: Path, cooc_counts: Dict, term_counts: Dict, examples: Dict):
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for (t1, t2), n_cooc in cooc_counts.items():
        n_term1 = term_counts.get(t1, 0)
        n_term2 = term_counts.get(t2, 0)
        jaccard = compute_jaccard(n_cooc, n_term1, n_term2)
        ejemplos = ' || '.join(examples.get((t1, t2), []))

        rows.append({
            'term_1': t1,
            'term_2': t2,
            'n_cooc': n_cooc,
            'n_term1': n_term1,
            'n_term2': n_term2,
            'jaccard': f"{jaccard:.4f}",
            'ejemplos_contexto': ejemplos
        })

    rows.sort(key=lambda r: (-r['n_cooc'], -float(r['jaccard'])))

    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['term_1', 'term_2', 'n_cooc', 'n_term1', 'n_term2', 'jaccard', 'ejemplos_contexto']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Output escrito: {output_csv}")
    print(f"✅ Pares generados: {len(rows)}")


def main():
    parser = argparse.ArgumentParser(
        description="Coocurrencias de escenas en ventanas (tension narrativa)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--input', type=str, required=True, help='units.csv de entrada')
    parser.add_argument('--patterns', type=str, required=True, help='YAML de patrones')
    parser.add_argument('--window', type=int, default=40, help='Ventana de tokens (default: 40)')
    parser.add_argument('--output', type=str, required=True, help='CSV de salida')

    args = parser.parse_args()

    units_csv = Path(args.input)
    patterns_yaml = Path(args.patterns)
    output_csv = Path(args.output)

    if not units_csv.exists():
        print(f"❌ Error: units.csv no existe: {units_csv}")
        sys.exit(1)

    if not patterns_yaml.exists():
        print(f"❌ Error: patterns YAML no existe: {patterns_yaml}")
        sys.exit(1)

    try:
        patterns = load_patterns(patterns_yaml)
        cooc_counts, term_counts, examples = process_units(units_csv, patterns, args.window)
        write_output(output_csv, cooc_counts, term_counts, examples)
        print("\nRecordatorio: coocurrencia ≠ causalidad; indica densidad narrativa.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

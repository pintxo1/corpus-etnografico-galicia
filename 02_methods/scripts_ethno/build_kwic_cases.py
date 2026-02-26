#!/usr/bin/env python3
"""
build_kwic_cases.py - Detectar casos/escenas etnográficas mediante regex KWIC

**Propósito:**
Aplicar patrones regex (escenas_minimas.yml) sobre texto plano (units.csv)
para detectar escenas etnográficas relevantes. Output: casos en formato KWIC.

**Filosofía anti-positivista:**
Un match regex NO es "evidencia" de realidad social.
Es una escena textual que requiere lectura etnográfica situada.
Los patrones son HEURÍSTICAS para muestrear, no variables para medir.

**Output:**
CSV con columnas:
- case_id: hash sha256 de (obra_id + unidad_id + escena_tipo + start_idx)
- obra_id, unidad_id: ubicación en corpus
- escena_tipo: tipo de escena según patrón YAML
- kwic: fragmento Key-Word-In-Context (keyword resaltado con **)
- ventana_texto: contexto ampliado (±ventana tokens)
- start_idx, end_idx: posición en texto unidad (para replicabilidad)
- match_term: término que matcheó (para debugging)

**Uso:**
    python 02_methods/scripts_ethno/build_kwic_cases.py \
        --units 01_data/text/units.csv \
        --patterns 02_methods/patterns/escenas_minimas.yml \
        --output 01_data/kwic_exports/cases_raw.csv
"""

import argparse
import csv
import hashlib
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Aumentar limite de tamaño de campo CSV (textos largos)
csv.field_size_limit(10 * 1024 * 1024)

try:
    import yaml
except ImportError:
    yaml = None


def _parse_value(value: str, key: str):
    """Parsear valores simples de YAML: strings con comillas y enteros."""
    value = value.strip()
    
    if value.startswith("'") and value.endswith("'"):
        value = value[1:-1]
    elif value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    
    if key == 'ventana':
        try:
            return int(value)
        except ValueError:
            return 80
    
    return value


def _load_patterns_fallback(yaml_path: Path) -> Dict:
    """
    Parser YAML simple para el formato de escenas_minimas.yml.
    Soporta:
    - Claves top-level
    - Campos: nombre, descripcion (multi-line con >), regex, ventana
    """
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
            
            # Nueva clave top-level
            if not raw.startswith(' ') and stripped.endswith(':'):
                # Guardar anterior
                if current_key:
                    if in_desc:
                        current_obj['descripcion'] = ' '.join(desc_lines).strip()
                    patterns[current_key] = current_obj
                
                current_key = stripped[:-1]
                current_obj = {}
                in_desc = False
                desc_lines = []
                continue
            
            # Campos indentados
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
                        # Cerrar descripcion si aparece otro campo
                        current_obj['descripcion'] = ' '.join(desc_lines).strip()
                        in_desc = False
                        desc_lines = []
                    
                    current_obj[key] = _parse_value(value, key)
                else:
                    if in_desc:
                        desc_lines.append(stripped)
    
    # Guardar último
    if current_key:
        if in_desc:
            current_obj['descripcion'] = ' '.join(desc_lines).strip()
        patterns[current_key] = current_obj
    
    return patterns


def load_patterns(yaml_path: Path) -> Dict:
    """Cargar patrones desde YAML (PyYAML o parser simple)."""
    if yaml:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            patterns = yaml.safe_load(f)
    else:
        print("⚠️  PyYAML no disponible. Usando parser YAML simple.")
        patterns = _load_patterns_fallback(yaml_path)
    
    if not patterns:
        raise ValueError(f"Archivo YAML vacío o inválido: {yaml_path}")
    
    print(f"📋 Patrones cargados: {len(patterns)} tipos de escena\n")
    return patterns


def generate_case_id(obra_id: str, unidad_id: str, escena_tipo: str, start_idx: int) -> str:
    """
    Generar case_id único y replicable.
    SHA256 de (obra_id + unidad_id + escena_tipo + start_idx).
    """
    content = f"{obra_id}|{unidad_id}|{escena_tipo}|{start_idx}"
    return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]


def extract_kwic_window(text: str, match_start: int, match_end: int, window_tokens: int = 80) -> Tuple[str, str, int, int]:
    """
    Extraer KWIC + ventana de contexto.
    
    Returns:
        (kwic, ventana_texto, window_start_idx, window_end_idx)
    """
    tokens = text.split()
    
    # Calcular índices de token del match
    text_before_match = text[:match_start]
    text_match = text[match_start:match_end]
    
    token_start = len(text_before_match.split())
    token_end = token_start + len(text_match.split())
    
    # Ventana de contexto (±window_tokens)
    window_start = max(0, token_start - window_tokens)
    window_end = min(len(tokens), token_end + window_tokens)
    
    # Reconstruir textos
    kwic_tokens = (
        tokens[max(0, token_start - 5):token_start] +
        ['**' + t + '**' for t in tokens[token_start:token_end]] +
        tokens[token_end:min(len(tokens), token_end + 5)]
    )
    kwic = ' '.join(kwic_tokens)
    
    ventana_tokens_list = tokens[window_start:window_end]
    ventana_texto = ' '.join(ventana_tokens_list)
    
    # Calcular índices de caracteres de la ventana
    window_start_char = len(' '.join(tokens[:window_start])) + (1 if window_start > 0 else 0)
    window_end_char = len(' '.join(tokens[:window_end]))
    
    return kwic, ventana_texto, window_start_char, window_end_char


def detect_cases_in_unit(
    obra_id: str,
    unidad_id: str,
    text: str,
    patterns: Dict,
    min_text_length: int = 100
) -> List[Dict]:
    """
    Detectar casos en una unidad textual.
    
    Returns:
        List of case dicts
    """
    if len(text) < min_text_length:
        return []
    
    cases = []
    
    for escena_tipo, config in patterns.items():
        regex_pattern = config.get('regex', '')
        ventana_tokens = config.get('ventana', 80)
        
        if not regex_pattern:
            continue
        
        # Buscar matches (case-insensitive)
        try:
            regex = re.compile(regex_pattern, re.IGNORECASE)
        except re.error as e:
            print(f"⚠️  Error en regex '{escena_tipo}': {e}")
            continue
        
        for match in regex.finditer(text):
            match_start = match.start()
            match_end = match.end()
            match_term = match.group(0)
            
            # Extraer KWIC + ventana
            kwic, ventana_texto, window_start, window_end = extract_kwic_window(
                text, match_start, match_end, ventana_tokens
            )
            
            # Generar case_id
            case_id = generate_case_id(obra_id, unidad_id, escena_tipo, match_start)
            
            cases.append({
                'case_id': case_id,
                'obra_id': obra_id,
                'unidad_id': unidad_id,
                'escena_tipo': escena_tipo,
                'kwic': kwic,
                'ventana_texto': ventana_texto,
                'start_idx': match_start,
                'end_idx': match_end,
                'match_term': match_term
            })
    
    return cases


def process_units_corpus(units_csv: Path, patterns: Dict, output_csv: Path):
    """
    Procesar todo el corpus units.csv y detectar casos.
    """
    print(f"📄 Procesando corpus: {units_csv}\n")
    
    all_cases = []
    obras_procesadas = 0
    total_units = 0
    
    with open(units_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            obra_id = row['obra_id']
            unidad_id = row['unidad_id']
            text = row['text']
            
            total_units += 1
            
            # Detectar casos en esta unidad
            cases = detect_cases_in_unit(obra_id, unidad_id, text, patterns)
            
            if cases:
                all_cases.extend(cases)
                obras_procesadas += 1
                
                if obras_procesadas % 10 == 0:
                    print(f"✅ {obras_procesadas} unidades procesadas | {len(all_cases)} casos detectados")
    
    # Escribir CSV output
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = [
            'case_id', 'obra_id', 'unidad_id', 'escena_tipo',
            'kwic', 'ventana_texto', 'start_idx', 'end_idx', 'match_term'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(all_cases)
    
    print(f"\n{'='*70}")
    print(f"✅ Detección completa:")
    print(f"   Unidades procesadas: {total_units}")
    print(f"   Unidades con casos: {obras_procesadas}")
    print(f"   Casos detectados: {len(all_cases)}")
    print(f"   Output: {output_csv}")
    print(f"{'='*70}\n")
    
    # Estadísticas por tipo de escena
    escenas_counts = {}
    for case in all_cases:
        escena_tipo = case['escena_tipo']
        escenas_counts[escena_tipo] = escenas_counts.get(escena_tipo, 0) + 1
    
    print("\n📊 Casos por tipo de escena:")
    for escena, count in sorted(escenas_counts.items(), key=lambda x: -x[1]):
        print(f"   {escena:30s} | {count:4d} casos")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Detectar casos/escenas etnográficas mediante regex KWIC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo de uso:
    python 02_methods/scripts_ethno/build_kwic_cases.py \\
        --units 01_data/text/units.csv \\
        --patterns 02_methods/patterns/escenas_minimas.yml \\
        --output 01_data/kwic_exports/cases_raw.csv
        """
    )
    
    parser.add_argument(
        '--units',
        type=str,
        required=True,
        help="Archivo CSV con unidades textuales (output de tei_to_text.py)"
    )
    
    parser.add_argument(
        '--patterns',
        type=str,
        default='02_methods/patterns/escenas_minimas.yml',
        help="Archivo YAML con patrones de escenas (default: escenas_minimas.yml)"
    )

    parser.add_argument(
        '--scene-yaml',
        type=str,
        default=None,
        help="Alias de --patterns para seleccionar diccionario (v1/v2)"
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='01_data/kwic_exports/cases_raw.csv',
        help="Archivo CSV de salida (default: 01_data/kwic_exports/cases_raw.csv)"
    )
    
    args = parser.parse_args()
    
    # Validar inputs
    units_csv = Path(args.units)
    patterns_yaml = Path(args.scene_yaml) if args.scene_yaml else Path(args.patterns)
    output_csv = Path(args.output)
    
    if not units_csv.exists():
        print(f"❌ Error: units.csv no existe: {units_csv}")
        sys.exit(1)
    
    if not patterns_yaml.exists():
        print(f"❌ Error: patterns YAML no existe: {patterns_yaml}")
        sys.exit(1)
    
    try:
        # Cargar patrones
        patterns = load_patterns(patterns_yaml)
        
        # Procesar corpus
        process_units_corpus(units_csv, patterns, output_csv)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

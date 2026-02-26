#!/usr/bin/env python3
"""
tei_to_text.py - Extraer texto plano de corpus TEI para análisis etnográfico

**Propósito:**
Procesar archivos TEI-XML y extraer texto plano organizado por unidades narrativas
(capítulos, cuentos, poemas, escenas teatrales).

**Output:**
CSV con columnas:
- obra_id: Identificador único de obra (filename base)
- unidad_id: Identificador de unidad narrativa (cap_01, escena_02, poema, etc.)
- text: Texto plano limpio (sin marcado XML, normalizado)
- xml_ref: Referencia a nodo TEI original (para consulta manual)
- n_tokens: Número de tokens (whitespace split)

**Estructura TEI esperada:**
- <body> con <div type="chapter">, <div type="scene">, <lg type="poem">, etc.
- Flexibilidad: Si TEI no tiene estructura clara, extraer todo <body> como unidad única

**Uso:**
    python 02_methods/scripts_tei/tei_to_text.py \\
        --input 01_data/tei/source/ \\
        --output 01_data/text/units.csv
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

try:
    from lxml import etree
except ImportError:
    print("❌ Error: lxml no instalado. Instalar con: pip install lxml")
    sys.exit(1)

# TEI namespace (P5)
TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}


def clean_text(text: str) -> str:
    """Limpiar texto extraído: normalizar espacios, eliminar saltos excesivos."""
    if not text:
        return ""
    
    # Comprimir whitespace múltiple
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar espacios inicio/final
    text = text.strip()
    
    return text


def count_tokens(text: str) -> int:
    """Contar tokens (whitespace split)."""
    return len(text.split())


def extract_unit_text(element) -> str:
    """
    Extraer texto de un elemento TEI (div, lg, etc.).
    Recursivamente obtiene texto de todos los hijos, ignorando <note> y <ref>.
    """
    text_parts = []
    
    for text in element.itertext():
        # Evitar notas al pie y referencias bibliográficas (ruido)
        if text.strip():
            text_parts.append(text.strip())
    
    return ' '.join(text_parts)


def detect_unit_type(div_element) -> str:
    """
    Detectar tipo de unidad según atributos TEI.
    Ejemplo: <div type="chapter" n="1"> → chapter
    """
    unit_type = div_element.get('type', 'div')
    return unit_type


def extract_units_from_tei(tei_path: Path) -> List[Dict]:
    """
    Extraer unidades narrativas de un archivo TEI.
    
    Returns:
        List of dicts: [{'obra_id': ..., 'unidad_id': ..., 'text': ..., 'xml_ref': ..., 'n_tokens': ...}]
    """
    obra_id = tei_path.stem  # Filename sin extensión
    
    try:
        tree = etree.parse(str(tei_path))
        root = tree.getroot()
    except Exception as e:
        print(f"⚠️  Error parseando {tei_path.name}: {e}")
        return []
    
    units = []
    
    # Buscar <text><body> (estructura estándar TEI)
    body = root.find('.//tei:text/tei:body', namespaces=TEI_NS)
    
    if body is None:
        # Fallback: Si no hay body, buscar cualquier <body> (TEI sin namespace)
        body = root.find('.//body')
    
    if body is None:
        print(f"⚠️  No se encontró <body> en {tei_path.name}")
        return []
    
    # Estrategia: Buscar divs con type (capítulos, escenas, etc.)
    divs = body.findall('.//tei:div[@type]', namespaces=TEI_NS)
    
    if not divs:
        # Fallback: Si no hay divs con type, buscar cualquier <div>
        divs = body.findall('.//div')
    
    if divs:
        # Procesar cada div como unidad
        for i, div in enumerate(divs, start=1):
            unit_type = detect_unit_type(div)
            unit_number = div.get('n', str(i))  # Usar @n si existe, sino secuencial
            
            # Formatear unidad_id: si es número, usar 02d; sino usar string tal cual
            if unit_number.isdigit():
                unidad_id = f"{unit_type}_{int(unit_number):02d}"
            else:
                unidad_id = f"{unit_type}_{unit_number}"
            
            text = extract_unit_text(div)
            
            if not text:
                continue
            
            xml_ref = f"{obra_id}.xml#div{i}"
            n_tokens = count_tokens(text)
            
            units.append({
                'obra_id': obra_id,
                'unidad_id': unidad_id,
                'text': clean_text(text),
                'xml_ref': xml_ref,
                'n_tokens': n_tokens
            })
    
    else:
        # Fallback final: Extraer todo <body> como unidad única
        print(f"⚠️  {tei_path.name}: No se detectó estructura (divs), extrayendo <body> completo")
        text = extract_unit_text(body)
        
        if text:
            units.append({
                'obra_id': obra_id,
                'unidad_id': 'body_completo',
                'text': clean_text(text),
                'xml_ref': f"{obra_id}.xml#body",
                'n_tokens': count_tokens(text)
            })
    
    return units


def process_tei_corpus(input_dir: Path, output_csv: Path):
    """
    Procesar todos los archivos TEI de input_dir y generar CSV en output_csv.
    """
    input_dir = Path(input_dir)
    output_csv = Path(output_csv)
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Directorio input no existe: {input_dir}")
    
    # Buscar archivos .xml
    tei_files = sorted(input_dir.glob('*.xml'))
    
    if not tei_files:
        print(f"⚠️  No se encontraron archivos .xml en {input_dir}")
        return
    
    print(f"📄 Procesando {len(tei_files)} archivos TEI...\n")
    
    all_units = []
    obras_procesadas = 0
    
    for tei_path in tei_files:
        units = extract_units_from_tei(tei_path)
        
        if units:
            all_units.extend(units)
            obras_procesadas += 1
            print(f"✅ {tei_path.name:60s} | {len(units):3d} unidades")
        else:
            print(f"❌ {tei_path.name:60s} | 0 unidades (error o vacío)")
    
    # Escribir CSV
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['obra_id', 'unidad_id', 'text', 'xml_ref', 'n_tokens']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(all_units)
    
    print(f"\n{'='*70}")
    print(f"✅ Procesado completo:")
    print(f"   Obras procesadas: {obras_procesadas}/{len(tei_files)}")
    print(f"   Unidades extraídas: {len(all_units)}")
    print(f"   Output: {output_csv}")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Extraer texto plano de corpus TEI → units.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo de uso:
    python 02_methods/scripts_tei/tei_to_text.py \\
        --input 01_data/tei/source/ \\
        --output 01_data/text/units.csv
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help="Directorio con archivos TEI .xml"
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='01_data/text/units.csv',
        help="Archivo CSV de salida (default: 01_data/text/units.csv)"
    )
    
    args = parser.parse_args()
    
    try:
        process_tei_corpus(args.input, args.output)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

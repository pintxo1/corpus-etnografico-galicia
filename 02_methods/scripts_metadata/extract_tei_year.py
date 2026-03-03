#!/usr/bin/env python3
"""
extract_tei_year.py - Extrae año de publicación desde TEI headers.

Busca en orden de prioridad:
1. teiHeader/fileDesc/publicationStmt/date[@when]
2. teiHeader/fileDesc/publicationStmt/date (text content)
3. teiHeader/sourceDesc/biblStruct/monogr/imprint/date[@when]
4. teiHeader/sourceDesc/bibl/date[@when]
5. Fallback: inferir de filename o dejar vacío

Normaliza a número entero (ej: 1886) y calcula decade (ej: 1880s).
"""

import argparse
import csv
import re
from pathlib import Path
from xml.etree import ElementTree as ET
import pandas as pd

BASE_DIR = Path(__file__).parent.parent.parent
TEI_DIR = BASE_DIR / "01_data" / "tei" / "source"
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"

# Namespace para TEI
TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}

def extract_year_from_tei(tei_path: Path) -> tuple[int, str, str]:
    """
    Extrae año desde TEI. Retorna (year, source_xpath, confidence).
    year: int o None
    source_xpath: str (ruta TEI usada)
    confidence: "high", "medium", "low", "missing"
    
    NOTA: publicationStmt/date suele ser fecha de digitalización, NO fecha original.
    """
    try:
        tree = ET.parse(tei_path)
        root = tree.getroot()
    except Exception as e:
        return None, "error", f"XML parse error: {e}"
    
    # 1. sourceDesc/biblStruct/monogr/imprint/date[@when]
    xpath = ".//tei:sourceDesc/tei:biblStruct/tei:monogr/tei:imprint/tei:date[@when]"
    match = root.find(xpath, TEI_NS)
    if match is not None and match.get("when"):
        year_str = match.get("when").strip()
        try:
            year = int(year_str[:4])
            return year, "sourceDesc/biblStruct/imprint/date[@when]", "high"
        except (ValueError, TypeError):
            pass
    
    # 2. sourceDesc/bibl/date[@when]
    xpath = ".//tei:sourceDesc/tei:bibl/tei:date[@when]"
    match = root.find(xpath, TEI_NS)
    if match is not None and match.get("when"):
        year_str = match.get("when").strip()
        try:
            year = int(year_str[:4])
            return year, "sourceDesc/bibl/date[@when]", "high"
        except (ValueError, TypeError):
            pass
    
    # 3. teiHeader/fileDesc/sourceDesc/biblStruct o bibl (año en texto)
    xpath = ".//tei:sourceDesc//*"
    for elem in root.findall(xpath, TEI_NS):
        if elem.text:
            # Buscar patrón año: 1XXX o 2XXX PERO EXCLUIR 202X (fechas de digitalización)
            m = re.search(r'\b(1[0-9]{3})\b', elem.text)  # Solo 1800-1999
            if m:
                year = int(m.group(1))
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                return year, f"sourceDesc/{tag}[text]", "medium"
    
    # 4. profileDesc/textClass comments o notas
    xpath = ".//tei:profileDesc//tei:note"
    for elem in root.findall(xpath, TEI_NS):
        if elem.text:
            m = re.search(r'\b(1[0-9]{3})\b', elem.text)
            if m:
                year = int(m.group(1))
                return year, "profileDesc/note[text]", "low"
    
    return None, "not_found", "missing"

def year_to_decade(year: int) -> str:
    """Convierte año a decade string (1886 -> 1880s)."""
    if year is None:
        return "unknown_year"
    decade_start = (year // 10) * 10
    return f"{decade_start}s"

def main():
    parser = argparse.ArgumentParser(description="Extraer años desde TEI headers")
    parser.add_argument(
        "--tei-dir",
        type=Path,
        default=TEI_DIR,
        help="Directorio con archivos TEI"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=TABLES_DIR / "work_years_from_tei.csv",
        help="Archivo output: work_years_from_tei.csv"
    )
    args = parser.parse_args()
    
    print("=" * 70)
    print("EXTRACT_TEI_YEAR: Extrae año desde TEI headers")
    print("=" * 70)
    print()
    
    # Encontrar archivos TEI
    tei_files = sorted(args.tei_dir.glob("*tei.xml"))
    print(f"📂 Encontrados {len(tei_files)} archivos TEI\n")
    
    results = []
    missing_count = 0
    for tei_file in tei_files:
        obra_id = tei_file.stem.replace("_tei", "")
        year, source, confidence = extract_year_from_tei(tei_file)
        decade = year_to_decade(year)
        
        results.append({
            "obra_id": obra_id,
            "year": year,
            "decade": decade,
            "year_source_xpath": source,
            "year_confidence": confidence,
            "tei_file": tei_file.name
        })
        
        if confidence == "missing":
            missing_count += 1
            print(f"⚠️  {obra_id}: NO AÑO ENCONTRADO")
        elif confidence in ["low", "medium"]:
            print(f"⚠️  {obra_id}: año {year} (confianza: {confidence}, xpath: {source})")
    
    # Guardar output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(args.output, index=False)
    
    print()
    print("=" * 70)
    print(f"✅ Años extraídos: {args.output}")
    print("=" * 70)
    print()
    print(f"Resumen:")
    print(f"  - Total obras: {len(df)}")
    print(f"  - Con año (confianza alta): {(df['year_confidence'] == 'high').sum()}")
    print(f"  - Con año (confianza media): {(df['year_confidence'] == 'medium').sum()}")
    print(f"  - Con año (confianza baja): {(df['year_confidence'] == 'low').sum()}")
    print(f"  - Sin año: {missing_count}")
    print()
    
    print("Distribución por década:")
    decade_counts = df['decade'].value_counts().sort_index()
    for decade, count in decade_counts.items():
        print(f"  {decade}: {count}")
    print()

if __name__ == "__main__":
    main()

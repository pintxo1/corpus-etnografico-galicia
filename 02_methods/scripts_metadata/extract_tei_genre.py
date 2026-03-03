#!/usr/bin/env python3
"""
extract_tei_genre.py - Extrae género/formato desde TEI headers.

Busca el género en rutas típicas TEI:
  1. //tei:textClass/tei:classCode[@scheme='genero']
  2. //tei:textClass/tei:keywords/tei:term[@type='genre']
  3. //tei:catRef[@target] (si apunta a género)
  4. //tei:note[@type='genre']

Normaliza a un set estable: novela, cuento_relato, poesia_poemario,
teatro, ensayo_cronica, otro, unknown.

Output: 04_outputs/tables/work_genre_from_tei.csv
"""

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple

from lxml import etree

# Namespace TEI
NS = {"tei": "http://www.tei-c.org/ns/1.0"}

# Mapeo de normalización de género
GENRE_NORMALIZATION = {
    # Teatro
    "teatro": "teatro",
    "drama": "teatro",
    "comedia": "teatro",
    "tragedia": "teatro",
    "pieza teatral": "teatro",
    
    # Novela
    "novela": "novela",
    "novel": "novela",
    "narrativa larga": "novela",
    
    # Cuento/relato
    "cuento": "cuento_relato",
    "relato": "cuento_relato",
    "short story": "cuento_relato",
    "narrativa breve": "cuento_relato",
    "narración": "cuento_relato",
    
    # Poesía
    "poesía": "poesia_poemario",
    "poesia": "poesia_poemario",
    "poetry": "poesia_poemario",
    "poemario": "poesia_poemario",
    "poema": "poesia_poemario",
    "versos": "poesia_poemario",
    
    # Ensayo/crónica
    "ensayo": "ensayo_cronica",
    "crónica": "ensayo_cronica",
    "cronica": "ensayo_cronica",
    "essay": "ensayo_cronica",
    "artículo": "ensayo_cronica",
    "articulo": "ensayo_cronica",
    "prosa periodística": "ensayo_cronica",
    
    # Otros
    "otro": "otro",
    "mixto": "otro",
    "híbrido": "otro",
    "varios": "otro",
}


def extract_genre_from_tei(tei_path: Path) -> Tuple[str, str, str, str]:
    """
    Extrae género desde un archivo TEI.
    
    Returns:
        (genre_raw, genre_norm, genre_confidence, genre_source_xpath)
    """
    try:
        tree = etree.parse(str(tei_path))
    except Exception as e:
        return ("", "unknown", "error", f"Parse error: {e}")
    
    # Estrategia 1: classCode con scheme='genero'
    classCode = tree.xpath("//tei:textClass/tei:classCode[@scheme='genero']", namespaces=NS)
    if classCode:
        genre_raw = classCode[0].text.strip() if classCode[0].text else ""
        if genre_raw:
            genre_norm = normalize_genre(genre_raw)
            confidence = "high" if genre_norm != "otro" else "medium"
            return (genre_raw, genre_norm, confidence, "//tei:textClass/tei:classCode[@scheme='genero']")
    
    # Estrategia 2: keywords/term[@type='genre']
    keywords = tree.xpath("//tei:textClass/tei:keywords/tei:term[@type='genre']", namespaces=NS)
    if keywords:
        genre_raw = keywords[0].text.strip() if keywords[0].text else ""
        if genre_raw:
            genre_norm = normalize_genre(genre_raw)
            confidence = "medium"
            return (genre_raw, genre_norm, confidence, "//tei:textClass/tei:keywords/tei:term[@type='genre']")
    
    # Estrategia 3: keywords/term (sin @type, intentar inferir)
    keywords_general = tree.xpath("//tei:textClass/tei:keywords/tei:term", namespaces=NS)
    for term in keywords_general:
        text = term.text.strip() if term.text else ""
        if text.lower() in GENRE_NORMALIZATION:
            genre_raw = text
            genre_norm = normalize_genre(genre_raw)
            confidence = "medium"
            return (genre_raw, genre_norm, confidence, "//tei:textClass/tei:keywords/tei:term (inferred)")
    
    # Estrategia 4: catRef[@target]
    catRef = tree.xpath("//tei:textClass/tei:catRef[@target]", namespaces=NS)
    if catRef:
        target = catRef[0].get("target", "")
        if "genre" in target.lower():
            # Extraer texto del target (ej. #genre_teatro → teatro)
            genre_raw = target.split("_")[-1] if "_" in target else target.replace("#", "")
            if genre_raw:
                genre_norm = normalize_genre(genre_raw)
                confidence = "low"
                return (genre_raw, genre_norm, confidence, "//tei:textClass/tei:catRef[@target]")
    
    # Estrategia 5: note[@type='genre']
    note = tree.xpath("//tei:notesStmt/tei:note[@type='genre']", namespaces=NS)
    if note:
        genre_raw = note[0].text.strip() if note[0].text else ""
        if genre_raw:
            genre_norm = normalize_genre(genre_raw)
            confidence = "low"
            return (genre_raw, genre_norm, confidence, "//tei:notesStmt/tei:note[@type='genre']")
    
    # No encontrado
    return ("", "unknown", "low", "not_found")


def normalize_genre(genre_raw: str) -> str:
    """
    Normaliza género a set estable.
    """
    genre_lower = genre_raw.lower().strip()
    
    # Búsqueda exacta
    if genre_lower in GENRE_NORMALIZATION:
        return GENRE_NORMALIZATION[genre_lower]
    
    # Búsqueda parcial (keywords en el raw)
    for key, norm in GENRE_NORMALIZATION.items():
        if key in genre_lower or genre_lower in key:
            return norm
    
    # Fallback
    return "otro"


def main():
    parser = argparse.ArgumentParser(description="Extrae género desde TEI headers")
    parser.add_argument("--tei-dir", type=Path, default=Path("01_data/tei/source"),
                        help="Directorio con archivos TEI")
    parser.add_argument("--output", type=Path, default=Path("04_outputs/tables/work_genre_from_tei.csv"),
                        help="CSV de salida")
    args = parser.parse_args()
    
    # Base dir relativo al script
    BASE_DIR = Path(__file__).parent.parent.parent
    tei_dir = BASE_DIR / args.tei_dir
    output_path = BASE_DIR / args.output
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("EXTRACT_TEI_GENRE: Extrae género desde TEI headers")
    print("="*70)
    print()
    
    # Buscar archivos TEI
    tei_files = sorted(list(tei_dir.glob("*.xml")) + list(tei_dir.glob("*.tei.xml")))
    # Deduplicate
    tei_files_unique = []
    seen = set()
    for f in tei_files:
        if f.name not in seen:
            tei_files_unique.append(f)
            seen.add(f.name)
    tei_files = tei_files_unique
    
    print(f"[tei] Encontrados {len(tei_files)} archivos TEI")
    print()
    
    # Extraer género
    results = []
    stats = {"high": 0, "medium": 0, "low": 0, "error": 0, "unknown": 0}
    
    for tei_file in tei_files:
        obra_id = tei_file.stem
        genre_raw, genre_norm, genre_confidence, genre_source_xpath = extract_genre_from_tei(tei_file)
        
        results.append({
            "obra_id": obra_id,
            "genre_raw": genre_raw,
            "genre_norm": genre_norm,
            "genre_confidence": genre_confidence,
            "genre_source_xpath": genre_source_xpath,
            "genre_missing_flag": 1 if genre_norm == "unknown" else 0
        })
        
        # Stats
        stats[genre_confidence] = stats.get(genre_confidence, 0) + 1
        if genre_norm == "unknown":
            stats["unknown"] += 1
    
    # Guardar CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["obra_id", "genre_raw", "genre_norm",
                                                "genre_confidence", "genre_source_xpath",
                                                "genre_missing_flag"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ work_genre_from_tei.csv guardado: {output_path}")
    print()
    print("="*70)
    print("ESTADÍSTICAS DE EXTRACCIÓN:")
    print("="*70)
    print(f"  Total obras: {len(results)}")
    print(f"  Confidence high: {stats['high']}")
    print(f"  Confidence medium: {stats['medium']}")
    print(f"  Confidence low: {stats['low']}")
    print(f"  Errors: {stats['error']}")
    print(f"  Genre unknown: {stats['unknown']} ({100*stats['unknown']/len(results):.1f}%)")
    print()
    
    # Top géneros
    genre_counts = {}
    for r in results:
        genre_counts[r["genre_norm"]] = genre_counts.get(r["genre_norm"], 0) + 1
    
    print("Top géneros normalizados:")
    for genre, count in sorted(genre_counts.items(), key=lambda x: -x[1]):
        print(f"  {genre}: {count}")
    print()
    
    # Obras con unknown
    if stats["unknown"] > 0:
        print(f"⚠️  Obras con genre_norm=unknown ({stats['unknown']}):")
        for r in results:
            if r["genre_norm"] == "unknown":
                print(f"  - {r['obra_id']}: '{r['genre_raw']}' ({r['genre_source_xpath']})")
        print()
        print("Recomendación: revisar TEI headers de estas obras y añadir <classCode scheme='genero'>")
        print()


if __name__ == "__main__":
    main()

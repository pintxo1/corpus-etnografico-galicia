#!/usr/bin/env python3
"""
Extrae metadata canónica desde TEI headers
Input: 01_data/tei/source/*.xml
Output: 04_outputs/tables/works_metadata_from_tei.csv

Campos: obra_id, title, author, author_key, year, source_file, 
        author_confidence, why_missing
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
import re
import unicodedata
import argparse


def slugify(text):
    """Convierte texto a slug sin tildes, lowercase"""
    if not text:
        return ""
    # Normalizar unicode (NFKD)
    text = unicodedata.normalize('NFKD', text)
    # Eliminar diacríticos
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Lowercase, espacios por underscore
    text = text.lower().replace(' ', '_').replace(',', '')
    return text


def extract_author_from_tei(filepath):
    """
    Extrae autor desde TEI header con fallbacks robustos.
    
    Retorna: (author, confidence, why_missing)
    - author: string o None
    - confidence: 'high' | 'medium' | 'low' | None
    - why_missing: razón si no se encontró
    """
    
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        return None, None, f"XML parse error: {str(e)}"
    
    # Namespace default TEI
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Estrategia 1: teiHeader/fileDesc/titleStmt/author (más común)
    author_elem = root.find('.//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author', ns)
    if author_elem is not None and author_elem.text:
        author = author_elem.text.strip()
        return author, 'high', None
    
    # Estrategia 2: Sin namespace (algunos TEI no tienen namespace explícito)
    author_elem = root.find('.//fileDesc/titleStmt/author')
    if author_elem is not None and author_elem.text:
        author = author_elem.text.strip()
        return author, 'high', None
    
    # Estrategia 3: respStmt/name[@type='author']
    resp_elems = root.findall('.//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:respStmt/tei:name[@type="author"]', ns)
    if not resp_elems:
        resp_elems = root.findall('.//fileDesc/titleStmt/respStmt/name[@type="author"]')
    
    if resp_elems:
        authors = [elem.text.strip() for elem in resp_elems if elem.text]
        if authors:
            author = '; '.join(authors)
            return author, 'medium', None
    
    # Estrategia 4: respStmt con role='author'
    resp_elems = root.findall('.//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:respStmt[@role="author"]', ns)
    if not resp_elems:
        resp_elems = root.findall('.//fileDesc/titleStmt/respStmt[@role="author"]')
    
    if resp_elems:
        names = resp_elems[0].findall('.//tei:name', ns) + resp_elems[0].findall('.//name')
        if names:
            author = names[0].text.strip() if names[0].text else None
            if author:
                return author, 'medium', None
    
    # Si llegamos aquí, no hay autor
    return None, None, "No author found in titleStmt or respStmt"


def extract_title_from_tei(filepath):
    """Extrae título desde TEI"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except:
        return None
    
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Estrategia 1: con namespace
    title_elem = root.find('.//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title', ns)
    if title_elem is not None and title_elem.text:
        return title_elem.text.strip()
    
    # Estrategia 2: sin namespace
    title_elem = root.find('.//fileDesc/titleStmt/title')
    if title_elem is not None and title_elem.text:
        return title_elem.text.strip()
    
    return None


def extract_year_from_tei(filepath):
    """Extrae año desde publicationStmt"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except:
        return None
    
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Buscar date
    date_elem = root.find('.//tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date', ns)
    if date_elem is None:
        date_elem = root.find('.//fileDesc/publicationStmt/date')
    
    if date_elem is not None:
        when = date_elem.get('when')
        if when:
            # Extraer año (YYYY-MM-DD o YYYY)
            match = re.match(r'(\d{4})', when)
            if match:
                return int(match.group(1))
    
    return None


def obra_id_from_filename(filename):
    """Genera obra_id desde nombre de archivo (sin .xml)"""
    return filename.replace('.xml', '')


def main():
    parser = argparse.ArgumentParser(description='Extrae metadata desde TEI headers')
    parser.add_argument('--tei-dir', required=True, help='Directorio con archivos TEI')
    parser.add_argument('--output', required=True, help='Path output CSV')
    
    args = parser.parse_args()
    
    tei_dir = Path(args.tei_dir)
    output_path = Path(args.output)
    
    if not tei_dir.exists():
        print(f"❌ ERROR: Directorio no existe: {tei_dir}")
        exit(1)
    
    # Encontrar archivos XML
    xml_files = sorted(tei_dir.glob('*.xml'))
    print(f"📂 Encontrados {len(xml_files)} archivos TEI")
    
    metadata = []
    n_with_author = 0
    n_without_author = 0
    
    for xml_file in xml_files:
        obra_id = obra_id_from_filename(xml_file.name)
        title = extract_title_from_tei(xml_file)
        author, confidence, why_missing = extract_author_from_tei(xml_file)
        year = extract_year_from_tei(xml_file)
        author_key = slugify(author) if author else None
        
        if author:
            n_with_author += 1
            author_confidence = confidence or 'high'
        else:
            n_without_author += 1
            author_confidence = None
        
        metadata.append({
            'obra_id': obra_id,
            'title': title,
            'author': author,
            'author_key': author_key,
            'year': year,
            'source_file': xml_file.name,
            'author_confidence': author_confidence,
            'why_missing': why_missing if not author else None
        })
    
    # Crear DataFrame
    df = pd.DataFrame(metadata)
    
    # Guardar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Metadata extraída: {output_path}")
    print(f"\n📊 Resumen:")
    print(f"   Total TEI: {len(xml_files)}")
    print(f"   Con autor: {n_with_author}")
    print(f"   Sin autor: {n_without_author}")
    
    # Mostrar top autores
    print(f"\n🔝 Top autores por número de obras:")
    author_counts = df[df['author'].notna()]['author'].value_counts().head(10)
    for author, count in author_counts.items():
        print(f"   {author}: {count} obras")
    
    # Obras sin autor
    if n_without_author > 0:
        print(f"\n⚠️  Obras sin autor identificado ({n_without_author}):")
        unknown = df[df['author'].isna()][['obra_id', 'title', 'why_missing']]
        for _, row in unknown.head(15).iterrows():
            print(f"   - {row['obra_id']}: {row['why_missing']}")


if __name__ == '__main__':
    main()

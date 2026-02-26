#!/usr/bin/env python3
"""
Extrae metadata canónica desde TEI headers (VERSIÓN 2: MEJORADA)
Input: 01_data/tei/source/*.xml
Output: 04_outputs/tables/works_metadata_from_tei.csv

Campos: obra_id, title, author_raw, author_normalized, author_norm_key, year, 
        source_file, author_confidence, why_missing

Garantías:
- Si author NO se encuentra: author_confidence + why_missing SIEMPRE rellenos
- Búsqueda extendida en TEI (titleStmt → respStmt → sourceDesc → profileDesc)
- Si SIEMPRE falha: inferir desde filename + marcar low_inferred
"""

import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
import yaml
import re
import unicodedata
import argparse


def slugify(text):
    """Convierte texto a slug sin tildes, lowercase"""
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower().replace(' ', '_').replace(',', '').replace('.', '')
    return text


def load_author_normalization(normalization_file):
    """Carga reglas de normalización de autores"""
    if not Path(normalization_file).exists():
        print(f"⚠️  Archivo de normalización no encontrado: {normalization_file}")
        return {}
    
    try:
        with open(normalization_file, 'r', encoding='utf-8') as f:
            rules = yaml.safe_load(f) or {}
        return rules.get('author_mappings', {})
    except Exception as e:
        print(f"⚠️  Error leyendo normalización: {e}")
        return {}


def normalize_author(author_raw, normalization_rules):
    """Aplica reglas de normalización al autor"""
    if not author_raw:
        return None
    
    author_raw = author_raw.strip()
    
    # Buscar coincidencia exacta en reglas
    if author_raw in normalization_rules:
        return normalization_rules[author_raw]
    
    # Si no hay regla, devolver como está
    return author_raw


def extract_author_from_tei_extended(filepath):
    """
    Extrae autor desde TEI header con búsqueda EXTENDIDA.
    
    Búsqueda en orden de preferencia:
    1. teiHeader/fileDesc/titleStmt/author
    2. teiHeader/fileDesc/titleStmt/respStmt/name[@type='author']
    3. teiHeader/fileDesc/titleStmt/respStmt[@role='author']/name
    4. teiHeader/fileDesc/sourceDesc/bibl/author
    5. teiHeader/profileDesc/particDesc/listPerson/person (si nombre principal)
    
    Retorna: (author_raw, confidence, why_missing)
    """
    
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except Exception as e:
        return None, None, f"XML parse error: {str(e)}"
    
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # ===== BÚSQUEDA 1: titleStmt/author (incluyendo VACÍOS)
    author_elem = root.find('.//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:author', ns)
    if author_elem is None:
        author_elem = root.find('.//fileDesc/titleStmt/author')
    
    if author_elem is not None:
        # El elemento existe
        text = author_elem.text.strip() if author_elem.text else ""
        if text:
            # Tiene contenido
            return text, 'high', None
        else:
            # Elemento existe pero está vacío
            return None, None, "author element found in titleStmt but empty (no text content)"
    
    # ===== BÚSQUEDA 2: titleStmt/respStmt/@role='author'/name
    resp_elems = root.findall(
        './/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:respStmt[@role="author"]/tei:name', ns
    )
    if not resp_elems:
        resp_elems = root.findall('.//fileDesc/titleStmt/respStmt[@role="author"]/name')
    
    if resp_elems and resp_elems[0].text:
        return resp_elems[0].text.strip(), 'high', None
    
    # ===== BÚSQUEDA 3: titleStmt/respStmt/name[@type='author']
    resp_elems = root.findall(
        './/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:respStmt/tei:name[@type="author"]', ns
    )
    if not resp_elems:
        resp_elems = root.findall('.//fileDesc/titleStmt/respStmt/name[@type="author"]')
    
    if resp_elems:
        authors = [elem.text.strip() for elem in resp_elems if elem.text]
        if authors:
            return authors[0], 'medium', None
    
    # ===== BÚSQUEDA 4: sourceDesc/bibl/author
    bibl_author = root.find('.//tei:teiHeader/tei:fileDesc/tei:sourceDesc/tei:bibl/tei:author', ns)
    if bibl_author is None:
        bibl_author = root.find('.//fileDesc/sourceDesc/bibl/author')
    
    if bibl_author is not None and bibl_author.text:
        return bibl_author.text.strip(), 'medium', None
    
    # ===== BÚSQUEDA 5: profileDesc/particDesc/listPerson/person (principal)
    person_elems = root.findall(
        './/tei:teiHeader/tei:profileDesc/tei:particDesc/tei:listPerson/tei:person', ns
    )
    if not person_elems:
        person_elems = root.findall('.//profileDesc/particDesc/listPerson/person')
    
    if person_elems:
        # Buscar el primero con @role='author' o el primero en general
        for person in person_elems:
            if person.get('role') == 'author':
                name_elem = person.find('.//tei:name', ns) or person.find('.//name')
                if name_elem is not None and name_elem.text:
                    return name_elem.text.strip(), 'low', None
        
        # Si no hay con role, tomar el primero
        name_elem = person_elems[0].find('.//tei:name', ns) or person_elems[0].find('.//name')
        if name_elem is not None and name_elem.text:
            return name_elem.text.strip(), 'low', None
    
    # ===== SI TODO FALLA: None
    return None, None, "No author in titleStmt, respStmt, sourceDesc/bibl, or profileDesc/particDesc"


def infer_author_from_filename(obra_id):
    """Intenta inferir autor desde el obra_id si contiene patrón conocido"""
    obra_id_lower = obra_id.lower()
    
    # Patrones heurísticos conocidos
    if 'castelao' in obra_id_lower or 'cousas' in obra_id_lower:
        return 'Alfonso R. Castelao'  # Author raw (será normalizado después)
    
    # Si no hay patrón, None
    return None


def extract_title_from_tei(filepath):
    """Extrae título desde TEI"""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except:
        return None
    
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    title_elem = root.find('.//tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title', ns)
    if title_elem is None:
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
    
    date_elem = root.find('.//tei:teiHeader/tei:fileDesc/tei:publicationStmt/tei:date', ns)
    if date_elem is None:
        date_elem = root.find('.//fileDesc/publicationStmt/date')
    
    if date_elem is not None:
        when = date_elem.get('when')
        if when:
            match = re.match(r'(\d{4})', when)
            if match:
                return int(match.group(1))
    
    return None


def obra_id_from_filename(filename):
    """Genera obra_id desde nombre de archivo (sin .xml)"""
    return filename.replace('.xml', '')


def main():
    parser = argparse.ArgumentParser(description='Extrae metadata desde TEI headers (v2: extendida)')
    parser.add_argument('--tei-dir', required=True, help='Directorio con archivos TEI')
    parser.add_argument('--output', required=True, help='Path output CSV')
    parser.add_argument('--normalization', default='02_methods/patterns/author_normalization.yml',
                        help='Path a archivo de normalización de autores')
    
    args = parser.parse_args()
    
    tei_dir = Path(args.tei_dir)
    output_path = Path(args.output)
    
    if not tei_dir.exists():
        print(f"❌ ERROR: Directorio no existe: {tei_dir}")
        exit(1)
    
    # Cargar reglas de normalización
    normalization_rules = load_author_normalization(args.normalization)
    
    # Encontrar archivos XML
    xml_files = sorted(tei_dir.glob('*.xml'))
    print(f"📂 Encontrados {len(xml_files)} archivos TEI")
    
    metadata = []
    n_with_author_tei = 0
    n_with_author_inferred = 0
    n_without_author = 0
    
    for xml_file in xml_files:
        obra_id = obra_id_from_filename(xml_file.name)
        title = extract_title_from_tei(xml_file)
        author_raw, confidence, why_missing = extract_author_from_tei_extended(xml_file)
        year = extract_year_from_tei(xml_file)
        
        # ===== Si no encontrado en TEI: intentar inferencia
        if author_raw is None:
            author_raw_inferred = infer_author_from_filename(obra_id)
            if author_raw_inferred:
                author_raw = author_raw_inferred
                confidence = 'low_inferred'
                why_missing = f"Not found in TEI header; inferred from filename: {obra_id}"
                n_with_author_inferred += 1
            else:
                # No TIE, No inferencia: marcar missing
                confidence = 'missing'
                why_missing = f"Not found in TEI (titleStmt/respStmt/sourceDesc/profileDesc); no filename pattern matched"
                n_without_author += 1
        else:
            n_with_author_tei += 1
        
        # ===== Normalizar autor
        author_normalized = normalize_author(author_raw, normalization_rules) if author_raw else None
        author_norm_key = slugify(author_normalized) if author_normalized else None
        
        metadata.append({
            'obra_id': obra_id,
            'title': title,
            'author_raw': author_raw,
            'author_normalized': author_normalized,
            'author_norm_key': author_norm_key,
            'year': year,
            'source_file': xml_file.name,
            'author_confidence': confidence,
            'why_missing': why_missing
        })
    
    # Crear DataFrame
    df = pd.DataFrame(metadata)
    
    # Guardar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"\n✅ Metadata extraída (v2): {output_path}")
    print(f"\n📊 Resumen:")
    print(f"   Total TEI: {len(xml_files)}")
    print(f"   Con autor TEI: {n_with_author_tei}")
    print(f"   Autor inferido: {n_with_author_inferred}")
    print(f"   Sin autor: {n_without_author}")
    print(f"   TOTAL con autor: {n_with_author_tei + n_with_author_inferred} ({(n_with_author_tei + n_with_author_inferred) / len(xml_files) * 100:.1f}%)")
    
    # Mostrar top autores normalizados
    print(f"\n🔝 Top autores normalizados:")
    author_counts = df[df['author_normalized'].notna()]['author_normalized'].value_counts().head(10)
    for author, count in author_counts.items():
        print(f"   {author}: {count} obras")
    
    # Obras sin autor
    if n_without_author > 0:
        print(f"\n⚠️  Obras sin autor ({n_without_author}):")
        unknown = df[df['author_confidence'] == 'missing'][['obra_id', 'title', 'why_missing']]
        for _, row in unknown.iterrows():
            print(f"   - {row['obra_id']}: {row['why_missing']}")
    
    # Obras con author inferido
    if n_with_author_inferred > 0:
        print(f"\n🔎 Obras con autor inferido ({n_with_author_inferred}):")
        inferred = df[df['author_confidence'] == 'low_inferred'][['obra_id', 'author_raw', 'why_missing']]
        for _, row in inferred.iterrows():
            print(f"   - {row['obra_id']}: {row['author_raw']} ({row['why_missing']})")


if __name__ == '__main__':
    main()

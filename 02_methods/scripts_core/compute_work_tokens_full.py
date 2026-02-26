#!/usr/bin/env python3
"""
compute_work_tokens_full.py
Calcula tokens_total_full extrayendo texto completo desde tei:body (TEI XML).
No usa units.csv snippets; utiliza cuerpo completo del documento.

BUGFIX: castelao_cousas_tei_v2 tenía tokens truncados (707); esto corrige eso.
"""

import pandas as pd
from pathlib import Path
from lxml import etree
import re
from collections import defaultdict

TEI_DIR = Path(__file__).parent.parent.parent / "01_data" / "tei" / "source"
OUTPUTS_DIR = Path(__file__).parent.parent.parent / "04_outputs" / "tables"
METADATA_FILE = OUTPUTS_DIR / "works_metadata_from_tei.csv"

# Namespaces
NSMAP = {
    'tei': 'http://www.tei-c.org/ns/1.0'
}

def obra_id_from_filename(filename: str) -> str:
    """Convierte nombre TEI a obra_id."""
    # E.g., "castelao_cousas_tei_v2.xml" -> "castelao_cousas_tei_v2"
    return filename.replace('.xml', '').replace('.tei.xml', '')

def extract_fulltext_from_tei(tei_file: Path) -> str:
    """Extrae texto completo del elemento tei:body, ignorando elementos no textuales."""
    try:
        tree = etree.parse(str(tei_file))
        root = tree.getroot()
        
        # Buscar tei:body
        body = root.find('.//tei:body', NSMAP)
        if body is None:
            # Fallback: si no hay body, usar todo
            body = root
        
        # Extraer texto: iterar sobre elementos, saltando elementos no textuales
        texts = []
        for elem in body.iter():
            # Saltar elementos que no contienen texto
            if elem.tag in [
                '{http://www.tei-c.org/ns/1.0}pb',
                '{http://www.tei-c.org/ns/1.0}milestone',
                '{http://www.tei-c.org/ns/1.0}note',
                '{http://www.tei-c.org/ns/1.0}ref',
                '{http://www.tei-c.org/ns/1.0}ptr',
                '{http://www.tei-c.org/ns/1.0}gap',
            ]:
                continue
            
            # Agregar texto del elemento
            if elem.text:
                texts.append(elem.text)
            
            # Agregar tail (texto después del elemento)
            if elem.tail:
                texts.append(elem.tail)
        
        fulltext = ' '.join(texts)
        
        # Limpieza: múltiples espacios
        fulltext = re.sub(r'\s+', ' ', fulltext).strip()
        
        return fulltext
    except Exception as e:
        print(f"  [warning] Error parsing {tei_file.name}: {e}")
        return ""

def tokenize(text: str) -> int:
    """Cuenta tokens (palabras)."""
    if not text:
        return 0
    
    # Tokenización simple: palabras separadas por espacios
    tokens = text.split()
    return len(tokens)

def main():
    """Calcula tokens_total_full para cada obra."""
    print("\n" + "="*70)
    print("COMPUTE_WORK_TOKENS_FULL: Extrae tokens desde TEI completo")
    print("="*70 + "\n")
    
    # Cargar metadatos para obtener mapeo source_file -> obra_id
    metadata = pd.read_csv(METADATA_FILE)
    filename_to_obra_id = dict(zip(metadata['source_file'], metadata['obra_id']))
    
    print(f"[metadata] Cargados {len(metadata)} obras desde works_metadata_from_tei.csv\n")
    
    # Iterar sobre TEI files (deduplicar .tei.xml capturados por *.xml)
    tei_files = sorted(set(TEI_DIR.glob("*.xml")) | set(TEI_DIR.glob("*.tei.xml")))
    
    results = []
    
    print(f"[tei] Procesando {len(tei_files)} archivos TEI from {TEI_DIR}...\n")
    
    for tei_file in tei_files:
        # Obtener obra_id
        obra_id = filename_to_obra_id.get(tei_file.name)
        if not obra_id:
            print(f"  [warning] {tei_file.name} no encontrado en metadata")
            continue
        
        # Extraer texto completo
        fulltext = extract_fulltext_from_tei(tei_file)
        
        # Contar tokens
        tokens_total_full = tokenize(fulltext)
        chars_total_full = len(fulltext)
        
        results.append({
            'obra_id': obra_id,
            'tokens_total_full': tokens_total_full,
            'chars_total_full': chars_total_full,
            'tokens_source': 'fulltext_tei'
        })
        
        # Print progress
        if tokens_total_full < 1000:
            print(f"  ⚠️  {obra_id}: {tokens_total_full} tokens (bajo)")
        elif tokens_total_full > 500000:
            print(f"  📊 {obra_id}: {tokens_total_full} tokens (muy alto)")
    
    # Crear DataFrame y salvar
    df = pd.DataFrame(results)
    df = df.sort_values('obra_id').reset_index(drop=True)
    
    output_file = OUTPUTS_DIR / "work_tokens_full.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ work_tokens_full.csv guardado: {output_file}\n")
    
    # Estadísticas
    print("="*70)
    print("ESTADÍSTICAS:")
    print(f"  - Total obras procesadas: {len(df)}")
    print(f"  - Tokens min: {df['tokens_total_full'].min()}")
    print(f"  - Tokens max: {df['tokens_total_full'].max()}")
    print(f"  - Tokens media: {df['tokens_total_full'].mean():.0f}")
    print(f"  - Obras <1000 tokens: {(df['tokens_total_full'] < 1000).sum()}")
    print("="*70 + "\n")
    
    # Mostrar obras con tokens muy bajos
    low_token_works = df[df['tokens_total_full'] < 1000].sort_values('tokens_total_full')
    if len(low_token_works) > 0:
        print("Obras con tokens < 1000 (probables truncados o muy breves):")
        print(low_token_works.to_string(index=False))
        print()

if __name__ == "__main__":
    main()

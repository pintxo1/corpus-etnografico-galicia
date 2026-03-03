#!/usr/bin/env python3
"""Extract negative cases from TEI corpus without emigrant mentions."""
import xml.etree.ElementTree as ET
import re
import pandas as pd
import os
import sys

# Change to repo root
os.chdir('/Users/Pintxo/corpus-etnografico-galicia')

# Definir obras sin menciones
negative_works_meta = {
    'cara_de_plata_001': {'author': 'Valle-Inclán, Ramón del', 'year': 1923, 'decade': '1920s'},
    'castelao_cousas_tei_v2': {'author': 'Castelao, Alfonso Rodríguez', 'year': 1926, 'decade': '1920s'},
    'el_quinto': {'author': 'Pardo Bazán, Emilia', 'year': 1895, 'decade': '1890s'},
    'la_danza_del_peregrino': {'author': 'Pardo Bazán, Emilia', 'year': 1916, 'decade': '1910s'},
    'la_flor_seca': {'author': 'Pardo Bazán, Emilia', 'year': 1893, 'decade': '1890s'},
    'testigo_irrecusable': {'author': 'Pardo Bazán, Emilia', 'year': 1916, 'decade': '1910s'}
}

# Keywords de escena limítrofe
keywords = [
    "barco", "vapor", "vap", "buque", "embarc", "porto", "puerto", "Havana", "Habana", 
    "América", "ultramar", "Buenos Aires", "Montevideo", "pasaporte", "billete", "carta", 
    "remesa", "dólar", "peseta", "retorno", "volver", "ida", "viaxe", "viajar", "marchar", 
    "partir", "voyage", "traverser", "volta", "galera", "transatlántico", "adeus"
]

tei_source = '01_data/tei/source'
corpus = pd.read_csv('04_outputs/tables/corpus_master_table_v2tokens.csv')

candidates = []

for obra_id, meta in negative_works_meta.items():
    tei_file = f'{tei_source}/{obra_id}.xml'
    
    # Obtener tokens_total del corpus
    corpus_row = corpus[corpus['obra_id'] == obra_id].iloc[0]
    tokens_total = int(corpus_row['tokens_total'])
    
    # Leer TEI
    try:
        tree = ET.parse(tei_file)
        root = tree.getroot()
        
        # Extraer namespace
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'} if 'http://www.tei-c.org/ns/1.0' in root.tag else {}
        
        # Buscar body
        if ns:
            body_elem = root.find('.//tei:body', ns)
        else:
            body_elem = root.find('.//body')
        
        if body_elem is None:
            print(f"✗ {obra_id}: No body element found")
            continue
        
        # Extraer texto limpio
        text = ''.join(body_elem.itertext())
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Buscar keywords
        found_keywords = {}
        for kw in keywords:
            pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(text))
            if matches:
                found_keywords[kw] = len(matches)
        
        if found_keywords:
            # Tomar el keyword con mayor frecuencia
            best_kw = max(found_keywords.items(), key=lambda x: x[1])[0]
            count = found_keywords[best_kw]
            
            # Extraer fragmento
            pattern = re.compile(r'\b' + re.escape(best_kw) + r'\b', re.IGNORECASE)
            match = pattern.search(text)
            
            if match:
                start = match.start()
                # Retroceder ~75-100 palabras
                words_before = text[:start].split()[-100:]
                start_pos = len(text[:start]) - len(' '.join(words_before))
                
                # Avanzar ~75-100 palabras
                words_after = text[match.end():].split()[:100]
                end_pos = match.end() + len(' '.join(words_after))
                
                fragment = text[start_pos:end_pos].strip()
                fragment = ' '.join(fragment.split())
                
                candidates.append({
                    'obra_id': obra_id,
                    'author': meta['author'],
                    'year': meta['year'],
                    'decade': meta['decade'],
                    'tokens_total': tokens_total,
                    'n_emigrant_mentions': 0,
                    'best_keyword': best_kw,
                    'keyword_count': count,
                    'other_keywords': ' | '.join(sorted([k for k in found_keywords.keys() if k != best_kw])[:5]),
                    'fragment_length': len(fragment.split()),
                    'tei_file': tei_file,
                    'fragment': fragment
                })
                
                print(f"✓ {obra_id}: {len(found_keywords)} keywords | '{best_kw}' ({count}x)")
            else:
                print(f"⚠ {obra_id}: Keyword found but no match")
        else:
            print(f"✗ {obra_id}: No keywords found")
    
    except Exception as e:
        print(f"✗ {obra_id}: Error: {str(e)}")

# Mostrar resumen
print(f"\n\nResumen: {len(candidates)} candidatas encontradas de 6 obras\n")
for c in candidates:
    print(f"{c['obra_id']}")
    print(f"  Keywords: {len(c['other_keywords'].split('|')) + 1} total | Mejor: '{c['best_keyword']}' ({c['keyword_count']}x)")
    print(f"  Fragment: {c['fragment_length']} palabras | Path: {c['tei_file']}")
    print()

# Guardar tabla de candidatos
if candidates:
    os.makedirs('04_outputs/case_cards', exist_ok=True)
    
    # Tabla sin fragmentos
    df = pd.DataFrame(candidates)
    df_table = df.drop('fragment', axis=1)
    df_table.to_csv('04_outputs/case_cards/negative_candidates_table.csv', index=False)
    print(f"\n✓ Tabla guardada: 04_outputs/case_cards/negative_candidates_table.csv")
    
    # También guardar candidatos en memoria para el siguiente paso
    import json
    with open('04_outputs/case_cards/_candidates.json', 'w') as f:
        json.dump(candidates, f, indent=2)
else:
    print("\n✗ No candidates found")

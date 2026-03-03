#!/usr/bin/env python3
"""Validate all negative candidates against emigrant markers."""
import xml.etree.ElementTree as ET
import re
import yaml
import pandas as pd
from collections import defaultdict
import os

os.chdir('/Users/Pintxo/corpus-etnografico-galicia')

# Load emigrant markers
with open('02_methods/patterns/emigrante_markers.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

markers = config['markers']
marker_list = [(m.get('marker', '').strip(), m.get('marker', '').strip()) for m in markers if m.get('marker')]

# Load negative candidates
candidates_data = pd.read_csv('04_outputs/case_cards/negative_candidates_table.csv')

print(f"{'='*80}")
print(f"VALIDACIÓN DE TODOS LOS CANDIDATOS NEGATIVOS")
print(f"{'='*80}\n")

validation_results = []

for idx, row in candidates_data.iterrows():
    obra_id = row['obra_id']
    tei_file = row['tei_file']
    
    print(f"\n[{idx+1}/{len(candidates_data)}] Validando: {obra_id}")
    print(f"{'─'*80}")
    
    # Extract TEI text
    try:
        tree = ET.parse(tei_file)
        root = tree.getroot()
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'} if 'http://www.tei-c.org/ns/1.0' in root.tag else {}
        body_elem = root.find('.//tei:body', ns) if ns else root.find('.//body')
        
        if body_elem is None:
            print(f"  ✗ No body element found")
            validation_results.append({
                'obra_id': obra_id,
                'valid_negative': False,
                'reason': 'No TEI body found',
                'emigrant_hits': -1,
                'markers_hit': ''
            })
            continue
        
        fulltext = ' '.join(body_elem.itertext())
        fulltext = re.sub(r'\s+', ' ', fulltext).strip()
        
        # Search for markers
        total_hits = 0
        markers_hit = []
        
        for marker_name, pattern in marker_list:
            try:
                regex_pattern = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
            except:
                try:
                    regex_pattern = re.compile(pattern, re.IGNORECASE)
                except:
                    continue
            
            matches = list(regex_pattern.finditer(fulltext))
            if matches:
                total_hits += len(matches)
                markers_hit.append(f"{marker_name}({len(matches)})")
        
        is_negative = total_hits == 0
        status = "✓ VALID" if is_negative else "✗ NOT NEGATIVE"
        markers_str = ', '.join(markers_hit) if markers_hit else 'NONE'
        
        print(f"  {status}: {total_hits} emigrant marker hits")
        if markers_hit:
            print(f"    Markers: {markers_str}")
        
        validation_results.append({
            'obra_id': obra_id,
            'valid_negative': is_negative,
            'reason': 'No emigrant markers' if is_negative else f'{total_hits} markers found',
            'emigrant_hits': total_hits,
            'markers_hit': markers_str
        })
    
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        validation_results.append({
            'obra_id': obra_id,
            'valid_negative': False,
            'reason': f'Error: {str(e)}',
            'emigrant_hits': -1,
            'markers_hit': ''
        })

# Summary
print(f"\n{'='*80}")
print("RESUMEN DE VALIDACIÓN")
print(f"{'='*80}\n")

results_df = pd.DataFrame(validation_results)
valid_negatives = results_df[results_df['valid_negative']]

print(f"Total candidatos: {len(results_df)}")
print(f"Negativos válidos: {len(valid_negatives)}")
print(f"NO negativos: {len(results_df) - len(valid_negatives)}\n")

print("Resultados detallados:")
for idx, row in results_df.iterrows():
    status = "✓" if row['valid_negative'] else "✗"
    print(f"{status} {row['obra_id']:<40} | hits: {row['emigrant_hits']:>2} | {row['reason']}")

# Save results
results_df.to_csv('04_outputs/case_cards/validation_all_candidates.csv', index=False)
print(f"\n✓ Validation results saved to: 04_outputs/case_cards/validation_all_candidates.csv")

# Select best valid negative
if len(valid_negatives) > 0:
    best_negative = valid_negatives.iloc[0]['obra_id']
    print(f"\n✅ BEST VALID NEGATIVE: {best_negative}")
    print(f"   (Will use for case_negative_v2.md)")
else:
    print(f"\n❌ NO VALID NEGATIVES FOUND!")
    print(f"   All candidates contain emigrant markers.")


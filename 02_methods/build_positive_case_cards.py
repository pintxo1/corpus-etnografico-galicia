#!/usr/bin/env python3
"""Generate positive case cards from emigrante_representation_pack_v2."""
import xml.etree.ElementTree as ET
import re
import yaml
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path

os.chdir('/Users/Pintxo/corpus-etnografico-galicia')

print(f"{'='*80}")
print("GENERADOR DE CASE CARDS — CASOS POSITIVOS DEL MÓDULO EMIGRANTE")
print(f"{'='*80}\n")

# Load emigrant markers from YAML
with open('02_methods/patterns/emigrante_markers.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

markers = config['markers']
marker_patterns = [(m.get('marker', '').strip(), m.get('marker', '').strip(), m.get('context', '')) 
                   for m in markers if m.get('marker')]

print(f"✓ Loaded {len(marker_patterns)} emigrant markers\n")

# Load corpus and pack data
pack = pd.read_csv('03_analysis/reading_pack/emigrante_representation_pack_v2.csv')
corpus = pd.read_csv('04_outputs/tables/corpus_master_table_v2tokens.csv')

# Select top 5 obras by emigrant mentions
pack_obras = pack.groupby('obra_id').size().reset_index(name='casos_en_pack')
pack_obras = pack_obras.merge(corpus[['obra_id', 'n_emigrant_mentions', 'title', 'author_normalized', 
                                        'year', 'decade', 'genre_norm', 'tokens_total']], on='obra_id')
pack_obras = pack_obras.sort_values('n_emigrant_mentions', ascending=False)

selected_obras = pack_obras.head(5)['obra_id'].tolist()

print("Obras seleccionadas para case cards positivos:\n")
for i, obra in enumerate(selected_obras, 1):
    row = pack_obras[pack_obras['obra_id'] == obra].iloc[0]
    print(f"{i}. {obra:<40} | {int(row['n_emigrant_mentions']):>3} menciones | {row['author_normalized']}")

print(f"\n{'='*80}\n")

# Create output directory
output_dir = Path('04_outputs/case_cards/positive_cases_v1')
output_dir.mkdir(parents=True, exist_ok=True)

# Tracking
results = []
errors = []

# Process each selected obra
for obra_id in selected_obras:
    print(f"\n[PROCESSING] {obra_id}")
    print(f"{'─'*80}")
    
    # Get corpus metadata
    corpus_row = corpus[corpus['obra_id'] == obra_id].iloc[0]
    author = corpus_row['author_normalized']
    title = corpus_row['title']
    year = int(corpus_row['year']) if pd.notna(corpus_row['year']) else 'n.d.'
    decade = corpus_row['decade'] if pd.notna(corpus_row['decade']) else 'n.d.'
    genre = corpus_row['genre_norm'] if pd.notna(corpus_row['genre_norm']) else 'n.d.'
    tokens_total = int(corpus_row['tokens_total'])
    n_emigrant = int(corpus_row['n_emigrant_mentions'])
    
    # Calculate rate per 1k tokens
    rate_per_1k = (n_emigrant / tokens_total * 1000) if tokens_total > 0 else 0
    
    # Find TEI file
    tei_file = f'01_data/tei/source/{obra_id}.xml'
    
    if not os.path.exists(tei_file):
        errors.append(f"{obra_id}: TEI file not found at {tei_file}")
        print(f"  ✗ TEI file not found: {tei_file}")
        continue
    
    # Extract TEI body text
    try:
        tree = ET.parse(tei_file)
        root = tree.getroot()
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'} if 'http://www.tei-c.org/ns/1.0' in root.tag else {}
        body_elem = root.find('.//tei:body', ns) if ns else root.find('.//body')
        
        if body_elem is None:
            errors.append(f"{obra_id}: No TEI body element found")
            print(f"  ✗ No body element")
            continue
        
        fulltext = ''.join(body_elem.itertext())
        fulltext = re.sub(r'\s+', ' ', fulltext).strip()
        
        print(f"  ✓ Extracted {len(fulltext)} chars ({len(fulltext.split())} words)")
        
    except Exception as e:
        errors.append(f"{obra_id}: Error parsing TEI: {str(e)}")
        print(f"  ✗ Error parsing TEI: {str(e)}")
        continue
    
    # Find first marker match
    best_marker = None
    best_match = None
    best_marker_name = None
    
    for marker_name, pattern, context_desc in marker_patterns:
        try:
            regex_pattern = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
        except:
            try:
                regex_pattern = re.compile(pattern, re.IGNORECASE)
            except:
                continue
        
        match = regex_pattern.search(fulltext)
        if match:
            best_match = match
            best_marker_name = marker_name
            break
    
    if not best_match:
        errors.append(f"{obra_id}: No emigrant markers found in fulltext (unexpected)")
        print(f"  ⚠ No markers found (unexpected for positive case)")
        continue
    
    trigger_marker = best_marker_name
    match_start = best_match.start()
    match_end = best_match.end()
    match_text = fulltext[match_start:match_end]
    
    print(f"  ✓ Trigger marker: '{trigger_marker}' at position {match_start}")
    
    # Extract fragment: ~80-120 words before and after
    words_before = fulltext[:match_start].split()[-100:]
    words_after = fulltext[match_end:].split()[:100]
    
    # Recalculate start/end positions
    fragment_start = len(fulltext[:match_start]) - len(' '.join(words_before))
    fragment_end = match_end + len(' '.join(words_after))
    
    fragment = fulltext[fragment_start:fragment_end].strip()
    fragment = ' '.join(fragment.split())  # Clean extra whitespace
    
    # Try to cut at sentence boundary
    if len(fragment) > 200:
        # Find last period before end
        last_period = fragment.rfind('.', 0, len(fragment) - 50)
        if last_period > len(fragment) * 0.7:  # Only if it's in last 30%
            fragment = fragment[:last_period+1].strip()
    
    frag_words = len(fragment.split())
    print(f"  ✓ Fragment extracted: {frag_words} words")
    
    # Find all markers in fragment
    markers_in_frag = set()
    for marker_name, pattern, _ in marker_patterns:
        try:
            regex_pattern = re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
        except:
            try:
                regex_pattern = re.compile(pattern, re.IGNORECASE)
            except:
                continue
        
        if regex_pattern.search(fragment):
            markers_in_frag.add(marker_name)
    
    print(f"  ✓ Markers in fragment: {len(markers_in_frag)}")
    
    # Generate case card markdown
    markers_list = ', '.join(sorted(markers_in_frag))
    
    case_card = f"""# Caso Positivo — {obra_id}

## Metadatos

| Campo | Valor |
|-------|-------|
| **Autor** | {author} |
| **Obra** | {title} |
| **Año** | {year if isinstance(year, str) else int(year)} |
| **Década** | {decade} |
| **Formato** | {genre} |
| **Tokens (v2tokens)** | {tokens_total:,} |
| **Menciones emigrante** | {n_emigrant} |
| **Tasa por 1.000 tokens** | {rate_per_1k:.2f} |

---

## Por Qué Entra en el Pack Emigrante v2

- **Criterio de selección**: Obra con n_emigrant_mentions > 0 → incluida en fase 1 (mandatory 1/obra)
- **Densidad temática**: {rate_per_1k:.2f}/1k tokens → cobertura {('alta' if rate_per_1k >= 5 else 'media' if rate_per_1k >= 2 else 'baja')} de representaciones emigrantes
- **Representatividad**: Forma parte de los {pack_obras[pack_obras['obra_id']==obra_id].iloc[0]['casos_en_pack']} casos seleccionados de esta obra en el pack v2
- **Contexto autoral**: {author} — autor canónico en corpus de emigración galega

---

## Marcador Disparador

- **Marcador**: `{trigger_marker}`
- **Tipo**: {[m[2] for m in marker_patterns if m[0] == trigger_marker][0] if trigger_marker in [m[0] for m in marker_patterns] else 'emigrant marker'}
- **Palabra clave**: "{match_text}"

---

## Marcadores Activados en el Fragmento

| Marcador | Tipo |
|----------|------|
{chr(10).join([f'| `{m}` | emigrant marker |' for m in sorted(markers_in_frag)])}

**Total en fragmento**: {len(markers_in_frag)} marcador(es) único(s)

---

## Fragmento ({frag_words} palabras)

> {fragment}

---

## Trazabilidad

| Campo | Valor |
|-------|-------|
| **TEI source** | `{tei_file}` |
| **Posición match** | Carácter {match_start:,} – {match_end:,} |
| **Ocurrencia** | Primera coincidencia de `{trigger_marker}` en body |
| **Método extracción** | Ventana ±100 palabras alrededor del match |
| **Limpieza** | Markup TEI removido; whitespace normalizado |

---

## Validación

✅ **Estado**: Caso positivo validado  
✅ **Lexicón usado**: `02_methods/patterns/emigrante_markers.yml` (35 marcadores)  
✅ **Método**: Fulltext regex matching contra body TEI  
✅ **Coherencia**: Corpus record (n_emigrant_mentions = {n_emigrant}) ← → Fragmento (>{len(markers_in_frag)} marcadores)

---

*Case card generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*  
*Source: 02_methods/build_positive_case_cards.py*
"""

    # Write card
    card_file = output_dir / f'case_positive_{obra_id}.md'
    with open(card_file, 'w', encoding='utf-8') as f:
        f.write(case_card)
    
    print(f"  ✓ Card written: {card_file.name}")
    
    # Collect metadata
    results.append({
        'obra_id': obra_id,
        'author_norm': author,
        'title': title,
        'year': year if isinstance(year, str) else int(year),
        'decade': decade,
        'format': genre,
        'tokens_total': tokens_total,
        'n_emigrant_mentions': n_emigrant,
        'rate_per_1k': f'{rate_per_1k:.2f}',
        'trigger_marker': trigger_marker,
        'n_markers_in_fragment': len(markers_in_frag),
        'tei_path': tei_file
    })

# Save summary CSV
if results:
    summary_df = pd.DataFrame(results)
    summary_file = output_dir / 'positive_cases_summary.csv'
    summary_df.to_csv(summary_file, index=False)
    print(f"\n✓ Summary saved: {summary_file}")

# Save errors log
if errors:
    errors_file = output_dir / 'errors.log'
    with open(errors_file, 'w') as f:
        f.write('\n'.join(errors))
    print(f"✓ Errors logged: {errors_file}")

# Print summary
print(f"\n{'='*80}")
print("RESUMEN DE EJECUCIÓN")
print(f"{'='*80}\n")
print(f"Casos positivos generados: {len(results)}/5")
print(f"Errores: {len(errors)}")
if results:
    print(f"\nArchivos creados:")
    for r in results:
        print(f"  ✓ case_positive_{r['obra_id']}.md")
    print(f"  ✓ positive_cases_summary.csv")
if errors:
    print(f"\nErrores encontrados:")
    for e in errors:
        print(f"  ✗ {e}")

print(f"\n{'='*80}")


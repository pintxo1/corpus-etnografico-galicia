#!/usr/bin/env python3
"""
update_emigrant_pack_v2.py
Actualiza emigrante_representation_pack.csv con:
- Validación de cuotas por autor y década
- Marcado explícito de NEGATIVE controls
- Generación de fichas MD para análisis

Fase 11: Evidence Pack v2
"""

import argparse
import pandas as pd
from pathlib import Path
from collections import defaultdict
import hashlib

READINGS_DIR = Path(__file__).parent.parent.parent / "03_analysis" / "reading_pack"
TABLES_DIR = Path(__file__).parent.parent.parent / "04_outputs" / "tables"
CASES_DIR = Path(__file__).parent.parent.parent / "03_analysis" / "cases"

def load_pack(pack_file: Path) -> pd.DataFrame:
    """Carga pack existente."""
    df = pd.read_csv(pack_file)
    print(f"[pack] Cargados {len(df)} casos")
    return df

def load_master_table(master_file: Path) -> pd.DataFrame:
    """Carga tabla maestra."""
    df = pd.read_csv(master_file)
    return df

def load_kwic_cases() -> pd.DataFrame:
    """Carga casos KWIC emigrante."""
    kwic_file = CASES_DIR / "emigrante_kwic_cases.csv"
    if kwic_file.exists():
        df = pd.read_csv(kwic_file)
        return df
    return pd.DataFrame()

def enrich_pack_with_metadata(pack: pd.DataFrame, master: pd.DataFrame) -> pd.DataFrame:
    """Enriquece pack con metadata de master table."""
    # El pack ya tiene author_normalized y year; solo agregar decade y otras columnas
    pack_enriched = pack.copy()
    
    # Hacer merge solo para columnas que falten
    master_for_merge = master[['obra_id', 'decade', 'n_emigrant_mentions']].copy()
    
    pack_enriched = pack_enriched.merge(
        master_for_merge,
        on='obra_id',
        how='left',
        suffixes=('', '_master')
    )
    
    # Si no hay 'decade' en pack, esta vendrá del master
    print(f"[enrich] Pack enriquecido con metadata")
    return pack_enriched

def analyze_quotas(pack: pd.DataFrame, master: pd.DataFrame) -> dict:
    """Analiza cuotas por autor y década."""
    stats = {
        'by_author': defaultdict(int),
        'by_decade': defaultdict(int),
        'negative': 0,
        'total': len(pack)
    }
    
    for _, row in pack.iterrows():
        if pd.notna(row.get('author_normalized')):
            stats['by_author'][row['author_normalized']] += 1
        if pd.notna(row.get('decade')) and row['decade'] != 'unknown_year':
            stats['by_decade'][row['decade']] += 1
        
        # Detectar negativos (obras sin menciones emigrante o explícitamente marcadas)
        if row.get('n_emigrant_mentions', 0) == 0 or str(row.get('type', '')).upper() == 'NEGATIVE':
            stats['negative'] += 1
    
    return stats

def validate_pack(pack: pd.DataFrame, master: pd.DataFrame) -> dict:
    """Valida conformidad del pack."""
    # Contar obras únicas por autor
    authors_in_pack = pack['author_normalized'].nunique()
    authors_in_corpus = master['author_normalized'].nunique()
    
    # Contar décadas
    decades_in_pack = pack[pack['decade'] != 'unknown_year']['decade'].nunique()
    decades_in_corpus = master[master['decade'] != 'unknown_year']['decade'].nunique()
    
    # Casos por autor
    author_coverage = pack.groupby('author_normalized').size().to_dict()
    
    return {
        'authors_in_pack': authors_in_pack,
        'authors_in_corpus': authors_in_corpus,
        'decades_in_pack': decades_in_pack,
        'decades_in_corpus': decades_in_corpus,
        'author_coverage': author_coverage,
        'total_cases': len(pack),
        'negative_count': (pack.get('type', '') == 'NEGATIVE').sum() if 'type' in pack.columns else 0
    }

def generate_case_cards(pack: pd.DataFrame, kwic: pd.DataFrame):
    """Genera fichas MD para cada caso del pack."""
    CARDS_DIR = READINGS_DIR / "emigrante_representation_pack_v2" / "cases"
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    
    card_count = 0
    for idx, case in pack.iterrows():
        case_id = case['case_id'] if 'case_id' in case else f"case_{idx:04d}"
        
        # Buscar KWIC si existe
        kwic_context = ""
        if not kwic.empty and 'case_id' in kwic.columns:
            kwic_match = kwic[kwic['case_id'] == case_id]
            if not kwic_match.empty:
                row = kwic_match.iloc[0]
                kwic_context = f"\n## KWIC (Contexto)\n\n{row.get('context_left', '')} **[{row.get('marker', 'N/A')}]** {row.get('context_right', '')}\n"
        
        # Generar ficha
        card_md = f"""# Caso: {case_id}

## Metadatos
- **Obra**: {case.get('obra_id', 'N/A')}
- **Autor**: {case.get('author_normalized', 'N/A')}
- **Año**: {case.get('year', 'N/A')}
- **Década**: {case.get('decade', 'N/A')}
- **Unidad**: {case.get('unidad_id', 'N/A')}
- **Tipo**: {case.get('type', 'NORMAL')}

## Texto
{case.get('text', 'N/A')}

{kwic_context}

## Anotación (vacío para llenar)

### Representación del emigrante
- **Presente**: [ ] Sí / [ ] No
- **Protagonista**: [ ] Sí / [ ] No
- **Tema central**: [ ] Sí / [ ] No

### Aspecto emigrante
- Emigración de: [ ] Galiza / [ ] España / [ ] Indeterminada
- Destino principal: _____________________
- Motivación: _____________________
- Resultado: _____________________

### Observaciones
_____________________

---
*Caso {idx+1}/{len(pack)}*
"""
        
        card_file = CARDS_DIR / f"{case_id}.md"
        card_file.write_text(card_md, encoding='utf-8')
        card_count += 1
    
    print(f"[cards] Generadas {card_count} fichas de anotación en {CARDS_DIR}")

def main():
    """Ejecuta actualización del pack v2."""
    parser = argparse.ArgumentParser(description="Actualiza emigrante_representation_pack_v2")
    parser.add_argument(
        "--pack-input",
        default=str(READINGS_DIR / "emigrante_representation_pack.csv"),
        help="Ruta a pack base"
    )
    parser.add_argument(
        "--master-table",
        default=str(TABLES_DIR / "corpus_master_table.csv"),
        help="Ruta a tabla maestra"
    )
    parser.add_argument(
        "--pack-output",
        default=str(READINGS_DIR / "emigrante_representation_pack_v2.csv"),
        help="Ruta output para pack v2"
    )
    args = parser.parse_args()
    print("\n" + "="*70)
    print("UPDATE_EMIGRANT_PACK_V2: Validación y enriquecimiento del pack")
    print("="*70 + "\n")
    
    # Cargar datos
    pack = load_pack(Path(args.pack_input))
    master = load_master_table(Path(args.master_table))
    kwic = load_kwic_cases()
    
    # Enriquecer con metadata
    pack_enriched = enrich_pack_with_metadata(pack, master)
    
    # Validar cuotas
    print("\n[validation] Analizando cuotas...")
    stats = analyze_quotas(pack_enriched, master)
    validation = validate_pack(pack_enriched, master)
    
    print(f"  - Casos totales: {stats['total']}")
    print(f"  - Casos negativos: {stats['negative']}")
    print(f"  - Autores representados: {validation['authors_in_pack']}/{validation['authors_in_corpus']}")
    print(f"  - Décadas representadas: {validation['decades_in_pack']}/{validation['decades_in_corpus']}")
    print(f"  - Cobertura por autor:")
    for author, count in sorted(validation['author_coverage'].items(), key=lambda x: x[1], reverse=True):
        print(f"    • {author}: {count} casos")
    
    # Salvar pack enriquecido
    output_file = Path(args.pack_output)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    pack_enriched.to_csv(output_file, index=False)
    print(f"\n✅ {output_file.name} guardado: {output_file}")
    
    # Generar fichas de anotación
    print("\n[cards] Generando fichas de anotación...")
    generate_case_cards(pack_enriched, kwic)
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()

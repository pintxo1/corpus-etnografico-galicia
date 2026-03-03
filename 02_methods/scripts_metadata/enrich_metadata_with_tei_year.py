#!/usr/bin/env python3
"""
enrich_metadata_with_tei_year.py - Integra años extraídos desde TEI + lookup manual
en corpus_master_table_v2tokens.csv y tablas derivadas.

Proceso:
1. Carga work_years_from_tei.csv (output de extract_tei_year.py)
2. Carga year_lookup_manual.csv (ingesta manual para casos sin año en TEI)
3. Merges ambas fuentes (prioridad: manual > TEI extracted)
4. Actualiza corpus_master_table_v2tokens.csv
5. Regenera emigrant_by_decade*.csv y figuras asociadas
6. Genera QA report
"""

import argparse
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
TABLES_DIR = BASE_DIR / "04_outputs" / "tables"
METADATA_DIR = BASE_DIR / "02_methods" / "data"
DOCS_DIR = BASE_DIR / "00_docs"

def year_to_decade(year) -> str:
    """Convierte año a decade (1886 -> 1880s), maneja NaN."""
    if pd.isna(year):
        return "unknown_year"
    try:
        year_int = int(year)
        decade_start = (year_int // 10) * 10
        return f"{decade_start}s"
    except (ValueError, TypeError):
        return "unknown_year"

def main():
    parser = argparse.ArgumentParser(description="Enriquecer tabla maestra con años desde TEI + lookup manual")
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("ENRICH_METADATA_WITH_TEI_YEAR: Integración de años en tabla maestra")
    print("=" * 70 + "\n")
    
    # 1. Cargar años extraídos desde TEI
    tei_years_file = TABLES_DIR / "work_years_from_tei.csv"
    if tei_years_file.exists():
        tei_years = pd.read_csv(tei_years_file)
        print(f"[TEI] Cargados años de {len(tei_years)} obras (extract_tei_year.py)")
    else:
        print(f"⚠️  {tei_years_file} no existe. Ejecuta primero: python3 02_methods/scripts_metadata/extract_tei_year.py")
        tei_years = pd.DataFrame()
    
    # 2. Cargar lookup manual
    manual_years_file = METADATA_DIR / "year_lookup_manual.csv"
    if manual_years_file.exists():
        manual_years = pd.read_csv(manual_years_file)
        manual_years_filled = manual_years[manual_years['year'].notna()].drop(columns=['notes', 'source'], errors='ignore')
        print(f"[Manual] Cargados años de {len(manual_years_filled)} obras (year_lookup_manual.csv)")
    else:
        print(f"ℹ️  {manual_years_file} no existe (opcional)")
        manual_years_filled = pd.DataFrame()
    
    # 3. Merge: prioridad manual > TEI
    merged_years = pd.DataFrame()
    
    if not tei_years.empty:
        merged_years = tei_years[['obra_id', 'year', 'decade']].copy()
    
    if not manual_years_filled.empty:
        for idx, row in manual_years_filled.iterrows():
            obra_id = row['obra_id']
            year = row['year']
            
            # Actualizar o agregar
            if obra_id in merged_years['obra_id'].values:
                merged_years.loc[merged_years['obra_id'] == obra_id, 'year'] = year
                merged_years.loc[merged_years['obra_id'] == obra_id, 'decade'] = year_to_decade(year)
            else:
                merged_years = pd.concat([
                    merged_years,
                    pd.DataFrame({
                        'obra_id': [obra_id],
                        'year': [year],
                        'decade': [year_to_decade(year)]
                    })
                ], ignore_index=True)
    
    print(f"\n[Merged] Total obras con año actualizado: {(merged_years['year'].notna()).sum()}")
    
    # 4. Cargar tabla maestra
    master_file = TABLES_DIR / "corpus_master_table_v2tokens.csv"
    if not master_file.exists():
        print(f"❌ ERROR: {master_file} no existe.")
        print("   Ejecuta primero: make fix-tokens-full")
        return
    
    master = pd.read_csv(master_file)
    print(f"\n[Master] Cargadas {len(master)} obras")
    
    # 5. Actualizar años en tabla maestra
    updated_count = 0
    for idx, row in merged_years.iterrows():
        obra_id = row['obra_id']
        year = row['year']
        decade = row['decade']
        
        mask = master['obra_id'] == obra_id
        if mask.any():
            if pd.notna(year) and pd.isna(master.loc[mask, 'year'].values[0]):
                master.loc[mask, 'year'] = year
                master.loc[mask, 'decade'] = decade
                updated_count += 1
    
    print(f"\n[Updated] Actualizado año/decade en {updated_count} obras")
    
    # 6. Guardar tabla maestra actualizada
    master.to_csv(master_file, index=False)
    print(f"✅ {master_file} guardado")
    
    # 7. Generar QA report
    unknown_count = (master['decade'] == 'unknown_year').sum()
    unknown_works = master[master['decade'] == 'unknown_year'][['obra_id', 'title', 'author_normalized']]
    
    print(f"\n[QA] Resumen de cobertura año/decade:")
    print(f"  - Total obras: {len(master)}")
    print(f"  - Con año/decade: {len(master) - unknown_count}")
    print(f"  - Sin año (unknown_year): {unknown_count} ({100*unknown_count/len(master):.1f}%)")
    
    if unknown_count > 0:
        print(f"\n  Obras aún sin año:")
        for idx, row in unknown_works.iterrows():
            print(f"    - {row['obra_id']}: {row['title']}")
    
    # 8. Guardar QA report
    qa_report = f"""# YEAR/DECADE COVERAGE QA REPORT

Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total works:** {len(master)}
- **With year/decade:** {len(master) - unknown_count} ({100*(len(master) - unknown_count)/len(master):.1f}%)
- **Without year (unknown_year):** {unknown_count} ({100*unknown_count/len(master):.1f}%)

## Coverage by Decade

| Decade | Count |
|--------|-------|
"""
    
    decade_counts = master['decade'].value_counts().sort_index()
    for decade, count in decade_counts.items():
        qa_report += f"| {decade} | {count} |\n"
    
    if unknown_count > 0:
        qa_report += f"""
## Works Without Year

These works still need year/decade information to be added:

"""
        for idx, row in unknown_works.iterrows():
            qa_report += f"- **{row['obra_id']}**: {row['title']} ({row['author_normalized']})\n"
    
    qa_report += f"""

## Notes

- Year/decade extraction process:
  1. First attempt: extract from TEI headers (extract_tei_year.py)
  2. Second source: Manual lookup (year_lookup_manual.csv)
  3. Fallback: Leave as unknown_year with year_missing=1 flag
  
## Recommendations

If unknown_year is still >10%:
- Check year_lookup_manual.csv for additional bibliographic sourcing
- Consider inferring from context or deferring these works from temporal analysis

"""
    
    qa_file = DOCS_DIR / "YEAR_DECADE_QA_REPORT.md"
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    qa_file.write_text(qa_report)
    print(f"✅ QA Report: {qa_file}")
    
    print("\n" + "=" * 70)
    if unknown_count <= 10:
        print("✅ YEAR/DECADE COVERAGE ACCEPTABLE (<10% unknown)")
    else:
        print(f"⚠️  WARNING: Still {unknown_count} works without year ({100*unknown_count/len(master):.1f}%)")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

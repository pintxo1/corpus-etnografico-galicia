#!/usr/bin/env python3
"""
SCRIPT 01: Análisis Etnográfico Base
Corpus Etnográfico Galicia (1860-1950)

Extrae densidades de 13 categorías etnográficas del corpus TEI.
Output: CSV con métricas por documento y por década.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List
from collections import Counter
import pandas as pd

# Ajustar path para importar utilidades
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from extraer_texto_tei import extraer_texto_tei

# Configuración
BASE_DIR = Path(__file__).parent.parent
TEI_DIR = BASE_DIR / "data" / "tei"
METADATA_FILE = BASE_DIR / "data" / "metadata" / "corpus.csv"
DICCIONARIO_FILE = BASE_DIR / "diccionarios" / "diccionario_etnografico_v1_0_0.json"
OUTPUT_DIR = BASE_DIR / "outputs" / "metricas_etnograficas"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("ANÁLISIS ETNOGRÁFICO BASE - 13 Categorías")
print("=" * 80)
print()


def cargar_diccionario_etnografico(path: Path) -> Dict:
    """Carga diccionario etnográfico desde JSON."""
    print(f"📖 Cargando diccionario: {path.name}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   ✓ Versión: {data['version']}")
    print(f"   ✓ Enfoque: {data['enfoque']}")
    print(f"   ✓ Categorías: {len(data['categories'])}")
    
    return data


def normalizar_texto(texto: str) -> str:
    """Normaliza texto: lowercase y sin acentos."""
    # Lowercase
    texto = texto.lower()
    
    # Eliminar acentos
    acentos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'ñ': 'n', 'ç': 'c'
    }
    for original, reemplazo in acentos.items():
        texto = texto.replace(original, reemplazo)
    
    return texto


def calcular_frecuencias_categoria(texto: str, patterns: List[str]) -> int:
    """
    Calcula frecuencias de una categoría usando regex patterns.
    
    Args:
        texto: Texto normalizado
        patterns: Lista de patrones regex
    
    Returns:
        Total de matches (permite overlaps=False como en diccionario)
    """
    texto_norm = normalizar_texto(texto)
    freq_total = 0
    
    for pattern in patterns:
        matches = re.finditer(pattern, texto_norm)
        freq_total += len(list(matches))
    
    return freq_total


def analizar_documento(tei_file: Path, diccionario: Dict, metadata_row: pd.Series) -> Dict:
    """
    Analiza un documento TEI y extrae métricas etnográficas.
    
    Returns:
        Dict con métricas por categoría
    """
    # Extraer texto TEI
    resultado = extraer_texto_tei(tei_file)
    texto = resultado['texto']
    
    if not texto:
        print(f"   ⚠️  {tei_file.stem}: Texto vacío")
        return None
    
    # Calcular tokens (aproximación)
    tokens = len(texto.split())
    
    # Calcular frecuencias por categoría
    metricas = {
        'doc_id': tei_file.stem,
        'archivo': tei_file.name,
        'titulo': metadata_row.get('title', ''),
        'autor': metadata_row.get('author', ''),
        'year': metadata_row.get('year_first_pub', ''),
        'decada': metadata_row.get('decada_norm', ''),
        'genero': metadata_row.get('genero_macro_normalizado', ''),
        'tokens': tokens
    }
    
    # Iterar sobre categorías
    for cat_name, cat_data in diccionario['categories'].items():
        patterns = cat_data['patterns']
        freq = calcular_frecuencias_categoria(texto, patterns)
        densidad = (freq / tokens) * 10000 if tokens > 0 else 0
        
        metricas[f'{cat_name}_freq'] = freq
        metricas[f'{cat_name}_densidad'] = round(densidad, 2)
    
    return metricas


def main():
    # Cargar diccionario
    diccionario = cargar_diccionario_etnografico(DICCIONARIO_FILE)
    
    # Cargar metadata
    print(f"\n📊 Cargando metadata: {METADATA_FILE.name}")
    metadata = pd.read_csv(METADATA_FILE)
    print(f"   ✓ {len(metadata)} documentos en metadata")
    
    # Verificar TEI directory
    if not TEI_DIR.exists():
        print(f"\n❌ ERROR: Directorio TEI no encontrado: {TEI_DIR}")
        print("   Asegúrate de que el symlink data/tei apunta a corpus-literario/tei/")
        sys.exit(1)
    
    tei_files = list(TEI_DIR.glob("*.xml"))
    print(f"\n📁 Archivos TEI encontrados: {len(tei_files)}")
    
    if len(tei_files) == 0:
        print("❌ ERROR: No se encontraron archivos TEI")
        sys.exit(1)
    
    # Procesar documentos
    print(f"\n🔬 Analizando documentos...")
    print("-" * 80)
    
    resultados = []
    procesados = 0
    errores = 0
    
    for tei_file in tei_files:
        # Buscar metadata
        metadata_row = metadata[metadata['tei_file'] == f"tei/{tei_file.name}"]
        
        if metadata_row.empty:
            print(f"   ⚠️  {tei_file.stem}: Sin metadata, usando defaults")
            metadata_row = pd.Series({'title': '', 'author': '', 'year_first_pub': '', 
                                     'decada_norm': '', 'genero_macro_normalizado': ''})
        else:
            metadata_row = metadata_row.iloc[0]
        
        # Analizar
        try:
            metricas = analizar_documento(tei_file, diccionario, metadata_row)
            if metricas:
                resultados.append(metricas)
                procesados += 1
                
                if procesados % 10 == 0:
                    print(f"   ✓ Procesados: {procesados}/{len(tei_files)}")
        except Exception as e:
            print(f"   ❌ {tei_file.stem}: Error - {e}")
            errores += 1
    
    print("-" * 80)
    print(f"✓ Procesamiento completado:")
    print(f"  - Exitosos: {procesados}")
    print(f"  - Errores: {errores}")
    print()
    
    # Crear DataFrame
    df = pd.DataFrame(resultados)
    
    # Guardar resultados
    output_file = OUTPUT_DIR / "metricas_etnograficas_completo.csv"
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"💾 Guardado: {output_file}")
    print(f"   📊 {len(df)} documentos × {len(df.columns)} columnas")
    
    # Generar resumen por década
    if 'decada' in df.columns and df['decada'].notna().any():
        print(f"\n📈 Generando resumen por década...")
        
        # Categorías de densidad
        density_cols = [col for col in df.columns if col.endswith('_densidad')]
        
        resumen_decada = df.groupby('decada')[density_cols].agg(['mean', 'std', 'count'])
        resumen_decada.to_csv(OUTPUT_DIR / "resumen_por_decada.csv")
        print(f"   ✓ Guardado: resumen_por_decada.csv")
        
        # Mostrar tabla resumida
        print(f"\n📊 RESUMEN POR DÉCADA (top 5 categorías por densidad media):")
        print("-" * 80)
        
        # Calcular medias por década
        medias = df.groupby('decada')[density_cols].mean()
        
        for decada in sorted(medias.index):
            if pd.notna(decada):
                print(f"\n  {int(decada)}s:")
                top5 = medias.loc[decada].sort_values(ascending=False).head(5)
                for cat, densidad in top5.items():
                    cat_clean = cat.replace('_densidad', '')
                    print(f"    • {cat_clean:30s}: {densidad:6.2f}")
    
    # Generar resumen por autor
    if 'autor' in df.columns and df['autor'].notna().any():
        print(f"\n👤 Generando resumen por autor...")
        
        density_cols = [col for col in df.columns if col.endswith('_densidad')]
        resumen_autor = df.groupby('autor')[density_cols].agg(['mean', 'count'])
        resumen_autor.to_csv(OUTPUT_DIR / "resumen_por_autor.csv")
        print(f"   ✓ Guardado: resumen_por_autor.csv")
    
    print("\n" + "=" * 80)
    print("✅ ANÁLISIS ETNOGRÁFICO COMPLETADO")
    print("=" * 80)
    print(f"\nOutputs en: {OUTPUT_DIR}/")
    print("  • metricas_etnograficas_completo.csv")
    print("  • resumen_por_decada.csv")
    print("  • resumen_por_autor.csv")
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
SCRIPT 02: Análisis de Coocurrencias Sociales
Corpus Etnográfico Galicia (1860-1950)

Identifica qué categorías etnográficas aparecen juntas en los mismos documentos.
Pregunta: ¿Cuándo se menciona hambre + violencia? ¿estructura_social + trabajo_deuda?

Output: CSV con matriz de coocurrencias y coeficientes Jaccard.
"""

import pandas as pd
from pathlib import Path
from itertools import combinations
import numpy as np

# Configuración
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / "outputs" / "metricas_etnograficas" / "metricas_etnograficas_completo.csv"
OUTPUT_DIR = BASE_DIR / "outputs" / "coocurrencias"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("ANÁLISIS DE COOCURRENCIAS SOCIALES")
print("=" * 80)
print()


def calcular_coocurrencias(df: pd.DataFrame, umbral_densidad: float = 5.0):
    """
    Calcula coocurrencias entre categorías.
    
    Dos categorías "coocurren" en un documento si ambas tienen densidad > umbral.
    
    Args:
        df: DataFrame con métricas etnográficas
        umbral_densidad: Densidad mínima para considerar que categoría está "presente"
    
    Returns:
        DataFrame con coocurrencias
    """
    # Identificar columnas de densidad
    density_cols = [col for col in df.columns if col.endswith('_densidad')]
    categorias = [col.replace('_densidad', '') for col in density_cols]
    
    print(f"📊 Categorías encontradas: {len(categorias)}")
    print(f"📄 Documentos: {len(df)}")
    print(f"🎯 Umbral de densidad: {umbral_densidad}\n")
    
    # Crear matriz binaria (1 si categoría presente, 0 si ausente)
    matriz_presencia = pd.DataFrame()
    for col in density_cols:
        cat_name = col.replace('_densidad', '')
        matriz_presencia[cat_name] = (df[col] > umbral_densidad).astype(int)
    
    # Calcular coocurrencias para cada par de categorías
    resultados = []
    
    for cat1, cat2 in combinations(categorias, 2):
        # Documentos donde ambas categorías están presentes
        ambas_presentes = (matriz_presencia[cat1] == 1) & (matriz_presencia[cat2] == 1)
        coocurrencias = ambas_presentes.sum()
        
        # Solo cat1 presente
        solo_cat1 = (matriz_presencia[cat1] == 1) & (matriz_presencia[cat2] == 0)
        solo_cat1_count = solo_cat1.sum()
        
        # Solo cat2 presente
        solo_cat2 = (matriz_presencia[cat1] == 0) & (matriz_presencia[cat2] == 1)
        solo_cat2_count = solo_cat2.sum()
        
        # Ninguna presente
        ninguna = (matriz_presencia[cat1] == 0) & (matriz_presencia[cat2] == 0)
        ninguna_count = ninguna.sum()
        
        # Índice de Jaccard: J(A,B) = |A ∩ B| / |A ∪ B|
        union = coocurrencias + solo_cat1_count + solo_cat2_count
        jaccard = coocurrencias / union if union > 0 else 0
        
        resultados.append({
            'categoria_1': cat1,
            'categoria_2': cat2,
            'coocurrencias': coocurrencias,
            'solo_cat1': solo_cat1_count,
            'solo_cat2': solo_cat2_count,
            'ninguna': ninguna_count,
            'jaccard_index': round(jaccard, 4),
            'total_documentos': len(df)
        })
    
    return pd.DataFrame(resultados)


def main():
    # Verificar que existe el archivo de input
    if not INPUT_FILE.exists():
        print(f"❌ ERROR: No se encuentra el archivo de métricas etnográficas")
        print(f"   Esperado: {INPUT_FILE}")
        print(f"\n   Ejecuta primero: python scripts/01_analisis_etnografico.py")
        return
    
    # Cargar métricas
    print(f"📖 Cargando métricas: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE)
    print(f"   ✓ {len(df)} documentos cargados\n")
    
    # Calcular coocurrencias
    print("🔬 Calculando coocurrencias...")
    cooc_df = calcular_coocurrencias(df, umbral_densidad=5.0)
    
    # Ordenar por número de coocurrencias (descendente)
    cooc_df = cooc_df.sort_values('coocurrencias', ascending=False)
    
    # Guardar resultados
    output_file = OUTPUT_DIR / "matriz_coocurrencias.csv"
    cooc_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n💾 Guardado: {output_file}")
    print(f"   📊 {len(cooc_df)} pares de categorías analizados")
    
    # Mostrar top 10 coocurrencias
    print("\n" + "=" * 80)
    print("TOP 10 COOCURRENCIAS MÁS FRECUENTES")
    print("=" * 80)
    print()
    
    top10 = cooc_df.head(10)
    for idx, row in top10.iterrows():
        print(f"{row['categoria_1']:30s} + {row['categoria_2']:30s}")
        print(f"  → Coocurrencias: {row['coocurrencias']:3d} docs | Jaccard: {row['jaccard_index']:.3f}")
        print()
    
    # Mostrar pares con alta correlación (Jaccard > 0.5)
    alta_correlacion = cooc_df[cooc_df['jaccard_index'] > 0.5]
    
    if len(alta_correlacion) > 0:
        print("=" * 80)
        print(f"PARES CON ALTA CORRELACIÓN (Jaccard > 0.5)")
        print("=" * 80)
        print()
        
        for idx, row in alta_correlacion.iterrows():
            print(f"• {row['categoria_1']} + {row['categoria_2']}")
            print(f"  Jaccard: {row['jaccard_index']:.3f} | Coocurrencias: {row['coocurrencias']} docs")
        print()
    else:
        print("ℹ️  No se encontraron pares con correlación Jaccard > 0.5\n")
    
    print("=" * 80)
    print("✅ ANÁLISIS DE COOCURRENCIAS COMPLETADO")
    print("=" * 80)
    print(f"\nOutput: {OUTPUT_DIR}/matriz_coocurrencias.csv")
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cargar_diccionario_v1.py - Loader para diccionario centralizado v1.0.x (basado en regex)
========================================================================================

Carga diccionario_corpus_v1_0_1.json (o anterior) y proporciona interfaz compatible
con la infraestructura existente.

Uso:
    from cargar_diccionario_v1 import cargar_diccionario, DICCIONARIO, CATEGORIAS_REGEX
    
    # DICCIONARIO: dict bruto del JSON
    # CATEGORIAS_REGEX: dict compilado listo para usar

Autor: Proyecto DH - Análisis Migración Gallega
Fecha: Febrero 2026
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def cargar_diccionario_json(version: str = "v1_0_1") -> dict:
    """
    Carga diccionario JSON centralizado.
    
    Args:
        version: "v1_0_1", "v1_0_0", etc. (sin .json)
    
    Returns:
        Dict con estructura de diccionario
    """
    ruta_repo = Path(__file__).parent.parent
    ruta_diccionaria = ruta_repo / 'diccionarios' / f'diccionario_corpus_{version}.json'
    
    if not ruta_diccionaria.exists():
        raise FileNotFoundError(f"Diccionario no encontrado: {ruta_diccionaria}")
    
    with open(ruta_diccionaria, 'r', encoding='utf-8') as f:
        return json.load(f)


def compilar_categorias_regex(diccionario: dict) -> Dict[str, List]:
    """
    Compila regex patterns de diccionario en listas reutilizables.
    
    Args:
        diccionario: Dict cargado del JSON
    
    Returns:
        Dict {categoria: [patron_compilado1, patron_compilado2, ...]}
    """
    categorias_compiladas = {}
    
    for categoria, datos in diccionario.get('categories', {}).items():
        patrones_raw = datos.get('patterns', [])
        patrones_compilados = []
        
        for patron_raw in patrones_raw:
            try:
                # Compilar con flags IGNORECASE + UNICODE
                patron_compilado = re.compile(patron_raw, re.IGNORECASE | re.UNICODE)
                patrones_compilados.append(patron_compilado)
            except re.error as e:
                print(f"⚠️  Error compilando patrón '{patron_raw[:30]}': {e}")
        
        if patrones_compilados:
            categorias_compiladas[categoria] = patrones_compilados
    
    return categorias_compiladas


def buscar_matches(texto: str, categorias_regex: Dict[str, List]) -> Dict[str, List]:
    """
    Busca todos los matches en un texto para todas las categorías.
    
    Args:
        texto: Texto normalizado (lowercase)
        categorias_regex: Dict de patrones compilados
    
    Returns:
        Dict {categoria: [(match_text, position, patron_usado), ...]}
    """
    matches_por_categoria = {}
    
    for categoria, patrones in categorias_regex.items():
        matches = []
        
        for patron in patrones:
            for match_obj in patron.finditer(texto):
                matches.append({
                    'text': match_obj.group(),
                    'start': match_obj.start(),
                    'end': match_obj.end(),
                    'patron': patron.pattern[:50]  # Primeros 50 chars del regex
                })
        
        matches_por_categoria[categoria] = matches
    
    return matches_por_categoria


def contar_matches(matches_por_categoria: Dict[str, List], texto_len_tokens: int) -> Dict[str, float]:
    """
    Calcula densidad (matches por 10k tokens) para cada categoría.
    
    Args:
        matches_por_categoria: Dict de matches
        texto_len_tokens: Total de tokens en texto
    
    Returns:
        Dict {categoria: densidad_por_10k}
    """
    densidades = {}
    
    for categoria, matches in matches_por_categoria.items():
        n_matches = len(matches)
        if texto_len_tokens > 0:
            densidad = (n_matches / texto_len_tokens) * 10000
        else:
            densidad = 0
        
        densidades[categoria] = {
            'count': n_matches,
            'densidad': densidad
        }
    
    return densidades


# ===== CARGA AUTOMÁTICA =====

try:
    # Intentar cargar v1.0.1 (recomendada)
    DICCIONARIO = cargar_diccionario_json('v1_0_1')
    print("✅ Diccionario v1.0.1 cargado")
except FileNotFoundError:
    # Fallback a v1.0.0
    try:
        DICCIONARIO = cargar_diccionario_json('v1_0_0')
        print("✅ Diccionario v1.0.0 cargado (v1.0.1 no encontrada)")
    except FileNotFoundError:
        print("❌ Ni v1.0.1 ni v1.0.0 encontrados")
        DICCIONARIO = {}

# Compilar patrones
CATEGORIAS_REGEX = compilar_categorias_regex(DICCIONARIO)

# Para backwards-compatibility con scripts viejos que usan CATEGORIAS como lista de términos
# (aunque esta versión es regex-based, no term-based)
CATEGORIAS = {
    cat: [] for cat in DICCIONARIO.get('categories', {}).keys()
}


if __name__ == '__main__':
    print("\n✅ Módulo cargar_diccionario_v1.py listo")
    print(f"\nDiccionario v{DICCIONARIO.get('version')}")
    print(f"Categorías: {list(CATEGORIAS.keys())}")
    print(f"Patrones compilados: {sum(len(p) for p in CATEGORIAS_REGEX.values())}")

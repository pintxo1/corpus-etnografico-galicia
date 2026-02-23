#!/usr/bin/env python3
"""
Extracción de Texto desde TEI-XML
Migración gallega a América (1860-1950)

Módulo utilitario para extraer texto limpio del <body> de archivos TEI.
Ignora metadatos del <teiHeader> y se enfoca en el contenido textual.

Puede usarse como módulo importable o como script independiente.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from lxml import etree

# TEI namespace (estándar)
TEI_NAMESPACE = {'tei': 'http://www.tei-c.org/ns/1.0'}


def extraer_texto_tei(tei_file: Path, 
                     incluir_metadata: bool = False) -> Dict[str, str]:
    """
    Extrae texto del body de un archivo TEI-XML.
    
    Args:
        tei_file: Ruta al archivo TEI
        incluir_metadata: Si True, intenta extraer título y autor del teiHeader
        
    Returns:
        Diccionario con 'texto', opcionalmente 'titulo' y 'autor'
    """
    resultado = {
        'archivo': tei_file.stem,
        'texto': '',
        'titulo': '',
        'autor': ''
    }
    
    try:
        tree = etree.parse(str(tei_file))
        
        # Extraer texto del body
        # Intentar primero con namespace TEI estándar
        body_elements = tree.xpath('//tei:text//tei:body//text()', 
                                   namespaces=TEI_NAMESPACE)
        
        # Si no funciona, intentar sin namespace
        if not body_elements:
            body_elements = tree.xpath('//text//body//text()')
        
        # Limpiar y unir texto
        texto = ' '.join([t.strip() for t in body_elements if t.strip()])
        resultado['texto'] = texto
        
        # Extraer metadata si se solicita
        if incluir_metadata:
            # Intentar extraer título
            titulos = tree.xpath('//tei:titleStmt//tei:title/text()', 
                               namespaces=TEI_NAMESPACE)
            if not titulos:
                titulos = tree.xpath('//titleStmt//title/text()')
            resultado['titulo'] = titulos[0].strip() if titulos else tei_file.stem
            
            # Intentar extraer autor
            autores = tree.xpath('//tei:titleStmt//tei:author/text()', 
                               namespaces=TEI_NAMESPACE)
            if not autores:
                autores = tree.xpath('//titleStmt//author/text()')
            resultado['autor'] = autores[0].strip() if autores else 'Desconocido'
        
        return resultado
        
    except etree.XMLSyntaxError as e:
        print(f"⚠ Error de sintaxis XML en {tei_file.name}: {e}")
        return resultado
    except Exception as e:
        print(f"⚠ Error procesando {tei_file.name}: {e}")
        return resultado


def extraer_corpus_completo(tei_folder: str = '../tei',
                            incluir_metadata: bool = True) -> List[Dict[str, str]]:
    """
    Extrae texto de todos los archivos TEI en una carpeta.
    
    Args:
        tei_folder: Carpeta con archivos TEI-XML
        incluir_metadata: Si True, extrae también título y autor
        
    Returns:
        Lista de diccionarios con texto y metadata de cada documento
    """
    tei_folder = Path(tei_folder)
    
    if not tei_folder.exists():
        print(f"⚠ La carpeta {tei_folder} no existe")
        return []
    
    tei_files = list(tei_folder.glob("*.xml"))
    
    if not tei_files:
        print(f"⚠ No se encontraron archivos XML en {tei_folder}")
        return []
    
    print(f"Extrayendo texto de {len(tei_files)} documentos...\n")
    
    corpus = []
    for i, tei_file in enumerate(tei_files, 1):
        print(f"[{i}/{len(tei_files)}] {tei_file.name}")
        doc = extraer_texto_tei(tei_file, incluir_metadata)
        
        if doc['texto']:
            num_chars = len(doc['texto'])
            print(f"           {num_chars:,} caracteres extraídos")
            corpus.append(doc)
        else:
            print(f"           ⚠ No se pudo extraer texto")
    
    print(f"\n✓ Extracción completada: {len(corpus)} documentos")
    return corpus


def validar_estructura_tei(tei_file: Path) -> Dict[str, bool]:
    """
    Valida que un archivo TEI tenga la estructura mínima esperada.
    
    Args:
        tei_file: Ruta al archivo TEI
        
    Returns:
        Diccionario con resultados de validación
    """
    validacion = {
        'xml_valido': False,
        'tiene_teiheader': False,
        'tiene_text': False,
        'tiene_body': False,
        'tiene_contenido': False
    }
    
    try:
        tree = etree.parse(str(tei_file))
        validacion['xml_valido'] = True
        
        # Verificar elementos con y sin namespace
        def existe_elemento(xpath_con_ns, xpath_sin_ns):
            elementos = tree.xpath(xpath_con_ns, namespaces=TEI_NAMESPACE)
            if not elementos:
                elementos = tree.xpath(xpath_sin_ns)
            return len(elementos) > 0
        
        validacion['tiene_teiheader'] = existe_elemento(
            '//tei:teiHeader', '//teiHeader'
        )
        validacion['tiene_text'] = existe_elemento(
            '//tei:text', '//text'
        )
        validacion['tiene_body'] = existe_elemento(
            '//tei:text//tei:body', '//text//body'
        )
        
        # Verificar que el body tenga contenido
        body_text = tree.xpath('//tei:text//tei:body//text()', 
                              namespaces=TEI_NAMESPACE)
        if not body_text:
            body_text = tree.xpath('//text//body//text()')
        
        texto_limpio = ' '.join([t.strip() for t in body_text if t.strip()])
        validacion['tiene_contenido'] = len(texto_limpio) > 0
        
    except etree.XMLSyntaxError:
        pass
    except Exception:
        pass
    
    return validacion


def imprimir_reporte_validacion(tei_folder: str = '../tei'):
    """
    Imprime reporte de validación de estructura TEI para todos los archivos.
    
    Args:
        tei_folder: Carpeta con archivos TEI
    """
    tei_folder = Path(tei_folder)
    tei_files = list(tei_folder.glob("*.xml"))
    
    print("=" * 70)
    print("VALIDACIÓN DE ESTRUCTURA TEI")
    print("=" * 70)
    print()
    
    problemas = []
    
    for tei_file in tei_files:
        validacion = validar_estructura_tei(tei_file)
        
        if all(validacion.values()):
            print(f"✓ {tei_file.name}")
        else:
            print(f"✗ {tei_file.name}")
            for campo, valor in validacion.items():
                if not valor:
                    print(f"    ⚠ Falta: {campo}")
            problemas.append(tei_file.name)
    
    print()
    print("=" * 70)
    if problemas:
        print(f"⚠ {len(problemas)} archivo(s) con problemas de estructura")
    else:
        print(f"✓ Todos los archivos tienen estructura TEI válida")
    print("=" * 70)


def main():
    """Función principal para uso como script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extracción de texto desde archivos TEI-XML'
    )
    parser.add_argument('--tei-folder', default='../tei',
                       help='Carpeta con archivos TEI (default: ../tei)')
    parser.add_argument('--validar', action='store_true',
                       help='Solo validar estructura sin extraer')
    parser.add_argument('--exportar', metavar='ARCHIVO',
                       help='Exportar corpus extraído a archivo JSON')
    
    args = parser.parse_args()
    
    if args.validar:
        # Solo validar estructura
        imprimir_reporte_validacion(args.tei_folder)
    else:
        # Extraer corpus
        corpus = extraer_corpus_completo(args.tei_folder, incluir_metadata=True)
        
        # Exportar si se solicita
        if args.exportar and corpus:
            import json
            output_path = Path(args.exportar)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(corpus, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Corpus exportado a: {output_path}")


if __name__ == "__main__":
    main()

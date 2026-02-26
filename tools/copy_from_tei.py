#!/usr/bin/env python3
"""
copy_from_tei.py - Copiar corpus TEI con trazabilidad

**Propósito:**
Copiar archivos TEI desde corpus externo (corpus-literario/tei/) 
a este proyecto (01_data/tei/source/), generando MANIFEST.md con:
- Timestamp de copia
- SHA-256 checksums por archivo (detectar cambios futuros)
- Validación básica de estructura TEI (lxml parsea sin error)

**Uso:**
    python tools/copy_from_tei.py --source /ruta/corpus-literario/tei/ --output 01_data/tei/source/

**Argumentos:**
    --source: Directorio con archivos .xml (TEI)
    --output: Directorio destino (default: 01_data/tei/source/)
    --validate: Validar TEI con lxml (default: True)

**Output:**
    - Archivos .xml copiados a --output
    - MANIFEST.md con checksums y timestamp

**Filosofía:**
Este script implementa reproducibilidad:
- No symlinks (problemas si corpus original se mueve)
- SHA-256 permite detectar si archivos cambian entre versiones
- MANIFEST.md documenta proveniencia (quién, cuándo, desde dónde)
"""

import argparse
import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple
import sys

try:
    from lxml import etree
except ImportError:
    print("❌ Error: lxml no instalado. Instalar con: pip install lxml")
    sys.exit(1)


def compute_sha256(filepath: Path) -> str:
    """Calcular SHA-256 de archivo."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def validate_tei(filepath: Path) -> Tuple[bool, str]:
    """
    Validación básica de TEI: ¿parsea con lxml?
    
    Returns:
        (valid: bool, message: str)
    """
    try:
        tree = etree.parse(str(filepath))
        root = tree.getroot()
        
        # Check si tiene namespace TEI (flexible: acepta TEI P5 o variantes)
        if 'TEI' not in root.tag:
            return False, f"Root tag no es TEI: {root.tag}"
        
        return True, "OK"
    
    except etree.XMLSyntaxError as e:
        return False, f"XML syntax error: {e}"
    except Exception as e:
        return False, f"Parsing error: {e}"


def copy_tei_corpus(source_dir: Path, output_dir: Path, validate: bool = True) -> List[dict]:
    """
    Copiar archivos .xml de source_dir a output_dir con checksums.
    
    Returns:
        List of dicts: [{'filename': ..., 'sha256': ..., 'valid': ..., 'message': ...}]
    """
    source_dir = Path(source_dir).resolve()
    output_dir = Path(output_dir).resolve()
    
    if not source_dir.exists():
        raise FileNotFoundError(f"Directorio source no existe: {source_dir}")
    
    # Crear output_dir si no existe
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Buscar archivos .xml en source
    xml_files = sorted(source_dir.glob('*.xml'))
    
    if not xml_files:
        print(f"⚠️  Ningún archivo .xml encontrado en {source_dir}")
        return []
    
    print(f"📁 Copiando {len(xml_files)} archivos .xml desde:")
    print(f"   Source: {source_dir}")
    print(f"   Output: {output_dir}\n")
    
    results = []
    
    for xml_file in xml_files:
        filename = xml_file.name
        dest_file = output_dir / filename
        
        # Copiar archivo
        shutil.copy2(xml_file, dest_file)
        
        # Calcular SHA-256
        sha256 = compute_sha256(dest_file)
        
        # Validar TEI (opcional)
        valid, message = (True, "Skipped") if not validate else validate_tei(dest_file)
        
        status = "✅" if valid else "❌"
        print(f"{status} {filename:40s} | SHA256: {sha256[:12]}... | {message}")
        
        results.append({
            'filename': filename,
            'sha256': sha256,
            'valid': valid,
            'message': message
        })
    
    return results


def write_manifest(output_dir: Path, results: List[dict], source_dir: Path):
    """Escribir MANIFEST.md con timestamp y checksums."""
    manifest_path = output_dir / 'MANIFEST.md'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write("# MANIFEST - Corpus TEI\n\n")
        f.write(f"**Generado:** {timestamp}  \n")
        f.write(f"**Source:** `{source_dir}`  \n")
        f.write(f"**Archivos copiados:** {len(results)}  \n\n")
        f.write("---\n\n")
        f.write("## Checksums (SHA-256)\n\n")
        f.write("| Archivo | SHA-256 | Valid TEI | Notes |\n")
        f.write("|---------|---------|-----------|-------|\n")
        
        for r in results:
            valid_icon = "✅" if r['valid'] else "❌"
            message = r['message'] if r['message'] != "OK" else ""
            f.write(f"| `{r['filename']}` | `{r['sha256']}` | {valid_icon} | {message} |\n")
        
        f.write("\n---\n\n")
        f.write("## Uso del MANIFEST\n\n")
        f.write("1. **Trazabilidad:** Documenta origen y fecha de copia del corpus\n")
        f.write("2. **Integridad:** Verificar checksums si sospecha de corrupción:\n")
        f.write("   ```bash\n")
        f.write("   shasum -a 256 01_data/tei/source/*.xml\n")
        f.write("   # Comparar con checksums en esta tabla\n")
        f.write("   ```\n")
        f.write("3. **Versionado:** Si corpus original cambia, re-ejecutar `copy_from_tei.py` generará nuevo MANIFEST (comparar diffs)\n\n")
        f.write("**Última actualización:** Ver timestamp arriba  \n")
        f.write("**Script:** `tools/copy_from_tei.py`\n")
    
    print(f"\n📄 MANIFEST generado: {manifest_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Copiar corpus TEI con checksums y validación",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplo de uso:
    python tools/copy_from_tei.py --source ../corpus-literario/tei/
    python tools/copy_from_tei.py --source /path/to/corpus/ --output 01_data/tei/source/ --no-validate
        """
    )
    
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        help="Directorio con archivos TEI .xml (corpus original)"
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='01_data/tei/source',
        help="Directorio destino (default: 01_data/tei/source/)"
    )
    
    parser.add_argument(
        '--no-validate',
        dest='validate',
        action='store_false',
        help="Desactivar validación TEI (más rápido, menos seguro)"
    )
    
    args = parser.parse_args()
    
    # Convertir a Path
    source_dir = Path(args.source)
    output_dir = Path(args.output)
    
    # Copiar archivos
    try:
        results = copy_tei_corpus(source_dir, output_dir, validate=args.validate)
        
        if not results:
            print("\n⚠️  No se copiaron archivos.")
            return
        
        # Escribir MANIFEST
        write_manifest(output_dir, results, source_dir)
        
        # Summary
        valid_count = sum(1 for r in results if r['valid'])
        invalid_count = len(results) - valid_count
        
        print("\n" + "="*60)
        print(f"✅ Copia completada: {len(results)} archivos")
        if args.validate:
            print(f"   TEI válidos: {valid_count} | Inválidos: {invalid_count}")
        print(f"   Checksums: Ver {output_dir / 'MANIFEST.md'}")
        print("="*60)
        
        if invalid_count > 0:
            print("\n⚠️  ADVERTENCIA: Algunos archivos TEI no validaron correctamente.")
            print("   Revisar MANIFEST.md para detalles.")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

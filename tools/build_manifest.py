#!/usr/bin/env python3
"""
Build Manifest: Reproducibilidad y auditabilidad de artefactos
Lista todos los archivos generados con sha256, tamaño y timestamp
"""

import argparse
import os
import sys
import hashlib
import csv
from datetime import datetime
from pathlib import Path


def compute_sha256(filepath):
    """Calcula SHA256 de un archivo"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def build_manifest(
    outputs_dir="04_outputs",
    patterns_dir="02_methods/patterns",
    output_manifest_dir="04_outputs/manifests"
):
    """
    Recorre outputs_dir y patterns_dir para listar todos los artefactos
    generados con hash, tamaño y timestamp.
    
    Excluye archivos basura: .DS_Store, __pycache__, *.pyc, directorios ocultos.
    
    Outputs:
    - 04_outputs/manifests/ARTIFACTS_MANIFEST.csv
    - 04_outputs/manifests/ARTIFACTS_MANIFEST.md
    """
    
    os.makedirs(output_manifest_dir, exist_ok=True)
    
    # Archivos/dirs a excluir
    EXCLUDED = {'.DS_Store', '__pycache__', '.gitignore', '.git'}
    EXCLUDED_EXTENSIONS = {'.pyc', '.pyo', '.pyd', '.so'}
    
    def should_exclude(filepath, filename):
        """Determina si archivo debe ser excluido"""
        if filename in EXCLUDED:
            return True
        if filename.startswith('.'):
            return True
        if any(filepath.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
            return True
        if '__pycache__' in filepath:
            return True
        return False
    
    artifacts = []
    
    # ============================================================================
    # Escanear 04_outputs/ (outputs)
    # ============================================================================
    outputs_path = Path(outputs_dir)
    if outputs_path.exists():
        for root, dirs, files in os.walk(outputs_path):
            for file in files:
                if should_exclude(os.path.join(root, file), file):
                    continue
                
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, outputs_dir)
                
                # Skip manifests mismos (evitar recursión)
                if "manifests" in rel_path:
                    continue
                
                try:
                    size = os.path.getsize(filepath)
                    sha256 = compute_sha256(filepath)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                    file_type = "output"
                    
                    artifacts.append({
                        'path': rel_path,
                        'category': file_type,
                        'size_bytes': size,
                        'sha256': sha256,
                        'modified': mtime
                    })
                except Exception as e:
                    print(f"⚠️  Warning: {filepath} - {e}", file=sys.stderr)
    
    # ============================================================================
    # Escanear 02_methods/patterns/ (reglas YAML)
    # ============================================================================
    patterns_path = Path(patterns_dir)
    if patterns_path.exists():
        for file in patterns_path.glob("*.yml"):
            filepath = str(file)
            rel_path = f"patterns/{file.name}"
            
            try:
                size = os.path.getsize(filepath)
                sha256 = compute_sha256(filepath)
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                file_type = "rules"
                
                artifacts.append({
                    'path': rel_path,
                    'category': file_type,
                    'size_bytes': size,
                    'sha256': sha256,
                    'modified': mtime
                })
            except Exception as e:
                print(f"⚠️  Warning: {filepath} - {e}", file=sys.stderr)
    
    # ============================================================================
    # Escribir CSV manifest
    # ============================================================================
    csv_path = os.path.join(output_manifest_dir, "ARTIFACTS_MANIFEST.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['path', 'category', 'size_bytes', 'sha256', 'modified'])
        writer.writeheader()
        writer.writerows(sorted(artifacts, key=lambda x: x['path']))
    
    # ============================================================================
    # Escribir Markdown manifest con resumen
    # ============================================================================
    md_path = os.path.join(output_manifest_dir, "ARTIFACTS_MANIFEST.md")
    
    # Agrupar por categoría
    by_category = {}
    for art in artifacts:
        cat = art['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(art)
    
    md_content = f"""# Artifacts Manifest

**Generated:** {datetime.now().isoformat()}

## Summary

| Category | Count | Total Size (MB) |
|----------|-------|-----------------|
"""
    
    for cat in sorted(by_category.keys()):
        items = by_category[cat]
        total_size = sum(a['size_bytes'] for a in items) / 1024 / 1024
        md_content += f"| {cat} | {len(items)} | {total_size:.2f} |\n"
    
    md_content += "\n---\n\n"
    
    # ============================================================================
    # Detalle por categoría
    # ============================================================================
    for cat in sorted(by_category.keys()):
        items = sorted(by_category[cat], key=lambda x: x['path'])
        md_content += f"## {cat.upper()} ({len(items)} files)\n\n"
        md_content += "| Path | Size (bytes) | SHA256 | Modified |\n"
        md_content += "|------|--------------|--------|----------|\n"
        for art in items:
            path_display = art['path'][:50]  # Truncate for readability
            sha_short = art['sha256'][:8]
            md_content += f"| `{path_display}` | {art['size_bytes']:,} | {sha_short}... | {art['modified'][:10]} |\n"
        md_content += "\n"
    
    md_content += """---

## Reproducibility

To verify manifest integrity:

```bash
# Compute current SHA256 of each artifact
for row in $(tail -n +2 ARTIFACTS_MANIFEST.csv); do
    path=$(echo $row | cut -d',' -f1)
    expected_sha=$(echo $row | cut -d',' -f4)
    actual_sha=$(sha256sum "$path" | cut -d' ' -f1)
    if [ "$expected_sha" != "$actual_sha" ]; then
        echo "❌ MISMATCH: $path"
    fi
done
```

---

*Manifest for ethnographic pipeline outputs*
"""
    
    with open(md_path, 'w') as f:
        f.write(md_content)
    
    # ============================================================================
    # Imprimir resumen
    # ============================================================================
    print(f"\n✅ Manifest CSV: {csv_path}")
    print(f"✅ Manifest MD: {md_path}")
    print(f"\nTotal artifacts indexed: {len(artifacts)}")
    for cat in sorted(by_category.keys()):
        print(f"  - {cat}: {len(by_category[cat])}")
    
    return csv_path, md_path


def main():
    parser = argparse.ArgumentParser(
        description="Build reproducibility manifest for pipeline outputs"
    )
    parser.add_argument('--outputs-dir', default='04_outputs')
    parser.add_argument('--patterns-dir', default='02_methods/patterns')
    parser.add_argument('--manifest-dir', default='04_outputs/manifests')
    
    args = parser.parse_args()
    
    build_manifest(
        outputs_dir=args.outputs_dir,
        patterns_dir=args.patterns_dir,
        output_manifest_dir=args.manifest_dir
    )


if __name__ == '__main__':
    main()

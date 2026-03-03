#!/usr/bin/env python3
"""Build Zenodo dataset package: freeze-lite + documentation + metadata."""
import csv
import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Root of repository
REPO_ROOT = Path(__file__).resolve().parents[1]
ZENODO_ROOT = REPO_ROOT / "zenodo"

# Subdirectories within zenodo/
DATASET_DIR = ZENODO_ROOT / "dataset_freeze_lite"
METADATA_DIR = ZENODO_ROOT / "metadata"
LICENSES_DIR = ZENODO_ROOT / "licenses"


class FileClassifier:
    """Classify files as: include, exclude (with reason), or skip."""

    # Files to INCLUDE in Zenodo dataset
    INCLUDE_PATTERNS = {
        # Freeze-lite bundle (primary deliverable)
        ("05_freeze/v1.0.2-lite/figures", "figures"),
        ("05_freeze/v1.0.2-lite/tables", "tables"),
        ("05_freeze/v1.0.2-lite/reports", "reports"),
        ("05_freeze/v1.0.2-lite/manifests", "manifests"),
        
        # Key documentation
        ("00_docs/PACK_V2_METHOD.md", "metadata"),
        ("00_docs/FREEZE_LITE.md", "metadata"),
        ("00_docs/DATA_DICTIONARY.md", "metadata"),
        ("00_docs/METHODOLOGY.md", "metadata"),
        ("00_docs/PAPER_METHOD_SUMMARY.md", "metadata"),
        
        # Key analysis tables
        ("04_outputs/tables/corpus_master_table_v2tokens.csv", "metadata"),
        ("04_outputs/tables/token_mismatch_audit.csv", "metadata"),
        ("04_outputs/tables/emigrant_mentions_by_work.csv", "metadata"),
        
        # Case studies
        ("04_outputs/case_cards", "metadata"),
        
        # Licenses
        ("LICENSE", "licenses"),
    }

    # Files to EXCLUDE with documented reasons
    EXCLUDE_REASONS = {
        # TEI XML (full corpus may have copyright restrictions)
        "01_data/tei/source": "Copyright: Full TEI corpus not public in Zenodo (available via GitHub)",
        "01_data/tei/sample": "Sample only; full TEI in GitHub",
        
        # Configuration files with potential credentials
        "CONFIG_ANALISIS.yml": "Configuration file; use GitHub version",
        ".env": "Credentials file (if exists)",
        
        # Intermediate/temporal outputs
        "04_outputs/tables": "Intermediate analysis tables (not in freeze-lite; see freeze-lite/ instead)",
        "04_outputs/figures": "Intermediate figures (use freeze-lite/figures/ for final)",
        "03_analysis": "Analysis workspace (see freeze-lite/ for deliverables)",
        
        # Code (belongs in GitHub release)
        "02_methods/scripts_core": "Code: use GitHub repo + release for reproducibility",
        "02_methods/scripts_viz": "Code: use GitHub repo + release",
        "tools": "Code tooling: see GitHub repo",
        
        # Large generated outputs not in freeze-lite
        "01_data/text": "Plaintext full corpus (large; not needed with freeze-lite)",
        
        # Version control and caches
        ".git": "Git directory: not for dataset",
        ".venv": "Virtual environment: not for dataset",
        "__pycache__": "Python cache: not for dataset",
        ".DS_Store": "macOS metadata: not for dataset",
    }

    @classmethod
    def classify_file(cls, file_path: Path) -> Tuple[str, str]:
        """
        Classify a file.
        
        Returns: (action, reason)
        - action: 'include', 'exclude', or 'skip'
        - reason: description
        """
        rel_path = file_path.relative_to(REPO_ROOT)
        rel_str = str(rel_path)

        # Check exclusions first
        for exclude_pattern, reason in cls.EXCLUDE_REASONS.items():
            if rel_str.startswith(exclude_pattern) or rel_str == exclude_pattern:
                return "exclude", reason

        # Check inclusions
        for include_pattern, category in cls.INCLUDE_PATTERNS:
            if rel_str.startswith(include_pattern) or rel_str == include_pattern:
                return "include", category

        # If not explicitly included, skip
        return "skip", "not in include list"


def compute_sha256(file_path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def copy_file_recursive(src: Path, dst_parent: Path, category: str) -> List[Tuple[Path, str]]:
    """
    Recursively copy files from src to dst_parent/category/.
    Returns list of (destination_path, sha256).
    """
    copied = []
    
    if src.is_file():
        # Single file
        dst_subdir = dst_parent / category
        dst_subdir.mkdir(parents=True, exist_ok=True)
        dst = dst_subdir / src.name
        shutil.copy2(src, dst)
        sha = compute_sha256(dst)
        copied.append((dst, sha))
    elif src.is_dir():
        # Directory: copy all files recursively
        for file_path in src.rglob("*"):
            if file_path.is_file():
                rel = file_path.relative_to(src)
                dst_subdir = (dst_parent / category / src.name).parent / src.name
                dst_subdir.mkdir(parents=True, exist_ok=True)
                dst = dst_subdir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dst)
                sha = compute_sha256(dst)
                copied.append((dst, sha))
    
    return copied


def build_package() -> None:
    """Build the Zenodo dataset package."""
    
    print("\n" + "="*80)
    print("CONSTRUYENDO PAQUETE ZENODO")
    print("="*80 + "\n")

    # Clean and create directories
    if ZENODO_ROOT.exists():
        print(f"Limpiando {ZENODO_ROOT}...")
        shutil.rmtree(ZENODO_ROOT)
    
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    LICENSES_DIR.mkdir(parents=True, exist_ok=True)
    print("✓ Directorios creados\n")

    # Classify and copy files
    included_files: Dict[Path, str] = {}  # dst_path -> sha256
    excluded_files: Dict[str, str] = {}   # path -> reason
    included_count = 0
    excluded_count = 0

    print("Clasificando archivos...\n")

    for file_path in REPO_ROOT.rglob("*"):
        if file_path.is_dir():
            continue
        if file_path.name.startswith("."):
            continue

        action, reason = FileClassifier.classify_file(file_path)

        if action == "include":
            rel_path = file_path.relative_to(REPO_ROOT)
            print(f"  ✓ {rel_path} → {reason}")
            
            # Determine target directory
            if reason == "figures":
                target_dir = DATASET_DIR / "figures"
            elif reason == "tables":
                target_dir = DATASET_DIR / "tables"
            elif reason == "reports":
                target_dir = DATASET_DIR / "reports"
            elif reason == "manifests":
                target_dir = DATASET_DIR / "manifests"
            elif reason == "metadata":
                target_dir = METADATA_DIR
            elif reason == "licenses":
                target_dir = LICENSES_DIR
            else:
                target_dir = ZENODO_ROOT
            
            target_dir.mkdir(parents=True, exist_ok=True)
            dst = target_dir / file_path.name
            shutil.copy2(file_path, dst)
            sha = compute_sha256(dst)
            included_files[dst] = sha
            included_count += 1

        elif action == "exclude":
            rel_path = file_path.relative_to(REPO_ROOT)
            excluded_files[str(rel_path)] = reason
            excluded_count += 1

    print(f"\n✓ Archivos incluidos: {included_count}")
    print(f"✓ Archivos excluidos: {excluded_count}\n")

    # Generate manifest_checksums.csv (in ZENODO_ROOT)
    manifest_csv = ZENODO_ROOT / "manifest_checksums.csv"
    with open(manifest_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "sha256", "size_bytes", "type"])
        for dst_path, sha in sorted(included_files.items()):
            size = dst_path.stat().st_size
            file_type = dst_path.suffix if dst_path.suffix else "dir"
            rel = dst_path.relative_to(ZENODO_ROOT)
            writer.writerow([str(rel), sha, size, file_type])
    
    print(f"✓ Manifest checksums: manifest_checksums.csv")

    # Generate manifest_files.md (in ZENODO_ROOT)
    manifest_md = ZENODO_ROOT / "manifest_files.md"
    with open(manifest_md, "w") as f:
        f.write("# Manifest of Files\n\n")
        f.write("## Figures\n")
        figures_dir = DATASET_DIR / "figures"
        if figures_dir.exists():
            for fig in sorted(figures_dir.rglob("*")):
                if fig.is_file():
                    size_kb = fig.stat().st_size / 1024
                    rel = fig.relative_to(ZENODO_ROOT)
                    f.write(f"- {rel} ({size_kb:.1f} KB)\n")
        
        f.write("\n## Tables\n")
        tables_dir = DATASET_DIR / "tables"
        if tables_dir.exists():
            for table in sorted(tables_dir.rglob("*")):
                if table.is_file():
                    size_kb = table.stat().st_size / 1024
                    rel = table.relative_to(ZENODO_ROOT)
                    f.write(f"- {rel} ({size_kb:.1f} KB)\n")
        
        f.write("\n## Reports\n")
        reports_dir = DATASET_DIR / "reports"
        if reports_dir.exists():
            for report in sorted(reports_dir.rglob("*")):
                if report.is_file():
                    size_kb = report.stat().st_size / 1024
                    rel = report.relative_to(ZENODO_ROOT)
                    f.write(f"- {rel} ({size_kb:.1f} KB)\n")
    
    print(f"✓ Manifest files: manifest_files.md")

    # Generate README_ZENODO_DATASET.md
    readme_md = ZENODO_ROOT / "README_ZENODO_DATASET.md"
    with open(readme_md, "w") as f:
        f.write("""# Corpus Etnográfico Galicia — Freeze-Lite Dataset

## What This Is

This is a **Freeze-Lite** submission to Zenodo containing:
- Final publication-ready figures (PNG, PDF, JPEG)
- Analysis tables (CSV format)
- Methodology documentation
- QA reports and case studies

**Purpose**: Provide a citable, self-contained dataset for the paper:
> [PAPER TITLE] (2026)

## What's Included

### `dataset_freeze_lite/`
- **figures/**: 56 bilingual figures (EN/ES) as PNG, PDF, and JPEG
- **tables/**: Key analysis tables (CSV)
  - corpus_master_table_v2tokens.csv (80 works metadata)
  - emigrant_mentions_by_work.csv (mention densities)
  - token_mismatch_audit.csv (QA results)
  - Plus 50+ derived tables
- **reports/**: Analysis reports (Markdown)
- **manifests/**: Checksums and file inventory (SHA256)

### `metadata/`
- **PACK_V2_METHOD.md**: Emigrant representation pack selection methodology
- **FREEZE_LITE.md**: Bundle structure and integrity documentation
- **PAPER_METHOD_SUMMARY.md**: Complete methodology for paper
- **DATA_DICTIONARY.md**: Column definitions
- **METHODOLOGY.md**: Detection system and analysis workflow
- **case_negative_v2.md & case_positive_*.md**: Case study examples
- Key CSV tables for reproducibility

### `licenses/`
- LICENSE: Project license

## What's NOT Included (and Why)

| Excluded | Reason |
|----------|--------|
| `01_data/tei/source/` | Full TEI-XML corpus has copyright restrictions; available via GitHub |
| `02_methods/scripts_*` | Code belongs in GitHub repo + release for reproducibility tracking |
| `.git/`, `.venv/`, `__pycache__` | Version control and environment files not needed |
| `CONFIG_ANALISIS.yml` | Configuration file; use GitHub version |
| Intermediate outputs | Large derived tables not in freeze-lite (use freeze-lite/ subset) |

## How to Use

### 1. Citing This Dataset

```bibtex
@dataset{corpus_etnografico_2026,
  title={Corpus Etnográfico Galicia — Freeze-Lite Dataset},
  author={[Your Name]},
  year={2026},
  publisher={Zenodo},
  doi={10.5281/zenodo.XXXXXXX}
}
```

### 2. Reproduce Analysis

This dataset is **self-contained for visualization and secondary analysis**:
1. Download figures from `dataset_freeze_lite/figures/`
2. Load tables from `dataset_freeze_lite/tables/` in pandas/R/Excel
3. Review methodology in `metadata/PAPER_METHOD_SUMMARY.md`

For **full reproducibility** (re-running analysis from TEI source):
- Clone GitHub repository: [INSERT GITHUB URL]
- See `README.md` for setup and pipeline instructions
- TEI corpus available in repo

### 3. Validation

All files include SHA256 checksums in `manifest_checksums.csv`:

```bash
cd zenodo
sha256sum -c manifest_checksums.csv
```

**Expected**: All hashes should match (0 failed).

## File Statistics

Generated: {generated_date}

- **Total files**: {total_files}
- **Total size**: {total_size_mb:.1f} MB
- **Figures**: {fig_count} (PNG/PDF/JPEG)
- **Tables**: {table_count} (CSV)
- **Documentation**: {doc_count} files

## Metadata

| Field | Value |
|-------|-------|
| **Project** | Corpus Etnográfico Galicia |
| **Period** | 19th–20th century Galician literature |
| **Corpus** | 80 literary works, 11,564–262,479 tokens each |
| **Focus** | Emigrant representations in narrative |
| **Language** | Galician, Spanish |
| **Format** | TEI-XML (source), CSV (analysis), PNG/PDF/JPEG (figures) |
| **License** | [INSERT LICENSE] |

## Contact & Questions

For questions or corrections, please:
1. Open an issue on GitHub: [INSERT GITHUB REPO]
2. Contact: [INSERT EMAIL/ORCID]

## References (from documentation)

See `metadata/` for full documentation:
- Detection limits and system parameters
- Sampling strategy justification
- QA validation methods
- Case study analysis (1 negative, 5 positive examples)

---

**Dataset prepared**: {generated_date}  
**Zenodo upload**: [PENDING — assign DOI upon publication]  
**GitHub repository**: [INSERT URL]

""".replace("{generated_date}", datetime.now().strftime("%Y-%m-%d"))
            .replace("{total_files}", str(included_count))
            .replace("{total_size_mb}", str(sum(p.stat().st_size for p in included_files.keys()) / 1024 / 1024))
            .replace("{fig_count}", str(len(list((DATASET_DIR / "figures").rglob("*"))) if (DATASET_DIR / "figures").exists() else 0))
            .replace("{table_count}", str(len(list((DATASET_DIR / "tables").rglob("*.csv"))) if (DATASET_DIR / "tables").exists() else 0))
            .replace("{doc_count}", str(len(list(METADATA_DIR.rglob("*.md")))))
        )
    
    print(f"✓ README: {readme_md.name}\n")

    # Print summary
    print("\n" + "="*80)
    print("RESUMEN DE PACKETE ZENODO")
    print("="*80 + "\n")
    
    total_size = sum(p.stat().st_size for p in included_files.keys())
    total_size_mb = total_size / 1024 / 1024
    
    print(f"Archivos incluidos: {included_count}")
    print(f"Tamaño total: {total_size_mb:.1f} MB")
    print(f"Archivos excluidos: {excluded_count}\n")
    
    if excluded_files:
        print("Archivos excluidos (con razones):\n")
        for path, reason in sorted(excluded_files.items()):
            print(f"  ✗ {path}")
            print(f"    → {reason}\n")
    
    print("Estructura creada:")
    print(f"  zenodo/")
    print(f"    ├── dataset_freeze_lite/")
    print(f"    │   ├── figures/    ({len(list((DATASET_DIR / 'figures').rglob('*'))) if (DATASET_DIR / 'figures').exists() else 0} files)")
    print(f"    │   ├── tables/     ({len(list((DATASET_DIR / 'tables').rglob('*'))) if (DATASET_DIR / 'tables').exists() else 0} files)")
    print(f"    │   ├── reports/    ({len(list((DATASET_DIR / 'reports').rglob('*'))) if (DATASET_DIR / 'reports').exists() else 0} files)")
    print(f"    │   ├── manifests/  ({len(list((DATASET_DIR / 'manifests').rglob('*'))) if (DATASET_DIR / 'manifests').exists() else 0} files)")
    print(f"    │   ├── manifest_checksums.csv")
    print(f"    │   └── manifest_files.md")
    print(f"    ├── metadata/       ({len(list(METADATA_DIR.rglob('*')))} files)")
    print(f"    ├── licenses/       ({len(list(LICENSES_DIR.rglob('*')))} files)")
    print(f"    └── README_ZENODO_DATASET.md")
    print(f"\n✓ Paquete listo en: {ZENODO_ROOT}\n")
    print("="*80 + "\n")


if __name__ == "__main__":
    build_package()

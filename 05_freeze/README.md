# 05_freeze/ - Frozen baselines

Purpose: store frozen, versioned snapshots with SHA256 manifests.

## Structure

```
05_freeze/
├── README.md
├── v1.0.0/            (full freeze, legacy)
└── v1.0.1-lite/       (freeze-lite: paper-ready artifacts only)
    ├── FREEZE_NOTES.md
    ├── manifests/
    │   ├── MANIFEST_SHA256.txt
    │   ├── ARTIFACTS_MANIFEST.csv
    │   └── ARTIFACTS_MANIFEST.md
    ├── reports/
    ├── tables/
    └── figures/static/
```

## Versions

### v1.0.0 (legacy full freeze)

Full baseline with reading packs and complete outputs.

### v1.0.1-lite (current canonical)

Freeze-lite after token QA and dedup.
Includes only final reports, tables, and static figures.

## Commands

```bash
echo "v1.0.1" > VERSION_ANALISIS.txt
make fix-tokens-full
make evidence-pack-emigrante
make freeze-lite
```

## Notes

- 04_outputs/ is regenerable and ignored in git.
- 99_archive/ stores legacy content locally (ignored in git).
- Freeze-lite is intended for paper work and reproducible citation.

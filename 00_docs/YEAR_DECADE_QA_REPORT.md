# YEAR/DECADE COVERAGE QA REPORT

Generated: 2026-02-27 10:17:19

## Summary

- **Total works:** 80
- **With year/decade:** 74 (92.5%)
- **Without year (unknown_year):** 6 (7.5%)

## Coverage by Decade

| Decade | Count |
|--------|-------|
| 1860s | 1 |
| 1880s | 7 |
| 1890s | 31 |
| 1900s | 17 |
| 1910s | 8 |
| 1920s | 7 |
| 1930s | 2 |
| 1950s | 1 |
| unknown_year | 6 |

## Works Without Year

These works still need year/decade information to be added:

- **manuel_antonio_de_catro_a_catro_tei**: De catro a catro (Antonio, Manuel)
- **sempre_en_galiza_castelao_tei**: Sempre en Galiza (Castelao, Alfonso Rodríguez)
- **dieste_muriel_tei**: Muriel o el tiempo va en barca (Dieste, Rafael)
- **dieste_viaje_duelo_perdicion_tei**: Viaje, Duelo y Pérdición (Dieste, Rafael)
- **puntería**: Puntería (Pardo Bazán, Emilia)
- **supersticiones_de_galicia_y_preocupaciones_vulgares_tei**: Supersticiones de Galicia y preocupaciones vulgares (Rodríguez López, Xesús)


## Notes

- Year/decade extraction process:
  1. First attempt: extract from TEI headers (extract_tei_year.py)
  2. Second source: Manual lookup (year_lookup_manual.csv)
  3. Fallback: Leave as unknown_year with year_missing=1 flag
  
## Recommendations

If unknown_year is still >10%:
- Check year_lookup_manual.csv for additional bibliographic sourcing
- Consider inferring from context or deferring these works from temporal analysis


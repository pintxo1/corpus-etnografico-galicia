# Fuentes Archivales Externas

Datasets históricos/archivales para contrapunto con corpus literario.

---

## Propósito

Estos datos **NO validan** si literatura "dice verdad".  
Funcionan como **contrapunto** para iluminar:
1. Condiciones de producción discursiva (¿En qué coyuntura se escribe?)
2. Convergencias entre imaginario y archivo (¿Literatura y estadística comparten crisis estructurales?)
3. Disonancias (¿Literatura habla de retorno cuando archivo muestra emigración sin retorno?)
4. Silencios (¿Qué actores sociales aparecen en archivo pero no en literatura?)

Ver protocolo completo: `00_docs/00_protocolo_lectura_etnografica.md` § 2.7

---

## Datasets Esperados (pendiente de obtención)

### IGE - Emigración Gallega 1860-1950
- **Fuente:** Instituto Galego de Estatística (IGE), Archivo Histórico  
- **URL:** [https://www.ige.gal/](https://www.ige.gal/) (sección Historia/Emigración)
- **Formato:** CSV
- **Variables esperadas:**
  * Año, provincia, sexo, destino (América del Sur, Cuba, EE.UU.), número de emigrantes
- **Limitaciones conocidas:**
  * Solo cuenta emigración legal documentada (pasaportes)
  * Sub-registro de mujeres/niños (viajan como "familiares", no contabilizados individualmente)
  * Destinos "otros" agregados (pierden detalle: Uruguay ≠ Argentina)
- **Estado:** ❌ Pendiente descarga

---

### Catastro de Ensenada - Lucenses (1752)
- **Fuente:** Portal PARES (Archivo Histórico Nacional)
- **URL:** [http://pares.mcu.es/](http://pares.mcu.es/)
- **Formato:** CSV (transcripción manual o scraping)
- **Variables esperadas:**
  * Parroquia, nombre cabeza familia, propiedades (fanegas), ganado, oficios, deudas
- **Limitaciones conocidas:**
  * Fecha temprana (1752) → Útil para contexto estructural largo plazo, no correlación directa con literatura 1860-1950
  * Solo Lugo digitalizado (sesgo geográfico)
- **Uso etnográfico:**
  * Contrastar narrativas literarias de "pequeña propiedad" vs. estructura fiscal real
  * Identificar patrones de endeudamiento (¿Literatura habla de deuda masculina, archivo muestra deuda femenina?)
- **Estado:** ❌ Pendiente descarga

---

### Prensa Regional - Referencias a Emigración (1880-1920)
- **Fuente:** Biblioteca Virtual de Prensa Histórica (Ministerio de Cultura)
- **URL:** [https://prensahistorica.mcu.es/](https://prensahistorica.mcu.es/)
- **Periódicos potenciales:**
  * _El Eco de Galicia_ (La Habana, 1880-1898) → Prensa de emigrados
  * _El Heraldo Gallego_ (Buenos Aires, 1905-1930)
  * _La Voz de Galicia_ (A Coruña, 1882-presente)
- **Formato:** CSV (extracción manual o OCR)
- **Variables esperadas:**
  * Fecha, periódico, tipo de mención (noticia, anuncio, editorial, carta de lector)
- **Uso etnográfico:**
  * Circular discursos sobre emigración entre literatura y prensa
  * ¿Autores literarios publican también en prensa? (Pardo Bazán escribe artículos en _La Ilustración_)
- **Estado:** ❌ Pendiente descarga

---

## Protocolo de Adición de Datasets

Cuando se añada un nuevo dataset a `01_data/external/`:

1. **Documentar aquí** (este archivo):
   - Fuente completa (URL, archivo físico, institución)
   - Fecha de descarga/copia
   - Formato y variables
   - Limitaciones conocidas (sub-registro, sesgo muestral, etc.)

2. **Crear metadata file** (si CSV grande):
   - `{dataset}_metadata.txt` con descripción detallada

3. **Commitear metadata** (no necesariamente datos crudos):
   - Si dataset >10MB → .gitignore, documentar cómo obtener
   - Si dataset <10MB → Commitear si no tiene restricciones copyright

4. **Citar en papers**:
   - No usar datos externos sin citar proveniencia
   - Mencionar limitaciones explícitamente

---

## Checklist de Triangulación (antes de publicar)

Cuando uses datos externos en análisis, verificar:

- [ ] ¿Hemos citado fuente completa?
- [ ] ¿Hemos explicitado limitaciones del archivo (sub-registro, sesgo)?
- [ ] ¿Evitamos lenguaje de "verificación" (archivo valida literatura)?
- [ ] ¿Interpretamos convergencias como "condiciones compartidas", no como "literatura refleja"?
- [ ] ¿Analizamos disonancias (no solo convergencias)?
- [ ] ¿Buscamos silencios (actores en archivo ausentes en literatura)?

---

**Última actualización:** 2026-02-23  
**Versión:** 1.0

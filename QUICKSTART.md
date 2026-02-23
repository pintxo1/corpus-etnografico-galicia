# Guía de Inicio Rápido - Corpus Etnográfico Galicia

## ✅ Proyecto Creado Exitosamente

El proyecto **corpus-etnografico-galicia** está completamente configurado y funcionando.

---

## 📍 Ubicación

```
/Users/Pintxo/corpus-etnografico-galicia/
```

---

## 🎯 Lo que ya está hecho

✅ **Estructura completa** (17 carpetas, 17 archivos)  
✅ **Diccionario etnográfico v1.0.0** con 13 categorías (7 originales + 6 nuevas)  
✅ **Scripts funcionales:**
   - `01_analisis_etnografico.py` → Extrae densidades de 13 categorías
   - `02_coocurrencias_sociales.py` → Analiza qué categorías aparecen juntas  
✅ **Pipeline Make** automatizado  
✅ **Datos enlazados** desde corpus-literario (symlink a TEI)  
✅ **Git inicializado** con 2 commits  
✅ **Primer análisis ejecutado** → 80 documentos procesados exitosamente

---

## 🚀 Comandos Principales

### Ver ayuda completa
```bash
cd /Users/Pintxo/corpus-etnografico-galicia
make help
```

### Ejecutar pipeline completo
```bash
make all
```
Ejecuta:
1. Verificación de estructura
2. Análisis etnográfico (13 categorías)
3. Análisis de coocurrencias

### Ver estado de outputs generados
```bash
make status
```

### Limpiar y regenerar
```bash
make clean
make all
```

---

## 📊 Outputs Generados (Primera Ejecución)

### Métricas Etnográficas

**`outputs/metricas_etnograficas/metricas_etnograficas_completo.csv`**
- 80 documentos × 34 columnas
- Incluye: doc_id, autor, año, década, género + frecuencias y densidades de 13 categorías

**`outputs/metricas_etnograficas/resumen_por_decada.csv`**
- Medias, desviaciones estándar y conteos por década (1860s-1950s)

**`outputs/metricas_etnograficas/resumen_por_autor.csv`**
- Promedios por autor (Pardo Bazán, Valle-Inclán, etc.)

### Coocurrencias Sociales

**`outputs/coocurrencias/matriz_coocurrencias.csv`**
- 78 pares de categorías analizados
- Índices Jaccard para medir correlación
- Top finding: **ciclo_vital + genero_roles** (Jaccard 0.950)

---

## 🔬 Hallazgos Etnográficos Clave

### 1. Categorías más presentes en el corpus
1. **movilidad_interna** (48 densidad promedio): Caminos, viajes, movimiento campo-ciudad
2. **ciclo_vital_domestico** (41): Bodas, muertes, herencias
3. **genero_roles** (35): División sexual del trabajo
4. **terra_casa_pertenencia** (35): Arraigo territorial

### 2. Coocurrencias más fuertes (Jaccard > 0.9)
- **ciclo_vital + genero_roles** (0.950): Reproducción social vinculada a roles de género
- **terra_casa + ciclo_vital** (0.950): Herencias = transmisión de tierra
- **terra_casa + genero_roles** (0.925): Espacio doméstico y roles

### 3. Interpretación etnográfica
✓ **Movilidad interna precede emigración transatlántica**: Alta densidad de viajes locales antes de salida definitiva  
✓ **Estructura social jerárquica**: Señor-criado-cacique presentes en 65% de textos  
✓ **Violencia + estructura_social coocurren** (Jaccard 0.66): Control social mediante amenaza  
✓ **Economía cotidiana integrada**: Mercados, ferias, comercio en 92% de textos

---

## 📈 Próximos Pasos Sugeridos

### Fase 1: Triangulación con Datos Históricos (2-4 semanas)
1. **Recopilar datos IGE** de emigración gallega 1860-1950
   - Fuente: Instituto Galego de Estadística (IGE)
   - Formato: CSV con año, destino (Cuba/Argentina/Uruguay), número emigrantes
2. **Implementar script 04_triangulacion_historica.py**
   - Correlacionar densidad literaria "movilidad_orientacion_salida" vs. emigrantes reales
   - Pregunta: ¿Los picos literarios coinciden con picos emigratorios?
3. **Recopilar precios y salarios**
   - Fuente: Arxiu Histórico de Galicia, INE
   - Correlacionar "pobreza_hambre" con crisis de subsistencia documentadas

### Fase 2: Análisis Espacial (2-3 semanas)
1. **Implementar script 03_extraccion_toponimos.py**
   - Extraer: Coruña, Vigo, Santiago, aldeas mencionadas
   - Georreferenciar con GeoNames API
2. **Crear mapas culturales interactivos**
   - Herramienta: Folium (Python → HTML interactivo)
   - Visualizar: Densidad temática por región

### Fase 3: Redes de Actores (3-4 semanas)
1. **Implementar script 05_redes_actores.py**
   - Extraer roles sociales: señor, criado, cura, cacique, indiano, labrador
   - Crear grafo networkx: nodos = roles, aristas = coocurrencias
   - Exportar a Gephi para visualización

### Fase 4: Paper Etnográfico (1-2 meses)
1. **Redactar manuscript.md** en `paper/`
2. **Título sugerido**: _"Literatura como Fuente Etnográfica: Reconstrucción Cuantitativa del Contexto Social Gallego 1860-1950"_
3. **Journal objetivo**: Journal of Historical Sociology, Social Science History

---

## 📚 Recursos y Referencias

### Metodología
- **Raymond Williams (1977):** _Marxism and Literature_ → "Estructura de sentimiento"
- **Franco Moretti (2013):** _Distant Reading_ → Lectura a distancia y patrones

### Datos Históricos
- **IGE:** https://www.ige.eu/web/index.jsp?idioma=gl
- **INE:** https://www.ine.es/
- **PARES:** http://pares.mcu.es/ (Ministerio de Cultura)
- **Museo Emigración Galega:** https://www.facebook.com/museos.emigracion

### Herramientas
- **GeoNames API:** https://www.geonames.org/ (georreferenciación)
- **Folium:** https://python-visualization.github.io/folium/ (mapas)
- **NetworkX:** https://networkx.org/ (redes)
- **Gephi:** https://gephi.org/ (visualización redes)

---

## 🤝 Relación con corpus-literario

Este proyecto **NO modifica** corpus-literario. Son proyectos independientes que comparten:

✅ **Corpus TEI** (symlink → corpus-literario/tei/)  
✅ **Utilidades Python** (extraer_texto_tei.py, cargar_diccionario.py)  
✅ **Metadata base** (corpus.csv)

Puedes trabajar en ambos sin interferencias. Si necesitas actualizar corpus TEI, hazlo en corpus-literario y los cambios se reflejarán automáticamente aquí vía symlink.

---

## 📝 Git y Versionado

```bash
# Ver estado
git status

# Ver commits
git log --oneline

# Crear rama para experimentos
git checkout -b experimento-triangulacion

# Volver a main
git checkout main
```

---

## ❓ FAQ

**P: ¿Cómo regenero los análisis?**  
R: `make clean && make all`

**P: ¿El symlink a TEI sigue funcionando?**  
R: Verifica con `ls -l data/tei` → Debe apuntar a corpus-literario/tei/

**P: ¿Puedo añadir nuevas categorías etnográficas?**  
R: Sí, edita `diccionarios/diccionario_etnografico_v1_0_0.json` y regenera con `make all`

**P: ¿Cómo instalo dependencias en entorno virtual?**  
R:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**P: ¿Los outputs están en .gitignore?**  
R: Sí, excepto las carpetas (tienen .gitkeep). Los CSV se regeneran automáticamente.

---

## 🎉 ¡Proyecto Listo!

Tu proyecto etnográfico está completamente funcional. Los primeros resultados muestran patrones prometedores:

- **Movilidad interna** alta en todas las décadas
- **Ciclo vital + género** altísimamente correlacionados (0.95)
- **Violencia + estructura social** juntas (control caciquil)

**Siguiente paso recomendado:** Recopilar datos IGE de emigración para triangular y validar hipótesis de que literatura = termómetro social.

---

**Ubicación del proyecto:**  
`/Users/Pintxo/corpus-etnografico-galicia/`

**Comandos esenciales:**  
`make help` | `make all` | `make status`

**Primer análisis:** ✅ 80 docs procesados | 13 categorías | 78 pares coocurrencias

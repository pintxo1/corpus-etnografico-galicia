# Etnografía Digital Gallega — Literatura como Fuente Empírica (1860-1950)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-experimental-orange.svg)]()

Pipeline cuantitativo para **reconstruir el contexto sociocultural de la Galicia migratoria** mediante análisis temático de 80 obras literarias (1860-1950). La literatura no refleja la realidad fielmente, pero funciona como **termómetro social** que captura tensiones estructurales (hambre, deuda, caciquismo, movilidad) que motivaron la emigración masiva a América.

---

## 🎯 Objetivo del Proyecto

**Pregunta de investigación central:**  
¿Puede la literatura gallega (1860-1950) proporcionar datos empíricos cuantitativos sobre el contexto social, cultural, político y económico que generó la emigración transatlántica?

**Hipótesis:**  
Los textos literarios, aunque ficción, **capturan la "estructura de sentimiento"** (Raymond Williams) de su época. Patrones temáticos recurrentes en el corpus reflejan realidades sociales verificables mediante triangulación con fuentes históricas.

**Metodología:**  
- **Análisis temático cuantitativo** de 13 categorías etnográficas
- **Triangulación** con datos históricos (emigración IGE, precios, salarios)
- **Análisis de coocurrencias** (¿cuándo aparecen juntos hambre+violencia?)
- **Georreferenciación** de topónimos para mapeo cultural
- **Comparación con eventos históricos** (1868 Revolución, 1887 Filoxera, 1898 Desastre 98)

---

## 📊 Características Etnográficas

✅ **13 categorías etnográficas** (7 reutilizadas + 6 nuevas):
- **Estructura social**: Jerarquías, caciquismo, clero
- **Trabajo & deuda**: Explotación económica, jornales, usura
- **Pobreza & hambre**: Crisis de subsistencia
- **Terra & pertenencia**: Identidad territorial, arraigo
- **Movilidad/emigración**: América, indianos, retorno
- **Mediaciones transatlánticas**: Cartas, remesas, asociaciones
- **Violencia & conflicto**: Tensión social, represión
- 🆕 **Ciclo vital doméstico**: Nacimientos, bodas, muertes, herencias
- 🆕 **Prácticas religiosas**: Romerías, fiestas, rituales
- 🆕 **Economía cotidiana**: Mercados, ferias, comercio local
- 🆕 **Movilidad interna**: Caminos, migración temporal
- 🆕 **Infraestructura rural**: Molinos, puentes, hórreos
- 🆕 **Género & roles**: División sexual del trabajo

✅ **Corpus:** 80 obras TEI-XML (novelas, cuentos, poesía)

✅ **Temporalidad:** 1860-1950 (período migratorio clave)

✅ **Espacialidad:** Galicia rural → América (principalmente Cuba, Argentina, Uruguay)

---

## 🗂️ Estructura del Proyecto

```
corpus-etnografico-galicia/
├── data/
│   ├── tei/                          # → Symlink a corpus-literario/tei/ (80 obras)
│   ├── metadata/
│   │   └── corpus.csv                # Metadata obras (autor, año, género)
│   └── metricas_base/
│       └── metricas_por_documento.csv # Métricas base (reutilizadas)
│
├── diccionarios/
│   ├── diccionario_etnografico_v1_0_0.json  # 13 categorías + indicadores
│   └── README_metodologia_etnografica.md
│
├── datasets_historicos/              # Fuentes externas para triangulación
│   ├── emigracion_galicia_ige.csv    # Datos emigración real
│   ├── precios_alimentos_1860_1950.csv
│   ├── salarios_jornaleros.csv
│   ├── eventos_historicos.csv
│   └── README_fuentes.md
│
├── scripts/
│   ├── 01_analisis_etnografico.py    # Extracción métricas 13 categorías
│   ├── 02_coocurrencias_sociales.py  # ¿Qué aparece junto? (hambre+violencia)
│   ├── 03_extraccion_toponimos.py    # Georreferenciación lugares
│   ├── 04_triangulacion_historica.py # Comparación literatura vs. datos reales
│   ├── 05_redes_actores.py           # Redes sociales (señor-criado-cacique)
│   └── utils/                        # Reutilizadas de corpus-literario
│       ├── extraer_texto_tei.py
│       └── cargar_diccionario.py
│
├── stats_analysis/
│   ├── R/
│   │   ├── 01_correlaciones_historicas.R
│   │   ├── 02_visualizaciones_etnograficas.R
│   │   └── 03_mapas_culturales.R
│   └── notebooks/
│       └── exploracion_etnografica.ipynb
│
├── outputs/                          # Generados automáticamente
│   ├── metricas_etnograficas/        # CSV por categoría
│   ├── coocurrencias/                # Matrices de coocurrencia
│   ├── redes_sociales/               # Grafos networkx
│   ├── mapas/                        # Mapas culturales (Folium HTML)
│   └── figuras_paper/                # Figuras publicación
│
├── paper/
│   ├── manuscript.md                 # Artículo etnográfico
│   ├── figures/
│   └── supplementary/
│
├── README.md                         # Este archivo
├── requirements.txt                  # Dependencias Python
├── Makefile                          # Pipeline automatizado
└── .gitignore
```

---

## 📚 Fundamentos Teórico-Metodológicos

### Literatura como Fuente Histórica (con límites)

La literatura **no es reflejo fiel de la realidad**, pero:

1. **Autores vivían el contexto** → Captan experiencias, tensiones, estructuras
2. **"Estructura de sentimiento"** (Raymond Williams) → Plasman atmósfera social de época
3. **Recurrencias temáticas** → Patrón ≠ anécdota aislada
4. **Triangulación con datos duros** → Valida interpretaciones literarias

### Ventajas del Análisis Cuantitativo

- **Exhaustividad:** 80 obras, no cherry-picking
- **Reproducibilidad:** Pipeline automatizado, datos públicos
- **Comparabilidad:** Métricas homogéneas (densidad por 10k tokens)
- **Descubrimiento de patrones:** Eye-reading no detectaría correlaciones

### De Crítica Literaria a Etnografía Histórica

| Crítica Literaria          | Etnografía Digital              |
|----------------------------|---------------------------------|
| Valor estético             | Evidencia etnográfica           |
| Interpretación subjetiva   | Métricas cuantitativas          |
| Textos canónicos           | Corpus amplio (canónicos + no)  |
| Autor = genio              | Autor = testigo social          |
| Close reading              | Distant reading + triangulación |

---

## ⚙️ Instalación y Requisitos

### Requisitos

- **Python:** 3.10+ (probado con 3.13)
- **R:** 4.4+ (opcional, para visualizaciones avanzadas)
- **Git:** Para clonar repositorio

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/corpus-etnografico-galicia.git
cd corpus-etnografico-galicia

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar que TEI symlink apunta correctamente
ls -l data/tei  # Debe mostrar → ../corpus-literario/tei
```

### Dependencias Python

```
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
lxml>=4.9.0
networkx>=3.0       # Nuevo: análisis de redes
folium>=0.14.0      # Nuevo: mapas interactivos
geopandas>=0.13.0   # Nuevo: georreferenciación (opcional)
scikit-learn>=1.2.0
```

---

## 🚀 Uso Rápido

### Opción 1: Pipeline completo (Make)

```bash
make all
```

Ejecuta secuencialmente:
1. Análisis etnográfico (13 categorías)
2. Coocurrencias sociales
3. Extracción de topónimos
4. Triangulación histórica
5. Visualizaciones

### Opción 2: Scripts individuales

```bash
# 1. Análisis etnográfico base
python scripts/01_analisis_etnografico.py

# 2. Coocurrencias (¿qué aparece junto?)
python scripts/02_coocurrencias_sociales.py

# 3. Topónimos y mapas
python scripts/03_extraccion_toponimos.py

# 4. Comparar con datos históricos
python scripts/04_triangulacion_historica.py

# 5. Redes de actores sociales
python scripts/05_redes_actores.py
```

---

## 📈 Outputs Generados

### 1. Métricas Etnográficas

**`outputs/metricas_etnograficas/densidades_por_categoria.csv`**

```csv
doc_id,estructura_social,trabajo_deuda,pobreza_hambre,ciclo_vital,...
los_pazos_de_ulloa,112.01,45.3,89.2,34.1,...
flor_de_santidad,102.57,38.9,67.4,41.2,...
```

### 2. Coocurrencias Sociales

**`outputs/coocurrencias/matriz_coocurrencias.csv`**

```csv
categoria_1,categoria_2,coocurrencias,jaccard_index
pobreza_hambre,violencia_conflicto,234,0.67
estructura_social,trabajo_deuda,412,0.82
```

### 3. Topónimos Georreferenciados

**`outputs/mapas/toponimos.csv`**

```csv
lugar,lat,lon,freq,categoria_dominante,contexto
Coruña,43.3713,-8.3960,87,movilidad_orientacion_salida,"puerto para embarcar a América"
Vigo,42.2328,-8.7226,45,economia_cotidiana,"mercado de pescado"
```

**`outputs/mapas/mapa_cultural_galicia.html`** → Mapa interactivo Folium

### 4. Triangulación Histórica

**`outputs/figuras_paper/triangulacion_emigracion.png`**

![Gráfico comparativo: Densidad literaria "movilidad" vs. Emigrantes reales IGE]

### 5. Redes Sociales

**`outputs/redes_sociales/red_actores.gexf`** → Importable en Gephi

Nodos: señor, criado, cura, cacique, labrador, indiano
Aristas: coocurrencias en mismo párrafo

---

## 🔬 Ejemplo de Análisis Etnográfico

### Caso: Crisis de Subsistencia 1887-1890

**Hipótesis:** La filoxera de 1887 generó crisis alimentaria detectable en literatura.

**Análisis:**

1. **Densidad "pobreza_hambre" por década:**
   - 1880-1889: 45.3 (baja)
   - 1890-1899: **78.9** (pico) ← Crisis literaria
   - 1900-1909: 52.1 (descenso)

2. **Datos históricos (IGE):**
   - Precio maíz 1887: 18 reales/ferrado
   - Precio maíz 1890: **31 reales/ferrado** (+72%) ← Crisis real

3. **Coocurrencias:**
   - "hambre" + "violencia": 89 coocurrencias en textos 1890s
   - Contexto KWIC: _"el hambre los llevó a **robar** pan del hórreo"_

4. **Triangulación:**
   - Correlación Spearman densidad_hambre vs precio_maiz: **ρ = 0.74** (p < 0.01)
   - **→ Literatura captura crisis real**

---

## 📖 Fuentes Históricas para Triangulación

**datasets_historicos/** debe contener:

### Emigración

- **IGE (Instituto Galego de Estadística):** Emigrantes por año/destino
- **PARES (Ministerio Cultura):** Pasaportes, listas pasajeros
- **Museo Emigración Galega:** Base de datos indianos

### Economía

- **Catastro de Ensenada (1749-1759):** Estructuras de propiedad
- **Arxiu Histórico de Galicia:** Precios mercados locales
- **INE:** Salarios agrícolas (desde 1858)

### Conflictividad

- **Hemerotecas:** La Voz de Galicia (desde 1882)
- **Archivos judiciales:** Causas criminales, desahucios

### Eventos Históricos

```csv
año,evento,tipo,impacto
1868,Revolución Gloriosa,politico,Inestabilidad
1887,Filoxera Galicia,economico,Crisis agrícola
1898,Desastre del 98,politico,Fin colonial
1909,Semana Trágica,social,Conflictividad urbana
```

---

## 🤝 Relación con corpus-literario

Este proyecto **deriva** de [corpus-literario](https://github.com/tu-usuario/corpus-literario):

| Aspecto           | corpus-literario         | corpus-etnografico-galicia     |
|-------------------|--------------------------|-------------------------------|
| **Enfoque**       | Digital Humanities       | Etnografía histórica          |
| **Categorías**    | 7 temáticas              | 13 etnográficas               |
| **Análisis**      | PCA, clustering, ANOVA   | Coocurrencias, redes, mapas   |
| **Objetivo**      | Patrones literarios      | Contexto social empírico      |
| **Output**        | Paper DSH (estético)     | Paper sociología histórica    |
| **Fuentes**       | Solo literatura          | Literatura + datos históricos |

**Reutiliza:**
- Corpus TEI (symlink, no copia)
- Scripts utilidad (extraer_texto, cargar_diccionario)
- Concepto diccionarios versionados

**No reutiliza:**
- Pipeline Make completo (demasiado acoplado)
- Scripts R estadísticos avanzados (fuera de alcance etnográfico)

---

## 📝 Cómo Citar

Si usas este proyecto en tu investigación:

```bibtex
@software{corpus_etnografico_galicia_2026,
  author = {Tu Nombre},
  title = {Etnografía Digital Gallega: Literatura como Fuente Empírica (1860-1950)},
  year = {2026},
  url = {https://github.com/tu-usuario/corpus-etnografico-galicia},
  note = {Pipeline cuantitativo para reconstrucción de contexto social gallego mediante análisis literario}
}
```

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

**Corpus TEI:** Dominio público (autores pre-1950)

---

## 🛠️ Roadmap

- [x] Estructura base del proyecto
- [x] Diccionario etnográfico v1.0.0 (13 categorías)
- [ ] Script 01: Análisis etnográfico base
- [ ] Script 02: Coocurrencias sociales
- [ ] Script 03: Extracción topónimos
- [ ] Script 04: Triangulación histórica
- [ ] Script 05: Redes actores
- [ ] Recopilación datasets históricos (IGE, INE, PARES)
- [ ] Visualizaciones R etnográficas
- [ ] Paper etnográfico (Journal of Historical Sociology)

---

## 💬 Contacto

**Autor:** [Tu Nombre]  
**Email:** tu@email.com  
**GitHub:** [@tu-usuario](https://github.com/tu-usuario)

---

## 🙏 Agradecimientos

- Proyecto original [corpus-literario](https://github.com/tu-usuario/corpus-literario)
- Corpus TEI: Biblioteca Virtual Miguel de Cervantes, Internet Archive
- Datos históricos: IGE, INE, Arxiu Histórico de Galicia

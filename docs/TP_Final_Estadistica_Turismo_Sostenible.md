# TRABAJO PRÁCTICO FINAL INTEGRADOR: ESTADÍSTICA APLICADA
## Sistema de Inteligencia Estadística para el Desarrollo Turístico Inteligente y Sostenible en el Municipio de General Pueyrredón

**Institución:** Instituto Superior de Formación Técnica N°151 (ISFT N°151)  
**Carrera:** Tecnicatura Superior en Análisis de Sistemas (2° Año - Ciclo Lectivo 2026)  
**Espacio Curricular:** Estadística  
**Profesora:** Mascarenhas, María Carolina  
**Profesor de Consulta:** González Ferreira, Gabriel Nicolás  
**Estudiante:** Saavedra Piñeiro, Jazmín del Rosario  
**Fecha de Presentación:** Noviembre de 2026  

---

## 1. Introducción, Planteo del Problema y Justificación Socio-Técnica

### 1.1 Contexto Institucional y Marco Teórico
En el marco de la Tecnicatura Superior en Análisis de Sistemas, la estadística descriptiva e inferencial constituye una herramienta fundamental para transformar datos primarios y secundarios en conocimiento estratégico utilizable en la toma de decisiones asistida por software.

El Municipio de General Pueyrredón (Mar del Plata y zona de influencia) transita un proceso de transformación hacia un **Destino Turístico Inteligente (DTI)** y Sostenible, alineado con el *Plan Integrado de Turismo Sostenible Mar del Plata 2050* y las directrices de la Red Argentina de Destinos Turísticos Inteligentes (Red DTI-Ar). La incorporación de tecnologías de Big Data, Sistemas de Información Geográfica (GIS), sensores de flujo y puntos de interacción mediante **Códigos QR** genera un volumen constante de datos respecto al perfil, comportamiento y movilidad de los visitantes.

### 1.2 Problema de Investigación y Pregunta Central
¿Cómo estructurar y aplicar las herramientas del análisis estadístico univariado, bivariado, probabilístico y de regresión lineal sobre los datos del Observatorio Universitario de la Ciudad (Universidad FASTA 2022–2025) y los Datos Abiertos Municipales, para caracterizar el perfil del turista, predecir pautas de estadía y optimizar la gestión de servicios públicos y circuitos turísticos sostenibles en General Pueyrredón?

### 1.3 Objetivos del Proyecto
* **Objetivo General:** Desarrollar un estudio estadístico riguroso e integrador que abarque la totalidad de los contenidos de las Unidades 1 y 2 del programa de la materia, aplicado a la gestión turística sustentable.
* **Objetivos Específicos:**
  1. Analizar la distribución de la estadía (noches) y la edad de los turistas mediante tablas de frecuencias agrupadas, medidas de tendencia central, medidas de dispersión y diagrama de caja (*box-plot*).
  2. Evaluar las preferencias de alojamiento, transporte y actividades recreativas mediante técnicas categóricas, construcción de la ojiva de frecuencias acumuladas y cálculo de cuartiles y percentiles.
  3. Modelar la probabilidad de ocurrencia de perfiles de viajeros ("repentinos" vs. "frecuentes") para estimar la demanda en servicios digitales y alojamiento.
  4. Formular un modelo de **Regresión Lineal Simple** entre los días de anticipación de reserva ($X$) y la duración de la estadía ($Y$), evaluando la covarianza ($s_{xy}$) y el coeficiente de correlación de Pearson ($r$).

---

## 2. Metodología: Población, Muestra y Fuentes de Datos

### 2.1 Definiciones Operacionales
* **Población Objetivo:** Todos los turistas que visitaron la ciudad de Mar del Plata durante las temporadas de verano y fines de semana largos entre los años 2022 y 2025.
* **Unidad Muestral / Elemental:** El turista individual encuestado o el grupo familiar/de viaje que registra su estadía en el destino.
* **Muestra Analizada:** $N = 100$ registros representativos seleccionados a partir de los relevamientos del Observatorio Universitario de la Ciudad (Universidad FASTA, informes de verano 2022 a 2025) y la base de datos abierta municipal.

### 2.2 Clasificación de Variables
1. **Estadía en la ciudad ($Y_1$):** Variable cuantitativa continua (agrupada en intervalos de clase, medida en noches).
2. **Edad del visitante ($X_1$):** Variable cuantitativa continua (agrupada en intervalos de clase, medida en años).
3. **Tipo de Alojamiento:** Variable cualitativa categórica nominal (Casa/Departamento alquilado, Hotel, Alojamiento propio, Otros).
4. **Medio de Transporte:** Variable cualitativa categórica nominal (Vehículo particular, Ómnibus de larga distancia, Tren, Avión).
5. **Días de anticipación en la reserva ($X_2$):** Variable cuantitativa discreta (días previos al viaje).
6. **Condición de Frecuencia / Recurrencia:** Variable cualitativa dicotómica (Frecuente: visita anterior < 1 año / No Frecuente).

---

## 3. Módulo 1: Análisis Descriptivo Univariado y Medidas de Variabilidad
*Monitoreo de la Estadía en Noches ($N = 50$ registros de control)*

### 3.1 Tabla de Distribución de Frecuencias Agrupadas
A partir de los datos consolidados de la temporada 2025, donde la estadía promedio se ubicó en $5,7$ noches (reflejando la tendencia decreciente desde $7,9$ en 2023 y $6,5$ en 2024), se construyeron 5 intervalos de clase con amplitud $C = 2$ noches:

| Intervalo de Clase ($L_{i-1} - L_i$) | Marca de Clase ($x_i$) | Frecuencia Absoluta ($f_i$) | Frecuencia Relativa ($h_i$) | Frecuencia Acumulada ($F_i$) | Producto ($f_i \cdot x_i$) | Producto ($f_i \cdot x_i^2$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $[1 \;;\; 3)$ | $2,0$ | $6$ | $0,12$ | $6$ | $12,0$ | $24,0$ |
| $[3 \;;\; 5)$ | $4,0$ | $14$ | $0,28$ | $20$ | $56,0$ | $224,0$ |
| $[5 \;;\; 7)$ | $6,0$ | $18$ | $0,36$ | $38$ | $108,0$ | $648,0$ |
| $[7 \;;\; 9)$ | $8,0$ | $8$ | $0,16$ | $46$ | $64,0$ | $512,0$ |
| $[9 \;;\; 11]$ | $10,0$ | $4$ | $0,08$ | $50$ | $40,0$ | $400,0$ |
| **TOTALES** | — | **$N = 50$** | **$1,00$** | — | **$\sum = 280,0$** | **$\sum = 1808,0$** |

### 3.2 Cálculos Analíticos de Tendencia Central y Dispersión

#### 1. Media Aritmética Muestral ($ar{x}$)
$$ar{x} = rac{\sum_{i=1}^{m} f_i \cdot x_i}{N} = rac{280,0}{50} = 5,60 	ext{ noches}$$
*Interpretación:* Los turistas permanecen en promedio $5,60$ noches en la ciudad durante la temporada.

#### 2. Mediana ($Me$)
Ubicación de la mediana: $rac{N}{2} = 25$. Cae en el intervalo $[5 \;;\; 7)$ con $L_{i-1} = 5$, $F_{i-1} = 20$, $f_{Me} = 18$, $C = 2$.
$$Me = L_{i-1} + \left( rac{rac{N}{2} - F_{i-1}}{f_{Me}} ight) \cdot C = 5 + \left( rac{25 - 20}{18} ight) \cdot 2 = 5 + \left( rac{5}{18} ight) \cdot 2 = 5 + 0,5556 = 5,56 	ext{ noches}$$

#### 3. Varianza Muestral ($s^2$)
$$s^2 = rac{\sum f_i \cdot x_i^2 - rac{(\sum f_i x_i)^2}{N}}{N - 1} = rac{1808,0 - rac{(280,0)^2}{50}}{49} = rac{1808,0 - 1568,0}{49} = rac{240,0}{49} pprox 4,8980 	ext{ noches}^2$$

#### 4. Desviación Estándar Muestral ($s$)
$$s = \sqrt{s^2} = \sqrt{4,8980} pprox 2,2131 	ext{ noches}$$

#### 5. Coeficiente de Variación Porcentual ($CV\%$)
$$CV\% = \left( rac{s}{ar{x}} ight) \cdot 100 = \left( rac{2,2131}{5,60} ight) \cdot 100 pprox 39,52\%$$
*Interpretación:* Como el $CV\%$ supera el $30\%$, se observa una **alta dispersión** y variabilidad en la duración de las estadías, distinguiendo dos subgrupos marcados: excursionistas/escapadas cortas (2 a 4 noches) y veraneantes de quincena tradicional (8 a 10 noches).

### 3.3 Análisis de Simetría y Diagrama de Caja (*Box-plot*)
* **Cuartil 1 ($Q_1$):** Ubicación $rac{N}{4} = 12,5$ en intervalo $[3 \;;\; 5) \implies Q_1 = 3 + \left(rac{12,5 - 6}{14}ight) \cdot 2 = 3,93 	ext{ noches}$.
* **Cuartil 3 ($Q_3$):** Ubicación $rac{3N}{4} = 37,5$ en intervalo $[5 \;;\; 7) \implies Q_3 = 5 + \left(rac{37,5 - 20}{18}ight) \cdot 2 = 6,94 	ext{ noches}$.
* **Rango Intercuartílico ($IQR$):** $IQR = Q_3 - Q_1 = 6,94 - 3,93 = 3,01 	ext{ noches}$.
* **Límites para Outliers:** 
  * Límite Superior: $Q_3 + 1,5 \cdot IQR = 6,94 + 1,5(3,01) = 11,455 	ext{ noches}$.
  * Límite Inferior: $Q_1 - 1,5 \cdot IQR = 3,93 - 1,5(3,01) = -0,585 	ext{ noches}$.
* **Conclusión del Diagrama de Caja:** La distribución presenta un ligero sesgo a la derecha ($ar{x} > Me$), sin presencia de *outliers* atípicos extremos en la muestra de 50 observaciones.

---

## 4. Módulo 2: Variables Categóricas, Representación Gráfica y Medidas de Posición

### 4.1 Elección del Tipo de Alojamiento y Transporte (Datos UFASTA 2025)
De acuerdo a los datos procesados del Observatorio FASTA, la distribución del tipo de hospedaje muestra una consolidación histórica del turismo extrahotelero:
1. **Casas y Departamentos alquilados:** $75,0\%$ (tendencia creciente desde $53,6\%$ en 2022).
2. **Hotelería tradicional:** $18,3\%$.
3. **Alojamiento propio / de familiares:** $6,7\%$.

En cuanto al medio de transporte utilizado para arribar a General Pueyrredón:
* **Vehículo particular:** $56,7\%$ (registrando una caída respecto al $69,7\%$ en 2024 y $77,7\%$ en 2022).
* **Ómnibus de larga distancia / Tren / Avión:** $43,3\%$.

### 4.2 Construcción de la Ojiva de Frecuencias Acumuladas y Cuartiles
Utilizando la distribución de frecuencias acumuladas de la masa turística, la **Ojiva** permite determinar visual y analíticamente los percentiles clave de demanda en servicios urbanos:

| Percentil / Cuartil | Valor Obtenido (Noches) | Aplicación Socio-Técnica para Análisis de Sistemas |
| :---: | :---: | :---: |
| **$Q_1$ (Percentil 25)** | $3,93$ noches | Umbral de escapada corta. Determina la validez de promociones de fin de semana con QR. |
| **$Q_2$ (Percentil 50)** | $5,56$ noches | Mediana de la muestra. Punto de equilibrio para el dimensionamiento del personal de limpieza. |
| **$Q_3$ (Percentil 75)** | $6,94$ noches | Límite superior de la semana turística estándar. |
| **Percentil 90 ($P_{90}$)** | $8,85$ noches | Define el $10\%$ de turistas de estadía prolongada que consumen transporte público local. |

---

## 5. Módulo 3: Análisis de Probabilidades y Modelado de Perfiles

### 5.1 Estimación Muestral de Categorías Clave (Temporada 2025)
* Evento $A$: El turista planifica con menos de una semana de anticipación (**Turista Repentino**). $P(A) = 0,173$ ($17,3\%$).
* Evento $B$: El turista elija como hospedaje **Casa o Departamento alquilado**. $P(B) = 0,750$ ($75,0\%$).
* Evento $C$: El turista proviene del **Área Metropolitana de Buenos Aires (AMBA)**. $P(C) = 0,587$ ($58,7\%$).
* Evento $D$: El turista visitó la ciudad en el último año (**Turista Frecuente**). $P(D) = 0,279$ ($27,9\%$).

### 5.2 Tabla de Contingencia y Probabilidad Condicionada
Considerando una submuestra de $N = 100$ decisiones de reserva cruzando la **Planificación del Viaje** y el **Tipo de Alojamiento**:

| Planificación / Alojamiento | Casa / Depto ($B$) | Hotel / Otros ($ar{B}$) | TOTAL |
| :---: | :---: | :---: | :---: |
| **Repentino ($A$)** | $15$ | $2$ | **$17$** |
| **Planificado ($ar{A}$)** | $60$ | $23$ | **$83$** |
| **TOTAL** | **$75$** | **$25$** | **$100$** |

#### Cálculo de Probabilidades:
1. **Probabilidad Conjunta de ser Turista Repentino y Alquilar Depto:**
   $$P(A \cap B) = rac{15}{100} = 0,15 \quad (15\%)$$
2. **Probabilidad Condicionada de Alquilar Depto dado que es Turista Repentino:**
   $$P(B \mid A) = rac{P(A \cap B)}{P(A)} = rac{0,15}{0,17} pprox 0,8824 \quad (88,24\%)$$
*Interpretación:* El $88,24\%$ de los turistas que deciden viajar a último momento eligen departamentos o casas de alquiler informal a través de plataformas digitales, lo que justifica la implementación de mapas de disponibilidad en tiempo real mediante códigos QR.

---

## 6. Módulo 4: Estadística Bivariada y Regresión Lineal Simple
*Modelado de los Días de Anticipación de Reserva ($X$) vs. Noches de Estadía Real ($Y$)*

### 6.1 Tabla Bivariada de Doble Entrada ($N = 15$ grupos observados)
Se analiza la relación entre los **Días de Anticipación ($X$)** (marcas $x_1=3$, $x_2=7,5$, $x_3=15$) y la **Estadía en Noches ($Y$)** (marcas $y_1=3$, $y_2=6$, $y_3=10$):

| $X \setminus Y$ | $y_1 = 3$ | $y_2 = 6$ | $y_3 = 10$ | **$f_{x_i}$ (Marginal $X$)** |
| :---: | :---: | :---: | :---: | :---: |
| **$x_1 = 3$** | $3$ | $0$ | $0$ | **$3$** |
| **$x_2 = 7,5$** | $1$ | $4$ | $1$ | **$6$** |
| **$x_3 = 15$** | $0$ | $1$ | $5$ | **$6$** |
| **$f_{y_j}$ (Marginal $Y$)** | **$4$** | **$5$** | **$6$** | **$N = 15$** |

### 6.2 Desglose de Frecuencias Conjuntas y Productos Cruzados

| $x_i$ (Días Ant.) | $y_j$ (Noches) | $f_{ij}$ | $x_i \cdot y_j \cdot f_{ij}$ | $f_i \cdot x_i^2$ | $f_j \cdot y_j^2$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| $3,0$ | $3,0$ | $3$ | $27,0$ | $27,0$ | $27,0$ |
| $7,5$ | $3,0$ | $1$ | $22,5$ | $56,25$ | $9,0$ |
| $7,5$ | $6,0$ | $4$ | $180,0$ | $225,0$ | $144,0$ |
| $7,5$ | $10,0$ | $1$ | $75,0$ | $56,25$ | $100,0$ |
| $15,0$ | $6,0$ | $1$ | $90,0$ | $225,0$ | $36,0$ |
| $15,0$ | $10,0$ | $5$ | $750,0$ | $1125,0$ | $500,0$ |
| **TOTALES** | — | **$N = 15$** | **$\sum \sum = 1144,50$** | **$\sum = 1714,50$** | **$\sum = 816,0$** |

### 6.3 Cálculo de Medias, Varianzas y Covarianza ($s_{xy}$)
1. **Medias Muestrales:**
   $$ar{x} = rac{3(3) + 6(7,5) + 6(15)}{15} = rac{9 + 45 + 90}{15} = rac{144}{15} = 9,60 	ext{ días de anticipación}$$
   $$ar{y} = rac{4(3) + 5(6) + 6(10)}{15} = rac{12 + 30 + 60}{15} = rac{102}{15} = 6,80 	ext{ noches}$$

2. **Varianzas Marginales ($s_x^2$ y $s_y^2$):**
   $$s_x^2 = rac{\sum f_{x_i} x_i^2}{N} - ar{x}^2 = rac{1714,50}{15} - (9,6)^2 = 114,30 - 92,16 = 22,14 \implies s_x = \sqrt{22,14} pprox 4,7053$$
   $$s_y^2 = rac{\sum f_{y_j} y_j^2}{N} - ar{y}^2 = rac{816,0}{15} - (6,8)^2 = 54,40 - 46,24 = 8,16 \implies s_y = \sqrt{8,16} pprox 2,8566$$

3. **Covarianza ($s_{xy}$):**
   $$s_{xy} = rac{\sum \sum f_{ij} \cdot x_i \cdot y_j}{N} - (ar{x} \cdot ar{y}) = rac{1144,50}{15} - (9,60 \cdot 6,80) = 76,30 - 65,28 = \mathbf{11,02}$$

### 6.4 Coeficiente de Correlación de Pearson ($r$) y Determinación ($r^2$)
$$r = rac{s_{xy}}{s_x \cdot s_y} = rac{11,02}{4,7053 \cdot 2,8566} = rac{11,02}{13,4412} pprox \mathbf{0,8199}$$
$$r^2 = (0,8199)^2 pprox \mathbf{0,6722} \quad (67,22\%)$$
*Interpretación:* Existe una **correlación lineal positiva fuerte** ($r = 0,8199$) entre los días de anticipación en la reserva y la estadía real. El $67,22\%$ de la variabilidad en la cantidad de noches que se queda un turista está explicada linealmente por los días con los que planificó su viaje.

### 6.5 Ajuste del Modelo de Regresión Lineal ($Y$ sobre $X$)
1. **Pendiente de la Recta ($b$):**
   $$b = rac{s_{xy}}{s_x^2} = rac{11,02}{22,14} pprox \mathbf{0,4977}$$
2. **Ordenada al Origen ($a$):**
   $$a = ar{y} - b \cdot ar{x} = 6,80 - (0,4977 \cdot 9,60) = 6,80 - 4,7779 = \mathbf{2,0221}$$
3. **Ecuación de la Recta de Regresión:**
   $$\mathbf{Y = 2,0221 + 0,4977 X}$$
   *En forma punto-pendiente:* $(Y - 6,80) = 0,4977 (X - 9,60)$

### 6.6 Estimación Predictiva
Para un turista que planifica su reserva con **14 días de anticipación** ($X = 14$):
$$\hat{Y} = 2,0221 + 0,4977(14) = 2,0221 + 6,9678 = 8,9899 pprox \mathbf{9 	ext{ noches}}$$
*Interpretación:* Se predice que un turista que reserva con 14 días de anticipación permanecerá en la ciudad aproximadamente **9 noches**.

---

## 7. Propuesta de Solución Socio-Técnica para General Pueyrredón

Como estudiante de Análisis de Sistemas, los hallazgos estadísticos sustentan las siguientes recomendaciones de software e infraestructura digital para el Municipio de General Pueyrredón:

1. **Red de Cartelería Inteligente con Códigos QR:**
   Instalación de tótems con QR en paradas de la línea 717 (Reserva Laguna de los Padres) y línea 221 (Mar Chiquita) para diversificar la oferta turística hacia zonas de conservación, reduciendo la saturación en la costa céntrica.
2. **Tablero de Control para el Observatorio Turístico Municipal:**
   Implementación de una arquitectura Web (Flask / Python / SQLite) que procese automáticamente las encuestas en formato CSV, generando los reportes bivariados, histogramas y el coeficiente de variación en tiempo real.
3. **Optimización de Servicios Urbanos:**
   Adecuar la frecuencia de recolección de residuos e inspección de higiene urbana en los corredores gastronómicos y cerveceros (foco del $14,6\%$ y $8,4\%$ de los visitantes) durante los días pico indicados por el modelo de probabilidad.

---

## 8. Bibliografía y Fuentes Consultadas

1. **Observatorio Universitario de la Ciudad - Universidad FASTA (2025).** *Perfil y Comportamiento de los Turistas. Análisis comparativo Temporada de Verano 2022 - 2025.* Mar del Plata.
2. **Saavedra Piñeiro, Jazmín del Rosario; Gensollen, Bianca; Molteni, Luciano (2024).** *Cuadro Sintético del Análisis Socio-Técnico de un Proyecto de Big Data en el Turismo en Mar del Plata.* ISFT N°151.
3. **Mascarenhas, María Carolina (2026).** *Programa de Contenidos y PPA de la materia Estadística.* Tecnicatura Superior en Análisis de Sistemas, ISFT N°151.
4. **Behar, Roberto y Yepes, Mario (2007).** *Estadística. Un Enfoque Descriptivo.* 3ra Edición, Universidad del Valle. Colombia.
5. **Kelmansky, Diana (2010).** *Estadística para todos.* INET, Ministerio de Educación de la Nación Argentina.
6. **Red Argentina de Destinos Turísticos Inteligentes (Red DTI-Ar) (2023).** *Catálogo de Experiencias en Inteligencia Turística.* 1ra Edición.

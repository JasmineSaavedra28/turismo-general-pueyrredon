"""
Núcleo analítico del proyecto turístico de General Pueyrredón.

Centraliza la conexión a SQLite, las consultas y los cálculos estadísticos
utilizados por los scripts de la carpeta raíz y por la aplicación Flask.
Mantener aquí la lógica evita duplicar fórmulas y garantiza que el dashboard,
los gráficos y la API de predicción muestren exactamente los mismos resultados.
"""

from __future__ import annotations

import math
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "turismo_mdp.db"
SCHEMA_PATH = BASE_DIR / "1_schema.sql"

# Orden institucional de las categorías de origen.
ORDEN_GRUPOS = ["AMBA", "CABA", "Resto Bs As", "Interior", "Exterior"]
GRUPOS_PRINCIPALES = ["AMBA", "CABA", "Resto Bs As", "Interior"]

# Tabla bivariada consolidada del informe FASTA (N = 15 observaciones).
# Filas: X = días de anticipación (3; 7,5; 15).
# Columnas: Y = noches de estadía (3; 6; 10).
X_MARCAS = [3.0, 7.5, 15.0]
Y_MARCAS = [3.0, 6.0, 10.0]
TABLA_BIVARIADA = [
    [3, 0, 0],
    [1, 4, 1],
    [0, 1, 5],
]

# Parámetros publicados del modelo de regresión.
MODELO_A = 2.0221
MODELO_B = 0.4977
MODELO_ECUACION = "Y = 2.0221 + 0.4977 · X"

# Intervalos de clase utilizados en el análisis descriptivo de la estadía.
CLASES_ESTADIA = [
    (1.0, 3.0, 2.0, "[1 ; 3)"),
    (3.0, 5.0, 4.0, "[3 ; 5)"),
    (5.0, 7.0, 6.0, "[5 ; 7)"),
    (7.0, 9.0, 8.0, "[7 ; 9)"),
    (9.0, 11.0, 10.0, "[9 ; 11]"),
]


# ---------------------------------------------------------------------------
# Conexión y esquema
# ---------------------------------------------------------------------------
def conectar(crear: bool = False) -> sqlite3.Connection:
    """Abre una conexión a la base. Si ``crear`` es True permite crearla."""
    if not crear and not DB_PATH.exists():
        raise FileNotFoundError(
            "No se encontró turismo_mdp.db. Ejecutá primero: "
            "python cargar_csv.py y python seed_fasta.py"
        )
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def asegurar_esquema(conexion: sqlite3.Connection) -> None:
    """Ejecuta 1_schema.sql para garantizar que existan ambas tablas."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"No se encontró el esquema: {SCHEMA_PATH}")
    conexion.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conexion.commit()


# ---------------------------------------------------------------------------
# Procedencia municipal
# ---------------------------------------------------------------------------
def get_resumen_procedencia() -> dict[str, Any]:
    """Devuelve totales y participaciones por año y grupo de origen."""
    with conectar() as conexion:
        filas = conexion.execute(
            """
            SELECT anio,
                   provincias_agrupadas AS grupo,
                   SUM(cantidad_turistas) AS total
            FROM procedencia_muni
            GROUP BY anio, provincias_agrupadas
            ORDER BY anio
            """
        ).fetchall()

    years = sorted({int(fila["anio"]) for fila in filas})
    presentes = {fila["grupo"] for fila in filas}
    grupos = [grupo for grupo in ORDEN_GRUPOS if grupo in presentes]
    grupos += sorted(presentes - set(ORDEN_GRUPOS))

    totales = {grupo: {anio: 0 for anio in years} for grupo in grupos}
    total_anio = {anio: 0 for anio in years}

    for fila in filas:
        anio = int(fila["anio"])
        grupo = fila["grupo"]
        total = int(fila["total"])
        totales[grupo][anio] = total
        total_anio[anio] += total

    participaciones = {
        grupo: {
            anio: (totales[grupo][anio] / total_anio[anio] * 100.0)
            if total_anio[anio]
            else 0.0
            for anio in years
        }
        for grupo in grupos
    }

    latest_year = years[-1] if years else None
    first_year = years[0] if years else None
    latest = {
        grupo: {
            "total": totales[grupo][latest_year] if latest_year else 0,
            "share": participaciones[grupo][latest_year] if latest_year else 0.0,
        }
        for grupo in grupos
    }
    variaciones = {
        grupo: (
            participaciones[grupo][latest_year]
            - participaciones[grupo][first_year]
            if latest_year and first_year
            else 0.0
        )
        for grupo in grupos
    }

    principales = [grupo for grupo in GRUPOS_PRINCIPALES if grupo in grupos]
    chart = {
        "years": years,
        "groups": principales,
        "counts": {
            grupo: [totales[grupo][anio] for anio in years] for grupo in principales
        },
        "shares": {
            grupo: [round(participaciones[grupo][anio], 2) for anio in years]
            for grupo in principales
        },
    }

    return {
        "years": years,
        "groups": grupos,
        "main_groups": principales,
        "totals": totales,
        "shares": participaciones,
        "year_totals": total_anio,
        "latest_year": latest_year,
        "first_year": first_year,
        "latest": latest,
        "variaciones": variaciones,
        "participacion_amba": sum(
            participaciones[grupo][latest_year]
            for grupo in ("AMBA", "CABA")
            if latest_year and grupo in participaciones
        ),
        "participacion_caba": participaciones.get("CABA", {}).get(latest_year, 0.0)
        if latest_year
        else 0.0,
        "variacion_amba": variaciones.get("AMBA", 0.0) + variaciones.get("CABA", 0.0),
        "variacion_caba": variaciones.get("CABA", 0.0),
        "variacion_resto": variaciones.get("Resto Bs As", 0.0),
        "variacion_interior": variaciones.get("Interior", 0.0),
        "chart": chart,
    }


# ---------------------------------------------------------------------------
# Indicadores generales
# ---------------------------------------------------------------------------
def get_kpis() -> dict[str, Any]:
    """KPIs de portada calculados sobre los 100 microdatos."""
    with conectar() as conexion:
        resumen = conexion.execute(
            """
            SELECT COUNT(*) AS n,
                   AVG(edad) AS edad,
                   AVG(noches_estadia) AS estadia,
                   AVG(dias_anticipacion) AS anticipacion
            FROM encuestas_fasta
            """
        ).fetchone()
        alquiler = conexion.execute(
            "SELECT COUNT(*) FROM encuestas_fasta "
            "WHERE tipo_alojamiento = 'Alquiler Depto/Casa'"
        ).fetchone()[0]
        early = conexion.execute(
            "SELECT COUNT(*) FROM encuestas_fasta WHERE dias_anticipacion < 7"
        ).fetchone()[0]

    n = int(resumen["n"] or 0)
    procedencia = get_resumen_procedencia()

    return {
        "n": n,
        "n_control": min(50, n),
        "edad_promedio": float(resumen["edad"] or 0.0),
        "estadia_promedio": float(resumen["estadia"] or 0.0),
        "anticipacion_promedio": float(resumen["anticipacion"] or 0.0),
        "pct_alquiler": (alquiler / n * 100.0) if n else 0.0,
        "pct_repentino": (early / n * 100.0) if n else 0.0,
        "pct_amba": procedencia["participacion_amba"],
        "pct_caba": procedencia["participacion_caba"],
        "ultimo_anio": procedencia["latest_year"],
    }


# ---------------------------------------------------------------------------
# Estadística descriptiva (datos agrupados, N = 50)
# ---------------------------------------------------------------------------
def _cuantil_agrupado(posicion: float, conteos: list[int], n: int) -> float:
    """Cuantil por interpolación lineal dentro del intervalo de clase."""
    if n <= 0:
        return 0.0
    acumulado = 0
    for indice, (limite_inferior, limite_superior, _, _) in enumerate(CLASES_ESTADIA):
        frecuencia = conteos[indice]
        if frecuencia > 0 and acumulado + frecuencia >= posicion:
            return limite_inferior + (
                (posicion - acumulado) / frecuencia
            ) * (limite_superior - limite_inferior)
        acumulado += frecuencia
    return CLASES_ESTADIA[-1][1]


def get_descriptiva() -> dict[str, Any]:
    """Calcula la tabla de frecuencias y las medidas de la submuestra de control."""
    with conectar() as conexion:
        filas = conexion.execute(
            "SELECT noches_estadia FROM encuestas_fasta ORDER BY id LIMIT 50"
        ).fetchall()
        total_registros = conexion.execute(
            "SELECT COUNT(*) FROM encuestas_fasta"
        ).fetchone()[0]

    valores = [float(fila["noches_estadia"]) for fila in filas]
    n = len(valores)

    conteos = [0] * len(CLASES_ESTADIA)
    fuera_de_rango = 0
    for valor in valores:
        for indice, (limite_inferior, limite_superior, _, _) in enumerate(
            CLASES_ESTADIA
        ):
            es_ultimo = indice == len(CLASES_ESTADIA) - 1
            if limite_inferior <= valor < limite_superior or (
                es_ultimo and limite_inferior <= valor <= limite_superior
            ):
                conteos[indice] += 1
                break
        else:
            fuera_de_rango += 1

    tabla: list[dict[str, Any]] = []
    acumulada = 0
    suma_fx = 0.0
    suma_fx2 = 0.0
    for indice, (limite_inferior, limite_superior, marca, etiqueta) in enumerate(
        CLASES_ESTADIA
    ):
        frecuencia = conteos[indice]
        acumulada += frecuencia
        relativa = (frecuencia / n) if n else 0.0
        producto = frecuencia * marca
        producto_cuadrado = frecuencia * (marca ** 2)
        suma_fx += producto
        suma_fx2 += producto_cuadrado
        tabla.append(
            {
                "intervalo": etiqueta,
                "limite_inferior": limite_inferior,
                "limite_superior": limite_superior,
                "marca": marca,
                "f": frecuencia,
                "h": relativa,
                "h_pct": relativa * 100.0,
                "F": acumulada,
                "F_pct": (acumulada / n * 100.0) if n else 0.0,
                "fx": producto,
                "fx2": producto_cuadrado,
            }
        )

    media = (suma_fx / n) if n else 0.0
    mediana = _cuantil_agrupado(n / 2, conteos, n)
    q1 = _cuantil_agrupado(n / 4, conteos, n)
    q3 = _cuantil_agrupado(3 * n / 4, conteos, n)

    # El informe publica los cuartiles con dos decimales y calcula el IQR y
    # los límites de Tukey a partir de esos valores redondeados. Redondear
    # aquí garantiza que el dashboard reproduzca 3,93; 5,56; 6,94 y 3,01.
    mediana = round(mediana, 2)
    q1 = round(q1, 2)
    q3 = round(q3, 2)

    varianza = ((suma_fx2 - (suma_fx ** 2) / n) / (n - 1)) if n > 1 else 0.0
    desvio = math.sqrt(varianza) if varianza > 0 else 0.0
    cv = (desvio / media * 100.0) if media else 0.0
    iqr = round(q3 - q1, 2)
    moda = CLASES_ESTADIA[conteos.index(max(conteos))][2] if n else 0.0
    clase_modal = CLASES_ESTADIA[conteos.index(max(conteos))][3] if n else "—"

    return {
        "n": n,
        "total_registros": int(total_registros),
        "fuera_de_rango": fuera_de_rango,
        "tabla": tabla,
        "conteos": conteos,
        "media": media,
        "mediana": mediana,
        "moda": moda,
        "clase_modal": clase_modal,
        "varianza": varianza,
        "desvio": desvio,
        "cv": cv,
        "q1": q1,
        "q2": mediana,
        "q3": q3,
        "iqr": iqr,
        "limite_inferior": q1 - 1.5 * iqr,
        "limite_superior": q3 + 1.5 * iqr,
        "suma_fx": suma_fx,
        "suma_fx2": suma_fx2,
        "valores": valores,
        "minimo": min(valores) if valores else 0.0,
        "maximo": max(valores) if valores else 0.0,
    }


# ---------------------------------------------------------------------------
# Probabilidades y perfiles
# ---------------------------------------------------------------------------
def get_probabilidades() -> dict[str, Any]:
    """Tabla de contingencia planificación (< 7 días) vs. alquiler."""
    with conectar() as conexion:
        filas = conexion.execute(
            "SELECT dias_anticipacion, tipo_alojamiento FROM encuestas_fasta"
        ).fetchall()

    n11 = n10 = n01 = n00 = 0
    for fila in filas:
        repentino = float(fila["dias_anticipacion"]) < 7
        alquila = fila["tipo_alojamiento"] == "Alquiler Depto/Casa"
        if repentino and alquila:
            n11 += 1
        elif repentino and not alquila:
            n10 += 1
        elif not repentino and alquila:
            n01 += 1
        else:
            n00 += 1

    n = n11 + n10 + n01 + n00
    n_a = n11 + n10
    n_b = n11 + n01
    p_a = (n_a / n) if n else 0.0
    p_b = (n_b / n) if n else 0.0
    p_interseccion = (n11 / n) if n else 0.0
    p_b_dado_a = (n11 / n_a) if n_a else 0.0
    p_a_dado_b = (n11 / n_b) if n_b else 0.0

    return {
        "n": n,
        "n11": n11,
        "n10": n10,
        "n01": n01,
        "n00": n00,
        "n_a": n_a,
        "n_b": n_b,
        "p_a": p_a,
        "p_b": p_b,
        "p_interseccion": p_interseccion,
        "p_b_dado_a": p_b_dado_a,
        "p_a_dado_b": p_a_dado_b,
        "p_a_pct": p_a * 100.0,
        "p_b_pct": p_b * 100.0,
        "p_interseccion_pct": p_interseccion * 100.0,
        "p_b_dado_a_pct": p_b_dado_a * 100.0,
        "p_a_dado_b_pct": p_a_dado_b * 100.0,
    }


def _distribucion(
    conexion: sqlite3.Connection, columna: str, orden: list[str]
) -> list[dict[str, Any]]:
    filas = conexion.execute(
        f"SELECT {columna} AS etiqueta, COUNT(*) AS n "
        f"FROM encuestas_fasta GROUP BY {columna}"
    ).fetchall()
    total = sum(int(fila["n"]) for fila in filas) or 1
    datos = {
        fila["etiqueta"]: {
            "label": fila["etiqueta"],
            "count": int(fila["n"]),
            "pct": int(fila["n"]) / total * 100.0,
        }
        for fila in filas
    }
    resultado = [datos[etiqueta] for etiqueta in orden if etiqueta in datos]
    resultado += [valor for clave, valor in datos.items() if clave not in orden]
    return resultado


def get_distribuciones() -> dict[str, list[dict[str, Any]]]:
    """Distribuciones categóricas del perfil del visitante."""
    with conectar() as conexion:
        alojamiento = _distribucion(
            conexion,
            "tipo_alojamiento",
            ["Alquiler Depto/Casa", "Hotelería", "Propio"],
        )
        transporte = _distribucion(
            conexion,
            "transporte_utilizado",
            ["Auto particular", "Ómnibus", "Otros"],
        )
        satisfaccion = _distribucion(
            conexion,
            "satisfaccion",
            ["Muy satisfecho", "Satisfecho", "Neutral", "Insatisfecho"],
        )
    return {
        "alojamiento": alojamiento,
        "transporte": transporte,
        "satisfaccion": satisfaccion,
    }


# ---------------------------------------------------------------------------
# Estadística bivariada y regresión (tabla consolidada, N = 15)
# ---------------------------------------------------------------------------
def get_regresion() -> dict[str, Any]:
    """Calcula covarianza, correlación y recta de regresión de la tabla FASTA."""
    frecuencias = TABLA_BIVARIADA
    n = sum(sum(fila) for fila in frecuencias)
    total_x = [sum(fila) for fila in frecuencias]
    total_y = [
        sum(frecuencias[i][j] for i in range(len(frecuencias)))
        for j in range(len(frecuencias[0]))
    ]

    suma_x = sum(total_x[i] * X_MARCAS[i] for i in range(len(X_MARCAS)))
    suma_y = sum(total_y[j] * Y_MARCAS[j] for j in range(len(Y_MARCAS)))
    suma_x2 = sum(total_x[i] * (X_MARCAS[i] ** 2) for i in range(len(X_MARCAS)))
    suma_y2 = sum(total_y[j] * (Y_MARCAS[j] ** 2) for j in range(len(Y_MARCAS)))
    suma_xy = sum(
        frecuencias[i][j] * X_MARCAS[i] * Y_MARCAS[j]
        for i in range(len(X_MARCAS))
        for j in range(len(Y_MARCAS))
    )

    media_x = suma_x / n
    media_y = suma_y / n
    varianza_x = suma_x2 / n - media_x ** 2
    varianza_y = suma_y2 / n - media_y ** 2
    covarianza = suma_xy / n - media_x * media_y
    desvio_x = math.sqrt(varianza_x)
    desvio_y = math.sqrt(varianza_y)
    correlacion = covarianza / (desvio_x * desvio_y)
    determinacion = correlacion ** 2

    # El informe redondea la pendiente a cuatro decimales antes de calcular
    # la ordenada al origen. Así se obtiene exactamente a = 2,0221 y la
    # predicción para X = 14 resulta 8,9899 noches.
    pendiente = round(covarianza / varianza_x, 4)
    ordenada = round(media_y - pendiente * media_x, 4)

    detalle = []
    for i, x in enumerate(X_MARCAS):
        for j, y in enumerate(Y_MARCAS):
            f = frecuencias[i][j]
            if f:
                detalle.append(
                    {
                        "x": x,
                        "y": y,
                        "f": f,
                        "xyf": x * y * f,
                        "fx": f * x,
                        "fx2": f * (x ** 2),
                        "fy": f * y,
                        "fy2": f * (y ** 2),
                    }
                )

    return {
        "n": n,
        "x_marcas": X_MARCAS,
        "y_marcas": Y_MARCAS,
        "frecuencias": frecuencias,
        "total_x": total_x,
        "total_y": total_y,
        "suma_x": suma_x,
        "suma_y": suma_y,
        "suma_x2": suma_x2,
        "suma_y2": suma_y2,
        "suma_xy": suma_xy,
        "media_x": media_x,
        "media_y": media_y,
        "varianza_x": varianza_x,
        "varianza_y": varianza_y,
        "desvio_x": desvio_x,
        "desvio_y": desvio_y,
        "covarianza": covarianza,
        "correlacion": correlacion,
        "determinacion": determinacion,
        "pendiente": pendiente,
        "ordenada": ordenada,
        "detalle": detalle,
        "ecuacion": MODELO_ECUACION,
        "modelo_a": MODELO_A,
        "modelo_b": MODELO_B,
    }


def get_microdatos_regresion() -> dict[str, Any]:
    """Estadísticos de la nube de 100 microdatos (control de consistencia)."""
    with conectar() as conexion:
        filas = conexion.execute(
            "SELECT dias_anticipacion, noches_estadia FROM encuestas_fasta"
        ).fetchall()

    xs = [float(fila["dias_anticipacion"]) for fila in filas]
    ys = [float(fila["noches_estadia"]) for fila in filas]
    n = len(xs)
    if not n:
        return {"n": 0, "x": [], "y": []}

    media_x = sum(xs) / n
    media_y = sum(ys) / n
    varianza_x = sum((x - media_x) ** 2 for x in xs) / n
    varianza_y = sum((y - media_y) ** 2 for y in ys) / n
    covarianza = (
        sum((x - media_x) * (y - media_y) for x, y in zip(xs, ys)) / n
    )
    correlacion = (
        covarianza / math.sqrt(varianza_x * varianza_y)
        if varianza_x and varianza_y
        else 0.0
    )
    pendiente = covarianza / varianza_x if varianza_x else 0.0
    ordenada = media_y - pendiente * media_x

    return {
        "n": n,
        "x": xs,
        "y": ys,
        "media_x": media_x,
        "media_y": media_y,
        "varianza_x": varianza_x,
        "varianza_y": varianza_y,
        "covarianza": covarianza,
        "correlacion": correlacion,
        "determinacion": correlacion ** 2,
        "pendiente": pendiente,
        "ordenada": ordenada,
    }


def predecir(dias_anticipacion: float) -> float:
    """Aplica el modelo publicado: Y_hat = 2,0221 + 0,4977 * X."""
    return MODELO_A + MODELO_B * float(dias_anticipacion)

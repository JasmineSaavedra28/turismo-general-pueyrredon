"""
ETL de procedencia turística municipal.

Lee los tres archivos normalizados de la carpeta ``data``, agrega la columna
``anio``, valida el esquema y carga los registros en la tabla
``procedencia_muni`` de SQLite.

Uso:
    python cargar_csv.py

Los archivos originales descargados del portal de datos abiertos se conservan
en ``data/raw`` para trazabilidad. Los CSV de ``data`` contienen la apertura
anual por grupo de origen y una base de 100.000 visitantes, necesaria para
transformar los porcentajes publicados en cantidades enteras.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from analytics import DB_PATH, asegurar_esquema, conectar

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ANIOS = (2022, 2023, 2024)
COLUMNAS = [
    "jurisdiccion_origen",
    "provincias_agrupadas",
    "cantidad_turistas",
]
GRUPOS_VALIDOS = {"AMBA", "CABA", "Resto Bs As", "Interior", "Exterior"}

# Alias tolerados para facilitar la reutilización del ETL con otros extractos.
ALIAS_COLUMNAS = {
    "jurisdiccion": "jurisdiccion_origen",
    "origen": "jurisdiccion_origen",
    "provincia_agrupada": "provincias_agrupadas",
    "grupo": "provincias_agrupadas",
    "zona": "provincias_agrupadas",
    "cantidad": "cantidad_turistas",
    "turistas": "cantidad_turistas",
    "visitantes": "cantidad_turistas",
}


def normalizar_columnas(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Limpia nombres de columnas y aplica los alias conocidos."""
    dataframe = dataframe.copy()
    dataframe.columns = [
        str(columna).strip().lower().replace(" ", "_").replace("-", "_")
        for columna in dataframe.columns
    ]
    dataframe = dataframe.rename(columns=ALIAS_COLUMNAS)
    return dataframe


def leer_anio(anio: int) -> pd.DataFrame:
    """Lee y valida un CSV anual."""
    ruta = DATA_DIR / f"Procedencia_turistas_{anio}.csv"
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Verificá la carpeta data/."
        )

    dataframe = pd.read_csv(ruta, encoding="utf-8-sig")
    dataframe = normalizar_columnas(dataframe)

    faltantes = [columna for columna in COLUMNAS if columna not in dataframe.columns]
    if faltantes:
        raise ValueError(
            f"{ruta.name}: faltan columnas obligatorias: {', '.join(faltantes)}"
        )

    dataframe = dataframe[COLUMNAS].copy()
    dataframe["jurisdiccion_origen"] = (
        dataframe["jurisdiccion_origen"].astype(str).str.strip()
    )
    dataframe["provincias_agrupadas"] = (
        dataframe["provincias_agrupadas"].astype(str).str.strip()
    )
    dataframe["cantidad_turistas"] = pd.to_numeric(
        dataframe["cantidad_turistas"], errors="coerce"
    )

    if dataframe[COLUMNAS].isna().any().any():
        raise ValueError(f"{ruta.name}: contiene valores vacíos o no numéricos.")
    if (dataframe["cantidad_turistas"] < 0).any():
        raise ValueError(f"{ruta.name}: hay cantidades negativas.")
    if not set(dataframe["provincias_agrupadas"]).issubset(GRUPOS_VALIDOS):
        invalidos = set(dataframe["provincias_agrupadas"]) - GRUPOS_VALIDOS
        raise ValueError(
            f"{ruta.name}: grupos desconocidos: {', '.join(sorted(invalidos))}"
        )

    dataframe["cantidad_turistas"] = dataframe["cantidad_turistas"].round().astype(int)
    dataframe["anio"] = anio
    return dataframe[
        ["anio", "jurisdiccion_origen", "provincias_agrupadas", "cantidad_turistas"]
    ]


def cargar() -> pd.DataFrame:
    """Concatena los tres años, carga la base y devuelve el dataset unificado."""
    dataframes = [leer_anio(anio) for anio in ANIOS]
    dataset = pd.concat(dataframes, ignore_index=True)

    if dataset.empty:
        raise ValueError("El dataset unificado quedó vacío.")

    conexion = conectar(crear=True)
    try:
        asegurar_esquema(conexion)
        conexion.execute("DELETE FROM procedencia_muni")
        filas = [
            (
                int(fila.anio),
                str(fila.jurisdiccion_origen),
                str(fila.provincias_agrupadas),
                int(fila.cantidad_turistas),
            )
            for fila in dataset.itertuples(index=False)
        ]
        conexion.executemany(
            """
            INSERT INTO procedencia_muni
                (anio, jurisdiccion_origen, provincias_agrupadas, cantidad_turistas)
            VALUES (?, ?, ?, ?)
            """,
            filas,
        )
        conexion.commit()
    finally:
        conexion.close()

    return dataset


def main() -> int:
    print("=" * 72)
    print(" ETL · PROCEDENCIA TURÍSTICA · GENERAL PUEYRREDÓN")
    print("=" * 72)
    try:
        dataset = cargar()
    except Exception as error:  # noqa: BLE001 - se informa al usuario final
        print(f"\n[ERROR] {error}")
        return 1

    print(f"\nBase de datos: {DB_PATH}")
    print(f"Registros cargados: {len(dataset)}")
    print("\nTotales por año:")
    totales = dataset.groupby("anio")["cantidad_turistas"].sum()
    for anio, total in totales.items():
        print(f"  {anio}: {total:>10,.0f} visitantes (base de análisis)")

    print("\nParticipación por grupo de origen (%):")
    tabla = (
        dataset.groupby(["anio", "provincias_agrupadas"])["cantidad_turistas"]
        .sum()
        .unstack(fill_value=0)
    )
    porcentajes = tabla.div(tabla.sum(axis=1), axis=0) * 100
    print(porcentajes.round(1).to_string())

    print("\n[OK] Ingesta finalizada. Ahora ejecutá: python seed_fasta.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

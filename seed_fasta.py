"""
Generación de la muestra sintética del Observatorio FASTA 2025.

Inserta 100 microdatos calibrados con los parámetros publicados por la
Universidad FASTA y con las frecuencias del informe utilizado en el TP:

  * Edad promedio: 36,8 años.
  * Estadía promedio: 5,7 noches.
  * Anticipación promedio: 7,4 días.
  * Alojamiento: 75 % alquiler de depto./casa, 18 % hotelería, 7 % propio.
  * Transporte: 57 % auto particular, 30 % ómnibus, 13 % otros.
  * 17 % de turistas "repentinos" (reserva con menos de 7 días).
  * P(Alquiler | Repentino) = 15/17 = 88,24 %.

Los primeros 50 registros forman la submuestra de control utilizada por el
módulo descriptivo (N = 50). Sus noches de estadía se distribuyen en los cinco
intervalos del informe con frecuencias 6, 14, 18, 8 y 4, lo que reproduce por
datos agrupados: media 5,60; mediana 5,56; Q1 3,93; Q3 6,94 y s² 4,898.

Uso:
    python seed_fasta.py
"""

from __future__ import annotations

import sys

import numpy as np

from analytics import (
    CLASES_ESTADIA,
    asegurar_esquema,
    conectar,
)

SEED = 2025
N = 100
N_CONTROL = 50
CONTROL_COUNTS = [6, 14, 18, 8, 4]
EDAD_MEDIA = 36.8
ESTADIA_MEDIA = 5.70
ANTICIPACION_MEDIA = 7.4
REPENTINOS = 17


def calibrar_media(
    valores: np.ndarray, objetivo: float, minimo: float, maximo: float
) -> np.ndarray:
    """Desplaza y recorta un vector hasta que su media sea el objetivo."""
    resultado = np.asarray(valores, dtype=float).copy()
    for _ in range(500):
        diferencia = objetivo - float(resultado.mean())
        if abs(diferencia) < 1e-12:
            break
        resultado = np.clip(resultado + diferencia, minimo, maximo)
    return resultado


def generar_estadia(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Genera las 50 noches de control y las 50 restantes."""
    control_partes = []
    for (limite_inferior, limite_superior, marca, _), cantidad in zip(
        CLASES_ESTADIA, CONTROL_COUNTS
    ):
        valores = rng.normal(marca, 0.55, cantidad)
        valores = np.clip(valores, limite_inferior + 0.05, limite_superior - 0.05)
        control_partes.append(valores)
    control = np.concatenate(control_partes)

    # La media global debe quedar en 5,70 noches.
    objetivo_resto = (ESTADIA_MEDIA * N - control.sum()) / (N - N_CONTROL)
    resto = rng.normal(5.85, 2.10, N - N_CONTROL)
    resto = np.clip(resto, 1.0, 14.0)
    resto = calibrar_media(resto, objetivo_resto, 1.0, 14.0)

    return control, resto


def generar_anticipacion(
    rng: np.random.Generator, estadias: np.ndarray
) -> np.ndarray:
    """Genera X con 17 reservas repentinas y una media global de 7,4 días."""
    orden = np.argsort(estadias)
    indices_repentinos = orden[:REPENTINOS]
    indices_planificados = orden[REPENTINOS:]

    # Las reservas de último momento se asocian a estadías más cortas.
    tempranas = rng.normal(4.2, 1.30, REPENTINOS)
    tempranas = np.clip(tempranas, 1.0, 6.90)
    tempranas = calibrar_media(tempranas, 4.0, 1.0, 6.90)

    media_planificadas = (
        ANTICIPACION_MEDIA * N - 4.0 * REPENTINOS
    ) / (N - REPENTINOS)
    planificadas = rng.normal(8.15, 1.95, N - REPENTINOS)
    planificadas = np.clip(planificadas, 7.05, 16.0)
    planificadas = calibrar_media(
        planificadas, media_planificadas, 7.05, 16.0
    )

    anticipacion = np.empty(N, dtype=float)
    anticipacion[indices_repentinos] = np.sort(tempranas)
    anticipacion[indices_planificados] = np.sort(planificadas)
    return anticipacion


def generar_edad(rng: np.random.Generator) -> np.ndarray:
    """Edad con media 36,8, recortada al rango etario del relevamiento."""
    edades = rng.normal(EDAD_MEDIA, 12.0, N)
    edades = np.clip(edades, 18.0, 78.0)
    return calibrar_media(edades, EDAD_MEDIA, 18.0, 78.0)


def main() -> int:
    print("=" * 72)
    print(" SEED · MICRODATOS CALIBRADOS · OBSERVATORIO FASTA 2025")
    print("=" * 72)

    rng = np.random.default_rng(SEED)
    control, resto = generar_estadia(rng)
    estadias = np.concatenate([control, resto])
    anticipacion = generar_anticipacion(rng, estadias)
    edades = generar_edad(rng)

    # ------------------------------------------------------------------
    # Categorías: 75 alquiler / 18 hotelería / 7 propio
    # Contingencia: 15(A∩B), 2(A∩B'), 60(A'∩B), 23(A'∩B')
    # ------------------------------------------------------------------
    orden = np.argsort(estadias)
    indices_repentinos = orden[:REPENTINOS]
    indices_planificados = orden[REPENTINOS:]

    alojamiento = np.empty(N, dtype=object)
    alojamiento[indices_repentinos[:15]] = "Alquiler Depto/Casa"
    alojamiento[indices_repentinos[15]] = "Hotelería"
    alojamiento[indices_repentinos[16]] = "Propio"

    planificados_mezclados = rng.permutation(indices_planificados)
    alojamiento[planificados_mezclados[:60]] = "Alquiler Depto/Casa"
    alojamiento[planificados_mezclados[60:77]] = "Hotelería"
    alojamiento[planificados_mezclados[77:]] = "Propio"

    transporte = np.array(
        ["Auto particular"] * 57 + ["Ómnibus"] * 30 + ["Otros"] * 13,
        dtype=object,
    )
    rng.shuffle(transporte)

    satisfaccion = np.array(
        ["Muy satisfecho"] * 42
        + ["Satisfecho"] * 38
        + ["Neutral"] * 14
        + ["Insatisfecho"] * 6,
        dtype=object,
    )
    rng.shuffle(satisfaccion)

    # Redondeo final y control de consistencia.
    edades = np.round(edades, 1)
    estadias = np.round(estadias, 2)
    anticipacion = np.round(anticipacion, 2)

    filas = [
        (
            float(edades[i]),
            float(estadias[i]),
            float(anticipacion[i]),
            str(alojamiento[i]),
            str(transporte[i]),
            str(satisfaccion[i]),
        )
        for i in range(N)
    ]

    # Validaciones que garantizan la reproducibilidad del informe.
    assert len(filas) == N
    assert (anticipacion < 7).sum() == REPENTINOS
    assert (alojamiento == "Alquiler Depto/Casa").sum() == 75
    assert (alojamiento == "Hotelería").sum() == 18
    assert (alojamiento == "Propio").sum() == 7
    assert (transporte == "Auto particular").sum() == 57
    assert (transporte == "Ómnibus").sum() == 30
    assert (transporte == "Otros").sum() == 13

    conexion = conectar(crear=True)
    try:
        asegurar_esquema(conexion)
        conexion.execute("DELETE FROM encuestas_fasta")
        conexion.executemany(
            """
            INSERT INTO encuestas_fasta
                (edad, noches_estadia, dias_anticipacion,
                 tipo_alojamiento, transporte_utilizado, satisfaccion)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            filas,
        )
        conexion.commit()
    finally:
        conexion.close()

    print(f"\nRegistros insertados: {N}")
    print(f"Edad promedio:          {np.mean(edades):.2f} años")
    print(f"Estadía promedio:       {np.mean(estadias):.2f} noches")
    print(f"Anticipación promedio:  {np.mean(anticipacion):.2f} días")
    print(f"Reservas < 7 días:      {(anticipacion < 7).sum()} ({(anticipacion < 7).mean() * 100:.1f} %)")
    print("\nAlojamiento:")
    for etiqueta in ("Alquiler Depto/Casa", "Hotelería", "Propio"):
        cantidad = int((alojamiento == etiqueta).sum())
        print(f"  {etiqueta:<22} {cantidad:>3} ({cantidad:>5.1f} %)")
    print("\nTransporte:")
    for etiqueta in ("Auto particular", "Ómnibus", "Otros"):
        cantidad = int((transporte == etiqueta).sum())
        print(f"  {etiqueta:<22} {cantidad:>3} ({cantidad:>5.1f} %)")

    control_conteos = []
    for limite_inferior, limite_superior, _, _ in CLASES_ESTADIA:
        if limite_superior == 11.0:
            cantidad = int(((control >= limite_inferior) & (control <= limite_superior)).sum())
        else:
            cantidad = int(((control >= limite_inferior) & (control < limite_superior)).sum())
        control_conteos.append(cantidad)
    print(f"\nSubmuestra de control (N = {N_CONTROL}) · frecuencias: {control_conteos}")
    print("\n[OK] Seed finalizado. Ahora ejecutá: python 2_descriptiva.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Módulo de estadística bivariada y regresión lineal simple.

Calcula la covarianza, el coeficiente de correlación de Pearson, el
coeficiente de determinación y la recta de mínimos cuadrados a partir de la
tabla bivariada consolidada del informe FASTA (N = 15). Genera el diagrama de
dispersión con las observaciones agrupadas y la recta ajustada.

Uso:
    python 3_regresion.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from analytics import get_regresion

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "static" / "img"
NAVY = "#0b2a4a"
TEAL = "#1b8a8f"
SAND = "#f2c14e"
CORAL = "#e76f51"
GRAY = "#64748b"


def configurar_estilo() -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titleweight": "bold",
            "axes.titlesize": 16,
            "axes.labelsize": 11,
            "axes.labelcolor": NAVY,
            "xtick.color": GRAY,
            "ytick.color": GRAY,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "grid.color": "#e2e8f0",
            "grid.linewidth": 0.8,
        }
    )


def generar_dispersion(reg: dict, ruta: Path) -> None:
    """Dispersión de la tabla bivariada N = 15 con la recta ajustada."""
    figura, eje = plt.subplots(figsize=(10, 6.6))
    generador = np.random.default_rng(11)
    primera_celda = True

    # Cada celda de la tabla se dibuja como un conjunto de observaciones
    # levemente desplazadas y un círculo cuyo tamaño representa su frecuencia.
    for i, x in enumerate(reg["x_marcas"]):
        for j, y in enumerate(reg["y_marcas"]):
            frecuencia = reg["frecuencias"][i][j]
            if not frecuencia:
                continue

            desplazamiento_x = generador.normal(0, 0.13, frecuencia)
            desplazamiento_y = generador.normal(0, 0.13, frecuencia)
            eje.scatter(
                x + desplazamiento_x,
                y + desplazamiento_y,
                s=36,
                color=NAVY,
                alpha=0.62,
                edgecolors="white",
                linewidths=0.5,
                zorder=3,
                label="Observaciones agrupadas (N = 15)" if primera_celda else None,
            )
            eje.scatter(
                x,
                y,
                s=90 + 150 * frecuencia,
                facecolors="none",
                edgecolors=TEAL,
                linewidths=2.0,
                alpha=0.95,
                zorder=4,
                label="Tamaño del círculo = frecuencia conjunta" if primera_celda else None,
            )
            eje.text(
                x + 0.28,
                y + 0.28,
                f"f = {frecuencia}",
                fontsize=9,
                color=TEAL,
                fontweight="bold",
                zorder=5,
            )
            primera_celda = False

    eje.scatter(
        [reg["media_x"]],
        [reg["media_y"]],
        marker="P",
        s=160,
        color=CORAL,
        edgecolors="white",
        linewidths=1.2,
        zorder=6,
        label=f"Punto medio ({reg['media_x']:.2f}; {reg['media_y']:.2f})",
    )

    x_linea = np.linspace(0, 17, 200)
    y_linea = reg["ordenada"] + reg["pendiente"] * x_linea
    eje.plot(
        x_linea,
        y_linea,
        color=CORAL,
        linewidth=2.8,
        label="Recta de mínimos cuadrados",
        zorder=5,
    )

    eje.set_xlim(0, 17)
    eje.set_ylim(0, 15)
    eje.set_xlabel("Días de anticipación de la reserva (X)")
    eje.set_ylabel("Noches de estadía (Y)")
    eje.set_title(
        "Relación entre anticipación y estadía",
        loc="left",
        color=NAVY,
        pad=16,
    )

    texto = (
        f"$\\hat{{Y}} = {reg['ordenada']:.4f} + {reg['pendiente']:.4f}\\,X$\n"
        f"$r = {reg['correlacion']:.4f}$   ·   $r^2 = {reg['determinacion']:.4f}$\n"
        f"$S_{{xy}} = {reg['covarianza']:.2f}$   ·   $N = {reg['n']}$"
    )
    eje.text(
        0.035,
        0.965,
        texto,
        transform=eje.transAxes,
        va="top",
        ha="left",
        fontsize=11,
        color=NAVY,
        bbox=dict(
            boxstyle="round,pad=0.65",
            facecolor="#f8fafc",
            edgecolor="#cbd5e1",
            linewidth=0.9,
            alpha=0.96,
        ),
        zorder=7,
    )

    eje.grid(alpha=0.65)
    eje.legend(loc="lower right", frameon=False, fontsize=9)
    figura.text(
        0.01,
        0.015,
        "Fuente: Observatorio Universitario de la Ciudad (UFASTA, 2025). Tabla bivariada "
        "consolidada (N = 15). Los puntos se desplazan levemente para distinguir observaciones repetidas.",
        fontsize=7.8,
        color=GRAY,
    )
    figura.tight_layout(rect=(0, 0.04, 1, 1))
    figura.savefig(ruta, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(figura)


def main() -> int:
    configurar_estilo()
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    try:
        reg = get_regresion()
    except Exception as error:  # noqa: BLE001
        print(f"[ERROR] {error}")
        print("Ejecutá primero: python cargar_csv.py y python seed_fasta.py")
        return 1

    ruta = IMG_DIR / "regresion_lineal.png"
    generar_dispersion(reg, ruta)

    print("=" * 72)
    print(" ESTADÍSTICA BIVARIADA · REGRESIÓN LINEAL (N = 15)")
    print("=" * 72)

    matriz = pd.DataFrame(
        reg["frecuencias"],
        index=[f"X = {x:g}" for x in reg["x_marcas"]],
        columns=[f"Y = {y:g}" for y in reg["y_marcas"]],
    )
    matriz["Total X"] = reg["total_x"]
    fila_total = dict(zip(matriz.columns[:-1], reg["total_y"]))
    fila_total["Total X"] = reg["n"]
    matriz.loc["Total Y"] = fila_total
    print("\nTabla bivariada de frecuencias:")
    print(matriz.to_string())

    print(f"\nN = {reg['n']}")
    print(f"Media X:            {reg['media_x']:.4f} días")
    print(f"Media Y:            {reg['media_y']:.4f} noches")
    print(f"Varianza X:         {reg['varianza_x']:.4f}")
    print(f"Varianza Y:         {reg['varianza_y']:.4f}")
    print(f"Desvío X:           {reg['desvio_x']:.4f}")
    print(f"Desvío Y:           {reg['desvio_y']:.4f}")
    print(f"Covarianza Sxy:     {reg['covarianza']:.4f}")
    print(f"Correlación r:      {reg['correlacion']:.4f}")
    print(f"Determinación r²:   {reg['determinacion']:.4f}")
    print(f"Pendiente b:        {reg['pendiente']:.4f}")
    print(f"Ordenada a:         {reg['ordenada']:.4f}")
    print(f"Ecuación:           Y = {reg['ordenada']:.4f} + {reg['pendiente']:.4f} · X")
    print(f"\nPredicción para X = 14: Y = {reg['ordenada'] + reg['pendiente'] * 14:.4f} noches")

    print(f"\n[OK] Gráfico guardado en: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

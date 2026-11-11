"""
Módulo de estadística descriptiva univariada.

Calcula la tabla de frecuencias agrupadas y las medidas de resumen de la
submuestra de control (N = 50), genera el box-plot de la estadía y el gráfico
comparativo de procedencia por año.

Uso:
    python 2_descriptiva.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Backend sin ventana, apto para servidores.
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from analytics import get_descriptiva, get_resumen_procedencia

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "static" / "img"
NAVY = "#0b2a4a"
TEAL = "#1b8a8f"
SAND = "#f2c14e"
CORAL = "#e76f51"
GRAY = "#64748b"
PALETTE_ANIOS = [NAVY, TEAL, SAND]


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


def generar_boxplot(desc: dict, ruta: Path) -> None:
    """Box-plot construido con los cuartiles agrupados del informe."""
    valores = np.asarray(desc["valores"], dtype=float)
    stats = [
        {
            "label": "Noches de estadía",
            "med": desc["mediana"],
            "q1": desc["q1"],
            "q3": desc["q3"],
            "whislo": float(valores.min()),
            "whishi": float(valores.max()),
            "fliers": [],
            "mean": desc["media"],
        }
    ]

    figura, eje = plt.subplots(figsize=(9.2, 6.2))
    caja = eje.bxp(
        stats,
        showmeans=True,
        patch_artist=True,
        widths=0.42,
        showcaps=True,
        meanprops={
            "marker": "D",
            "markerfacecolor": SAND,
            "markeredgecolor": NAVY,
            "markersize": 8,
        },
        medianprops={"color": NAVY, "linewidth": 2.4},
        boxprops={"facecolor": "#bfe3e4", "edgecolor": TEAL, "linewidth": 1.8},
        whiskerprops={"color": TEAL, "linewidth": 1.8},
        capprops={"color": TEAL, "linewidth": 1.8},
    )

    # Nube de puntos: conserva la variabilidad de la submuestra de control.
    generador = np.random.default_rng(7)
    jitter = generador.normal(0, 0.035, len(valores))
    eje.scatter(
        np.full(len(valores), 1.0) + jitter,
        valores,
        s=26,
        color=NAVY,
        alpha=0.35,
        edgecolors="white",
        linewidths=0.4,
        zorder=3,
        label=f"Observaciones (N = {desc['n']})",
    )

    etiquetas = [
        ("Q1", desc["q1"], "#e8f4f4"),
        ("Me", desc["mediana"], "#fff4d6"),
        ("Q3", desc["q3"], "#e8f4f4"),
    ]
    for posicion, (nombre, valor, color) in enumerate(etiquetas):
        eje.annotate(
            f"{nombre} = {valor:.2f}",
            xy=(1.18, valor),
            xytext=(1.32, valor + (0.45 if posicion == 0 else -0.35 if posicion == 2 else 0)),
            fontsize=9.5,
            color=NAVY,
            bbox=dict(boxstyle="round,pad=0.35", fc=color, ec="#cbd5e1", lw=0.8),
            arrowprops=dict(arrowstyle="-", color="#94a3b8", lw=0.9),
        )

    eje.axhline(
        desc["media"],
        color=SAND,
        linestyle="--",
        linewidth=1.1,
        alpha=0.9,
        zorder=2,
    )
    eje.text(
        0.614,
        desc["media"] + 0.22,
        f"Media = {desc['media']:.2f}",
        fontsize=9,
        color="#8a6d1d",
    )

    eje.set_title(
        "Distribución de la estadía en General Pueyrredón",
        loc="left",
        color=NAVY,
        pad=16,
    )
    eje.set_ylabel("Noches de estadía")
    eje.set_ylim(0, 12.6)
    eje.set_xlim(0.55, 1.78)
    eje.set_xticks([1.0])
    eje.set_xticklabels(["Submuestra de control\n(N = 50)"], color=NAVY)
    eje.grid(axis="y", alpha=0.7)
    eje.grid(axis="x", visible=False)
    eje.legend(loc="upper right", frameon=False, fontsize=9)

    figura.text(
        0.01,
        0.015,
        "Fuente: Observatorio Universitario de la Ciudad (UFASTA, 2025). "
        "Cuartiles calculados por datos agrupados en 5 intervalos.",
        fontsize=7.8,
        color=GRAY,
    )
    figura.tight_layout(rect=(0, 0.04, 1, 1))
    figura.savefig(ruta, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(figura)


def generar_procedencia(resumen: dict, ruta: Path) -> None:
    """Barras agrupadas con la participación porcentual por origen y año."""
    years = resumen["years"]
    groups = resumen["main_groups"]
    shares = resumen["shares"]

    if not years or not groups:
        raise ValueError("No hay datos de procedencia para graficar.")

    x = np.arange(len(groups))
    ancho_total = 0.78
    ancho = ancho_total / len(years)

    figura, eje = plt.subplots(figsize=(10.4, 6.2))
    for indice, anio in enumerate(years):
        valores = [shares[grupo][anio] for grupo in groups]
        posiciones = x - ancho_total / 2 + ancho / 2 + indice * ancho
        barras = eje.bar(
            posiciones,
            valores,
            width=ancho * 0.92,
            label=str(anio),
            color=PALETTE_ANIOS[indice % len(PALETTE_ANIOS)],
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        for barra, valor in zip(barras, valores):
            eje.text(
                barra.get_x() + barra.get_width() / 2,
                barra.get_height() + 0.6,
                f"{valor:.1f}%",
                ha="center",
                va="bottom",
                fontsize=8.2,
                color=NAVY,
            )

    eje.set_title(
        "Procedencia de los visitantes · 2022-2024",
        loc="left",
        color=NAVY,
        pad=16,
    )
    eje.set_ylabel("Participación sobre el total anual (%)")
    eje.set_xlabel("Grupo de origen")
    eje.set_xticks(x)
    eje.set_xticklabels(groups, color=NAVY, fontweight="semibold")
    eje.set_ylim(0, 47)
    eje.grid(axis="y", alpha=0.7)
    eje.grid(axis="x", visible=False)
    eje.legend(
        title="Año",
        loc="upper right",
        frameon=False,
        ncol=len(years),
        fontsize=10,
        title_fontsize=9,
    )
    eje.text(
        0.995,
        0.965,
        f"Último año: {years[-1]}",
        transform=eje.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        color=GRAY,
    )

    figura.text(
        0.01,
        0.015,
        "Fuente: Datos Abiertos del Municipio de General Pueyrredón. "
        "Base de análisis: 100.000 visitantes por año. Exterior no incluido en el gráfico.",
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
        desc = get_descriptiva()
        resumen = get_resumen_procedencia()
    except Exception as error:  # noqa: BLE001
        print(f"[ERROR] {error}")
        print("Ejecutá primero: python cargar_csv.py y python seed_fasta.py")
        return 1

    ruta_boxplot = IMG_DIR / "boxplot_estadia.png"
    ruta_procedencia = IMG_DIR / "procedencia_comparativa.png"

    generar_boxplot(desc, ruta_boxplot)
    generar_procedencia(resumen, ruta_procedencia)

    print("=" * 72)
    print(" ESTADÍSTICA DESCRIPTIVA · ESTADÍA (N = 50)")
    print("=" * 72)
    tabla = pd.DataFrame(desc["tabla"])[
        ["intervalo", "marca", "f", "h_pct", "F", "fx", "fx2"]
    ]
    tabla.columns = [
        "Intervalo",
        "Marca (x)",
        "f",
        "h (%)",
        "F",
        "f·x",
        "f·x²",
    ]
    print(tabla.to_string(index=False))
    print(f"\nN = {desc['n']}   Σf·x = {desc['suma_fx']:.1f}   Σf·x² = {desc['suma_fx2']:.1f}")
    print(f"Media:                 {desc['media']:.4f}")
    print(f"Mediana:               {desc['mediana']:.4f}")
    print(f"Moda:                  {desc['moda']:.1f}")
    print(f"Varianza muestral:     {desc['varianza']:.4f}")
    print(f"Desvío estándar:       {desc['desvio']:.4f}")
    print(f"Coeficiente de variación: {desc['cv']:.2f} %")
    print(f"Q1: {desc['q1']:.4f}   Q2: {desc['q2']:.4f}   Q3: {desc['q3']:.4f}")
    print(f"IQR: {desc['iqr']:.4f}   Límites: [{desc['limite_inferior']:.4f}; {desc['limite_superior']:.4f}]")
    print(f"\n[OK] Gráfico guardado en: {ruta_boxplot}")
    print(f"[OK] Gráfico guardado en: {ruta_procedencia}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Aplicación Flask del Observatorio Turístico de General Pueyrredón.

Rutas:
    /              Portada con KPIs y marco socio-técnico.
    /procedencia   Evolución del origen de los visitantes (2022-2024).
    /descriptiva   Estadística univariada, box-plot y probabilidades.
    /regresion     Correlación, regresión y simulador predictivo.
    /predict       API POST que devuelve la estadía estimada.

Uso:
    python app.py
"""

from __future__ import annotations

import math
import sqlite3

from flask import Flask, jsonify, render_template, request

import analytics

app = Flask(__name__)
app.json.ensure_ascii = False
app.config["TEMPLATES_AUTO_RELOAD"] = True

META = {
    "institucion": "Instituto Superior de Formación Técnica N°151",
    "institucion_corta": "ISFT N°151",
    "ciudad": "General Pueyrredón · Mar del Plata",
    "carrera": "Tecnicatura Superior en Análisis de Sistemas",
    "materia": "Estadística · 2° Año",
    "ciclo": "Ciclo Lectivo 2026",
    "profesora": "Mascarenhas, María Carolina",
    "ayudante": "González Ferreira, Gabriel Nicolás",
    "estudiante": "Saavedra Piñeiro, Jazmín del Rosario",
    "titulo": (
        "Desarrollo Turístico Inteligente y Sostenible en el Municipio de "
        "General Pueyrredón"
    ),
    "subtitulo": (
        "Análisis estadístico multianual y modelo predictivo (2022-2025)"
    ),
    "anio": 2026,
}


# ---------------------------------------------------------------------------
# Formato argentino (miles con punto, decimales con coma)
# ---------------------------------------------------------------------------
def _formatear(valor: object, decimales: int = 2) -> str:
    if valor is None:
        return "—"
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    if not math.isfinite(numero):
        return "—"
    texto = f"{numero:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


@app.template_filter("n")
def filtro_numero(valor: object, decimales: int = 2) -> str:
    return _formatear(valor, decimales)


@app.template_filter("entero")
def filtro_entero(valor: object) -> str:
    return _formatear(valor, 0)


@app.template_filter("pct")
def filtro_pct(valor: object, decimales: int = 1) -> str:
    return f"{_formatear(valor, decimales)} %"


@app.template_filter("pp")
def filtro_pp(valor: object, decimales: int = 1) -> str:
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return "—"
    signo = "+" if numero >= 0 else "−"
    return f"{signo}{_formatear(abs(numero), decimales)} pp"


@app.context_processor
def inyectar_metadatos() -> dict:
    return {"meta": META}


@app.after_request
def cabeceras_seguridad(respuesta):
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    respuesta.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return respuesta


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    kpis = analytics.get_kpis()
    procedencia = analytics.get_resumen_procedencia()
    distribuciones = analytics.get_distribuciones()
    return render_template(
        "index.html",
        kpis=kpis,
        procedencia=procedencia,
        distribuciones=distribuciones,
    )


@app.route("/procedencia")
def procedencia():
    resumen = analytics.get_resumen_procedencia()
    return render_template("procedencia.html", resumen=resumen)


@app.route("/descriptiva")
def descriptiva():
    desc = analytics.get_descriptiva()
    probabilidades = analytics.get_probabilidades()
    distribuciones = analytics.get_distribuciones()
    return render_template(
        "descriptiva.html",
        desc=desc,
        prob=probabilidades,
        distribuciones=distribuciones,
    )


@app.route("/regresion")
def regresion():
    reg = analytics.get_regresion()
    return render_template("regresion.html", reg=reg)


@app.route("/predict", methods=["POST"])
def predict():
    """API interna: recibe días de anticipación y devuelve la estadía estimada."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return (
            jsonify(
                {
                    "error": "Se esperaba un cuerpo JSON con la clave 'dias_anticipacion'."
                }
            ),
            400,
        )

    valor = payload.get("dias_anticipacion", payload.get("dias"))
    try:
        dias = float(valor)
    except (TypeError, ValueError):
        return (
            jsonify({"error": "El valor de 'dias_anticipacion' debe ser numérico."}),
            400,
        )

    if not math.isfinite(dias):
        return jsonify({"error": "El valor debe ser un número finito."}), 400
    if dias < 0:
        return jsonify({"error": "Los días de anticipación no pueden ser negativos."}), 400
    if dias > 365:
        return jsonify({"error": "El valor máximo admitido es 365 días."}), 400

    estimacion = analytics.predecir(dias)
    return jsonify(
        {
            "dias_anticipacion": round(dias, 2),
            "estadia_estimada": round(estimacion, 4),
            "estadia_redondeada": round(estimacion, 1),
            "modelo": analytics.MODELO_ECUACION,
        }
    )


# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def no_encontrado(error):
    return (
        render_template(
            "error.html",
            codigo=404,
            titulo="Página no encontrada",
            detalle="La ruta solicitada no existe en el observatorio.",
        ),
        404,
    )


@app.errorhandler(FileNotFoundError)
def base_inexistente(error):
    return (
        render_template(
            "error.html",
            codigo="Base de datos",
            titulo="Todavía no está la base de datos",
            detalle=str(error),
        ),
        503,
    )


@app.errorhandler(sqlite3.Error)
def error_sqlite(error):
    return (
        render_template(
            "error.html",
            codigo="SQLite",
            titulo="No se pudo consultar la base",
            detalle=f"{error}. Verificá que los scripts de ingesta se hayan ejecutado.",
        ),
        500,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

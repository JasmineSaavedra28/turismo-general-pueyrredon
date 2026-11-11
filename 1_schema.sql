-- ============================================================================
--  Base de datos: turismo_mdp.db
--  Proyecto: Desarrollo Turístico Inteligente y Sostenible en General Pueyrredón
--  Materia: Estadística · ISFT N°151 · 2026
-- ============================================================================
--  Este archivo crea las dos tablas que alimentan el dashboard:
--    1) procedencia_muni  -> datos abiertos municipales (2022-2024)
--    2) encuestas_fasta   -> microdatos calibrados del Observatorio FASTA 2025
-- ============================================================================

PRAGMA encoding = 'UTF-8';

-- ----------------------------------------------------------------------------
--  Procedencia geográfica de los visitantes
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS procedencia_muni (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    anio                  INTEGER NOT NULL CHECK (anio IN (2022, 2023, 2024)),
    jurisdiccion_origen   TEXT    NOT NULL,
    provincias_agrupadas  TEXT    NOT NULL,
    cantidad_turistas     INTEGER NOT NULL CHECK (cantidad_turistas >= 0)
);

CREATE INDEX IF NOT EXISTS idx_procedencia_anio
    ON procedencia_muni (anio);

CREATE INDEX IF NOT EXISTS idx_procedencia_grupo
    ON procedencia_muni (provincias_agrupadas);

-- ----------------------------------------------------------------------------
--  Encuestas del Observatorio Universitario de la Ciudad (UFASTA)
--  X = días de anticipación de la reserva
--  Y = noches de estadía
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS encuestas_fasta (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    edad                  REAL    NOT NULL CHECK (edad >= 0),
    noches_estadia        REAL    NOT NULL CHECK (noches_estadia > 0),
    dias_anticipacion     REAL    NOT NULL CHECK (dias_anticipacion >= 0),
    tipo_alojamiento      TEXT    NOT NULL,
    transporte_utilizado  TEXT    NOT NULL,
    satisfaccion          TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_encuestas_anticipacion
    ON encuestas_fasta (dias_anticipacion);

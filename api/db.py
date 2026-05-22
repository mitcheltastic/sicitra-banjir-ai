"""
Database utility for saving prediction results to PostgreSQL (Prisma-managed).
Uses psycopg2 connection pooling for efficient, thread-safe connections.
"""

import os
import json
import logging
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool, extras

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# STEP 2: Connection Pool Setup
# ---------------------------------------------------------------------------

_connection_pool = None


def init_db():
    """
    Initialize the database connection pool.
    Call this once at app startup. Fails silently so the AI service
    keeps running even if the database is unreachable.
    """
    global _connection_pool
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        logger.warning("DATABASE_URL is not set – prediction saving is disabled.")
        return

    try:
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            dsn=database_url,
        )
        logger.info("✅ Database connection pool initialized successfully.")
    except psycopg2.Error as e:
        logger.error(f"❌ Failed to initialize database pool: {e}")
        _connection_pool = None


def close_db():
    """Cleanly close all connections in the pool."""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("Database connection pool closed.")


@contextmanager
def get_connection():
    """
    Context manager that borrows a connection from the pool,
    commits on success, rolls back on error, and always returns
    the connection to the pool.
    """
    if _connection_pool is None:
        raise RuntimeError("Database pool is not initialized.")

    conn = _connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _connection_pool.putconn(conn)


# ---------------------------------------------------------------------------
# STEP 3: Insertion Logic
# ---------------------------------------------------------------------------

INSERT_SQL = """
    INSERT INTO "PredictionResult" (
        "inputReceived",
        "classProbability",
        "description",
        "floodClass",
        "floodLevel",
        "riskLevel",
        "tmaValue",
        "createdAt",
        "updatedAt"
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    )
"""


def save_prediction(input_received: dict, prediction: dict) -> bool:
    """
    Persist a successful prediction to the PredictionResult table.

    Parameters
    ----------
    input_received : dict
        The raw input payload (will be stored as JSONB).
    prediction : dict
        The prediction result dict containing:
            - class_probability (dict)
            - description (str)
            - flood_class (int)
            - flood_level (str)
            - risk_level (str)
            - tma_value (float)

    Returns
    -------
    bool
        True if saved successfully, False otherwise.
    """
    if _connection_pool is None:
        logger.warning("DB pool not available – skipping prediction save.")
        return False

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(INSERT_SQL, (
                    extras.Json(input_received),
                    extras.Json(prediction["class_probability"]),
                    prediction["description"],
                    prediction["flood_class"],
                    prediction["flood_level"],
                    prediction["risk_level"],
                    prediction["tma_value"],
                ))
        logger.info("✅ Prediction saved to database.")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save prediction: {e}")
        return False

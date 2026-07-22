"""
Database connection pool and query management using raw psycopg2.
"""
from contextlib import contextmanager
from pathlib import Path
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Initialize Threaded Connection Pool for thread safety with FastAPI
try:
    db_pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=20,
        dsn=settings.database_url
    )
    logger.info("Database connection pool initialized successfully.")
except Exception as e:
    logger.critical("Failed to initialize database connection pool: %s", str(e))
    raise e


def get_db():
    """
    FastAPI dependency yielding a connection from the pool.
    Commits on success, rolls back on exception.
    """
    conn = db_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.exception("Database transaction failed, rolling back.")
        raise exc
    finally:
        db_pool.putconn(conn)


@contextmanager
def get_db_conn():
    """
    Context manager for non-FastAPI endpoints (e.g., startup scripts/tasks).
    """
    conn = db_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise exc
    finally:
        db_pool.putconn(conn)


def check_database_connection() -> bool:
    """
    Ping the database to verify active connection.
    """
    try:
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            return True
        finally:
            db_pool.putconn(conn)
    except Exception:
        return False


def init_db() -> None:
    """
    Initializes database tables by executing schema.sql.
    """
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    if not schema_path.exists():
        logger.error("Database schema.sql not found at: %s", schema_path)
        return

    logger.info("Executing database schema initialization...")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    try:
        with get_db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical("Failed to initialize database tables: %s", str(e))
        raise e


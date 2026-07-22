"""
Unit tests for database connection and raw SQL queries.
"""
import uuid
import pytest
import psycopg2.extras
from app.core.config import Settings
from app.core.database import get_db_conn, check_database_connection


def test_settings_database_url_priority():
    """Verify DATABASE_URL takes priority and converts postgres:// to postgresql://."""
    s = Settings(DATABASE_URL="postgres://user:pass@ep-xyz.neon.tech/neondb?sslmode=require")
    assert s.database_url.startswith("postgresql://")
    assert "neon.tech" in s.database_url


def test_database_connectivity():
    """Verify check_database_connection works correctly."""
    assert check_database_connection() is True


def test_raw_sql_crud():
    """Verify raw SQL CRUD operations against the database."""
    resume_id = str(uuid.uuid4())
    jd_id = str(uuid.uuid4())
    match_id = str(uuid.uuid4())

    with get_db_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # 1. Insert Resume
            cur.execute(
                """
                INSERT INTO resumes (id, filename, file_path, file_type, file_size, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, filename, status
                """,
                (resume_id, "test_file.pdf", "/test/path", "application/pdf", 2048, "uploaded")
            )
            resume_row = cur.fetchone()
            assert resume_row is not None
            assert resume_row["filename"] == "test_file.pdf"
            assert resume_row["status"] == "uploaded"

            # 2. Insert JD
            cur.execute(
                """
                INSERT INTO job_descriptions (id, title, company, raw_text)
                VALUES (%s, %s, %s, %s)
                RETURNING id, title
                """,
                (jd_id, "Python Developer", "Aml Corp", "FastAPI experience required.")
            )
            jd_row = cur.fetchone()
            assert jd_row is not None
            assert jd_row["title"] == "Python Developer"

            # 3. Insert Match
            cur.execute(
                """
                INSERT INTO match_results (id, resume_id, job_description_id, overall_score)
                VALUES (%s, %s, %s, %s)
                RETURNING id, overall_score
                """,
                (match_id, resume_id, jd_id, 92.5)
            )
            match_row = cur.fetchone()
            assert match_row is not None
            assert match_row["overall_score"] == 92.5

            # 4. Query & Verify
            cur.execute("SELECT filename FROM resumes WHERE id = %s", (resume_id,))
            assert cur.fetchone()["filename"] == "test_file.pdf"

            # 5. Clean up
            cur.execute("DELETE FROM match_results WHERE id = %s", (match_id,))
            cur.execute("DELETE FROM job_descriptions WHERE id = %s", (jd_id,))
            cur.execute("DELETE FROM resumes WHERE id = %s", (resume_id,))

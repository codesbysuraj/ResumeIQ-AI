"""Job Description ingestion endpoints using raw SQL."""
import json
from uuid import uuid4
from fastapi import APIRouter, Depends, status
import psycopg2.extras

from app.core.database import get_db
from app.schemas.job_description import JobDescriptionCreate, JobDescriptionResponse
from app.services.nlp.embeddings import EmbeddingService

router = APIRouter()


@router.post(
    "/",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job description",
)
def create_job_description(
    payload: JobDescriptionCreate,
    db = Depends(get_db),
) -> JobDescriptionResponse:
    """Store a job description and generate its text embeddings."""
    emb = EmbeddingService.generate_embedding(payload.raw_text)
    jd_id = str(uuid4())
    
    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(
            """
            INSERT INTO job_descriptions (id, title, company, raw_text, embeddings)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, title, company, raw_text, required_skills, preferred_skills, parsed_requirements, created_at, updated_at
            """,
            (
                jd_id,
                payload.title,
                payload.company,
                payload.raw_text,
                json.dumps({"vector": emb}),
            ),
        )
        row = cur.fetchone()
        
    return JobDescriptionResponse.model_validate(dict(row))

import asyncio
import json
import psycopg2.extras
from app.core.database import get_db_conn
from app.services.nlp.parser import ResumeParser, SKILL_ALIASES
from app.services.matching.matcher import ATSMatcher

def run_debug():
    # 1. Fetch latest Resume and JD from DB
    with get_db_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, raw_text, parsed_data FROM resumes ORDER BY updated_at DESC LIMIT 1")
            resume = cur.fetchone()
            
            cur.execute("SELECT id, raw_text FROM job_descriptions ORDER BY created_at DESC LIMIT 1")
            jd = cur.fetchone()

    if not resume or not jd:
        print("No resume or JD found in DB.")
        return

    print("----------------------")
    print("RESUME ID:", resume["id"])
    print("JD ID:", jd["id"])
    print("----------------------")

    # The issue: what happens in ATSMatcher?
    resume_text = resume["raw_text"] or ""
    jd_text = jd["raw_text"] or ""
    
    # Simulate what matching.py does
    parsed_profile = resume["parsed_data"] or {}
    
    # The user says parser works correctly. Let's see what parse_resume_text outputs now:
    new_parsed_profile = ResumeParser.parse_resume_text(resume_text)
    
    # We'll use new_parsed_profile to be sure we are using the latest parser logic
    resume_skills = new_parsed_profile.get("skills", [])
    
    # Now simulate calculate_skills_score
    jd_skills = ResumeParser.extract_skills(jd_text, custom_taxonomy=SKILL_ALIASES)
    
    print("RAW RESUME SKILLS (From new parse):", resume_skills)
    print("RAW JD SKILLS (From extract_skills):", jd_skills)
    
    # In extract_skills, it loops over SKILL_ALIASES.
    # What exactly did it find?
    
    resume_set = set(resume_skills)
    jd_set = set(jd_skills)
    
    print("NORMALIZED RESUME SKILLS (set):", list(resume_set))
    print("NORMALIZED JD SKILLS (set):", list(jd_set))
    
    matched = sorted(list(resume_set.intersection(jd_set)))
    missing = sorted(list(jd_set - resume_set))
    
    print("MATCHED SKILLS:", matched)
    print("MISSING SKILLS:", missing)
    print("----------------------")

    # Let's also print what was originally stored in DB, to see if that's the discrepancy
    print("DB PARSED SKILLS:", parsed_profile.get("skills", []))

if __name__ == "__main__":
    run_debug()

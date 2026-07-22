# ResumeIQ AI — Agentic NLP Recruitment Platform

ResumeIQ AI is an agentic recruitment and resume screening platform powered by **LangGraph multi-agent orchestration**. It ingests candidate resumes (PDF, DOCX), extracts structured candidate profiles using natural language processing (NLP) with synonym/alias normalization, runs weighted ATS semantic evaluations, and generates grounded executive feedback using Google Gemini.

---

## 🚀 Key Features

* **Agentic NLP Workflow (LangGraph)**: Replaced sequential processing with an autonomous multi-agent graph architecture (`DocumentAgent`, `NLPAgent`, `ATSAgent`, `AIAgent`, `DatabaseAgent`) managed by a central supervisor state graph with conditional edge routing and self-healing error state handling.
* **Synonym & Alias Skill Normalization**: Comprehensive `SKILL_ALIASES` taxonomy matching aliases (e.g. `Fast API` → `FastAPI`, `ML` → `Machine Learning`, `ReactJS` → `React`, `Postgres` → `PostgreSQL`, `LLM` → `LLMs`) using regex word boundaries to prevent false negative missing skills.
* **Grounded Gemini AI Feedback**: Uses Google Gemini to generate 4-bullet executive summaries (Summary, Strengths, Weaknesses, Recommendation) strictly grounded on structured match results (`matched_skills`, `missing_skills`, ATS scores) to completely eliminate AI hallucinations.
* **High-Fidelity Document Processing**: Secure, chunk-buffered document text extraction supporting PDF (PyMuPDF) and DOCX (python-docx) files with file signature verification.
* **Semantic Compatibility Matching**: Uses Sentence Transformers (`all-MiniLM-L6-v2`) to generate 384-dimensional vector embeddings of resumes and job descriptions, calculating cosine similarities for deep semantic matching.
* **Neon PostgreSQL Serverless Integration**: Raw, parameterized SQL queries via thread-safe `ThreadedConnectionPool` using the standard `psycopg2` driver. Includes automated table initialization on startup.
* **Developer Verification Dashboard**: Next.js 15 app featuring live status monitors, document ingestion preview, and detailed ATS compatibility breakdown.

---

## 🛠 Tech Stack

* **Orchestration**: LangGraph, LangChain Core.
* **Backend**: FastAPI, Python 3.12+, Psycopg2 (raw SQL), spaCy (NLP), Sentence Transformers (embeddings), PyMuPDF (PDF), python-docx (Word), Google Gemini (Generative AI).
* **Frontend**: Next.js 15, React, Tailwind CSS.
* **Database**: Neon Serverless PostgreSQL.

---

## 📂 Project Directory Structure

```text
├── backend/
│   ├── app/
│   │   ├── agents/                   # LangGraph Multi-Agent System
│   │   │   ├── state.py              # ResumeGraphState schema
│   │   │   ├── graph.py              # StateGraph orchestration & routing
│   │   │   ├── supervisor.py         # Graph entrypoint runner
│   │   │   ├── document_agent.py     # Text extraction agent
│   │   │   ├── nlp_agent.py          # NER & skill parsing agent
│   │   │   ├── ats_agent.py          # Scoring & vector similarity agent
│   │   │   ├── ai_agent.py           # Grounded Gemini summary agent
│   │   │   └── database_agent.py     # Neon PostgreSQL persistence agent
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── health.py         # Health check endpoint
│   │   │   │   ├── resume.py         # Resume upload endpoint
│   │   │   │   ├── job_description.py# JD ingestion endpoint
│   │   │   │   └── matching.py       # LangGraph ATS matching endpoint
│   │   │   └── router.py             # API router assembly
│   │   ├── core/
│   │   │   ├── config.py             # Application settings loader
│   │   │   ├── constants.py          # Central constants & weights
│   │   │   ├── database.py           # psycopg2 pool & schema builder
│   │   │   ├── exceptions.py         # Global exception handlers
│   │   │   ├── logging.py            # Structured logger configs
│   │   │   ├── security.py           # Sanitizers & validators
│   │   │   └── schema.sql            # Table definitions (DDL)
│   │   ├── services/
│   │   │   ├── ai/
│   │   │   │   └── gemini.py         # Grounded Gemini AI service
│   │   │   ├── matching/
│   │   │   │   └── matcher.py        # Weighted ATS evaluation engine
│   │   │   ├── nlp/
│   │   │   │   ├── embeddings.py     # Vector embeddings & cosine similarity
│   │   │   │   └── parser.py         # spaCy NER & skill taxonomy parser
│   │   │   └── resume/
│   │   │       ├── extractor.py      # Document text parser (fitz/docx)
│   │   │       ├── service.py        # Raw SQL orchestration service
│   │   │       └── storage.py        # Local file storage
│   │   └── main.py                   # FastAPI application factory
│   ├── requirements.txt              # Python dependencies
│   └── main.py                       # Development entrypoint
│
└── frontend/
    ├── src/
    │   └── app/
    │       ├── layout.tsx            # Base HTML layout
    │       ├── globals.css           # Tailwind CSS file
    │       └── page.tsx              # Verification Dashboard UI
    ├── package.json                  # Node scripts & dependencies
    └── tsconfig.json                 # TypeScript settings
```

---

## ⚙ Startup Instructions

### 1. Backend Server Setup

Navigate into the backend folder, configure environments, and spin up the server:

```powershell
cd backend

# Activate Virtual Environment
.\venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Start the Backend Server (Auto-builds schema tables on boot)
python main.py
```
*Backend runs live at: **http://localhost:8000** (interactive swagger docs available at `/docs`).*

### 2. Frontend Dashboard Setup

Navigate into the frontend folder and boot up the development server:

```bash
cd frontend

# Install Dependencies
npm install

# Start Dev Server
npm run dev
```
*Frontend runs live at: **http://localhost:3000**.*

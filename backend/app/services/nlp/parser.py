"""
NLP Parsing Service using spaCy and regex entity extraction.
"""
import re
from typing import Any, Dict, List, Optional, Set
import spacy

from app.core.config import settings

# Comprehensive Skill Taxonomy mapping aliases to canonical names
SKILL_ALIASES = {
    "fast api": "FastAPI",
    "fastapi": "FastAPI",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "postgressql": "PostgreSQL",
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    "large language model": "LLMs",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "transformers": "Sentence Transformers",
    "sentence transformers": "Sentence Transformers",
    "embedding": "Sentence Transformers",
    "embeddings": "Sentence Transformers",
    "rest": "REST APIs",
    "rest api": "REST APIs",
    "rest apis": "REST APIs",
    "javascript": "JavaScript",
    "js": "JavaScript",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "github": "Git",
    "git": "Git",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "spacy": "spaCy",
    "nlp": "Natural Language Processing",
    "natural language processing": "Natural Language Processing",
    "python": "Python",
    "docker": "Docker",
    "aws": "AWS",
    "amazon web services": "AWS",
    "ci/cd": "CI/CD",
    "typescript": "TypeScript",
    "java": "Java",
    "golang": "Go",
    "go": "Go",
    "c++": "C++",
    "rust": "Rust",
    "c#": "C#",
    "ruby": "Ruby",
    "php": "PHP",
    "sql": "SQL",
    "html": "HTML",
    "css": "CSS",
    "angular": "Angular",
    "vue": "Vue",
    "express": "Express",
    "django": "Django",
    "flask": "Flask",
    "spring boot": "Spring Boot",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
    "sqlite": "SQLite",
    "dynamodb": "DynamoDB",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "terraform": "Terraform",
    "linux": "Linux",
    "bash": "Bash",
    "deep learning": "Deep Learning",
    "computer vision": "Computer Vision",
    "scikit-learn": "Scikit-Learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "opencv": "OpenCV",
    "langchain": "LangChain",
    "rag": "RAG",
    "retrieval augmented generation": "RAG",
    "graphql": "GraphQL",
    "microservices": "Microservices",
    "unit testing": "Unit Testing",
    "pytest": "PyTest",
    "agile": "Agile",
    "scrum": "Scrum",
    "system design": "System Design"
}


class ResumeParser:
    """NLP Parser using spaCy pipeline and regex patterns."""

    _nlp = None

    @classmethod
    def get_nlp(cls):
        """Lazy loader for spaCy model."""
        if cls._nlp is None:
            try:
                cls._nlp = spacy.load(settings.SPACY_MODEL)
            except Exception:
                cls._nlp = spacy.blank("en")
        return cls._nlp

    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email address using regex."""
        match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        return match.group(0) if match else None

    @staticmethod
    def extract_phone(text: str) -> Optional[str]:
        """Extract phone number using regex."""
        pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        match = re.search(pattern, text)
        return match.group(0) if match else None

    @staticmethod
    def extract_links(text: str) -> Dict[str, Optional[str]]:
        """Extract LinkedIn, GitHub, and portfolio URLs."""
        linkedin = re.search(r"https?://(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?", text, re.IGNORECASE)
        github = re.search(r"https?://(www\.)?github\.com/[a-zA-Z0-9_-]+/?", text, re.IGNORECASE)
        return {
            "linkedin": linkedin.group(0) if linkedin else None,
            "github": github.group(0) if github else None,
        }

    @classmethod
    def extract_name(cls, text: str) -> Optional[str]:
        """Extract candidate name using spaCy NER (PERSON label) or fallback to first non-empty line."""
        nlp = cls.get_nlp()
        doc = nlp(text[:1000])  # Scan top part of resume for candidate name
        for ent in doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) <= 4:
                return ent.text.strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line.split()) <= 4 and not re.search(r"@|http|phone|resume", first_line, re.IGNORECASE):
                return first_line
        return None

    @staticmethod
    def extract_skills(text: str, custom_taxonomy: Optional[Dict[str, str]] = None) -> List[str]:
        """Extract technical skills matching taxonomy in lowercased text."""
        taxonomy = custom_taxonomy or SKILL_ALIASES
        text_lower = text.lower()
        extracted = set()
        for alias, canonical in taxonomy.items():
            escaped_alias = re.escape(alias)
            # Edge cases for symbols like c++ where word boundaries \b fail
            if alias in ["c++", "c#"]:
                pattern = r"(?:\b|\s)" + escaped_alias + r"(?:\s|\b|$)"
            else:
                pattern = r"\b" + escaped_alias + r"\b"
                
            if re.search(pattern, text_lower):
                extracted.add(canonical)
        return sorted(list(extracted))

    @staticmethod
    def extract_sections(text: str) -> Dict[str, str]:
        """Heuristically separate resume into common sections."""
        lines = text.split('\n')
        sections = {"Experience": [], "Projects": [], "Education": [], "Skills": [], "Summary": []}
        current_section = "Summary"
        
        for line in lines:
            line_lower = line.strip().lower()
            if not line_lower:
                continue
                
            # Header heuristics
            if line_lower in ["experience", "work experience", "employment history", "professional experience"]:
                current_section = "Experience"
                continue
            elif line_lower in ["projects", "personal projects", "academic projects", "key projects"]:
                current_section = "Projects"
                continue
            elif line_lower in ["education", "academic background"]:
                current_section = "Education"
                continue
            elif line_lower in ["skills", "technical skills", "technologies"]:
                current_section = "Skills"
                continue
                
            sections[current_section].append(line.strip())
            
        return {k: "\n".join(v) for k, v in sections.items()}

    @classmethod
    def parse_resume_text(cls, text: str) -> Dict[str, Any]:
        """Full parsing pipeline for raw resume text."""
        email = cls.extract_email(text)
        phone = cls.extract_phone(text)
        links = cls.extract_links(text)
        name = cls.extract_name(text)
        skills = cls.extract_skills(text)
        sections = cls.extract_sections(text)

        return {
            "contact_info": {
                "name": name,
                "email": email,
                "phone": phone,
                "linkedin": links.get("linkedin"),
                "github": links.get("github"),
            },
            "summary": sections["Summary"][:300].strip() if sections["Summary"] else (text[:300].strip() if text else ""),
            "skills": skills,
            "sections": sections,
            "raw_length": len(text),
        }

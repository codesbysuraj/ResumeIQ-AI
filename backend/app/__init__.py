"""
ResumeIQ AI — Backend Application Package.

Package layout:
    app.core        Configuration, database, logging, exceptions, security
    app.api         Route definitions (one file per domain)
    app.models      SQLAlchemy ORM models
    app.schemas     Pydantic request/response models
    app.services    Business logic (resume, NLP, matching, ATS, AI)
    app.utils       Shared helper functions
    app.main        Application factory (create_app)
"""

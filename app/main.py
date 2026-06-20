from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.session import Base, engine

# Learning-friendly startup. Alembic should manage schema changes after the first version.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="TaskFlow API: JWT authentication, refresh tokens, task CRUD, and Docker support.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {
        "message": "TaskFlow API is running",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }

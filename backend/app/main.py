from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import auth, content, social, analytics, campaigns, assistant, reports
import sys

settings = get_settings()

if not settings.SECRET_KEY:
    print("ERROR: SECRET_KEY is not set. Configure it via .env file or SECRET_KEY environment variable.", file=sys.stderr)
    sys.exit(1)

app = FastAPI(
    title="Marketing AI Platform",
    description="AI-powered digital marketing platform with autonomous agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(social.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "Marketing AI Platform",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}

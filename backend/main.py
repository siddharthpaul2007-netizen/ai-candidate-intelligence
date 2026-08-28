from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.api.router import router as api_router

app = FastAPI(
    title="AI Candidate Intelligence Platform API",
    description="Multi-Agent candidate evaluation, debate, and consensus API",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend is running successfully."
    }

app.include_router(api_router, prefix="/api")

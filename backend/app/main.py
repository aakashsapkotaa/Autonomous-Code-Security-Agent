"""
SecureShift FastAPI Backend
Main application entrypoint
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import scans, repositories, vulnerabilities, health, github

# Import models to ensure they're registered
from app.models import scan, repository, vulnerability, ai_fix

app = FastAPI(
    title="SecureShift API",
    description="Autonomous Code Security Agent Backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(scans.router, prefix="/api/scans", tags=["scans"])
app.include_router(repositories.router, prefix="/api/repositories", tags=["repositories"])
app.include_router(vulnerabilities.router, prefix="/api/vulnerabilities", tags=["vulnerabilities"])
app.include_router(github.router, prefix="/api/github", tags=["github"])

@app.get("/")
async def root():
    return {
        "message": "SecureShift API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "operational"
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("🚀 SecureShift API starting up...")
    print(f"📊 Supabase URL: {settings.SUPABASE_URL}")
    print(f"🔧 MCP Orchestrator: {settings.MCP_ORCHESTRATOR_URL}")
    print(f"🤖 MCP Fixer: {settings.MCP_FIXER_URL}")
    print(f"📝 MCP Reporter: {settings.MCP_REPORTER_URL}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 SecureShift API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

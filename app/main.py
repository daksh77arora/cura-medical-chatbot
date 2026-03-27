from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import global_exception_handler
# Heavy import deferred to lazy loading
# from app.rag.pipeline import RAGPipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: basic initialization
    setup_logging()
    app.state.rag = None # Initialize as None, will lazy-load
    yield
    # Shutdown: clean up if initialized
    if app.state.rag:
        await app.state.rag.cleanup()

app = FastAPI(
    title="MediBot API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
)

@app.get("/")
def root():
    return {
        "message": "Welcome to the MediBot Pro API v2.0",
        "status": "Online",
        "docs": "/docs (if in debug mode)",
        "health": "/health"
    }

app.add_middleware(CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(health_router)

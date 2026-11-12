from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="PARTH AI Server",
    version="1.0.0",
    description="Backend de geração procedural do PARTH: IA para Roblox.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS is configurable. Roblox HttpService is server-to-server and does not need CORS.
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-API-Key", "Authorization"],
    )

app.include_router(api_router)

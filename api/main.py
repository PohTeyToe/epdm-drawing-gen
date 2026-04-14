"""FastAPI application entry point for the drawing registry web UI."""

from __future__ import annotations

import re

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Morgan Solar Drawing Registry API",
        description="Web wrapper around the EPDM drawing number generator.",
        version="0.1.0",
    )

    allow_origins = [
        "http://localhost:5183",
        "http://127.0.0.1:5183",
        "http://localhost:5173",
    ]
    allow_origin_regex = r"https://.*\.vercel\.app"

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=allow_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "service": "morgan-solar-drawing-registry",
            "version": "0.1.0",
            "docs": "/docs",
        }

    return app


app = create_app()

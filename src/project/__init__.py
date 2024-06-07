import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import main


def create_app() -> FastAPI:
    app = FastAPI(
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        title="Knowledge Hub",
        version="0.1.0",
    )
    current_dir = os.path.dirname(os.path.realpath(__file__))
    static_dir = os.path.join(current_dir, ".", "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(main.router)

    return app


app = create_app()

import os
from contextlib import suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import router as v1_router
from app.api.v1 import websocket
from app.config import settings

app = FastAPI(title="Polsia AI Business Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix="/api/v1")
app.include_router(websocket.router)

with suppress(OSError):  # read-only filesystem (e.g. some test/sandbox environments)
    os.makedirs(settings.sites_dir, exist_ok=True)
app.mount("/sites", StaticFiles(directory=settings.sites_dir, html=True, check_dir=False), name="sites")

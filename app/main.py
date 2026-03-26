from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.users import router as users_router
from app.core.config import settings
from app.db.init_db import init_db

app = FastAPI(title="HDT Identity Provider")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.routers import auth, blog, email, categories, booking, users, public_blogs, public_categories
from app.services import auth_service

os.makedirs(settings.MEDIA_DIR, exist_ok=True)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://drpremgastro.sg",
        "https://www.drpremgastro.sg"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        auth_service.ensure_default_admin(db)
    finally:
        db.close()


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(blog.router)
app.include_router(email.router)
app.include_router(categories.router)
app.include_router(booking.router)
app.include_router(users.router)
app.include_router(public_blogs.router)
app.include_router(public_categories.router)

import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "Request failed."
    return JSONResponse(status_code=exc.status_code, content={"status": exc.status_code, "message": message})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.get("loc", []) if part != "body")
        detail = first.get("msg", "Validation error")
        message = f"{location}: {detail}" if location else detail
    else:
        message = "Validation error"
    return JSONResponse(status_code=422, content={"status": 422, "message": message})


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

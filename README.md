# acorn-prem-be

Backend API for Acorn (FastAPI).

## Requirements
- Python 3.13+
- PostgreSQL 14+
- Optional: `uv` (fast dependency manager)

## Language, Framework & Tools
- Language: Python
- Framework: FastAPI
- DB/ORM: PostgreSQL, SQLAlchemy
- Auth: JWT (python-jose), passlib (bcrypt)
- Email: fastapi-mail
- Server: Uvicorn

## How to Run
1) Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate
```

2) Install dependencies
```bash
pip install -e .
```
If you use `uv`, you can also run:
```bash
uv sync
```

3) Configure environment variables
- Copy `.env-example` to `.env`
- Set `DATABASE_URL`, `JWT_SECRET`, and mail settings as needed

4) Start the API
```bash
python main.py
```

5) Open health check
- http://localhost:8000/health

## Notes
- Default admin is seeded on startup from `.env`:
  - `ADMIN_SEED_EMAIL`, `ADMIN_SEED_PASSWORD`, `ADMIN_SEED_ROLE`
- Password reset emails use `FRONTEND_URL` to build the reset link

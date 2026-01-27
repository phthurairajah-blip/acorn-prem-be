from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Ensure models are imported so metadata is populated before create_all.
from app.db.models import blog, email_log, user, category, booking  # noqa: F401,E402

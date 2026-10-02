import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select

from .auth import hash_password
from .database import Base, SessionLocal, engine
from .models import Subject, User
from .routers import auth_router, bookings, subjects


def seed_data():
    with SessionLocal() as db:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com").lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "admin12345")

        admin = db.scalar(select(User).where(User.email == admin_email))
        if not admin:
            db.add(
                User(
                    email=admin_email,
                    password_hash=hash_password(admin_password),
                    role="admin",
                )
            )

        has_subject = db.scalar(select(Subject.id).limit(1))
        if not has_subject:
            db.add_all(
                [
                    Subject(
                        title="Математика",
                        description="Индивидуальное занятие по математике",
                        price=1200,
                        duration_minutes=60,
                        is_active=True,
                    ),
                    Subject(
                        title="Физика",
                        description="Индивидуальное занятие по физике",
                        price=1200,
                        duration_minutes=60,
                        is_active=True,
                    ),
                ]
            )
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_data()
    yield


app = FastAPI(
    title="Tutor Booking API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router.router)
app.include_router(subjects.router)
app.include_router(bookings.router)


@app.get("/health")
def health():
    return {"status": "ok"}

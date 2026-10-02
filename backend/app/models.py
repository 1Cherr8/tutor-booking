from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="client")

    bookings: Mapped[list["Booking"]] = relationship(back_populates="user")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="subject")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="RESTRICT"))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=False))
    status: Mapped[str] = mapped_column(String(30), default="planned")
    comment: Mapped[str] = mapped_column(Text, default="")

    user: Mapped[User] = relationship(back_populates="bookings")
    subject: Mapped[Subject] = relationship(back_populates="bookings")

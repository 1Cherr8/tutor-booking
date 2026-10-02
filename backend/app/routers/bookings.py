from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user
from ..database import get_db
from ..models import Booking, Subject, User
from ..schemas import BookingCreate, BookingRead, BookingUpdate

router = APIRouter(prefix="/bookings", tags=["bookings"])


def to_read(booking: Booking) -> BookingRead:
    return BookingRead(
        id=booking.id,
        user_id=booking.user_id,
        client_email=booking.user.email,
        subject_id=booking.subject_id,
        subject_title=booking.subject.title,
        start_time=booking.start_time,
        status=booking.status,
        comment=booking.comment,
    )


def get_booking_or_404(db: Session, booking_id: int) -> Booking:
    stmt = (
        select(Booking)
        .options(joinedload(Booking.user), joinedload(Booking.subject))
        .where(Booking.id == booking_id)
    )
    booking = db.scalar(stmt)
    if not booking:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return booking


def check_access(user: User, booking: Booking):
    if user.role != "admin" and booking.user_id != user.id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой записи")


@router.get("", response_model=list[BookingRead])
def list_bookings(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    stmt = select(Booking).options(joinedload(Booking.user), joinedload(Booking.subject))
    if user.role != "admin":
        stmt = stmt.where(Booking.user_id == user.id)
    stmt = stmt.order_by(Booking.start_time)
    return [to_read(item) for item in db.scalars(stmt).all()]


@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = get_booking_or_404(db, booking_id)
    check_access(user, booking)
    return to_read(booking)


@router.post("", response_model=BookingRead, status_code=201)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    subject = db.get(Subject, data.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    if not subject.is_active:
        raise HTTPException(status_code=400, detail="На этот предмет сейчас нельзя записаться")

    owner_id = user.id
    if user.role == "admin" and data.user_id is not None:
        owner = db.get(User, data.user_id)
        if not owner:
            raise HTTPException(status_code=404, detail="Клиент не найден")
        owner_id = owner.id

    booking = Booking(
        user_id=owner_id,
        subject_id=data.subject_id,
        start_time=data.start_time,
        status="planned",
        comment=data.comment,
    )
    db.add(booking)
    db.commit()
    return to_read(get_booking_or_404(db, booking.id))


@router.put("/{booking_id}", response_model=BookingRead)
def update_booking(
    booking_id: int,
    data: BookingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = get_booking_or_404(db, booking_id)
    check_access(user, booking)

    subject = db.get(Subject, data.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    booking.subject_id = data.subject_id
    booking.start_time = data.start_time
    booking.comment = data.comment
    if user.role == "admin":
        booking.status = data.status
    elif data.status in {"planned", "cancelled"}:
        booking.status = data.status

    db.commit()
    return to_read(get_booking_or_404(db, booking.id))


@router.delete("/{booking_id}", status_code=204)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    booking = get_booking_or_404(db, booking_id)
    check_access(user, booking)
    db.delete(booking)
    db.commit()

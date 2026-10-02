from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import get_current_user, require_admin
from ..database import get_db
from ..models import Subject, User
from ..schemas import SubjectCreate, SubjectRead, SubjectUpdate

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.get("", response_model=list[SubjectRead])
def list_subjects(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.scalars(select(Subject).order_by(Subject.id)).all()


@router.get("/{subject_id}", response_model=SubjectRead)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    return subject


@router.post("", response_model=SubjectRead, status_code=201)
def create_subject(
    data: SubjectCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    subject = Subject(**data.model_dump())
    db.add(subject)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Предмет с таким названием уже существует")
    db.refresh(subject)
    return subject


@router.put("/{subject_id}", response_model=SubjectRead)
def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    for key, value in data.model_dump().items():
        setattr(subject, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Предмет с таким названием уже существует")
    db.refresh(subject)
    return subject


@router.delete("/{subject_id}", status_code=204)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    db.delete(subject)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Нельзя удалить предмет, на который уже есть записи",
        )

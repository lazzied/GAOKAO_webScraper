from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, database, schemas

router = APIRouter(prefix="/exams", tags=["exams"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ExamRead, status_code=201)
def create_exam(
    exam: schemas.ExamCreate,
    db: Session = Depends(get_db),
):
    return crud.create_exam(db, exam)

@router.patch("/{exam_id}", response_model=schemas.ExamRead)
def partial_update_exam(
    exam_id:      int,
    new_data:     schemas.ExamUpdate,
    db:           Session = Depends(get_db),
):
    updated = crud.update_item_db(db, exam_id, new_data)
    if not updated:
        raise HTTPException(404, "Exam not found")
    return updated

@router.get("/last", response_model=schemas.ExamRead)
def read_last_exam(db: Session = Depends(get_db)):
    last = crud.get_last_exam(db)
    if not last:
        raise HTTPException(404, "No exams yet")
    return last

@router.get("/{exam_id}", response_model=schemas.ExamRead)
def read_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = crud.get_exam(db, exam_id)
    if not exam:
        raise HTTPException(404, "Exam not found")
    return exam

@router.get("/", response_model=list[schemas.ExamRead])
def list_exams(
    skip: int = 0,
    limit: int = 100,
    db:    Session = Depends(get_db),
):
    return crud.get_exams(db, skip, limit)

@router.delete("/{exam_id}", status_code=204)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    if not crud.delete_exam(db, exam_id):
        raise HTTPException(404, "Exam not found")

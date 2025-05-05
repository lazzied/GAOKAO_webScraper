from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models, database

router = APIRouter(prefix="/exams", tags=["exams"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=models.Exam, status_code=201)
def create_exam(exam: models.Exam, db: Session = Depends(get_db)):
    return crud.create_exam(db, exam)

@router.get("/{exam_id}", response_model=models.Exam)
def read_exam(exam_id: int, db: Session = Depends(get_db)):
    db_ex = crud.get_exam(db, exam_id)
    if not db_ex:
        raise HTTPException(status_code=404, detail="Exam not found")
    return db_ex

@router.get("/", response_model=list[models.Exam])
def list_exams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_exams(db, skip, limit)

@router.delete("/{exam_id}", status_code=204)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    if not crud.delete_exam(db, exam_id):
        raise HTTPException(status_code=404, detail="Exam not found")
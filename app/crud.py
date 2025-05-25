from sqlalchemy.orm import Session
from . import models, schemas

def get_exam(db: Session, exam_id: int) -> models.Exam | None:
    return (
        db.query(models.Exam)
          .filter(models.Exam.exam_id == exam_id)
          .first()
    )

def get_exams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Exam).offset(skip).limit(limit).all()

def get_last_exam(db: Session) -> models.Exam | None:
    return db.query(models.Exam).order_by(models.Exam.exam_id.desc()).first()

def create_exam(db: Session, exam_in: schemas.ExamCreate) -> models.Exam:
    db_exam = models.Exam(**exam_in.dict())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def update_item_db(db: Session, exam_id: int, exam_in: schemas.ExamUpdate) -> models.Exam:
    db_exam = get_exam(db, exam_id)
    if not db_exam:
        return None
    update_data = exam_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_exam, field, value)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def delete_exam(db: Session, exam_id: int) -> bool:
    db_exam = get_exam(db, exam_id)
    if not db_exam:
        return False
    db.delete(db_exam)
    db.commit()
    return True

def create_solution(
    db: Session,
    sol_in: schemas.SolutionCreate,
) -> models.Solution:
    db_sol = models.Solution(**sol_in.dict())
    db.add(db_sol)
    db.commit()
    db.refresh(db_sol)
    return db_sol

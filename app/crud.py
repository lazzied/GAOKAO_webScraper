#DB interaction logic
from sqlalchemy.orm import Session
from . import models

def get_exam(db: Session, exam_id: int) -> models.Exam | None:
    return db.query(models.Exam).filter(models.Exam.exam_id == exam_id).first()

def get_exams(db: Session, skip: int = 0, limit: int = 100):  #this is for pagination
    return db.query(models.Exam).offset(skip).limit(limit).all()

def get_all_exams(db: Session):
    return db.query(models.Exam).all()


def create_exam(db: Session, exam: models.Exam) -> models.Exam:
    db_ex = models.Exam(**exam.dict())  # no exam_id here
    db.add(db_ex)
    db.commit()
    db.refresh(db_ex)  # now db_ex.exam_id is populated
    return db_ex

def delete_exam(db: Session, exam_id: int) -> bool:
    ex = get_exam(db, exam_id)
    if not ex:
        return False
    db.delete(ex)
    db.commit()
    return True

def create_solution(db:Session, solution: models.Solution)-> models.Solution:
    db_sl = models.Solution(**solution.dict())  # no exam_id here
    db.add(db_sl)
    db.commit()
    db.refresh(db_sl)  # now db_ex.exam_id is populated
    return db_sl
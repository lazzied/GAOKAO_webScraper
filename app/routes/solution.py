from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models, database

router = APIRouter(prefix="/solutions", tags=["solutions"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=models.Solution, status_code=201)
def create_Solution(Solution: models.Solution, db: Session = Depends(get_db)):
    return crud.create_solution(db, Solution)
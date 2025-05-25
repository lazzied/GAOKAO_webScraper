from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, database, schemas

router = APIRouter(prefix="/solutions", tags=["solutions"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/",
    response_model=schemas.SolutionSchema,
    status_code=201,
)
def create_solution(
    sol_in: schemas.SolutionCreate,
    db: Session = Depends(get_db),
):
    return crud.create_solution(db, sol_in)

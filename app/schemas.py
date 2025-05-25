from pydantic import BaseModel
from typing  import Optional, List

class SolutionSchema(BaseModel):
    solution_id: int
    exam_id:     int

    class Config:
        orm_mode = True

class SolutionBase(BaseModel):
    exam_id: int

class SolutionCreate(SolutionBase):
    pass  # Nothing extra, used when creating



class ExamBase(BaseModel):
    country:      Optional[str] = None
    province:     Optional[str] = None
    answers:      Optional[bool] = False
    subject:      Optional[str] = None
    year:         Optional[int]  = None
    duration:     Optional[int]  = None
    coefficient:  Optional[int]  = None
    exam_path:    Optional[str]  = None
    answers_path: Optional[str]  = None
    exam_type:    Optional[str]  = None
    score:        Optional[int]  = None

class ExamCreate(ExamBase):
    """All fields optional, defaults applied in model __init__"""

class ExamUpdate(ExamBase):
    """Same as Create; we’ll do a partial update in crud"""

class ExamRead(ExamBase):
    exam_id:   int
    solutions: List[SolutionSchema] = []

    class Config:
        orm_mode = True



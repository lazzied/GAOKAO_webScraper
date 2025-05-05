# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship

class Exam(Base):
    __tablename__ = "exams"

    exam_id       = Column(Integer, primary_key=True, index=True, autoincrement=True)
    country       = Column(String,  nullable=True)
    province      = Column(String,  nullable=True)
    answers       = Column(Boolean, nullable=True)
    subject       = Column(String,  nullable=True)
    year          = Column(Date,    nullable=True)
    duration      = Column(Integer, nullable=True)   # in minutes
    coefficient   = Column(Integer, nullable=True)
    exam_path     = Column(String,  nullable=True)
    answers_path  = Column(String,  nullable=True)
    exam_type     = Column(String, nullable=True)
    score         = Column(Integer, nullable=True)

    def __init__(
        self,
        country,
        province=None,
        score=None,
        subject=None,
        year=None,
        duration=None,
        coefficient=None,
        exam_type=None,
        answers=False
    ):
        self.country     = country
        self.province    = province
        self.score       = score
        self.subject     = subject
        self.year        = year 
        self.duration    = duration  
        self.coefficient = coefficient
        self.exam_type   = exam_type 
        self.answers     = answers

    solutions = relationship("Solution", back_populates="exam", cascade="all, delete-orphan")


class Solution(Base):
    __tablename__ = "solutions"

    solution_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    exam_id     = Column(Integer, ForeignKey("exams.exam_id"), nullable=False, index=True)

    def __init__ (
            self,
            exam_id
    ):
        self.exam_id = exam_id

    # optional back-ref so you can do solution.exam and exam.solutions
    exam = relationship("Exam", back_populates="solutions")

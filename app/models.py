# app/models.py
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship

class Exam(Base):
    __tablename__ = "exams"

    exam_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    country = Column(String, nullable=True)
    province = Column(String, nullable=True)
    answers = Column(Boolean, nullable=True)
    subject = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    duration = Column(Integer, nullable=True)  
    coefficient = Column(Integer, nullable=True)
    exam_path = Column(String, nullable=True)
    answers_path = Column(String, nullable=True)
    exam_type = Column(String, nullable=True)
    score = Column(Integer, nullable=True)
    total_pages_number= Column(Integer, nullable=True)
    total_pages_scraped= Column(Integer, nullable=True)

    # Modified constructor
    def __init__(self, **kwargs):
        # Set default values first
        self.answers = False
        # Update with actual values
        super().__init__(**kwargs)

    solutions = relationship("Solution", back_populates="exam", cascade="all, delete-orphan")

class Solution(Base):
    __tablename__ = "solutions"

    solution_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    exam_id     = Column(Integer, ForeignKey("exams.exam_id"), nullable=False, index=True)
    total_pages_number= Column(Integer, nullable=True)
    total_pages_scraped= Column(Integer, nullable=True)

    def __init__ (
            self,
            exam_id
    ):
        self.exam_id = exam_id

    # optional back-ref so you can do solution.exam and exam.solutions
    exam = relationship("Exam", back_populates="solutions")

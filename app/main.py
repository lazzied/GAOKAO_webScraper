# entry point of fastAPI app
from fastapi import FastAPI
from . import models, database
from .routes import exam, solution

# Create tables (including auto-incr PKs)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Exam Collection API")

app.include_router(exam.router)
app.include_router(solution.router)
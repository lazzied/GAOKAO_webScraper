#DB connection and session setupfrom sqlalchemy import create_engine, Column, String, Integer, CHAR
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/CEE"


engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(bind=engine)



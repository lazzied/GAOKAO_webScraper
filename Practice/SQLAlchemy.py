from sqlalchemy import create_engine, Column, String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import ForeignKey

Base = declarative_base()

class Person(Base):
    __tablename__ = "people"
    ssn = Column("ssn", Integer, primary_key=True)
    firstname = Column("firstname", String)
    lastname = Column("lastname", String)
    gender = Column("gender", CHAR)
    age = Column("age", Integer)

    def __init__(self, ssn, first, last, gender, age):
        self.ssn = ssn
        self.firstname = first
        self.lastname = last
        self.gender = gender
        self.age = age

    def __repr__(self):
        return f"({self.ssn}) {self.firstname} {self.lastname} {self.gender} {self.age}"


class Thing(Base):
    __tablename__ = 'things'

    tid = Column("tid", Integer, primary_key = True)
    description = Column("description", String)
    owner= Column (Integer, ForeignKey("people.ssn"))

    def __init__(self, tid, description, owner):
        self.tid = tid
        self.description= description
        self.owner= owner
    def __repr__(self):
        return f""

# Connect to database
try:
    engine = create_engine("postgresql://postgres:postgres@localhost:5432/CEE", echo=True)
except SQLAlchemyError as e:
    print("Couldn't connect:", e)

Base.metadata.create_all(bind=engine)

Session = sessionmaker(bind=engine)
session = Session()

# Helper function to check and add if not exists
def add_person_if_not_exists(ssn, first, last, gender, age):
    if not session.query(Person).filter_by(ssn=ssn).first():  #first() is the first row from the database
        person = Person(ssn, first, last, gender, age)
        session.add(person)
        session.commit()
        print(f"Added: {person}")
    else:
        print(f"Skipped: {ssn} already exists.")

# Add persons conditionally
add_person_if_not_exists(12312, "Mike", "Smith", "m", 35)
add_person_if_not_exists(31234, "Anna", "Blue", "f", 40)
add_person_if_not_exists(985647, "BoB", "Blue", "m", 35)
add_person_if_not_exists(78245, "Angela", "Cold", "f", 22)


results = session.query(Person).filter(Person.firstname.in_(["  Anna", "Mike"]))


Base.metadata.drop_all(bind=engine)

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.openapi.utils import get_openapi

from typing import List, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()

# database setup
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


# Example:
# “id”:2234,
# “firstName”: “Mike”,
# “lastName”: “Wong”,
# “class”:”3 A”,
# “nationality”: “Singapore”

class StudentBase(SQLModel):
    firstName: str = Field(description="The students first name")
    lastName: str = Field(description="The students last name")
    student_class: str = Field(description="The students current class")
    nationality: str | None = Field(
        default=None, title="Students nationality", max_length=100
    )


class Student(StudentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class StudentRead(StudentBase):
    id: int


class StudentUpdate(SQLModel):
    firstName: Optional[str] = None
    student_class: Optional[str] = None


class StudentCreate(StudentBase):
    pass


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
async def on_startup():
    create_db_and_tables()


@app.get("/")
async def root():
    """ For testing connection """
    return {"message": "Hello World"}


@app.get("/fetchStudents/", response_model=List[StudentRead])
async def get_student_enrollments(
    *,
    session: Session = Depends(get_session),
    s_class: Optional[str] = None,
    id: Optional[int] = None
):
    """ Get students either by all, by class, or by student id
        url params: ?s_class= | ?id=
    """
    student_enrollments = session.exec(select(Student)).all()

    if s_class:
        same_class_list = []

        for student in student_enrollments:
            if student.student_class == s_class:
                same_class_list.append(student)

        if not same_class_list:
            raise HTTPException(status_code=404, detail="No students found for that class")

        return same_class_list

    if id:
        student = session.get(Student, id)

        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        return student

    return student_enrollments


@app.post("/fetchStudents/", response_model=StudentRead)
async def create_student_enrollment(*, session: Session = Depends(get_session), student: StudentCreate):
    student_db = Student.from_orm(student)
    session.add(student_db)
    session.commit()
    session.refresh(student_db)

    return student_db


@app.put("/fetchStudents/{student_id}", response_model=StudentRead)
async def update_student_enrollment(
    *, session: Session = Depends(get_session), student_id: int, student: StudentUpdate
):
    student_db = session.get(Student, student_id)

    if not student_db:
        raise HTTPException(status_code=404, detail="Student not found")

    student_data = student.dict(exclude_unset=True)

    for key, value in student_data.items():
        setattr(student_db, key, value)

    session.add(student_db)
    session.commit()
    session.refresh(student_db)

    return student_db


@app.delete("/fetchStudents/{student_id}")
async def delete_student(student_id: int):
    with Session(engine) as session:
        student = session.get(Student, student_id)

        if not student:
            raise HTTPException(status_code=404, detail="Student enrollment not found")

        session.delete(student)
        session.commit()

        return {"Student removed": True}


@app.post("/createSampleData")
async def create_sample_data():
    """ Populate database with sample data to make things easier :) """
    student_1 = Student(firstName="Mike", lastName="Wong", student_class="A 3", nationality="Singapore")
    student_2 = Student(firstName="King", lastName="Arthur", student_class="A 3", nationality="England")
    student_3 = Student(firstName="John", lastName="Doe", student_class="0 A", nationality="Brazil")
    student_4 = Student(firstName="Jane", lastName="Doe", student_class="C 2", nationality="Guam")
    student_5 = Student(firstName="That", lastName="Guy", student_class="D 3", nationality="Atlantis")

    with Session(engine) as session:
        session.add(student_1)
        session.add(student_2)
        session.add(student_3)
        session.add(student_4)
        session.add(student_5)
        session.commit()

    return {"data made": True}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Armada Test 2",
        version="1.0",
        summary="Assessment test to develop a REST API for student enrollment for a department",
        description="FastAPI using SQLModel. This should work...",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    app.openapi_schema = openapi_schema  # cache

    return app.openapi_schema


app.openapi = custom_openapi

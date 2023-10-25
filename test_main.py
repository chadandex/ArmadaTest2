import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import Student, app, get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ---- TESTS ----

def test_create_student(client: TestClient):
    response = client.post(
        "/fetchStudents/", json={
            "firstName": "Mike", "lastName": "Wong", "student_class": "3 A", "nationality": "Singapore"
        }
    )
    data = response.json()

    assert response.status_code == 200
    assert data["firstName"] == "Mike"
    assert data["lastName"] == "Wong"
    assert data["student_class"] == "3 A"
    assert data["nationality"] == "Singapore"
    assert data["id"] is not None


def test_create_student_incomplete(client: TestClient):
    response = client.post("/fetchStudents/", json={"firstName": "John", "lastName": "Doe"})

    assert response.status_code == 422


def test_get_student_by_id(session: Session, client: TestClient):
    student_1 = Student(firstName="Mike", lastName="Wong", student_class="3 A", nationality="Singapore")
    session.add(student_1)
    session.commit()

    response = client.get(f"/fetchStudents/?id={student_1.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["firstName"] == student_1.firstName
    assert data["lastName"] == student_1.lastName
    assert data["student_class"] == student_1.student_class
    assert data["nationality"] == student_1.nationality
    assert data["id"] == student_1.id


def test_get_all_students_by_class(session: Session, client: TestClient):
    student_class = "3 A"
    student_1 = Student(firstName="Mike", lastName="Wong", student_class=student_class, nationality="Singapore")
    student_2 = Student(firstName="King", lastName="Arthur", student_class=student_class, nationality="England")
    student_3 = Student(firstName="John", lastName="Doe", student_class="0 A", nationality="Brazil")

    session.add(student_1)
    session.add(student_2)
    session.add(student_3)
    session.commit()

    response = client.get(f"/fetchStudents/?s_class={student_class}")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 2

    assert data[0]["firstName"] == student_1.firstName
    assert data[0]["lastName"] == student_1.lastName
    assert data[0]["student_class"] == student_1.student_class
    assert data[0]["nationality"] == student_1.nationality
    assert data[0]["id"] == student_1.id

    assert data[1]["firstName"] == student_2.firstName
    assert data[1]["lastName"] == student_2.lastName
    assert data[1]["student_class"] == student_2.student_class
    assert data[1]["nationality"] == student_2.nationality
    assert data[1]["id"] == student_2.id


def test_delete_student(session: Session, client: TestClient):
    student_1 = Student(firstName="Mike", lastName="Wong", student_class="3 A", nationality="Singapore")
    session.add(student_1)
    session.commit()

    response = client.delete(f"/fetchStudents/{student_1.id}")

    student_from_db = session.get(Student, student_1.id)

    assert response.status_code == 200

    assert student_from_db is None

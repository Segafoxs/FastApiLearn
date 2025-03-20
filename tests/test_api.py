import pytest
from fastapi.testclient import TestClient

from sqlalchemy.orm import Session
from sqlalchemy.engine import create_engine
from models.dbModels import Base

from main import app
from api.api import get_db, get_db_user, get_db_user_from_id

class MockResponse:

    @staticmethod
    def none_user(email, db):
        return None

    @staticmethod
    def return_user(email, db):
        user = {"id": 1,
                "username": "admin"}

        return user




@pytest.fixture(name="session",scope="class", autouse=True)
def session_fixture():
    engine = create_engine("postgresql://postgres:admin1@localhost/testDataBase")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


class TestCase():
    def test_get_user(self, client: TestClient, monkeypatch):
        monkeypatch.setattr("api.api.get_db_user_from_id", MockResponse.return_user)

        response = client.get("/user/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["username"] == "admin"

    def test_create_user(self, client: TestClient, monkeypatch):

        monkeypatch.setattr("api.api.get_db_user", MockResponse.return_user)
        # пользователь есть в базе
        response = client.post(
            "/register/", json={"username": "admin", "password": "admin", "email": "admin@mail.ru"}
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "Email is busy"}

        # валидация email
        response = client.post(
            "/register/", json={"username": "serg", "password": "serg", "email": "serg"}
        )

        assert response.status_code == 422


        monkeypatch.setattr("api.api.get_db_user", MockResponse.none_user)
        #валидные данные
        response = client.post(
            "/register/", json={"username": "admin", "password": "admin", "email": "admin@mail.ru"}
        )

        assert response.status_code == 201
        assert response.json() == {"message": "User create successfully!"}


    def test_auth(self, client: TestClient):

        data = {"username": "admin@mail.ru", "password": "admin"}
        response = client.post("/login/", auth=(data["username"], data["password"]))
        assert response.status_code == 200
        assert response.json() == {"message": "You have access to the protected resource!",
         "id": 1,
         "username": "admin"}



    def test_rename_user(self, client: TestClient, monkeypatch):

        #Валидные данные
        response = client.put("/update/1", json={"username": "serg"})
        data = response.json()
        assert response.status_code == 200
        assert data["id"] == 1
        assert data["username"] == "serg"


        #Пользователь не найден
        response = client.put("/update/22", json={"username": "admin"})
        assert response.status_code == 404
        assert response.json() == {"detail": "User is not found"}


        response = client.put("/update/1", json={"username": 224})
        assert response.status_code == 422





    def test_delete_user(self , client: TestClient, monkeypatch):

        # пользователь не найден
        response = client.delete("/delete_user/22")

        assert response.status_code == 404
        assert response.json() == {"detail": "User is not found"}


        # удаление пользователя
        response = client.delete("delete_user/1")

        assert response.status_code == 200
        assert response.json() == {"message": "User delete successfully!"}

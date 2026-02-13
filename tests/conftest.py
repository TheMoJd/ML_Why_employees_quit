"""
Configuration pytest pour les tests.
Utilise une base SQLite en mémoire au lieu de PostgreSQL.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.connection import Base, get_db
from src.api.main import app


# Base de données SQLite en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dépendance get_db pour utiliser SQLite."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override la dépendance avant les tests
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Crée les tables au début de la session de tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Session BDD isolée par test avec rollback automatique."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def auth_headers():
    """Crée un utilisateur de test et retourne les headers Authorization."""
    from fastapi.testclient import TestClient
    from src.database import crud
    from src.api.auth import get_password_hash

    db = TestingSessionLocal()
    try:
        # Créer un user de test s'il n'existe pas
        user = crud.get_user_by_username(db, "testuser")
        if not user:
            crud.create_user(
                db,
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("testpassword"),
            )
    finally:
        db.close()

    # Login pour obtenir le token
    client = TestClient(app)
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

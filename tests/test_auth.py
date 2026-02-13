"""
Tests pour l'authentification JWT (register, login, protection des endpoints).
"""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)

# Compteur pour générer des usernames uniques par test
_counter = 0


def _unique_user():
    """Génère un username et email uniques."""
    global _counter
    _counter += 1
    return {
        "username": f"user_{_counter}",
        "email": f"user_{_counter}@example.com",
        "password": "securepassword",
    }


class TestRegister:

    def test_register_success(self):
        """Créer un compte retourne 201."""
        user = _unique_user()
        response = client.post("/auth/register", json=user)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user["username"]
        assert data["email"] == user["email"]
        assert "hashed_password" not in data
        assert data["is_active"] is True

    def test_register_duplicate_username(self):
        """Username dupliqué retourne 409."""
        user = _unique_user()
        client.post("/auth/register", json=user)
        user2 = {**user, "email": "other@example.com"}
        response = client.post("/auth/register", json=user2)
        assert response.status_code == 409

    def test_register_duplicate_email(self):
        """Email dupliqué retourne 409."""
        user = _unique_user()
        client.post("/auth/register", json=user)
        user2 = {**user, "username": "totally_different"}
        response = client.post("/auth/register", json=user2)
        assert response.status_code == 409

    def test_register_short_password(self):
        """Mot de passe trop court retourne 422."""
        user = _unique_user()
        user["password"] = "abc"
        response = client.post("/auth/register", json=user)
        assert response.status_code == 422

    def test_register_short_username(self):
        """Username trop court retourne 422."""
        response = client.post("/auth/register", json={
            "username": "ab", "email": "x@x.com", "password": "123456"
        })
        assert response.status_code == 422


class TestLogin:

    def test_login_success(self):
        """Login valide retourne un token."""
        user = _unique_user()
        client.post("/auth/register", json=user)
        response = client.post("/auth/token", data={
            "username": user["username"],
            "password": user["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_username(self):
        """Username inexistant retourne 401."""
        response = client.post("/auth/token", data={
            "username": "nonexistent_user_xyz",
            "password": "whatever",
        })
        assert response.status_code == 401

    def test_login_wrong_password(self):
        """Mauvais mot de passe retourne 401."""
        user = _unique_user()
        client.post("/auth/register", json=user)
        response = client.post("/auth/token", data={
            "username": user["username"],
            "password": "wrongpassword",
        })
        assert response.status_code == 401


class TestMe:

    def test_me_with_valid_token(self):
        """GET /auth/me avec token valide retourne le profil."""
        user = _unique_user()
        client.post("/auth/register", json=user)
        login_resp = client.post("/auth/token", data={
            "username": user["username"],
            "password": user["password"],
        })
        token = login_resp.json()["access_token"]
        response = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user["username"]

    def test_me_without_token(self):
        """GET /auth/me sans token retourne 401."""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_me_with_invalid_token(self):
        """GET /auth/me avec token invalide retourne 401."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401


class TestProtectedEndpoints:

    def test_predict_without_token_returns_401(self):
        """POST /predict sans token retourne 401."""
        response = client.post("/predict", json={"age": 35})
        assert response.status_code == 401

    def test_predict_batch_without_token_returns_401(self):
        """POST /predict/batch sans token retourne 401."""
        response = client.post("/predict/batch", json={"employees": []})
        assert response.status_code == 401

    def test_health_remains_public(self):
        """/health reste accessible sans token."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_remains_public(self):
        """/ reste accessible sans token."""
        response = client.get("/")
        assert response.status_code == 200

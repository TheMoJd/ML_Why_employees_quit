"""
Tests pour l'API FastAPI.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


# Fixture réutilisable pour un employé stable
@pytest.fixture
def valid_employee_stable():
    """Données valides pour un employé stable (faible risque de départ)."""
    return {
        "age": 35,
        "genre": "M",
        "revenu_mensuel": 5000.0,
        "statut_marital": "Marié(e)",
        "departement": "Consulting",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 2,
        "nombre_heures_travailless": 80.0,
        "annee_experience_totale": 10,
        "annees_dans_l_entreprise": 5,
        "annees_dans_le_poste_actuel": 3,
        "satisfaction_employee_environnement": 4,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equipe": 4,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 15,
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 3,
        "nombre_employee_sous_responsabilite": 1,
        "distance_domicile_travail": 10,
        "niveau_education": 3,
        "domaine_etude": "Transformation Digitale",
        "ayant_enfants": "Y",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 2,
        "annes_sous_responsable_actuel": 3
    }


@pytest.fixture
def valid_employee_at_risk():
    """Données valides pour un employé à risque (haut risque de départ)."""
    return {
        "age": 28,
        "genre": "M",
        "revenu_mensuel": 2000.0,
        "statut_marital": "Célibataire",
        "departement": "Consulting",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 5,
        "nombre_heures_travailless": 80.0,
        "annee_experience_totale": 6,
        "annees_dans_l_entreprise": 1,
        "annees_dans_le_poste_actuel": 0,
        "satisfaction_employee_environnement": 1,
        "note_evaluation_precedente": 2,
        "niveau_hierarchique_poste": 1,
        "satisfaction_employee_nature_travail": 1,
        "satisfaction_employee_equipe": 2,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "note_evaluation_actuelle": 2,
        "heure_supplementaires": "Oui",
        "augementation_salaire_precedente": 0,
        "nombre_participation_pee": 0,
        "nb_formations_suivies": 0,
        "nombre_employee_sous_responsabilite": 1,
        "distance_domicile_travail": 28,
        "niveau_education": 3,
        "domaine_etude": "Infra & Cloud",
        "ayant_enfants": "Y",
        "frequence_deplacement": "Frequent",
        "annees_depuis_la_derniere_promotion": 0,
        "annes_sous_responsable_actuel": 0
    }


class TestHealthEndpoint:
    """Tests pour l'endpoint /health."""
    
    def test_health_returns_200(self):
        """Vérifie que /health retourne un status 200."""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_response_structure(self):
        """Vérifie la structure de la réponse."""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "model_loaded" in data
        assert "version" in data
        assert data["status"] == "healthy"


class TestRootEndpoint:
    """Tests pour l'endpoint racine."""
    
    def test_root_returns_200(self):
        """Vérifie que / retourne un status 200."""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_contains_docs_link(self):
        """Vérifie que la racine contient le lien vers docs."""
        response = client.get("/")
        data = response.json()
        assert "docs" in data


class TestPredictEndpoint:
    """Tests pour l'endpoint /predict."""
    
    def test_predict_returns_200_with_valid_data(self, valid_employee_stable):
        """Vérifie qu'une prédiction valide retourne 200."""
        response = client.post("/predict", json=valid_employee_stable)
        assert response.status_code == 200
        
    def test_predict_response_structure(self, valid_employee_stable):
        """Vérifie la structure de la réponse de prédiction."""
        response = client.post("/predict", json=valid_employee_stable)
        if response.status_code == 200:
            data = response.json()
            assert "prediction" in data
            assert "probability" in data
            assert "label" in data
            assert data["prediction"] in [0, 1]
            assert 0 <= data["probability"] <= 1
    
    def test_predict_stable_employee_low_risk(self, valid_employee_stable):
        """Vérifie qu'un employé stable a une faible probabilité de départ."""
        response = client.post("/predict", json=valid_employee_stable)
        if response.status_code == 200:
            data = response.json()
            # Un employé stable devrait avoir une probabilité < 50%
            assert data["probability"] < 0.5
    
    def test_predict_validates_age(self, valid_employee_stable):
        """Vérifie que l'âge invalide est rejeté."""
        invalid_employee = valid_employee_stable.copy()
        invalid_employee["age"] = 10  # Trop jeune (< 18)
        response = client.post("/predict", json=invalid_employee)
        assert response.status_code == 422  # Validation error
    
    def test_predict_validates_genre(self, valid_employee_stable):
        """Vérifie que le genre invalide est rejeté."""
        invalid_employee = valid_employee_stable.copy()
        invalid_employee["genre"] = "Homme"  # Doit être "M" ou "F"
        response = client.post("/predict", json=invalid_employee)
        assert response.status_code == 422
    
    def test_predict_validates_departement(self, valid_employee_stable):
        """Vérifie que le département invalide est rejeté."""
        invalid_employee = valid_employee_stable.copy()
        invalid_employee["departement"] = "IT"  # N'existe pas
        response = client.post("/predict", json=invalid_employee)
        assert response.status_code == 422
    
    def test_predict_validates_missing_field(self):
        """Vérifie qu'un champ manquant est rejeté."""
        incomplete_employee = {
            "age": 35,
            "genre": "M"
            # Champs manquants
        }
        response = client.post("/predict", json=incomplete_employee)
        assert response.status_code == 422


class TestBatchPredictEndpoint:
    """Tests pour l'endpoint /predict/batch."""
    
    def test_batch_predict_accepts_list(self, valid_employee_stable, valid_employee_at_risk):
        """Vérifie que le batch accepte une liste d'employés."""
        employees = {
            "employees": [valid_employee_stable, valid_employee_at_risk]
        }
        response = client.post("/predict/batch", json=employees)
        assert response.status_code == 200
    
    def test_batch_predict_response_structure(self, valid_employee_stable):
        """Vérifie la structure de la réponse batch."""
        employees = {"employees": [valid_employee_stable]}
        response = client.post("/predict/batch", json=employees)
        if response.status_code == 200:
            data = response.json()
            assert "predictions" in data
            assert "total" in data
            assert data["total"] == 1
            assert len(data["predictions"]) == 1
    
    def test_batch_predict_empty_list(self):
        """Vérifie le comportement avec une liste vide."""
        employees = {"employees": []}
        response = client.post("/predict/batch", json=employees)
        if response.status_code == 200:
            data = response.json()
            assert data["total"] == 0

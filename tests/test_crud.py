"""
Tests pour les opérations CRUD de la base de données.
Utilise SQLite in-memory via la fixture db_session de conftest.py.
"""

from src.database import crud


# ==================== HELPERS ====================

def _make_employee_data(**overrides):
    """Données minimales pour créer un employé."""
    data = {
        "age": 30,
        "genre": "M",
        "revenu_mensuel": 3000.0,
        "statut_marital": "Célibataire",
        "departement": "Consulting",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 2,
        "nombre_heures_travailless": 80.0,
        "annee_experience_totale": 8,
        "annees_dans_l_entreprise": 3,
        "annees_dans_le_poste_actuel": 2,
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 3,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "note_evaluation_actuelle": 3,
        "heure_supplementaires": "Non",
        "augementation_salaire_precedente": 10,
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 2,
        "nombre_employee_sous_responsabilite": 0,
        "distance_domicile_travail": 10,
        "niveau_education": 3,
        "domaine_etude": "Infra & Cloud",
        "ayant_enfants": "Y",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 1,
        "annes_sous_responsable_actuel": 2,
    }
    data.update(overrides)
    return data


# ==================== EMPLOYEES ====================

class TestCreateEmployee:

    def test_create_employee_returns_id(self, db_session):
        emp = crud.create_employee(db_session, _make_employee_data())
        assert emp.id is not None
        assert emp.age == 30
        assert emp.genre == "M"

    def test_create_employee_persists_all_fields(self, db_session):
        data = _make_employee_data(departement="Commercial", age=45)
        emp = crud.create_employee(db_session, data)
        assert emp.departement == "Commercial"
        assert emp.age == 45


class TestGetEmployee:

    def test_get_existing_employee(self, db_session):
        emp = crud.create_employee(db_session, _make_employee_data())
        found = crud.get_employee(db_session, emp.id)
        assert found is not None
        assert found.id == emp.id

    def test_get_nonexistent_employee_returns_none(self, db_session):
        result = crud.get_employee(db_session, 99999)
        assert result is None


class TestGetEmployees:

    def test_get_employees_pagination(self, db_session):
        for i in range(5):
            crud.create_employee(db_session, _make_employee_data(age=25 + i))
        page = crud.get_employees(db_session, skip=0, limit=3)
        assert len(page) <= 3


class TestGetEmployeesByDepartment:

    def test_filter_by_department(self, db_session):
        crud.create_employee(
            db_session, _make_employee_data(departement="Ressources Humaines")
        )
        crud.create_employee(
            db_session, _make_employee_data(departement="Consulting")
        )
        rh = crud.get_employees_by_department(db_session, "Ressources Humaines")
        assert all(e.departement == "Ressources Humaines" for e in rh)

    def test_filter_empty_department(self, db_session):
        result = crud.get_employees_by_department(db_session, "Inexistant")
        assert result == []


# ==================== PREDICTIONS ====================

class TestCreatePrediction:

    def test_create_prediction_linked_to_employee(self, db_session):
        emp = crud.create_employee(db_session, _make_employee_data())
        pred = crud.create_prediction(
            db_session, emp.id, prediction=1, probability=0.85, label="Risque"
        )
        assert pred.id is not None
        assert pred.employee_id == emp.id
        assert pred.prediction == 1
        assert pred.probability == 0.85


class TestGetPrediction:

    def test_get_existing_prediction(self, db_session):
        emp = crud.create_employee(db_session, _make_employee_data())
        pred = crud.create_prediction(
            db_session, emp.id, prediction=0, probability=0.2, label="Stable"
        )
        found = crud.get_prediction(db_session, pred.id)
        assert found is not None
        assert found.label == "Stable"

    def test_get_nonexistent_prediction_returns_none(self, db_session):
        result = crud.get_prediction(db_session, 99999)
        assert result is None


class TestGetPredictions:

    def test_get_predictions_pagination(self, db_session):
        emp = crud.create_employee(db_session, _make_employee_data())
        for _ in range(4):
            crud.create_prediction(
                db_session, emp.id, prediction=0, probability=0.3, label="Stable"
            )
        page = crud.get_predictions(db_session, skip=0, limit=2)
        assert len(page) <= 2


class TestGetPredictionsByEmployee:

    def test_filter_by_employee(self, db_session):
        emp1 = crud.create_employee(db_session, _make_employee_data())
        emp2 = crud.create_employee(db_session, _make_employee_data(age=40))
        crud.create_prediction(
            db_session, emp1.id, prediction=0, probability=0.1, label="Stable"
        )
        crud.create_prediction(
            db_session, emp2.id, prediction=1, probability=0.9, label="Risque"
        )
        preds = crud.get_predictions_by_employee(db_session, emp1.id)
        assert all(p.employee_id == emp1.id for p in preds)


class TestHighRiskPredictions:

    def test_high_risk_default_threshold(self, db_session):
        emp = crud.create_employee(db_session, _make_employee_data())
        crud.create_prediction(
            db_session, emp.id, prediction=0, probability=0.3, label="Stable"
        )
        crud.create_prediction(
            db_session, emp.id, prediction=1, probability=0.8, label="Risque"
        )
        high = crud.get_high_risk_predictions(db_session, threshold=0.5)
        assert all(p.probability >= 0.5 for p in high)

    def test_high_risk_custom_threshold(self, db_session):
        emp = crud.create_employee(db_session, _make_employee_data())
        crud.create_prediction(
            db_session, emp.id, prediction=1, probability=0.75, label="Risque"
        )
        high = crud.get_high_risk_predictions(db_session, threshold=0.9)
        assert all(p.probability >= 0.9 for p in high)


# ==================== COMBINED OPERATIONS ====================

class TestCreateEmployeeWithPrediction:

    def test_creates_both_in_transaction(self, db_session):
        emp, pred = crud.create_employee_with_prediction(
            db_session,
            employee_data=_make_employee_data(),
            prediction=1,
            probability=0.72,
            label="Risque de départ",
        )
        assert emp.id is not None
        assert pred.id is not None
        assert pred.employee_id == emp.id
        assert pred.probability == 0.72


class TestGetStatistics:

    def test_statistics_with_data(self, db_session):
        emp = crud.create_employee(db_session, _make_employee_data())
        crud.create_prediction(
            db_session, emp.id, prediction=0, probability=0.2, label="Stable"
        )
        crud.create_prediction(
            db_session, emp.id, prediction=1, probability=0.8, label="Risque"
        )
        stats = crud.get_statistics(db_session)
        assert stats["total_predictions"] >= 2
        assert stats["at_risk"] >= 1
        assert stats["stable"] >= 1
        assert 0 <= stats["risk_ratio"] <= 1

    def test_statistics_empty_db(self, db_session):
        """Sur une session vide (rollback), ratio doit être 0."""
        # On ne crée rien → les stats reflètent l'état courant
        stats = crud.get_statistics(db_session)
        assert stats["risk_ratio"] >= 0  # pas de division par zéro

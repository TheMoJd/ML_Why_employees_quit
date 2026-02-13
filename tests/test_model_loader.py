"""
Tests pour le module de chargement du modèle ML et le preprocessing.
"""

from unittest.mock import patch, MagicMock
from pathlib import Path

from src.api.model_loader import (
    preprocess_input,
    predict_single,
    predict_batch,
    is_model_loaded,
    load_model,
)
from src.api.router import get_label


# ==================== FIXTURES ====================

SAMPLE_INPUT = {
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
    "annes_sous_responsable_actuel": 3,
}


# ==================== PREPROCESS ====================

class TestPreprocessInput:

    def test_genre_encoding_male(self):
        df = preprocess_input({**SAMPLE_INPUT, "genre": "M"})
        assert df["genre"].iloc[0] == 1

    def test_genre_encoding_female(self):
        df = preprocess_input({**SAMPLE_INPUT, "genre": "F"})
        assert df["genre"].iloc[0] == 0

    def test_heures_sup_encoding_oui(self):
        df = preprocess_input({**SAMPLE_INPUT, "heure_supplementaires": "Oui"})
        assert df["heure_supplementaires"].iloc[0] == 1

    def test_heures_sup_encoding_non(self):
        df = preprocess_input({**SAMPLE_INPUT, "heure_supplementaires": "Non"})
        assert df["heure_supplementaires"].iloc[0] == 0

    def test_id_columns_dropped(self):
        df = preprocess_input(SAMPLE_INPUT)
        assert "id" not in df.columns
        assert "eval_number" not in df.columns

    def test_one_hot_creates_columns(self):
        df = preprocess_input(SAMPLE_INPUT)
        # Les colonnes catégorielles doivent être one-hot encodées
        # Il ne doit plus rester de colonnes de type object
        object_cols = df.select_dtypes(include=["object"]).columns.tolist()
        assert len(object_cols) == 0


# ==================== PREDICT ====================

class TestPredictSingle:

    def test_returns_tuple(self):
        pred, prob = predict_single(SAMPLE_INPUT)
        assert isinstance(pred, int)
        assert isinstance(prob, float)

    def test_prediction_binary(self):
        pred, _ = predict_single(SAMPLE_INPUT)
        assert pred in (0, 1)

    def test_probability_range(self):
        _, prob = predict_single(SAMPLE_INPUT)
        assert 0.0 <= prob <= 1.0


class TestPredictBatch:

    def test_returns_list_of_correct_size(self):
        inputs = [SAMPLE_INPUT, SAMPLE_INPUT]
        results = predict_batch(inputs)
        assert len(results) == 2

    def test_each_result_is_tuple(self):
        results = predict_batch([SAMPLE_INPUT])
        pred, prob = results[0]
        assert isinstance(pred, int)
        assert isinstance(prob, float)

    def test_empty_batch(self):
        results = predict_batch([])
        assert results == []


# ==================== MODEL LOADING ====================

class TestIsModelLoaded:

    def test_returns_true_when_model_exists(self):
        assert is_model_loaded() is True

    def test_returns_false_when_model_missing(self):
        with patch(
            "src.api.model_loader.MODEL_PATH",
            Path("/nonexistent/model.pkl"),
        ):
            load_model.cache_clear()
            assert is_model_loaded() is False
            load_model.cache_clear()


class TestLoadModelMissing:

    def test_raises_file_not_found(self):
        with patch(
            "src.api.model_loader.MODEL_PATH",
            Path("/nonexistent/model.pkl"),
        ):
            load_model.cache_clear()
            try:
                load_model()
                assert False, "Should have raised FileNotFoundError"
            except FileNotFoundError:
                pass
            finally:
                load_model.cache_clear()


# ==================== GET_LABEL ====================

class TestPredictSingleWithoutProba:

    def test_fallback_when_no_predict_proba(self):
        """Modèle sans predict_proba → probability = float(prediction)."""
        mock_model = MagicMock()
        mock_model.predict.return_value = [1]
        del mock_model.predict_proba  # simule l'absence de predict_proba
        mock_model.feature_names_in_ = load_model().feature_names_in_

        with patch("src.api.model_loader.load_model") as mock_load:
            mock_load.return_value = mock_model
            load_model.cache_clear()
            pred, prob = predict_single(SAMPLE_INPUT)
            assert pred == 1
            assert prob == 1.0
            load_model.cache_clear()


# ==================== GET_LABEL ====================

class TestGetLabel:

    def test_label_at_risk(self):
        assert get_label(1) == "Risque de départ"

    def test_label_stable(self):
        assert get_label(0) == "Stable"

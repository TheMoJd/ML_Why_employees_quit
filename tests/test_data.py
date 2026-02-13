import os
import pandas as pd
from src.data_processing import (
    clean_eval_id, load_data, process_and_merge, prepare_features,
)


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def test_load_data():
    """Vérifie que load_data charge les 3 CSV correctement."""
    df_sirh, df_eval, df_sondage = load_data(
        os.path.join(DATA_DIR, "extrait_sirh.csv"),
        os.path.join(DATA_DIR, "extrait_eval.csv"),
        os.path.join(DATA_DIR, "extrait_sondage.csv"),
    )
    assert len(df_sirh) > 0
    assert "id_employee" in df_sirh.columns
    assert len(df_eval) > 0
    assert "eval_number" in df_eval.columns
    assert len(df_sondage) > 0
    assert "code_sondage" in df_sondage.columns


def test_clean_eval_id():
    """Vérifie que E_1 devient bien 1"""
    input_series = pd.Series(['E_1', 'E_20', 'E_999'])
    expected = pd.Series([1, 20, 999])

    result = clean_eval_id(input_series)
    pd.testing.assert_series_equal(result, expected, check_names=False)


def test_clean_eval_id_already_numeric():
    """Si la series est déjà numérique, retourne tel quel."""
    input_series = pd.Series([1, 20, 999])
    result = clean_eval_id(input_series)
    pd.testing.assert_series_equal(result, input_series, check_names=False)


def test_process_and_merge():
    """Vérifie la fusion des dataframes (Test d'intégration simple)"""
    df_sirh = pd.DataFrame({'id_employee': [1, 2], 'col_A': ['A', 'B']})
    df_eval = pd.DataFrame({'eval_number': ['E_1', 'E_2'], 'col_B': [10, 20]})
    df_sondage = pd.DataFrame({
        'code_sondage': ['1', '2'], 'col_C': ['x', 'y']
    })

    result = process_and_merge(df_sirh, df_eval, df_sondage)

    assert len(result) == 2
    assert 'id' in result.columns
    assert result['id'].iloc[0] == 1


def test_process_and_merge_no_matching_ids():
    """IDs qui ne matchent pas → DataFrame vide après inner merge."""
    df_sirh = pd.DataFrame({'id_employee': [1, 2], 'col_A': ['A', 'B']})
    df_eval = pd.DataFrame({'eval_number': ['E_3', 'E_4'], 'col_B': [10, 20]})
    df_sondage = pd.DataFrame({
        'code_sondage': ['5', '6'], 'col_C': ['x', 'y']
    })

    result = process_and_merge(df_sirh, df_eval, df_sondage)
    assert len(result) == 0


def test_prepare_features_creates_x_y():
    """Vérifie que la séparation X et y fonctionne"""
    df = pd.DataFrame({
        'id': [1, 2],
        'a_quitte_l_entreprise': ['Oui', 'Non'],
        'genre': ['Homme', 'Femme'],
        'salaire': [2000, 3000],
        'eval_number': ['E_1', 'E_2']
    })

    X, y = prepare_features(df)

    assert 'id' not in X.columns
    assert 'a_quitte_l_entreprise' not in X.columns
    assert y.iloc[0] == 1  # Oui -> 1
    assert y.iloc[1] == 0  # Non -> 0
    assert X.shape[1] > 0


def test_prepare_features_without_target():
    """Sans colonne a_quitte_l_entreprise, y doit être None."""
    df = pd.DataFrame({
        'id': [1, 2],
        'genre': ['Homme', 'Femme'],
        'salaire': [2000, 3000],
    })

    X, y = prepare_features(df)
    assert y is None
    assert 'id' not in X.columns

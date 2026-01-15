import pandas as pd
import pytest
from src.data_processing import clean_eval_id, process_and_merge, prepare_features

def test_clean_eval_id():
    """Vérifie que E_1 devient bien 1"""
    input_series = pd.Series(['E_1', 'E_20', 'E_999'])
    expected = pd.Series([1, 20, 999])
    
    result = clean_eval_id(input_series)
    pd.testing.assert_series_equal(result, expected, check_names=False)

def test_process_and_merge():
    """Vérifie la fusion des dataframes (Test d'intégration simple)"""
    # Création de données "Mock" (Faux données)
    df_sirh = pd.DataFrame({'id_employee': [1, 2], 'col_A': ['A', 'B']})
    df_eval = pd.DataFrame({'eval_number': ['E_1', 'E_2'], 'col_B': [10, 20]})
    df_sondage = pd.DataFrame({'code_sondage': ['1', '2'], 'col_C': ['x', 'y']})
    
    result = process_and_merge(df_sirh, df_eval, df_sondage)
    
    # On s'attend à 2 lignes et 3 colonnes de données + 1 colonne ID
    assert len(result) == 2
    assert 'id' in result.columns
    assert result['id'].iloc[0] == 1

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
    
    # Vérifications
    assert 'id' not in X.columns
    assert 'a_quitte_l_entreprise' not in X.columns
    assert y.iloc[0] == 1  # Oui -> 1
    assert y.iloc[1] == 0  # Non -> 0
    assert X.shape[1] > 0  # Il doit rester des colonnes
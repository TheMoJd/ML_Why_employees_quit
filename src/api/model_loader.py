"""
Module de chargement du modèle ML.
Gère le chargement, le cache et la prédiction avec prétraitement.
"""

import os
import joblib
from pathlib import Path
from functools import lru_cache
import pandas as pd
import numpy as np

# Import des fonctions de prétraitement
try:
    from src.data_processing import prepare_features
except ImportError:
    from ..data_processing import prepare_features


# Chemin du modèle (relatif à la racine du projet)
MODEL_PATH = Path(__file__).parent.parent.parent / "model_hr.pkl"


@lru_cache(maxsize=1)
def load_model():
    """
    Charge le modèle depuis le fichier pickle.
    Utilise un cache LRU pour éviter de recharger le modèle.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modèle introuvable: {MODEL_PATH}")
    
    return joblib.load(MODEL_PATH)


def preprocess_input(input_data: dict) -> pd.DataFrame:
    """
    Prétraite les données d'entrée pour correspondre au format attendu par le modèle.
    Applique les mêmes transformations que lors de l'entraînement.
    """
    # Créer un DataFrame avec les données brutes
    df = pd.DataFrame([input_data])
    
    # Ajouter les colonnes ID fictives (nécessaires pour prepare_features)
    df['id'] = 0
    df['eval_number'] = 'E_0'
    
    # Pas de target lors de la prédiction
    # On doit reproduire les mêmes transformations que prepare_features
    df_proc = df.copy()
    
    # Encodage binaire pour genre et heure_supplementaires
    if 'genre' in df_proc.columns:
        df_proc['genre'] = (df_proc['genre'] == 'M').astype(int)
    if 'heure_supplementaires' in df_proc.columns:
        df_proc['heure_supplementaires'] = (df_proc['heure_supplementaires'] == 'Oui').astype(int)
    
    # One Hot Encoding pour les colonnes catégorielles restantes
    cols_to_drop = ['id', 'eval_number']
    cat_cols = df_proc.select_dtypes(include=['object']).columns.tolist()
    cat_cols = [c for c in cat_cols if c not in cols_to_drop]
    
    df_proc = pd.get_dummies(df_proc, columns=cat_cols, drop_first=True, dtype=int)
    
    # Supprimer les colonnes ID
    df_proc = df_proc.drop(columns=[c for c in cols_to_drop if c in df_proc.columns], errors='ignore')
    
    return df_proc


def predict_single(input_data: dict) -> tuple[int, float]:
    """
    Effectue une prédiction pour un seul employé.
    
    Args:
        input_data: Dictionnaire des features de l'employé
        
    Returns:
        Tuple (prediction, probability)
    """
    model = load_model()
    
    # Prétraitement des données
    df = preprocess_input(input_data)
    
    # Aligner les colonnes avec celles du modèle
    if hasattr(model, 'feature_names_in_'):
        model_features = model.feature_names_in_
        # Ajouter les colonnes manquantes avec des 0
        for col in model_features:
            if col not in df.columns:
                df[col] = 0
        # Réordonner les colonnes
        df = df[model_features]
    
    # Prédiction
    prediction = model.predict(df)[0]
    
    # Probabilité (si le modèle le supporte)
    try:
        probabilities = model.predict_proba(df)[0]
        probability = probabilities[1]  # Probabilité de la classe 1 (départ)
    except AttributeError:
        probability = float(prediction)
    
    return int(prediction), float(probability)


def predict_batch(inputs: list[dict]) -> list[tuple[int, float]]:
    """
    Effectue des prédictions pour plusieurs employés.
    
    Args:
        inputs: Liste de dictionnaires des features
        
    Returns:
        Liste de tuples (prediction, probability)
    """
    results = []
    for input_data in inputs:
        pred, prob = predict_single(input_data)
        results.append((pred, prob))
    
    return results


def is_model_loaded() -> bool:
    """Vérifie si le modèle est chargé et accessible."""
    try:
        load_model()
        return True
    except Exception:
        return False

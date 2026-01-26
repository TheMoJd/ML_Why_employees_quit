"""
Module de chargement du modèle ML.
Gère le chargement, le cache et la prédiction.
"""

import os
import joblib
from pathlib import Path
from functools import lru_cache
import pandas as pd
import numpy as np


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


def predict_single(input_data: dict) -> tuple[int, float]:
    """
    Effectue une prédiction pour un seul employé.
    
    Args:
        input_data: Dictionnaire des features de l'employé
        
    Returns:
        Tuple (prediction, probability)
    """
    model = load_model()
    
    # Conversion en DataFrame pour le modèle
    df = pd.DataFrame([input_data])
    
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
    model = load_model()
    
    df = pd.DataFrame(inputs)
    
    predictions = model.predict(df)
    
    try:
        probabilities = model.predict_proba(df)[:, 1]
    except AttributeError:
        probabilities = predictions.astype(float)
    
    return [(int(p), float(prob)) for p, prob in zip(predictions, probabilities)]


def is_model_loaded() -> bool:
    """Vérifie si le modèle est chargé et accessible."""
    try:
        load_model()
        return True
    except Exception:
        return False

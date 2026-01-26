"""
Schémas Pydantic pour la validation des données de l'API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class EmployeeInput(BaseModel):
    """
    Données d'entrée pour prédire le turnover d'un employé.
    Les champs correspondent aux features du modèle entraîné.
    """
    age: int = Field(..., ge=18, le=70, description="Âge de l'employé")
    genre: int = Field(..., ge=0, le=1, description="Genre (0=Femme, 1=Homme)")
    anciennete_mois: int = Field(..., ge=0, description="Ancienneté en mois")
    salaire_mensuel: float = Field(..., gt=0, description="Salaire mensuel")
    heure_supplementaires: int = Field(..., ge=0, le=1, description="Heures sup (0=Non, 1=Oui)")
    satisfaction_travail: int = Field(..., ge=1, le=5, description="Satisfaction au travail (1-5)")
    evaluation_derniere: float = Field(..., ge=0, le=5, description="Dernière évaluation")
    distance_domicile: int = Field(..., ge=0, description="Distance domicile-travail en km")
    nombre_projets: int = Field(..., ge=0, description="Nombre de projets")
    heures_mensuelles_moy: float = Field(..., ge=0, description="Heures mensuelles moyennes")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "age": 35,
                    "genre": 1,
                    "anciennete_mois": 48,
                    "salaire_mensuel": 3500.0,
                    "heure_supplementaires": 0,
                    "satisfaction_travail": 3,
                    "evaluation_derniere": 3.5,
                    "distance_domicile": 15,
                    "nombre_projets": 4,
                    "heures_mensuelles_moy": 160.0
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """Réponse de prédiction pour un employé."""
    prediction: int = Field(..., description="0=Reste, 1=Quitte")
    probability: float = Field(..., ge=0, le=1, description="Probabilité de départ")
    label: str = Field(..., description="Interprétation textuelle")
    

class BatchPredictionRequest(BaseModel):
    """Requête pour prédictions multiples."""
    employees: List[EmployeeInput]


class BatchPredictionResponse(BaseModel):
    """Réponse pour prédictions multiples."""
    predictions: List[PredictionResponse]
    total: int


class HealthResponse(BaseModel):
    """Réponse du endpoint santé."""
    status: str
    model_loaded: bool
    version: str

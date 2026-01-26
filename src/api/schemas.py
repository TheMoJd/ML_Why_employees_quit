"""
Schémas Pydantic pour la validation des données de l'API.
Basés sur les colonnes réelles des datasets SIRH, EVAL et SONDAGE.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class EmployeeInput(BaseModel):
    """
    Données d'entrée pour prédire le turnover d'un employé.
    Les champs correspondent aux colonnes réelles des datasets.
    """
    # === SIRH ===
    age: int = Field(..., ge=18, le=70, description="Âge de l'employé")
    genre: Literal["M", "F"] = Field(..., description="Genre: 'M' ou 'F'")
    revenu_mensuel: float = Field(..., gt=0, description="Revenu mensuel")
    statut_marital: Literal["Célibataire", "Marié(e)", "Divorcé(e)"] = Field(..., description="Statut marital")
    departement: Literal["Commercial", "Consulting", "Ressources Humaines"] = Field(..., description="Département")
    poste: Literal[
        "Cadre Commercial", "Assistant de Direction", "Consultant", "Manager",
        "Tech Lead", "Représentant Commercial", "Directeur Technique",
        "Senior Manager", "Ressources Humaines"
    ] = Field(..., description="Poste occupé")
    nombre_experiences_precedentes: int = Field(..., ge=0, description="Nombre d'expériences précédentes")
    nombre_heures_travailless: float = Field(..., ge=0, description="Nombre d'heures travaillées")
    annee_experience_totale: int = Field(..., ge=0, description="Années d'expérience totale")
    annees_dans_l_entreprise: int = Field(..., ge=0, description="Années dans l'entreprise")
    annees_dans_le_poste_actuel: int = Field(..., ge=0, description="Années dans le poste actuel")
    
    # === EVAL ===
    satisfaction_employee_environnement: int = Field(..., ge=1, le=5, description="Satisfaction environnement (1-5)")
    note_evaluation_precedente: int = Field(..., ge=1, le=5, description="Note évaluation précédente (1-5)")
    niveau_hierarchique_poste: int = Field(..., ge=1, le=5, description="Niveau hiérarchique (1-5)")
    satisfaction_employee_nature_travail: int = Field(..., ge=1, le=5, description="Satisfaction nature travail (1-5)")
    satisfaction_employee_equipe: int = Field(..., ge=1, le=5, description="Satisfaction équipe (1-5)")
    satisfaction_employee_equilibre_pro_perso: int = Field(..., ge=1, le=5, description="Satisfaction équilibre pro/perso (1-5)")
    note_evaluation_actuelle: int = Field(..., ge=1, le=5, description="Note évaluation actuelle (1-5)")
    heure_supplementaires: Literal["Oui", "Non"] = Field(..., description="Heures sup: 'Oui' ou 'Non'")
    augementation_salaire_precedente: int = Field(..., ge=0, le=100, description="Augmentation salaire précédente (%)")
    
    # === SONDAGE ===
    nombre_participation_pee: int = Field(..., ge=0, description="Nombre participations PEE")
    nb_formations_suivies: int = Field(..., ge=0, description="Nombre de formations suivies")
    nombre_employee_sous_responsabilite: int = Field(..., ge=0, description="Nombre d'employés sous responsabilité")
    distance_domicile_travail: int = Field(..., ge=0, description="Distance domicile-travail (km)")
    niveau_education: int = Field(..., ge=1, le=5, description="Niveau d'éducation (1-5)")
    domaine_etude: Literal[
        "Infra & Cloud", "Transformation Digitale", "Marketing", 
        "Autre", "Entrepreunariat", "Ressources Humaines"
    ] = Field(..., description="Domaine d'étude")
    ayant_enfants: Literal["Y"] = Field(..., description="A des enfants: 'Y'")
    frequence_deplacement: Literal["Occasionnel", "Frequent", "Aucun"] = Field(..., description="Fréquence de déplacement")
    annees_depuis_la_derniere_promotion: int = Field(..., ge=0, description="Années depuis dernière promotion")
    annes_sous_responsable_actuel: int = Field(..., ge=0, description="Années sous responsable actuel")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
                    "satisfaction_employee_environnement": 3,
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

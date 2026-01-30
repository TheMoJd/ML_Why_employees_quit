"""
Opérations CRUD pour la base de données HR Analytics.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from .models import Employee, Prediction


# ==================== EMPLOYEES ====================

def create_employee(db: Session, employee_data: dict) -> Employee:
    """Crée un nouvel employé dans la base de données."""
    db_employee = Employee(**employee_data)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    """Récupère un employé par son ID."""
    return db.query(Employee).filter(Employee.id == employee_id).first()


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Employee]:
    """Récupère une liste d'employés avec pagination."""
    return db.query(Employee).offset(skip).limit(limit).all()


def get_employees_by_department(db: Session, departement: str) -> List[Employee]:
    """Récupère les employés par département."""
    return db.query(Employee).filter(Employee.departement == departement).all()


# ==================== PREDICTIONS ====================

def create_prediction(
    db: Session, 
    employee_id: int, 
    prediction: int, 
    probability: float, 
    label: str,
    model_version: str = "1.0.0"
) -> Prediction:
    """Crée une nouvelle prédiction liée à un employé."""
    db_prediction = Prediction(
        employee_id=employee_id,
        prediction=prediction,
        probability=probability,
        label=label,
        model_version=model_version
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction


def get_prediction(db: Session, prediction_id: int) -> Optional[Prediction]:
    """Récupère une prédiction par son ID."""
    return db.query(Prediction).filter(Prediction.id == prediction_id).first()


def get_predictions(db: Session, skip: int = 0, limit: int = 100) -> List[Prediction]:
    """Récupère une liste de prédictions avec pagination."""
    return db.query(Prediction).order_by(Prediction.predicted_at.desc()).offset(skip).limit(limit).all()


def get_predictions_by_employee(db: Session, employee_id: int) -> List[Prediction]:
    """Récupère toutes les prédictions d'un employé."""
    return db.query(Prediction).filter(Prediction.employee_id == employee_id).all()


def get_high_risk_predictions(db: Session, threshold: float = 0.5) -> List[Prediction]:
    """Récupère les prédictions à haut risque (probabilité > seuil)."""
    return db.query(Prediction).filter(Prediction.probability >= threshold).all()


# ==================== COMBINED OPERATIONS ====================

def create_employee_with_prediction(
    db: Session,
    employee_data: dict,
    prediction: int,
    probability: float,
    label: str
) -> tuple:
    """Crée un employé et sa prédiction en une seule transaction."""
    # Créer l'employé
    db_employee = Employee(**employee_data)
    db.add(db_employee)
    db.flush()  # Pour obtenir l'ID sans commit
    
    # Créer la prédiction
    db_prediction = Prediction(
        employee_id=db_employee.id,
        prediction=prediction,
        probability=probability,
        label=label
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_employee)
    db.refresh(db_prediction)
    
    return db_employee, db_prediction


def get_statistics(db: Session) -> dict:
    """Retourne des statistiques sur les prédictions."""
    total = db.query(Prediction).count()
    at_risk = db.query(Prediction).filter(Prediction.prediction == 1).count()
    stable = db.query(Prediction).filter(Prediction.prediction == 0).count()
    
    return {
        "total_predictions": total,
        "at_risk": at_risk,
        "stable": stable,
        "risk_ratio": at_risk / total if total > 0 else 0
    }

"""
Modèles SQLAlchemy pour la base de données HR Analytics.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from .connection import Base


class Employee(Base):
    """Modèle pour stocker les données des employés analysés."""
    
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    genre = Column(String(1), nullable=False)
    revenu_mensuel = Column(Float, nullable=False)
    statut_marital = Column(String(50), nullable=False)
    departement = Column(String(100), nullable=False)
    poste = Column(String(100), nullable=False)
    nombre_experiences_precedentes = Column(Integer, default=0)
    annee_experience_totale = Column(Integer, default=0)
    annees_dans_l_entreprise = Column(Integer, default=0)
    annees_dans_le_poste_actuel = Column(Integer, default=0)
    satisfaction_employee_environnement = Column(Integer)
    satisfaction_employee_nature_travail = Column(Integer)
    satisfaction_employee_equipe = Column(Integer)
    satisfaction_employee_equilibre_pro_perso = Column(Integer)
    heure_supplementaires = Column(String(3))
    distance_domicile_travail = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation avec les prédictions
    predictions = relationship("Prediction", back_populates="employee", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('age >= 18 AND age <= 100', name='check_age'),
        CheckConstraint("genre IN ('M', 'F')", name='check_genre'),
    )


class Prediction(Base):
    """Modèle pour stocker l'historique des prédictions ML."""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"))
    prediction = Column(Integer, nullable=False)
    probability = Column(Float, nullable=False)
    label = Column(String(50), nullable=False)
    model_version = Column(String(20), default="1.0.0")
    predicted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relation inverse
    employee = relationship("Employee", back_populates="predictions")
    
    __table_args__ = (
        CheckConstraint('prediction IN (0, 1)', name='check_prediction'),
        CheckConstraint('probability >= 0 AND probability <= 1', name='check_probability'),
    )

"""
Configuration de la connexion à la base de données PostgreSQL.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# URL de connexion à PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://hr_admin:hr_password_2024@localhost:5432/hr_analytics"
)

# Création du moteur SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """
    Générateur de session de base de données.
    Utilisé comme dépendance FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Teste la connexion à la base de données."""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return False

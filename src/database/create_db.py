"""
Script de création et d'initialisation de la base de données.
Usage: python -m src.database.create_db
"""

import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.connection import engine, Base, test_connection
from src.database.models import Employee, Prediction


def create_tables():
    """Crée toutes les tables définies dans les modèles."""
    print("Création des tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès!")


def drop_tables():
    """Supprime toutes les tables (ATTENTION: perte de données)."""
    print("Suppression des tables...")
    Base.metadata.drop_all(bind=engine)
    print("Tables supprimées!")


def init_database():
    """Initialise la base de données."""
    print("=" * 50)
    print("Initialisation de la base de données HR Analytics")
    print("=" * 50)
    
    # Test de connexion
    print("\n1. Test de connexion à PostgreSQL...")
    if not test_connection():
        print("ERREUR: Impossible de se connecter à PostgreSQL.")
        print("Vérifiez que Docker/PostgreSQL est démarré.")
        sys.exit(1)
    print("Connexion réussie!")
    
    # Création des tables
    print("\n2. Création des tables...")
    create_tables()
    
    print("\n" + "=" * 50)
    print("Base de données initialisée avec succès!")
    print("=" * 50)


if __name__ == "__main__":
    init_database()

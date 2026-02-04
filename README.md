# HR Analytics - Prédiction du Turnover Employé

API de machine learning pour prédire le risque de départ des employés.

## 🚀 Fonctionnalités

- **API REST** avec FastAPI et documentation Swagger
- **Prédiction individuelle** et **batch** du turnover
- **Base de données PostgreSQL** pour l'historique des prédictions
- **Pipeline CI/CD** avec GitHub Actions
- **Tests unitaires** avec Pytest

---

## 📁 Structure du projet

```
Project4/
├── .github/workflows/     # Pipeline CI/CD
├── scripts/
│   └── init.sql           # Script SQL d'initialisation
├── src/
│   ├── api/               # API FastAPI
│   │   ├── main.py        # Point d'entrée
│   │   ├── router.py      # Endpoints de prédiction
│   │   ├── schemas.py     # Schémas Pydantic
│   │   └── model_loader.py
│   ├── database/          # Module base de données
│   │   ├── connection.py  # Connexion SQLAlchemy
│   │   ├── models.py      # Modèles ORM
│   │   ├── crud.py        # Opérations CRUD
│   │   └── create_db.py   # Script de création
│   ├── data_processing.py
│   └── train.py
├── tests/                 # Tests unitaires
├── docker-compose.yml     # Configuration PostgreSQL
├── pyproject.toml         # Dépendances
└── README.md
```

---

## 🗄️ Schéma de la Base de Données

```
┌─────────────────────────────────────────────────────────────┐
│                        EMPLOYEES                             │
├─────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                     │
│ age                   INTEGER NOT NULL                       │
│ genre                 VARCHAR(1) CHECK ('M','F')             │
│ revenu_mensuel        FLOAT NOT NULL                         │
│ statut_marital        VARCHAR(50)                            │
│ departement           VARCHAR(100)                           │
│ poste                 VARCHAR(100)                           │
│ satisfaction_*        INTEGER (1-4)                          │
│ heure_supplementaires VARCHAR(3) CHECK ('Oui','Non')         │
│ created_at            TIMESTAMP DEFAULT NOW()                │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       PREDICTIONS                            │
├─────────────────────────────────────────────────────────────┤
│ id                    SERIAL PRIMARY KEY                     │
│ employee_id           INTEGER FK → employees(id)             │
│ prediction            INTEGER CHECK (0,1)                    │
│ probability           FLOAT CHECK (0-1)                      │
│ label                 VARCHAR(50)                            │
│ model_version         VARCHAR(20) DEFAULT '1.0.0'            │
│ predicted_at          TIMESTAMP DEFAULT NOW()                │
└─────────────────────────────────────────────────────────────┘
```

### Relations
- **employees** → **predictions** : Un employé peut avoir plusieurs prédictions (1:N)

---

## 🛠️ Installation

### Prérequis
- Python 3.9+
- Docker Desktop
- Git

### 1. Cloner le repository
```bash
git clone <url-du-repo>
cd Project4
```

### 2. Créer et activer l'environnement virtuel
```bash
python -m venv env
.\env\Scripts\activate  # Windows
source env/bin/activate # Linux/Mac
```

### 3. Installer les dépendances
```bash
pip install -e .[dev]
```

### 4. Configurer les variables d'environnement
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

---

## 🐳 Base de données PostgreSQL

### Démarrer PostgreSQL avec Docker
```bash
docker-compose up -d
```

### Vérifier le conteneur
```bash
docker ps
```

### Arrêter PostgreSQL
```bash
docker-compose down
```

---

## ▶️ Lancer l'API

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est accessible sur : http://localhost:8000

### Documentation
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

---

## 🔌 Endpoints de l'API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Page d'accueil |
| GET | `/health` | Vérification de santé |
| POST | `/predict` | Prédiction individuelle |
| POST | `/predict/batch` | Prédictions multiples |

### Exemple de requête
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "genre": "M",
    "revenu_mensuel": 5000,
    "statut_marital": "Marié(e)",
    "departement": "Consulting",
    "poste": "Consultant",
    ...
  }'
```

---

## 🧪 Tests

### Lancer les tests
```bash
pytest tests/ -v
```

### Avec couverture de code
```bash
pytest tests/ -v --cov=src --cov-report=html
```

Le rapport HTML est généré dans `htmlcov/`.

---

## 🔒 Sécurité et Authentification

### Gestion des secrets

| Fichier | Description | Versionné |
|---------|-------------|-----------|
| `.env` | Variables d'environnement réelles | ❌ Non (dans .gitignore) |
| `.env.example` | Template sans valeurs sensibles | ✅ Oui |

**Variables sensibles à configurer :**
```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key  # Pour JWT (si implémenté)
```

### Mesures de sécurité implémentées

1. **Validation des entrées** : Pydantic valide toutes les données entrantes
   - Types stricts (int, float, str)
   - Contraintes de valeurs (age >= 18, genre in ['M', 'F'])
   - Énumérations pour les champs à valeurs fixes

2. **Protection CORS** : Configuré dans `main.py`
   ```python
   # Production : remplacer "*" par les domaines autorisés
   allow_origins=["https://yourdomain.com"]
   ```

3. **Base de données sécurisée**
   - Contraintes CHECK au niveau SQL
   - Requêtes paramétrées via SQLAlchemy (protection injection SQL)
   - Utilisateur PostgreSQL dédié avec permissions limitées

4. **Gestion des erreurs**
   - Messages d'erreur génériques en production
   - Pas d'exposition des stack traces

### Authentification (Recommandations pour la production)

L'API actuelle est un POC sans authentification. Pour la production, implémenter :

```python
# Exemple avec JWT (à ajouter dans src/api/auth.py)
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Valider le token JWT
    # Retourner l'utilisateur ou lever une exception
    pass
```

**Options d'authentification recommandées :**
- **JWT** : Pour les APIs stateless
- **OAuth2** : Pour l'intégration avec des providers externes
- **API Key** : Pour les intégrations machine-to-machine

### Secrets GitHub Actions (CI/CD)

Configurer dans : `Settings > Secrets and variables > Actions`

| Secret | Description |
|--------|-------------|
| `DATABASE_URL` | URL de connexion PostgreSQL |
| `POSTGRES_USER` | Utilisateur BDD |
| `POSTGRES_PASSWORD` | Mot de passe BDD |
| `POSTGRES_DB` | Nom de la base |

---

## 📦 Déploiement

### Variables d'environnement requises
```
DATABASE_URL=postgresql://user:password@host:5432/dbname
API_HOST=0.0.0.0
API_PORT=8000
```

### Docker (Production)
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔄 CI/CD

Le pipeline GitHub Actions exécute automatiquement :
1. **Linting** avec Flake8
2. **Tests unitaires** avec Pytest
3. **Entraînement du modèle** (sur main)

---

## 📝 Licence

MIT License

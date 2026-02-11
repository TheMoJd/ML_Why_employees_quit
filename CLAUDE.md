# CLAUDE.md - Contexte du Projet HR Analytics

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Description du Projet

Application de prédiction du turnover des employés (attrition) utilisant le Machine Learning. Le projet transforme un notebook d'analyse en une application de production avec API REST, base de données et CI/CD.

## Stack Technique

- **Backend**: FastAPI (Python 3.9+)
- **ML**: scikit-learn, imbalanced-learn (SMOTE), Logistic Regression
- **Base de données**: PostgreSQL + SQLAlchemy ORM
- **Conteneurisation**: Docker Compose
- **CI/CD**: GitHub Actions (3 jobs: test → build → deploy)
- **Tests**: pytest + pytest-cov (seuil: 60%)

## Structure du Projet

```
Project4/
├── src/
│   ├── api/
│   │   ├── main.py          # Point d'entrée FastAPI
│   │   ├── router.py        # Endpoints /predict et /predict/batch
│   │   ├── schemas.py       # Schémas Pydantic (validation)
│   │   └── model_loader.py  # Chargement et prédiction ML
│   ├── database/
│   │   ├── connection.py    # Connexion SQLAlchemy
│   │   ├── models.py        # Modèles ORM (Employee, Prediction)
│   │   └── crud.py          # Opérations CRUD
│   ├── data_processing.py   # Prétraitement des données
│   └── train.py             # Script d'entraînement du modèle
├── data/
│   ├── extrait_sirh.csv     # Données RH (âge, genre, salaire, etc.)
│   ├── extrait_eval.csv     # Données évaluations
│   └── extrait_sondage.csv  # Données sondages employés
├── tests/
│   ├── test_api.py          # Tests endpoints API
│   └── test_data.py         # Tests preprocessing
├── scripts/
│   └── init.sql             # Initialisation PostgreSQL
├── .github/workflows/
│   └── ci_cd.yml            # Pipeline CI/CD
├── model_hr.pkl             # Modèle ML entraîné (ignoré par git)
├── docker-compose.yml       # PostgreSQL container
├── Dockerfile               # Image Docker pour déploiement
├── .dockerignore            # Exclusions Docker build
├── render.yaml              # Blueprint Render.com (déploiement)
├── runtime.txt              # Version Python pour Render (3.9.18)
├── pyproject.toml           # Config projet + dépendances
└── .env                     # Variables d'environnement (ignoré)
```

## Patterns d'Architecture

Le projet utilise plusieurs patterns établis pour maintenir la cohérence et la qualité du code:

- **Injection de Dépendances**: FastAPI `Depends()` pour les sessions de base de données
  - Exemple: `def predict(employee: EmployeeInput, db: Session = Depends(get_db))`

- **LRU Caching**: Le modèle ML est chargé une seule fois via `@lru_cache` dans [model_loader.py](src/api/model_loader.py)
  - Évite les rechargements coûteux à chaque prédiction

- **Gestion Transactionnelle**: Commit/rollback explicites dans [crud.py](src/database/crud.py)
  - `db.flush()` puis `db.refresh()` pour récupérer les IDs générés

- **Alignement des Features**: Mapping automatique des features au moment de la prédiction
  - Prévient le feature drift entre entraînement et production
  - Utilise `model.feature_names_in_` pour vérifier la cohérence

- **Type Safety**: Annotations de types Python 3.9+ partout
  - Pydantic pour la validation runtime
  - mypy pour la vérification statique (optionnelle)

- **Conversion de Types pour Merge**: Les 3 CSV sources ont des formats d'ID différents
  - SIRH: `id_employee` (peut être str ou int selon la version de pandas)
  - EVAL: `eval_number` format `E_1` → converti en int via `clean_eval_id()`
  - SONDAGE: `code_sondage` → converti en Int64 via `pd.to_numeric()`
  - Tous les IDs sont normalisés en Int64 avant le merge dans [data_processing.py](src/data_processing.py)

## Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Info API + lien docs |
| GET | `/health` | Santé de l'API + statut modèle |
| POST | `/predict` | Prédiction pour 1 employé |
| POST | `/predict/batch` | Prédictions multiples |

## Sécurité et Production

### Mesures Implémentées

1. **Validation des Entrées (Pydantic)**
   - Types stricts (int, float, str)
   - Contraintes: `age >= 18`, `genre in ['M', 'F']`, `satisfaction 1-5`
   - Énumérations pour champs à valeurs fixes

2. **Protection CORS** (configuré dans [main.py](src/api/main.py))
   ```python
   # Développement: permet tous les domaines
   allow_origins=["*"]

   # Production: restreindre aux domaines autorisés
   # allow_origins=["https://yourdomain.com"]
   ```

3. **Protection SQL**
   - SQLAlchemy ORM avec requêtes paramétrées
   - Prévient les injections SQL
   - Contraintes CHECK au niveau base de données

4. **Gestion des Secrets**
   - `.env` exclu de git (.gitignore)
   - GitHub Secrets pour CI/CD
   - Pas de credentials hardcodés

### Recommandations pour Production

- **Authentification**: Implémenter JWT ou OAuth2
- **HTTPS**: Obligatoire pour les déploiements
- **Rate Limiting**: Limiter les requêtes par IP/utilisateur
- **Monitoring**: Logs et métriques (à implémenter)

## Schéma des Données Employé

Les données proviennent de 3 sources fusionnées:

### SIRH (11 champs)
- `age`, `genre`, `revenu_mensuel`, `statut_marital`
- `departement`, `poste`, `nombre_experiences_precedentes`
- `nombre_heures_travailless`, `annee_experience_totale`
- `annees_dans_l_entreprise`, `annees_dans_le_poste_actuel`

### EVAL (9 champs)
- `satisfaction_employee_environnement` (1-5)
- `note_evaluation_precedente`, `note_evaluation_actuelle`
- `niveau_hierarchique_poste`, `satisfaction_employee_nature_travail`
- `satisfaction_employee_equipe`, `satisfaction_employee_equilibre_pro_perso`
- `heure_supplementaires` ("Oui"/"Non")
- `augementation_salaire_precedente`

### SONDAGE (10 champs)
- `nombre_participation_pee`, `nb_formations_suivies`
- `nombre_employee_sous_responsabilite`, `distance_domicile_travail`
- `niveau_education`, `domaine_etude`, `ayant_enfants`
- `frequence_deplacement`, `annees_depuis_la_derniere_promotion`
- `annes_sous_responsable_actuel`

### Structure de la Base de Données

```
┌─────────────────────────────────────────────┐
│              EMPLOYEES                      │
├─────────────────────────────────────────────┤
│ id (PK)              SERIAL                 │
│ age                  INTEGER (18-100)       │
│ genre                VARCHAR(1) ∈ {M,F}     │
│ revenu_mensuel       FLOAT                  │
│ + 27 autres champs (SIRH, EVAL, SONDAGE)   │
│ created_at           TIMESTAMP              │
└──────────────┬──────────────────────────────┘
               │ 1:N
               ▼
┌─────────────────────────────────────────────┐
│             PREDICTIONS                     │
├─────────────────────────────────────────────┤
│ id (PK)              SERIAL                 │
│ employee_id (FK)     → employees.id         │
│ prediction           INTEGER ∈ {0,1}        │
│ probability          FLOAT [0-1]            │
│ label                VARCHAR(50)            │
│ model_version        VARCHAR(20)            │
│ predicted_at         TIMESTAMP              │
└─────────────────────────────────────────────┘
```

**Indexes**:
- `idx_predictions_employee_id`: Requêtes par employé
- `idx_predictions_predicted_at`: Tri chronologique
- `idx_employees_departement`: Filtrage par département

**Vue**: `v_employee_predictions` (données dénormalisées pour analytics)

## Commandes Utiles

### Workflow de Développement Complet

```bash
# 1. Démarrer PostgreSQL
docker-compose up -d

# 2. Entraîner le modèle (REQUIS avant les tests et l'API)
python src/train.py

# 3. Lancer l'API en mode développement
uvicorn src.api.main:app --reload

# 4. Exécuter les tests
pytest tests/ -v --cov=src

# 5. Rapport de couverture HTML (ouvreur htmlcov/index.html)
pytest tests/ -v --cov=src --cov-report=html

# 6. Vérifier le seuil de couverture (60% minimum)
pytest tests/ --cov=src --cov-fail-under=60
```

### Commandes Individuelles

```bash
# Linting
flake8 src tests

# Linting strict (comme dans CI/CD)
flake8 src tests --max-complexity=10 --max-line-length=127

# Docker: vérifier le statut
docker ps

# Docker: arrêter PostgreSQL
docker-compose down

# Tests d'un fichier spécifique
pytest tests/test_api.py -v

# Tests avec fixtures
# - valid_employee_stable: Employé à faible risque
# - valid_employee_at_risk: Employé à haut risque
```

## Variables d'Environnement

### Configuration Locale

Copier `.env.example` vers `.env`:
```bash
# Base de données (Docker Compose)
DATABASE_URL=postgresql://hr_admin:hr_password_2024@localhost:5432/hr_analytics
POSTGRES_USER=hr_admin
POSTGRES_PASSWORD=hr_password_2024
POSTGRES_DB=hr_analytics

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Secrets GitHub (pour CI/CD)

Configurer dans `Settings > Secrets and variables > Actions`:
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DATABASE_URL`

### Fichiers Importants

- **Modèle**: `model_hr.pkl` (généré par `src/train.py`, ignoré par git)
- **Données**: `data/*.csv` (3 fichiers sources)
- **Tests**: SQLite in-memory (pas besoin de PostgreSQL pour les tests)

## CI/CD Pipeline

### Workflow GitHub Actions (3 Jobs)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    TEST     │───▶│    BUILD    │───▶│   DEPLOY    │
│  (toutes)   │    │   (main)    │    │ (main push) │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Job 1: Test (toutes branches)

- **Environment**: `test`
- **Étapes**:
  1. Checkout code
  2. Setup Python 3.9 avec pip cache
  3. Install dependencies (`pip install -e .[dev]`)
  4. **Lint**: flake8 (max-complexity=10, max-line-length=127)
  5. **Train Model**: `python src/train.py`
  6. **Tests**: `pytest --cov=src --cov-fail-under=60`
  7. Upload coverage report (artifact: `coverage-report`)

### Job 2: Build (main uniquement)

- **Environment**: `staging`
- **Condition**: `github.ref == 'refs/heads/main'`
- **Étapes**:
  1. Train model
  2. Upload artifact: `trained-model` (model_hr.pkl)

### Job 3: Deploy (main + push)

- **Environment**: `production`
- **Condition**: `main` branch + push event
- **Étapes**:
  1. Download model artifact
  2. Deploy (placeholder pour Heroku/AWS/Azure)

### Stratégie de Branches

- **develop**: Job test uniquement (pas de build/deploy)
- **main**: Pipeline complet (test → build → deploy)
- **pull_request**: Job test uniquement

### Quality Gates

- ✅ Lint: flake8 doit passer (erreurs E9, F63, F7, F82 bloquantes)
- ✅ Tests: Tous les tests doivent passer
- ✅ Coverage: Minimum 60% requis
- ✅ Model: Entraînement réussi avant les tests

### Isolation des Tests

- Tests utilisent SQLite in-memory (pas PostgreSQL)
- Fixtures: `valid_employee_stable`, `valid_employee_at_risk`
- Configuration dans [conftest.py](tests/conftest.py)

## Déploiement (Render.com)

### Configuration

- **Blueprint**: [render.yaml](render.yaml) définit le service web + base PostgreSQL
- **Python Version**: Spécifiée dans [runtime.txt](runtime.txt) (`python-3.9.18`)
- **Build**: `pip install -e . && python src/train.py` (installe les dépendances et entraîne le modèle)
- **Start**: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

### Architecture Render

```
┌─────────────────────┐     ┌─────────────────────┐
│  hr-analytics-api   │────▶│  hr-analytics-db    │
│  (Web Service)      │     │  (PostgreSQL)       │
│  Python 3.9.18      │     │  Plan: Free         │
│  Plan: Free         │     └─────────────────────┘
└─────────────────────┘
```

### Alternative Docker

Un [Dockerfile](Dockerfile) est aussi disponible pour un déploiement conteneurisé sur n'importe quelle plateforme.

## Améliorations Futures

Roadmap des fonctionnalités planifiées pour la production:

### Sécurité & Authentification
- **JWT/OAuth2**: Authentification des utilisateurs
- **Rate Limiting**: Limitation des requêtes par IP
- **HTTPS**: Déploiement avec certificats SSL/TLS

### Infrastructure
- **Docker Multi-Service**: Docker Compose pour API + PostgreSQL ensemble
- **Cloud Deployment**: AWS ECS, Azure App Service, ou GCP Cloud Run
- **Load Balancing**: Distribution de charge pour haute disponibilité

### Monitoring & Observabilité
- **Logging**: Centralisation des logs (Elasticsearch, CloudWatch)
- **Métriques**: Prometheus + Grafana
- **Alerting**: Notifications sur erreurs critiques

### ML Operations
- **Model Versioning**: Tracking des versions de modèle en base
- **A/B Testing**: Comparaison de plusieurs modèles en production
- **Retraining Pipeline**: Automatisation du réentraînement périodique

### Interface Utilisateur
- **Dashboard RH**: Interface web pour les managers
- **Visualisations**: Graphiques de prédictions par département
- **Export**: Rapports CSV/Excel

## Notes Importantes

- Le fichier `model_hr.pkl` est ignoré par git (*.pkl dans .gitignore)
- Le modèle est entraîné dans le CI avant les tests
- Les fichiers `enonce.md` et `enoncé.txt` contiennent les consignes (ignorés)
- Couverture de tests minimum: 60%

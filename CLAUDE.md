# CLAUDE.md - Contexte du Projet HR Analytics

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
├── pyproject.toml           # Config projet + dépendances
└── .env                     # Variables d'environnement (ignoré)
```

## Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Info API + lien docs |
| GET | `/health` | Santé de l'API + statut modèle |
| POST | `/predict` | Prédiction pour 1 employé |
| POST | `/predict/batch` | Prédictions multiples |

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

## Commandes Utiles

```bash
# Démarrer PostgreSQL
docker-compose up -d

# Entraîner le modèle
python src/train.py

# Lancer l'API
uvicorn src.api.main:app --reload

# Exécuter les tests
pytest tests/ -v --cov=src

# Linting
flake8 src tests
```

## Variables d'Environnement

Copier `.env.example` vers `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/hr_analytics
API_HOST=0.0.0.0
API_PORT=8000
```

## CI/CD Pipeline

1. **test**: Lint + Train Model + Tests (toutes branches)
2. **build**: Entraînement modèle + artifact (main uniquement)
3. **deploy**: Déploiement production (main + push uniquement)

Les secrets sont dans GitHub Settings > Secrets:
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DATABASE_URL`

## Notes Importantes

- Le fichier `model_hr.pkl` est ignoré par git (*.pkl dans .gitignore)
- Le modèle est entraîné dans le CI avant les tests
- Les fichiers `enonce.md` et `enoncé.txt` contiennent les consignes (ignorés)
- Couverture de tests minimum: 60%

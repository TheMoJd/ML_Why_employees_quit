# Support de Présentation - HR Analytics API
## Plan pour la soutenance auprès d'Aurélien (Futurisys)

---

## Slide 1: Page de titre
**HR Analytics - API de Prédiction du Turnover**
- Projet OpenClassrooms P4
- Votre nom
- Date

---

## Slide 2: Contexte et Objectifs
**Problématique**
- Anticiper le départ des employés pour réduire le turnover
- Rendre un modèle ML accessible en production

**Objectifs du POC**
- API REST performante et documentée
- Tests automatisés et CI/CD
- Base de données pour l'historique des prédictions

---

## Slide 3: Architecture Technique
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  FastAPI    │────▶│ PostgreSQL  │
│  (Swagger)  │     │    API      │     │     BDD     │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
                   ┌──────▼──────┐
                   │   Modèle    │
                   │     ML      │
                   └─────────────┘
```

**Stack technique**
- Python 3.9 + FastAPI
- PostgreSQL 15 + SQLAlchemy
- Docker Compose
- GitHub Actions (CI/CD)

---

## Slide 4: Structure du Projet
```
Project4/
├── src/
│   ├── api/           # Endpoints FastAPI
│   ├── database/      # ORM et CRUD
│   └── train.py       # Entraînement du modèle
├── tests/             # Tests Pytest
├── scripts/           # SQL d'initialisation
├── .github/workflows/ # Pipeline CI/CD
└── docker-compose.yml
```

---

## Slide 5: Démonstration de l'API
**Endpoints disponibles**

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Prédiction individuelle |
| POST | `/predict/batch` | Prédictions multiples |

**Démo live**
- Swagger UI : http://localhost:8000/docs
- Exemple de requête POST /predict
- Résultat : prediction (0/1), probability, label

---

## Slide 6: Base de Données
**Schéma relationnel**

```
EMPLOYEES (1) ────── (N) PREDICTIONS
```

**Tables**
- `employees` : Données RH de l'employé
- `predictions` : Historique des prédictions

**Avantages**
- Traçabilité des prédictions
- Analyse de la performance du modèle
- Audit possible

---

## Slide 7: Tests et Qualité du Code
**Couverture de tests**
- Tests unitaires avec Pytest
- Tests de validation des entrées
- Tests des scénarios d'erreur

**Types de tests**
- `/health` : Status et structure de réponse
- `/predict` : Validation Pydantic, prédictions
- `/predict/batch` : Traitement multiple

**Commande** : `pytest tests/ -v --cov=src`

---

## Slide 8: Pipeline CI/CD
**3 étapes automatisées**

```
┌─────────┐    ┌─────────┐    ┌─────────┐
│  TEST   │───▶│  BUILD  │───▶│ DEPLOY  │
│         │    │         │    │         │
│ Lint    │    │ Train   │    │ Prod    │
│ Pytest  │    │ Model   │    │ Release │
│ Coverage│    │         │    │         │
└─────────┘    └─────────┘    └─────────┘
```

**Fonctionnalités**
- Linting avec Flake8
- Tests avec couverture (>70%)
- Gestion des secrets GitHub
- Environnements : test, staging, production

---

## Slide 9: Sécurité
**Mesures implémentées**
1. Validation des entrées (Pydantic)
2. Protection CORS configurée
3. Requêtes SQL paramétrées (pas d'injection)
4. Secrets dans `.env` (non versionné)
5. GitHub Secrets pour CI/CD

**Recommandations production**
- Authentification JWT/OAuth2
- HTTPS obligatoire
- Rate limiting

---

## Slide 10: Gestion de Version Git
**Bonnes pratiques appliquées**

- Commits descriptifs et atomiques
- Branches feature pour les développements
- Tags pour les releases (`v1.0.0`)
- `.gitignore` configuré (pas de secrets)

**Historique**
```
v1.0.0 ← tag release
│
├── feat: CI/CD improvements
├── bdd: database setup
├── fastapi api V1
└── initial commit
```

---

## Slide 11: Points forts du POC
- API RESTful avec documentation Swagger automatique
- Validation robuste des données entrantes
- Pipeline CI/CD complet et automatisé
- Tests avec couverture de code
- Architecture modulaire et maintenable
- Gestion sécurisée des secrets

---

## Slide 12: Améliorations futures
**Court terme**
- Authentification JWT
- Monitoring et logging
- Conteneurisation complète (Dockerfile API)

**Moyen terme**
- Déploiement cloud (AWS/Azure/GCP)
- A/B testing des modèles
- Dashboard de monitoring

---

## Slide 13: Questions / Discussion
**Merci pour votre attention**

- Dépôt : [URL GitHub]
- Documentation : `/docs` (Swagger)
- Contact : [votre email]

---

## Notes pour la présentation

### Durée suggérée
- Introduction : 2 min
- Architecture : 3 min
- Démo live : 5 min
- CI/CD et tests : 3 min
- Sécurité : 2 min
- Questions : 5-10 min

### Points à préparer
1. Avoir Docker lancé pour la démo
2. Préparer des exemples de requêtes dans Postman/curl
3. Montrer le pipeline GitHub Actions en action
4. Préparer des réponses sur les choix techniques

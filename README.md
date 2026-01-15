# Project4 - Prédiction du Turnover Employé

## Description

Ce projet a pour objectif de prédire le turnover des employés à partir de données RH en utilisant un modèle de régression logistique avec un pipeline sklearn.

## Structure du projet

```
Project4/
├── .github/workflows/    # CI/CD GitHub Actions
├── src/                  # Code source
│   ├── data_processing.py
│   └── train.py
├── tests/                # Tests unitaires
├── pyproject.toml        # Configuration du projet
└── README.md
```

## Installation

```bash
# Cloner le repository
git clone <url-du-repo>
cd Project4

# Installer le package en mode développement
pip install -e .[dev]
```

## Tests

```bash
pytest tests/ -v
```

## CI/CD

Le projet utilise GitHub Actions pour :
- Exécuter les tests automatiquement à chaque push/pull request
- Valider la qualité du code

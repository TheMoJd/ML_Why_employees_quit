# Plan : Frontend Production-Quality pour HR Analytics

## Contexte

L'application HR Analytics est actuellement une API backend uniquement (FastAPI). Aucun frontend n'existe. L'objectif est de créer un frontend esthétique de niveau production, digne d'une application SaaS à succès mondial (style Linear, Stripe, Vercel).

Le frontend sera servi directement par FastAPI via `StaticFiles`, déployé sur le même service Render.com, sans framework JS ni étape de build.

---

## Fichiers à créer

| Fichier | Description |
|---------|-------------|
| `static/index.html` | Page HTML unique (SPA) |
| `static/css/style.css` | Styles complets (design system, composants, responsive, dark/light) |
| `static/js/app.js` | Logique applicative (formulaire multi-étapes, API, validation, résultats) |

## Fichiers à modifier

| Fichier | Modification |
|---------|-------------|
| `src/api/main.py` | Ajouter StaticFiles mount + FileResponse pour `/` + endpoint `/api/info` |
| `Dockerfile` | Ajouter `COPY static ./static` |

---

## 1. Modifications Backend (`src/api/main.py`)

### Imports à ajouter
```python
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
```

### Mount StaticFiles (après `app.include_router`)
```python
static_dir = Path(__file__).parent.parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
```

### Modifier GET `/` (servir HTML si disponible, sinon JSON fallback)
```python
@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    index_path = Path(__file__).parent.parent.parent / "static" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return {"message": "HR Turnover Prediction API", "docs": "/docs", "health": "/health"}
```

**Compatibilité tests** : En CI/test, `static/` n'existe pas → fallback JSON → les tests existants (`test_root_contains_docs_link` qui appelle `response.json()`) continuent de passer sans modification.

### Ajouter GET `/api/info`
```python
@app.get("/api/info", tags=["Root"])
async def api_info():
    return {"message": "HR Turnover Prediction API", "docs": "/docs", "health": "/health", "version": "1.0.0"}
```

---

## 2. Dockerfile

Ajouter après `COPY data ./data` (ligne 15) :
```dockerfile
COPY static ./static
```

Note : `.dockerignore` n'exclut pas `static/` donc aucun changement nécessaire.

---

## 3. Design System CSS

### Palette
- **Accent principal** : `#6366f1` (indigo) — actions, focus, liens
- **Succès** : `#10b981` (vert) — employé stable
- **Danger** : `#ef4444` (rouge) — risque de départ
- **Warning** : `#f59e0b` (ambre) — risque modéré
- **Fond light** : `#ffffff` / `#f8f9fb` / `#f0f2f5`
- **Fond dark** : `#0f1117` / `#161822` / `#1e2130`

### Fonctionnalités visuelles
- Dark/light mode via `[data-theme]` + CSS custom properties
- Glass-morphism en dark mode (`backdrop-filter: blur`)
- Animations fluides (fade-in, slide, gauge arc, spinner)
- Responsive (mobile < 640px)
- Police système (pas de dépendance externe)

---

## 4. Architecture JavaScript (IIFE)

### Structure
```
IIFE {
  CONFIG      - endpoints, étapes, valeurs par défaut
  state       - currentStep, formData, prediction, isLoading, theme
  api         - checkHealth(), predict(data)
  FIELDS      - définition déclarative des 30 champs (nom, type, contraintes, options)
  form        - rendu dynamique, collecte de valeurs
  stepper     - navigation 4 étapes, validation avant avancement
  validation  - miroir des contraintes Pydantic
  result      - jauge SVG semicirculaire, badge risque, interprétation
  theme       - localStorage, prefers-color-scheme, toggle
  init()      - démarrage
}
```

### Formulaire multi-étapes (4 étapes)

| Étape | ID | Contenu | Champs |
|-------|----|---------|--------|
| 1 | sirh | Profil RH | 11 champs (age, genre, revenu, département, poste, etc.) |
| 2 | eval | Évaluations | 9 champs (satisfactions 1-5, heures sup, augmentation) |
| 3 | sondage | Sondage | 10 champs (formations, distance, éducation, etc.) |
| 4 | review | Confirmation | Résumé en lecture seule des 30 champs + bouton Analyser |

### Types d'inputs spécifiques
- **Champs 1-5** : composant rating cliquable (dots numérotés) au lieu de dropdowns
- **Heures supplémentaires** : toggle switch (Oui/Non)
- **Augmentation salaire** : slider 0-100%
- **ayant_enfants** : champ caché (toujours "Y", contrainte Pydantic `Literal["Y"]`)
- **Selects** : dropdowns stylisés pour département, poste, statut_marital, domaine_etude, frequence_deplacement

### Valeurs par défaut
Issues de la fixture `valid_employee_stable` dans `tests/test_api.py` (lignes 18-49) :
```json
{
  "age": 35, "genre": "M", "revenu_mensuel": 5000,
  "statut_marital": "Marié(e)", "departement": "Consulting",
  "poste": "Consultant", "nombre_experiences_precedentes": 2,
  "nombre_heures_travailless": 80, "annee_experience_totale": 10,
  "annees_dans_l_entreprise": 5, "annees_dans_le_poste_actuel": 3,
  "satisfaction_employee_environnement": 4, "note_evaluation_precedente": 3,
  "niveau_hierarchique_poste": 2, "satisfaction_employee_nature_travail": 4,
  "satisfaction_employee_equipe": 4, "satisfaction_employee_equilibre_pro_perso": 3,
  "note_evaluation_actuelle": 3, "heure_supplementaires": "Non",
  "augementation_salaire_precedente": 15, "nombre_participation_pee": 1,
  "nb_formations_suivies": 3, "nombre_employee_sous_responsabilite": 1,
  "distance_domicile_travail": 10, "niveau_education": 3,
  "domaine_etude": "Transformation Digitale", "ayant_enfants": "Y",
  "frequence_deplacement": "Occasionnel", "annees_depuis_la_derniere_promotion": 2,
  "annes_sous_responsable_actuel": 3
}
```

---

## 5. Flux de l'application

```
LANDING (hero + bouton "Commencer l'analyse")
   |
   v
FORM Step 1 (SIRH) → Step 2 (EVAL) → Step 3 (SONDAGE) → Step 4 (REVIEW)
                                                               |
                                                          [Analyser]
                                                               |
                                                               v
                                                        POST /predict
                                                               |
                                                               v
                                                          RÉSULTAT
                                                     (jauge + badge + texte)
                                                               |
                                                     [Nouvelle analyse] → FORM Step 1
```

---

## 6. Visualisation du résultat

### Jauge SVG semicirculaire
- Arc SVG animé de 0% à la probabilité cible
- Couleur dynamique : vert (< 30%), ambre (30-60%), rouge (> 60%)
- Texte central : pourcentage (ex: "23.4%")

### Badge de risque
- Vert "Stable" / Ambre "Risque modéré" / Rouge "Risque de départ"
- Pastille pulsante colorée

### Texte d'interprétation
5 niveaux de messages contextuels selon la probabilité :
- < 20% : risque très faible
- 20-40% : risque faible
- 40-60% : risque modéré
- 60-80% : risque élevé
- > 80% : risque critique

---

## 7. Header avec health status

Au chargement, appel GET `/health`. Badge dans le header :
- Pastille verte pulsante + "Système opérationnel"
- Pastille rouge + "Modèle non chargé" si erreur

---

## 8. Anti-flash dark mode

Script inline dans `<head>` (avant le CSS) pour lire `localStorage` et appliquer `data-theme` immédiatement, évitant le flash blanc.

---

## 9. Points d'attention

1. **Noms de champs exacts** : le frontend doit envoyer les noms de `src/api/schemas.py` exactement (ex: `nombre_heures_travailless` avec double 's', `annes_sous_responsable_actuel`)
2. **Valeurs Literal exactes** : "Marié(e)", "Célibataire", "Divorcé(e)", "Oui"/"Non" — doivent être envoyées avec les accents/caractères spéciaux exacts
3. **`ayant_enfants`** : toujours `"Y"` (Literal contraint) → champ caché
4. **Encodage** : `Content-Type: application/json` avec `JSON.stringify()` gère l'UTF-8 nativement

---

## Vérification

1. S'assurer que `model_hr.pkl` existe (`python src/train.py` si besoin)
2. Lancer l'API : `uvicorn src.api.main:app --reload`
3. Ouvrir `http://localhost:8000/` → doit afficher le frontend
4. Vérifier `/docs` → Swagger toujours accessible
5. Vérifier `/health` → retourne toujours du JSON
6. Parcourir le formulaire complet (4 étapes) et soumettre
7. Vérifier la jauge de résultat et le badge de risque
8. Tester le toggle dark/light mode
9. Tester en viewport mobile (responsive)
10. Exécuter les tests existants : `pytest tests/ -v --cov=src` (doivent tous passer)

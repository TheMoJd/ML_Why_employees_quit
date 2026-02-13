# Tests ajoutés — HR Analytics

## Vue d'ensemble

| Métrique | Avant | Après |
|----------|-------|-------|
| Nombre de tests | 15 | 67 |
| Couverture totale | ~60% | 80.3% |
| Fichiers de tests | 3 | 6 |

## Fichiers créés

### tests/test_crud.py — 17 tests (base de données)

Tests directs des opérations CRUD sur SQLite in-memory.

**Employees :**

| Test | Vérifie |
|------|---------|
| `test_create_employee_returns_id` | ID auto-généré + champs persistés |
| `test_create_employee_persists_all_fields` | Département et âge custom |
| `test_get_existing_employee` | Récupération par ID |
| `test_get_nonexistent_employee_returns_none` | ID inexistant retourne None |
| `test_get_employees_pagination` | skip/limit respectés |
| `test_filter_by_department` | Filtre par département correct |
| `test_filter_empty_department` | Département inexistant retourne liste vide |

**Predictions :**

| Test | Vérifie |
|------|---------|
| `test_create_prediction_linked_to_employee` | FK employee_id correcte |
| `test_get_existing_prediction` | Récupération par ID |
| `test_get_nonexistent_prediction_returns_none` | ID inexistant retourne None |
| `test_get_predictions_pagination` | Pagination respectée |
| `test_filter_by_employee` | Filtre par employee_id |
| `test_high_risk_default_threshold` | Seuil 0.5 par défaut |
| `test_high_risk_custom_threshold` | Seuil custom (0.9) |

**Opérations combinées :**

| Test | Vérifie |
|------|---------|
| `test_creates_both_in_transaction` | Transaction combinée employé + prédiction, FK correcte |
| `test_statistics_with_data` | Comptages at_risk/stable + ratio |
| `test_statistics_empty_db` | Pas de division par zéro quand total = 0 |

### tests/test_model_loader.py — 15 tests (ML et preprocessing)

**Preprocessing :**

| Test | Vérifie |
|------|---------|
| `test_genre_encoding_male` | M encode en 1 |
| `test_genre_encoding_female` | F encode en 0 |
| `test_heures_sup_encoding_oui` | Oui encode en 1 |
| `test_heures_sup_encoding_non` | Non encode en 0 |
| `test_id_columns_dropped` | Colonnes id et eval_number supprimées |
| `test_one_hot_creates_columns` | Plus de colonnes de type object après encoding |

**Prédictions :**

| Test | Vérifie |
|------|---------|
| `test_returns_tuple` | predict_single retourne (int, float) |
| `test_prediction_binary` | prediction est 0 ou 1 |
| `test_probability_range` | probability entre 0.0 et 1.0 |
| `test_returns_list_of_correct_size` | predict_batch: 2 inputs donnent 2 résultats |
| `test_each_result_is_tuple` | Chaque résultat batch est (int, float) |
| `test_empty_batch` | Batch vide retourne liste vide |

**Chargement du modèle :**

| Test | Vérifie |
|------|---------|
| `test_returns_true_when_model_exists` | is_model_loaded retourne True |
| `test_returns_false_when_model_missing` | Path mocké inexistant retourne False |
| `test_raises_file_not_found` | Path invalide lève FileNotFoundError |
| `test_fallback_when_no_predict_proba` | Modèle sans predict_proba utilise le fallback |

**Labels :**

| Test | Vérifie |
|------|---------|
| `test_label_at_risk` | 1 donne "Risque de départ" |
| `test_label_stable` | 0 donne "Stable" |

### tests/test_connection.py — 3 tests (connexion BDD)

| Test | Vérifie |
|------|---------|
| `test_get_db_yields_session_and_closes` | Le générateur get_db yield une session puis se ferme |
| `test_connection_success` | Engine mock valide retourne True |
| `test_connection_failure` | Engine mock en erreur retourne False |

## Fichiers enrichis

### tests/test_api.py — +8 tests (validation API et persistance)

**Validation Pydantic supplémentaire :**

| Test | Vérifie |
|------|---------|
| `test_predict_validates_satisfaction_out_of_range` | satisfaction > 5 retourne 422 |
| `test_predict_validates_heure_supplementaires` | Valeur invalide retourne 422 |
| `test_predict_validates_statut_marital` | Statut invalide retourne 422 |
| `test_predict_validates_poste` | Poste invalide retourne 422 |
| `test_predict_validates_revenu_negatif` | Revenu negatif retourne 422 |
| `test_predict_validates_age_too_old` | Age > 70 retourne 422 |

**Comportement ML :**

| Test | Vérifie |
|------|---------|
| `test_predict_at_risk_employee_high_probability` | Employe a risque a une probabilite elevee |

**Persistance end-to-end :**

| Test | Vérifie |
|------|---------|
| `test_predict_persists_employee_and_prediction` | Apres /predict, employe et prediction existent en BDD |

### tests/test_data.py — +4 tests (cas limites data processing)

| Test | Vérifie |
|------|---------|
| `test_load_data` | Charge les 3 vrais CSV, colonnes cles presentes |
| `test_clean_eval_id_already_numeric` | Series deja numerique retourne tel quel |
| `test_process_and_merge_no_matching_ids` | IDs sans correspondance donnent un DataFrame vide |
| `test_prepare_features_without_target` | Pas de colonne cible donne y = None |

### tests/conftest.py — fixture partagée

Ajout de la fixture `db_session` qui fournit une session SQLite isolee par test avec rollback automatique, utilisee par test_crud.py et test_api.py.

## Couverture par module

| Module | Avant | Apres |
|--------|-------|-------|
| crud.py | indirect | 100% |
| models.py | indirect | 100% |
| schemas.py | partiel | 100% |
| connection.py | 52% | 100% |
| data_processing.py | 89% | 100% |
| model_loader.py | 93% | 97% |
| main.py | 79% | 79% |
| router.py | 88% | 88% |
| **TOTAL** | **~60%** | **80.3%** |

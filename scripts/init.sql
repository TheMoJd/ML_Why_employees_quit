-- Script d'initialisation de la base de données HR Analytics
-- Ce script est exécuté automatiquement au premier démarrage du conteneur PostgreSQL

-- Table des employés analysés
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 100),
    genre VARCHAR(1) NOT NULL CHECK (genre IN ('M', 'F')),
    revenu_mensuel FLOAT NOT NULL,
    statut_marital VARCHAR(50) NOT NULL,
    departement VARCHAR(100) NOT NULL,
    poste VARCHAR(100) NOT NULL,
    nombre_experiences_precedentes INTEGER DEFAULT 0,
    annee_experience_totale INTEGER DEFAULT 0,
    annees_dans_l_entreprise INTEGER DEFAULT 0,
    annees_dans_le_poste_actuel INTEGER DEFAULT 0,
    satisfaction_employee_environnement INTEGER CHECK (satisfaction_employee_environnement BETWEEN 1 AND 4),
    satisfaction_employee_nature_travail INTEGER CHECK (satisfaction_employee_nature_travail BETWEEN 1 AND 4),
    satisfaction_employee_equipe INTEGER CHECK (satisfaction_employee_equipe BETWEEN 1 AND 4),
    satisfaction_employee_equilibre_pro_perso INTEGER CHECK (satisfaction_employee_equilibre_pro_perso BETWEEN 1 AND 4),
    heure_supplementaires VARCHAR(3) CHECK (heure_supplementaires IN ('Oui', 'Non')),
    distance_domicile_travail INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des prédictions du modèle ML
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
    prediction INTEGER NOT NULL CHECK (prediction IN (0, 1)),
    probability FLOAT NOT NULL CHECK (probability >= 0 AND probability <= 1),
    label VARCHAR(50) NOT NULL,
    model_version VARCHAR(20) DEFAULT '1.0.0',
    predicted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances des requêtes
CREATE INDEX idx_predictions_employee_id ON predictions(employee_id);
CREATE INDEX idx_predictions_predicted_at ON predictions(predicted_at);
CREATE INDEX idx_employees_departement ON employees(departement);

-- Insertion d'exemples de données
INSERT INTO employees (age, genre, revenu_mensuel, statut_marital, departement, poste, 
                       nombre_experiences_precedentes, annee_experience_totale,
                       annees_dans_l_entreprise, annees_dans_le_poste_actuel,
                       satisfaction_employee_environnement, satisfaction_employee_nature_travail,
                       satisfaction_employee_equipe, satisfaction_employee_equilibre_pro_perso,
                       heure_supplementaires, distance_domicile_travail)
VALUES 
    (35, 'M', 5000.0, 'Marié(e)', 'Consulting', 'Consultant', 2, 10, 5, 3, 4, 4, 4, 3, 'Non', 10),
    (28, 'F', 3200.0, 'Célibataire', 'Commercial', 'Cadre Commercial', 1, 5, 2, 1, 3, 3, 2, 2, 'Oui', 25),
    (42, 'M', 8500.0, 'Marié(e)', 'Consulting', 'Manager', 4, 18, 12, 5, 4, 4, 4, 4, 'Non', 5);

-- Exemples de prédictions associées
INSERT INTO predictions (employee_id, prediction, probability, label)
VALUES 
    (1, 0, 0.15, 'Stable'),
    (2, 1, 0.72, 'Risque de départ'),
    (3, 0, 0.08, 'Stable');

-- Vue pour faciliter l'analyse des prédictions
CREATE OR REPLACE VIEW v_employee_predictions AS
SELECT 
    e.id as employee_id,
    e.age,
    e.genre,
    e.departement,
    e.poste,
    e.revenu_mensuel,
    p.prediction,
    p.probability,
    p.label,
    p.predicted_at
FROM employees e
LEFT JOIN predictions p ON e.id = p.employee_id
ORDER BY p.predicted_at DESC;

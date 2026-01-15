import pandas as pd
import numpy as np

def load_data(path_sirh, path_eval, path_sondage):
    """Charge les données depuis les fichiers CSV."""
    df_sirh = pd.read_csv(path_sirh)
    df_eval = pd.read_csv(path_eval)
    df_sondage = pd.read_csv(path_sondage)
    return df_sirh, df_eval, df_sondage

def clean_eval_id(series):
    """Transforme 'E_1' en 1."""
    if series.dtype == 'object':
        return series.str.replace('E_', '').astype(int)
    return series

def process_and_merge(df_sirh, df_eval, df_sondage):
    """Nettoie les clés et fusionne les dataframes."""
    # 1. SIRH
    df_sirh = df_sirh.rename(columns={'id_employee': 'id'})
    
    # 2. Eval
    df_eval = df_eval.copy()
    df_eval['id'] = clean_eval_id(df_eval['eval_number'])
    
    # 3. Sondage
    df_sondage = df_sondage.rename(columns={'code_sondage': 'id'})
    # Conversion sécurisée en int
    df_sondage['id'] = pd.to_numeric(df_sondage['id'], errors='coerce').astype('Int64')
    
    # Fusion Inner
    df_merged = df_sirh.merge(df_eval, on='id', how='inner')
    df_merged = df_merged.merge(df_sondage, on='id', how='inner')
    
    return df_merged

def prepare_features(df):
    """
    Prépare X et y pour l'entraînement.
    Encode les variables catégorielles (OneHot/Label).
    """
    df_proc = df.copy()
    
    # Cible
    if 'a_quitte_l_entreprise' in df_proc.columns:
        df_proc['target'] = (df_proc['a_quitte_l_entreprise'] == 'Oui').astype(int)
    
    # Colonnes à exclure (IDs et Target string)
    cols_to_drop = ['id', 'a_quitte_l_entreprise', 'eval_number', 'target']
    
    # Encodage binaire simple
    binary_cols = ['genre', 'heure_supplementaires']
    for col in binary_cols:
        if col in df_proc.columns:
            df_proc[col] = df_proc[col].astype('category').cat.codes
            
    # One Hot Encoding pour les autres catégorielles
    cat_cols = df_proc.select_dtypes(include=['object']).columns.tolist()
    # On retire les cols à drop de la liste des cat_cols si elles y sont
    cat_cols = [c for c in cat_cols if c not in cols_to_drop]
    
    df_proc = pd.get_dummies(df_proc, columns=cat_cols, drop_first=True, dtype=int)
    
    # Séparation X, y
    X = df_proc.drop(columns=[c for c in cols_to_drop if c in df_proc.columns], errors='ignore')
    y = df_proc['target'] if 'target' in df_proc.columns else None
    
    return X, y
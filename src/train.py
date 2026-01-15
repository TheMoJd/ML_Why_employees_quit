import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.metrics import classification_report

# Import relatif ou absolu selon l'installation
try:
    from src.data_processing import load_data, process_and_merge, prepare_features
except ImportError:
    from data_processing import load_data, process_and_merge, prepare_features

def main():
    print("Chargement des données...")
    # Assurez-vous que vos fichiers CSV sont dans un dossier 'data' à la racine
    try:
        df_sirh, df_eval, df_sondage = load_data(
            'data/extrait_sirh.csv',
            'data/extrait_eval.csv',
            'data/extrait_sondage.csv'
        )
    except FileNotFoundError:
        print("Erreur : Fichiers CSV introuvables dans le dossier 'data/'.")
        return

    print("Nettoyage et Fusion...")
    df_merged = process_and_merge(df_sirh, df_eval, df_sondage)
    
    print("Feature Engineering...")
    X, y = prepare_features(df_merged)
    
    print(f"Dimensions X: {X.shape}, y: {y.shape}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Pipeline : Scaling -> SMOTE -> LogReg (Meilleur modèle du notebook)
    pipeline = ImbPipeline([
        ('scaler', StandardScaler()),
        ('smote', SMOTE(random_state=42)),
        ('classifier', LogisticRegression(max_iter=1000, random_state=42))
    ])
    
    print("Entraînement du modèle...")
    pipeline.fit(X_train, y_train)
    
    # Évaluation rapide
    score = pipeline.score(X_test, y_test)
    print(f"Accuracy sur Test: {score:.4f}")
    
    # Sauvegarde
    joblib.dump(pipeline, 'model_hr.pkl')
    print("Modèle sauvegardé sous 'model_hr.pkl'")

if __name__ == "__main__":
    main()
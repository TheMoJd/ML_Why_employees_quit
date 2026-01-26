"""
Router FastAPI pour les endpoints de prédiction.
"""

from fastapi import APIRouter, HTTPException

from .schemas import (
    EmployeeInput,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse
)
from .model_loader import predict_single, predict_batch


router = APIRouter(prefix="/predict", tags=["Predictions"])


def get_label(prediction: int) -> str:
    """Retourne l'interprétation textuelle de la prédiction."""
    return "Risque de départ" if prediction == 1 else "Stable"


@router.post(
    "",
    response_model=PredictionResponse,
    summary="Prédiction pour un employé",
    description="Prédit si un employé risque de quitter l'entreprise"
)
async def predict_employee(employee: EmployeeInput) -> PredictionResponse:
    """
    Effectue une prédiction de turnover pour un employé.
    
    - **prediction**: 0 = l'employé reste, 1 = l'employé risque de partir
    - **probability**: Probabilité de départ (0.0 à 1.0)
    - **label**: Interprétation textuelle du résultat
    """
    try:
        prediction, probability = predict_single(employee.model_dump())
        
        return PredictionResponse(
            prediction=prediction,
            probability=probability,
            label=get_label(prediction)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")


@router.post(
    "/batch",
    response_model=BatchPredictionResponse,
    summary="Prédictions multiples",
    description="Prédit le turnover pour plusieurs employés en une seule requête"
)
async def predict_batch_employees(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """
    Effectue des prédictions pour plusieurs employés.
    
    Utile pour analyser un département ou une équipe entière.
    """
    try:
        inputs = [emp.model_dump() for emp in request.employees]
        results = predict_batch(inputs)
        
        predictions = [
            PredictionResponse(
                prediction=pred,
                probability=prob,
                label=get_label(pred)
            )
            for pred, prob in results
        ]
        
        return BatchPredictionResponse(
            predictions=predictions,
            total=len(predictions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction batch: {str(e)}")

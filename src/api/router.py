"""
Router FastAPI pour les endpoints de prédiction.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from .schemas import (
    EmployeeInput,
    PredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse
)
from .model_loader import predict_single, predict_batch
from .auth import get_current_user
from ..database.connection import get_db
from ..database import crud


router = APIRouter(prefix="/predict", tags=["Predictions"])


def get_label(prediction: int) -> str:
    """Retourne l'interprétation textuelle de la prédiction."""
    return "Risque de départ" if prediction == 1 else "Stable"


@router.post(
    "",
    response_model=PredictionResponse,
    summary="Prédiction pour un employé",
    description="Prédit si un employé risque de quitter l'entreprise et sauvegarde le résultat."
)
async def predict_employee(
    employee: EmployeeInput,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """
    Effectue une prédiction de turnover pour un employé.
    
    Sauvegarde automatiquement l'employé et le résultat en base de données.
    """
    try:
        # Prédiction
        inputs = employee.model_dump()
        prediction, probability = predict_single(inputs)
        label = get_label(prediction)
        
        # Sauvegarde en BDD
        crud.create_employee_with_prediction(
            db=db,
            employee_data=inputs,
            prediction=prediction,
            probability=probability,
            label=label
        )
        
        return PredictionResponse(
            prediction=prediction,
            probability=probability,
            label=label
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction: {str(e)}")


@router.post(
    "/batch",
    response_model=BatchPredictionResponse,
    summary="Prédictions multiples",
    description="Prédit le turnover pour plusieurs employés et sauvegarde les résultats."
)
async def predict_batch_employees(
    request: BatchPredictionRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BatchPredictionResponse:
    try:
        employees_data = [emp.model_dump() for emp in request.employees]
        results = predict_batch(employees_data)
        
        predictions = []
        for i, (pred, prob) in enumerate(results):
            label = get_label(pred)
            
            # Sauvegarde en BDD
            crud.create_employee_with_prediction(
                db=db,
                employee_data=employees_data[i],
                prediction=pred,
                probability=prob,
                label=label
            )
            
            predictions.append(
                PredictionResponse(
                    prediction=pred,
                    probability=prob,
                    label=label
                )
            )
        
        return BatchPredictionResponse(
            predictions=predictions,
            total=len(predictions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction batch: {str(e)}")

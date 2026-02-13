"""
Point d'entrée principal de l'API FastAPI.
Déploie le modèle de prédiction du turnover employé.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .schemas import HealthResponse
from .router import router as prediction_router
from .model_loader import is_model_loaded
from ..database.connection import engine, Base
from ..database.models import Employee, Prediction  # noqa: F401

# Chemin vers le dossier static
STATIC_DIR = Path(__file__).parent.parent.parent / "static"


@asynccontextmanager
async def lifespan(app):
    """Crée les tables automatiquement si elles n'existent pas."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass
    yield


# Métadonnées de l'API pour Swagger
app = FastAPI(
    lifespan=lifespan,
    title="HR Turnover Prediction API",
    description="""
API de prédiction du turnover des employés.

## Fonctionnalités

* **Prédiction individuelle** - Évalue le risque de départ d'un employé
* **Prédiction batch** - Analyse plusieurs employés en une requête
* **Documentation OpenAPI** - Interface Swagger intégrée

## Modèle

Le modèle utilise une régression logistique entraînée sur des données RH.
Il prédit la probabilité qu'un employé quitte l'entreprise.
    """,
    version="1.0.0",
    contact={
        "name": "Futurisys",
        "email": "contact@futurisys.com"
    },
    license_info={
        "name": "MIT"
    }
)

# Configuration CORS pour permettre les appels depuis n'importe quelle origine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montage du router de prédictions
app.include_router(prediction_router)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Vérification de santé de l'API"
)
async def health_check() -> HealthResponse:
    """
    Vérifie que l'API fonctionne et que le modèle est chargé.
    
    Utilisé pour les health checks Kubernetes/Docker.
    """
    return HealthResponse(
        status="healthy",
        model_loaded=is_model_loaded(),
        version="1.0.0"
    )


@app.get("/api/info", tags=["Root"])
async def api_info():
    """Informations sur l'API (JSON)."""
    return {
        "message": "HR Turnover Prediction API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"], include_in_schema=False)
async def root():
    """Sert le frontend si disponible, sinon JSON fallback."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path), media_type="text/html")
    return {
        "message": "HR Turnover Prediction API",
        "docs": "/docs",
        "health": "/health"
    }


# Montage des fichiers statiques (après les routes pour ne pas les masquer)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

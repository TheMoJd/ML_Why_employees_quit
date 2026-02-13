# Dockerfile pour l'API FastAPI
FROM python:3.9-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY pyproject.toml ./
COPY src ./src
COPY data ./data
COPY static ./static

# Installer les dépendances
RUN pip install --upgrade pip && \
    pip install -e .

# Entraîner le modèle au build
RUN python src/train.py

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

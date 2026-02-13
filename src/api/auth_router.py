"""
Router FastAPI pour l'authentification (register, login, profil).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .schemas import UserCreate, UserResponse, Token
from .auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from ..database.connection import get_db
from ..database import crud

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte",
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Crée un nouvel utilisateur."""
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur existe déjà",
        )
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cet email est déjà utilisé",
        )
    hashed = get_password_hash(user.password)
    db_user = crud.create_user(
        db, username=user.username, email=user.email,
        hashed_password=hashed,
    )
    return db_user


@router.post(
    "/token",
    response_model=Token,
    summary="Connexion (obtenir un token JWT)",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authentifie un utilisateur et retourne un token JWT."""
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": user.username})
    return Token(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Profil de l'utilisateur connecté",
)
def read_current_user(current_user=Depends(get_current_user)):
    """Retourne le profil de l'utilisateur authentifié."""
    return current_user

from core.Backend.auth.config.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context, oauth2_scheme
from core.Backend.app.database.database import  SessionLocal_users
from core.Backend.auth.schemas.schemas import  TokenData, User
from fastapi import  Depends, HTTPException, status
from core.Backend.auth.models.models import UserDB
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import  Annotated
import jwt



# Funções utilitárias
def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Erro ao verificar a senha: {e}")
        return False


# pegar o password transformado em hash
def get_password_hash(password):
    return pwd_context.hash(password)


# pegar a sessao do primeiro usuario encontrado
def get_user(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()


# verifica se esta autenticado
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# criar token de acesso
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # Copiando os dados para não modificar o original
    to_encode = data.copy()
    
    # Se expires_delta for fornecido, usa o valor. Caso contrário, usa o valor padrão
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adiciona o campo de expiração ao payload
    to_encode.update({"exp": expire})
    
    # Codifica o JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


# pegar a sessao atual
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError: # type: ignore
        raise credentials_exception
    db = SessionLocal_users()
    user = get_user(db, token_data.username)
    db.close()
    if user is None:
        raise credentials_exception
    return user


# verificar se a sessao ta ativa
async def get_current_active_user(
    current_user: Annotated[User , Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
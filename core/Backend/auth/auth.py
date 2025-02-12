from core.Backend.auth.models.models import UserDB
from core.Backend.app.database.database import  SessionLocal_users
from core.Backend.auth.config.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context, oauth2_scheme
from core.Backend.auth.schemas.schemas import  TokenData, User
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import  Annotated
import jwt
from fastapi import  Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from starlette.requests import Request
from starlette.responses import JSONResponse


# Funções utilitárias
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


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
    except InvalidTokenError:
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
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user




# Configurar o log
logging.basicConfig(level=logging.INFO)


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Loga os detalhes da requisição
        logging.info(f"Requisição recebida: {request.method} {request.url}")
        
        # Chama o próximo middleware ou rota
        response = await call_next(request)
        
        # Loga os detalhes da resposta
        logging.info(f"Resposta enviada com status {response.status_code}")
        
        return response
    

# middleware que verifica um token de autenticação antes de permitir o acesso a uma rota
class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        
        if token != "Bearer secret-token":
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        response = await call_next(request)
        return response
    

# talvez implementar, ou usar em cada rota
class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Em caso de erro, retorna uma resposta com código 500
            return JSONResponse(
                status_code=500,
                content={"message": "An unexpected error occurred", "error": str(e)},
            )
        
from core.Backend.auth.config.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context, oauth2_scheme
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from core.Backend.app.database.database import AsyncSessionLocal
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.Backend.auth.schemas.schemas import TokenData, User
from starlette.responses import JSONResponse
from core.Backend.auth.models.models import UserDB, Role
from starlette.requests import Request
from sqlalchemy.future import select  # Para consultas assíncronas
from typing import Annotated
import jwt


# Funções utilitárias
async def verify_password(plain_password: str, hashed_password: str) -> bool:
    # retorna um booleano ao verificar o passoword
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user(db: AsyncSession, email: str) -> UserDB:
    # busca o usuario pelo email
    result = await db.execute(select(UserDB).filter(UserDB.email == email))
    return result.scalars().first()


async def authenticate_user_by_email(db: AsyncSession, email: str, password: str):
    # buscar o usuário pelo e-mail
    result = await db.execute(select(UserDB).where(UserDB.email == email))
    user = result.scalars().first()

    # Verifica se o usuário foi encontrado e se a senha está correta
    if user and verify_password(password, user.hashed_password):
        return user
    return None

# Criar token de acesso
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Garantir que o 'role' seja serializável (se for Enum)
    if isinstance(to_encode.get("role"), Role):
        to_encode["role"] = to_encode["role"].value  # Pega o valor da Enum

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Pegar a sessão atual
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserDB:
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
    except jwt.exceptions.JWTError:
        raise credentials_exception

    async with AsyncSessionLocal() as db:
        user = await get_user(db, token_data.username)
        if user is None:
            raise credentials_exception
    return user


# Verificar se a sessão está ativa
async def get_current_active_user(current_user: Annotated[User , Depends(get_current_user)]) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user.")
    return current_user


# Função que verifica permissões de acesso
def check_permissions(user: UserDB, required_role: Role):
    if user.role != required_role and user.role != Role.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")



class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if token != "Bearer secret-token":
            raise HTTPException(status_code=401, detail="Unauthorized")
        response = await call_next(request)
        return response


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"message": "An unexpected error occurred", "error": str(e)},
            )
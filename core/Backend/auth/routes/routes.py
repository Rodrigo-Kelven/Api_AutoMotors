from fastapi import APIRouter, Depends, status, Form, Request
from core.Backend.auth.schemas.schemas import Token, User, UserResponse, UserResponseCreate, UserResponseEdit
from core.Backend.app.database.database import AsyncSessionLocal
from typing import List, Annotated
from core.Backend.auth.auth import OAuth2PasswordRequestForm, get_current_active_user, check_permissions, Role
from core.Backend.auth.services.services import ServicesAuth
from slowapi import Limiter
from slowapi.util import get_remote_address


# route for OAthu2
routes_auth_auten = APIRouter()


# decoracor do rate limit
limiter = Limiter(key_func=get_remote_address)


# Rota de login
@routes_auth_auten.post(
    path="/login",
    status_code=status.HTTP_200_OK,
    response_description="Informations of login",
    description="Route login user",
    name="Route login user"
)
@limiter.limit("20/minute") # O ideal é 5
async def login_for_access_token(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    return await ServicesAuth.login_user_Service(form_data)


# Rota para obter informações do usuário autenticado
@routes_auth_auten.get(
    path="/user/me/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=UserResponse,
    response_description="Informations user",
    description="Route get informations user",
    name="Route get informations user"
)
@limiter.limit("30/minute")  # Limite de 30 requisições por minuto
async def read_users_me(
    request: Request,
    current_user: Annotated[User , Depends(get_current_active_user)]
    ):
    check_permissions(current_user, Role.user)
    return current_user

# Rota para obter itens do usuário autenticado
# DESATIVADA
@routes_auth_auten.get(
    path="/users/me/items/",
    status_code=status.HTTP_202_ACCEPTED,
    response_description="Informations items user",
    description="Route get items user",
    name="Route get items user",
    deprecated=True
)
async def read_own_items(current_user: Annotated[User , Depends(get_current_active_user)]):
    return [{"item_id": "Foo", "owner": current_user.username}]

# Rota para criar um novo usuário
@routes_auth_auten.post(
    path="/user/register/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseCreate,
    response_description="Create user",
    description="Route create user",
    name="Route create user"
)
@limiter.limit("20/minute") # O ideal é 5
async def create_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
):
    return await ServicesAuth.create_user_Service(
        username, email, full_name, password)


# Rota para listar todos os usuários (somente admin)
# DESATIVADA
@routes_auth_auten.get(
    path="/users/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=List[UserResponse],
    response_description="Users",
    description="Route list users",
    name="Route list users",
    deprecated=True
)
async def get_users(current_user: Annotated[User , Depends(get_current_active_user)]):
    return await ServicesAuth.get_users_Service(current_user)

# Rota para atualizar informações do usuário
@routes_auth_auten.put(
    path="/user/update-account-me/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    response_description="Update informations user",
    description="Route update informations user",
    name="Route update user"
)
@limiter.limit("20/minute") # O ideal é 5
async def update_user(
    request: Request,
    email: str,
    user: UserResponseEdit,
    current_user: Annotated[User , Depends(get_current_active_user)]
    ):
    return await ServicesAuth.update_user_Service(email, user, current_user)

# Rota para deletar a conta do usuário
@routes_auth_auten.delete(
    path="/user/delete-account-me/",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Informations delete account",
    name="Route delete user"
)
@limiter.limit("10/minute")  # Limite de 10 requisições por minuto, o ideal é 2
async def delete_user(
    request: Request,
    current_user: Annotated[User  , Depends(get_current_active_user)]):
    return await ServicesAuth.delete_account_Service(current_user)
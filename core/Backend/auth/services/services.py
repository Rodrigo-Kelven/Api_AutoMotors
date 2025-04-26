from fastapi import APIRouter, Depends, HTTPException, status, Form, BackgroundTasks, Body
from fastapi.security import OAuth2PasswordRequestForm
from core.Backend.auth.schemas.schemas import Token, User, UserResponse, UserResponseCreate, UserResponseEdit
from core.Backend.app.database.database import AsyncSessionLocal
from core.Backend.auth.models.models import UserDB, Role
from typing import List, Annotated
from core.Backend.app.config.config import app_logger, auth_logger
from core.Backend.auth.auth import (
    authenticate_user_by_email,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    timedelta,
    get_current_active_user,
    check_permissions,
    get_password_hash,
    select,
    get_user
    )
from sqlalchemy.exc import IntegrityError


# servico somente de usuario
class ServicesAuth:

    @staticmethod
    async def login_user_Service(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        async with AsyncSessionLocal() as db:
            # autenticar o usuário usando o e-mail
            # este form_data.username nao recebe o username que foi passado em register, 
            # mas sim o username passado em login !!!!
            user = await authenticate_user_by_email(db, form_data.username, form_data.password)
            if not user:
                auth_logger.warning(msg="Usuario nao encontrado.")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email, "role": user.role}, 
                expires_delta=access_token_expires
            )
            auth_logger.info(msg=f"Usuário {form_data.username} logado com sucesso.")
            return Token(access_token=access_token, token_type="bearer")
    

    @staticmethod
    async def readUsersInformationsService(current_user: Annotated[User , Depends(get_current_active_user)]):
        """
        Args:
            confirma se o token é valido, sendo valido, realiza a busca dos dados do usuario referente ao token
        Returns:
            retorna os dados do usuario caso seja validade como logado tendo o token válido
        Raises:
            caso o nao seja autorizado, recebe um erro de acesso negado. 401
        """
        # Verifique as permissões antes de retornar as informações do usuário
        check_permissions(current_user, Role.user)  # Aqui verificamos se o usuário tem o papel de 'user'

        # Se a permissão foi verificada com sucesso, retornamos os dados do usuário
        return current_user
    

    @staticmethod
    async def create_user_Service(
        username: str = Form(...),
        email: str = Form(...),
        full_name: str = Form(...),
        password: str = Form(...),
    ):
        # Inicia a sessão com o banco de dados
        async with AsyncSessionLocal() as db:
            try:
                # Verifica se o username já está registrado
                user_with_username = await db.execute(select(UserDB).where(UserDB.username == username))
                if user_with_username.scalars().first():
                    auth_logger.warning(msg="Username já registrado!")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username já registrado!")

                # Verifica se o email já está registrado
                user_with_email = await db.execute(select(UserDB).where(UserDB.email == email))
                if user_with_email.scalars().first():
                    auth_logger.warning(msg="Email já registrado!")
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já registrado!")

                # Criação do usuário com senha criptografada
                hashed_password = await get_password_hash(password)
                db_user = UserDB(
                    username=username,
                    email=email,
                    full_name=full_name,
                    hashed_password=hashed_password,
                )
                
                # Adiciona o usuário à sessão do banco
                db.add(db_user)
                await db.commit()  # Commit para persistir a transação
                await db.refresh(db_user)  # Refresh para garantir que o db_user tenha os dados mais recentes
                auth_logger.info(msg=f"Usuario registrado: {username}.")
                return db_user

            except IntegrityError:
                await db.rollback()  # Reverte a transação em caso de erro
                auth_logger.warning(msg="Erro ao criar usuário. Verifique os dados fornecidos.")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar usuário. Verifique os dados fornecidos.")

            # except Exception as e:
            #     # Log de erros gerais e lançamento de exceção
            #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro inesperado: {str(e)}")
    

    # isto sera desativado, esta funcionalidade existira no painel de admin
    @staticmethod
    async def get_users_Service(current_user: Annotated[User , Depends(get_current_active_user)]):
        check_permissions(current_user, Role.admin)
        async with AsyncSessionLocal() as db:
            users = await db.execute(select(UserDB))
            return [UserResponse(**user.__dict__) for user in users.scalars()]

    

    @staticmethod
    async def update_user_Service(email: str, user: UserResponseEdit, current_user: Annotated[User , Depends(get_current_active_user)]):
        async with AsyncSessionLocal() as db:
            db_user = await get_user(db, email)

            if not db_user:
                auth_logger.error(msg="Usuário não encontrado!")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!")
            
            for key, value in user.dict(exclude_unset=True).items():
                setattr(db_user, key, value)
            
            await db.commit()
            await db.refresh(db_user)
            auth_logger.info(msg=f"Usuário {user.username} atualizado!")
            return db_user
    

    @staticmethod
    async def delete_account_Service(current_user: Annotated[User  , Depends(get_current_active_user)]):
        async with AsyncSessionLocal() as db:
            db_user = await get_user(db, current_user.email)

            if not db_user:
                auth_logger.error(msg="Usuário não encontrado!")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado!")
            
            await db.delete(db_user)
            await db.commit()
            auth_logger.info(msg=f"Usuário {current_user.username} deletado com sucesso!")
            return {"detail": f"Usuário {current_user.username} deletado com sucesso."}
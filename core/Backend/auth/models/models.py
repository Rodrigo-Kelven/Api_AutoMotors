from sqlalchemy import Column, Enum, String, Boolean, Enum as SQLAlchemyEnum
from core.Backend.app.database.database import Base_auth as Base
from enum import Enum as PyEnum


# Definindo os papéis possíveis (Role)
class Role(PyEnum):
    admin = "admin"
    user = "user"
    moderator = "moderator"


# Modelo de Usuário no banco de dados
class UserDB(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, unique=True, index=True, doc="Username do usuario, deve ser unico!")
    full_name = Column(String, index=True, doc="Nome completo do user")
    email = Column(String, unique=True, index=True, doc="Email do usuario, deve ser unico!")
    hashed_password = Column(String, doc="A senha do usuario é salva criptografada")
    disabled = Column(Boolean, default=False, doc="Estado do usuario, ativo/inativo")
    role = Column(SQLAlchemyEnum(Role), default=Role.admin, doc="Permissões do usuário: 'user', 'admin', ou 'moderator'")
    
from sqlalchemy import Column, String, Boolean
from core.Backend.app.database.database import Base


# Modelo de Usuário no banco de dados
class UserDB(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, unique=True, index=True, doc="Username do usuario, deve ser unico!")
    full_name = Column(String, index=True, doc="Nome completo do user")
    email = Column(String, unique=True, index=True, doc="Email do usuario, deve ser unico!")
    hashed_password = Column(String, doc="A senha do usuario é salva criptografada")
    disabled = Column(Boolean, default=False, doc="Estado do usuario, ativo/inativo")
    # caso queira criar um usuario admin, modifique aqui, ou na rota post
    role = Column(String, default="user", doc="permissoes do usuario, somente user")
# app/models/models.py
from sqlalchemy import Column, Integer, String
from app.database.database import Base

# tabela que será criada no db
class Carro(Base):
    __tablename__ = "carros"

    id = Column(Integer, primary_key=True, index=True)
    modelo = Column(String, index=True)
    ano = Column(Integer)
    preco = Column(Integer)
    imagem = Column(String)
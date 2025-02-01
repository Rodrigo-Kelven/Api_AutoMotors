from app.database.database import Base
from sqlalchemy import create_engine, Column, Integer, String


# Modelo de dados para o carro
class Carro(Base):
    __tablename__ = "carros"

    id = Column(Integer, primary_key=True, index=True)
    modelo = Column(String, index=True)
    ano = Column(Integer)
    preco = Column(Integer)
    imagem = Column(String)

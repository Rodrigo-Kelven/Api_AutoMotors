from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Modelo para a coleção de carros no MongoDB
class Carro(BaseModel):
    marca: str
    modelo: str
    categoria: str = "Carro"
    ano: int
    preco: float
    disponivel: bool
    tipo: str
    quilometragem: float
    cor: str
    portas: int
    lugares: int
    combustivel: str
    descricao: str
    endereco: str
    imagem: str
    data_criacao: datetime = datetime.utcnow()

    class Config:
        # Configuração para trabalhar com MongoDB
        arbitrary_types_allowed = True
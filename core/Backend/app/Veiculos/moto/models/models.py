from pydantic import BaseModel
from datetime import datetime


# Modelo para a coleção de carros no MongoDB
class Motos(BaseModel):
    marca: str
    modelo: str
    ano: int
    preco: float
    tipo: str
    disponivel: bool
    quilometragem: float
    cor: str
    lugares: int
    combustivel: str
    descricao: str
    endereco: str
    imagem: str
    data_criacao: datetime = datetime.utcnow()

    class Config:
        # Configuração para trabalhar com MongoDB
        arbitrary_types_allowed = True
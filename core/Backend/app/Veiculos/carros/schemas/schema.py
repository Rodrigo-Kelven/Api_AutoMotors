# app/schemas/schema.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CarroInfo(BaseModel):
    id: str  
    marca: str
    modelo: str
    categoria: str
    ano: int
    preco: float
    tipo: str
    disponivel: bool
    quilometragem: float
    cor: str
    portas: int
    lugares: int
    combustivel: str
    descricao: str
    endereco: str
    imagem: str
    data_criacao: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True  # Permite tipos como ObjectId

    @classmethod
    def from_mongo(cls, document) -> "CarroInfo":
        # Converte o _id do MongoDB (ObjectId) para string
        document["id"] = str(document["_id"])
        return cls(**document)


# somente para respostas sem _id/id
class CarroInfoResponse(BaseModel):
    marca: str
    modelo: str
    categoria: str
    ano: int
    preco: float
    tipo: str
    disponivel: bool
    quilometragem: float
    cor: str
    portas: int
    lugares: int
    combustivel: str
    descricao: str
    endereco: str
    imagem: str
    data_criacao: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True  # Permite tipos como ObjectId

    @classmethod
    def from_mongo(cls, document) -> "CarroInfoResponse":
        # Converte o _id do MongoDB (ObjectId) para string
        document["id"] = str(document["_id"])
        return cls(**document)



class Veiculo(BaseModel):
    id: Optional[int] = Field(default=None, title="ID do veículo")
    marca: str = Field(..., title="Marca do veículo")
    modelo: str = Field(..., title="Modelo do veículo")
    ano: int = Field(..., ge=1886, title="Ano do veículo")
    preco: float = Field(..., ge=0, title="Preço do veículo")
    disponivel: bool = Field(default=True, title="Disponibilidade do veículo")
    tipo: str = Field(..., title="Tipo de veículo")
    quilometragem: Optional[float] = Field(default=0, ge=0, title="Quilometragem do veículo")
    cor: Optional[str] = Field(default=None, title="Cor do veículo")
    data_cadastro: datetime = Field(default_factory=datetime.utcnow, title="Data de cadastro do veículo")
# app/schemas/schema.py
from pydantic import BaseModel


class CarroBase(BaseModel):
    modelo: str
    ano: int
    preco: float

class CarroCreate(CarroBase):
    imagem: str

class CarroInfo(BaseModel):
    id: int
    modelo: str
    ano: int
    kilometros: float 
    cor: str 
    combustivel: str 
    preco: float
    descricao: str
    imagem: str


    class Config:
        orm_mode = True


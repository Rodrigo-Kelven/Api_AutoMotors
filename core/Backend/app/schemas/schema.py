# app/schemas/schema.py
from pydantic import BaseModel

class CarroBase(BaseModel):
    modelo: str
    ano: int
    preco: float

class CarroCreate(CarroBase):
    imagem: str

class Carro(CarroBase):
    id: int

    class Config:
        orm_mode = True
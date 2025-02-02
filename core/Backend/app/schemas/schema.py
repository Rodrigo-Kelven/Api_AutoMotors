# app/schemas/schema.py
from pydantic import BaseModel

# criar modelos para cada categoria
# implementar mais caracteristicas para cada categoria

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


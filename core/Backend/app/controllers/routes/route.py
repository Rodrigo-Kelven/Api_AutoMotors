from fastapi import APIRouter, UploadFile, File, Form, status
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.models import Carro
from app.schemas.schema import CarroInfo
import os

router = APIRouter()

# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# rota POST 
@router.post(
        path="/carros/",
        status_code=status.HTTP_201_CREATED,
        response_model=CarroInfo,
        response_description="Informations of Car",
        description="Route create car",
        name="Route create car"
)
async def create_carro(
    Modelo: str = Form(..., title="Modelo do veiculo", alias="Modelo", description="Modelo do veiculo"),
    Ano: int = Form(..., title="Ano do veiculo", alias="Ano", description="Ano do veiculo"),
    Kilometros: float = Form(...),
    Cor: str = Form(...),
    Combustivel: str = Form(...),
    Preco: float = Form(..., title="Preço do veiculo", alias="Preco", description="Preço do veiculo"),
    Descricao: str = Form(..., title="Descriçao do veiculo", alias="Descricao", description="Descricao do veiculo"),
    Imagem: UploadFile = File(..., title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo")
):
    file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(await Imagem.read())
    
    db: Session = SessionLocal()
    carro = Carro(modelo=Modelo, ano=Ano, preco=Preco, descricao=Descricao, kilometros=Kilometros, cor=Cor, combustivel=Combustivel, imagem=file_location)
    db.add(carro)
    db.commit()
    db.refresh(carro)
    db.close()
    return carro

# rota GET
@router.get(
        path="/carros/",
        status_code=status.HTTP_200_OK,
        response_description="Informations of car",
        description="Route get informations of car",
        name="Route get informations of car"
)
async def get_carros():
    db: Session = SessionLocal()
    carros = db.query(Carro).all()
    db.close()
    return carros


# Rota GET para renderizar o template HTML
@router.get(
        path="/",
        status_code=status.HTTP_200_OK,
        response_description="Renderizaçao pag",
        description="Renderizacao pag",
        name="Renderizacao pag",
        response_class=HTMLResponse
)
async def read_root(request: Request):
    db: Session = SessionLocal()
    carros = db.query(Carro).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "carros": carros})
from fastapi import APIRouter, status, Body, Form, Query, HTTPException, UploadFile, File
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.Veiculos.moto.schemas.schemas import MotosInfo
from app.Veiculos.moto.models.models import Motos
import os


route_motos = APIRouter()

@route_motos.get(
    path="/veiculos-ultra-leves",
    status_code=status.HTTP_200_OK,
    response_model=list[MotosInfo],
    response_description="Informaçoes de veiculo",
    description="Route para pegar informações do veiculo",
    name="Pegar informações do veiculo"
)
async def list_veiculos():
    db: Session = SessionLocal()
    moto = db.query(Motos).all()
    db.close()
    return moto


# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# rota POST 
@route_motos.post(
        path="/veiculos-ultra-leves/",
        status_code=status.HTTP_201_CREATED,
        response_model=MotosInfo,
        response_description="Informações da Moto",
        description="Route para criar registro de Moto",
        name="Criar registro para Moto"
)
async def create_moto(
    Marca: str = Form(..., title="Marca do veiculo", alias="Marca", description="Marca do veiculo" ),
    Modelo: str = Form(..., title="Modelo do veiculo", alias="Modelo", description="Modelo do veiculo"),
    Ano: int = Form(..., title="Ano do veiculo", alias="Ano", description="Ano do veiculo"),
    Preco: float = Form(..., title="Preço do veiculo", alias="Preco", description="Preço do veiculo"),
    Tipo: str = Form(..., title="Tipo de veiculo", alias="Tipo", description="Tipo do veiculo", example="Moto esportiva"),
    #Cap_Maxima: int = Form(..., title="Capacidade máxima do veiculo", alias="Cap_Maxima", description="Capacidade maxima do veículo"),
    Disponivel: bool = Form(..., title="Veiculo disponivel", alias="Disponivel", description="Disponibilidade do veiculo"),
    Quilometragem: float = Form(..., title="Kilometros rodados", alias="Quilometragem", description="Kilometros rodados"),
    Cor: str = Form(..., title="Cor do veiculo", alias="Cor", description="Cor do veiculo"),
    Lugares: int = Form(..., title="Capacidade de ocupantes do veiculo", alias="Lugares", description="Quantidade de ocupantes do veiculo"),
    Combustivel: str = Form(..., title="Combustivel do veiculo", alias="Combustivel", description="Combustivel do veiculo"),
    Descricao: str = Form(..., title="Descriçao do veiculo", alias="Descricao", description="Descricao do veiculo"),
    Endereco: str = Form(..., title="Endereco", alias="Endereco", description="Endereco"),
    Imagem: UploadFile = File(..., title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo")
):
    file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(await Imagem.read())
    
    db: Session = SessionLocal()
    moto = Motos(
        marca=Marca,
        modelo=Modelo,
        ano=Ano,
        preco=Preco,
        tipo=Tipo,
        #cap_maxima=Cap_Maxima,
        disponivel=Disponivel,
        quilometragem=Quilometragem,
        cor=Cor,
        lugares=Lugares,
        combustivel=Combustivel,
        descricao=Descricao,
        endereco=Endereco,
        imagem=file_location
    )
    db.add(moto)
    db.commit()
    db.refresh(moto)
    db.close()
    return moto



# Rota GET para renderizar o template HTML
@route_motos.get(
        path="/veiculos-ultra-leves",
        status_code=status.HTTP_200_OK,
        response_description="Informações da Moto",
        description="Route para renderizar pagina",
        name="Renderizar pagina",
        response_class=HTMLResponse
)
async def read_root(request: Request):
    db: Session = SessionLocal()
    motos = db.query(Motos).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "carros": motos})


# rota GET
@route_motos.get(
        path="/veiculos-ultra-leves/",
        status_code=status.HTTP_200_OK,
        response_model=list[MotosInfo],
        response_description="Informaçoes da Moto",
        description="Route para pegar informações da motos",
        name="Pegar informações das motos"
)
async def get_carros():
    db: Session = SessionLocal()
    carros = db.query(Motos).all()
    db.close()
    return carros


# Rota PUT para atualizar um carro
@route_motos.put(
    path="/veiculos-ultra-leves/{moto_id}",
    status_code=status.HTTP_200_OK,
    response_model=MotosInfo,
    response_description="Informações do veiculo atualizadas",
    description="Route update information bikes",
    name ="Atualizar infomações da moto"
)
async def update_veiculo(
    moto_id: int,
    Marca: str = Form(..., title="Marca do veiculo", alias="Marca", description="Marca do veiculo" ),
    Modelo: str = Form(..., title="Modelo do veiculo", alias="Modelo", description="Modelo do veiculo"),
    Ano: int = Form(..., title="Ano do veiculo", alias="Ano", description="Ano do veiculo"),
    Preco: float = Form(..., title="Preço do veiculo", alias="Preco", description="Preço do veiculo"),
    Tipo: str = Form(..., title="Tipo de veiculo", alias="Tipo", description="Tipo do veiculo", example="Moto Esportiva"),
    #Cap_Maxima: int = Form(..., title="Capacidade máxima do veiculo", alias="Cap_Maxima", description="Capacidade maxima do veículo"),
    Disponivel: bool = Form(..., title="Veiculo disponivel", alias="Disponivel", description="Disponibilidade do veiculo"),
    Quilometragem: float = Form(..., title="Kilometros rodados", alias="Quilometragem", description="Kilometros rodados"),
    Cor: str = Form(..., title="Cor do veiculo", alias="Cor", description="Cor do veiculo"),
    Lugares: int = Form(..., title="Capacidade de ocupantes do veiculo", alias="Lugares", description="Quantidade de ocupantesat do veiculo"),
    Combustivel: str = Form(..., title="Combustivel do veiculo", alias="Combustivel", description="Combustivel do veiculo"),
    Descricao: str = Form(..., title="Descriçao do veiculo", alias="Descricao", description="Descricao do veiculo"),
    Endereco: str = Form(..., title="Endereco", alias="Endereco", description="Endereco"),
    Imagem: UploadFile = File(..., title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo")
):
    db: Session = SessionLocal()
    moto = db.query(Motos).filter(Motos.id == moto_id).first()

    if not moto:
        db.close()
        raise HTTPException(status_code=404, detail="Moto não encontrada")

    moto.marca = Marca
    moto.modelo = Modelo
    moto.ano = Ano
    moto.preco = Preco
    moto.disponivel = Disponivel
    moto.tipo = Tipo

    moto.disponivel = Disponivel
    moto.quilometragem = Quilometragem
    moto.cor = Cor
    moto.lugares = Lugares
    moto.combustivel = Combustivel
    moto.descricao = Descricao
    moto.endereco = Endereco
    

    if Imagem:
        file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
        with open(file_location, "wb") as file_object:
            file_object.write(await Imagem.read())
        moto.imagem = file_location

    db.commit()
    db.refresh(moto)
    db.close()
    return moto

# Rota DELETE para excluir um carro
@route_motos.delete(
    path="/veiculos-ultra-leves/{moto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Moto deletada",
    description="Route delete moto",
    name="Deletar moto"
)
async def delete_carro(moto_id: int):
    db: Session = SessionLocal()
    moto = db.query(Motos).filter(Motos.id == moto_id).first()

    if not moto:
        db.close()
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    db.delete(moto)
    db.commit()
    db.close()
    return {"detail": "Moto excluída com sucesso"}
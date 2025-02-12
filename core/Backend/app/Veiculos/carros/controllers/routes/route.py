from fastapi import APIRouter, UploadFile, File, Form, status, Query, Body, HTTPException
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from core.Backend.app.database.database import SessionLocal_veiculos
from core.Backend.app.Veiculos.carros.models.models import Carro
from core.Backend.app.Veiculos.carros.schemas.schema import CarroInfo
import os


# adicionar validacao e controle de acesso nas rotas, o usuario nao cadastrado e logado somente ver, ao logar, pode criar veiculos e editar seus dados e etc
router_carros = APIRouter()


# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# rota POST 
@router_carros.post(
        path="/veiculos-leves/",
        status_code=status.HTTP_201_CREATED,
        response_model=CarroInfo,
        response_description="Informaçoes do carros",
        description="Route para criar registro de carro",
        name="Criar registro para Carro"
)
# dividir por categorias, schema, models, categoria pra cada um
# rael, esses forms devem estar somente no front, os dados serao enviado em forma de forms diretamente para o db, junto com a imagem
# entao esses forms dessa rota sairao, ou nao, sla, veremos ao desenrolar do projeto
async def create_carro(
    Marca: str = Form(..., title="Marca do veiculo", alias="Marca", description="Marca do veiculo" ),
    Modelo: str = Form(..., title="Modelo do veiculo", alias="Modelo", description="Modelo do veiculo"),
    Ano: int = Form(..., title="Ano do veiculo", alias="Ano", description="Ano do veiculo"),
    Preco: float = Form(..., title="Preço do veiculo", alias="Preco", description="Preço do veiculo"),
    Tipo: str = Form(..., title="Tipo de veiculo", alias="Tipo", description="Tipo do veiculo", example="carro",),
    Disponivel: bool = Form(..., title="Veiculo disponivel", alias="Disponivel", description="Disponibilidade do veiculo"),
    Quilometragem: float = Form(..., title="Kilometros rodados", alias="Quilometragem", description="Kilometros rodados"),
    Cor: str = Form(..., title="Cor do veiculo", alias="Cor", description="Cor do veiculo"),
    Portas: int = Form(..., title="Numero de portas do veiculo", alias="Portas", description="Numero de portas do veiculo"),
    Lugares: int = Form(..., title="Capacidade de ocupantes do veiculo", alias="Lugares", description="Quantidade de ocupantes do veiculo"),
    Combustivel: str = Form(..., title="Combustivel do veiculo", alias="Combustivel", description="Combustivel do veiculo"),
    Descricao: str = Form(..., title="Descriçao do veiculo", alias="Descricao", description="Descricao do veiculo"),
    Endereco: str = Form(..., title="Endereco", alias="Endereco", description="Endereco"),
    Imagem: UploadFile = File(..., title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo")
):
    file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(await Imagem.read())
    
    db: Session = SessionLocal_veiculos()
    carro = Carro(
        marca=Marca,
        modelo=Modelo,
        ano=Ano,
        preco=Preco,
        disponivel=Disponivel,
        tipo=Tipo,
        quilometragem=Quilometragem,
        cor=Cor,
        portas=Portas,
        lugares=Lugares,
        combustivel=Combustivel,
        descricao=Descricao,
        endereco=Endereco,
        imagem=file_location
    )
    db.add(carro)
    db.commit()
    db.refresh(carro)
    db.close()
    return carro

# rota GET
@router_carros.get(
        path="/veiculos-leves/",
        status_code=status.HTTP_200_OK,
        response_model=list[CarroInfo],
        response_description="Informaçoes do carros",
        description="Route para pegar informacoes do carro",
        name="Pegar informacoes do Carro"
)
async def get_carros():
    db: Session = SessionLocal_veiculos()
    carros = db.query(Carro).all()
    db.close()
    return carros


# Rota GET para renderizar o template HTML
@router_carros.get(
        path="/veiculos-leves",
        status_code=status.HTTP_200_OK,
        response_description="Renderizaçao da pagina",
        description="Renderizacao de pagina",
        name="Renderizacao da pagina",
        response_class=HTMLResponse
)
async def read_root(request: Request):
    db: Session = SessionLocal_veiculos()
    carros = db.query(Carro).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "carros": carros})


# Rota PUT para atualizar um carro
@router_carros.put(
    path="/veiculos-leves/{carro_id}",
    status_code=status.HTTP_200_OK,
    response_model=CarroInfo,
    response_description="Informções atualizadas",
    description="Route update informações do carro",
    name ="Atualizar informações do Carro"
)
async def update_carro(
    carro_id: int,
    Marca: str = Form(..., title="Marca do veiculo", alias="Marca", description="Marca do veiculo" ),
    Modelo: str = Form(..., title="Modelo do veiculo", alias="Modelo", description="Modelo do veiculo"),
    Ano: int = Form(..., title="Ano do veiculo", alias="Ano", description="Ano do veiculo"),
    Preco: float = Form(..., title="Preço do veiculo", alias="Preco", description="Preço do veiculo"),
    Tipo: str = Form(..., title="Tipo de veiculo", alias="Tipo", description="Tipo do veiculo", example="carro",),
    Disponivel: bool = Form(..., title="Veiculo disponivel", alias="Disponivel", description="Disponibilidade do veiculo"),
    Quilometragem: float = Form(..., title="Kilometros rodados", alias="Quilometragem", description="Kilometros rodados"),
    Cor: str = Form(..., title="Cor do veiculo", alias="Cor", description="Cor do veiculo"),
    Portas: int = Form(..., title="Numero de portas do veiculo", alias="Portas", description="Numero de portas do veiculo"),
    Lugares: int = Form(..., title="Capacidade de ocupantes do veiculo", alias="Lugares", description="Quantidade de ocupantes do veiculo"),
    Combustivel: str = Form(..., title="Combustivel do veiculo", alias="Combustivel", description="Combustivel do veiculo"),
    Descricao: str = Form(..., title="Descriçao do veiculo", alias="Descricao", description="Descricao do veiculo"),
    Endereco: str = Form(..., title="Endereco", alias="Endereco", description="Endereco"),
    Imagem: UploadFile = File(None, title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo")
):
    db: Session = SessionLocal_veiculos()
    carro = db.query(Carro).filter(Carro.id == carro_id).first()

    if not carro:
        db.close()
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    carro.marca = Marca
    carro.modelo = Modelo
    carro.ano = Ano
    carro.preco = Preco
    carro.disponivel = Disponivel
    carro.tipo = Tipo
    carro.quilometragem = Quilometragem
    carro.cor = Cor
    carro.portas = Portas
    carro.lugares = Lugares
    carro.combustivel = Combustivel
    carro.descricao = Descricao
    carro.endereco = Endereco
    

    if Imagem:
        file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
        with open(file_location, "wb") as file_object:
            file_object.write(await Imagem.read())
        carro.imagem = file_location

    db.commit()
    db.refresh(carro)
    db.close()
    return carro

# Rota DELETE para excluir um carro
@router_carros.delete(
    path="/veiculos-leves/{carro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Delete carro",
    description="Route delete carro",
    name="Delete Carro"
)
async def delete_carro(carro_id: int,):
    db: Session = SessionLocal_veiculos()
    carro = db.query(Carro).filter(Carro.id == carro_id).first()

    if not carro:
        db.close()
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    db.delete(carro)
    db.commit()
    db.close()
    return {"detail": "Carro excluído com sucesso"}
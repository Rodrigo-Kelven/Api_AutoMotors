from fastapi import APIRouter, UploadFile, File, Form, status, Query, Body, HTTPException
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from core.Backend.app.database.database import SessionLocal_veiculos
from core.Backend.app.Veiculos.caminhao.models.models import Caminhao
from core.Backend.app.Veiculos.caminhao.schemas.schemas import CaminhaoInfo
import os


# adicionar validacao e controle de acesso nas rotas, o usuario nao cadastrado e logado somente ver, ao logar, pode criar veiculos e editar seus dados e etc
router_caminhoes = APIRouter()


# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# rota POST 
@router_caminhoes.post(
        path="/veiculos-pesados/",
        status_code=status.HTTP_201_CREATED,
        response_model=CaminhaoInfo,
        response_description="Informaçoes do carros",
        description="Route para criar registro de carro",
        name="Criar registro para Carro"
)
# dividir por categorias, schema, models, categoria pra cada um
# rael, esses forms devem estar somente no front, os dados serao enviado em forma de forms diretamente para o db, junto com a imagem
# entao esses forms dessa rota sairao, ou nao, sla, veremos ao desenrolar do projeto
async def create_caminhao(
    Marca: str = Form(..., title="Marca do veiculo", alias="Marca", description="Marca do veiculo" ),
    Modelo: str = Form(..., title="Modelo do veiculo", alias="Modelo", description="Modelo do veiculo"),
    Ano: int = Form(..., title="Ano do veiculo", alias="Ano", description="Ano do veiculo"),
    Preco: float = Form(..., title="Preço do veiculo", alias="Preco", description="Preço do veiculo"),
    Tipo: str = Form(..., title="Tipo de veiculo", alias="Tipo", description="Tipo do veiculo", example="carro",),
    Cap_Maxima: int = Form(..., title="Capacidade máxima do veiculo", alias="Cap_Maxima", description="Capacidade maxima do veículo"),
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
    caminhao = Caminhao(
        marca=Marca,
        modelo=Modelo,
        ano=Ano,
        preco=Preco,
        disponivel=Disponivel,
        tipo=Tipo,
        cap_maxima=Cap_Maxima,
        quilometragem=Quilometragem,
        cor=Cor,
        portas=Portas,
        lugares=Lugares,
        combustivel=Combustivel,
        descricao=Descricao,
        endereco=Endereco,
        imagem=file_location
    )
    db.add(caminhao)
    db.commit()
    db.refresh(caminhao)
    db.close()
    return caminhao

# rota GET
@router_caminhoes.get(
        path="/veiculos-pesados/",
        status_code=status.HTTP_200_OK,
        response_model=list[CaminhaoInfo],
        response_description="Informaçoes do carros",
        description="Route para pegar informacoes do carro",
        name="Pegar informacoes do Carro"
)
async def get_caminhao():
    db: Session = SessionLocal_veiculos()
    carros = db.query(Caminhao).all()
    db.close()
    return carros


# Rota GET para renderizar o template HTML
@router_caminhoes.get(
        path="/veiculos-pesados",
        status_code=status.HTTP_200_OK,
        response_description="Renderizaçao da pagina",
        description="Renderizacao de pagina",
        name="Renderizacao da pagina",
        response_class=HTMLResponse
)
async def read_root(request: Request):
    db: Session = SessionLocal_veiculos()
    caminhao = db.query(Caminhao).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": request, "carros": caminhao})


# Rota PUT para atualizar um carro
@router_caminhoes.put(
    path="/veiculos-pesados/{caminhao_id}",
    status_code=status.HTTP_200_OK,
    response_model=CaminhaoInfo,
    response_description="Informções atualizadas",
    description="Route update informações do carro",
    name ="Atualizar informações do Carro"
)
async def update_caminhao(
    caminhao_id: int,
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
    caminhao = db.query(Caminhao).filter(Caminhao.id == caminhao_id).first()

    if not caminhao:
        db.close()
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    caminhao.marca = Marca
    caminhao.modelo = Modelo
    caminhao.ano = Ano
    caminhao.preco = Preco
    caminhao.disponivel = Disponivel
    caminhao.tipo = Tipo
    caminhao.quilometragem = Quilometragem
    caminhao.cor = Cor
    caminhao.portas = Portas
    caminhao.lugares = Lugares
    caminhao.combustivel = Combustivel
    caminhao.descricao = Descricao
    caminhao.endereco = Endereco
    

    if Imagem:
        file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
        with open(file_location, "wb") as file_object:
            file_object.write(await Imagem.read())
        caminhao.imagem = file_location

    db.commit()
    db.refresh(caminhao)
    db.close()
    return caminhao

# Rota DELETE para excluir um carro
@router_caminhoes.delete(
    path="/veiculos-pesados/{caminhao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Delete carro",
    description="Route delete carro",
    name="Delete Carro"
)
async def delete_carro(caminhao_id: int,):
    db: Session = SessionLocal_veiculos()
    caminhao = db.query(Caminhao).filter(Caminhao.id == caminhao_id).first()

    if not caminhao:
        db.close()
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    db.delete(caminhao)
    db.commit()
    db.close()
    return {"detail": "Carro excluído com sucesso"}
from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException, Request
from typing import List
from bson import ObjectId
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from core.Backend.app.database.database import db
from core.Backend.app.Veiculos.caminhao.models.models import Caminhao
from core.Backend.app.Veiculos.caminhao.schemas.schemas import CaminhaoInfo
import os


# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


router_caminhoes = APIRouter()



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

    # Salva o carro no MongoDB
    result = await db.caminhao.insert_one(caminhao.dict())  # Converte o objeto para um dict
    caminhao_db = await db.caminhao.find_one({"_id": result.inserted_id})  # Recupera o carro inserido do banco
    
    # Converte para o modelo CarroInfo, incluindo o id
    return CaminhaoInfo.from_mongo(caminhao_db)


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
    caminhao_cursor = db.caminhao.find()
    carros = [CaminhaoInfo.from_mongo(caminhao) for caminhao in await caminhao_cursor.to_list(length=100)]
    return carros


@router_caminhoes.get(
    path="/veiculos-pesados/{caminhao_id}",
    status_code=status.HTTP_200_OK,
    response_model=CaminhaoInfo,
    response_description="Informações dos carros",
    description="Route para pegar informações do carro",
    name="Pegar informações do Carro"
)
async def get_carros(caminhao_id: str):
    try:
        # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
        caminhao_object_id = ObjectId(caminhao_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID de carro inválido")

    # Busca o carro no banco de dados
    caminhao = await db.caminhao.find_one({"_id": caminhao_object_id})

    if not caminhao:
        raise HTTPException(status_code=404, detail="Caminhao não encontrado")
    
    # Retorna o carro no formato adequado, com o id convertido
    return CaminhaoInfo.from_mongo(caminhao)


# Rota GET para renderizar o template HTML
@router_caminhoes.get(
        deprecated=True,
        path="/veiculos-pesados",
        status_code=status.HTTP_200_OK,
        response_description="Renderizaçao da pagina",
        description="Renderizacao de pagina",
        name="Renderizacao da pagina",
        response_class=HTMLResponse
)
async def read_root(request: Request):
    caminhao_cursor = db.caminhao.find()
    caminhao = [CaminhaoInfo.from_mongo(caminhao) for caminhao in await caminhao_cursor.to_list(length=100)]
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
    caminhao_id: str,
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
    Imagem: UploadFile = File(None, title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo")
):

    try:
        # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
        caminhao_object_id = ObjectId(caminhao_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID de carro inválido")

    # Busca o carro no banco de dados
    caminhao = await db.caminhao.find_one({"_id": caminhao_object_id})

    if not caminhao:
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    update_data = {
        "marca": Marca,
        "modelo": Modelo,
        "ano": Ano,
        "preco": Preco,
        "disponivel": Disponivel,
        "tipo": Tipo,
        "cap_maxima": Cap_Maxima,
        "quilometragem": Quilometragem,
        "cor": Cor,
        "portas": Portas,
        "lugares": Lugares,
        "combustivel": Combustivel,
        "descricao": Descricao,
        "endereco": Endereco,
    }

    if Imagem:
        file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
        with open(file_location, "wb") as file_object:
            file_object.write(await Imagem.read())
        update_data["imagem"] = file_location

    # Atualiza o carro no banco de dados
    await db.caminhao.update_one({"_id": caminhao_object_id}, {"$set": update_data})
    
    # Recupera o carro atualizado
    updated_carro = await db.caminhao.find_one({"_id": caminhao_object_id})
    
    # Retorna o carro atualizado como CarroInfo
    return CaminhaoInfo.from_mongo(updated_carro)



# Rota DELETE para excluir um carro
@router_caminhoes.delete(
    path="/veiculos-pesados/{caminhao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Delete carro",
    description="Route delete carro",
    name="Delete Carro"
)
async def delete_carro(caminhao_id: str):
    try:
        # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
        carro_object_id = ObjectId(caminhao_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID de carro inválido")

    # Busca o carro no banco de dados
    carro = await db.caminhao.find_one({"_id": carro_object_id})

    if not carro:
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    # Exclui o carro usando o ObjectId
    await db.caminhao.delete_one({"_id": carro_object_id})

    return {"detail": "Carro excluído com sucesso"}
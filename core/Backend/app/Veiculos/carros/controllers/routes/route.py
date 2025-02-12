from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException, Request
from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from core.Backend.app.Veiculos.carros.models.models import Carro
from core.Backend.app.Veiculos.carros.schemas.schema import CarroInfo
from core.Backend.app.database.database import db
import os

# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# Verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)




router_carros = APIRouter()


# Rota POST para criar um carro
@router_carros.post(
    path="/veiculos-leves/",
    status_code=status.HTTP_201_CREATED,
    response_model=CarroInfo,
    response_description="Informações do carro",
    description="Route para criar registro de carro",
    name="Criar registro para Carro"
)
async def create_carro(
    Marca: str = Form(...),
    Modelo: str = Form(...),
    Ano: int = Form(...),
    Preco: float = Form(...),
    Tipo: str = Form(...),
    Disponivel: bool = Form(...),
    Quilometragem: float = Form(...),
    Cor: str = Form(...),
    Portas: int = Form(...),
    Lugares: int = Form(...),
    Combustivel: str = Form(...),
    Descricao: str = Form(...),
    Endereco: str = Form(...),
    Imagem: UploadFile = File(...),
):
    file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(await Imagem.read())
    
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
        imagem=file_location,
    )

    # Salva o carro no MongoDB
    result = await db.carros.insert_one(carro.dict())  # Converte o objeto para um dict
    carro_db = await db.carros.find_one({"_id": result.inserted_id})  # Recupera o carro inserido do banco
    
    # Converte para o modelo CarroInfo, incluindo o id
    return CarroInfo.from_mongo(carro_db)

# Rota GET para listar todos os carros
@router_carros.get(
    path="/veiculos-leves/",
    status_code=status.HTTP_200_OK,
    response_model=List[CarroInfo],
    response_description="Informações dos carros",
    description="Route para pegar informações do carro",
    name="Pegar informações do Carro"
)
async def get_carros():
    carros_cursor = db.carros.find()
    carros = [CarroInfo.from_mongo(carro) for carro in await carros_cursor.to_list(length=100)]
    return carros



# Rota GET para renderizar o template HTML
@router_carros.get(
    deprecated=True,
    path="/veiculos-leves",
    status_code=status.HTTP_200_OK,
    response_description="Renderização da página",
    description="Renderização de página",
    name="Renderização da página",
    response_class=HTMLResponse
)
async def read_root(request: Request):
    carros_cursor = db.carros.find()
    carros = [CarroInfo.from_mongo(carro) for carro in await carros_cursor.to_list(length=100)]
    return templates.TemplateResponse("index.html", {"request": request, "carros": carros})


# Rota PUT para atualizar um carro
from bson import ObjectId

@router_carros.put(
    path="/veiculos-leves/{carro_id}",
    status_code=status.HTTP_200_OK,
    response_model=CarroInfo,
    response_description="Informações atualizadas",
    description="Route update informações do carro",
    name="Atualizar informações do Carro"
)
async def update_carro(
    carro_id: str,
    Marca: str = Form(...),
    Modelo: str = Form(...),
    Ano: int = Form(...),
    Preco: float = Form(...),
    Tipo: str = Form(...),
    Disponivel: bool = Form(...),
    Quilometragem: float = Form(...),
    Cor: str = Form(...),
    Portas: int = Form(...),
    Lugares: int = Form(...),
    Combustivel: str = Form(...),
    Descricao: str = Form(...),
    Endereco: str = Form(...),
    Imagem: UploadFile = File(None),
):
    try:
        # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
        carro_object_id = ObjectId(carro_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID de carro inválido")

    # Busca o carro no banco de dados
    carro = await db.carros.find_one({"_id": carro_object_id})

    if not carro:
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    update_data = {
        "marca": Marca,
        "modelo": Modelo,
        "ano": Ano,
        "preco": Preco,
        "disponivel": Disponivel,
        "tipo": Tipo,
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
    await db.carros.update_one({"_id": carro_object_id}, {"$set": update_data})
    
    # Recupera o carro atualizado
    updated_carro = await db.carros.find_one({"_id": carro_object_id})
    
    # Retorna o carro atualizado como CarroInfo
    return CarroInfo.from_mongo(updated_carro)


# Rota DELETE para excluir um carro
@router_carros.delete(
    path="/veiculos-leves/{carro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Delete carro",
    description="Route delete carro",
    name="Delete Carro"
)
async def delete_carro(carro_id: str):
    try:
        # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
        carro_object_id = ObjectId(carro_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID de carro inválido")

    # Busca o carro no banco de dados
    carro = await db.carros.find_one({"_id": carro_object_id})

    if not carro:
        raise HTTPException(status_code=404, detail="Carro não encontrado")

    # Exclui o carro usando o ObjectId
    await db.carros.delete_one({"_id": carro_object_id})

    return {"detail": "Carro excluído com sucesso"}


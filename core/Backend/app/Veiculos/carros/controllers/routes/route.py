from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException, Request, Depends
from core.Backend.app.Veiculos.carros.schemas.schema import CarroInfo
from core.Backend.app.Veiculos.carros.models.models import Carro
from core.Backend.auth.auth import get_current_user
from core.Backend.app.config.config import logger
from core.Backend.app.database.database import db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from bson import ObjectId
from typing import List
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
    Imagem: UploadFile = File(..., title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo"),
    current_user: str = Depends(get_current_user)  # Garante que o usuário está autenticado
):
    # Salva a imagem no diretório uploads

    file_location = os.path.join(UPLOAD_DIRECTORY, Imagem.filename)
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
        imagem="uploads/" + Imagem.filename,
    )


    # Salva o carro no MongoDB
    result = await db.carros.insert_one(carro.dict())  # Converte o objeto para um dict
    carro_db = await db.carros.find_one({"_id": result.inserted_id})  # Recupera o carro inserido do banco


    # logs
    logger.info(
        msg=f"Carro inserido: {carro_db["_id"]}"
    )

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
    
    if carros:
        logger.info(
            msg="Carros sendo listados!"
        )
        return carros
    
    if not carros:
        logger.info(
            msg="Nenhum carro inserido!"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum carro inserido!")


@router_carros.get(
    path="/veiculos-leves/{carro_id}",
    status_code=status.HTTP_200_OK,
    response_model=CarroInfo,
    response_description="Informações dos carros",
    description="Route para pegar informações do carro",
    name="Pegar informações do Carro"
)
async def get_carros(carro_id: str):
    try:
        # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
        carro_object_id = ObjectId(carro_id)

    except Exception as e:
        logger.error(
            msg="ID de carro inválido!"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de carro inválido!")

    # Busca o carro no banco de dados
    carro = await db.carros.find_one({"_id": carro_object_id})

    if not carro:
        logger.error(
            msg="Carro não encontrado!"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado!")
    
    # logs
    logger.info(
        msg=f"Informações do carro: {carro["_id"]}"
    )

    # Retorna o carro no formato adequado, com o id convertido
    return CarroInfo.from_mongo(carro)


# Rota GET para renderizar o template HTML
@router_carros.get(
    path="/veiculos-leves/page/",
    status_code=status.HTTP_200_OK,
    response_description="Renderização da página",
    description="Renderização de página",
    name="Renderização da página",
    response_class=HTMLResponse
)
async def read_root(request: Request):
    carros_cursor = db.carros.find()
    carros = [CarroInfo.from_mongo(carro) for carro in await carros_cursor.to_list(length=100)]

    logger.info(
        msg="Pagina de veiculos leves: carros!"
    )
    return templates.TemplateResponse("index.html", {"request": request, "carros": carros})


# Rota PUT para atualizar um carro
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
    Imagem: UploadFile = File(..., title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo"),
    current_user: str = Depends(get_current_user)
):
    try:
        # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
        carro_object_id = ObjectId(carro_id)
    except Exception as e:
        logger.error(
            msg="ID de carro inválido!"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de carro inválido!")

    # Busca o carro no banco de dados
    carro = await db.carros.find_one({"_id": carro_object_id})

    if not carro:
        logger.error(
            msg="Carro não encontrado!"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado")

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

    # logs
    logger.info(
        msg=f"Carro atualizado: {updated_carro["_id"]}"
    )
    
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
async def delete_carro(
    carro_id: str,
    current_user: str = Depends(get_current_user)  # Garante que o usuário está autenticado
    ):
    try:
        # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
        carro_object_id = ObjectId(carro_id)
    except Exception as e:
        logger.error(
            msg="ID de carro inválido!"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de carro inválido!")

    # Busca o carro no banco de dados
    carro = await db.carros.find_one({"_id": carro_object_id})

    if not carro:
        logger.error(
            msg="Carro não encontrado!"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado!")

    # Exclui o carro usando o ObjectId
    await db.carros.delete_one({"_id": carro_object_id})

    # logs
    logger.info(
        msg=f"Carro deletado: {carro["_id"]}"
    )

    return {"detail": "Carro excluído com sucesso"}
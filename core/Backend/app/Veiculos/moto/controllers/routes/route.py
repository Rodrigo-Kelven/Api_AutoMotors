from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException, Request, Depends
from core.Backend.app.Veiculos.moto.schemas.schemas import MotosInfo
from core.Backend.app.Veiculos.moto.models.models import Motos
from core.Backend.auth.auth import get_current_user
from core.Backend.app.config.config import logger
from core.Backend.app.database.database import db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from bson import ObjectId
import os


# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


route_motos = APIRouter()


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
    Disponivel: bool = Form(..., title="Veiculo disponivel", alias="Disponivel", description="Disponibilidade do veiculo"),
    Quilometragem: float = Form(..., title="Kilometros rodados", alias="Quilometragem", description="Kilometros rodados"),
    Cor: str = Form(..., title="Cor do veiculo", alias="Cor", description="Cor do veiculo"),
    Lugares: int = Form(..., title="Capacidade de ocupantes do veiculo", alias="Lugares", description="Quantidade de ocupantes do veiculo"),
    Combustivel: str = Form(..., title="Combustivel do veiculo", alias="Combustivel", description="Combustivel do veiculo"),
    Descricao: str = Form(..., title="Descriçao do veiculo", alias="Descricao", description="Descricao do veiculo"),
    Endereco: str = Form(..., title="Endereco", alias="Endereco", description="Endereco"),
    Imagem: UploadFile = File(..., title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo"),
    current_user: str = Depends(get_current_user)  # Garante que o usuário está autenticado
):
    file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(await Imagem.read())
    
    moto = Motos(
        marca=Marca,
        modelo=Modelo,
        ano=Ano,
        preco=Preco,
        tipo=Tipo,
        disponivel=Disponivel,
        quilometragem=Quilometragem,
        cor=Cor,
        lugares=Lugares,
        combustivel=Combustivel,
        descricao=Descricao,
        endereco=Endereco,
        imagem=file_location
    )

    # Salva o moto no MongoDB
    result = await db.motos.insert_one(moto.dict())  # Converte o objeto para um dict
    moto_db = await db.motos.find_one({"_id": result.inserted_id})  # Recupera o moto inserido do banco
    
    # Converte para o modelo MotoInfo, incluindo o id
    return MotosInfo.from_mongo(moto_db)


@route_motos.get(
    path="/veiculos-ultra-leves",
    status_code=status.HTTP_200_OK,
    response_model=list[MotosInfo],
    response_description="Informaçoes da moto",
    description="Route para pegar informações da moto",
    name="Pegar informações do Moto"
)
async def list_veiculos():
    motos_cursor = db.motos.find()
    motos = [MotosInfo.from_mongo(moto) for moto in await motos_cursor.to_list(length=100)]

    if motos:
        logger.info(
            msg="Motos sendo listadas!"
        )
        return motos
    
    if not motos:
        logger.error(
            msg="Nenhuma moto inserida!"
            )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma moto inserido!")



@route_motos.get(
    path="/veiculos-ultra-leves/{moto_id}",
    status_code=status.HTTP_200_OK,
    response_model=MotosInfo,
    response_description="Informaçoes da moto",
    description="Route para pegar informações da moto",
    name="Pegar informações da moto"
)
async def list_veiculos(moto_id: str):
    try:
        # Tenta converter a moto_id para ObjectId, porque o MongoDB trabalha com objetos!
        moto_object_id = ObjectId(moto_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de moto inválido")

    # Busca a moto no banco de dados
    moto = await db.motos.find_one({"_id": moto_object_id})

    if not moto:
        logger.info(
            msg="Moto não encontrada!"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moto não encontrada")
    
    # logger.info(
    #     msg=f"Informações da moto: {moto["_id"]}"
    # )
    
    # Retorna a moto no formato adequado, com o id convertido
    return MotosInfo.from_mongo(moto)


# Rota GET para renderizar o template HTML
@route_motos.get(
        path="/veiculos-ultra-leves/page/",
        status_code=status.HTTP_200_OK,
        response_description="Informações da Moto",
        description="Route para renderizar pagina",
        name="Renderizar pagina",
        response_class=HTMLResponse
)
async def read_root(request: Request):
    motos_cursor = db.motos.find()
    motos = [MotosInfo.from_mongo(moto) for moto in await motos_cursor.to_list(length=100)]

    logger.info(
        msg="Pagina de veiculos ultra leves: motos!"
    )
    return templates.TemplateResponse("index.html", {"request": request, "carros": motos})




# Rota PUT para atualizar uma moto
@route_motos.put(
    path="/veiculos-ultra-leves/{moto_id}",
    status_code=status.HTTP_200_OK,
    response_model=MotosInfo,
    response_description="Informações do veiculo atualizadas",
    description="Route update information moto",
    name ="Atualizar infomações da moto"
)
async def update_veiculo(
    moto_id: str,
    Marca: str = Form(..., title="Marca do veiculo", alias="Marca", description="Marca do veiculo" ),
    Modelo: str = Form(..., title="Modelo do veiculo", alias="Modelo", description="Modelo do veiculo"),
    Ano: int = Form(..., title="Ano do veiculo", alias="Ano", description="Ano do veiculo"),
    Preco: float = Form(..., title="Preço do veiculo", alias="Preco", description="Preço do veiculo"),
    Tipo: str = Form(..., title="Tipo de veiculo", alias="Tipo", description="Tipo do veiculo", example="Moto Esportiva"),
    Disponivel: bool = Form(..., title="Veiculo disponivel", alias="Disponivel", description="Disponibilidade do veiculo"),
    Quilometragem: float = Form(..., title="Kilometros rodados", alias="Quilometragem", description="Kilometros rodados"),
    Cor: str = Form(..., title="Cor do veiculo", alias="Cor", description="Cor do veiculo"),
    Lugares: int = Form(..., title="Capacidade de ocupantes do veiculo", alias="Lugares", description="Quantidade de ocupantesat do veiculo"),
    Combustivel: str = Form(..., title="Combustivel do veiculo", alias="Combustivel", description="Combustivel do veiculo"),
    Descricao: str = Form(..., title="Descriçao do veiculo", alias="Descricao", description="Descricao do veiculo"),
    Endereco: str = Form(..., title="Endereco", alias="Endereco", description="Endereco"),
    Imagem: UploadFile = File(..., title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo"),
    current_user: str = Depends(get_current_user)  # Garante que o usuário está autenticado
):
    try:
        # Tenta converter a moto_id para ObjectId, porque o MongoDB trabalha com objetos!
        moto_object_id = ObjectId(moto_id)
    except Exception as e:
        logger.error(
            msg="Id moto invalido!"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de moto inválido")

    # Busca a moto no banco de dados
    moto = await db.motos.find_one({"_id": moto_object_id})

    if not moto:
        logger.error(
            msg="Moto nao encontrada"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moto não encontrada!")

    update_data = {
        "marca": Marca,
        "modelo": Modelo,
        "ano": Ano,
        "preco": Preco,
        "disponivel": Disponivel,
        "tipo": Tipo,
        "quilometragem": Quilometragem,
        "cor": Cor,
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

    # Atualiza a moto no banco de dados
    await db.motos.update_one({"_id": moto_object_id}, {"$set": update_data})
    
    # Recupera a moto atualizada
    updated_moto = await db.motos.find_one({"_id": moto_object_id})

    # logger.info(
    #     msg=f"Moto atualizada: {moto["_id"]}"
    # )
    
    # Retorna a moto atualizado como MotoInfo
    return MotosInfo.from_mongo(updated_moto)


# Rota DELETE para excluir uma moto
@route_motos.delete(
    path="/veiculos-ultra-leves/{moto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Moto deletada",
    description="Route delete moto",
    name="Deletar Moto"
)
async def delete_carro(
    moto_id: str,
    current_user: str = Depends(get_current_user)  # Garante que o usuário está autenticado
    ):
    try:
        # Tenta converter o moto_id para ObjectId, porque o MongoDB trabalha com objetos!
        moto_object_id = ObjectId(moto_id)
    except Exception as e:
        logger.error(
            msg="Id moto invalido!"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de moto inválido")

    # Busca o moto no banco de dados
    moto = await db.motos.find_one({"_id": moto_object_id})

    if not moto:
        logger.info(
            msg="Moto não encontrada!"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Moto não encontrada!")

    # Exclui a moto usando o ObjectId
    await db.motos.delete_one({"_id": moto_object_id})

    # logger.info(
    #     msg=f"Moto excluída com sucesso! {moto["_id"]}"
    # )
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Moto excluida com sucesso!")
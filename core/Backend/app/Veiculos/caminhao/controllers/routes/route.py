from fastapi import APIRouter, UploadFile, File, Form, status, HTTPException, Request, Depends, Path
from core.Backend.app.Veiculos.caminhao.schemas.schemas import CaminhaoInfo, CaminhaoInfoResponse
from core.Backend.app.Veiculos.caminhao.models.models import Caminhao
from core.Backend.auth.auth import get_current_user
from core.Backend.app.config.config import logger
from core.Backend.app.database.database import db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from bson import ObjectId
from typing import List, Union
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
        response_description="Informaçoes do caminhao",
        description="Route para criar registro de caminhao",
        name="Criar registro para Caminhao"
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
    Imagem: UploadFile = File(..., title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo"),
    current_user: str = Depends(get_current_user)  # Garante que o usuário está autenticado
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

    # Salva o caminhao no MongoDB
    result = await db.caminhao.insert_one(caminhao.dict())  # Converte o objeto para um dict
    caminhao_db = await db.caminhao.find_one({"_id": result.inserted_id})  # Recupera o carro inserido do banco
    
    # Converte para o modelo CaminhaoInfo, incluindo o id
    return CaminhaoInfo.from_mongo(caminhao_db)


# rota GET
@router_caminhoes.get(
        path="/veiculos-pesados/",
        status_code=status.HTTP_200_OK,
        response_model=list[CaminhaoInfo],
        response_description="Informaçoes do caminhao",
        description="Route para pegar informacoes do caminhao",
        name="Pegar informacoes do Caminhao"
)
async def get_caminhao():
    caminhao_cursor = db.caminhao.find()
    caminhao = [CaminhaoInfo.from_mongo(caminhao) for caminhao in await caminhao_cursor.to_list(length=100)]
    
    if caminhao:
        logger.info(
            msg="Caminhoes sendo listados!"
        )
        return caminhao
    
    if not caminhao:
        logger.error(
            msg="Nenhum caminhao inserido!"
            )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum caminhao inserido!")



# Função para converter second_search para o tipo adequado
def convert_search_value(value: str, campo: str):
    try:
        # Tentando converter conforme o tipo do campo
        if campo in ["ano", "preco", "quilometragem", "portas", "lugares"]:
            return float(value) if "." in value else int(value)
        return value  # Para outros campos, mantemos como string
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Valor para '{campo}' é inválido.")


# Rota para buscar carros com parâmetros dinâmicos
@router_caminhoes.get(
        path="/veiculos-pesados/{first_params}/{second_params}",
        response_model=List[CaminhaoInfoResponse],
        #response_class=HTMLResponse,
        )
async def get_carros(
    #request: Request,
    first_params: str = Path(..., max_length=13, description="Campo a ser consultado no MongoDB" ,example="ano"),
    second_params: Union[str, int, float] = Path(..., description="Valor para filtrar o campo", example="2005"),

):
    # Validar se o campo é permitido
    campos_validos = [
        "marca", "modelo", "ano",
        "preco", "tipo", "cor",
        "quilometragem", "portas",
        "lugares", "combustivel",
        "descricao", "endereco"
    ]
    
    if first_params not in campos_validos:
        logger.error(
            msg=f"Campo '{first_params}' não é válido para consulta em {first_params}."
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Campo '{first_params}' não é válido para consulta.")
    
    # Converter o segundo parâmetro para o tipo correto antes da consulta
    converted_value = convert_search_value(second_params, first_params)
    
    # Consulta para pegar os itens com o campo first_query igual a second_search
    caminhao_cursor = db.caminhao.find({first_params: converted_value})
    
    # Usando to_list para pegar os resultados e modificar o _id
    caminhoes = []
    logger.info(
        msg="Parametros armazenados na lista para retorno"
    )
    async for caminhao in caminhao_cursor:
        del caminhao['_id']  # Remover o campo _id
        caminhoes.append(caminhao)
    
    # Se não encontrou nenhum carro, retornar um erro
    if not caminhoes:
        logger.info(
            msg="Nenhum caminhão encontrado com os parâmetros fornecidos."
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum caminhão encontrado com os parâmetros fornecidos.")
    
    return caminhoes  # Retornando a lista de carros
    # aqui conseque renderizar no frontend
    #return templates.TemplateResponse("index.html", {"request": request, "caminhoes": caminhoes})





@router_caminhoes.get(
    path="/veiculos-pesados/{caminhao_id}",
    status_code=status.HTTP_200_OK,
    response_model=CaminhaoInfo,
    response_description="Informações dos caminhao",
    description="Route para pegar informações do caminhao",
    name="Pegar informações do Caminhao"
)
async def get_carros(caminhao_id: str):
    try:
        # Tenta converter o caminhao_id para ObjectId, porque o MongoDB trabalha com objetos!
        caminhao_object_id = ObjectId(caminhao_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de caminhao inválido")

    # Busca o caminhao no banco de dados
    caminhao = await db.caminhao.find_one({"_id": caminhao_object_id})

    if not caminhao:
        logger.info(
            msg="Caminhao não encontrado!"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caminhao não encontrado!")
    
    logger.info(
        msg=f"Informações da caminhao!"
    )
    # Retorna o caminhao no formato adequado, com o id convertido
    return CaminhaoInfo.from_mongo(caminhao)


# Rota GET para renderizar o template HTML
@router_caminhoes.get(
        path="/veiculos-pesados/page/",
        status_code=status.HTTP_200_OK,
        response_description="Renderizaçao da pagina",
        description="Renderizacao de pagina",
        name="Renderizacao da pagina",
        response_class=HTMLResponse
)
async def read_root(request: Request):
    caminhao_cursor = db.caminhao.find()
    caminhao = [CaminhaoInfo.from_mongo(caminhao) for caminhao in await caminhao_cursor.to_list(length=100)]
    
    logger.info(
        msg="Pagina de veiculos pesados: caminhões!"
    )
    return templates.TemplateResponse("index.html", {"request": request, "carros": caminhao})


# Rota PUT para atualizar um caminhao
@router_caminhoes.put(
    path="/veiculos-pesados/{caminhao_id}",
    status_code=status.HTTP_200_OK,
    response_model=CaminhaoInfo,
    response_description="Informções atualizadas",
    description="Route update informações do Caminhao",
    name ="Atualizar informações do Caminhao"
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
    Imagem: UploadFile = File(None, title="Imagem do veiculo", alias="Imagem", description="Imagem do veiculo"),
    current_user: str = Depends(get_current_user)  # Garante que o usuário está autenticado
):

    try:
        # Tenta converter o caminhao_id para ObjectId, porque o MongoDB trabalha com objetos!
        caminhao_object_id = ObjectId(caminhao_id)
    except Exception as e:
        logger.error(
            msg="ID de caminhao inválido!"
        )
        raise HTTPException(status_code=400, detail="ID de caminhao inválido!")

    # Busca o caminhao no banco de dados
    caminhao = await db.caminhao.find_one({"_id": caminhao_object_id})

    if not caminhao:
        logger.info(
            msg="Caminhao não encontrado!"
        )
        raise HTTPException(status_code=404, detail="Caminhao não encontrado!")

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

    # Atualiza o caminhao no banco de dados
    await db.caminhao.update_one({"_id": caminhao_object_id}, {"$set": update_data})
    
    # Recupera o caminhao atualizado
    updated_caminhao = await db.caminhao.find_one({"_id": caminhao_object_id})
    
    logger.info(
        msg=f"Caminhao atualizado!"
    )

    # Retorna o caminhao atualizado como CaminhaoInfo
    return CaminhaoInfo.from_mongo(updated_caminhao)



# Rota DELETE para excluir um carro
@router_caminhoes.delete(
    path="/veiculos-pesados/{caminhao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Delete caminhao",
    description="Route delete caminhao",
    name="Delete Carro"
)
async def delete_carro(
    caminhao_id: str,
    current_user: str = Depends(get_current_user)  # Garante que o usuário está autenticado
    ):
    try:
        # Tenta converter caminhao_id para ObjectId, porque o MongoDB trabalha com objetos!
        carro_object_id = ObjectId(caminhao_id)
    except Exception as e:
        logger.error(
            msg="Id caminhao invalido!"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de caminhao inválido!")

    # Busca o caminhao no banco de dados
    caminhao = await db.caminhao.find_one({"_id": carro_object_id})

    if not caminhao:
        logger.info(
            msg="Caminhao não encontrado!"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caminhao não encontrado!")

    # Exclui o caminhao usando o ObjectId
    await db.caminhao.delete_one({"_id": carro_object_id})

    logger.info(
        msg=f"Caminhao excluído com sucesso!"
    )
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Caminhao excluido com sucesso!")
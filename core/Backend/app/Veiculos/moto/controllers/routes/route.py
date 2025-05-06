from fastapi import APIRouter, UploadFile, File, Form, status, Request, Depends, Path
from core.Backend.app.Veiculos.moto.schemas.schemas import MotosInfo, MotosInfoResponse
from core.Backend.app.services.services_moto import ServicesMoto
from core.Backend.auth.auth import get_current_user
from fastapi.responses import HTMLResponse
from typing import List, Union
from core.Backend.app.config.config import limiter


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
@limiter.limit("5/minute") # O ideal é 5
async def createBike(
    request: Request,
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
    # servico para registro da moto
    return await ServicesMoto.createBikeService(
        Marca, Modelo, Ano, Preco, Tipo, Disponivel,
        Quilometragem, Cor, Lugares, Combustivel, Descricao,
        Endereco, Imagem
    )


@route_motos.get(
    path="/veiculos-ultra-leves/",
    status_code=status.HTTP_200_OK,
    response_model=list[MotosInfo],
    response_description="Informaçoes da moto",
    description="Route para pegar informações da moto",
    name="Pegar informações do Moto"
)
@limiter.limit("40/minute")
async def getBikes(request: Request):
    # servico de listagem de todos os veiculos leves 'motos'
    return await ServicesMoto.getBikesService()


# Rota para buscar carros com parâmetros dinâmicos
@route_motos.get(
        path="/veiculos-ultra-leves/{first_params}/{second_params}",
        response_model=List[MotosInfoResponse],
        #response_class=HTMLResponse,
)
@limiter.limit("40/minute")
async def getBikesWithParams(
    request: Request,
    first_params: str = Path(..., max_length=13, description="Campo a ser consultado no MongoDB" ,example="ano"),
    second_params: Union[str, int, float] = Path(..., description="Valor para filtrar o campo", example="2005"),

):
    # servico para dados somente por parametros
    return await ServicesMoto.getBikesWithParamsService(first_params, second_params)



@route_motos.get(
    path="/veiculos-ultra-leves/{moto_id}",
    status_code=status.HTTP_200_OK,
    response_model=MotosInfo,
    response_description="Informaçoes da moto",
    description="Route para pegar informações da moto",
    name="Pegar informações da moto"
)
@limiter.limit("30/minute")
async def getBikeById(moto_id: str, request: Request):
    # servico para pegar moto por ID
    return await ServicesMoto.getBikeByIdService(moto_id)


# Rota GET para renderizar o template HTML
@route_motos.get(
        path="/veiculos-ultra-leves/page/",
        status_code=status.HTTP_200_OK,
        response_description="Informações da Moto",
        description="Route para renderizar pagina",
        name="Renderizar pagina",
        response_class=HTMLResponse
)
@limiter.limit("40/minute")
async def bikePage(request: Request):
    # servico para renderiza dados no HTML
    return await ServicesMoto.getBikePageService(request)



# Rota PUT para atualizar uma moto
@route_motos.put(
    path="/veiculos-ultra-leves/{moto_id}",
    status_code=status.HTTP_200_OK,
    response_model=MotosInfo,
    response_description="Informações do veiculo atualizadas",
    description="Route update information moto",
    name ="Atualizar infomações da moto"
)
@limiter.limit("5/minute") # O ideal é 5
async def updateBike(
    request: Request,
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
    # servico para update da moto
    return await ServicesMoto.updateBikeService(
        moto_id, Marca, Modelo, Ano, Preco, Tipo, Disponivel,
        Quilometragem, Cor, Lugares, Combustivel, Descricao,
        Endereco, Imagem
    )

# Rota DELETE para excluir uma moto
@route_motos.delete(
    path="/veiculos-ultra-leves/{moto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Moto deletada",
    description="Route delete moto",
    name="Deletar Moto"
)
@limiter.limit("10/minute") # O ideal é 5
async def deleteBike(
    request: Request,
    moto_id: str,
    current_user: str = Depends(get_current_user)  # Garante que o usuário está autenticado
):
    # servico de delete
    return await ServicesMoto.deleteBikeService(moto_id)
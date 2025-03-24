from fastapi import APIRouter, Path, UploadFile, File, Form, status, Request, Depends
from core.Backend.app.Veiculos.carros.schemas.schema import CarroInfo, CarroInfoResponse
from core.Backend.app.services.services_carro import ServiceCarros
from core.Backend.auth.auth import get_current_user
from core.Backend.app.config.config import logger
from core.Backend.app.database.database import db
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import List, Union



# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")



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
    # servico para realizar todo o processo de forma mais clean code
    return await ServiceCarros.create_car(
        Marca, Modelo, Ano, Preco, Disponivel,
        Tipo, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
    )


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

    # servico para retonar todos os carros
    return await ServiceCarros.get_all_cars()



# Rota para buscar carros com parâmetros dinâmicos
@router_carros.get(
        path="/veiculos-leves/{first_params}/{second_params}",
        response_model=List[CarroInfoResponse],
        #response_class=HTMLResponse,
        )
async def get_carros(
    #request: Request,
    first_params: str = Path(..., max_length=13, description="Campo que deseja requisitar" ,example="ano"),
    second_params: Union[str, int, float] = Path(..., description="Valor do campo para filtragem.", example="2005"),

):
    # servico para pegar informacoes com base em parametros
    return await ServiceCarros.get_car_with_parameters(first_params, second_params)

@router_carros.get(
    path="/veiculos-leves/{carro_id}",
    status_code=status.HTTP_200_OK,
    response_model=CarroInfo,
    response_description="Informações dos carros",
    description="Route para pegar informações do carro",
    name="Pegar informações do Carro"
)
async def get_carros(carro_id: str):
    # servico para pegar informacoes do carro
    return await ServiceCarros.get_car_ID(carro_id)


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
    # servico para update do carro
    return await ServiceCarros.update_car(
        carro_id, Marca, Modelo, Ano, Preco, Disponivel,
        Tipo, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
    )

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

    # servico para deletar carro
    return await ServiceCarros.delete_car(carro_id)
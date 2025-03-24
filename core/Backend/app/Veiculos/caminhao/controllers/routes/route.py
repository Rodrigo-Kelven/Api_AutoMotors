from fastapi import APIRouter, UploadFile, File, Form, status, Request, Depends, Path
from core.Backend.app.Veiculos.caminhao.schemas.schemas import CaminhaoInfo, CaminhaoInfoResponse
from core.Backend.app.services.services_caminhao import ServiceCaminhao
from core.Backend.auth.auth import get_current_user
from fastapi.responses import HTMLResponse
from typing import List, Union


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
    # servico de registro de caminhao
    return await ServiceCaminhao.create_caminhao(
        Marca, Modelo, Ano, Preco, Disponivel, Tipo,
        Cap_Maxima, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
    )


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
    # servico para retornar todos os caminhos do banco de dados
    return await ServiceCaminhao.get_all_caminhoes()


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
    # servico retorna dados compativel com os parametros
    return await ServiceCaminhao.get_caminhao_with_params(first_params ,second_params)


@router_caminhoes.get(
    path="/veiculos-pesados/{caminhao_id}",
    status_code=status.HTTP_200_OK,
    response_model=CaminhaoInfo,
    response_description="Informações dos caminhao",
    description="Route para pegar informações do caminhao",
    name="Pegar informações do Caminhao"
)
async def get_carros(caminhao_id: str):
    # servico para retornar dados com base o ID do caminhao
    return await ServiceCaminhao.get_caminhao_ID(caminhao_id)


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
    # servico para renderiza as informacoes no HTML
    return await ServiceCaminhao.render_HTML(request)

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
    # servico para update somente com o ID do caminhao 
    return await ServiceCaminhao.update_caminhao(
        caminhao_id, Marca, Modelo, Ano, Preco, Disponivel, Tipo,
        Cap_Maxima, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
    )



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
    # servico para delete de caminhao somente com ID
    return await ServiceCaminhao.delete_caminhao(caminhao_id)
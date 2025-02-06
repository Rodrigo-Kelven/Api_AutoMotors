from fastapi import APIRouter
import logging
from enum import Enum
from app.Veiculos.carros.controllers.routes.route import router
from app.Veiculos.caminhao.controllers.routes.route import router_caminhoes
from app.Veiculos.moto.controllers.routes.route import route_motos

class Tags(Enum):
    carros = "Veiculos Leves"
    caminhoes = "Veiculos Pesados"
    motos = "Veiculos Ultra Leves"

app = APIRouter()

def all_routes(app):
    app.include_router(router, tags=[Tags.carros], prefix="/api-veiculos/categoria")
    app.include_router(router_caminhoes, tags=[Tags.caminhoes], prefix="/api-veiculos/categoria")
    app.include_router(route_motos, tags=[Tags.motos], prefix="/api-veiculos/categoria")


"""
def include_router(
    router: APIRouter,
    *,
    prefix: str = "",
    tags: List[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    responses: Dict[int | str, Dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    include_in_schema: bool = True,
    default_response_class: type[Response] = Default(JSONResponse),
    callbacks: List[BaseRoute] | None = None,
    generate_unique_id_function: (APIRoute) -> str = Default(generate_unique_id)
) -> None
"""

def adicionar_route_documentacao(app):
    # Configuração do logger
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Adicione um evento de inicialização para logar a URL
    @app.on_event("startup")
    async def startup_event():
        logger.info("Aplicação iniciada. Acesse a documentação em: http://0.0.0.0:8000/docs")

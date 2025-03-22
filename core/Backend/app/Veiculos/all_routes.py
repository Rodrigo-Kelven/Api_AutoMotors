from fastapi import APIRouter
from enum import Enum
from core.Backend.app.Veiculos.carros.controllers.routes.route import router_carros
from core.Backend.app.Veiculos.caminhao.controllers.routes.route import router_caminhoes
from core.Backend.app.Veiculos.moto.controllers.routes.route import route_motos
from core.Backend.auth.routes.routes import routes_auth_auten

# tags 
class Tags(Enum):
    carros = "Veiculos Leves"
    caminhoes = "Veiculos Pesados"
    motos = "Veiculos Ultra Leves"
    auth_auten = "Autenticação e Autorização"

# prefixp da api
class Prefix(Enum):
    api = "/api-v2/veiculos/categoria"
    api_auth = "/api-v2/veiculos/auth"



app = APIRouter()

def all_routes(app):
    app.include_router(router_carros, tags=[Tags.carros], prefix=Prefix.api.value)
    app.include_router(router_caminhoes, tags=[Tags.caminhoes], prefix=Prefix.api.value)
    app.include_router(route_motos, tags=[Tags.motos], prefix=Prefix.api.value)
    app.include_router(routes_auth_auten, tags=[Tags.auth_auten], prefix=Prefix.api_auth.value)


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
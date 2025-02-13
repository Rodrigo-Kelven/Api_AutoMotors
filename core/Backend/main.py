from fastapi import FastAPI
from core.Backend.app.database.database import Base, engine_automotors_users
from core.Backend.app.config.config import *
from fastapi.staticfiles import StaticFiles
from core.Backend.app.Veiculos.all_routes import all_routes

# chama o arquivo de configuraçao
app = FastAPI()
# Monta o diretório de uploads para servir imagens
# esta parte é crucial, se não for montado aqui, as imagens nao irão renderizar
# pois o fastapi vai entender que o diretorio não foi montado
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.add_middleware(LogRequestMiddleware)

# cria as tabelas ao iniciar a aplicação, sim, deve estar aqui
Base.metadata.create_all(bind=engine_automotors_users)

# chama todas as rotas para o app FastAPI
all_routes(app)

# Adiciona o middleware ao FastAPI, verifica requests e responses
app.add_middleware(LogRequestMiddleware)


# funcao para configuracao do middleware
app.middleware("http")(rate_limit_middleware)

# adicionar CORS para implementacao com o frontend
#cors(app)


@app.get("/")
def read_root():
    logger.info(
        msg="Endpoint raiz acessado"
        )
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    logger.debug(f"Item solicitado: {item_id}")
    if item_id > 10:
        logger.error(
            msg="ID do item é muito alto",
            stacklevel=1
            )
    return {"item_id": item_id}


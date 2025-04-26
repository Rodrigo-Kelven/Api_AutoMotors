from fastapi import FastAPI
from core.Backend.app.database.database import Base_auth, engine_auth
from core.Backend.app.config.config import LogRequestMiddleware, rate_limit_middleware, config_CORS
from fastapi.staticfiles import StaticFiles
from core.Backend.app.Veiculos.all_routes import all_routes



app = FastAPI(
    debug=True,
    title="API Auto Motors with FastAPI",
    summary="Este projeto é uma API RESTful para um sistema de uma"
    "concéssionária. Um simples projeto baseado num ecommerce construido em FastAPI."
    "A ideia e criar um pequeno sistema e usa-lo como base em outros projetos."
    "Ele permite que os usuários realizem operações como criar, ler, atualizar e excluir produtos, além de gerenciar pedidos e usuários.",
    version="2.1.10"
)

# Monta o diretório de uploads para servir imagens
# esta parte é crucial, se não for montado aqui, as imagens nao irão renderizar
# pois o fastapi vai entender que o diretorio não foi montado
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.add_middleware(LogRequestMiddleware)


@app.on_event("startup")
async def startup_event():
    try:
        # Criação das tabelas no banco de dados de usuários
        async with engine_auth.begin() as conn:
            await conn.run_sync(Base_auth.metadata.create_all)

        # chama todas as rotas para o app FastAPI
        all_routes(app)
        
        # Adiciona o middleware ao FastAPI, verifica requests e responses
        app.add_middleware(LogRequestMiddleware)

        # funcao para configuracao do middleware
        app.middleware("http")(rate_limit_middleware)

        # adicionar CORS para implementacao com o frontend
        config_CORS(app)

    except Exception as e:
        return e

@app.on_event("shutdown")
async def shutdown_event():
    await engine_auth.dispose()

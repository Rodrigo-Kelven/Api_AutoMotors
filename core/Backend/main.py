from fastapi import FastAPI
from app.database.database import Base, engine
from fastapi.staticfiles import StaticFiles
from app.controllers.routes.route import router


# chama o arquivo de configuraçao
app = FastAPI()
# Monta o diretório de uploads para servir imagens
# esta parte é crucial, se não for montado aqui, as imagens nao irão renderizar
# pois o fastapi vai entender que o diretorio não foi montado
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# cria as tabelas ao iniciar a aplicação, sim, deve estar aqui
Base.metadata.create_all(bind=engine)

# Inclui as rotas
app.include_router(router)

# configuração
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
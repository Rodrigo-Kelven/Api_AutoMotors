from fastapi import FastAPI
from app.database.database import Base, engine_automotors_veiculos
from app.config.config import *
from fastapi.staticfiles import StaticFiles
from app.Veiculos.all_routes import all_routes


# chama o arquivo de configuraçao
app = FastAPI()
# Monta o diretório de uploads para servir imagens
# esta parte é crucial, se não for montado aqui, as imagens nao irão renderizar
# pois o fastapi vai entender que o diretorio não foi montado
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# cria as tabelas ao iniciar a aplicação, sim, deve estar aqui
Base.metadata.create_all(bind=engine_automotors_veiculos)

all_routes(app)

# Adiciona o middleware ao FastAPI, verifica requests e responses
app.add_middleware(LogRequestMiddleware)

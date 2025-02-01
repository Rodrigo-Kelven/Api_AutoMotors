from fastapi import FastAPI
from app.database.database import Base, engine
from app.controllers.all_routes import all_routes


# Criação das tabelas
Base.metadata.create_all(bind=engine)

# chama todas as rotas de uma única vez
app = FastAPI()
all_routes(app)
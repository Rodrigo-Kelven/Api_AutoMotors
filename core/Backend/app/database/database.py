from sqlalchemy.ext.declarative import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from core.Backend.app.config.config import logger
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import redis
import os

# Conexão com o MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")  # Substitua com sua URL do MongoDB
db = client.veiculos  # O banco de dados para veículos em MongoDB

# Conexão com o Redis
redis_client_users = redis.Redis(host='localhost', port=6379, db=1)  # Conectando ao banco de dados 0

# Inicializa a conexão com o Redis
redis_client_config_rate_limit_middleware = redis.Redis(host='localhost', port=6379, db=0)  # Conectando ao banco de dados 0

# Definindo o caminho do banco de dados SQLite
db_users_path = "./databases/DB_users/db_users/users_users.db" # -> banco de dados de usuarios


# Verificar se a pasta existe, caso contrário, criar
db_directory_users = os.path.dirname(db_users_path)

# verifica se o diretorio existe
if not os.path.exists(db_directory_users):
    os.makedirs(db_directory_users)  # Cria o diretório se não existir

# URL do banco de dados SQLite dentro da pasta 'databases'
SQLALCHEMY_DATABASE_api_automotors_users_URL = f"sqlite:///{db_users_path}"

# Criando o engine para conectar ao banco de dados, aqui esta criando uma ponte para ai sim conectar a aplicacao ao DB e executar as operacoes
engine_automotors_users = create_engine(SQLALCHEMY_DATABASE_api_automotors_users_URL, connect_args={"check_same_thread": False})


# Testando a conexão, db users
try:
    with engine_automotors_users.connect():
        logger.info(
            msg=f"Conexão bem-sucedida!"
        )
except Exception as e:
    logger.info(
        msg=f"Error de conexão, status: {e}!"
    )

# Sessão para interagir com o banco de dados, essa sesao é muito importante, ela é responsavel por 'manter uma sessao'
SessionLocal_users = sessionmaker(autocommit=False, autoflush=False, bind=engine_automotors_users)

# Base para definir os modelos
Base = declarative_base()

# Dependência para obter a sessão do banco de dados de usuários
def get_db_users():
    db_users = SessionLocal_users()
    try:
        yield db_users
    finally:
        db_users.close()
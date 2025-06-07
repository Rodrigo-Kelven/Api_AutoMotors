from sqlalchemy.ext.declarative import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.orm import sessionmaker
import redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


# Conexão com o MongoDB
client = AsyncIOMotorClient("mongodb://mongodb:27017")  # Substitua com sua URL do MongoDB
db_leves = client["veiculos_leves"]  # O banco de dados para veículos leve em MongoDB
db_pesados = client["veiculos_pesados"] # O banco de dados para veículos pesados em MongoDB
db_ultra_leves = client["veiculos_ultra_leves"] # O banco de dados para veículos ultra leves em MongoDB

# Conexão com o Redis
redis_client_users = redis.Redis(host='redis-container', port=6379, db=1)  # Conectando ao banco de dados 1

# Inicializa a conexão com o Redis
redis_client_config_rate_limit_middleware = redis.Redis(host='redis-container', port=6379, db=0)  # Conectando ao banco de dados 0

# URL do banco de dados PostgreSQL
DATABASE_URL = "postgresql+asyncpg://user:password@api_automotors-db-1:5432/fastapi_db"


# Criação do engine assíncrono
engine_auth = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=20,  # Tamanho do pool de conexões
    max_overflow=0,  # Conexões adicionais permitidas
    pool_pre_ping=True, # Verifica se a conexão está ativa antes de se conectar
)

# Criação do gerenciador de sessões assíncronas
AsyncSessionLocal = sessionmaker(bind=engine_auth, class_=AsyncSession, expire_on_commit=False)


# Criação da base para os modelos
Base_auth = declarative_base()

# Função para obter a sessão de banco de dados
async def get_user_db():
    async with AsyncSessionLocal() as session:
        yield session
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


# Configurações e chave secreta

# Use este comando para gerar sua chave caso queira: openssl rand -hex 64
# sim esta chave é uma chave inutilizavel
# NÃO PODE SUBIR SUAS CHAVES PRIVADAS PARA O REPOSITORIO!!
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256" # algoritmo para a criptografia dos passwords
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # tempo de expiracao do token

# Inicialização de FastAPI e outras configurações
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# O usuário digita o username e a senha no frontend e aperta Enter.
# O frontend (rodando no browser do usuário) manda o username e a senha para uma URL específica na sua API (declarada com tokenUrl="token").
# Esse parâmetro contém a URL que o client (o frontend rodando no browser do usuário) vai usar para mandar o username e senha para obter um token
# se mudar a rota de login, nao esqueca de mudar aqui, porque o fastapi simplesmente nao AVISA PORRA
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api-v2/veiculos/auten_auth/login") 
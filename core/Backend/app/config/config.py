from core.Backend.app.database.database import redis_client_config_rate_limit_middleware
from starlette.middleware.base import BaseHTTPMiddleware
from logging.handlers import RotatingFileHandler
from fastapi import Request, HTTPException
from starlette.requests import Request
from starlette.responses import Response
import logging
import time
import os
from slowapi import Limiter
from slowapi.util import get_remote_address


logging.basicConfig(level=logging.INFO)

class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):

        # Loga os detalhes da requisição
        logging.info(f"Requisição recebida: {request.method} {request.url}")
        start_time = time.time()  # Marcar o tempo de início
        process_time = time.time() - start_time  # Calcula o tempo de processamento
        # Chama o próximo middleware ou rota
        response: Response = await call_next(request)  # Chama a próxima parte da solicitação
        response.headers['X-Process-Time'] = str(process_time)  # Adiciona o tempo de processamento no cabeçalho da resposta

        # Loga os detalhes da resposta
        logging.info(msg=f"Resposta enviada com status {response.status_code}")
        
        return response
    

# Constantes para o rate limiting
RATE_LIMIT = 200  # Número máximo de requisições por minuto
TIME_WINDOW = 60  # Janela de tempo em segundos (1 minuto)


# Middleware para controle de taxa
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = int(time.time())

    # Obtém a contagem atual e o timestamp do Redis
    db_logger.info(
        msg="Usando Redis."
    )
    print("##################")
    print("Usando Redis")
    print("##################")
    count = redis_client_config_rate_limit_middleware.get(f"rate_limit:{client_ip}:count")
    timestamp = redis_client_config_rate_limit_middleware.get(f"rate_limit:{client_ip}:timestamp")

    if count is None or timestamp is None:
        count = 0
        timestamp = now
    else:
        count = int(count)
        timestamp = int(timestamp)


    count = int(count)

    # Reseta contagem se a janela de tempo tiver expirado
    if now - int(timestamp) > TIME_WINDOW:
        count = 0
        timestamp = now
        redis_client_config_rate_limit_middleware.set(f"rate_limit:{client_ip}:count", count)
        redis_client_config_rate_limit_middleware.set(f"rate_limit:{client_ip}:timestamp", timestamp)
        #redis_client_config_rate_limit_middleware.expire(f"rate_limit:{client_ip}:count", TIME_WINDOW)
        # Removi a linha de expiração do timestamp
        # Neste caso, o timestamp continuará existindo no Redis, mas ele será sobrescrito quando o contador for zerado novamente, então não há problema em não expirá-lo.


    print(f"Count: {count}, Rate Limit: {RATE_LIMIT}, Now: {now}, Timestamp: {timestamp}")

    # Verifica se o limite foi atingido
    if count >= RATE_LIMIT:
        remaining_time = TIME_WINDOW - (now - int(timestamp))
        headers = {
            "X-RateLimit-Limit": str(RATE_LIMIT),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(remaining_time)
        }
        raise HTTPException(status_code=429, detail="Too many requests", headers=headers)

    # Incrementa a contagem de requisições
    count += 1
    redis_client_config_rate_limit_middleware.set(f"rate_limit:{client_ip}:count", count)

    headers = {
        "X-RateLimit-Limit": str(RATE_LIMIT),
        "X-RateLimit-Remaining": str(RATE_LIMIT - count),
        "X-RateLimit-Reset": str(TIME_WINDOW - (now - int(timestamp)))
    }

    # Chama o próximo middleware ou rota
    response = await call_next(request)
    response.headers.update(headers)
    return response
"""
# O código define um middleware que intercepta todas as requisições HTTP1.
# RATE_LIMIT define o número máximo de requisições permitidas por minuto1.
# TIME_WINDOW define a janela de tempo em segundos (neste caso, 1 minuto)1.
# request_counts é um dicionário que rastreia o número de requisições por endereço IP1.
# O middleware verifica se o endereço IP do cliente já está no dicionário request_counts. Se não estiver, ele adiciona o endereço IP com uma contagem inicial de 0 e o timestamp atual1.
# Se o tempo desde a primeira requisição do cliente for maior que TIME_WINDOW, a contagem é resetada1.
# Se o número de requisições exceder o RATE_LIMIT, uma exceção HTTPException é levantada com o código de status 429 (Too Many Requests)1.
# Os cabeçalhos X-RateLimit-Limit, X-RateLimit-Remaining e X-RateLimit-Reset são adicionados à resposta para informar o cliente sobre o limite de requisições1.
"""


# caso precise de mais configuracao, documente e especifique porque
def config_CORS(app):
    from fastapi.middleware.cors import CORSMiddleware

    origins = [
        "http://localhost.tiangolo.com",
        "https://localhost.tiangolo.com",
        "http://localhost:5173/", # react
        "http://localhost:8080",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["X-Custom-Header"],
        max_age=3600,
    )


"""
### Resumo visual
### Nível configurado	Logs que ele aceita
-----------------------------------------------
* DEBUG	    DEBUG, INFO, WARNING, ERROR, CRITICAL
* INFO	    INFO, WARNING, ERROR, CRITICAL
* WARNING	WARNING, ERROR, CRITICAL
* ERROR	    ERROR, CRITICAL
* CRITICAL	CRITICAL
"""



os.makedirs("logs", exist_ok=True)
# Formato padrão
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def setup_logger(name, log_file, level=logging.INFO):
    """Cria e retorna um logger com arquivo próprio."""
    handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False  # Evita que os logs se repitam no console

    return logger

# Loggers separados
app_logger = setup_logger("app_logger", "logs/app.log", logging.INFO)
auth_logger = setup_logger("auth_logger", "logs/auth.log", logging.INFO)
#db_logger = setup_logger("db_logger", "logs/db.log", logging.ERROR)
db_logger = setup_logger("db_logger", "logs/db.log", logging.INFO)
car_logger = setup_logger("car_logger", "logs/car.log", logging.INFO)
truck_logger = setup_logger("truck_logger", "logs/truck.log", logging.INFO)
bike_logger = setup_logger("bike_logger", "logs/bike.log", logging.INFO)



# decoracor do rate limit de auth
limiter = Limiter(
    key_func=get_remote_address,
    enabled=True,
    )
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.responses import JSONResponse
import traceback
import logging
from fastapi import Request, HTTPException
import time


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
        logging.info(f"Resposta enviada com status {response.status_code}")
        
        return response
    


RATE_LIMIT = 65 # Número máximo de requisições por minuto
TIME_WINDOW = 60  # Janela de tempo em segundos (1 minuto)
request_counts = {}  # Dicionário para rastrear o número de requisições por IP


# middleware
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    now = int(time.time())

    if client_ip not in request_counts:
        request_counts[client_ip] = {"count": 0, "timestamp": now}

    if now - request_counts[client_ip]["timestamp"] > TIME_WINDOW:
        request_counts[client_ip] = {"count": 0, "timestamp": now}

    if request_counts[client_ip]["count"] >= RATE_LIMIT:
        remaining_time = TIME_WINDOW - (now - request_counts[client_ip]["timestamp"])
        headers = {
            "X-RateLimit-Limit": str(RATE_LIMIT),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(remaining_time)
        }
        raise HTTPException(status_code=429, detail="Too many requests", headers=headers)

    request_counts[client_ip]["count"] += 1
    headers = {
        "X-RateLimit-Limit": str(RATE_LIMIT),
        "X-RateLimit-Remaining": str(RATE_LIMIT - request_counts[client_ip]["count"]),
        "X-RateLimit-Reset": str(TIME_WINDOW - (now - request_counts[client_ip]["timestamp"]))
    }
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


# atualizar e confighurar
def cors(app):
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
        allow_methods=["*"],
        allow_headers=["*"],
    )

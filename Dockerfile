# Usar uma imagem Python mais leve
FROM python:3.11-slim

# Define o diretório de trabalho no container
WORKDIR /src

# Copia todos os arquivos para o diretório de trabalho
COPY . .

# Instala as dependências necessárias
RUN pip install  -r core/Backend/requirements.txt

# Expondo a porta 8000 para o host
EXPOSE 8000

# Executa o comando para iniciar o servidor Uvicorn
CMD ["uvicorn", "core.Backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["fastapi", "dev", "main.py", "--reload", "--port", "8000"]

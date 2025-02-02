# usar uma imagem mais leve
FROM python:3.11
# diretorio de trabalho
WORKDIR /app
# copy tudo para o diretorio de trabalho
COPY . .
# instala as dependeicas nescessarias
RUN pip install -r requirements.txt
# expoe a porta do container para maquina
EXPOSE 8000
# executa este comando ao iniciar o container
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
#!/bin/bash

# cria a imagem
docker build -t backend-api -f Backend.Dockerfile .
# cria o container
docker run -it --name back-api -p 8000:8000 backend-api
#cria o container e deleta ao para-lo
# docker run -it --rm --name back-api -p 8000:8000 backend-api

#!/bin/bash

# rodar container com banco de dados NosQL para os veiculos
docker run --name mongodb -d -p 27017:27017 -v ~/mongodb-data:/data/db mongo
# rodar container com banco de dados SQL para usuários
docker run --name redis-container -d -p 6379:6379 redis
fastapi dev main.py --reload --port 8000

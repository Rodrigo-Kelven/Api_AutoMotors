#!/bin/bash

docker run --name mongodb -d -p 27017:27017 -v ~/mongodb-data:/data/db mongo
docker run --name redis-container -d -p 6379:6379 redis
fastapi dev main.py --reload --port 8000

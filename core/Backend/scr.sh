#!/bin/bash

docker run --name mongodb -d -p 27017:27017 -v ~/mongodb-data:/data/db mongo
fastapi dev main.py --reload --port 8000

from fastapi import APIRouter
from app.controllers.routes.route import route

app = APIRouter()

def all_routes(app):
    app.include_router(route)
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database.database import SessionLocal
from app.models.models import Carro
import os

route = APIRouter()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@route.post("/carros/")
async def create_carro(
    modelo: str = Form(...),
    ano: int = Form(...),
    preco: float = Form(...),
    file: UploadFile = File(...)
):
    file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
    with open(file_location, "wb") as file_object:
        file_object.write(await file.read())
    
    db = SessionLocal()
    carro = Carro(modelo=modelo, ano=ano, preco=preco, imagem=file_location)
    db.add(carro)
    db.commit()
    db.refresh(carro)
    db.close()
    
    return carro

@route.get("/carros/")
async def get_carros():
    db = SessionLocal()
    carros = db.query(Carro).all()
    db.close()
    return carros

@route.get("/", response_class=HTMLResponse)
async def read_root():
    db = SessionLocal()
    carros = db.query(Carro).all()
    db.close()
    return templates.TemplateResponse("index.html", {"request": {}, "carros": carros})

route.mount("/uploads", StaticFiles(directory=UPLOAD_DIRECTORY), name="uploads")


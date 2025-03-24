from core.Backend.app.Veiculos.carros.schemas.schema import CarroInfo
from core.Backend.app.Veiculos.carros.models.models import Carro
from core.Backend.app.database.database import db
from core.Backend.app.config.config import logger
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, status
from bson import ObjectId
import os


# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# Verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


# servico somente de carros
class ServiceCarros:


    @staticmethod
    async def create_car(
        Marca, Modelo, Ano, Preco, Disponivel,
        Tipo, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
        ):
        # Salva a imagem no diretório uploads
        file_location = os.path.join(UPLOAD_DIRECTORY, Imagem.filename)
        with open(file_location, "wb") as file_object:
            file_object.write(await Imagem.read())
        
        carro = Carro(
            marca=Marca,
            modelo=Modelo,
            ano=Ano,
            preco=Preco,
            disponivel=Disponivel,
            tipo=Tipo,
            quilometragem=Quilometragem,
            cor=Cor,
            portas=Portas,
            lugares=Lugares,
            combustivel=Combustivel,
            descricao=Descricao,
            endereco=Endereco,
            imagem="uploads/" + Imagem.filename,
        )


        # Salva o carro no MongoDB
        result = await db.carros.insert_one(carro.dict())  # Converte o objeto para um dict
        carro_db = await db.carros.find_one({"_id": result.inserted_id})  # Recupera o carro inserido do banco


        # logs
        logger.info(
            msg=f"Carro inserido! "
        )

        # Converte para o modelo CarroInfo, incluindo o id
        return CarroInfo.from_mongo(carro_db)


    @staticmethod
    async def get_all_cars():

        carros_cursor = db.carros.find()
        carros = [CarroInfo.from_mongo(carro) for carro in await carros_cursor.to_list(length=100)]
        
        if carros:
            logger.info(
                msg="Carros sendo listados!"
            )
            return carros
        
        if not carros:
            logger.info(
                msg="Nenhum carro inserido!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum carro inserido!")
        
    
    @staticmethod
    # Função para converter second_search para o tipo adequado
    def convert_search_value(value: str, campo: str):
        try:
            # Tentando converter conforme o tipo do campo
            if campo in ["ano", "preco", "quilometragem", "portas", "lugares"]:
                return float(value) if "." in value else int(value)
            return value  # Para outros campos, mantemos como string
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Valor para '{campo}' é inválido.")
        
    
    @staticmethod
    async def get_car_with_parameters(first_params, second_params):
        # Validar se o campo é permitido
        campos_validos = [
            "marca", "modelo", "ano",
            "preco", "tipo", "cor",
            "quilometragem", "portas",
            "lugares", "combustivel",
            "descricao", "endereco", "categoria"
        ]
        
        if first_params not in campos_validos:
            logger.error(
                msg=f"Campo '{first_params}' não é válido para consulta em {first_params}."
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Campo '{first_params}' não é válido para consulta.")
        
        # Converter o segundo parâmetro para o tipo correto antes da consulta
        converted_value = ServiceCarros.convert_search_value(second_params, first_params)
        
        # Consulta para pegar os itens com o campo first_query igual a second_search
        carros_cursor = db.carros.find({first_params: converted_value})
        
        # Usando to_list para pegar os resultados e modificar o _id
        carros = []
        logger.info(
            msg="Parametros armazenados na lista para retorno"
        )
        async for carro in carros_cursor:
            del carro['_id']  # Remover o campo _id
            carros.append(carro)
        
        # Se não encontrou nenhum carro, retornar um erro
        if not carros:
            logger.info(
                msg="Nenhum carro encontrado com os parâmetros fornecidos."
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum carro encontrado com os parâmetros fornecidos.")
        
        return carros  # Retornando a lista de carros
        # aqui conseque renderizar no frontend
        #return templates.TemplateResponse("index.html", {"request": request, "carros": carros})

    
    @staticmethod
    async def get_car_ID(carro_id):
        try:
            # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
            carro_object_id = ObjectId(carro_id)

        except Exception as e:
            logger.error(
                msg="ID de carro inválido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de carro inválido!")

        # Busca o carro no banco de dados
        carro = await db.carros.find_one({"_id": carro_object_id})

        if not carro:
            logger.error(
                msg="Carro não encontrado!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado!")
        
        # logs
        logger.info(
            msg=f"Informações do carro"
        )

        # Retorna o carro no formato adequado, com o id convertido
        return CarroInfo.from_mongo(carro)
    

    @staticmethod
    async def render_HTML(request):
        carros_cursor = db.carros.find()
        carros = [CarroInfo.from_mongo(carro) for carro in await carros_cursor.to_list(length=100)]

        logger.info(
            msg="Pagina de veiculos leves: carros!"
        )
        return templates.TemplateResponse("index.html", {"request": request, "carros": carros})


    
    @staticmethod
    async def update_car(
        carro_id, Marca, Modelo, Ano, Preco, Disponivel,
        Tipo, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
        ):
        try:
            # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
            carro_object_id = ObjectId(carro_id)
        except Exception as e:
            logger.error(
                msg="ID de carro inválido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de carro inválido!")

        # Busca o carro no banco de dados
        carro = await db.carros.find_one({"_id": carro_object_id})

        if not carro:
            logger.error(
                msg="Carro não encontrado!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado")

        update_data = {
            "marca": Marca,
            "modelo": Modelo,
            "ano": Ano,
            "preco": Preco,
            "disponivel": Disponivel,
            "tipo": Tipo,
            "quilometragem": Quilometragem,
            "cor": Cor,
            "portas": Portas,
            "lugares": Lugares,
            "combustivel": Combustivel,
            "descricao": Descricao,
            "endereco": Endereco,
        }

        if Imagem:
            file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
            with open(file_location, "wb") as file_object:
                file_object.write(await Imagem.read())
            update_data["imagem"] = file_location

        # Atualiza o carro no banco de dados
        await db.carros.update_one({"_id": carro_object_id}, {"$set": update_data})
        
        # Recupera o carro atualizado
        updated_carro = await db.carros.find_one({"_id": carro_object_id})

        # logs
        logger.info(
            msg=f"Carro atualizado!"
        )
        
        # Retorna o carro atualizado como CarroInfo
        return CarroInfo.from_mongo(updated_carro)
    
    @staticmethod
    async def delete_car(carro_id):
        try:
            # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
            carro_object_id = ObjectId(carro_id)
        except Exception as e:
            logger.error(
                msg="ID de carro inválido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de carro inválido!")

        # Busca o carro no banco de dados
        carro = await db.carros.find_one({"_id": carro_object_id})

        if not carro:
            logger.error(
                msg="Carro não encontrado!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado!")

        # Exclui o carro usando o ObjectId
        await db.carros.delete_one({"_id": carro_object_id})

        # logs
        logger.info(
            msg=f"Carro deletado!"
        )

        return {"detail": "Carro excluído com sucesso"}
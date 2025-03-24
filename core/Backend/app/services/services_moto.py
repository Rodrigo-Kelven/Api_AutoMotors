import os
from core.Backend.app.Veiculos.moto.models.models import Motos
from core.Backend.app.Veiculos.moto.schemas.schemas import MotosInfo
from core.Backend.app.database.database import db
from fastapi import HTTPException, status
from core.Backend.app.config.config import logger
from bson import ObjectId


# verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)



class ServicesMoto:

    @staticmethod
    async def create_moto(
        Marca, Modelo, Ano, Preco, Tipo, Disponivel,
        Quilometragem, Cor, Lugares, Combustivel, Descricao,
        Endereco, Imagem
    ):
        file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
        with open(file_location, "wb") as file_object:
            file_object.write(await Imagem.read())
        
        moto = Motos(
            marca=Marca,
            modelo=Modelo,
            ano=Ano,
            preco=Preco,
            tipo=Tipo,
            disponivel=Disponivel,
            quilometragem=Quilometragem,
            cor=Cor,
            lugares=Lugares,
            combustivel=Combustivel,
            descricao=Descricao,
            endereco=Endereco,
            imagem=file_location
        )

        # Salva o moto no MongoDB
        result = await db.motos.insert_one(moto.dict())  # Converte o objeto para um dict
        moto_db = await db.motos.find_one({"_id": result.inserted_id})  # Recupera o moto inserido do banco
        
        # Converte para o modelo MotoInfo, incluindo o id
        return MotosInfo.from_mongo(moto_db)
    
    @staticmethod
    async def get_all_motos():
        motos_cursor = db.motos.find()
        motos = [MotosInfo.from_mongo(moto) for moto in await motos_cursor.to_list(length=100)]

        if motos:
            logger.info(
                msg="Motos sendo listadas!"
            )
            return motos
        
        if not motos:
            logger.error(
                msg="Nenhuma moto inserida!"
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma moto inserido!")
        
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
    async def get_with_params(first_params, second_params):
        # Validar se o campo é permitido
        campos_validos = [
            "marca", "modelo", "ano",
            "preco", "tipo", "cor",
            "quilometragem", "lugares",
            "combustivel", "descricao",
            "endereco", "categoria"
        ]
        
        if first_params not in campos_validos:
            logger.error(
                msg=f"Campo '{first_params}' não é válido para consulta em {first_params}."
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Campo '{first_params}' não é válido para consulta.")
        
        # Converter o segundo parâmetro para o tipo correto antes da consulta
        converted_value = ServicesMoto.convert_search_value(second_params, first_params)
        
        # Consulta para pegar os itens com o campo first_query igual a second_search
        motos_cursor = db.motos.find({first_params: converted_value})
        
        # Usando to_list para pegar os resultados e modificar o _id
        motos = []
        logger.info(
            msg="Parametros armazenados na lista para retorno"
        )
        async for moto in motos_cursor:
            del moto['_id']  # Remover o campo _id
            motos.append(moto)
        
        # Se não encontrou nenhum carro, retornar um erro
        if not motos:
            logger.info(
                msg="Nenhuma moto encontrada com os parâmetros fornecidos."
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma moto encontrada com os parâmetros fornecidos.")
        
        return motos  # Retornando a lista de carros
        # aqui conseque renderizar no frontend
        #return templates.TemplateResponse("index.html", {"request": request, "motos": motos})

    @staticmethod
    async def get_moto_ID(moto_id):
        try:
            # Tenta converter a moto_id para ObjectId, porque o MongoDB trabalha com objetos!
            moto_object_id = ObjectId(moto_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de moto inválido")

        # Busca a moto no banco de dados
        moto = await db.motos.find_one({"_id": moto_object_id})

        if not moto:
            logger.info(
                msg="Moto não encontrada!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moto não encontrada")
        
        logger.info(
            msg=f"Informações da moto!"
        )
        
        # Retorna a moto no formato adequado, com o id convertido
        return MotosInfo.from_mongo(moto)
    

    @staticmethod
    async def update_moto(
        moto_id, Marca, Modelo, Ano, Preco, Tipo, Disponivel,
        Quilometragem, Cor, Lugares, Combustivel, Descricao,
        Endereco, Imagem
    ):
        try:
            # Tenta converter a moto_id para ObjectId, porque o MongoDB trabalha com objetos!
            moto_object_id = ObjectId(moto_id)
        except Exception as e:
            logger.error(
                msg="Id moto invalido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de moto inválido")

        # Busca a moto no banco de dados
        moto = await db.motos.find_one({"_id": moto_object_id})

        if not moto:
            logger.error(
                msg="Moto nao encontrada"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moto não encontrada!")

        update_data = {
            "marca": Marca,
            "modelo": Modelo,
            "ano": Ano,
            "preco": Preco,
            "disponivel": Disponivel,
            "tipo": Tipo,
            "quilometragem": Quilometragem,
            "cor": Cor,
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

        # Atualiza a moto no banco de dados
        await db.motos.update_one({"_id": moto_object_id}, {"$set": update_data})
        
        # Recupera a moto atualizada
        updated_moto = await db.motos.find_one({"_id": moto_object_id})

        logger.info(
            msg=f"Moto atualizada!"
        )
        
        # Retorna a moto atualizado como MotoInfo
        return MotosInfo.from_mongo(updated_moto)

    async def delete_moto_ID(moto_id):
        try:
            # Tenta converter o moto_id para ObjectId, porque o MongoDB trabalha com objetos!
            moto_object_id = ObjectId(moto_id)
        except Exception as e:
            logger.error(
                msg="Id moto invalido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de moto inválido")

        # Busca o moto no banco de dados
        moto = await db.motos.find_one({"_id": moto_object_id})

        if not moto:
            logger.info(
                msg="Moto não encontrada!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Moto não encontrada!")

        # Exclui a moto usando o ObjectId
        await db.motos.delete_one({"_id": moto_object_id})

        logger.info(
            msg=f"Moto excluída com sucesso!"
        )
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Moto excluida com sucesso!")
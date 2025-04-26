from core.Backend.app.config.config import app_logger
from core.Backend.app.Veiculos.moto.models.models import Motos
from core.Backend.app.Veiculos.moto.schemas.schemas import MotosInfo
from core.Backend.app.database.database import db
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, status
from bson import ObjectId
import os


# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


# servico somente para motos
class ServicesMoto:


    @staticmethod
    async def createBikeService(
        Marca, Modelo, Ano, Preco, Tipo, Disponivel,
        Quilometragem, Cor, Lugares, Combustivel, Descricao,
        Endereco, Imagem
    ):
        """
        Cria um novo veiculo com as informações fornecidas e armazena mongodb

        Args:
            Marca (str): A marca do caminhao.
            Modelo (str): O modelo do caminhao.
            Ano (int): O ano de fabricação do caminhao.
            Preco (float): O preço do caminhao.
            Disponivel (bool): Indica se o caminhao está disponível para venda.
            Tipo (str): O tipo do caminhao.
            Quilometragem (float): A quilometragem do caminhao.
            Cor (str): A cor do caminhao.
            Lugares (int): O número de lugares disponíveis no caminhao.
            Combustivel (str): O tipo de combustível utilizado pelo caminhao.
            Descricao (str): Uma descrição detalhada do caminhao.
            Endereco (str): O endereço onde o caminhao está localizado.
            Imagem (UploadFile): O arquivo de imagem do caminhao.


        Returns:
            Um objeto contendo as informações do veiculo criado.

        Raises:
            Exception: Para outros erros que possam ocorrer durante a criação do veiculo.
        """
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
    async def getBikesService():
        """
        Args:
            nenhum parametro é passado
        Returns:
            uma lista de todos os veiculos listados na tabela no banco de dados
        Raises:
            caso nenhum veiculo seja encontrado: 404, not found
        """
        motos_cursor = db.motos.find()
        motos = [MotosInfo.from_mongo(moto) for moto in await motos_cursor.to_list(length=100)]

        if motos:
            app_logger.info(
                msg="Motos sendo listadas!"
            )
            return motos
        
        if not motos:
            app_logger.error(
                msg="Nenhuma moto inserida!"
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma moto inserido!")
        

    @staticmethod
    # Função para converter second_search para o tipo adequado
    def convert_search_value(value: str, campo: str):
        """
        Args:
            value recebe um numero inteiro relacionado ao valor do campo
            campo recebe o valor e verifica se é possivel consultar com o campo passado
        Returns:
            retorna a permissao para a realizacao da consulta
        Raises:
            Caso nao seja encontrado campo ou value, erro 400, bad request
        """

        try:
            # Tentando converter conforme o tipo do campo
            if campo in ["ano", "preco", "quilometragem", "portas", "lugares"]:
                return float(value) if "." in value else int(value)
            return value  # Para outros campos, mantemos como string
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Valor para '{campo}' é inválido.")
        

    @staticmethod
    async def getBikesWithParamsService(first_params, second_params):
        """
        Args:
            recebe dois tipos de parametros para realizar consulta
            first_params: sendo string
            second_params: sendo inteiro
        Returns:
            o resultado referente com os parametros de pesquisa 
        Raises:
            caso first_params nao esteja setado em campos_validos, retorna 400, bad request
            caso nao possua carros: 404, not found
        """
        # Validar se o campo é permitido
        campos_validos = [
            "marca", "modelo", "ano",
            "preco", "tipo", "cor",
            "quilometragem", "lugares",
            "combustivel", "descricao",
            "endereco", "categoria"
        ]
        
        if first_params not in campos_validos:
            app_logger.error(
                msg=f"Campo '{first_params}' não é válido para consulta em {first_params}."
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Campo '{first_params}' não é válido para consulta.")
        
        # Converter o segundo parâmetro para o tipo correto antes da consulta
        converted_value = ServicesMoto.convert_search_value(second_params, first_params)
        
        # Consulta para pegar os itens com o campo first_query igual a second_search
        motos_cursor = db.motos.find({first_params: converted_value})
        
        # Usando to_list para pegar os resultados e modificar o _id
        motos = []
        app_logger.info(
            msg="Parametros armazenados na lista para retorno"
        )
        async for moto in motos_cursor:
            del moto['_id']  # Remover o campo _id
            motos.append(moto)
        
        # Se não encontrou nenhum veiculo, retornar um erro
        if not motos:
            app_logger.info(
                msg="Nenhuma moto encontrada com os parâmetros fornecidos."
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma moto encontrada com os parâmetros fornecidos.")
        
        return motos  # Retornando a lista de veiculo
        # aqui conseque renderizar no frontend
        #return templates.TemplateResponse("index.html", {"request": request, "motos": motos})


    @staticmethod
    async def getBikeByIdService(moto_id):
        """
        Args:
            moto_id sera passado como um objeto 'json', já que o id é um uuid
        Return:
            caso o id esteja no banco de dados, o objeto mongo db é transformando para pydantic, e o valor retornado
        Raises:
            caso o carro nao exista: 404, not found
        """
        try:
            # Tenta converter a moto_id para ObjectId, porque o MongoDB trabalha com objetos!
            moto_object_id = ObjectId(moto_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de moto inválido")

        # Busca a moto no banco de dados
        moto = await db.motos.find_one({"_id": moto_object_id})

        if not moto:
            app_logger.info(
                msg="Moto não encontrada!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Moto não encontrada")
        
        app_logger.info(
            msg=f"Informações da moto!"
        )
        
        # Retorna a moto no formato adequado, com o id convertido
        return MotosInfo.from_mongo(moto)
    

    @staticmethod
    async def getBikePageService(request):
        """
        Args:
            request é passao para relaizar a consulta no banco de dados e renderizar no front
        Returns:
            os dados retornados nao tratados e renderizados
        Raises:
            caso nenhum carro exista: 404, not found
        """
        motos_cursor = db.motos.find()
        motos = [MotosInfo.from_mongo(moto) for moto in await motos_cursor.to_list(length=100)]

        app_logger.info(
            msg="Pagina de veiculos ultra leves: motos!"
        )
        return templates.TemplateResponse("index.html", {"request": request, "carros": motos})
        

    @staticmethod
    async def updateBikeService(
        moto_id, Marca, Modelo, Ano, Preco, Tipo, Disponivel,
        Quilometragem, Cor, Lugares, Combustivel, Descricao,
        Endereco, Imagem
    ):
        """
        atualiza as informacoes do veiculo
        Args:
            Marca (str): A marca do caminhao.
            Modelo (str): O modelo do caminhao.
            Ano (int): O ano de fabricação do caminhao.
            Preco (float): O preço do caminhao.
            Disponivel (bool): Indica se o caminhao está disponível para venda.
            Tipo (str): O tipo do caminhao.
            Quilometragem (float): A quilometragem do caminhao.
            Cor (str): A cor do caminhao.
            Lugares (int): O número de lugares disponíveis no caminhao.
            Combustivel (str): O tipo de combustível utilizado pelo caminhao.
            Descricao (str): Uma descrição detalhada do caminhao.
            Endereco (str): O endereço onde o caminhao está localizado.
            Imagem (UploadFile): O arquivo de imagem do caminhao.
        
        Return:
            retorna as informacoes do veiculo ja atualizado
        
        Raises:
            caso o id seja invalido: 400, bad request
            caso o caminhao nao exista: 404, not found

        """
        try:
            # Tenta converter a moto_id para ObjectId, porque o MongoDB trabalha com objetos!
            moto_object_id = ObjectId(moto_id)
        except Exception as e:
            app_logger.error(
                msg="Id moto invalido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de moto inválido")

        # Busca a moto no banco de dados
        moto = await db.motos.find_one({"_id": moto_object_id})

        if not moto:
            app_logger.error(
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

        app_logger.info(
            msg=f"Moto atualizada!"
        )
        
        # Retorna a moto atualizado como MotoInfo
        return MotosInfo.from_mongo(updated_moto)

    async def deleteBikeService(moto_id):
        """
        Args:
            moto_id é passado para realilzar consulta no banco de dados
        Returns:
            ao deletar veiculo, é retornado status code 204, not content
        Raises:
            caso o id seja invalido: 400, bad request
            caso o carro nao exista: 404, not found
        """
        try:
            # Tenta converter o moto_id para ObjectId, porque o MongoDB trabalha com objetos!
            moto_object_id = ObjectId(moto_id)
        except Exception as e:
            app_logger.error(
                msg="Id moto invalido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de moto inválido")

        # Busca o moto no banco de dados
        moto = await db.motos.find_one({"_id": moto_object_id})

        if not moto:
            app_logger.info(
                msg="Moto não encontrada!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Moto não encontrada!")

        # Exclui a moto usando o ObjectId
        await db.motos.delete_one({"_id": moto_object_id})

        app_logger.info(
            msg=f"Moto excluída com sucesso!"
        )
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Moto excluida com sucesso!")
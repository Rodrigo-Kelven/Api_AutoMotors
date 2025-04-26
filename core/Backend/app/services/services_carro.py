from core.Backend.app.Veiculos.carros.schemas.schema import CarroInfo
from core.Backend.app.Veiculos.carros.models.models import Carro
from core.Backend.app.database.database import db
from core.Backend.app.config.config import car_logger
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
    async def createCarService(
        Marca, Modelo, Ano, Preco, Disponivel,
        Tipo, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
        ):
        """
        Cria um novo veiculo com as informações fornecidas e armazena mongodb

        Args:
            Marca (str): A marca do carro.
            Modelo (str): O modelo do carro.
            Ano (int): O ano de fabricação do carro.
            Preco (float): O preço do carro.
            Disponivel (bool): Indica se o carro está disponível para venda.
            Tipo (str): O tipo do carro.
            Quilometragem (float): A quilometragem do carro.
            Cor (str): A cor do carro.
            Portas (int): O número de portas do carro.
            Lugares (int): O número de lugares disponíveis no carro.
            Combustivel (str): O tipo de combustível utilizado pelo carro.
            Descricao (str): Uma descrição detalhada do carro.
            Endereco (str): O endereço onde o carro está localizado.
            Imagem (UploadFile): O arquivo de imagem do carro.

        Returns:
            Um objeto contendo as informações do carro criado.

        Raises:
            Exception: Para outros erros que possam ocorrer durante a criação do carro.
        """

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
        car_logger.info(
            msg=f"Carro inserido! ID: {result.inserted_id}"
        )

        # Converte para o modelo CarroInfo, incluindo o id
        return CarroInfo.from_mongo(carro_db)


    @staticmethod
    async def getCarsService():
        """
        Realiza um get par retornar todos os carros no banco de dados
        Args:
            nenhum dados como parametros
        Returns:
            um objeto mongodb é transformando em um objeto pytdantic e retornado em forma de lista
        Raises:
            Caso nao exista nenhum carro no banco de dados, not fount 404
        """

        carros_cursor = db.carros.find()
        carros = [CarroInfo.from_mongo(carro) for carro in await carros_cursor.to_list(length=100)]
        
        if carros:
            car_logger.info(
                msg="Carros sendo listados!"
            )
            return carros
        
        if not carros:
            car_logger.info(
                msg="Nenhum carro inserido!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum carro inserido!")
        
    
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
    async def getCarWithParamsService(first_params, second_params):
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
            "quilometragem", "portas",
            "lugares", "combustivel",
            "descricao", "endereco", "categoria"
        ]
        
        if first_params not in campos_validos:
            car_logger.error(
                msg=f"Campo '{first_params}' não é válido para consulta em {first_params}."
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Campo '{first_params}' não é válido para consulta.")
        
        # Converter o segundo parâmetro para o tipo correto antes da consulta
        converted_value = ServiceCarros.convert_search_value(second_params, first_params)
        
        # Consulta para pegar os itens com o campo first_query igual a second_search
        carros_cursor = db.carros.find({first_params: converted_value})
        
        # Usando to_list para pegar os resultados e modificar o _id
        carros = []
        car_logger.info(
            msg="Parametros armazenados na lista para retorno"
        )
        async for carro in carros_cursor:
            del carro['_id']  # Remover o campo _id
            carros.append(carro)
        
        # Se não encontrou nenhum carro, retornar um erro
        if not carros:
            car_logger.info(
                msg="Nenhum carro encontrado com os parâmetros fornecidos."
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum carro encontrado com os parâmetros fornecidos.")
        
        return carros  # Retornando a lista de carros
        # aqui conseque renderizar no frontend
        #return templates.TemplateResponse("index.html", {"request": request, "carros": carros})

    
    @staticmethod
    async def getCarByIdService(carro_id):
        """
        Args:
            carro_id sera passado como um objeto 'json', já que o id é um uuid
        Return:
            caso o id esteja no banco de dados, o objeto mongo db é transformando para pydantic, e o valor retornado
        Raises:
            caso o carro nao exista: 404, not found
        """
        try:
            # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
            carro_object_id = ObjectId(carro_id)

        except Exception as e:
            car_logger.error(
                msg="ID de carro inválido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de carro inválido!")

        # Busca o carro no banco de dados
        carro = await db.carros.find_one({"_id": carro_object_id})
        
        if not carro:
            car_logger.error(
                msg="Carro não encontrado!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado!")
        
        # logs
        car_logger.info(
            msg=f"Informações do carro"
        )

        # Retorna o carro no formato adequado, com o id convertido
        return CarroInfo.from_mongo(carro)
    

    @staticmethod
    async def getCarPageService(request):
        """
        Args:
            request é passao para relaizar a consulta no banco de dados e renderizar no front
        Returns:
            os dados retornados nao tratados e renderizados
        Raises:
            caso nenhum carro exista: 404, not found
        """
        carros_cursor = db.carros.find()
        carros = [CarroInfo.from_mongo(carro) for carro in await carros_cursor.to_list(length=100)]

        car_logger.info(
            msg="Pagina de veiculos leves: carros!"
        )
        return templates.TemplateResponse("index.html", {"request": request, "carros": carros})


    
    @staticmethod
    async def updateCarByIdService(
        carro_id, Marca, Modelo, Ano, Preco, Disponivel,
        Tipo, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
        ):
        """
        atualiza as informacoes do veiculo
        Args:
            Marca (str): A marca do carro.
            Modelo (str): O modelo do carro.
            Ano (int): O ano de fabricação do carro.
            Preco (float): O preço do carro.
            Disponivel (bool): Indica se o carro está disponível para venda.
            Tipo (str): O tipo do carro.
            Quilometragem (float): A quilometragem do carro.
            Cor (str): A cor do carro.
            Portas (int): O número de portas do carro.
            Lugares (int): O número de lugares disponíveis no carro.
            Combustivel (str): O tipo de combustível utilizado pelo carro.
            Descricao (str): Uma descrição detalhada do carro.
            Endereco (str): O endereço onde o carro está localizado.
            Imagem (UploadFile): O arquivo de imagem do carro.
        
        Return:
            retorna as informacoes do veiculo ja atualizado
        
        Raises:
            caso o id seja invalido: 400, bad request
            caso o carro nao exista: 404, not found

        """
        try:
            # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
            carro_object_id = ObjectId(carro_id)
        except Exception as e:
            car_logger.error(
                msg="ID de carro inválido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de carro inválido!")

        # Busca o carro no banco de dados
        carro = await db.carros.find_one({"_id": carro_object_id})

        if not carro:
            car_logger.error(
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
        car_logger.info(
            msg=f"Carro atualizado!"
        )
        
        # Retorna o carro atualizado como CarroInfo
        return CarroInfo.from_mongo(updated_carro)
    

    @staticmethod
    async def deleteCarByIdService(carro_id):
        """
        Args:
            carro_id é passado para realilzar consulta no banco de dados
        Returns:
            ao deletar veiculo, é retornado status code 204, not content
        Raises:
            caso o id seja invalido: 400, bad request
            caso o carro nao exista: 404, not found
        """
        try:
            # Tenta converter o carro_id para ObjectId, porque o MongoDB trabalha com objetos!
            carro_object_id = ObjectId(carro_id)
        except Exception as e:
            car_logger.error(
                msg="ID de carro inválido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de carro inválido!")

        # Busca o carro no banco de dados
        carro = await db.carros.find_one({"_id": carro_object_id})

        if not carro:
            car_logger.error(
                msg="Carro não encontrado!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carro não encontrado!")

        # Exclui o carro usando o ObjectId
        await db.carros.delete_one({"_id": carro_object_id})

        # logs
        car_logger.info(
            msg=f"Carro deletado!"
        )

        return {"detail": "Carro excluído com sucesso"}
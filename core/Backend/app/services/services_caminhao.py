from core.Backend.app.Veiculos.caminhao.models.models import Caminhao
from core.Backend.app.Veiculos.caminhao.schemas.schemas import CaminhaoInfo
from core.Backend.app.database.database import db
from core.Backend.app.config.config import logger
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, status
from bson import ObjectId
import os


# Configura o diretório de templates
templates = Jinja2Templates(directory="templates")

# verifica se a pasta existe
UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


#servico somente para caminhao
class ServiceCaminhao:


    @staticmethod
    async def createTruckservice(
        Marca, Modelo, Ano, Preco, Disponivel, Tipo,
        Cap_Maxima, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
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
            Cap_Maxima: capacidade maxima do veiculo
            Quilometragem (float): A quilometragem do caminhao.
            Cor (str): A cor do caminhao.
            Portas (int): O número de portas do caminhao.
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
        file_location = f"{UPLOAD_DIRECTORY}/{Imagem.filename}"
        with open(file_location, "wb") as file_object:
            file_object.write(await Imagem.read())
        
        caminhao = Caminhao(
            marca=Marca,
            modelo=Modelo,
            ano=Ano,
            preco=Preco,
            disponivel=Disponivel,
            tipo=Tipo,
            cap_maxima=Cap_Maxima,
            quilometragem=Quilometragem,
            cor=Cor,
            portas=Portas,
            lugares=Lugares,
            combustivel=Combustivel,
            descricao=Descricao,
            endereco=Endereco,
            imagem=file_location
        )

        # Salva o caminhao no MongoDB
        result = await db.caminhao.insert_one(caminhao.dict())  # Converte o objeto para um dict
        caminhao_db = await db.caminhao.find_one({"_id": result.inserted_id})  # Recupera o carro inserido do banco
        
        # Converte para o modelo CaminhaoInfo, incluindo o id
        return CaminhaoInfo.from_mongo(caminhao_db)
    

    @staticmethod
    async def getTrucksService():
        """
            Args:
                nenhum parametro é passado
            Returns:
                uma lista de todos os veiculos listados na tabela no banco de dados
            Raises:
                caso nenhum veiculo seja encontrado: 404, not found
        """
        caminhao_cursor = db.caminhao.find()
        caminhao = [CaminhaoInfo.from_mongo(caminhao) for caminhao in await caminhao_cursor.to_list(length=100)]
        
        if caminhao:
            logger.info(
                msg="Caminhoes sendo listados!"
            )
            return caminhao
        
        if not caminhao:
            logger.error(
                msg="Nenhum caminhao inserido!"
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum caminhao inserido!")
        

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
    async def getTrucskWithParamsService(first_params, second_params):
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
        second_params
        if first_params not in campos_validos:
            logger.error(
                msg=f"Campo '{first_params}' não é válido para consulta em {first_params}."
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Campo '{first_params}' não é válido para consulta.")
        
        # Converter o segundo parâmetro para o tipo correto antes da consulta
        converted_value = ServiceCaminhao.convert_search_value(second_params, first_params)
        
        # Consulta para pegar os itens com o campo first_query igual a second_search
        caminhao_cursor = db.caminhao.find({first_params: converted_value})
        
        # Usando to_list para pegar os resultados e modificar o _id
        caminhoes = []
        logger.info(
            msg="Parametros armazenados na lista para retorno"
        )
        async for caminhao in caminhao_cursor:
            del caminhao['_id']  # Remover o campo _id
            caminhoes.append(caminhao)
        
        # Se não encontrou nenhum carro, retornar um erro
        if not caminhoes:
            logger.info(
                msg="Nenhum caminhão encontrado com os parâmetros fornecidos."
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhum caminhão encontrado com os parâmetros fornecidos.")
        
        return caminhoes  # Retornando a lista de carros
        # aqui conseque renderizar no frontend
        #return templates.TemplateResponse("index.html", {"request": request, "caminhoes": caminhoes})

    
    @staticmethod
    async def getTruckByIdService(caminhao_id):
        """
        Args:
            caminhao_id sera passado como um objeto 'json', já que o id é um uuid
        Return:
            caso o id esteja no banco de dados, o objeto mongo db é transformando para pydantic, e o valor retornado
        Raises:
            caso o carro nao exista: 404, not found
        """
        try:
            # Tenta converter o caminhao_id para ObjectId, porque o MongoDB trabalha com objetos!
            caminhao_object_id = ObjectId(caminhao_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de caminhao inválido")

        # Busca o caminhao no banco de dados
        caminhao = await db.caminhao.find_one({"_id": caminhao_object_id})

        if not caminhao:
            logger.info(
                msg="Caminhao não encontrado!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caminhao não encontrado!")
        
        logger.info(
            msg=f"Informações da caminhao!"
        )
        # Retorna o caminhao no formato adequado, com o id convertido
        return CaminhaoInfo.from_mongo(caminhao)
    

    @staticmethod
    async def getTruckPageService(request):
        """
        Args:
            request é passao para relaizar a consulta no banco de dados e renderizar no front
        Returns:
            os dados retornados nao tratados e renderizados
        Raises:
            caso nenhum carro exista: 404, not found
        """
        caminhao_cursor = db.caminhao.find()
        caminhao = [CaminhaoInfo.from_mongo(caminhao) for caminhao in await caminhao_cursor.to_list(length=100)]
        
        logger.info(
            msg="Pagina de veiculos pesados: caminhões!"
        )
        return templates.TemplateResponse("index.html", {"request": request, "carros": caminhao})

    
    @staticmethod
    async def updateTruckService(
        caminhao_id, Marca, Modelo, Ano, Preco, Disponivel, Tipo,
        Cap_Maxima, Quilometragem, Cor, Portas, Lugares,
        Combustivel, Descricao, Endereco, Imagem
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
            Cap_Maxima: capacidade maxima do veiculo
            Quilometragem (float): A quilometragem do caminhao.
            Cor (str): A cor do caminhao.
            Portas (int): O número de portas do caminhao.
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
            # Tenta converter o caminhao_id para ObjectId, porque o MongoDB trabalha com objetos!
            caminhao_object_id = ObjectId(caminhao_id)
        except Exception as e:
            logger.error(
                msg="ID de caminhao inválido!"
            )
            raise HTTPException(status_code=400, detail="ID de caminhao inválido!")

        # Busca o caminhao no banco de dados
        caminhao = await db.caminhao.find_one({"_id": caminhao_object_id})

        if not caminhao:
            logger.info(
                msg="Caminhao não encontrado!"
            )
            raise HTTPException(status_code=404, detail="Caminhao não encontrado!")

        update_data = {
            "marca": Marca,
            "modelo": Modelo,
            "ano": Ano,
            "preco": Preco,
            "disponivel": Disponivel,
            "tipo": Tipo,
            "cap_maxima": Cap_Maxima,
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

        # Atualiza o caminhao no banco de dados
        await db.caminhao.update_one({"_id": caminhao_object_id}, {"$set": update_data})
        
        # Recupera o caminhao atualizado
        updated_caminhao = await db.caminhao.find_one({"_id": caminhao_object_id})
        
        logger.info(
            msg=f"Caminhao atualizado!"
        )

        # Retorna o caminhao atualizado como CaminhaoInfo
        return CaminhaoInfo.from_mongo(updated_caminhao)
    

    @staticmethod
    async def deleteTruckService(caminhao_id):
        """
        Args:
            caminhao_id é passado para realilzar consulta no banco de dados
        Returns:
            ao deletar veiculo, é retornado status code 204, not content
        Raises:
            caso o id seja invalido: 400, bad request
            caso o carro nao exista: 404, not found
        """
        try:
            # Tenta converter caminhao_id para ObjectId, porque o MongoDB trabalha com objetos!
            caminhao_object_id = ObjectId(caminhao_id)
        except Exception as e:
            logger.error(
                msg="Id caminhao invalido!"
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de caminhao inválido!")

        # Busca o caminhao no banco de dados
        caminhao = await db.caminhao.find_one({"_id": caminhao_object_id})

        if not caminhao:
            logger.info(
                msg="Caminhao não encontrado!"
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caminhao não encontrado!")

        # Exclui o caminhao usando o ObjectId
        await db.caminhao.delete_one({"_id": caminhao_object_id})

        logger.info(
            msg=f"Caminhao excluído com sucesso!"
        )
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Caminhao excluido com sucesso!")
# Api AutoMotors
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![GraphQL](https://img.shields.io/badge/GraphQL-%23E10098.svg?style=for-the-badge&logo=graphql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-%23C72C41.svg?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white) 
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) 
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)


## Descrição
Este projeto é uma API RESTful para um sistema de uma concéssionária. Um simples projeto baseado num ecommerce construido em FastAPI. A ideia e criar um pequeno sistema e usa-lo como base em outros projetos
Ele permite que os usuários realizem operações como criar, ler, atualizar e excluir produtos, além de gerenciar pedidos e usuários.

# Versão 2.2.0

## Tecnologias Utilizadas
- [Python](https://www.python.org/) - Linguagem de programação
- [FastAPI](https://fastapi.tiangolo.com/) - Framework para construção de APIs
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para interagir com o banco de dados
- [PostGreSQL](https://www.postgresql.org/) - Banco de dados para armazenamento dos dados dos usuarios
- [PgAdmin](https://hub.docker.com/r/dpage/pgadmin4/) - ce gráfica do banco de dados PostGreSQL
- [MongoDB](https://hub.docker.com/_/mongo) - Banco de dados NoSQL para armazenamento dos dados dos veiculos
- [Mongo-Express](https://hub.docker.com/_/mongo-express) - Interface gráfica do banco de dados MongoDB
- [Redis](https://hub.docker.com/_/redis) - Banco de dados Caching
- [Redisinsight](https://hub.docker.com/r/redis/redisinsight) - Interface gráfica do banco de dados Redis
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Validação de dados
- [Docker](https://www.docker.com/) - Conteirização da aplicação


## Instalação
```bash
  git clone https://github.com/Rodrigo-Kelven/Api_AutoMotors
  cd Api_AutoMotors
  docker-compose up
```

# Paineis de administração
- ## Swagger FastAPI
        http://127.0.0.1:8000/docs
- ## Mongo Express
        http://127.0.0.1:8081/
- ## PgAdmin
        http://127.0.0.1:5050/login?next=/


# Contribuições
Contribuições são bem-vindas! Se você tiver sugestões ou melhorias, sinta-se à vontade para abrir um issue ou enviar um pull request.;)

## Autores
- [@Rodrigo_Kelven](https://github.com/Rodrigo-Kelven)
- [@Rael Santana](https://github.com/Raelsantana)

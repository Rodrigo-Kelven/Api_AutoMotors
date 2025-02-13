
# Api AutoMotors
## Descrição
Este projeto é uma API RESTful para um sistema de uma concéssionária. Um simples projeto baseado num ecommerce construido em FastAPI. A ideia e criar um pequeno sistema e usa-lo como base em outros projetos
Ele permite que os usuários realizem operações como criar, ler, atualizar e excluir produtos, além de gerenciar pedidos e usuários.

# Versão
- 0.0.15

## Tecnologias Utilizadas
- [Python](https://www.python.org/) - Linguagem de programação
- [FastAPI](https://fastapi.tiangolo.com/) - Framework para construção de APIs
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para interagir com o banco de dados
- [SQLite](https://www.sqlite.org/index.html) - Banco de dados leve (temporariamente para usuarios)
- [MongoDB](https://hub.docker.com/_/mongo) - Banco de dados NoSQL 
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Validação de dados
- [Docker](https://www.docker.com/) - Conteirização da aplicação


## Instalação
```bash
  git clone https://github.com/Rodrigo-Kelven/Api_AutoMotors
  cd Api_AutoMotors/app
  pip install -r requirements.txt
```
### Atençao a esta parte! Ela é crucial para o funcionamento da API.
```bash
  fastapi dev main.py --reload --port 8000
```


# Contribuições
Contribuições são bem-vindas! Se você tiver sugestões ou melhorias, sinta-se à vontade para abrir um issue ou enviar um pull request.;)

## Autores
- [@Rodrigo_Kelven](https://github.com/Rodrigo-Kelven)
- [@Rael Santana](https://github.com/Raelsantana)


# Api AutoMotors
## Descrição
Este projeto é uma API RESTful para um sistema de uma concéssionária. Um simples projeto baseado num ecommerce construido em FastAPI. A ideia e criar um pequeno sistema e usa-lo como base em outros projetos
Ele permite que os usuários realizem operações como criar, ler, atualizar e excluir produtos, além de gerenciar pedidos e usuários.


## Tecnologias Utilizadas
- [Python](https://www.python.org/) - Linguagem de programação
- [FastAPI](https://fastapi.tiangolo.com/) - Framework para construção de APIs
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para interagir com o banco de dados
- [SQLite](https://www.sqlite.org/index.html) - Banco de dados leve
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

## Melhorias da API
- ### Arquitetura do Ecommerce
    - Micro-Services
        - Criar um sistema de validação separado da API principal
        - Separar: (visualização, validação, regras de negócio)
    - Criar schemas e modelos flexiveis para diferentes tipos de veiculos
        - Utilizar NoSQL, RoBo 3T
        - Redis
 
- ### Painel Admin
    - Adicionar pesquisa de produtos baseado em:
        -  nome do produto
        -  categoria do produto
        -  preço do produto
            - media de preço dos produtos
       - quantidade de estrelas dos produtos -> média
      
- ### Criação de um painel administrativo -> (Baseado no Django)
    - Controle de:
        - Estoque
        - Usuarios -> Update
        - Produtos
        - Análise de vendas
          
- ### Frontend
  - Utilizar Flask para renderizar páginas em (Html, CSS)
  - Usar algum framework -> (React, Vue, etc)
    
- ### Autenticação e Autorização:
    - Implementar um sistema de autenticação, como OAuth2 ou JWT, para garantir que apenas usuários autorizados possam acessar a API.
    - Centralizar a autorização para controlar o acesso a diferentes serviços

- ### Otimização do Roteamento:
    - Utilizar técnicas de balanceamento de carga para distribuir as solicitações entre múltiplos serviços, melhorando a eficiência e a resiliência.
    - Implementação de um mecanismo de fallback para redirecionar solicitações em caso de falha de um serviço.

- ### Caching:
    - Adicionar caching para respostas frequentes, utilizando Redis ou Memcached, para reduzir a latência e a carga nos serviços de backend.
    - Definir políticas de expiração para garantir que os dados em cache sejam atualizados conforme necessário.

- ### Monitoramento e Logging:
    - Integrar ferramentas de monitoramento, como Prometheus ou Grafana, para acompanhar o desempenho da API e identificar gargalos.
    - Implementar um sistema de logging detalhado para registrar erros e eventos importantes, facilitando a depuração.

- ### Documentação:
    - Utilizar ferramentas como Swagger ou Redoc para gerar documentação interativa da API, facilitando o uso por desenvolvedores.
    - Manter a documentação atualizada com exemplos de uso e descrições claras dos endpoints.

- ### Testes Automatizados:
    - Criar uma suíte de testes automatizados para garantir que a API funcione conforme esperado e para detectar regressões rapidamente.
    - Realizar testes de carga para avaliar como a API se comporta sob diferentes níveis de tráfego.

- ### Tratamento de Erros:
    - Implementar um sistema de tratamento de erros que retorne mensagens de erro claras e significativas para os usuários.
    - Utilizar códigos de status HTTP apropriados para diferentes tipos de falhas.

- ### Versionamento da API:
    - Considerar implementar versionamento na API para permitir atualizações sem quebrar a compatibilidade com clientes existentes.
    - Utilizar um padrão de URL que inclua a versão, como /api/v1/....

- ### Segurança:
    - Apliquar práticas de segurança, como validação de entrada e proteção contra ataques comuns (ex: SQL Injection, XSS).
    - Considerar o uso de HTTPS para proteger a comunicação entre clientes e a API.

- ### Feedback do Usuário:
    - Coletar feedback dos usuários da API para identificar áreas de melhoria e novas funcionalidades que podem ser adicionadas.


# Contribuições
Contribuições são bem-vindas! Se você tiver sugestões ou melhorias, sinta-se à vontade para abrir um issue ou enviar um pull request.;)

## Autores
- [@Rodrigo_Kelven](https://github.com/Rodrigo-Kelven)
- [@Rael Santana](https://github.com/Raelsantana)

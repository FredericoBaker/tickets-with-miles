# Buscador de Voos com Milhas na Smiles

## Integrantes do Grupo
- Frederico Dolher Souza Baker (2021031513)
- Daniel Oliveira Barbosa (2020006450)
- Victor Prates Figueiredo (2019007317)

## Descrição do Sistema
Esta é uma aplicação que permite a pesquisa de voos da plataforma Smiles com flexibilidade de datas. Ao fornecer os seguintes parâmetros:
- **Origem** (código IATA do aeroporto)
- **Destino** (código IATA do aeroporto)
- **Data de partida**
- **Flexibilidade de dias**

Retorna-se uma lista de voos que atendem aos critérios, apresentando informações como o custo em milhas e detalhes do itinerário.

## Tecnologias Utilizadas
- **Django**: Framework web usado para construir a aplicação.
- **Python**: Linguagem principal do desenvolvimento.
- **aiohttp**: Biblioteca para realizar requisições assíncronas ao API da Smiles.
- **SQLite**: Banco de dados local para armazenar informações como aeroportos.
- **Unittest**: Framework para testes automatizados.

## Como Rodar o Projeto

1. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```

3. Acesse o diretório do projeto Django:
   ```bash
   cd tickets_with_miles
   ```

4. Realize as migrações para configurar o banco de dados:
   ```bash
   python manage.py migrate
   ```

5. Carregue a base de dados com os aeroportos:
   ```bash
   python manage.py load_airports
   ```

6. Rode o projeto:
   ```bash
   python manage.py runserver
   ```

7. Acesse a aplicação no navegador através de [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Observações

Para executar os testes de unidade, integração e E2E respectivamente:

```bash
python manage.py test flights/tests/unit
```

```bash
python manage.py test flights/tests/integration
```

```bash
python manage.py test flights/tests/e2e
```
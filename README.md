# ProjetoEC

## Como Executar

1. **Configurar o Ambiente:**
   Criar um ficheiro `.env` na raiz do projeto tendo o ficheiro de exemplo como base:
   ```console
   cp .env.example .env
   ```
2. **Compose para levantar os serviços (App, SQL, NoSQL e Vetorial):**
    ```console
    docker-compose up --build -d
    ```
3. **Aceder à Aplicação ficará disponível em:** http://localhost:8501

## Qualidade de Código (Linter)
Para validar a conformidade do código com as normas PEP8 através do container da aplicação:

```console
docker-compose run app flake8 .
```
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

## Instalar o LLM (gemma3:4b) no Container
1. **Identificar o Container:**
      ```console
   docker ps
   ```
2. **Entrar no Container:**
      ```console
   docker exec -it <nome_do_container_ollama> bash
   ```
3. **Instalar o Modelo:**
    ```console
   ollama pull gemma3:4b
   ```
4. **Confirmar a Instalação:**
    ```console
   ollama list
   ```



## Qualidade de Código (Linter)
Para validar a conformidade do código com as normas PEP8 através do container da aplicação:

```console
docker-compose run app flake8 .
```

## Integração do dataset WUENIC

Para ingerir o dataset WUENIC:

```bash
python -c "from utils.ingest_wuenic import ingest_wuenic; ingest_wuenic('path_to_excel.xlsx')"
```

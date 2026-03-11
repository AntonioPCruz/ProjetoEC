FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o requirements.txt da raiz do projeto
COPY requirements.txt ./requirements.txt

# Instala dependências
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia o conteúdo da API (main.py, chat.py) e módulos necessários
COPY src/api ./api
COPY src/rag ./rag
COPY src/agents ./agents

# Expõe a porta do FastAPI
EXPOSE 8500

# Comando para correr a API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8500", "--reload"]
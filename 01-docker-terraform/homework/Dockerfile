# Usa imagem Python 3.11 slim (mais leve)
FROM python:3.11-slim

# Copia o executável do 'uv' da imagem oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Adiciona o ambiente virtual ao PATH do sistema
ENV PATH="/app/.venv/bin:$PATH"

# Copia arquivos de dependência primeiro (otimiza o cache do Docker)
COPY "pyproject.toml" "uv.lock" ".python-version" ./

# Instala as dependências travadas no arquivo lock
RUN uv sync --locked

# Copia o script de ingestão para o container | 1º é o arquivo de origem, 2º é o destino
COPY ingest_data.py .

# Define o comando que será executado ao iniciar o container
ENTRYPOINT ["python", "ingest_data.py"]
# /api_gateway/Dockerfile

# 1. Imagem Base (leve)
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copia e instala as dependências
# (fastapi, uvicorn, pika)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia o código da aplicação
COPY main.py .

# 5. Expõe a porta que o Uvicorn usará (porta padrão 8000)
EXPOSE 8000

# --- ADICIONAR ESTAS LINHAS ---
# 7. (Mitigação T-07) Cria um usuário não-root
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

# Define o proprietário dos arquivos da aplicação
RUN chown -R appuser:appgroup /app

# Muda para o usuário não-root
USER appuser
# --- FIM DA ADIÇÃO ---

# Linha final (já existe)
CMD [...]

# 6. Comando para rodar a aplicação
# host="0.0.0.0" é crucial para expor fora do container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
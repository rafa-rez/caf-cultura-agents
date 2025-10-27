# /agente_classificador/Dockerfile

# 1. Imagem Base (leve)
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copia e instala as dependências
# (Separado para aproveitar o cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia o código da aplicação
COPY main.py .

# 5. Expõe a porta que o Uvicorn usará (diferente do Gateway)
EXPOSE 8001

# 6. Comando para rodar a aplicação
# host="0.0.0.0" é crucial para expor fora do container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
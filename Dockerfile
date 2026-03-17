# Usa uma imagem oficial e leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY main.py .

# Expõe a porta que a aplicação vai rodar
EXPOSE 8080

# Comando para iniciar o servidor Uvicorn
CMD ["uvicorn", "main:app", "--workers", "4", "--host", "0.0.0.0", "--port", "8080"]
FROM docker.m.daocloud.io/library/python:3.11-slim

# Устанавливаем системные зависимости для сборки psutil
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Открываем порт для Streamlit
EXPOSE 8501

# Команда запуска с отключением проверки обновлений и настройки адреса
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
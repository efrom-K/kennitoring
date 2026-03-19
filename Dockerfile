FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для сборки psutil и работы с Docker
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Открываем порт Streamlit
EXPOSE 8050

# Запуск через модуль python для надежности
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8050", "--server.address=0.0.0.0"]
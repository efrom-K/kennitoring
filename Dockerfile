FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Возвращаем твой порт 8050
EXPOSE 8050

# Явно указываем порт в команде запуска
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port=8050", "--server.address=0.0.0.0"]
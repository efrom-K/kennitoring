FROM docker.m.daocloud.io/library/python:3.11-slim

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8050

CMD ["streamlit", "run", "app.py", "--server.port=8050", "--server.address=0.0.0.0"]
FROM python:3.11-slim

ARG BUILD_SHA=unknown
ARG APP_VERSION=1.0.0

ENV PANACEA_BUILD_SHA=${BUILD_SHA} \
    PANACEA_VERSION=${APP_VERSION}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app:create_app()"]

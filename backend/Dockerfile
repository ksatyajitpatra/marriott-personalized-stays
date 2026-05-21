FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app

EXPOSE 8000

# docker-compose mounts the data/ folder at /data, so SEEDS_PATH points there.
ENV SEEDS_PATH=/data/seeds

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

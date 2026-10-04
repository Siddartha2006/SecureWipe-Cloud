FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home --uid 10001 appuser
COPY backend/app ./app
USER 10001:10001
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import os; from redis import Redis; Redis.from_url(os.environ['REDIS_URL']).ping()"
CMD ["sh", "-c", "exec rq worker --url \"$REDIS_URL\" securewipe"]

FROM python:3.12-slim
WORKDIR /server
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src/
COPY alembic ./alembic/
COPY alembic.ini ./alembic.ini
COPY .env ./.env
EXPOSE 8000
CMD ["sh", "-c", "uvicorn src.app.main:app --host 0.0.0.0 --port 8000"]


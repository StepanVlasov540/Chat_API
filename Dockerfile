# 1. Базовый образ
FROM python:3.11-slim

# 2. Рабочая директория
WORKDIR /app

# 3. Копируем и устанавливаем зависимости (кешируется)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем всё приложение
COPY app/ app/
COPY alembic/ alembic/

# 5. Порт
EXPOSE 8000

# 6. Команда запуска
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]


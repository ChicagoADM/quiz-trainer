FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Копируем и устанавливаем зависимости
COPY requirements.txt /app/
RUN pip install --upgrade pip --no-cache-dir && pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . /app/

# Собираем статику (если есть)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# При старте контейнера выполняем миграции и запускаем сервер
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn quiz_project.wsgi:application --bind 0.0.0.0:8000"]
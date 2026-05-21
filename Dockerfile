FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --upgrade pip --no-cache-dir && pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

# Создаём миграции для quiz, применяем их, собираем статику и стартуем
CMD ["sh", "-c", "python manage.py makemigrations quiz --noinput && python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn quiz_project.wsgi:application --bind 0.0.0.0:8000"]
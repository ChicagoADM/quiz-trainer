FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Установка зависимостей
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем проект
COPY . /app/

# Собираем статику
RUN python manage.py collectstatic --noinput

# Порт, который будет слушать gunicorn
EXPOSE 8000

# Запуск gunicorn
CMD ["gunicorn", "quiz_project.wsgi:application", "--bind", "0.0.0.0:8000"]
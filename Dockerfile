FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Устанавливаем системные зависимости, если они нужны (обычно для Django не требуются)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем Python-зависимости
COPY requirements.txt /app/
RUN pip install --upgrade pip --no-cache-dir && pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . /app/

# Собираем статику
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "quiz_project.wsgi:application", "--bind", "0.0.0.0:8000"]
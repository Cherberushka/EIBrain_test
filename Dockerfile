FROM python:alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Установим директорию для работы

WORKDIR /EIBrain

COPY ./requirements.txt ./
COPY .env ./

# Устанавливаем зависимости и gunicorn
RUN pip install --upgrade pip
RUN apt update && apt install ffmpeg -y
RUN pip install --no-cache-dir -r ./requirements.txt

# Копируем файлы и билд
COPY ./ ./

RUN chmod -R 777 ./
ENTRYPOINT ["python", "app.py"]
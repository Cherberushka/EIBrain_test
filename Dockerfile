FROM python:3.10

WORKDIR /telegram_bot

COPY requirements.txt ./
COPY .env ./

RUN apt update && apt install ffmpeg -y
RUN pip install -r requirements.txt

COPY ./ ./

ENTRYPOINT ["python", "app.py"]
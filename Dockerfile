FROM python:3.10

WORKDIR /bot

COPY pip_requirements.txt ./
COPY .env ./

RUN apt update && apt install ffmpeg -y
RUN pip install -r pip_requirements.txt

COPY ./ ./

ENTRYPOINT ["python", "app.py"]

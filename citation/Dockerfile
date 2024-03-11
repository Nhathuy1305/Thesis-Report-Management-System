FROM python:3.9-slim-bullseye

WORKDIR /app

RUN apt-get update \
    && apt-get install -y xpdf libmagic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
CMD ["python3", "main.py"]
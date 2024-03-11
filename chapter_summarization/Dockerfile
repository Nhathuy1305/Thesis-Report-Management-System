FROM python:3.9-slim-bullseye
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN python3 -m nltk.downloader punkt
COPY . .
CMD ["python3", "main.py"]
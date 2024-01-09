FROM python:latest
WORKDIR /app

RUN apt-get update && apt-get install -y xpdf

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
FROM postgres:latest

RUN apt-get update
RUN apt-get install -y curl

COPY init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
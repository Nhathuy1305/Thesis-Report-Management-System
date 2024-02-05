FROM postgres:alpine

RUN apk --no-cache add curl

COPY init.sql /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432
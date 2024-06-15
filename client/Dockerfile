FROM node:18-alpine as build
WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH
COPY package.json package-lock.json ./
RUN npm install --silent --unsafe-perm
RUN npm install react-scripts@3.0.1 -g --silent --unsafe-perm
COPY . /app
RUN npm run build

FROM node:18-alpine
RUN npm install -g http-server
WORKDIR /app
COPY --from=build /app/build /app
EXPOSE 3000
CMD ["http-server", "-p", "3000"]

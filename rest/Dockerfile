FROM node:18-alpine
WORKDIR /app
COPY ["package.json", "package-lock.json", "tsconfig.json", "./"]
RUN npm install
RUN echo "fs.inotify.max_user_watches=524288" >> /etc/sysctl.conf && sysctl -p
RUN ulimit -n 2048
COPY . .
EXPOSE 5000
CMD ["npm", "start"]
FROM node:20-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY package.json .
RUN npm install && npm audit fix --force

COPY . .

COPY wait-for-it.sh .
RUN chmod +x wait-for-it.sh

EXPOSE 5173

CMD ["/bin/sh", "./wait-for-it.sh", "backend:8000", "--", "npm", "run", "dev"]
FROM node:20-slim

WORKDIR /app

COPY package.json .
RUN npm install && npm audit fix --force

COPY . .

COPY wait-for-it.sh .
RUN chmod +x wait-for-it.sh

EXPOSE 5173

CMD ["./wait-for-it.sh", "backend:8000", "--", "npm", "run", "dev"]
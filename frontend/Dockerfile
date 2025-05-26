FROM node:20-slim

WORKDIR /app

COPY package.json .
RUN npm install && npm audit fix --force

COPY . .

RUN npm run build

EXPOSE 5173

CMD ["npx", "vite", "preview", "--host", "0.0.0.0", "--port", "5173"]
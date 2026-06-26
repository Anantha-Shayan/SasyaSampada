# Dockerfile for SasyaSampada frontend
FROM node:22-slim

WORKDIR /app

COPY package.json package-lock.json* ./
COPY public/ ./public
COPY src/ ./src
COPY tailwind.config.js postcss.config.js ./

RUN npm install
RUN npm run build

EXPOSE 3000
CMD ["npx", "serve", "-s", "build", "-l", "3000"]

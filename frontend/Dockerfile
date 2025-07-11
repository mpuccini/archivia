# Frontend Dockerfile - multi-stage per produzione
FROM node:18-alpine AS build

WORKDIR /app

# Copia package.json e installa dipendenze
COPY package.json ./
RUN npm install

# Copia il codice sorgente
COPY . .

# Argomento per l'API URL
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Builda l'applicazione
RUN npm run build

# Stage di produzione con nginx
FROM nginx:alpine

# Copia i file buildati
COPY --from=build /app/dist /usr/share/nginx/html

# Configurazione nginx per Single Page Application
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

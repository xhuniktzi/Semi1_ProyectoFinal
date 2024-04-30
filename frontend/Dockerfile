# Etapa de construcción
# Utilizamos una imagen de Node.js para compilar la aplicación Angular
FROM node:16 as build-stage

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos de configuración de Node.js y instalamos las dependencias
COPY package.json package-lock.json ./
RUN npm install

# Copiamos el resto del código fuente de la aplicación Angular al contenedor
COPY . .

# Compilamos la aplicación para producción
RUN npm run build -- --output-path=./dist/out --configuration production

# Etapa de producción
# Utilizamos una imagen de NGINX para servir la aplicación
FROM nginx:alpine

# Copiamos los archivos estáticos generados en la etapa de construcción al servidor NGINX
COPY --from=build-stage /app/dist/out/ /usr/share/nginx/html

# Opcional: Si tienes un archivo de configuración de NGINX personalizado, lo puedes copiar
# COPY nginx.conf /etc/nginx/nginx.conf
# COPY nginx-selfsigned.crt /etc/ssl/certs/nginx-selfsigned.crt
# COPY nginx-selfsigned.key /etc/ssl/private/nginx-selfsigned.key

# Exponemos el puerto 80 para acceder al servidor NGINX
EXPOSE 80
EXPOSE 443

# Comando para iniciar NGINX y mantenerlo en ejecución
CMD ["nginx", "-g", "daemon off;"]

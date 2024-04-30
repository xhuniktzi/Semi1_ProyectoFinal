# Usar una imagen base de Python 3.11
FROM python:3.11-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos Pipfile y Pipfile.lock en el contenedor
COPY Pipfile Pipfile.lock /app/

# Instalar pipenv
RUN pip install --upgrade pip && \
    pip install pipenv

# Instalar las dependencias del proyecto
RUN pipenv install --deploy --ignore-pipfile

# Copiar el resto del código fuente de la aplicación en el contenedor
COPY src/ /app/

# Exponer el puerto donde se ejecutará la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["pipenv", "run", "python", "app.py"]

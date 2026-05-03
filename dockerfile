# Usamos una imagen oficial y ligera de Python
FROM python:3.10-slim

# Configuraciones de entorno para optimizar Python en contenedores
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos primero para aprovechar el caché de Docker
COPY requirements.txt .

# Actualizamos pip e instalamos las dependencias
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código fuente al contenedor
COPY . .

# Exponemos el puerto por defecto de FastAPI
EXPOSE 8000

# Comando para arrancar el servidor con recarga automática (--reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
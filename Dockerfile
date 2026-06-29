# Usar una versión de Python pequeña y rápida
FROM python:3.10-slim

# Crear una carpeta dentro de la caja llamada /app
WORKDIR /app

# Copiar el requirements.txt e instalar las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo tu código (app.py, templates, static, database) a la caja
COPY . .

# Decir por qué puerto va a salir la página
EXPOSE 5000

# La orden para encender Flask
CMD ["python", "app.py"]
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Al instalar paquetes pip guarda una cache de los paquetes que descarga, pero
# podemos desactivar esta opcion para que el contenedor pese menos
RUN pip install --no-cache-dir -r requirements.txt 
COPY . .

CMD ["python3", "main.py"]

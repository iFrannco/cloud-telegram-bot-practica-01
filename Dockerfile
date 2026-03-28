FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Instalamos dependencias y forzamos versiones corregidas en la misma capa
# para no dejar metadata vulnerable en capas intermedias.
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir --upgrade --force-reinstall --no-deps \
        "wheel==0.46.2" \
        "jaraco.context==6.1.0"

COPY . .

CMD ["python3", "main.py"]

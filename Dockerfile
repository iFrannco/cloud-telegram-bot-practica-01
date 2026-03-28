FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Instalamos dependencias del proyecto y forzamos versiones corregidas de
# paquetes de tooling que Trivy detecto como vulnerables en la imagen final.
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip uninstall -y wheel jaraco.context || true
RUN python -m pip install --no-cache-dir "wheel>=0.46.2" "jaraco.context>=6.1.0"

COPY . .

CMD ["python3", "main.py"]

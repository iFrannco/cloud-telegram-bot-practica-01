FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Instalamos dependencias del proyecto y eliminamos tooling de empaquetado
# que no hace falta en runtime y que Trivy esta reportando como vulnerable.
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip uninstall -y pip wheel jaraco.context || true

COPY . .

CMD ["python3", "main.py"]

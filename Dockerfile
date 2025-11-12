# Dockerfile Multi-Stage para API de Predicción de Obesidad
# Optimizado para producción con tamaño mínimo

# ============================================================
# Stage 1: Builder - Instalación de dependencias
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo requirements para aprovechar caché de Docker
COPY api/requirements.txt .

# Instalar dependencias Python en directorio temporal
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================
# Stage 2: Runtime - Imagen final mínima
# ============================================================
FROM python:3.11-slim

# Metadata
LABEL maintainer="ObesityMine53 Team"
LABEL description="API de predicción de obesidad con XGBoost"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MODEL_PATH=/app/artefactos/pipelines_optimizados.joblib \
    LOG_LEVEL=info

WORKDIR /app

# Crear usuario no-root antes de copiar archivos
RUN useradd -m -u 1000 apiuser

# Copiar dependencias instaladas desde builder y asignar permisos
COPY --from=builder --chown=apiuser:apiuser /root/.local /home/apiuser/.local

# Copiar código de la API
COPY --chown=apiuser:apiuser api/ /app/api/

# Copiar modelo entrenado
COPY --chown=apiuser:apiuser artefactos/pipelines_optimizados.joblib /app/artefactos/

# Cambiar ownership de /app
RUN chown -R apiuser:apiuser /app

# Cambiar a usuario no-root
USER apiuser

# Agregar binarios de usuario al PATH
ENV PATH="/home/apiuser/.local/bin:$PATH"

# Health check (simplificado sin requests)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import http.client; conn = http.client.HTTPConnection('localhost', 8000); conn.request('GET', '/health'); r = conn.getresponse(); exit(0 if r.status == 200 else 1)"

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["python", "-m", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

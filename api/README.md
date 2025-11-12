# API de Predicción de Obesidad

API REST para clasificación de niveles de obesidad utilizando Machine Learning (XGBoost).

## 🚀 Quick Start

### Ejecución Local

```powershell
# Instalar dependencias
pip install -r api/requirements.txt

# Ejecutar servidor
python -m uvicorn api.app:app --reload --port 8000
```

Acceder a:
- **API**: http://localhost:8000
- **Documentación (Swagger)**: http://localhost:8000/docs
- **Documentación (ReDoc)**: http://localhost:8000/redoc

### Ejecución con Docker

```powershell
# Opción 1: Docker directo
docker build -t obesity-api .
docker run -p 8000:8000 obesity-api

# Opción 2: Docker Compose (recomendado)
docker-compose up -d
```

## 📡 Endpoints Principales

### Health Check
```bash
GET /health
```

### Predicción Individual
```bash
POST /predict
Content-Type: application/json

{
  "Age": 25.0,
  "Height": 1.75,
  "Weight": 70.0,
  "Gender": "male",
  "family_history_with_overweight": "yes",
  "FAVC": "yes",
  "FCVC": 2.0,
  "NCP": 3.0,
  "CAEC": "sometimes",
  "SMOKE": "no",
  "CH2O": 2.0,
  "SCC": "no",
  "FAF": 2.0,
  "TUE": 1.0,
  "CALC": "no",
  "MTRANS": "public_transportation"
}
```

**Respuesta:**
```json
{
  "prediction": "normal_weight",
  "confidence": 0.9234,
  "probabilities": {
    "insufficient_weight": 0.0012,
    "normal_weight": 0.9234,
    "overweight_level_i": 0.0543,
    ...
  },
  "bmi": 22.86
}
```

### Explicabilidad (SHAP)
```bash
POST /explain

{
  "instance": { ... },
  "explain_type": "shap"
}
```

## 🧪 Testing

```powershell
# Ejecutar tests
pytest tests/test_api.py -v

# Con cobertura
pytest tests/test_api.py --cov=api --cov-report=html
```

**Resultados**: 10 passed, 8 skipped (requieren modelo cargado)

## 📊 Modelo

- **Algoritmo**: XGBoost Classifier
- **F1-Score (Test)**: 0.9426
- **Accuracy (Test)**: 0.9424
- **Features**: 16 variables (Age, Height, Weight, etc.)
- **Clases**: 7 niveles de obesidad

## 📚 Documentación Completa

Ver documentación detallada:
- **[API_DEPLOYMENT.md](../docs/API_DEPLOYMENT.md)** - Guía completa de deployment
  - Instalación y configuración
  - Documentación de todos los endpoints
  - Docker y Docker Compose
  - Deployment en GCP (Cloud Run, GKE, Compute Engine)
  - Troubleshooting y optimización
  
- **[POSTMAN_GUIDE.md](../docs/POSTMAN_GUIDE.md)** - Guía de uso con Postman
  - Instrucciones paso a paso para cada endpoint
  - Ejemplos de requests con JSON completo
  - Casos de uso reales
  - Validaciones y manejo de errores
  - Tips y tricks para Postman

## 🔧 Estructura

```
api/
├── __init__.py          # Versión del API
├── models.py            # Schemas Pydantic
├── prediction.py        # Lógica de predicción y SHAP
├── app.py               # Endpoints FastAPI
└── requirements.txt     # Dependencias
```

## 🐳 Docker

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
```

## ☁️ GCP Deployment

```bash
# Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/obesity-api
gcloud run deploy obesity-api --image gcr.io/PROJECT_ID/obesity-api --platform managed
```

## 📝 Notas

- **Validación**: Pydantic valida automáticamente todos los inputs
- **Explicabilidad**: SHAP muestra contribución de cada feature
- **Health Check**: Docker incluye health check automático cada 30s
- **CORS**: Configurado para permitir todos los orígenes (ajustar en producción)

---

**Versión**: 1.0.0  
**Última actualización**: 2025-01-11

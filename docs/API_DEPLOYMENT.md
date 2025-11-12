# API de Predicción de Obesidad - Deployment Guide

## 📋 Descripción

API REST para predicción de niveles de obesidad utilizando Machine Learning (XGBoost). Incluye endpoints para predicción individual, por lote, y explicabilidad con SHAP.

**Modelo**: XGBoost optimizado
- F1-Score (Test): 0.9426
- Accuracy (Test): 0.9424

---

## 🚀 Instalación y Ejecución

### Opción 1: Ejecución Local con Python

#### Requisitos
- Python 3.11+
- Entorno virtual configurado

#### Pasos

```powershell
# 1. Activar entorno virtual
.\.conda\Scripts\activate

# 2. Instalar dependencias de la API
pip install -r api/requirements.txt

# 3. Ejecutar servidor de desarrollo
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

Acceder a:
- API: http://localhost:8000
- Documentación interactiva (Swagger): http://localhost:8000/docs
- Documentación alternativa (ReDoc): http://localhost:8000/redoc

---

### Opción 2: Ejecución con Docker

#### Requisitos
- Docker Desktop instalado
- Docker Compose (incluido en Docker Desktop)

#### Construir y ejecutar

```powershell
# 1. Construir imagen Docker
docker build -t obesity-api:latest .

# 2. Ejecutar contenedor
docker run -d \
  --name obesity-api \
  -p 8000:8000 \
  obesity-api:latest

# O usar Docker Compose (recomendado)
docker-compose up -d
```

#### Verificar estado

```powershell
# Ver logs
docker logs obesity-api

# Verificar salud
curl http://localhost:8000/health

# Detener contenedor
docker-compose down
```

---

### Opción 3: Ejecución con Docker Compose (Producción)

```powershell
# Iniciar todos los servicios
docker-compose up -d

# Verificar servicios activos
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f api

# Reiniciar servicios
docker-compose restart

# Detener y eliminar contenedores
docker-compose down
```

---

## 📡 Endpoints de la API

### 1. Health Check

Verifica el estado del servicio y carga del modelo.

**Request**
```bash
GET /health
```

**Response** (200)
```json
{
  "status": "healthy",
  "model_loaded": true,
  "message": "Servicio operativo"
}
```

---

### 2. Predicción Individual

Predice el nivel de obesidad para un individuo.

**Request**
```bash
POST /predict
Content-Type: application/json
```

**Body**
```json
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

**Response** (200)
```json
{
  "prediction": "normal_weight",
  "confidence": 0.9234,
  "probabilities": {
    "insufficient_weight": 0.0012,
    "normal_weight": 0.9234,
    "overweight_level_i": 0.0543,
    "overweight_level_ii": 0.0123,
    "obesity_type_i": 0.0067,
    "obesity_type_ii": 0.0015,
    "obesity_type_iii": 0.0006
  },
  "bmi": 22.86
}
```

**Ejemplo con curl**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

---

### 3. Predicción por Lote

Predice para múltiples instancias (máximo 100).

**Request**
```bash
POST /predict_batch
Content-Type: application/json
```

**Body**
```json
{
  "instances": [
    {
      "Age": 25.0,
      "Height": 1.75,
      "Weight": 70.0,
      "Gender": "male",
      ...
    },
    {
      "Age": 30.0,
      "Height": 1.65,
      "Weight": 55.0,
      "Gender": "female",
      ...
    }
  ]
}
```

**Response** (200)
```json
{
  "predictions": [
    {
      "prediction": "normal_weight",
      "confidence": 0.9234,
      "probabilities": {...},
      "bmi": 22.86
    },
    {
      "prediction": "insufficient_weight",
      "confidence": 0.8567,
      "probabilities": {...},
      "bmi": 20.20
    }
  ]
}
```

---

### 4. Información del Modelo

Retorna metadatos y métricas del modelo.

**Request**
```bash
GET /model_info
```

**Response** (200)
```json
{
  "model_name": "XGBoost",
  "model_type": "XGBoost Classifier",
  "f1_score_test": 0.9426,
  "accuracy_test": 0.9424,
  "hyperparameters": {
    "colsample_bytree": 0.7,
    "learning_rate": 0.001,
    "max_depth": 5,
    "n_estimators": 100,
    "subsample": 0.7
  },
  "features": ["Age", "Height", "Weight", ...],
  "target_classes": {
    "0": "insufficient_weight",
    "1": "normal_weight",
    ...
  },
  "trained_date": "2025-11-11"
}
```

---

### 5. Explicabilidad (SHAP)

Explica qué features contribuyen más a la predicción.

**Request**
```bash
POST /explain
Content-Type: application/json
```

**Body**
```json
{
  "instance": {
    "Age": 25.0,
    "Height": 1.75,
    "Weight": 70.0,
    ...
  },
  "explain_type": "shap"
}
```

**Response** (200)
```json
{
  "prediction": "normal_weight",
  "feature_contributions": {
    "Weight": 0.1234,
    "Height": -0.0567,
    "BMI": 0.0891,
    "Age": 0.0234,
    "FAF": -0.0123,
    ...
  },
  "explain_type": "shap"
}
```

**Interpretación de SHAP:**
- **Valores positivos**: Aumentan la probabilidad de la clase predicha
- **Valores negativos**: Disminuyen la probabilidad de la clase predicha
- **Magnitud**: Indica la importancia de la contribución

**Tipos de explicación:**
- `"shap"`: Valores SHAP específicos para la instancia (requiere SHAP instalado)
- `"feature_importance"`: Importancia global de features del modelo

---

## 🔧 Validaciones de Campos

### Campos Numéricos

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| `Age` | float | 1-120 | Edad en años |
| `Height` | float | 0.5-2.5 | Altura en metros |
| `Weight` | float | 20-300 | Peso en kilogramos |
| `FCVC` | float | 0-3 | Frecuencia consumo vegetales |
| `NCP` | float | 1-4 | Número comidas principales |
| `CH2O` | float | 0-3 | Consumo agua diario (litros) |
| `FAF` | float | 0-3 | Frecuencia actividad física |
| `TUE` | float | 0-2 | Tiempo usando tecnología (horas) |

### Campos Categóricos (Enums)

#### Gender
- `"male"`
- `"female"`

#### YesNo (family_history_with_overweight, FAVC, SMOKE, SCC)
- `"yes"`
- `"no"`

#### Frequency (CAEC, CALC)
- `"no"`
- `"sometimes"`
- `"frequently"`
- `"always"`

#### Transport (MTRANS)
- `"automobile"`
- `"motorbike"`
- `"bike"`
- `"public_transportation"`
- `"walking"`

---

## 🐳 Docker - Configuración Avanzada

### Variables de Entorno

```env
LOG_LEVEL=info           # Nivel de logging (debug, info, warning, error)
MODEL_PATH=/app/artefactos/pipelines_optimizados.joblib
WORKERS=1                # Número de workers uvicorn
```

### Personalizar Docker Compose

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - LOG_LEVEL=debug
      - WORKERS=2
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Health Check

Docker incluye health check automático cada 30s:
```bash
# Verificar salud del contenedor
docker inspect --format='{{.State.Health.Status}}' obesity-api
```

---

## ☁️ Deployment en Google Cloud Platform (GCP)

### Opción 1: Cloud Run (Serverless)

```bash
# 1. Autenticar con GCP
gcloud auth login

# 2. Configurar proyecto
gcloud config set project YOUR_PROJECT_ID

# 3. Build y push a Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/obesity-api

# 4. Deploy a Cloud Run
gcloud run deploy obesity-api \
  --image gcr.io/YOUR_PROJECT_ID/obesity-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2
```

### Opción 2: Google Kubernetes Engine (GKE)

```bash
# 1. Crear cluster
gcloud container clusters create obesity-cluster \
  --num-nodes=2 \
  --zone=us-central1-a

# 2. Configurar kubectl
gcloud container clusters get-credentials obesity-cluster --zone=us-central1-a

# 3. Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Opción 3: Compute Engine (VM)

```bash
# 1. Crear instancia
gcloud compute instances create obesity-api-vm \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --zone=us-central1-a \
  --machine-type=e2-medium

# 2. SSH y configurar Docker
gcloud compute ssh obesity-api-vm

# 3. Copiar código y ejecutar docker-compose
```

---

## 🧪 Testing

### Ejecutar Tests de la API

```powershell
# Instalar dependencias de testing
pip install pytest httpx

# Ejecutar tests
pytest tests/test_api.py -v

# Con cobertura
pytest tests/test_api.py --cov=api --cov-report=html
```

### Tests Disponibles

- ✅ Health check endpoint
- ✅ Predicción individual con datos válidos
- ✅ Validación de campos (Age, Height, Weight, etc.)
- ✅ Predicción por lote
- ✅ Límite de 100 instancias en batch
- ✅ Información del modelo
- ✅ Explicabilidad SHAP
- ✅ Manejo de errores 422 (validación)

---

## 📊 Monitoreo y Logs

### Ver Logs (Docker)

```bash
# Logs en tiempo real
docker logs -f obesity-api

# Últimas 100 líneas
docker logs --tail 100 obesity-api

# Logs con timestamps
docker logs -t obesity-api
```

### Logs de Uvicorn

La API genera logs estructurados:
```
INFO: Started server process [1]
INFO: Waiting for application startup.
INFO: Iniciando servicio de predicción...
INFO: Modelo cargado exitosamente
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## ❗ Troubleshooting

### Problema: Modelo no carga

**Síntoma**: `/health` retorna `"model_loaded": false`

**Solución**:
```bash
# Verificar que el archivo del modelo existe
ls -la artefactos/pipelines_optimizados.joblib

# Verificar permisos
chmod 644 artefactos/pipelines_optimizados.joblib

# Revisar logs
docker logs obesity-api | grep "Error cargando modelo"
```

### Problema: Error 422 en predicción

**Síntoma**: `422 Unprocessable Entity`

**Solución**: Verificar que todos los campos cumplen validaciones:
- Age: 1-120
- Height: 0.5-2.5 metros
- Weight: 20-300 kg
- Gender: "male" o "female"
- Campos Yes/No: "yes" o "no" (no "Yes" o "YES")

### Problema: SHAP no disponible

**Síntoma**: Explicación retorna `feature_importance` en lugar de `shap`

**Solución**:
```bash
# Verificar instalación de SHAP
pip install shap==0.47.2

# O en Docker, rebuild imagen
docker-compose build --no-cache
```

### Problema: Docker build falla

**Síntoma**: Error durante `docker build`

**Solución**:
```bash
# Limpiar cache de Docker
docker system prune -a

# Build sin cache
docker build --no-cache -t obesity-api:latest .

# Verificar espacio en disco
docker system df
```

### Problema: Puerto 8000 ocupado

**Síntoma**: `Error: address already in use`

**Solución**:
```powershell
# Windows: Encontrar proceso usando puerto 8000
netstat -ano | findstr :8000

# Matar proceso (reemplazar PID)
taskkill /PID <PID> /F

# O usar puerto diferente
docker run -p 8080:8000 obesity-api:latest
```

---

## 📈 Performance y Optimización

### Benchmarks Esperados

Con hardware estándar (2 CPU, 2GB RAM):
- **Predicción individual**: ~50-100ms
- **Batch (100 instancias)**: ~1-2s
- **Explicación SHAP**: ~200-500ms

### Optimizaciones

1. **Aumentar workers Uvicorn**:
```bash
uvicorn api.app:app --workers 4
```

2. **Cachear predicciones** (implementación futura con Redis)

3. **Batch processing** para alta carga

---

## 🔐 Seguridad

### Recomendaciones para Producción

1. **Autenticación**: Agregar API keys o JWT
2. **Rate limiting**: Limitar requests por IP
3. **HTTPS**: Usar certificados SSL/TLS
4. **Secrets**: Variables sensibles en entorno, no código
5. **CORS**: Restringir origins permitidos

```python
# Ejemplo CORS restrictivo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # No "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 📝 Notas Adicionales

### Clases de Obesidad

| Código | Clase | BMI Range |
|--------|-------|-----------|
| 0 | insufficient_weight | < 18.5 |
| 1 | normal_weight | 18.5-24.9 |
| 2 | overweight_level_i | 25-27.4 |
| 3 | overweight_level_ii | 27.5-29.9 |
| 4 | obesity_type_i | 30-34.9 |
| 5 | obesity_type_ii | 35-39.9 |
| 6 | obesity_type_iii | ≥ 40 |

### Actualizaciones del Modelo

Para actualizar el modelo sin rebuild:
```bash
# 1. Reemplazar archivo del modelo
cp nuevo_modelo.joblib artefactos/pipelines_optimizados.joblib

# 2. Reiniciar contenedor
docker-compose restart api
```

---

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [Docker Documentation](https://docs.docker.com/)
- [GCP Cloud Run](https://cloud.google.com/run/docs)

---

## 🤝 Soporte

Para problemas o dudas:
1. Revisar logs: `docker logs obesity-api`
2. Verificar health: `curl http://localhost:8000/health`
3. Consultar documentación interactiva: http://localhost:8000/docs

---

**Versión**: 1.0.0  
**Última actualización**: 2025-01-11

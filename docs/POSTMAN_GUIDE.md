# Guía de Uso con Postman - API de Predicción de Obesidad

## 🚀 Configuración Inicial

### 1. Verificar que la API está corriendo

Asegúrate de que el contenedor Docker está activo:
```powershell
docker ps
```

Deberías ver algo como:
```
CONTAINER ID   IMAGE               STATUS                 PORTS
47c3e93bdfb9   obesitymine53-api   Up (healthy)          0.0.0.0:8000->8000/tcp
```

Si no está corriendo:
```powershell
docker-compose up -d
```

---

## 📡 Endpoints en Postman

### 1. Health Check - Verificar Estado del Servicio

**Método:** `GET`  
**URL:** `http://localhost:8000/health`

**Headers:** Ninguno necesario

**Body:** Ninguno

**Respuesta esperada (200 OK):**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "XGBoost",
  "model_version": "2.0.3",
  "api_version": "1.0.0",
  "message": "Servicio operativo"
}
```

**Pasos en Postman:**
1. Crear nueva request
2. Método: GET
3. URL: `http://localhost:8000/health`
4. Click en "Send"

---

### 2. Predicción Individual - POST /predict

**Método:** `POST`  
**URL:** `http://localhost:8000/predict`

**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
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

**Respuesta esperada (200 OK):**
```json
{
  "prediction": "normal_weight",
  "prediction_code": 1,
  "confidence": 0.1785,
  "probabilities": {
    "insufficient_weight": 0.1362,
    "normal_weight": 0.1785,
    "overweight_level_i": 0.139,
    "overweight_level_ii": 0.1366,
    "obesity_type_i": 0.1368,
    "obesity_type_ii": 0.1367,
    "obesity_type_iii": 0.1361
  },
  "bmi": 22.86
}
```

**Pasos en Postman:**
1. Crear nueva request
2. Método: POST
3. URL: `http://localhost:8000/predict`
4. Tab "Headers": Agregar `Content-Type` = `application/json`
5. Tab "Body": Seleccionar "raw" y "JSON"
6. Pegar el JSON del body
7. Click en "Send"

---

### 3. Predicción por Lote - POST /predict_batch

**Método:** `POST`  
**URL:** `http://localhost:8000/predict_batch`

**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "instances": [
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
    },
    {
      "Age": 30.0,
      "Height": 1.65,
      "Weight": 55.0,
      "Gender": "female",
      "family_history_with_overweight": "no",
      "FAVC": "no",
      "FCVC": 3.0,
      "NCP": 3.0,
      "CAEC": "no",
      "SMOKE": "no",
      "CH2O": 2.5,
      "SCC": "yes",
      "FAF": 3.0,
      "TUE": 0.5,
      "CALC": "no",
      "MTRANS": "walking"
    }
  ]
}
```

**Respuesta esperada (200 OK):**
```json
{
  "predictions": [
    {
      "prediction": "normal_weight",
      "prediction_code": 1,
      "confidence": 0.1785,
      "probabilities": {...},
      "bmi": 22.86
    },
    {
      "prediction": "insufficient_weight",
      "prediction_code": 0,
      "confidence": 0.1567,
      "probabilities": {...},
      "bmi": 20.20
    }
  ]
}
```

**Pasos en Postman:**
1. Crear nueva request
2. Método: POST
3. URL: `http://localhost:8000/predict_batch`
4. Tab "Headers": Agregar `Content-Type` = `application/json`
5. Tab "Body": Seleccionar "raw" y "JSON"
6. Pegar el JSON del body (con array de instances)
7. Click en "Send"

**Nota:** Máximo 100 instancias por request

---

### 4. Información del Modelo - GET /model_info

**Método:** `GET`  
**URL:** `http://localhost:8000/model_info`

**Headers:** Ninguno necesario

**Body:** Ninguno

**Respuesta esperada (200 OK):**
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
  "features": [
    "Age", "Height", "Weight", "Gender",
    "family_history_with_overweight", "FAVC",
    "FCVC", "NCP", "CAEC", "SMOKE",
    "CH2O", "SCC", "FAF", "TUE", "CALC", "MTRANS"
  ],
  "target_classes": {
    "0": "insufficient_weight",
    "1": "normal_weight",
    "2": "overweight_level_i",
    "3": "overweight_level_ii",
    "4": "obesity_type_i",
    "5": "obesity_type_ii",
    "6": "obesity_type_iii"
  },
  "trained_date": "2025-11-11"
}
```

**Pasos en Postman:**
1. Crear nueva request
2. Método: GET
3. URL: `http://localhost:8000/model_info`
4. Click en "Send"

---

### 5. Explicabilidad SHAP - POST /explain

**Método:** `POST`  
**URL:** `http://localhost:8000/explain`

**Headers:**
- `Content-Type: application/json`

**Body (raw JSON):**
```json
{
  "instance": {
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
  },
  "explain_type": "shap"
}
```

**Opciones para `explain_type`:**
- `"shap"` - Valores SHAP específicos para la instancia
- `"feature_importance"` - Importancia global de features

**Respuesta esperada (200 OK):**
```json
{
  "prediction": "normal_weight",
  "feature_contributions": {
    "Weight": 0.1234,
    "Height": -0.0567,
    "Age": 0.0234,
    "FAF": -0.0123,
    "FCVC": -0.0089,
    "Gender": 0.0045,
    "family_history_with_overweight": 0.0012,
    "FAVC": 0.0008,
    "NCP": 0.0005,
    "CAEC": 0.0003,
    "SMOKE": 0.0001,
    "CH2O": -0.0002,
    "SCC": -0.0003,
    "TUE": -0.0004,
    "CALC": -0.0005,
    "MTRANS": -0.0006
  },
  "explain_type": "shap"
}
```

**Interpretación:**
- **Valores positivos**: Aumentan probabilidad de la clase predicha
- **Valores negativos**: Disminuyen probabilidad de la clase predicha
- Los valores están ordenados por importancia (magnitud)

**Pasos en Postman:**
1. Crear nueva request
2. Método: POST
3. URL: `http://localhost:8000/explain`
4. Tab "Headers": Agregar `Content-Type` = `application/json`
5. Tab "Body": Seleccionar "raw" y "JSON"
6. Pegar el JSON del body
7. Click en "Send"

---

### 6. Documentación Interactiva (Swagger)

**Método:** Abrir en navegador  
**URL:** `http://localhost:8000/docs`

Aquí podrás:
- Ver todos los endpoints disponibles
- Probar cada endpoint directamente desde el navegador
- Ver ejemplos de request/response
- Descargar especificación OpenAPI

---

## 🔧 Crear Colección en Postman

### Importar Collection Automática

1. Abre Postman
2. Click en "Import"
3. Selecciona "Link"
4. Pega: `http://localhost:8000/openapi.json`
5. Click "Continue" e "Import"

Esto creará automáticamente una colección con todos los endpoints.

### O Crear Colección Manual

1. **Crear nueva Collection:**
   - Click en "New" → "Collection"
   - Nombre: "Obesity API"
   - Description: "API de predicción de obesidad con XGBoost"

2. **Agregar requests:**
   - Click derecho en la colección → "Add request"
   - Configura cada endpoint según las secciones anteriores

3. **Variables de entorno:**
   - Click en el ícono de ojo (Environment quick look)
   - Click "Add" para crear nuevo entorno
   - Nombre: "Local"
   - Agregar variable:
     - Key: `base_url`
     - Value: `http://localhost:8000`
   - Usar en requests: `{{base_url}}/predict`

---

## 📋 Ejemplos de Casos de Uso

### Caso 1: Persona con Peso Normal
```json
{
  "Age": 25,
  "Height": 1.75,
  "Weight": 70,
  "Gender": "male",
  "family_history_with_overweight": "no",
  "FAVC": "no",
  "FCVC": 3,
  "NCP": 3,
  "CAEC": "no",
  "SMOKE": "no",
  "CH2O": 2.5,
  "SCC": "yes",
  "FAF": 3,
  "TUE": 0.5,
  "CALC": "no",
  "MTRANS": "walking"
}
```

### Caso 2: Persona con Obesidad
```json
{
  "Age": 45,
  "Height": 1.60,
  "Weight": 100,
  "Gender": "female",
  "family_history_with_overweight": "yes",
  "FAVC": "yes",
  "FCVC": 1,
  "NCP": 4,
  "CAEC": "frequently",
  "SMOKE": "no",
  "CH2O": 1,
  "SCC": "no",
  "FAF": 0,
  "TUE": 2,
  "CALC": "frequently",
  "MTRANS": "automobile"
}
```

### Caso 3: Persona Activa
```json
{
  "Age": 30,
  "Height": 1.80,
  "Weight": 75,
  "Gender": "male",
  "family_history_with_overweight": "no",
  "FAVC": "no",
  "FCVC": 3,
  "NCP": 3,
  "CAEC": "sometimes",
  "SMOKE": "no",
  "CH2O": 3,
  "SCC": "yes",
  "FAF": 3,
  "TUE": 0.5,
  "CALC": "no",
  "MTRANS": "bike"
}
```

---

## ⚠️ Validaciones y Errores Comunes

### Error 422: Validation Error

**Causa:** Datos de entrada inválidos

**Ejemplo de error:**
```json
{
  "detail": [
    {
      "type": "float_parsing",
      "loc": ["body", "Age"],
      "msg": "Input should be a valid number",
      "input": "veinte"
    }
  ]
}
```

**Validaciones:**
- `Age`: 1-120
- `Height`: 0.5-2.5 (metros)
- `Weight`: 20-300 (kg)
- `Gender`: solo "male" o "female"
- Campos Yes/No: solo "yes" o "no" (minúsculas)
- `FCVC`, `CH2O`, `FAF`: 0-3
- `NCP`: 1-4
- `TUE`: 0-2

### Error 503: Service Unavailable

**Causa:** Modelo no cargado

**Solución:**
```powershell
# Revisar logs
docker logs obesity-api

# Reiniciar contenedor
docker-compose restart api
```

### Error 500: Internal Server Error

**Causa:** Error en el procesamiento

**Solución:** Revisar logs del contenedor

---

## 🎯 Tips para Postman

1. **Guardar respuestas como ejemplos:**
   - Después de recibir una respuesta exitosa
   - Click en "Save Response" → "Save as example"
   - Te ayuda a documentar la API

2. **Tests automáticos:**
   - Tab "Tests" en cada request
   - Ejemplo:
   ```javascript
   pm.test("Status code is 200", function () {
       pm.response.to.have.status(200);
   });
   
   pm.test("Response has prediction", function () {
       var jsonData = pm.response.json();
       pm.expect(jsonData).to.have.property('prediction');
   });
   ```

3. **Pre-request Scripts:**
   - Tab "Pre-request Script"
   - Generar datos aleatorios:
   ```javascript
   pm.environment.set("random_age", Math.floor(Math.random() * 60) + 20);
   pm.environment.set("random_weight", Math.floor(Math.random() * 50) + 50);
   ```

4. **Collection Runner:**
   - Click en la colección → "Run"
   - Ejecuta todos los requests secuencialmente
   - Útil para testing automatizado

---

## 📚 Recursos Adicionales

- **Documentación Swagger:** http://localhost:8000/docs
- **Documentación ReDoc:** http://localhost:8000/redoc
- **OpenAPI Schema:** http://localhost:8000/openapi.json

---

**Última actualización:** 2025-11-11

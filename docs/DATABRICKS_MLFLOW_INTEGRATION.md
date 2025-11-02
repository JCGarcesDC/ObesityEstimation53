# Integración MLflow con Databricks

## Resumen de la Implementación

Esta documentación describe la integración exitosa de MLflow con Databricks para el proyecto ObesityMine53, donde se implementó un pipeline completo de machine learning con tracking automático de experimentos y modelos.

## Arquitectura de la Solución

### Componentes Principales

1. **Databricks Workspace**: https://dbc-cb01d0d2-09c5.cloud.databricks.com
2. **MLflow Tracking Server**: Integrado en Databricks
3. **Unity Catalog**: Sistema de metadatos moderno
4. **Experimento MLflow**: `/Shared/ObesityEstimation`

### Configuración de Credenciales

Archivo: `config/credentials.yaml`

```yaml
# Databricks credentials
databricks:
  token: "inserta_tu_token_real_aqui"
  host: "https://dbc-cb01d0d2-09c5.cloud.databricks.com"

# MLflow configuration
mlflow:
  experiment_name: "/Shared/ObesityEstimation"
  tracking_uri: "databricks"
```

## Implementación Técnica

### 1. Configuración de la Conexión

```python
import mlflow
import mlflow.sklearn
import mlflow.xgboost
from src.utils.databricks_utils import get_databricks_config

# Configurar la conexión a Databricks
config = get_databricks_config()
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment(config['mlflow']['experiment_name'])
```

### 2. Logging de Modelos y Métricas

```python
# Ejemplo de logging para cada modelo
with mlflow.start_run(run_name=f"{model_name}_obesity_estimation"):
    # Log del modelo
    if model_name == 'XGBoost':
        mlflow.xgboost.log_model(model, "model")
    else:
        mlflow.sklearn.log_model(model, "model")
    
    # Log de métricas
    mlflow.log_metrics({
        "accuracy_train": accuracy_train,
        "accuracy_test": accuracy_test,
        "f1_train": f1_train,
        "f1_test": f1_test,
        "precision_test": precision_test,
        "recall_test": recall_test
    })
    
    # Log de parámetros del modelo
    mlflow.log_params(model.get_params())
```

## Resultados de la Implementación

### Modelos Entrenados y Trackeados

| Modelo | F1-Score (Test) | Accuracy (Test) | Estado MLflow |
|--------|----------------|-----------------|---------------|
| Random Forest | 0.9394 | 0.9394 | ✅ Logged |
| XGBoost | **0.9426** | **0.9455** | ✅ Logged |
| Gradient Boosting | 0.9333 | 0.9394 | ✅ Logged |
| AdaBoost | 0.9121 | 0.9152 | ✅ Logged |
| SVM | 0.9242 | 0.9273 | ✅ Logged |
| Logistic Regression | 0.9061 | 0.9091 | ✅ Logged |
| Naive Bayes | 0.8606 | 0.8727 | ✅ Logged |

**Mejor Modelo**: XGBoost con F1-Score de 94.26% y Accuracy de 94.55%

### Métricas Detalladas del Mejor Modelo (XGBoost)

- **Accuracy Train**: 99.62%
- **Accuracy Test**: 94.55%
- **F1-Score Train**: 99.62%
- **F1-Score Test**: 94.26%
- **Precision Test**: 94.55%
- **Recall Test**: 94.55%

## URLs y Enlaces Importantes

### Databricks Workspace
- **URL Principal**: https://dbc-cb01d0d2-09c5.cloud.databricks.com
- **Experimento MLflow**: https://dbc-cb01d0d2-09c5.cloud.databricks.com/#mlflow/experiments

### Experimento Específico
- **Nombre**: `/Shared/ObesityEstimation`
- **Descripción**: Comparación de 7 modelos de ML para estimación de obesidad
- **Runs Totales**: 7 (uno por cada modelo)

## Resolución de Problemas Encontrados

### 1. Error de Experimento No Encontrado
**Problema**: `RestException: RESOURCE_DOES_NOT_EXIST: Experiment '/Users/.../ObesityEstimation' not found`

**Solución**: Cambiar la ruta del experimento a `/Shared/ObesityEstimation`

```python
# Antes (incorrecto)
mlflow.set_experiment("/Users/user/ObesityEstimation")

# Después (correcto)
mlflow.set_experiment("/Shared/ObesityEstimation")
```

### 2. Error de Unity Catalog
**Problema**: `MlflowException: The registered_model_name argument is not supported when using the Unity Catalog.`

**Solución**: Remover el parámetro `registered_model_name` del logging

```python
# Antes (incorrecto)
mlflow.sklearn.log_model(model, "model", registered_model_name="obesity_model")

# Después (correcto)
mlflow.sklearn.log_model(model, "model")
```

### 3. Error de Mapeo de Columnas
**Problema**: Nombres de columnas no coincidían con el DataFrame de resultados

**Solución**: Verificar y corregir los nombres exactos de las columnas del DataFrame

```python
# Verificar columnas disponibles
print("Columnas del DataFrame:", df_results.columns.tolist())

# Usar nombres exactos
f1_test = df_results.loc[df_results['Modelo'] == model_name, 'F1-Score (Test)'].iloc[0]
```

## Configuración del Entorno

### Dependencias Principales
```txt
mlflow>=2.0.0
databricks-cli
pandas
scikit-learn
xgboost
numpy
```

### Variables de Entorno
```bash
# Configurar Databricks CLI (opcional)
export DATABRICKS_HOST="https://dbc-cb01d0d2-09c5.cloud.databricks.com"
export DATABRICKS_TOKEN="your_token_here"
```

## Estructura de Archivos Modificados

```
ObesityMine53/
├── config/
│   └── credentials.yaml          # Credenciales de Databricks
├── src/
│   └── utils/
│       └── databricks_utils.py   # Utilidades de conexión
├── notebooks/
│   └── 3. Model Building, Tuning, and Evaluation/
│       └── 3.1_model_building_and_tuning.ipynb  # Notebook principal
└── docs/
    ├── DATABRICKS_MLFLOW_INTEGRATION.md        # Esta documentación
    ├── DATABRICKS_TECHNICAL_GUIDE.md           # Guía técnica
    └── README.md                               # Índice general
```

## Próximos Pasos

1. **Optimización de Hiperparámetros**: Usar MLflow para tracking de hyperparameter tuning
2. **Model Registry**: Registrar el mejor modelo en Unity Catalog
3. **Deployment**: Configurar serving del modelo desde Databricks
4. **Monitoring**: Implementar monitoring de drift de datos y modelos

## Conclusiones

La integración MLflow-Databricks fue exitosa y permite:

- ✅ Tracking automático de todos los experimentos
- ✅ Comparación visual de modelos en la UI de MLflow
- ✅ Almacenamiento centralizado de artefactos
- ✅ Reproducibilidad completa de experimentos
- ✅ Colaboración mejorada entre equipos
- ✅ Preparación para producción con Unity Catalog

El pipeline completo procesó exitosamente 7 modelos diferentes, identificando XGBoost como el mejor performer con un F1-Score de 94.26% en el conjunto de prueba.
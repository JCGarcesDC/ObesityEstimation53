# Guía Técnica: Implementación Databricks + MLflow

## Introducción

Esta guía proporciona instrucciones paso a paso para replicar la integración de MLflow con Databricks en cualquier proyecto de machine learning.

## Prerrequisitos

### Software Requerido
- Python 3.8+
- Jupyter Notebook o JupyterLab
- Git
- Cuenta de Databricks (Community o Workspace)

### Dependencias Python
```bash
pip install mlflow>=2.0.0
pip install databricks-cli
pip install pandas scikit-learn xgboost numpy
```

## Configuración Inicial

### 1. Configuración de Databricks

#### Obtener Token de Acceso
1. Accede a tu workspace de Databricks
2. Ve a Settings > User Settings
3. Genera un nuevo Personal Access Token
4. Copia y guarda el token de forma segura

#### Configurar Workspace
1. Crea un directorio compartido: `/Shared/tu_proyecto`
2. Configura permisos de escritura para tu usuario
3. Verifica que Unity Catalog esté habilitado (si está disponible)

### 2. Estructura de Archivos del Proyecto

```
tu_proyecto/
├── config/
│   └── credentials.yaml
├── src/
│   └── utils/
│       └── databricks_utils.py
├── notebooks/
│   └── experimento_principal.ipynb
└── data/
    └── tu_dataset.csv
```

### 3. Configuración de Credenciales

Crear `config/credentials.yaml`:
```yaml
# Databricks credentials
databricks:
  token: "inserta_tu_token_real_aqui"
  host: "https://tu-workspace.cloud.databricks.com"

# MLflow configuration
mlflow:
  experiment_name: "/Shared/tu_proyecto/experimentos"
  tracking_uri: "databricks"
```

### 4. Utilidades de Conexión

Crear `src/utils/databricks_utils.py`:
```python
import yaml
import os
from pathlib import Path

def get_databricks_config():
    """
    Carga la configuración de Databricks desde el archivo credentials.yaml
    """
    # Buscar el archivo de configuración
    config_path = Path(__file__).parent.parent.parent / "config" / "credentials.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    return config

def setup_databricks_env():
    """
    Configura las variables de entorno para Databricks
    """
    config = get_databricks_config()
    
    os.environ['DATABRICKS_HOST'] = config['databricks']['host']
    os.environ['DATABRICKS_TOKEN'] = config['databricks']['token']
    
    return config

def test_databricks_connection():
    """
    Prueba la conexión a Databricks
    """
    try:
        import mlflow
        
        config = setup_databricks_env()
        mlflow.set_tracking_uri("databricks")
        
        # Intentar crear o acceder al experimento
        experiment = mlflow.set_experiment(config['mlflow']['experiment_name'])
        print(f"✅ Conexión exitosa a Databricks")
        print(f"🎯 Experimento: {config['mlflow']['experiment_name']}")
        print(f"🆔 Experiment ID: {experiment.experiment_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False
```

## Implementación en Notebook

### 1. Configuración Inicial del Notebook

```python
# Importaciones necesarias
import mlflow
import mlflow.sklearn
import mlflow.xgboost
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Importar utilidades personalizadas
import sys
sys.path.append('../src')
from utils.databricks_utils import setup_databricks_env, test_databricks_connection

# Configurar la conexión
print("🔧 Configurando conexión a Databricks...")
config = setup_databricks_env()

# Probar la conexión
test_databricks_connection()

# Configurar MLflow
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment(config['mlflow']['experiment_name'])
```

### 2. Preparación de Datos

```python
# Cargar y preparar datos
df = pd.read_csv('../data/tu_dataset.csv')
X = df.drop('target_column', axis=1)
y = df['target_column']

# División de datos
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"📊 Datos preparados:")
print(f"   Train: {X_train.shape[0]} muestras")
print(f"   Test: {X_test.shape[0]} muestras")
```

### 3. Entrenamiento y Logging de Modelos

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

# Definir modelos a entrenar
models = {
    'Random Forest': RandomForestClassifier(random_state=42),
    'Logistic Regression': LogisticRegression(random_state=42),
    'XGBoost': XGBClassifier(random_state=42)
}

# Entrenar y trackear cada modelo
results = []

for model_name, model in models.items():
    print(f"\n🚀 Entrenando {model_name}...")
    
    with mlflow.start_run(run_name=f"{model_name}_experiment"):
        # Entrenar modelo
        model.fit(X_train, y_train)
        
        # Predicciones
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Calcular métricas
        accuracy_train = accuracy_score(y_train, y_pred_train)
        accuracy_test = accuracy_score(y_test, y_pred_test)
        f1_train = f1_score(y_train, y_pred_train, average='weighted')
        f1_test = f1_score(y_test, y_pred_test, average='weighted')
        precision_test = precision_score(y_test, y_pred_test, average='weighted')
        recall_test = recall_score(y_test, y_pred_test, average='weighted')
        
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
        
        # Log de parámetros
        mlflow.log_params(model.get_params())
        
        # Guardar resultados
        results.append({
            'Modelo': model_name,
            'Accuracy (Train)': round(accuracy_train, 4),
            'Accuracy (Test)': round(accuracy_test, 4),
            'F1-Score (Train)': round(f1_train, 4),
            'F1-Score (Test)': round(f1_test, 4),
            'Precision (Test)': round(precision_test, 4),
            'Recall (Test)': round(recall_test, 4)
        })
        
        print(f"   ✅ {model_name} completado - F1: {f1_test:.4f}")

# Mostrar resultados
df_results = pd.DataFrame(results)
print("\n📈 Resumen de Resultados:")
print(df_results.to_string(index=False))
```

## Verificación y Monitoreo

### 1. Verificar Experimentos en Databricks

```python
# Obtener información del experimento actual
current_experiment = mlflow.get_experiment_by_name(config['mlflow']['experiment_name'])
print(f"🎯 Experimento: {current_experiment.name}")
print(f"🆔 ID: {current_experiment.experiment_id}")
print(f"🔗 URL: {config['databricks']['host']}/#mlflow/experiments/{current_experiment.experiment_id}")

# Listar runs recientes
runs = mlflow.search_runs(experiment_ids=[current_experiment.experiment_id])
print(f"\n📋 Runs encontrados: {len(runs)}")
print(runs[['run_name', 'status', 'start_time']].head())
```

### 2. Análisis del Mejor Modelo

```python
# Encontrar el mejor modelo por F1-Score
best_run = runs.loc[runs['metrics.f1_test'].idxmax()]
print(f"\n🏆 Mejor Modelo:")
print(f"   Nombre: {best_run['tags.mlflow.runName']}")
print(f"   F1-Score: {best_run['metrics.f1_test']:.4f}")
print(f"   Accuracy: {best_run['metrics.accuracy_test']:.4f}")
print(f"   Run ID: {best_run['run_id']}")
```

## Troubleshooting

### Errores Comunes y Soluciones

#### 1. Error de Autenticación
```
Error: Invalid token
```
**Solución**: Verificar que el token esté correctamente configurado y no haya expirado.

#### 2. Experimento No Encontrado
```
RESOURCE_DOES_NOT_EXIST: Experiment not found
```
**Solución**: Verificar que la ruta del experimento existe y tienes permisos de acceso.

#### 3. Error de Unity Catalog
```
The registered_model_name argument is not supported when using Unity Catalog
```
**Solución**: Remover el parámetro `registered_model_name` del log del modelo.

#### 4. Error de Conexión
```
Cannot connect to Databricks
```
**Solución**: Verificar la URL del host y la conectividad de red.

### Script de Diagnóstico

```python
def diagnose_setup():
    """
    Script de diagnóstico para verificar la configuración
    """
    checks = []
    
    # Verificar archivo de configuración
    try:
        config = get_databricks_config()
        checks.append("✅ Archivo de configuración cargado")
    except Exception as e:
        checks.append(f"❌ Error en configuración: {e}")
        return checks
    
    # Verificar conexión a Databricks
    try:
        import mlflow
        mlflow.set_tracking_uri("databricks")
        checks.append("✅ Conexión a MLflow establecida")
    except Exception as e:
        checks.append(f"❌ Error de conexión MLflow: {e}")
    
    # Verificar experimento
    try:
        exp = mlflow.set_experiment(config['mlflow']['experiment_name'])
        checks.append(f"✅ Experimento accesible: {exp.experiment_id}")
    except Exception as e:
        checks.append(f"❌ Error de experimento: {e}")
    
    return checks

# Ejecutar diagnóstico
print("🔍 Ejecutando diagnóstico del sistema:")
for check in diagnose_setup():
    print(f"   {check}")
```

## Best Practices

1. **Seguridad**: Nunca commitear tokens en Git
2. **Naming**: Usar nombres descriptivos para runs y experimentos
3. **Organización**: Agrupar experimentos por proyecto
4. **Reproducibilidad**: Siempre configurar random_state
5. **Monitoring**: Revisar regularmente los experimentos en la UI de Databricks

## Recursos Adicionales

- [Documentación de MLflow](https://mlflow.org/docs/latest/)
- [Guía de Databricks MLflow](https://docs.databricks.com/mlflow/index.html)
- [Unity Catalog Documentation](https://docs.databricks.com/data-governance/unity-catalog/index.html)
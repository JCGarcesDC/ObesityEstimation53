# Documentación paso a paso: Notebook 3.1 Model Building, Tuning, and Evaluation

Este documento explica cada paso del notebook `3.1_model_building_and_tuning.ipynb`, asegurando claridad, reproducibilidad y buenas prácticas para terceros. Se incluye el mapeo al archivo de pipelines en `src/pipelines.py` y recomendaciones para replicabilidad.

---

## 1. Roles y responsabilidades

Al inicio del notebook se especifican los roles involucrados:
- **Data Engineer**: Adquisición, integración y calidad de datos.
- **Data Scientist**: Análisis exploratorio, definición de variables, validación y extracción de insights.
- **ML Engineer**: Implementación de pipelines, optimización y reproducibilidad.
- **Software Engineer**: Estructura modular, calidad de código, automatización y CI/CD.

## 2. Importación de librerías y entorno

Se importan librerías estándar y se imprime la versión de cada una para asegurar reproducibilidad:
```python
import sys
import pandas as pd
import sklearn
import numpy as np
print(sys.version)
print('pandas', pd.__version__)
print('scikit-learn', sklearn.__version__)
print('numpy', np.__version__)
```
**Mejor práctica:** Documentar versiones y dependencias en `requirements.txt`.

## 3. Configuración de rutas y carga de funciones

Se configura la ruta raíz y se importan funciones desde `src`:
```python
ruta_raiz_proyecto = os.path.abspath(os.path.join(os.getcwd(), '../../'))
sys.path.append(ruta_raiz_proyecto)
from src.cargar_analisis import cargar_dataframe, crear_listas_variables
from src.pipelines import preparar_datos_para_modelado
from src.modelos import obtener_configuraciones_modelos, optimizar_y_comparar_modelos, guardar_artefactos_ml
```
**Mapeo:** El pipeline principal se encuentra en `src/pipelines.py`.

## 4. Carga de datos

Se carga el dataset y se generan listas de variables:
```python
path_data = '../../data/obesity_estimation_model.csv'
df = cargar_dataframe(path_data)
variables_numericas, variables_categoricas, variable_objetivo = crear_listas_variables(to_lower=1, exclude_mixed=1)
```
**Mejor práctica:** Validar la integridad y formato del archivo antes de procesar.

## 5. Preprocesamiento con pipelines

Se utiliza la función `preparar_datos_para_modelado` de `src/pipelines.py` para dividir y transformar los datos:
```python
X_train, X_test, y_train, y_test, preprocesador = preparar_datos_para_modelado(df, variable_objetivo, 0.2, 1)
```
**Mapeo:** Esta función encapsula la lógica de preprocesamiento y asegura reproducibilidad.

## 6. Configuración y evaluación de modelos

Se obtienen configuraciones y se realiza optimización:
```python
configuracion_modelos = obtener_configuraciones_modelos()
df_resultados_opt, pipelines_optimizados = optimizar_y_comparar_modelos(
    configuracion_modelos,
    preprocesador,
    X_train, y_train, X_test, y_test
)
```
**Mejor práctica:** Documentar los hiperparámetros y guardar los resultados para trazabilidad.

## 7. Guardado de artefactos

Se guardan los resultados y pipelines optimizados:
```python
guardar_artefactos_ml(
    df_resultados=df_resultados_opt,
    pipelines=pipelines_optimizados,
    base_path='../../artefactos/'
)
```
**Mejor práctica:** Usar rutas relativas y carpetas separadas para artefactos y modelos.

---

## Recomendaciones de buenas prácticas
- Mantener la documentación actualizada y clara.
- Versionar los notebooks y scripts.
- Usar funciones modulares y reutilizables (ver `src/pipelines.py`).
- Validar entradas y salidas en cada paso.
- Automatizar pruebas y validaciones.
- Registrar dependencias y versiones.

---

**Este documento facilita la comprensión y replicabilidad del notebook 3.1, mapeando cada paso al código fuente y asegurando que terceros puedan seguir el flujo sin ambigüedades.**

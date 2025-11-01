# Manipulación de datos
import pandas as pd
import numpy as np
from typing import Tuple, Any, List, Dict, Text
from IPython.display import display, Markdown
import math
import joblib
import os

# Ignorar warning
import warnings
warnings.filterwarnings('ignore')

# Preprocesamiento
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# Modelos de clasificación a evaluar
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC

# Busca de mejores hiperparametros
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

# Métricas de rendimiento
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, ConfusionMatrixDisplay, classification_report

# Gráficos
import matplotlib.pyplot as plt
import seaborn as sns

# MLflow
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
from joblib import parallel_backend
from mlflow.models import infer_signature

# Obtener los parametros de los modelos ===============================================================================================================
def obtener_configuraciones_modelos() -> List[Dict[str, Any]]:
    """
    Define y devuelve una lista de diccionarios, donde cada diccionario contiene
    la configuración (modelo, nombre y parámetros de búsqueda) para diferentes
    clasificadores de Machine Learning.

    Estas configuraciones están diseñadas para ser utilizadas con Pipeline y GridSearchCV/
    RandomizedSearchCV de scikit-learn, de ahí el prefijo 'clasificador__' en los parámetros.

    Parámetros (Input):
        Esta función no requiere ningún parámetro de entrada.

    Retorno (Output):
        List[Dict[str, Any]]: Una lista de diccionarios, cada uno con las claves:
                              'nombre' (str), 'modelo' (object), y 'parametros' (dict).
    """
    # Definir los modelos y los hiperparámetros a probar para cada uno
    configuracion_modelos = [
        {
            'nombre': 'regresion_logistica',
            'modelo': LogisticRegression(max_iter=2000, random_state=11),
            'parametros': {
                'clasificador__penalty': ['l1', 'l2'],
                # Nota: 'lbfgs' no funciona con 'l1', pero GridSearchCV/Pipeline lo maneja
                'clasificador__solver': ['liblinear', 'saga', 'lbfgs'], # Elige el algoritmo para encontrar los coeficientes óptimos.
                'clasificador__C': [0.01, 0.1, 1.0, 3.0, 10.0] # Controla la intensidad de la regularización. Valores más bajos (más fuerza de regularización) reducen el sobreajuste al penalizar coeficientes grandes. 0.01, 0.1, 1, 10
            }
        },
        {
            'nombre': 'decision_tree',
            'modelo': DecisionTreeClassifier(random_state=11),
            'parametros': {
                'clasificador__criterion': ['gini', 'entropy', 'log_loss'], 
                'clasificador__max_depth': [5, 10, 12, 15], # Controla la profundidad máxima del árbol. Valores más bajos limitan la complejidad del modelo, reduciendo el sobreajuste.
                'clasificador__min_samples_split': [2, 5, 10], # Define el número mínimo de muestras requeridas para dividir un nodo interno. Valores más altos evitan el sobreajuste.
                'clasificador__min_samples_leaf': [1, 3, 5], # Define el número mínimo de muestras requeridas para que un nodo sea una hoja (nodo final). Valores más altos evitan sobreajuste.
                'clasificador__max_leaf_nodes': [5, 10, 15, 20] # Define el número máximo de hojas que puede tener el árbol. Limita directamente el tamaño del árbol, reduciendo el sobreajuste
            }
        },
        {
            'nombre': 'random_forest',
            'modelo': RandomForestClassifier(random_state=11),
            'parametros': {
                'clasificador__criterion': ['gini', 'entropy', 'log_loss'],
                'clasificador__n_estimators': [100, 200, 300],
                'clasificador__max_depth': [5, 10, 15, 20],
                'clasificador__min_samples_split': [2, 5, 8],
                'clasificador__min_samples_leaf': [1, 5, 8],
            }
        },
        {
            'nombre': 'xgboost',
            # eval_metric se incluye para evitar warnings de XGBoost
            'modelo': XGBClassifier(random_state=11, eval_metric='mlogloss'),
            'parametros': {
                'clasificador__n_estimators': [100, 150, 200],
                'clasificador__max_depth': [5, 7, 10], # Reduce profundidad para evitar overfitting
                'clasificador__learning_rate': [0.001, 0.01, 0.1, 0.3], # Mantiene estabilidad
                'clasificador__subsample': [0.7, 0.8, 0.9, 1], # Reduce overfitting
                'clasificador__colsample_bytree': [0.7, 0.8, 0.9, 1], # Reduce la cantidad de features usadas por árbol

            }
        },
        {
            'nombre': 'knn',
            'modelo': KNeighborsClassifier(),
            'parametros': {
                'clasificador__n_neighbors': [2, 3, 5, 7, 10, 15, 20],
                'clasificador__weights': ['uniform', 'distance'],
                'clasificador__metric': ['euclidean', 'manhattan', 'minkowski']
            }
        },
        {
            'nombre': 'mlp',
            # early_stopping=True ayuda a prevenir el sobreajuste
            'modelo': MLPClassifier(random_state=11, early_stopping=True),
            'parametros': {
                'clasificador__hidden_layer_sizes': [(50,), (100,), (50, 50), (100, 100), (150,150)], # Define la arquitectura de la red neuronal
                'clasificador__activation': ['relu', 'tanh', 'logistic'], # Define la función de activación
                'clasificador__solver': ['adam', 'sgd'], # Define el algoritmo de optimización
                'clasificador__alpha': [0.001, 0.01, 0.05, 0.1], # Controla la regularización L2
                'clasificador__learning_rate': ['constant', 'adaptive'], # Define la tasa de aprendizaje
            }
        },
        {
            'nombre': 'svm',
            'modelo': SVC(random_state=11), 
            'parametros': {
                'clasificador__C': [0.01, 0.1, 1.0, 2.0, 10.0], # Controla la penalización por errores de clasificación. Valores más bajos (mayor regularización) reducen el sobreajuste.
                'clasificador__gamma': [0.0001, 0.001, 0.01, 0.1, 1.0], # Controla el alcance de la influencia de un solo punto de entrenamiento. Valores más bajos (menor influencia) reducen el sobreajuste.
                'clasificador__kernel': ['linear', 'rbf', 'poly', 'sigmoid'], # Define el tipo de kernel a utilizar
            }
        }
    ]

    return configuracion_modelos

# Entrenar cada modelo y obtener los mejores resultados ===============================================================================================================
def optimizar_y_comparar_modelos(
    config_modelos: list,
    preprocesador,
    X_train, y_train, X_test, y_test,
    mlflow_tracking_uri: str = "databricks",
    mlflow_experiment: str = "/Shared/ObesityEstimation"
) -> Tuple[pd.DataFrame, dict]:
    """
    Automatiza la optimización y evaluación de múltiples modelos de clasificación.

    Para cada modelo en la configuración, realiza una búsqueda de hiperparámetros
    con GridSearchCV, evalúa el mejor modelo encontrado en el conjunto de prueba
    y devuelve una tabla comparativa.

    Args:
        config_modelos (list): Lista de diccionarios con la configuración de cada modelo.
        preprocesador: El ColumnTransformer para preprocesar los datos.
        X_train, y_train, X_test, y_test: Conjuntos de datos divididos.

    Returns:
        Tuple[pd.DataFrame, dict]:
            - Un DataFrame con los resultados de rendimiento de cada modelo optimizado.
            - Un diccionario con los mejores pipelines entrenados para cada modelo.
    """

    # Configurar conexión a Databricks
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(mlflow_experiment)

    resultados_optimizados = []
    mejores_pipelines = {}

    for config in config_modelos:
        nombre_modelo = config['nombre']
        print(f"--- Optimizando: {nombre_modelo} ---")

        # Crear el pipeline completo
        pipeline = Pipeline(steps=[
            ('preprocesador', preprocesador),
            ('clasificador', config['modelo'])
        ])

        # Configurar y ejecutar GridSearchCV
        grid_search = GridSearchCV(
            pipeline,
            config['parametros'],
            cv=5,  # 5-fold cross-validation
            scoring='f1_weighted',
            n_jobs=1,
            verbose=1
        )
        
        # Iniciar run en MLflow
        with mlflow.start_run(run_name=nombre_modelo):
            # Entrenar con fallback seguro para Windows
            try:
                with parallel_backend('threading'):
                    grid_search.fit(X_train, y_train)
            except Exception:
                grid_search.fit(X_train, y_train)

            mejor_pipeline = grid_search.best_estimator_
            mejores_pipelines[nombre_modelo] = mejor_pipeline

            # Métricas
            y_pred_train = mejor_pipeline.predict(X_train)
            y_pred_test = mejor_pipeline.predict(X_test)

            accuracy_train = accuracy_score(y_train, y_pred_train)
            f1_train = f1_score(y_train, y_pred_train, average='weighted')
            accuracy_test = accuracy_score(y_test, y_pred_test)
            f1_test = f1_score(y_test, y_pred_test, average='weighted')

            # Ejemplo de entrada y signature
            input_example = X_train.head(5)
            signature = infer_signature(X_train, mejor_pipeline.predict(X_train))

            # Registrar parámetros y métricas
            mlflow.log_params(grid_search.best_params_)
            mlflow.log_metric("accuracy_train", float(accuracy_train))
            mlflow.log_metric("f1_train", float(f1_train))
            mlflow.log_metric("accuracy_test", float(accuracy_test))
            mlflow.log_metric("f1_test", float(f1_test))

            # Reporte de clasificación como artefacto de texto
            report = classification_report(y_test, y_pred_test)
            mlflow.log_text(report, "classification_report.txt")

            # Calcular matriz de confusión
            cm = confusion_matrix(y_test, y_pred_test)
            # Crear figura
            fig, ax = plt.subplots(figsize=(6, 6))
            disp = ConfusionMatrixDisplay(confusion_matrix=cm)
            disp.plot(cmap='Blues', ax=ax, colorbar=False)
            plt.title(f"Matriz de Confusión - {nombre_modelo}")
            plt.xlabel("Predicción")
            plt.ylabel("Real")
            plt.tight_layout()
            # Guardar directamente en MLflow
            mlflow.log_figure(fig, "confusion_matrix_" + nombre_modelo +".png")
            # Cerrar figura para liberar memoria
            plt.close(fig)

            # Guardar el pipeline completo
            mlflow.sklearn.log_model(sk_model = mejor_pipeline
                                     , name = nombre_modelo
                                     , input_example = input_example
                                     , signature = signature)

            print(f"Run registrada en MLflow para: {nombre_modelo}")
            print(f"F1 Test: {f1_test:.4f}")
            print(f"Mejores parámetros: {grid_search.best_params_}")

            # Guardar para el DataFrame local
            resultados_optimizados.append({
                'Modelo': nombre_modelo,
                'F1-Score (Train)': f1_train,
                'Accuracy (Train)': accuracy_train,
                'F1-Score (Test)': f1_test,
                'Accuracy (Test)': accuracy_test,
                'Mejores Parámetros': grid_search.best_params_
            })

    # Mostrar tabla final
    df_resultados = pd.DataFrame(resultados_optimizados).sort_values(by='F1-Score (Test)', ascending=False)
    display(df_resultados)

    return df_resultados, mejores_pipelines



"""
        grid_search.fit(X_train, y_train)

        # Guardar el mejor pipeline encontrado
        mejor_pipeline = grid_search.best_estimator_
        mejores_pipelines[nombre_modelo] = mejor_pipeline

        # Evaluar en el conjunto de entrenamiento
        predicciones_train = mejor_pipeline.predict(X_train)
        accuracy_train = accuracy_score(y_train, predicciones_train)
        f1_train = f1_score(y_train, predicciones_train, average='weighted')

        # Evaluar en el conjunto de prueba
        predicciones_test = mejor_pipeline.predict(X_test)
        accuracy_test = accuracy_score(y_test, predicciones_test)
        f1_test = f1_score(y_test, predicciones_test, average='weighted')

        # Guardar resultados
        resultados_optimizados.append({
            'Modelo': nombre_modelo,
            'Mejores Parámetros': grid_search.best_params_,
            'F1-Score (Train)': f1_train,
            'Accuracy (Train)': accuracy_train,
            'F1-Score (Test)': f1_test,
            'Accuracy (Test)': accuracy_test
        })

        print(f"Mejor F1-Score (CV) para {nombre_modelo}: {grid_search.best_score_:.4f}\n")
        print(f"Mejores parametros: {grid_search.best_params_}\n")

    # Mostrar la tabla de resultados finales
    print("\n--- Tabla Comparativa de Modelos Optimizados ---")
    display(pd.DataFrame(resultados_optimizados).sort_values(by='F1-Score (Test)', ascending=False))

    return pd.DataFrame(resultados_optimizados), mejores_pipelines
"""

# Almacenar los mejores modelos y sus configuraciones ===============================================================================================================
def guardar_artefactos_ml(
    df_resultados: pd.DataFrame,
    pipelines: Dict[str, Any],
    base_path: Text = '../../artefactos/',
    results_name: Text = 'mejores_modelos.csv',
    pipelines_name: Text = 'pipelines_optimizados.joblib'
) -> None:
    """
    Guarda los resultados de la optimización y los modelos (pipelines) entrenados.

    Crea un directorio de destino si no existe.

    Args:
        df_resultados (pd.DataFrame): DataFrame con la tabla comparativa de modelos.
        pipelines (Dict[str, Any]): Diccionario que contiene los mejores pipelines entrenados.
        base_path (str): Directorio base donde se guardarán los archivos.
        results_name (str): Nombre del archivo CSV para los resultados.
        pipelines_name (str): Nombre del archivo joblib para los pipelines.

    Returns:
        None
    """
    # 1. Crear el directorio de destino si no existe
    os.makedirs(base_path, exist_ok=True)

    # Rutas completas
    ruta_resultados = os.path.join(base_path, results_name)
    ruta_pipelines = os.path.join(base_path, pipelines_name)

    # 2. Guardar el DataFrame de resultados (como CSV)
    try:
        df_resultados.to_csv(ruta_resultados, index=False)
    except Exception as e:
        print(f"Error al guardar resultados CSV")

    # 3. Guardar el diccionario de pipelines (usando joblib)
    try:
        joblib.dump(pipelines, ruta_pipelines)
    except Exception as e:
        print(f"Error al guardar pipelines (joblib)")

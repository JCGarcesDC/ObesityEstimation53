"""
Módulo de Predicción y Explicabilidad.

Maneja la carga del modelo, predicciones y explicaciones SHAP.
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
import logging

# Importar solo si está disponible
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP no disponible. Explicabilidad limitada.")

logger = logging.getLogger(__name__)


class ModelPredictor:
    """Clase para manejar predicciones y explicabilidad del modelo."""
    
    # Mapeo de códigos numéricos a nombres de clases
    OBESITY_MAPPING_REVERSE = {
        0: 'insufficient_weight',
        1: 'normal_weight',
        2: 'overweight_level_i',
        3: 'overweight_level_ii',
        4: 'obesity_type_i',
        5: 'obesity_type_ii',
        6: 'obesity_type_iii'
    }
    
    def __init__(self, model_path: str = "artefactos/pipelines_optimizados.joblib"):
        """
        Inicializa el predictor cargando el modelo.
        
        Args:
            model_path: Ruta al archivo joblib con los pipelines
        """
        self.model_path = Path(model_path)
        self.pipelines = None
        self.best_model = None
        self.best_model_name = "XGBoost"  # El mejor según análisis
        self.preprocessor = None
        self.feature_names = None
        self.explainer = None
        
        self._load_model()
        self._initialize_explainer()
    
    def _load_model(self):
        """Carga el modelo y preprocesador desde disco."""
        try:
            logger.info(f"Cargando modelo desde {self.model_path}")
            self.pipelines = joblib.load(self.model_path)
            
            # Seleccionar el mejor modelo (XGBoost)
            if self.best_model_name in self.pipelines:
                self.best_model = self.pipelines[self.best_model_name]
                logger.info(f"Modelo {self.best_model_name} cargado exitosamente")
                
                # Extraer preprocesador y clasificador
                if hasattr(self.best_model, 'named_steps'):
                    self.preprocessor = self.best_model.named_steps.get('preprocesador')
                    classifier = self.best_model.named_steps.get('clasificador')
                    
                    # Obtener nombres de features después del preprocesamiento
                    if hasattr(self.preprocessor, 'get_feature_names_out'):
                        self.feature_names = list(self.preprocessor.get_feature_names_out())
                    
            else:
                raise ValueError(f"Modelo {self.best_model_name} no encontrado en pipelines")
                
        except Exception as e:
            logger.error(f"Error cargando modelo: {str(e)}")
            raise
    
    def _initialize_explainer(self):
        """Inicializa el explicador SHAP si está disponible."""
        if not SHAP_AVAILABLE:
            logger.warning("SHAP no disponible, explicabilidad deshabilitada")
            return
        
        try:
            # Crear un pequeño dataset de fondo para SHAP
            # En producción, se podría usar un sample del training data
            logger.info("Inicializando explicador SHAP...")
            # Por ahora, se inicializará bajo demanda
            self.explainer = None
        except Exception as e:
            logger.warning(f"No se pudo inicializar SHAP: {str(e)}")
    
    def calculate_bmi(self, weight: float, height: float) -> float:
        """
        Calcula el Índice de Masa Corporal.
        
        Args:
            weight: Peso en kg
            height: Altura en metros
            
        Returns:
            BMI calculado
        """
        return round(weight / (height ** 2), 2)
    
    def preprocess_input(self, input_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Preprocesa los datos de entrada para el modelo.
        
        Args:
            input_data: Diccionario con los datos de entrada
            
        Returns:
            DataFrame preparado para predicción
        """
        # Crear DataFrame con los datos
        df = pd.DataFrame([input_data])
        
        # Calcular IMC (BMI)
        df['IMC'] = df['Weight'] / (df['Height'] ** 2)
        
        # Convertir nombres de columnas a minúsculas (el modelo espera minúsculas)
        df.columns = df.columns.str.lower()
        
        # Asegurar que las columnas estén en orden correcto
        expected_cols = [
            'age', 'height', 'weight', 'gender', 
            'family_history_with_overweight', 'favc', 'fcvc', 'ncp',
            'caec', 'smoke', 'ch2o', 'scc', 'faf', 'tue', 'calc', 'mtrans', 'imc'
        ]
        
        df = df[expected_cols]
        
        return df
    
    def predict(self, input_data: Dict[str, Any]) -> Tuple[int, np.ndarray]:
        """
        Realiza predicción para una instancia.
        
        Args:
            input_data: Diccionario con features de entrada
            
        Returns:
            Tuple con (predicción, probabilidades)
        """
        if self.best_model is None:
            raise ValueError("Modelo no cargado")
        
        # Preprocesar entrada
        X = self.preprocess_input(input_data)
        
        # Predicción
        prediction = self.best_model.predict(X)[0]
        probabilities = self.best_model.predict_proba(X)[0]
        
        return int(prediction), probabilities
    
    def predict_with_details(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza predicción completa con detalles.
        
        Args:
            input_data: Diccionario con features de entrada
            
        Returns:
            Diccionario con predicción y detalles
        """
        # Calcular BMI
        bmi = self.calculate_bmi(input_data['Weight'], input_data['Height'])
        
        # Predicción
        prediction_code, probabilities = self.predict(input_data)
        prediction_name = self.OBESITY_MAPPING_REVERSE[prediction_code]
        
        # Probabilidades por clase
        prob_dict = {
            self.OBESITY_MAPPING_REVERSE[i]: float(prob) 
            for i, prob in enumerate(probabilities)
        }
        
        # Confianza (máxima probabilidad)
        confidence = float(np.max(probabilities))
        
        return {
            "prediction": prediction_name,
            "prediction_code": prediction_code,
            "confidence": round(confidence, 4),
            "probabilities": {k: round(v, 4) for k, v in prob_dict.items()},
            "bmi": bmi
        }
    
    def explain_prediction(
        self, 
        input_data: Dict[str, Any], 
        explain_type: str = "shap"
    ) -> Dict[str, Any]:
        """
        Genera explicación de la predicción.
        
        Args:
            input_data: Diccionario con features
            explain_type: Tipo de explicación ('shap' o 'feature_importance')
            
        Returns:
            Diccionario con valores de contribución
        """
        if explain_type == "feature_importance" or not SHAP_AVAILABLE:
            return self._get_feature_importance()
        
        elif explain_type == "shap":
            return self._get_shap_explanation(input_data)
        
        else:
            raise ValueError(f"Tipo de explicación no soportado: {explain_type}")
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Obtiene importancia de features del modelo."""
        try:
            classifier = self.best_model.named_steps.get('clasificador')
            
            if hasattr(classifier, 'feature_importances_'):
                importances = classifier.feature_importances_
                
                # Mapear a nombres de features originales
                feature_names = [
                    'Age', 'Height', 'Weight', 'Gender', 
                    'family_history_with_overweight', 'FAVC', 'FCVC', 'NCP',
                    'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE', 'CALC', 'MTRANS'
                ]
                
                # Tomar primeras N importancias (correspondientes a features originales)
                importance_dict = {}
                for i, name in enumerate(feature_names[:len(importances)]):
                    if i < len(importances):
                        importance_dict[name] = round(float(importances[i]), 4)
                
                # Ordenar por importancia
                importance_dict = dict(
                    sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                )
                
                return importance_dict
            
            return {"info": "Feature importance no disponible para este modelo"}
            
        except Exception as e:
            logger.error(f"Error obteniendo feature importance: {str(e)}")
            return {"error": str(e)}
    
    def _get_shap_explanation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera explicación SHAP para la predicción."""
        if not SHAP_AVAILABLE:
            return {"error": "SHAP no disponible"}
        
        try:
            # Preprocesar entrada
            X = self.preprocess_input(input_data)
            X_transformed = self.preprocessor.transform(X)
            
            # Obtener el clasificador
            classifier = self.best_model.named_steps.get('clasificador')
            
            # Crear explicador si no existe
            if self.explainer is None:
                self.explainer = shap.TreeExplainer(classifier)
            
            # Calcular valores SHAP
            shap_values = self.explainer.shap_values(X_transformed)
            
            # Si es multiclase, tomar valores para la clase predicha
            prediction_code, _ = self.predict(input_data)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[prediction_code]
            
            # Mapear a nombres de features
            feature_names = [
                'Age', 'Height', 'Weight', 'Gender', 
                'family_history_with_overweight', 'FAVC', 'FCVC', 'NCP',
                'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE', 'CALC', 'MTRANS'
            ]
            
            shap_dict = {}
            for i, name in enumerate(feature_names[:len(shap_values[0])]):
                if i < len(shap_values[0]):
                    shap_dict[name] = round(float(shap_values[0][i]), 4)
            
            # Ordenar por valor absoluto
            shap_dict = dict(
                sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            )
            
            return shap_dict
            
        except Exception as e:
            logger.error(f"Error generando explicación SHAP: {str(e)}")
            # Fallback a feature importance
            return self._get_feature_importance()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información sobre el modelo cargado."""
        return {
            "model_name": self.best_model_name,
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
                'Age', 'Height', 'Weight', 'Gender', 
                'family_history_with_overweight', 'FAVC', 'FCVC', 'NCP',
                'CAEC', 'SMOKE', 'CH2O', 'SCC', 'FAF', 'TUE', 'CALC', 'MTRANS'
            ],
            "target_classes": self.OBESITY_MAPPING_REVERSE,
            "trained_date": "2025-11-11"
        }

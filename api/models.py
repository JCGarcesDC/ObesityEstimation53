"""
Pydantic Models para Request/Response de la API.

Define los esquemas de validación para entrada y salida de datos.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum


class GenderEnum(str, Enum):
    """Enumeración para género."""
    male = "male"
    female = "female"


class YesNoEnum(str, Enum):
    """Enumeración para respuestas sí/no."""
    yes = "yes"
    no = "no"


class FrequencyEnum(str, Enum):
    """Enumeración para frecuencias de consumo."""
    no = "no"
    sometimes = "sometimes"
    frequently = "frequently"
    always = "always"


class TransportEnum(str, Enum):
    """Enumeración para tipo de transporte."""
    automobile = "automobile"
    motorbike = "motorbike"
    bike = "bike"
    public_transportation = "public_transportation"
    walking = "walking"


class ObesityPredictionRequest(BaseModel):
    """Schema para request de predicción individual."""
    
    Age: float = Field(..., ge=1, le=120, description="Edad en años")
    Height: float = Field(..., ge=0.5, le=2.5, description="Altura en metros")
    Weight: float = Field(..., ge=20, le=300, description="Peso en kilogramos")
    Gender: GenderEnum = Field(..., description="Género (male/female)")
    
    family_history_with_overweight: YesNoEnum = Field(
        ..., 
        description="¿Historial familiar de sobrepeso? (yes/no)",
        alias="family_history_with_overweight"
    )
    
    FAVC: YesNoEnum = Field(
        ..., 
        description="¿Consume frecuentemente alimentos altos en calorías? (yes/no)"
    )
    
    FCVC: float = Field(..., ge=0, le=3, description="Frecuencia de consumo de vegetales (0-3)")
    NCP: float = Field(..., ge=1, le=4, description="Número de comidas principales (1-4)")
    
    CAEC: FrequencyEnum = Field(
        ..., 
        description="Consumo de alimentos entre comidas"
    )
    
    SMOKE: YesNoEnum = Field(..., description="¿Fuma? (yes/no)")
    CH2O: float = Field(..., ge=0, le=3, description="Consumo diario de agua en litros (0-3)")
    SCC: YesNoEnum = Field(..., description="¿Monitorea calorías consumidas? (yes/no)")
    FAF: float = Field(..., ge=0, le=3, description="Frecuencia de actividad física (0-3)")
    TUE: float = Field(..., ge=0, le=2, description="Tiempo usando tecnología en horas (0-2)")
    
    CALC: FrequencyEnum = Field(
        ..., 
        description="Consumo de alcohol"
    )
    
    MTRANS: TransportEnum = Field(
        ..., 
        description="Tipo de transporte usado"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "Age": 25,
                "Height": 1.75,
                "Weight": 80,
                "Gender": "male",
                "family_history_with_overweight": "yes",
                "FAVC": "yes",
                "FCVC": 2.0,
                "NCP": 3.0,
                "CAEC": "sometimes",
                "SMOKE": "no",
                "CH2O": 2.0,
                "SCC": "no",
                "FAF": 1.0,
                "TUE": 1.0,
                "CALC": "sometimes",
                "MTRANS": "public_transportation"
            }
        }


class ObesityPredictionResponse(BaseModel):
    """Schema para response de predicción."""
    
    prediction: str = Field(..., description="Categoría de obesidad predicha")
    prediction_code: int = Field(..., description="Código numérico de la predicción (0-6)")
    confidence: float = Field(..., ge=0, le=1, description="Confianza de la predicción")
    probabilities: Dict[str, float] = Field(..., description="Probabilidades para cada clase")
    bmi: float = Field(..., description="Índice de Masa Corporal calculado")
    
    class Config:
        schema_extra = {
            "example": {
                "prediction": "normal_weight",
                "prediction_code": 1,
                "confidence": 0.95,
                "probabilities": {
                    "insufficient_weight": 0.01,
                    "normal_weight": 0.95,
                    "overweight_level_i": 0.03,
                    "overweight_level_ii": 0.01,
                    "obesity_type_i": 0.0,
                    "obesity_type_ii": 0.0,
                    "obesity_type_iii": 0.0
                },
                "bmi": 26.12
            }
        }


class BatchPredictionRequest(BaseModel):
    """Schema para predicción por lotes."""
    
    instances: List[ObesityPredictionRequest] = Field(
        ..., 
        min_items=1, 
        max_items=100,
        description="Lista de instancias para predicción (máx 100)"
    )


class BatchPredictionResponse(BaseModel):
    """Schema para response de predicción por lotes."""
    
    predictions: List[ObesityPredictionResponse]
    total: int = Field(..., description="Total de predicciones realizadas")


class ExplainRequest(BaseModel):
    """Schema para request de explicabilidad."""
    
    instance: ObesityPredictionRequest
    explain_type: str = Field(
        default="shap", 
        description="Tipo de explicación: 'shap' o 'feature_importance'"
    )
    
    @validator('explain_type')
    def validate_explain_type(cls, v):
        if v not in ['shap', 'feature_importance']:
            raise ValueError("explain_type debe ser 'shap' o 'feature_importance'")
        return v


class ExplainResponse(BaseModel):
    """Schema para response de explicabilidad."""
    
    prediction: ObesityPredictionResponse
    explanation: Dict[str, Any] = Field(..., description="Valores de contribución de features")
    explanation_type: str
    
    class Config:
        schema_extra = {
            "example": {
                "prediction": {
                    "prediction": "normal_weight",
                    "prediction_code": 1,
                    "confidence": 0.95,
                    "probabilities": {},
                    "bmi": 26.12
                },
                "explanation": {
                    "Weight": 0.35,
                    "Height": -0.12,
                    "Age": 0.08,
                    "FAF": -0.15,
                    "FCVC": -0.10
                },
                "explanation_type": "shap"
            }
        }


class HealthResponse(BaseModel):
    """Schema para health check."""
    
    status: str = Field(default="healthy")
    model_loaded: bool
    model_name: str = Field(default="unknown")
    model_version: str = Field(default="unknown")
    api_version: str = Field(default="1.0.0")
    message: str = Field(default="")


class ModelInfoResponse(BaseModel):
    """Schema para información del modelo."""
    
    model_name: str
    model_type: str
    f1_score_test: float
    accuracy_test: float
    hyperparameters: Dict[str, Any]
    features: List[str]
    target_classes: Dict[int, str]
    trained_date: Optional[str] = None

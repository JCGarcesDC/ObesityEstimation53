"""
API FastAPI para Servicio de Predicción de Obesidad.

Endpoints:
- GET /health: Verificación de salud del servicio
- POST /predict: Predicción individual
- POST /predict_batch: Predicción por lote
- GET /model_info: Información del modelo
- POST /explain: Explicación de predicción con SHAP
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import List
from contextlib import asynccontextmanager

from api.models import (
    ObesityPredictionRequest,
    ObesityPredictionResponse,
    BatchPredictionRequest,
    BatchPredictionResponse,
    ExplainRequest,
    ExplainResponse,
    HealthResponse,
    ModelInfoResponse
)
from api.prediction import ModelPredictor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Variable global para el predictor
predictor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manejo del ciclo de vida de la aplicación."""
    # Startup
    global predictor
    logger.info("Iniciando servicio de predicción...")
    try:
        predictor = ModelPredictor()
        logger.info("Modelo cargado exitosamente")
    except Exception as e:
        logger.error(f"Error cargando modelo: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Cerrando servicio de predicción...")


# Crear aplicación FastAPI
app = FastAPI(
    title="API de Predicción de Obesidad",
    description="Servicio de Machine Learning para clasificación de niveles de obesidad",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejo global de excepciones."""
    logger.error(f"Error no manejado: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Error interno del servidor"}
    )


@app.get("/", include_in_schema=False)
async def root():
    """Redirección a documentación."""
    return {
        "message": "API de Predicción de Obesidad",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Verificación de salud del servicio.
    
    Retorna el estado del servicio y si el modelo está cargado.
    """
    try:
        if predictor is None:
            return HealthResponse(
                status="unhealthy",
                model_loaded=False,
                model_name="unknown",
                model_version="unknown",
                message="Modelo no cargado"
            )
        
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            model_name="XGBoost",
            model_version="2.0.3",
            message="Servicio operativo"
        )
    
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            model_name="unknown",
            model_version="unknown",
            message=str(e)
        )


@app.post("/predict", response_model=ObesityPredictionResponse, tags=["Prediction"])
async def predict(request: ObesityPredictionRequest):
    """
    Predicción individual de nivel de obesidad.
    
    Recibe características de un individuo y retorna:
    - Predicción del nivel de obesidad
    - Confianza de la predicción
    - Probabilidades para todas las clases
    - BMI calculado
    """
    try:
        if predictor is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Modelo no disponible"
            )
        
        # Convertir request a dict
        input_data = request.model_dump()
        
        # Realizar predicción
        result = predictor.predict_with_details(input_data)
        
        return ObesityPredictionResponse(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en predicción: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando predicción: {str(e)}"
        )


@app.post("/predict_batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_batch(request: BatchPredictionRequest):
    """
    Predicción por lote para múltiples instancias.
    
    Permite procesar hasta 100 instancias en una sola petición.
    Retorna predicciones individuales para cada instancia.
    """
    try:
        if predictor is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Modelo no disponible"
            )
        
        predictions = []
        
        for instance in request.instances:
            input_data = instance.model_dump()
            result = predictor.predict_with_details(input_data)
            predictions.append(ObesityPredictionResponse(**result))
        
        return BatchPredictionResponse(predictions=predictions)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en predicción batch: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando batch: {str(e)}"
        )


@app.get("/model_info", response_model=ModelInfoResponse, tags=["Model"])
async def get_model_info():
    """
    Información sobre el modelo cargado.
    
    Retorna:
    - Nombre y tipo del modelo
    - Métricas de evaluación
    - Hiperparámetros
    - Features utilizadas
    - Clases objetivo
    """
    try:
        if predictor is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Modelo no disponible"
            )
        
        info = predictor.get_model_info()
        return ModelInfoResponse(**info)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo info del modelo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo información: {str(e)}"
        )


@app.post("/explain", response_model=ExplainResponse, tags=["Explainability"])
async def explain_prediction(request: ExplainRequest):
    """
    Explicación de predicción usando SHAP.
    
    Retorna la contribución de cada feature a la predicción.
    Útil para entender qué factores influyen más en el resultado.
    
    Tipos de explicación:
    - 'shap': Valores SHAP (requiere librería shap)
    - 'feature_importance': Importancia global de features
    """
    try:
        if predictor is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Modelo no disponible"
            )
        
        # Convertir request a dict
        input_data = request.instance.model_dump()
        
        # Obtener predicción
        result = predictor.predict_with_details(input_data)
        
        # Obtener explicación
        feature_contributions = predictor.explain_prediction(
            input_data,
            explain_type=request.explain_type
        )
        
        return ExplainResponse(
            prediction=result["prediction"],
            feature_contributions=feature_contributions,
            explain_type=request.explain_type
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en explicación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando explicación: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

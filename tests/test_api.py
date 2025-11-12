"""
Tests para API de Predicción de Obesidad.

Cubre endpoints, validación y respuestas.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.app import app

# Cliente de prueba
client = TestClient(app)


class TestHealthEndpoint:
    """Tests para el endpoint de salud."""
    
    def test_health_check_success(self):
        """Health check debe retornar 200."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        # Permitir estado unhealthy si modelo no carga en tests
        assert data["status"] in ["healthy", "unhealthy"]
    
    def test_health_check_structure(self):
        """Health check debe tener estructura correcta."""
        response = client.get("/health")
        data = response.json()
        
        required_fields = ["status", "model_loaded", "message"]
        for field in required_fields:
            assert field in data


class TestPredictEndpoint:
    """Tests para el endpoint de predicción individual."""
    
    @pytest.fixture
    def valid_payload(self):
        """Payload válido para predicción."""
        return {
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
    
    def test_predict_success(self, valid_payload):
        """Predicción con datos válidos debe retornar 200 o 503."""
        response = client.post("/predict", json=valid_payload)
        
        # Si modelo no está cargado, retorna 503
        if response.status_code == 503:
            pytest.skip("Modelo no disponible en tests")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "prediction" in data
        assert "confidence" in data
        assert "probabilities" in data
        assert "bmi" in data
    
    def test_predict_response_types(self, valid_payload):
        """Verificar tipos de datos en respuesta."""
        response = client.post("/predict", json=valid_payload)
        
        if response.status_code == 503:
            pytest.skip("Modelo no disponible en tests")
            
        data = response.json()
        
        assert isinstance(data["prediction"], str)
        assert isinstance(data["confidence"], float)
        assert isinstance(data["probabilities"], dict)
        assert isinstance(data["bmi"], float)
    
    def test_predict_invalid_age(self, valid_payload):
        """Edad fuera de rango debe retornar 422."""
        invalid_payload = valid_payload.copy()
        invalid_payload["Age"] = 150.0  # Edad inválida
        
        response = client.post("/predict", json=invalid_payload)
        assert response.status_code == 422
    
    def test_predict_invalid_height(self, valid_payload):
        """Altura inválida debe retornar 422."""
        invalid_payload = valid_payload.copy()
        invalid_payload["Height"] = 3.0  # Altura imposible
        
        response = client.post("/predict", json=invalid_payload)
        assert response.status_code == 422
    
    def test_predict_invalid_weight(self, valid_payload):
        """Peso inválido debe retornar 422."""
        invalid_payload = valid_payload.copy()
        invalid_payload["Weight"] = 10.0  # Peso muy bajo
        
        response = client.post("/predict", json=invalid_payload)
        assert response.status_code == 422
    
    def test_predict_invalid_gender(self, valid_payload):
        """Género inválido debe retornar 422."""
        invalid_payload = valid_payload.copy()
        invalid_payload["Gender"] = "other"  # No soportado
        
        response = client.post("/predict", json=invalid_payload)
        assert response.status_code == 422
    
    def test_predict_missing_field(self, valid_payload):
        """Falta campo obligatorio debe retornar 422."""
        incomplete_payload = valid_payload.copy()
        del incomplete_payload["Age"]
        
        response = client.post("/predict", json=incomplete_payload)
        assert response.status_code == 422
    
    def test_predict_bmi_calculation(self, valid_payload):
        """Verificar cálculo de BMI correcto."""
        response = client.post("/predict", json=valid_payload)
        
        if response.status_code == 503:
            pytest.skip("Modelo no disponible en tests")
            
        data = response.json()
        
        expected_bmi = round(70.0 / (1.75 ** 2), 2)
        assert data["bmi"] == pytest.approx(expected_bmi, abs=0.01)


class TestBatchPredictEndpoint:
    """Tests para predicción por lote."""
    
    @pytest.fixture
    def valid_batch_payload(self):
        """Payload válido con múltiples instancias."""
        return {
            "instances": [
                {
                    "Age": 25.0, "Height": 1.75, "Weight": 70.0,
                    "Gender": "male", "family_history_with_overweight": "yes",
                    "FAVC": "yes", "FCVC": 2.0, "NCP": 3.0,
                    "CAEC": "sometimes", "SMOKE": "no", "CH2O": 2.0,
                    "SCC": "no", "FAF": 2.0, "TUE": 1.0,
                    "CALC": "no", "MTRANS": "public_transportation"
                },
                {
                    "Age": 30.0, "Height": 1.65, "Weight": 55.0,
                    "Gender": "female", "family_history_with_overweight": "no",
                    "FAVC": "no", "FCVC": 3.0, "NCP": 3.0,
                    "CAEC": "no", "SMOKE": "no", "CH2O": 2.5,
                    "SCC": "yes", "FAF": 3.0, "TUE": 0.5,
                    "CALC": "no", "MTRANS": "walking"
                }
            ]
        }
    
    def test_batch_predict_success(self, valid_batch_payload):
        """Predicción batch exitosa."""
        response = client.post("/predict_batch", json=valid_batch_payload)
        
        if response.status_code == 503:
            pytest.skip("Modelo no disponible en tests")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "predictions" in data
        assert len(data["predictions"]) == 2
    
    def test_batch_predict_max_limit(self):
        """No permitir más de 100 instancias."""
        oversized_batch = {
            "instances": [
                {
                    "Age": 25.0, "Height": 1.75, "Weight": 70.0,
                    "Gender": "male", "family_history_with_overweight": "yes",
                    "FAVC": "yes", "FCVC": 2.0, "NCP": 3.0,
                    "CAEC": "sometimes", "SMOKE": "no", "CH2O": 2.0,
                    "SCC": "no", "FAF": 2.0, "TUE": 1.0,
                    "CALC": "no", "MTRANS": "public_transportation"
                }
            ] * 101  # 101 instancias
        }
        
        response = client.post("/predict_batch", json=oversized_batch)
        assert response.status_code == 422


class TestModelInfoEndpoint:
    """Tests para endpoint de información del modelo."""
    
    def test_model_info_success(self):
        """Model info debe retornar 200."""
        response = client.get("/model_info")
        
        if response.status_code == 503:
            pytest.skip("Modelo no disponible en tests")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar campos esenciales
        assert "model_name" in data
        assert "model_type" in data
        assert "f1_score_test" in data
        assert "accuracy_test" in data
        assert "hyperparameters" in data
        assert "features" in data
        assert "target_classes" in data
    
    def test_model_info_values(self):
        """Verificar valores esperados en model info."""
        response = client.get("/model_info")
        
        if response.status_code == 503:
            pytest.skip("Modelo no disponible en tests")
            
        data = response.json()
        
        assert data["model_name"] == "XGBoost"
        assert data["f1_score_test"] == pytest.approx(0.9426, abs=0.001)
        assert len(data["features"]) == 16  # 16 features
        assert len(data["target_classes"]) == 7  # 7 clases


class TestExplainEndpoint:
    """Tests para explicabilidad."""
    
    @pytest.fixture
    def valid_explain_payload(self):
        """Payload válido para explicación."""
        return {
            "instance": {
                "Age": 25.0, "Height": 1.75, "Weight": 70.0,
                "Gender": "male", "family_history_with_overweight": "yes",
                "FAVC": "yes", "FCVC": 2.0, "NCP": 3.0,
                "CAEC": "sometimes", "SMOKE": "no", "CH2O": 2.0,
                "SCC": "no", "FAF": 2.0, "TUE": 1.0,
                "CALC": "no", "MTRANS": "public_transportation"
            },
            "explain_type": "feature_importance"
        }
    
    def test_explain_success(self, valid_explain_payload):
        """Explicación exitosa."""
        response = client.post("/explain", json=valid_explain_payload)
        
        if response.status_code == 503:
            pytest.skip("Modelo no disponible en tests")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "prediction" in data
        assert "feature_contributions" in data
        assert "explain_type" in data
    
    def test_explain_feature_importance(self, valid_explain_payload):
        """Explicación con feature importance."""
        response = client.post("/explain", json=valid_explain_payload)
        
        if response.status_code == 503:
            pytest.skip("Modelo no disponible en tests")
            
        data = response.json()
        
        assert isinstance(data["feature_contributions"], dict)
        assert len(data["feature_contributions"]) > 0
    
    def test_explain_invalid_type(self, valid_explain_payload):
        """Tipo de explicación inválido debe retornar 422."""
        invalid_payload = valid_explain_payload.copy()
        invalid_payload["explain_type"] = "invalid_type"
        
        response = client.post("/explain", json=invalid_payload)
        assert response.status_code == 422


class TestRootEndpoint:
    """Tests para endpoint raíz."""
    
    def test_root_endpoint(self):
        """Root debe retornar información básica."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "docs" in data
        assert "health" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

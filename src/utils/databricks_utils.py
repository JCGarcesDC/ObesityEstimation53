"""
Utilidades para trabajar con Databricks y MLflow en el proyecto ObesityMine53
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Optional

def load_databricks_credentials() -> Dict[str, str]:
    """
    Cargar credenciales de Databricks desde el archivo de configuración
    
    Returns:
        Dict con las credenciales de Databricks
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "credentials.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de credenciales en: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        credentials = yaml.safe_load(file)
    
    if 'databricks' not in credentials:
        raise ValueError("No se encontraron credenciales de Databricks en el archivo")
    
    return credentials['databricks']

def load_mlflow_databricks_config() -> Dict[str, str]:
    """
    Cargar configuración de MLflow para Databricks
    
    Returns:
        Dict con la configuración de MLflow
    """
    config_path = Path(__file__).parent.parent.parent / "config" / "credentials.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de credenciales en: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        credentials = yaml.safe_load(file)
    
    if 'mlflow_databricks' not in credentials:
        raise ValueError("No se encontró configuración de MLflow para Databricks")
    
    return credentials['mlflow_databricks']

def setup_databricks_environment() -> None:
    """
    Configurar variables de entorno para Databricks
    """
    try:
        databricks_creds = load_databricks_credentials()
        
        os.environ['DATABRICKS_TOKEN'] = databricks_creds['token']
        os.environ['DATABRICKS_HOST'] = databricks_creds['host']
        
        print("✅ Variables de entorno de Databricks configuradas")
        
    except Exception as e:
        print(f"❌ Error al configurar Databricks: {e}")
        raise

def setup_mlflow_databricks_environment() -> None:
    """
    Configurar variables de entorno para MLflow con Databricks
    """
    try:
        mlflow_config = load_mlflow_databricks_config()
        
        if 'tracking_uri' in mlflow_config:
            os.environ['MLFLOW_TRACKING_URI'] = mlflow_config['tracking_uri']
        
        if 'registry_uri' in mlflow_config:
            os.environ['MLFLOW_REGISTRY_URI'] = mlflow_config['registry_uri']
        
        print("✅ Variables de entorno de MLflow configuradas")
        
    except Exception as e:
        print(f"❌ Error al configurar MLflow: {e}")
        raise

def setup_full_databricks_environment() -> None:
    """
    Configurar todo el entorno de Databricks y MLflow
    """
    setup_databricks_environment()
    setup_mlflow_databricks_environment()
    print("🎉 Entorno completo de Databricks configurado")

def get_databricks_client():
    """
    Obtener cliente de Databricks (requiere databricks-sdk)
    
    Returns:
        Cliente de Databricks configurado
    """
    try:
        from databricks.sdk import WorkspaceClient
        
        setup_databricks_environment()
        
        # El cliente usará automáticamente las variables de entorno
        client = WorkspaceClient()
        
        return client
        
    except ImportError:
        raise ImportError("El paquete 'databricks-sdk' no está instalado. Instálalo con: pip install databricks-sdk")
    except Exception as e:
        raise Exception(f"Error al crear cliente de Databricks: {e}")

def get_mlflow_client():
    """
    Obtener cliente de MLflow configurado para Databricks
    
    Returns:
        Cliente de MLflow configurado
    """
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
        
        setup_mlflow_databricks_environment()
        setup_databricks_environment()  # MLflow también necesita las credenciales de Databricks
        
        # Configurar MLflow
        mlflow_config = load_mlflow_databricks_config()
        if 'tracking_uri' in mlflow_config:
            mlflow.set_tracking_uri(mlflow_config['tracking_uri'])
        
        client = MlflowClient()
        
        return client
        
    except ImportError:
        raise ImportError("El paquete 'mlflow' no está instalado. Instálalo con: pip install mlflow")
    except Exception as e:
        raise Exception(f"Error al crear cliente de MLflow: {e}")

def test_databricks_connection() -> bool:
    """
    Probar la conexión a Databricks
    
    Returns:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        import requests
        
        databricks_creds = load_databricks_credentials()
        
        headers = {
            'Authorization': f'Bearer {databricks_creds["token"]}',
            'Content-Type': 'application/json'
        }
        
        url = f"{databricks_creds['host']}/api/2.0/clusters/list"
        response = requests.get(url, headers=headers, timeout=10)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error al probar conexión: {e}")
        return False

def test_mlflow_connection() -> bool:
    """
    Probar la conexión a MLflow en Databricks
    
    Returns:
        True si la conexión es exitosa, False en caso contrario
    """
    try:
        client = get_mlflow_client()
        
        # Intentar listar experimentos
        experiments = client.search_experiments()
        
        return True
        
    except Exception as e:
        print(f"Error al probar conexión MLflow: {e}")
        return False
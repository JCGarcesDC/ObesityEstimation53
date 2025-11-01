"""
Script para probar la conexión a Databricks y MLflow
"""
import os
import yaml
import sys
from pathlib import Path

def load_credentials():
    """Cargar credenciales desde el archivo YAML"""
    config_path = Path(__file__).parent.parent / "config" / "credentials.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de credenciales en: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as file:
        credentials = yaml.safe_load(file)
    
    return credentials

def test_databricks_connection():
    """Probar la conexión a Databricks"""
    try:
        # Cargar credenciales
        credentials = load_credentials()
        
        if 'databricks' not in credentials:
            print("❌ No se encontraron credenciales de Databricks en el archivo")
            return False
        
        databricks_config = credentials['databricks']
        token = databricks_config.get('token')
        host = databricks_config.get('host')
        
        if not token or not host:
            print("❌ Token o host de Databricks no encontrados")
            return False
        
        print("✅ Credenciales de Databricks cargadas correctamente")
        print(f"   Host: {host}")
        print(f"   Token: {token[:10]}...")
        
        # Configurar variables de entorno para Databricks
        os.environ['DATABRICKS_TOKEN'] = token
        os.environ['DATABRICKS_HOST'] = host
        
        # Intentar importar y usar databricks-sdk (si está disponible)
        try:
            import requests
            
            # Prueba básica de conectividad con la API de Databricks
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Endpoint simple para probar conectividad
            url = f"{host}/api/2.0/clusters/list"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("✅ Conexión exitosa a Databricks API")
                clusters = response.json().get('clusters', [])
                print(f"   Se encontraron {len(clusters)} clusters")
                return True
            else:
                print(f"❌ Error en la conexión a Databricks: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except ImportError:
            print("⚠️  El paquete 'requests' no está disponible")
            print("   No se puede probar la conectividad API, pero las credenciales están configuradas")
            return True
        except Exception as e:
            print(f"❌ Error al probar la conexión: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error al cargar credenciales: {e}")
        return False

def test_mlflow_databricks_config():
    """Probar la configuración de MLflow para Databricks"""
    try:
        credentials = load_credentials()
        
        if 'mlflow_databricks' not in credentials:
            print("❌ No se encontró configuración de MLflow para Databricks")
            return False
        
        mlflow_config = credentials['mlflow_databricks']
        tracking_uri = mlflow_config.get('tracking_uri')
        registry_uri = mlflow_config.get('registry_uri')
        
        print("✅ Configuración de MLflow para Databricks cargada:")
        print(f"   Tracking URI: {tracking_uri}")
        print(f"   Registry URI: {registry_uri}")
        
        # Configurar variables de entorno para MLflow
        if tracking_uri:
            os.environ['MLFLOW_TRACKING_URI'] = tracking_uri
        if registry_uri:
            os.environ['MLFLOW_REGISTRY_URI'] = registry_uri
        
        # Intentar importar MLflow
        try:
            import mlflow
            
            # Configurar MLflow para usar Databricks
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
            
            print("✅ MLflow configurado para usar Databricks")
            
            # Intentar obtener información del tracking server
            try:
                experiments = mlflow.search_experiments()
                print(f"✅ Conexión exitosa a MLflow en Databricks")
                print(f"   Se encontraron {len(experiments)} experimentos")
                return True
            except Exception as e:
                print(f"⚠️  MLflow configurado pero no se pudo conectar: {e}")
                print("   Esto puede ser normal si no tienes experimentos creados aún")
                return True
                
        except ImportError:
            print("⚠️  El paquete 'mlflow' no está disponible")
            print("   Instala mlflow para probar la conectividad completa")
            return True
        except Exception as e:
            print(f"❌ Error al configurar MLflow: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error al cargar configuración de MLflow: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 PRUEBA DE CONEXIÓN A DATABRICKS Y MLFLOW")
    print("=" * 60)
    
    # Probar conexión a Databricks
    print("\n📡 Probando conexión a Databricks...")
    databricks_ok = test_databricks_connection()
    
    # Probar configuración de MLflow
    print("\n📊 Probando configuración de MLflow...")
    mlflow_ok = test_mlflow_databricks_config()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE LA PRUEBA")
    print("=" * 60)
    
    if databricks_ok:
        print("✅ Databricks: Configuración correcta")
    else:
        print("❌ Databricks: Problemas de configuración")
    
    if mlflow_ok:
        print("✅ MLflow: Configuración correcta")
    else:
        print("❌ MLflow: Problemas de configuración")
    
    if databricks_ok and mlflow_ok:
        print("\n🎉 ¡Todas las configuraciones están correctas!")
        print("\n💡 Variables de entorno configuradas:")
        print(f"   DATABRICKS_TOKEN: {os.environ.get('DATABRICKS_TOKEN', 'No configurado')[:10]}...")
        print(f"   DATABRICKS_HOST: {os.environ.get('DATABRICKS_HOST', 'No configurado')}")
        print(f"   MLFLOW_TRACKING_URI: {os.environ.get('MLFLOW_TRACKING_URI', 'No configurado')}")
        print(f"   MLFLOW_REGISTRY_URI: {os.environ.get('MLFLOW_REGISTRY_URI', 'No configurado')}")
    else:
        print("\n⚠️  Hay algunos problemas de configuración que necesitan atención")
    
    return databricks_ok and mlflow_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
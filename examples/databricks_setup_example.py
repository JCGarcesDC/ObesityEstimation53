"""
Ejemplo de uso de las utilidades de Databricks en el proyecto ObesityMine53
"""
import sys
import os
from pathlib import Path

# Agregar el directorio src al path para imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from utils.databricks_utils import (
        setup_full_databricks_environment,
        test_databricks_connection,
        test_mlflow_connection
    )
except ImportError as e:
    print(f"Error de importación: {e}")
    print(f"Buscando en: {src_path}")
    print(f"Archivos en src: {list(Path(src_path).glob('*'))}")
    sys.exit(1)

def main():
    """
    Ejemplo de configuración y uso de Databricks
    """
    print("🔧 Configurando entorno de Databricks...")
    
    try:
        # Configurar entorno completo
        setup_full_databricks_environment()
        
        print("\n📡 Probando conexiones...")
        
        # Probar conexión a Databricks
        if test_databricks_connection():
            print("✅ Conexión a Databricks: OK")
        else:
            print("❌ Conexión a Databricks: FAILED")
        
        # Probar conexión a MLflow (si está disponible)
        try:
            if test_mlflow_connection():
                print("✅ Conexión a MLflow: OK")
            else:
                print("❌ Conexión a MLflow: FAILED")
        except ImportError:
            print("⚠️  MLflow no está instalado, omitiendo prueba")
        
        print("\n🎉 Configuración completada!")
        
        # Mostrar variables de entorno configuradas
        import os
        print("\n💡 Variables de entorno activas:")
        print(f"   DATABRICKS_HOST: {os.environ.get('DATABRICKS_HOST', 'No configurado')}")
        print(f"   DATABRICKS_TOKEN: {os.environ.get('DATABRICKS_TOKEN', 'No configurado')[:10]}...")
        print(f"   MLFLOW_TRACKING_URI: {os.environ.get('MLFLOW_TRACKING_URI', 'No configurado')}")
        print(f"   MLFLOW_REGISTRY_URI: {os.environ.get('MLFLOW_REGISTRY_URI', 'No configurado')}")
        
    except Exception as e:
        print(f"❌ Error en la configuración: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
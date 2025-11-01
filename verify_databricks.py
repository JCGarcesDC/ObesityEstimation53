"""
Script de verificación rápida para Databricks
Ejecutar con: python verify_databricks.py
"""
import sys
import os
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def quick_verification():
    """Verificación rápida de la configuración de Databricks"""
    
    print("🔍 VERIFICACIÓN RÁPIDA DE DATABRICKS")
    print("=" * 50)
    
    try:
        from utils.databricks_utils import (
            setup_full_databricks_environment,
            test_databricks_connection
        )
        
        # Configurar entorno
        setup_full_databricks_environment()
        
        # Probar conexión
        if test_databricks_connection():
            print("✅ ESTADO: Databricks configurado y funcionando correctamente")
            
            # Mostrar información básica
            print(f"\n📋 CONFIGURACIÓN ACTIVA:")
            print(f"   🌐 Host: {os.environ.get('DATABRICKS_HOST', 'No configurado')}")
            print(f"   🔑 Token: {os.environ.get('DATABRICKS_TOKEN', 'No configurado')[:15]}...")
            print(f"   📊 MLflow URI: {os.environ.get('MLFLOW_TRACKING_URI', 'No configurado')}")
            
            return True
        else:
            print("❌ ESTADO: Problemas de conectividad con Databricks")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = quick_verification()
    
    if success:
        print("\n🎉 ¡Todo listo para usar Databricks!")
    else:
        print("\n⚠️  Revisa la configuración de credenciales")
    
    sys.exit(0 if success else 1)
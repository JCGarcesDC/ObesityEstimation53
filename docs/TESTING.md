# Pruebas (pytest)

Ejecuta todas las pruebas con un solo comando, de forma silenciosa y rápida:

```bash
pytest -q
```

Notas:
- Requiere tener instalado el paquete del proyecto (pip install -e .) o ejecutar pytest desde la raíz del repo.
- Las pruebas cubren:
  - Preprocesamiento (limpieza, outliers, BMI)
  - Carga de datos (CSVDataLoader)
  - Preparación de datos para modelado (ColumnTransformer)
  - Pipeline de features (FeatureEngineeringPipeline)
  - Prueba de integración extremo a extremo (carga -> preprocesamiento -> predicción -> métricas)

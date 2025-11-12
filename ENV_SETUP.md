# Configuración del Ambiente Virtual - ObesityMine53# Configuración del entorno conda



Este proyecto utiliza un ambiente virtual Python local en la carpeta `.conda/` que ya está preconfigurado con Python 3.11.14 y todas las dependencias necesarias.Este archivo explica cómo crear y activar el entorno conda para este proyecto en Windows PowerShell.



## ✅ Estado Actual del Ambiente1. Abrir PowerShell (Windows PowerShell o Anaconda Prompt).



El ambiente virtual **YA ESTÁ INSTALADO Y FUNCIONAL** en `.conda/` con:2. Para crear el entorno desde `environment.yml`:

- **Python**: 3.11.14

- **Paquetes ML**: NumPy, Pandas, Scikit-learn, XGBoost, LightGBM, CatBoost```powershell

- **MLOps**: MLflow, DVC, pytest, pytest-covconda env create -f environment.yml

- **Notebooks**: Jupyter, IPyKernel```

- **Calidad**: Black, Flake8, isort, pre-commit

- **Total**: 200+ paquetes instaladosEsto creará un entorno llamado `obesitymine` (ver `name:` en `environment.yml`).



## 🚀 Uso Rápido (Quick Start)3. Activar el entorno:



### Opción 1: Script de Activación (Recomendado)```powershell

```powershellconda activate obesitymine

.\activate_env.ps1```

```

Este script verifica el ambiente y muestra información útil.4. Comprobar las dependencias instaladas:



### Opción 2: Uso Directo```powershell

```powershellpython -c "import sys; import numpy; import pandas; print(sys.version); print(numpy.__version__); print(pandas.__version__)"

# Ejecutar Python```

.\.conda\python.exe --version

5. Notas:

# Ejecutar scripts- Si usas Anaconda/Miniconda, asegúrate de tener `conda` en el PATH o usar Anaconda Prompt.

.\.conda\python.exe src\train.py- Para actualizar dependencias, edita `environment.yml` y ejecuta:



# Ejecutar tests```powershell

.\.conda\python.exe -m pytest -qconda env update -f environment.yml -n obesitymine

```

# Jupyter Notebook

.\.conda\python.exe -m jupyter notebook6. Alternativa si no tienes conda: crear un virtualenv y usar pip.

```

```powershell

### Opción 3: Crear Alias (PowerShell)python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt

```powershell```

# Añade al perfil: $PROFILE

Set-Alias py "$PWD\.conda\python.exe"## 2. Instalar el kernel Jupyter para el entorno



# Luego usa:Ejecuta este comando una sola vez (con el entorno activado):

py --version

py -m pytest -q```powershell

```python -m ipykernel install --user --name obesitymine --display-name "Python (obesitymine)"

```

## 📦 Verificación del Ambiente

## 3. Seleccionar el kernel en Jupyter/VS Code

```powershell

# Ver todos los paquetes instalados- Al abrir un notebook, selecciona el kernel llamado "Python (obesitymine)" en la barra superior.

.\.conda\python.exe -m pip list- Así todos los notebooks usarán el entorno y dependencias configuradas.



# Verificar paquetes clave## 4. Ubicación de los datos

.\.conda\python.exe -c "import numpy, pandas, sklearn, pytest; print('✅ Ambiente OK')"

- Coloca tus archivos CSV originales en la carpeta `data/raw/`.

# Ejecutar tests completos- Los scripts de procesamiento deben leer desde `data/raw/` y guardar los datos limpios en `data/processed/`.

.\.conda\python.exe -m pytest -q tests/
```

## 🔧 Mantenimiento

### Instalar nuevos paquetes
```powershell
.\.conda\python.exe -m pip install <paquete>
```

### Actualizar paquete
```powershell
.\.conda\python.exe -m pip install --upgrade <paquete>
```

### Exportar dependencias actualizadas
```powershell
.\.conda\python.exe -m pip freeze > requirements.txt
```

## 🆕 Crear Ambiente Nuevo (si no existe)

Si necesitas recrear el ambiente desde cero:

### Con Conda (preferido)
```powershell
conda env create -f environment.yml
conda activate obesitymine
```

### Con venv + pip (alternativa)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 🎯 Instalar Kernel Jupyter para el Ambiente

Ejecuta este comando una sola vez (para usar el ambiente en Jupyter/VS Code):

```powershell
.\.conda\python.exe -m ipykernel install --user --name obesitymine --display-name "Python (obesitymine)"
```

## 📁 Ubicación de los datos

- Coloca tus archivos CSV originales en la carpeta `data/raw/`.
- Los scripts de procesamiento deben leer desde `data/raw/` y guardar los datos limpios en `data/processed/`.

## 🧪 Comandos de Testing

```powershell
# Ejecutar todas las pruebas
.\.conda\python.exe -m pytest -q

# Ejecutar con cobertura
.\.conda\python.exe -m pytest --cov=src tests/

# Ejecutar tests específicos
.\.conda\python.exe -m pytest tests/test_preprocessing_cleaning.py -v
```

## 🐛 Troubleshooting

### "python no se reconoce como comando"
Usa la ruta completa: `.\.conda\python.exe`

### "No module named X"
Instala el paquete:
```powershell
.\.conda\python.exe -m pip install X
```

### Recrear ambiente desde cero
```powershell
# Opción 1: Borrar .conda y usar conda
Remove-Item -Recurse -Force .conda
conda env create -f environment.yml -p .\.conda

# Opción 2: Usar venv
python -m venv .conda
.\.conda\Scripts\Activate.ps1
pip install -r requirements.txt
```

# Script de Activación del Ambiente Virtual - ObesityMine53
# Uso: .\activate_env.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Activando Ambiente Virtual (.conda)  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que existe el ambiente
$condaPath = ".\.conda"
if (-Not (Test-Path $condaPath)) {
    Write-Host "❌ ERROR: Ambiente virtual no encontrado en $condaPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Para crear el ambiente, ejecuta:" -ForegroundColor Yellow
    Write-Host "  1. Instala Miniconda/Anaconda" -ForegroundColor White
    Write-Host "  2. conda env create -f environment.yml" -ForegroundColor White
    Write-Host "  3. conda activate obesitymine" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✅ Ambiente encontrado: $condaPath" -ForegroundColor Green
Write-Host ""

# Verificar Python
$pythonExe = "$condaPath\python.exe"
if (Test-Path $pythonExe) {
    $pythonVersion = & $pythonExe --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python no encontrado en el ambiente" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📦 Paquetes principales instalados:" -ForegroundColor Yellow
& $pythonExe -c "import sys; import numpy as np; import pandas as pd; import sklearn; import pytest; print(f'  • NumPy: {np.__version__}'); print(f'  • Pandas: {pd.__version__}'); print(f'  • Scikit-learn: {sklearn.__version__}'); print(f'  • Pytest: {pytest.__version__}')"

Write-Host ""
Write-Host "🎯 Para usar este ambiente:" -ForegroundColor Cyan
Write-Host "  Comando completo: .\.conda\python.exe <script.py>" -ForegroundColor White
Write-Host "  Ejemplo: .\.conda\python.exe src\train.py" -ForegroundColor White
Write-Host ""
Write-Host "  O crea un alias en tu perfil de PowerShell:" -ForegroundColor White
Write-Host '  Set-Alias py "$PWD\.conda\python.exe"' -ForegroundColor Gray
Write-Host "  py --version" -ForegroundColor Gray
Write-Host ""

Write-Host "🧪 Comandos útiles:" -ForegroundColor Cyan
Write-Host "  .\.conda\python.exe -m pytest -q          # Ejecutar tests" -ForegroundColor White
Write-Host "  .\.conda\python.exe -m pip list          # Ver paquetes" -ForegroundColor White
Write-Host "  .\.conda\python.exe -m jupyter notebook  # Abrir Jupyter" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✅ Ambiente listo para usar           " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

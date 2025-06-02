
@echo off
echo =============================
echo  INICIANDO PROYECTO FLASK
echo =============================

cd /d %~dp0

if not exist "venv\" (
    echo Creando entorno virtual...
    py -m venv venv
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -r requirements.txt

echo Ejecutando app.py...
py app.py

pause

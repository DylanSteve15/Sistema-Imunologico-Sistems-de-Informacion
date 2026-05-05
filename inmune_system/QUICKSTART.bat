@echo off
REM QUICKSTART.bat - Guía rápida de inicio para Windows

echo ==================================================
echo   Sistema Inmunologico de Monitoreo de BD
echo   Fase de Inicio Rapido
echo ==================================================
echo.

REM Paso 1: Verificar Python
echo [1/5] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado. Instalalo desde python.org
    pause
    exit /b 1
)
echo ✓ Python OK
echo.

REM Paso 2: Instalar dependencias
echo [2/5] Instalando dependencias...
pip install -r requirements.txt
echo ✓ Dependencias instaladas
echo.

REM Paso 3: Verificar MySQL
echo [3/5] Verificando conexion MySQL...
python test_db.py >nul 2>&1
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudo conectar a MySQL
    echo Asegurate de:
    echo   1. Tener MySQL corriendo (WampServer)
    echo   2. Actualizar credenciales en db.py
    echo.
)
echo.

REM Paso 4: Importar esquema
echo [4/5] Se recomienda importar el esquema SQL:
echo   mysql -u root -p erp_database ^< db_schema.sql
echo   (O importa desde phpMyAdmin)
echo.

REM Paso 5: Ejecutar servidor
echo [5/5] Iniciando servidor Flask...
echo Accede a: http://localhost:5000
echo.
echo Presiona CTRL+C para detener
echo.

python app.py

pause

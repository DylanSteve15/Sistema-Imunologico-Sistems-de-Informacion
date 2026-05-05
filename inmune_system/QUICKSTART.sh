#!/bin/bash
# QUICKSTART - Guía rápida de inicio

echo "=================================================="
echo "  Sistema Inmunológico de Monitoreo de BD"
echo "  Fase de Inicio Rápido"
echo "=================================================="
echo ""

# Paso 1: Verificar Python
echo "[1/5] Verificando Python..."
python --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python no encontrado. Instálalo desde python.org"
    exit 1
fi
echo "✓ Python OK"
echo ""

# Paso 2: Instalar dependencias
echo "[2/5] Instalando dependencias..."
pip install -r requirements.txt
echo "✓ Dependencias instaladas"
echo ""

# Paso 3: Verificar MySQL
echo "[3/5] Verificando conexión MySQL..."
python test_db.py 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ADVERTENCIA: No se pudo conectar a MySQL"
    echo "Asegúrate de:"
    echo "  1. Tener MySQL corriendo (WampServer)"
    echo "  2. Actualizar credenciales en db.py"
    echo ""
fi
echo ""

# Paso 4: Importar esquema
echo "[4/5] Se recomienda importar el esquema SQL:"
echo "  mysql -u root -p erp_database < db_schema.sql"
echo ""

# Paso 5: Ejecutar servidor
echo "[5/5] Iniciando servidor Flask..."
echo "Accede a: http://localhost:5000"
echo ""
echo "Presiona CTRL+C para detener"
echo ""

python app.py

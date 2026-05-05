#!/usr/bin/env python3
import db

conn = db.conectar()
cursor = conn.cursor()

print("\n" + "="*80)
print("🔍 DIAGNÓSTICO DETALLADO - VERIFICACIÓN DE CLAVES FORÁNEAS")
print("="*80)

# 1. Verificar PK de cada tabla referenciada
print("\n1️⃣  PK DE TABLAS REFERENCIADAS:")
print("-"*80)

tablas_ref = {
    'canal_venta': 'venta.IdCanal',
    'cliente': 'venta.IdCliente',
    'sucursal': 'venta.IdSucursal',
    'empleado': 'venta.IdEmpleado',
    'producto': 'venta.IdProducto',
    'proveedor': 'compra.IdProveedor',
    'tipo_producto': 'producto.IdTipoProducto'
}

for tabla, referencia in tablas_ref.items():
    try:
        cursor.execute(f"DESCRIBE `{tabla}`")
        columnas = cursor.fetchall()
        pk = None
        for col in columnas:
            if col[3] == 'PRI':
                pk = col[0]
                break
        registros = 0
        cursor.execute(f"SELECT COUNT(*) FROM `{tabla}`")
        registros = cursor.fetchone()[0]
        
        status = "✅" if registros > 0 else "⚠️"
        print(f"  {status} {tabla:20} | PK: {pk:20} | Registros: {registros}")
    except Exception as e:
        print(f"  ❌ {tabla:20} | Error: {e}")

# 2. Verificar valores reales de FK en venta
print("\n2️⃣  VALORES FK EN TABLA VENTA (primeras 5 filas):")
print("-"*80)

try:
    cursor.execute("""
        SELECT IdVenta, Fecha, IdCanal, IdCliente, IdSucursal, IdEmpleado, IdProducto
        FROM venta
        LIMIT 5
    """)
    rows = cursor.fetchall()
    for row in rows:
        print(f"  IdVenta={row[0]} | Fecha={row[1]} | IdCanal={row[2]} | IdCliente={row[3]} | IdSucursal={row[4]} | IdEmpleado={row[5]} | IdProducto={row[6]}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# 3. Verificar si los valores de FK existen en sus tablas
print("\n3️⃣  VERIFICACIÓN CRUZADA DE FK (muestreo):")
print("-"*80)

fk_checks = [
    ("canal_venta", "IdCanal", 1),
    ("cliente", "IdCliente", 1),
    ("sucursal", "IdSucursal", 1),
    ("empleado", "IDEmpleado", 1001056),  # ⚠️ Nota: IDEmpleado con D mayúscula
    ("producto", "IdProducto", 42925),
    ("proveedor", "IdProveedor", 1),
    ("tipo_producto", "IdTipoProducto", 1),
]

for tabla, columna, test_valor in fk_checks:
    try:
        cursor.execute(f"SELECT 1 FROM `{tabla}` WHERE `{columna}` = %s LIMIT 1", (test_valor,))
        existe = cursor.fetchone()
        status = "✅" if existe else "❌"
        print(f"  {status} {tabla:20} WHERE {columna:20} = {test_valor} | {'EXISTS' if existe else 'NOT FOUND'}")
    except Exception as e:
        print(f"  ❌ {tabla:20} | Error al consultar: {e}")

# 4. Problemas específicos
print("\n4️⃣  PROBLEMAS DETECTADOS:")
print("-"*80)

# Problema 1: IDEmpleado vs IdEmpleado
print("  ⚠️  PROBLEMA 1: Inconsistencia en nombre de columna")
print("      - Tabla 'empleado' usa: IDEmpleado (D mayúscula)")
print("      - Tabla 'venta' espera: IdEmpleado (d minúscula)")
print("      - Esto causa que las FKs fallen")

# Problema 2: Verificar si hay FKs definidas
try:
    cursor.execute("""
        SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'venta'
    """)
    fks = cursor.fetchall()
    print(f"\n  ⚠️  PROBLEMA 2: FKs definidas en tabla venta:")
    for fk in fks:
        if fk[3]:  # Si tiene tabla referenciada
            print(f"      - {fk[0]}: {fk[1]}.{fk[2]} -> {fk[3]}.{fk[4]}")
except Exception as e:
    print(f"  ⚠️  PROBLEMA 2: No se pueden leer las FKs: {e}")

conn.close()

print("\n" + "="*80)
print("📋 CONCLUSIÓN:")
print("="*80)
print("Para que funcione, necesitas:")
print("  1. Corregir el mismatch de IDEmpleado vs IdEmpleado en el código")
print("  2. Asegurar que el código consulte con los nombres correctos de columnas")
print("  3. Verificar que la función verify_foreign_keys() sea compatible")
print("="*80 + "\n")

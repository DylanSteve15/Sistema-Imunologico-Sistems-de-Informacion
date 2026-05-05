from db import conectar

# Guardar alerta (cuando se detecta un problema)
def guardar_alerta(tabla, descripcion, severidad="MEDIA"):
    conn = conectar()
    cursor = conn.cursor()

    sql = """
        INSERT INTO alertas_inmunitarias (tabla_afectada, tipo, descripcion, severidad)
        VALUES (%s, %s, %s, %s)
    """

    valores = (tabla, "Anomalia detectada", descripcion, severidad)

    cursor.execute(sql, valores)
    conn.commit()

    conn.close()


# Registrar memoria inmunológica
def registrar_memoria(tipo_anomalia):
    conn = conectar()
    cursor = conn.cursor()

    # ⚠️ IMPORTANTE: para que esto funcione bien, asegúrate de que tipo_anomalia sea UNIQUE
    sql = """
        INSERT INTO memoria_inmunologica (tipo_anomalia, frecuencia, ultima_ocurrencia)
        VALUES (%s, 1, NOW())
        ON DUPLICATE KEY UPDATE
            frecuencia = frecuencia + 1,
            ultima_ocurrencia = NOW()
    """

    cursor.execute(sql, (tipo_anomalia,))
    conn.commit()

    conn.close()
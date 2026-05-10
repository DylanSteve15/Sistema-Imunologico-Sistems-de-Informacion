import logging
import re
from db import conectar

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def normalizar_descripcion(texto):
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = re.sub(r'\d+(\.\d+)?', '{num}', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def guardar_alerta(tabla, descripcion, severidad="MEDIA"):
    conn = conectar()
    if not conn:
        logging.error("No se pudo conectar a la base de datos para guardar alerta.")
        return False

    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO alertas_inmunitarias
            (tabla_afectada, tipo, descripcion, severidad)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (tabla, "Anomalia detectada", descripcion, severidad))
        conn.commit()
        logging.info(f"Alerta registrada en {tabla} con severidad {severidad}")
        return True

    except Exception as e:
        logging.error(f"Error al guardar alerta: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def registrar_memoria(tabla, tipo_anomalia, severidad="MEDIA"):
    conn = conectar()
    if not conn:
        logging.error("No se pudo conectar a la base de datos para registrar memoria.")
        return False

    try:
        cursor = conn.cursor()
        tipo_normalizado = normalizar_descripcion(tipo_anomalia)

        sql = """
            INSERT INTO memoria_inmunologica
            (tabla_afectada, tipo_anomalia, tipo_normalizado, severidad, frecuencia, ultima_ocurrencia)
            VALUES (%s, %s, %s, %s, 1, NOW())
            ON DUPLICATE KEY UPDATE
                frecuencia = frecuencia + 1,
                severidad = VALUES(severidad),
                ultima_ocurrencia = NOW()
        """
        cursor.execute(sql, (tabla, tipo_anomalia, tipo_normalizado, severidad))
        conn.commit()

        logging.info(f"Memoria actualizada: {tabla} | {tipo_normalizado}")
        return True

    except Exception as e:
        logging.error(f"Error al registrar memoria: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def obtener_frecuencia_anomalia(tabla, descripcion):
    conn = conectar()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        tipo_normalizado = normalizar_descripcion(descripcion)

        sql = """
            SELECT frecuencia
            FROM memoria_inmunologica
            WHERE tabla_afectada = %s AND tipo_normalizado = %s
            LIMIT 1
        """
        cursor.execute(sql, (tabla, tipo_normalizado))
        row = cursor.fetchone()
        return int(row[0]) if row else 0

    except Exception as e:
        logging.error(f"Error al consultar frecuencia: {e}")
        return 0

    finally:
        conn.close()


def es_excepcion(tabla, descripcion):
    conn = conectar()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        tipo_normalizado = normalizar_descripcion(descripcion)

        sql = """
            SELECT 1
            FROM excepciones_inmunitarias
            WHERE tabla_afectada = %s
              AND tipo_normalizado = %s
            LIMIT 1
        """
        cursor.execute(sql, (tabla, tipo_normalizado))
        return cursor.fetchone() is not None

    except Exception as e:
        logging.error(f"Error al verificar excepción: {e}")
        return False

    finally:
        conn.close()


def marcar_como_falso_positivo(id_alerta):
    conn = conectar()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tabla_afectada, tipo, descripcion, severidad
            FROM alertas_inmunitarias
            WHERE id = %s
        """, (id_alerta,))
        alerta = cursor.fetchone()

        if not alerta:
            return False

        tabla, tipo, descripcion, severidad = alerta
        tipo_normalizado = normalizar_descripcion(descripcion)

        cursor.execute("""
            INSERT INTO excepciones_inmunitarias
            (tabla_afectada, tipo, descripcion, tipo_normalizado, severidad, fecha_aprendizaje)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (tabla, tipo, descripcion, tipo_normalizado, severidad))

        cursor.execute("""
            DELETE FROM alertas_inmunitarias
            WHERE id = %s
        """, (id_alerta,))

        conn.commit()
        logging.info(f"Alerta {id_alerta} movida a excepciones.")
        return True

    except Exception as e:
        logging.error(f"Error al marcar falso positivo: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def sugerir_severidad_por_memoria(tabla, descripcion, severidad_actual="MEDIA"):
    frecuencia = obtener_frecuencia_anomalia(tabla, descripcion)

    if frecuencia >= 10:
        return "CRITICA"
    if frecuencia >= 5 and severidad_actual == "MEDIA":
        return "ALTA"
    if frecuencia >= 3 and severidad_actual == "BAJA":
        return "MEDIA"
    return severidad_actual
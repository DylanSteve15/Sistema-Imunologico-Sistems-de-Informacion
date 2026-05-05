import mysql.connector

def conectar():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # 👈 pon tu contraseña si tienes
            database="erp_database"
        )
        return conexion
    except Exception as e:
        print("Error de conexión:", e)
        return None
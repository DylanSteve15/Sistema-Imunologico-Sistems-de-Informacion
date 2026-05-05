from db import conectar

def detectar_anomalias(tabla, datos):

    conn = conectar()
    cursor = conn.cursor()

    anomalias = []

    def parse_float(x):
        if x is None:
            return 0.0
        s = str(x).strip()
        if s == '':
            return 0.0
        # manejar formatos con comas
        try:
            return float(s)
        except Exception:
            try:
                # si tiene ',' como separador decimal
                if s.count(',') == 1 and s.count('.') == 0:
                    return float(s.replace(',', '.'))
                # quitar separadores de miles
                s2 = s.replace(',', '')
                return float(s2)
            except Exception:
                return 0.0

    def parse_int(x):
        try:
            return int(float(str(x).strip()))
        except Exception:
            return 0

    # VENTA
    if tabla == "venta":

        cursor.execute("SELECT AVG(Precio), AVG(Cantidad) FROM venta")
        prom = cursor.fetchone()
        # Reglas: precio/pronounced cambios y valores inválidos
        precio = parse_float(datos.get("Precio", 0))
        cantidad = parse_int(datos.get("Cantidad", 0))

        if precio <= 0:
            anomalias.append("Precio inválido o cero")
        elif prom[0] and precio > prom[0] * 3:
            anomalias.append("Precio de venta muy por encima del promedio")

        if cantidad <= 0:
            anomalias.append("Cantidad inválida o cero")
        elif prom[1] and cantidad > prom[1] * 3:
            anomalias.append("Cantidad de venta anómala")

        # No se aplican reglas basadas en IDs o en fechas aquí (se evitan validaciones por Id/Fecha)

    # COMPRA
    elif tabla == "compra":
        cantidad = int(datos.get("Cantidad", 0) or 0)
        if cantidad <= 0:
            anomalias.append("Compra con cantidad inválida")

        monto = float(datos.get("Monto", 0) or 0)
        if monto < 0:
            anomalias.append("Monto de compra negativo")

    # GASTO
    elif tabla == "gasto":

        cursor.execute("SELECT AVG(Monto) FROM gasto")
        prom = cursor.fetchone()[0]

        monto = float(datos.get("Monto", 0) or 0)
        if prom and monto > prom * 2:
            anomalias.append("Gasto excesivo detectado")
        if monto < 0:
            anomalias.append("Monto de gasto negativo")

    # CLIENTE
    elif tabla == "cliente":
        if len(datos.get("Nombre_y_Apellido", "")) < 5:
            anomalias.append("Nombre de cliente sospechoso")

    # Reglas generales
    # Campos con texto excesivamente largo o caracteres extraños
    for k, v in datos.items():
        try:
            if isinstance(v, str) and len(v) > 255:
                anomalias.append(f"Campo {k} demasiado largo")
        except Exception:
            pass

    conn.close()

    return anomalias
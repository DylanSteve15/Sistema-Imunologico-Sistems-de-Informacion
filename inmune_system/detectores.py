from db import conectar
import math


def obtener_precio_base(id_producto):
    conn = conectar()
    if not conn:
        return 0.0
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Precio FROM producto WHERE IdProducto = %s",
            (id_producto,)
        )
        row = cursor.fetchone()
        return float(row[0]) if row and row[0] is not None else 0.0
    except:
        return 0.0
    finally:
        conn.close()


def parse_numero(x):
    try:
        s = str(x).strip()

        if s == "":
            return 0.0

        if ',' in s and '.' in s:
            if s.rfind(',') > s.rfind('.'):
                s = s.replace('.', '').replace(',', '.')
            else:
                s = s.replace(',', '')
        elif ',' in s:
            s = s.replace('.', '').replace(',', '.')
        elif '.' in s:
            partes = s.split('.')
            if len(partes[-1]) == 3 and len(partes) > 1:
                s = s.replace('.', '')

        return float(s)
    except:
        return 0.0


def parse_entero(x):
    try:
        s = str(x).strip()
        if s == "":
            return 0
        s = s.replace('.', '').replace(',', '')
        return int(float(s))
    except:
        return 0

def calcular_estadisticos(tabla, campo):
    conn = conectar()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT
                COUNT(`{campo}`),
                AVG(`{campo}`),
                STDDEV_POP(`{campo}`),
                MIN(`{campo}`),
                MAX(`{campo}`)
            FROM `{tabla}`
            WHERE `{campo}` IS NOT NULL
        """)
        row = cursor.fetchone()

        if not row or row[0] == 0:
            return None

        n = int(row[0])
        media = float(row[1]) if row[1] is not None else 0.0
        desv = float(row[2]) if row[2] is not None else 0.0
        minimo = float(row[3]) if row[3] is not None else 0.0
        maximo = float(row[4]) if row[4] is not None else 0.0

        cursor.execute(f"""
            SELECT AVG(t.valor_mediano)
            FROM (
                SELECT `{campo}` AS valor_mediano
                FROM `{tabla}`
                WHERE `{campo}` IS NOT NULL
                ORDER BY `{campo}`
                LIMIT 2 - (SELECT COUNT(*) FROM `{tabla}` WHERE `{campo}` IS NOT NULL) % 2
                OFFSET (SELECT (COUNT(*) - 1) / 2 FROM `{tabla}` WHERE `{campo}` IS NOT NULL)
            ) t
        """)
        mediana_row = cursor.fetchone()
        mediana = float(mediana_row[0]) if mediana_row and mediana_row[0] is not None else media

        umbral_bajo = max(0, media - (2 * desv))
        umbral_alto = media + (2 * desv)

        coef_variacion = (desv / media * 100) if media > 0 else 0.0

        if coef_variacion < 15:
            nivel_riesgo = "BAJO"
        elif coef_variacion < 35:
            nivel_riesgo = "MEDIO"
        else:
            nivel_riesgo = "ALTO"

        return {
            "n": n,
            "media": media,
            "mediana": mediana,
            "desv_est": desv,
            "minimo": minimo,
            "maximo": maximo,
            "umbral_bajo": umbral_bajo,
            "umbral_alto": umbral_alto,
            "coef_variacion": coef_variacion,
            "nivel_riesgo": nivel_riesgo
        }

    except Exception:
        return None
    finally:
        conn.close()

def detectar_anomalias(tabla, datos):
    anomalias = []

    if tabla == "venta":
        anomalias.extend(_detectar_anomalias_venta(datos))

    elif tabla == "compra":
        anomalias.extend(_detectar_anomalias_compra(datos))

    elif tabla == "gasto":
        anomalias.extend(_detectar_anomalias_gasto(datos))

    elif tabla == "cliente":
        anomalias.extend(_detectar_anomalias_cliente(datos))

    elif tabla == "producto":
        anomalias.extend(_detectar_anomalias_producto(datos))

    return anomalias


def _detectar_anomalias_venta(datos):
    anomalias = []

    id_prod = datos.get("IdProducto")
    precio_total_ingresado = parse_numero(datos.get("Precio", 0))
    cantidad = parse_entero(datos.get("Cantidad", 0))
    precio_base = obtener_precio_base(id_prod)

    if precio_total_ingresado <= 0:
        anomalias.append("Precio total inválido (≤ 0)")

    if cantidad <= 0:
        anomalias.append("Cantidad inválida (≤ 0)")

    if not id_prod:
        anomalias.append("Venta sin producto asociado")

    if precio_base <= 0 and id_prod:
        anomalias.append("Producto sin precio base válido")
        return anomalias

    if precio_base > 0 and cantidad > 0:
        precio_total_esperado = precio_base * cantidad
        limite_superior = precio_total_esperado * 1.25
        limite_inferior = precio_total_esperado * 0.80

        if precio_total_ingresado > limite_superior:
            anomalias.append(
                f"Precio total ({precio_total_ingresado}) supera el 25% permitido del valor esperado ({precio_total_esperado})"
            )
        elif precio_total_ingresado < limite_inferior:
            anomalias.append(
                f"Precio total ({precio_total_ingresado}) está por debajo del 20% permitido del valor esperado ({precio_total_esperado})"
            )

    if cantidad > 100:
        anomalias.append(f"Cantidad ({cantidad}) inusualmente alta para una sola venta")

    stats_precio = calcular_estadisticos("venta", "Precio")
    if stats_precio and precio_total_ingresado > stats_precio["umbral_alto"]:
        anomalias.append(
            f"Precio de venta muy por encima del patrón histórico ({precio_total_ingresado} > {stats_precio['umbral_alto']:.2f})"
        )

    stats_cantidad = calcular_estadisticos("venta", "Cantidad")
    if stats_cantidad and cantidad > stats_cantidad["umbral_alto"]:
        anomalias.append(
            f"Cantidad de venta anómala según desviación estándar ({cantidad} > {stats_cantidad['umbral_alto']:.2f})"
        )

    return anomalias


def _detectar_anomalias_compra(datos):
    anomalias = []

    precio = parse_numero(datos.get("Precio", 0))
    cantidad = parse_entero(datos.get("Cantidad", 0))

    if cantidad <= 0:
        anomalias.append("Cantidad de compra inválida (≤ 0)")

    if precio <= 0:
        anomalias.append("Precio de compra inválido (≤ 0)")

    stats_precio = calcular_estadisticos("compra", "Precio")
    if stats_precio and precio > stats_precio["umbral_alto"]:
        anomalias.append(
            f"Precio de compra excesivo según patrón histórico ({precio} > {stats_precio['umbral_alto']:.2f})"
        )

    return anomalias


def _detectar_anomalias_gasto(datos):
    anomalias = []

    monto = parse_numero(datos.get("Monto", 0))

    if monto <= 0:
        anomalias.append("Monto de gasto inválido (≤ 0)")

    stats_monto = calcular_estadisticos("gasto", "Monto")
    if stats_monto and monto > stats_monto["umbral_alto"]:
        anomalias.append(
            f"Gasto excesivo detectado según desviación estándar ({monto} > {stats_monto['umbral_alto']:.2f})"
        )

    return anomalias


def _detectar_anomalias_cliente(datos):
    anomalias = []

    nombre = str(datos.get("NombreyApellido", "")).strip()
    telefono = str(datos.get("Telefono", "")).strip()

    if len(nombre) < 5:
        anomalias.append("Nombre de cliente sospechosamente corto")

    if telefono and len(telefono) < 7:
        anomalias.append("Teléfono de cliente sospechosamente corto")

    return anomalias


def _detectar_anomalias_producto(datos):
    anomalias = []

    nombre = str(datos.get("Producto", "")).strip()
    precio = parse_numero(datos.get("Precio", 0))

    if len(nombre) < 3:
        anomalias.append("Nombre de producto demasiado corto")

    if precio <= 0:
        anomalias.append("Precio de producto inválido (≤ 0)")

    stats_precio = calcular_estadisticos("producto", "Precio")
    if stats_precio and precio > stats_precio["umbral_alto"]:
        anomalias.append(
            f"Precio de producto fuera del patrón histórico ({precio} > {stats_precio['umbral_alto']:.2f})"
        )

    return anomalias
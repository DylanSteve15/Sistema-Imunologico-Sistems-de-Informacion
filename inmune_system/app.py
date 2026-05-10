from flask import Flask, render_template, request
from db import conectar
from inmunologico import analizar_y_guardar
from datetime import datetime
from ml_detector import detector_ml

app = Flask(__name__)


# =========================
# 🔧 HELPERS
# =========================

def get_primary_key(cursor, tabla):
    cursor.execute(f"DESCRIBE `{tabla}`")
    for c in cursor.fetchall():
        if c[3] == 'PRI':
            return c[0]
    return None


def get_table_schema(cursor, tabla):
    cursor.execute(f"DESCRIBE `{tabla}`")
    return cursor.fetchall()


def is_auto_increment_pk(cursor, tabla):
    cursor.execute(f"DESCRIBE `{tabla}`")
    for c in cursor.fetchall():
        campo = c[0]
        key = c[3]
        extra = c[5] if len(c) > 5 else ""
        if key == 'PRI' and 'auto_increment' in str(extra).lower():
            return campo
    return None


def get_referenced_table(cursor, tabla, columna):
    try:
        cursor.execute("""
            SELECT REFERENCED_TABLE_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
              AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (tabla, columna))
        row = cursor.fetchone()
        if row:
            return row[0]
    except Exception:
        pass

    mapa_fk = {
        "IdProducto": "producto",
        "IdTipoProducto": "tipoproducto",
        "IdProveedor": "proveedor",
        "IdCliente": "cliente",
        "IdEmpleado": "empleado",
        "IdSucursal": "sucursal",
        "IdSector": "sector",
        "IdCargo": "cargo",
        "IdCanal": "canalventa",
        "IdTipoGasto": "tipogasto",
        "IdLocalidad": "localidad",
        "IdProvincia": "provincia"
    }

    return mapa_fk.get(columna, columna[2:].lower())


def verify_foreign_keys(cursor, tabla, columnas, valores):
    pkcol = get_primary_key(cursor, tabla)

    for col, val in zip(columnas, valores):
        if not col.startswith('Id') or col == pkcol:
            continue

        ref_table = get_referenced_table(cursor, tabla, col)

        try:
            ref_pk = get_primary_key(cursor, ref_table) or col

            cursor.execute(
                f"SELECT 1 FROM `{ref_table}` WHERE `{ref_pk}`=%s LIMIT 1",
                (val,)
            )

            if not cursor.fetchone():
                return False, f"{col}={val} no existe en {ref_table}"

        except Exception as e:
            return False, f"Error FK en {col}: {str(e)}"

    return True, ""


# =========================
# 📅 CALENDARIO
# =========================

def asegurar_fecha_en_calendario(cursor, fecha):
    cursor.execute("SELECT 1 FROM calendario WHERE fecha = %s LIMIT 1", (fecha,))
    if cursor.fetchone():
        return

    f = datetime.strptime(fecha, "%Y-%m-%d")

    anio = f.year
    mes = f.month
    dia = f.day
    trimestre = (mes - 1) // 3 + 1
    semana = f.isocalendar()[1]

    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    dia_nombre = dias[f.weekday()]
    mes_nombre = meses[mes]

    cursor.execute("""
        INSERT INTO calendario
        (fecha, anio, mes, dia, trimestre, semana, dia_nombre, mes_nombre)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (fecha, anio, mes, dia, trimestre, semana, dia_nombre, mes_nombre))


# =========================
# 🏠 DASHBOARD
# =========================

@app.route('/')
def index():
    tablas = [("venta",), ("compra",), ("producto",)]
    return render_template('index.html', tablas=tablas)


# =========================
# 📋 FORMULARIO
# =========================

@app.route('/formulario/<tabla>')
def formulario_tabla(tabla):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"DESCRIBE `{tabla}`")
    columnas_raw = cursor.fetchall()

    columnas = []
    opciones = {}

    for col in columnas_raw:
        nombre = col[0]
        key = col[3]
        extra = col[5] if len(col) > 5 else ""

        if key == "PRI" and "auto_increment" in str(extra).lower():
            continue

        columnas.append(col)

        if nombre.startswith("Id") and key != 'PRI':
            ref_table = get_referenced_table(cursor, tabla, nombre)
            try:
                ref_pk = get_primary_key(cursor, ref_table) or "id"

                cursor.execute(
                    f"SELECT * FROM `{ref_table}` ORDER BY `{ref_pk}` DESC LIMIT 1500"
                )
                filas = cursor.fetchall()

                opciones[nombre] = [
                    (f[0], f"{f[0]} - {f[1] if len(f) > 1 and f[1] is not None else f[0]}")
                    for f in filas
                ]
            except Exception as e:
                print(f"Error cargando opciones para {nombre}: {e}")
                opciones[nombre] = []

    conn.close()

    return render_template(
        'formulario.html',
        tabla=tabla,
        columnas=columnas,
        opciones=opciones
    )


# =========================
# 🛒 INSERTAR
# =========================

@app.route('/api/insertar', methods=['POST'])
def api_insertar():
    tabla = request.form.get('tabla')
    conn = conectar()
    if not conn:
        return {"tipo": "danger", "mensaje": "No se pudo conectar a la base de datos"}

    cursor = conn.cursor()

    try:
        cursor.execute(f"DESCRIBE `{tabla}`")
        schema = cursor.fetchall()

        estructura = {c[0]: c[1].lower() for c in schema}
        pk_auto = None

        for c in schema:
            nombre = c[0]
            key = c[3]
            extra = c[5] if len(c) > 5 else ""
            if key == "PRI" and "auto_increment" in str(extra).lower():
                pk_auto = nombre

        datos = {}
        columnas = []
        valores = []

        for col in estructura:
            if col not in request.form:
                continue

            raw_val = request.form.get(col, "").strip()
            if raw_val == "":
                continue

            if col == pk_auto and raw_val in ("0", "0.0", ""):
                continue

            tipo = estructura[col]
            val = raw_val

            if "int" in tipo:
                val = int(str(raw_val).replace(".", "").replace(",", ""))
            elif "decimal" in tipo or "float" in tipo or "double" in tipo:
                v = str(raw_val).strip()

                if "," in v and "." in v:
                    if v.rfind(",") > v.rfind("."):
                        v = v.replace(".", "").replace(",", ".")
                    else:
                        v = v.replace(",", "")
                elif "," in v:
                    v = v.replace(".", "").replace(",", ".")
                elif "." in v:
                    partes = v.split(".")
                    if len(partes[-1]) == 3 and len(partes) > 1:
                        v = v.replace(".", "")

                val = float(v)

            columnas.append(col)
            valores.append(val)
            datos[col] = val

        print("TABLA:", tabla)
        print("COLUMNAS:", columnas)
        print("VALORES:", valores)
        print("DATOS:", datos)

        if "Fecha" in datos:
            asegurar_fecha_en_calendario(cursor, datos["Fecha"])
        if "FechaEntrega" in datos:
            asegurar_fecha_en_calendario(cursor, datos["FechaEntrega"])
        if "Fecha_Entrega" in datos:
            asegurar_fecha_en_calendario(cursor, datos["Fecha_Entrega"])

        ok, msg = verify_foreign_keys(cursor, tabla, columnas, valores)
        if not ok:
            conn.rollback()
            print("ERROR FK:", msg)
            return {"tipo": "danger", "mensaje": msg}

        permitido, anomalias = analizar_y_guardar(tabla, datos)
        if not permitido:
            conn.rollback()
            print("ANOMALIAS:", anomalias)
            return {"tipo": "danger", "mensaje": "Anomalía detectada", "anomalias": anomalias}

        cols_sql = ", ".join([f"`{c}`" for c in columnas])
        placeholders = ", ".join(["%s"] * len(valores))
        sql = f"INSERT INTO `{tabla}` ({cols_sql}) VALUES ({placeholders})"

        print("SQL FINAL:", sql)

        cursor.execute(sql, valores)
        conn.commit()

        print("INSERT OK")
        return {"tipo": "success", "mensaje": "Guardado correctamente"}

    except Exception as e:
        conn.rollback()
        print("ERROR REAL EN INSERT:", str(e))
        return {"tipo": "danger", "mensaje": str(e)}

    finally:
        conn.close()


# =========================
# 📊 VER DATOS
# =========================

@app.route('/api/datos/<tabla>')
def api_datos(tabla):
    conn = conectar()
    cursor = conn.cursor()

    pkcol = get_primary_key(cursor, tabla)
    if pkcol:
        cursor.execute(f"SELECT * FROM `{tabla}` ORDER BY `{pkcol}` DESC LIMIT 20")
    else:
        cursor.execute(f"SELECT * FROM `{tabla}` LIMIT 20")
    datos = cursor.fetchall()

    cursor.execute(f"DESCRIBE `{tabla}`")
    columnas = cursor.fetchall()

    conn.close()

    html = "<table class='table table-bordered'><tr>"
    for col in columnas:
        html += f"<th>{col[0]}</th>"
    html += "</tr>"

    for fila in datos:
        html += "<tr>"
        for val in fila:
            html += f"<td>{val}</td>"
        html += "</tr>"

    html += "</table>"
    return html


# =========================
# 🗑️ DELETE
# =========================

@app.route('/api/delete/<tabla>/<pk>')
def api_delete(tabla, pk):
    conn = conectar()
    cursor = conn.cursor()

    pkcol = get_primary_key(cursor, tabla)
    cursor.execute(f"DELETE FROM `{tabla}` WHERE `{pkcol}`=%s", (pk,))
    conn.commit()

    conn.close()
    return "OK"


# =========================
# ✏️ UPDATE
# =========================

@app.route('/api/update', methods=['POST'])
def api_update():
    tabla = request.form['tabla']

    conn = conectar()
    cursor = conn.cursor()

    pkcol = get_primary_key(cursor, tabla)

    set_parts = []
    valores = []
    pkval = None

    for k in request.form:
        if k == "tabla":
            continue
        if k == pkcol:
            pkval = request.form[k]
        else:
            set_parts.append(f"`{k}`=%s")
            valores.append(request.form[k])

    valores.append(pkval)

    sql = f"UPDATE `{tabla}` SET {', '.join(set_parts)} WHERE `{pkcol}`=%s"
    cursor.execute(sql, valores)

    conn.commit()
    conn.close()

    return "OK"


# =========================
# 📊 ALERTAS
# =========================

@app.route('/api/alertas')
def api_alertas():
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, tabla_afectada, tipo, descripcion, fecha, severidad
            FROM alertas_inmunitarias
            ORDER BY id DESC
            LIMIT 50
        """)
        datos = cursor.fetchall()
    except Exception as e:
        conn.close()
        return f"<div class='alert alert-danger'>Error cargando alertas: {str(e)}</div>"

    conn.close()

    html = f"""
    <div class='card shadow p-3'>
        <h4 class='mb-3'>🚨 Alertas del Sistema ({len(datos)})</h4>
        <div class='table-responsive'>
        <table class='table table-striped table-hover'>
        <thead class='table-dark'>
            <tr>
                <th>ID</th>
                <th>Tabla</th>
                <th>Tipo</th>
                <th>Descripción</th>
                <th>Fecha</th>
                <th>Severidad</th>
                <th>Acción</th>
            </tr>
        </thead>
        <tbody>
    """

    for a in datos:
        html += f"""
        <tr>
            <td>{a[0]}</td>
            <td>{a[1]}</td>
            <td>{a[2]}</td>
            <td>{a[3]}</td>
            <td>{a[4]}</td>
            <td class='fw-bold text-danger'>{a[5]}</td>
            <td>
                <button class='btn btn-sm btn-outline-success'
                        onclick="marcarFalsoPositivo({a[0]})">
                    Aprender
                </button>
            </td>
        </tr>
        """

    html += "</tbody></table></div></div>"
    return html


# =========================
# 🧠 MEMORIA
# =========================

@app.route('/api/memoria')
def api_memoria():
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, tabla_afectada, tipo_anomalia, tipo_normalizado, severidad,
                   frecuencia, ultima_ocurrencia
            FROM memoria_inmunologica
            ORDER BY frecuencia DESC, ultima_ocurrencia DESC
            LIMIT 100
        """)
        datos = cursor.fetchall()
    except Exception as e:
        conn.close()
        return f"<div class='alert alert-danger'>Error cargando memoria: {str(e)}</div>"

    conn.close()

    html = """
    <div class='card shadow p-3'>
        <h4 class='mb-3'>🧠 Memoria Inmunológica</h4>
        <div class='table-responsive'>
        <table class='table table-striped table-hover'>
        <thead class='table-dark'>
            <tr>
                <th>ID</th>
                <th>Tabla</th>
                <th>Tipo</th>
                <th>Patrón normalizado</th>
                <th>Severidad</th>
                <th>Frecuencia</th>
                <th>Última ocurrencia</th>
            </tr>
        </thead>
        <tbody>
    """

    for m in datos:
        html += f"""
        <tr>
            <td>{m[0]}</td>
            <td>{m[1]}</td>
            <td>{m[2]}</td>
            <td>{m[3]}</td>
            <td class='fw-bold text-danger'>{m[4]}</td>
            <td class='fw-bold text-primary'>{m[5]}</td>
            <td>{m[6]}</td>
        </tr>
        """

    html += "</tbody></table></div></div>"
    return html


# =========================
# 📋 TABLAS
# =========================

@app.route('/api/tablas')
def api_tablas():
    tablas = ["venta", "compra", "producto"]

    html = """
    <div class='card shadow p-3'>
        <h4 class='mb-3'>📊 Tablas del Sistema</h4>
        <table class='table table-hover'>
        <thead class='table-dark'>
            <tr>
                <th>Tabla</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody>
    """

    for t in tablas:
        html += f"""
        <tr>
            <td>{t}</td>
            <td>
                <button class='btn btn-sm btn-primary me-2'
                    onclick="loadPanel('tabla/{t}')">Ver</button>
                <button class='btn btn-sm btn-success'
                    onclick="loadPanel('formulario/{t}')">Insertar</button>
            </td>
        </tr>
        """

    html += "</tbody></table></div>"
    return html


# =========================
# 📊 VER TABLA COMPLETA
# =========================

@app.route('/api/tabla/<tabla>')
def api_ver_tabla(tabla):
    conn = conectar()
    cursor = conn.cursor()

    pkcol = get_primary_key(cursor, tabla)

    if pkcol:
        cursor.execute(f"SELECT * FROM `{tabla}` ORDER BY `{pkcol}` DESC LIMIT 200")
    else:
        cursor.execute(f"SELECT * FROM `{tabla}` LIMIT 200")

    datos = cursor.fetchall()

    cursor.execute(f"DESCRIBE `{tabla}`")
    columnas = cursor.fetchall()

    conn.close()

    html = "<div class='card p-3 shadow'>"
    html += f"<h4>Tabla: {tabla}</h4>"
    html += "<div class='table-responsive'>"
    html += "<table class='table table-striped table-bordered mt-3'>"

    html += "<thead class='table-dark'><tr>"
    for col in columnas:
        html += f"<th>{col[0]}</th>"
    html += "</tr></thead><tbody>"

    for fila in datos:
        html += "<tr>"
        for val in fila:
            html += f"<td>{val}</td>"
        html += "</tr>"

    html += "</tbody></table></div></div>"
    return html


# =========================
# 📊 ESTADÍSTICOS
# =========================

@app.route('/api/estadisticos')
def api_estadisticos():
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT
                p.IdProducto,
                p.Producto,
                COUNT(v.IdVenta) AS total_ventas,
                AVG(v.Precio) AS precio_promedio,
                MIN(v.Precio) AS precio_minimo,
                MAX(v.Precio) AS precio_maximo,
                STDDEV_POP(v.Precio) AS precio_desv,
                AVG(v.Cantidad) AS cantidad_promedio,
                MIN(v.Cantidad) AS cantidad_minima,
                MAX(v.Cantidad) AS cantidad_maxima,
                STDDEV_POP(v.Cantidad) AS cantidad_desv
            FROM producto p
            LEFT JOIN venta v ON v.IdProducto = p.IdProducto
            GROUP BY p.IdProducto, p.Producto
            HAVING COUNT(v.IdVenta) > 0
            ORDER BY total_ventas DESC, p.Producto ASC
            LIMIT 100
        """)
        datos = cursor.fetchall()

    except Exception as e:
        conn.close()
        return f"<div class='alert alert-danger'>Error cargando estadísticas por producto: {str(e)}</div>"

    conn.close()

    html = """
    <div class='card shadow p-3'>
        <h4 class='mb-3'>📊 Estadísticas por Producto</h4>
        <div class='table-responsive'>
        <table class='table table-striped table-hover table-bordered'>
        <thead class='table-dark'>
            <tr>
                <th>ID Producto</th>
                <th>Producto</th>
                <th>Total ventas</th>
                <th>Precio promedio</th>
                <th>Precio mínimo</th>
                <th>Precio máximo</th>
                <th>Desv. precio</th>
                <th>Cantidad promedio</th>
                <th>Cantidad mínima</th>
                <th>Cantidad máxima</th>
                <th>Desv. cantidad</th>
            </tr>
        </thead>
        <tbody>
    """

    for row in datos:
        id_producto = row[0]
        producto = row[1]
        total_ventas = row[2] or 0
        precio_promedio = float(row[3] or 0)
        precio_minimo = float(row[4] or 0)
        precio_maximo = float(row[5] or 0)
        precio_desv = float(row[6] or 0)
        cantidad_promedio = float(row[7] or 0)
        cantidad_minima = float(row[8] or 0)
        cantidad_maxima = float(row[9] or 0)
        cantidad_desv = float(row[10] or 0)

        html += f"""
        <tr>
            <td>{id_producto}</td>
            <td>{producto}</td>
            <td>{total_ventas}</td>
            <td>{precio_promedio:.2f}</td>
            <td>{precio_minimo:.2f}</td>
            <td>{precio_maximo:.2f}</td>
            <td>{precio_desv:.2f}</td>
            <td>{cantidad_promedio:.2f}</td>
            <td>{cantidad_minima:.2f}</td>
            <td>{cantidad_maxima:.2f}</td>
            <td>{cantidad_desv:.2f}</td>
        </tr>
        """

    html += """
        </tbody>
        </table>
        </div>
    </div>
    """
    return html 
    from detectores import calcular_estadisticos

    tablas_campos = {
        "venta": ["Precio", "Cantidad"],
        "compra": ["Precio", "Cantidad"],
        "gasto": ["Monto"],
        "producto": ["Precio"]
    }

    html = "<div class='row'>"

    for tabla, campos in tablas_campos.items():
        html += f"""
        <div class='col-md-6 col-lg-4 mb-4'>
            <div class='card shadow h-100'>
                <div class='card-header bg-primary text-white'>
                    <h5 class='mb-0'>📊 {tabla.upper()}</h5>
                </div>
                <div class='card-body'>
        """

        for campo in campos:
            try:
                stats = calcular_estadisticos(tabla, campo)

                if not stats or stats.get("n", 0) == 0:
                    html += f"""
                    <div class='mb-3 p-3 border rounded bg-light'>
                        <strong>{campo}</strong><br>
                        <span class='text-muted'>Sin datos suficientes</span>
                    </div>
                    """
                    continue

                color_riesgo = {
                    "BAJO": "success",
                    "MEDIO": "warning",
                    "ALTO": "danger"
                }.get(stats["nivel_riesgo"], "secondary")

                html += f"""
                <div class='mb-3 p-3 border rounded'>
                    <h6 class='fw-bold mb-2'>{campo}</h6>
                    <div><strong>Muestras:</strong> {stats['n']}</div>
                    <div><strong>Promedio:</strong> {stats['media']:.2f}</div>
                    <div><strong>Mediana:</strong> {stats['mediana']:.2f}</div>
                    <div><strong>Desv. Est.:</strong> {stats['desv_est']:.2f}</div>
                    <div><strong>Mínimo:</strong> {stats['minimo']:.2f}</div>
                    <div><strong>Máximo:</strong> {stats['maximo']:.2f}</div>
                    <div><strong>Rango normal:</strong> {stats['umbral_bajo']:.2f} - {stats['umbral_alto']:.2f}</div>
                    <div><strong>Coef. variación:</strong> {stats['coef_variacion']:.2f}%</div>
                    <div class='mt-2'>
                        <span class='badge bg-{color_riesgo}'>Variabilidad {stats['nivel_riesgo']}</span>
                    </div>
                </div>
                """

            except Exception as e:
                html += f"""
                <div class='mb-3 p-3 border rounded bg-light'>
                    <strong>{campo}</strong><br>
                    <span class='text-danger'>Error: {str(e)}</span>
                </div>
                """

        html += """
                </div>
            </div>
        </div>
        """

    html += "</div>"
    return html
# =========================
# 🤖 MACHINE LEARNING
# =========================

@app.route('/api/entrenar_ml/<tabla>')
def api_entrenar_ml(tabla):
    resultado = detector_ml.entrenar(tabla)
    return f"<div class='alert alert-success'>{resultado}</div>"


@app.route('/api/prediccion_ml/<tabla>', methods=['POST'])
def api_prediccion_ml(tabla):
    datos = {k: request.form.get(k, 0) for k in request.form if k != 'tabla'}
    prediccion = detector_ml.predecir(tabla, datos)
    return prediccion


@app.route('/api/falso_positivo/<int:id_alerta>')
def api_falso_positivo(id_alerta):
    from memoria import marcar_como_falso_positivo
    ok = marcar_como_falso_positivo(id_alerta)
    return "OK" if ok else "ERROR"


# =========================
# 🚀 RUN
# =========================

if __name__ == '__main__':
    app.run(debug=True)
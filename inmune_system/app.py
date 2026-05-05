from flask import Flask, render_template, request, redirect, url_for
from db import conectar
from inmunologico import analizar_y_guardar
from datetime import datetime

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
    except:
        pass
    return columna[2:].lower()


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
# 📅 CALENDARIO PRO (FIX REAL)
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

    # 🔥 NOMBRES EN ESPAÑOL
    dias = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
    meses = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

    dia_nombre = dias[f.weekday()]
    mes_nombre = meses[mes]

    cursor.execute("""
        INSERT INTO calendario
        (fecha, anio, mes, dia, trimestre, semana, dia_nombre, mes_nombre)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (fecha, anio, mes, dia, trimestre, semana, dia_nombre, mes_nombre))

    print(f"📅 Fecha insertada en calendario: {fecha}")


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
    columnas = cursor.fetchall()

    opciones = {}

    for col in columnas:
        nombre = col[0]

        if nombre.startswith("Id") and col[3] != 'PRI':
            ref_table = get_referenced_table(cursor, tabla, nombre)

            try:
                cursor.execute(f"SELECT * FROM `{ref_table}` LIMIT 100")
                filas = cursor.fetchall()
                opciones[nombre] = [
                    (f[0], f"{f[0]} - {f[1] if len(f) > 1 else f[0]}")
                    for f in filas
                ]
            except:
                opciones[nombre] = []

    conn.close()

    return render_template('formulario.html',
                           tabla=tabla,
                           columnas=columnas,
                           opciones=opciones)


# =========================
# 🛒 INSERTAR PRO
# =========================

@app.route('/api/insertar', methods=['POST'])
def api_insertar():

    tabla = request.form.get('tabla')

    conn = conectar()
    cursor = conn.cursor()

    datos = {}
    columnas = []
    valores = []

    try:
        cursor.execute(f"DESCRIBE `{tabla}`")
        estructura = {c[0]: c[1].lower() for c in cursor.fetchall()}

        # 🔄 LIMPIEZA + TIPOS
        for key in request.form:
            if key == "tabla":
                continue

            val = request.form.get(key).strip()
            if val == "":
                continue

            tipo = estructura.get(key, "")

            if "int" in tipo:
                val = int(val)
            elif "decimal" in tipo or "float" in tipo:
                val = float(val)
            elif "date" in tipo:
                val = val

            columnas.append(key)
            valores.append(val)
            datos[key] = val

        print("INSERT:", tabla, columnas, valores)

        # 🔥 ASEGURAR FECHAS ANTES DE VALIDAR FK
        if "Fecha" in datos:
            asegurar_fecha_en_calendario(cursor, datos["Fecha"])

        if "Fecha_Entrega" in datos:
            asegurar_fecha_en_calendario(cursor, datos["Fecha_Entrega"])

        # 🔥 IMPORTANTE: guardar calendario antes de usar FK
        conn.commit()

        # 🧠 SISTEMA INMUNE
        permitido, anomalias = analizar_y_guardar(tabla, datos)
        if not permitido:
            return {"tipo": "danger", "mensaje": "Anomalía", "anomalias": anomalias}

        # 🔗 VALIDAR FK
        ok, msg = verify_foreign_keys(cursor, tabla, columnas, valores)
        if not ok:
            return {"tipo": "danger", "mensaje": msg}

        # 🔥 INSERT FINAL
        cols = ", ".join([f"`{c}`" for c in columnas])
        placeholders = ", ".join(["%s"] * len(valores))

        sql = f"INSERT INTO `{tabla}` ({cols}) VALUES ({placeholders})"
        cursor.execute(sql, valores)

        conn.commit()
        conn.close()

        return {"tipo": "success", "mensaje": "Guardado correctamente"}

    except Exception as e:
        conn.rollback()
        conn.close()
        print("❌ ERROR:", e)
        return {"tipo": "danger", "mensaje": str(e)}


# =========================
# 📊 VER DATOS
# =========================

@app.route('/api/datos/<tabla>')
def api_datos(tabla):

    conn = conectar()
    cursor = conn.cursor()

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

    cursor.execute("SELECT * FROM alertas_inmunitarias ORDER BY Id DESC LIMIT 50")
    datos = cursor.fetchall()

    conn.close()

    html = """
    <div class='card shadow p-3'>
        <h4 class='mb-3'>🚨 Alertas del Sistema</h4>
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

    cursor.execute("SELECT * FROM memoria_inmunologica ORDER BY frecuencia DESC")
    datos = cursor.fetchall()

    conn.close()

    html = """
    <div class='card shadow p-3'>
        <h4 class='mb-3'>🧠 Memoria Inmunológica</h4>
        <div class='table-responsive'>
        <table class='table table-striped table-hover'>
        <thead class='table-dark'>
            <tr>
                <th>ID</th>
                <th>Tipo</th>
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
            <td class='fw-bold text-primary'>{m[2]}</td>
            <td>{m[3]}</td>
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
# 📊 VER TABLA COMPLETA (DESC)
# =========================

@app.route('/api/tabla/<tabla>')
def api_ver_tabla(tabla):

    conn = conectar()
    cursor = conn.cursor()

    # 🔑 detectar PK automáticamente
    pkcol = get_primary_key(cursor, tabla)

    # 🔥 ORDEN DESCENDENTE
    if pkcol:
        cursor.execute(f"SELECT * FROM `{tabla}` ORDER BY `{pkcol}` DESC LIMIT 200")
    else:
        cursor.execute(f"SELECT * FROM `{tabla}` LIMIT 200")

    datos = cursor.fetchall()

    cursor.execute(f"DESCRIBE `{tabla}`")
    columnas = cursor.fetchall()

    conn.close()

    # 🧾 GENERAR TABLA BONITA
    html = "<div class='card p-3 shadow'>"
    html += f"<h4>Tabla: {tabla}</h4>"
    html += "<div class='table-responsive'>"
    html += "<table class='table table-striped table-bordered mt-3'>"

    # encabezados
    html += "<thead class='table-dark'><tr>"
    for col in columnas:
        html += f"<th>{col[0]}</th>"
    html += "</tr></thead><tbody>"

    # filas
    for fila in datos:
        html += "<tr>"
        for val in fila:
            html += f"<td>{val}</td>"
        html += "</tr>"

    html += "</tbody></table></div></div>"

    return html


# =========================
# 🚀 RUN
# =========================

if __name__ == '__main__':
    app.run(debug=True)
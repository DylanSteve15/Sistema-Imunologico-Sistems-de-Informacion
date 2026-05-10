# 🧬 Sistema Inteligente de Monitoreo de Base de Datos
## Inspirado en el Sistema Inmunológico

Aplicación web desarrollada en **Python + Flask** para monitorear, validar y proteger la integridad lógica de una base de datos empresarial en **MySQL**, utilizando una metáfora inspirada en el sistema inmunológico humano.

El sistema analiza registros antes de insertarlos, detecta comportamientos anómalos, registra alertas, construye memoria histórica y aprende de falsos positivos para mejorar progresivamente su capacidad de respuesta.

---

## 📌 Descripción

Este proyecto implementa un mecanismo de defensa lógica para operaciones sobre un ERP, trasladando conceptos biológicos al contexto de bases de datos:

- **Self**: comportamiento esperado o registro válido.
- **Non-self**: comportamiento anómalo o sospechoso.
- **Antígeno**: dato ingresado que debe ser evaluado.
- **Anticuerpo**: regla o mecanismo de validación.
- **Memoria inmunológica**: historial de anomalías detectadas.
- **Aprendizaje adaptativo**: incorporación de falsos positivos como excepciones.

El objetivo no es solo insertar datos, sino **evaluarlos antes de persistirlos**, reduciendo errores, inconsistencias y operaciones sospechosas en tablas críticas del sistema. [file:1]

---

## 🎯 Objetivos

- Detectar anomalías antes de insertar registros.
- Validar reglas de negocio sobre tablas del ERP.
- Verificar integridad referencial de claves foráneas.
- Registrar alertas inmunológicas con severidad.
- Mantener memoria histórica de anomalías.
- Aprender de falsos positivos marcados por el usuario.
- Complementar la detección con modelos de Machine Learning. [file:1]

---

## 🏗️ Arquitectura

El proyecto sigue una arquitectura **cliente-servidor** con Flask como backend principal, MySQL como motor de persistencia y una interfaz web basada en plantillas HTML.

### Backend

| Archivo | Función |
|---------|---------|
| `app.py` | Controlador principal, rutas, formularios dinámicos, inserción, validación FK, calendario, alertas, memoria y vistas. |
| `db.py` | Conexión a la base de datos `erp_database`. |
| `inmunologico.py` | Motor central de análisis inmunológico y agregación de riesgo. |
| `detectores.py` | Reglas deterministas por tabla y validaciones estadísticas. |
| `memoria.py` | Gestión de alertas, memoria inmunológica, excepciones y aprendizaje por falsos positivos. |
| `ml_detector.py` | Entrenamiento y predicción de anomalías con Isolation Forest. | [file:1]

### Frontend

| Archivo | Función |
|---------|---------|
| `index.html` | Dashboard principal. |
| `formulario.html` | Formulario dinámico según la tabla seleccionada. |
| `alertas.html` | Vista de alertas inmunológicas. |
| `historial.html` | Historial o trazabilidad de eventos. |
| `tablas.html` | Listado de tablas disponibles. |
| `vertabla.html` | Vista tabular de registros. | [file:1]

### Base de datos

#### Tablas principales
- `venta`
- `compra`
- `producto`
- `cliente`
- `proveedor`
- `empleado`
- `sucursal`
- `canalventa`
- `tipoproducto`
- `tipogasto` [file:1]

#### Tablas auxiliares del sistema inmunológico
- `alertas_inmunitarias`
- `memoria_inmunologica`
- `excepciones_inmunitarias`
- `calendario` [file:1]

---

## 🧬 Modelo inmunológico

| Concepto biológico | Equivalente en el sistema |
|--------------------|---------------------------|
| Self | Operación válida |
| Non-self | Registro anómalo |
| Antígeno | Dato ingresado |
| Anticuerpo | Regla de validación |
| Memoria inmunológica | Historial de anomalías |
| Aprendizaje adaptativo | Gestión de falsos positivos | [file:1]

---

## ⚙️ Flujo de funcionamiento

1. El usuario accede al dashboard.
2. Selecciona una tabla del ERP.
3. El sistema genera automáticamente el formulario según la estructura de la tabla.
4. El usuario envía los datos.
5. Antes de insertar, el sistema:
   - normaliza tipos numéricos;
   - valida claves foráneas;
   - asegura fechas en `calendario`;
   - ejecuta reglas inmunológicas;
   - consulta memoria y excepciones;
   - complementa el análisis con ML si está disponible.
6. Si el registro es válido, se inserta.
7. Si es anómalo, se bloquea la operación y se registra la alerta.
8. El usuario puede marcar alertas como falsos positivos para que el sistema aprenda. [file:1]

---

## 🧪 Detección de anomalías

La detección actual combina dos capas:

### 1. Reglas deterministas
Implementadas en `detectores.py`, permiten validar condiciones específicas por tabla, por ejemplo:

#### `venta`
- Precio inválido o menor/igual a cero.
- Cantidad inválida o menor/igual a cero.
- Comparación del precio ingresado contra el precio base del producto.
- Evaluación del valor esperado según la cantidad.
- Revisión de cantidades inusualmente altas. [file:1]

#### `compra`
- Precio inválido.
- Cantidad inválida.
- Validaciones de consistencia del registro. [file:1]

#### `producto`
- Precio inválido.
- Nombre sospechosamente corto.
- Validación de coherencia general. [file:1]

#### `cliente`
- Nombre demasiado corto.
- Datos sospechosos o poco consistentes. [file:1]

### 2. Machine Learning
El módulo `ml_detector.py` usa **Isolation Forest** para detectar anomalías multivariadas en tablas con suficientes datos numéricos, funcionando como capa complementaria al sistema de reglas. [file:1]

---

## 🧠 Memoria inmunológica

Cada anomalía detectada puede registrarse en dos niveles:

### Alertas inmunitarias
Se almacenan en `alertas_inmunitarias` con:
- tabla afectada,
- tipo,
- descripción,
- fecha,
- severidad. [file:1]

### Memoria inmunológica
Se almacena en `memoria_inmunologica` con:
- tabla afectada,
- tipo de anomalía,
- versión normalizada,
- frecuencia,
- severidad,
- última ocurrencia. [file:1]

### Excepciones aprendidas
Los falsos positivos marcados por el usuario se almacenan en `excepciones_inmunitarias`, permitiendo que el sistema no vuelva a tratar esos mismos patrones como amenazas. [file:1]

---

## 📊 Estadísticos

El sistema incluye una vista estadística para apoyar la interpretación de patrones históricos. Actualmente, el enfoque más útil para el proyecto es el análisis **por producto**, mostrando:

- total de ventas por producto;
- precio promedio;
- precio mínimo y máximo;
- desviación estándar del precio;
- cantidad promedio, mínima y máxima;
- desviación estándar de cantidad.

Este enfoque se adapta mejor al proyecto que los promedios globales por tabla, ya que permite comparar cada venta contra el comportamiento histórico de su propio producto. [file:1]

---

## 🤖 Machine Learning

### Capacidades actuales
- Entrenamiento por tabla.
- Persistencia de modelos `.pkl`.
- Predicción de anomalías.
- Cálculo de score de confianza.
- Integración con Flask mediante endpoints. [file:1]

### Endpoints
- `GET /api/entrenar_ml/<tabla>`
- `POST /api/prediccion_ml/<tabla>` [file:1]

> El modelo de Machine Learning complementa el sistema basado en reglas; no lo reemplaza.

---

## 📅 Gestión automática de fechas

Cuando un registro contiene campos de fecha, el sistema verifica si esa fecha existe en la tabla `calendario`. Si no existe, la inserta automáticamente con atributos derivados como año, mes, día, trimestre, semana, nombre del día y nombre del mes. Esto evita errores de integridad referencial en tablas como `venta` y `compra`. [file:1]

---

## 🔗 Validación de claves foráneas

Antes de cada inserción, el sistema verifica que los IDs relacionados realmente existan en sus tablas de referencia. Esto se aplica a campos como:

- `IdProducto`
- `IdProveedor`
- `IdCliente`
- `IdEmpleado`
- `IdSucursal`
- `IdCanal`
- `IdTipoProducto`
- `IdTipoGasto` [file:1]

También se utiliza un mapeo explícito para columnas cuyo nombre no puede resolverse automáticamente a partir de la FK, por ejemplo:
- `IdCanal` → `canalventa`
- `IdTipoProducto` → `tipoproducto`
- `IdTipoGasto` → `tipogasto` [file:1]

---

## 📥 Endpoint principal de inserción

```http
POST /api/insertar
```

### Funciones principales
- detección dinámica de la estructura de tabla;
- exclusión de PK autoincrementales;
- normalización de enteros y decimales;
- aseguramiento de fechas;
- validación de claves foráneas;
- análisis inmunológico;
- inserción segura final. [file:1]

---

## 🌐 Endpoints disponibles

### Navegación
- `GET /`
- `GET /formulario/<tabla>`
- `GET /api/tablas`
- `GET /api/tabla/<tabla>`
- `GET /api/datos/<tabla>` [file:1]

### Inserción y edición
- `POST /api/insertar`
- `POST /api/update`
- `GET /api/delete/<tabla>/<pk>` [file:1]

### Sistema inmunológico
- `GET /api/alertas`
- `GET /api/memoria`
- `GET /api/falso_positivo/<id_alerta>` [file:1]

### Machine Learning
- `GET /api/entrenar_ml/<tabla>`
- `POST /api/prediccion_ml/<tabla>` [file:1]

### Estadísticos
- `GET /api/estadisticos` [file:1]

---

## 🧰 Requisitos

- Python 3.8 o superior
- MySQL 8
- pip
- Navegador web moderno [file:1]

---

## 🚀 Instalación

### 1. Ubicar el proyecto
```bash
cd "c:\Users\dylan\Documents\Phyton\Sistema Imunologico Sistems de Informacion\inmune_system"
```

### 2. Instalar dependencias
```bash
pip install flask mysql-connector-python scikit-learn pandas numpy joblib
```

### 3. Configurar la base de datos
```bash
mysql -u root -p erp_database < db_schema.sql
```

### 4. Configurar conexión en `db.py`
```python
import mysql.connector

def conectar():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="erp_database"
        )
        return conexion
    except Exception as e:
        print("Error de conexión:", e)
        return None
```

### 5. Ejecutar
```bash
python app.py
```

### 6. Abrir en navegador
[http://localhost:5000](http://localhost:5000)

---

## 📂 Estructura del proyecto

```bash
inmune_system/
│
├── app.py
├── db.py
├── detectores.py
├── inmunologico.py
├── memoria.py
├── ml_detector.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── index.html
│   ├── formulario.html
│   ├── alertas.html
│   ├── historial.html
│   ├── tablas.html
│   └── vertabla.html
│
└── __pycache__/
```

---

## 📌 Notas técnicas

- Las PK autoincrementales no deben enviarse manualmente.
- Los números deben normalizarse antes de insertarse.
- El sistema puede bloquear inserciones antes del `INSERT`.
- La memoria inmunológica crece cuando se detectan anomalías.
- El análisis ML requiere datos históricos suficientes para entrenar modelos confiables.
- La vista estadística debe interpretarse como apoyo al análisis, no como único mecanismo de decisión. [file:1]

---

## 💡 Aporte del proyecto

Este sistema no se limita a registrar datos. Su valor está en que:

- protege la integridad lógica de la base de datos;
- incorpora validación preventiva;
- centraliza alertas y memoria histórica;
- mejora la trazabilidad y auditoría;
- combina reglas deterministas con aprendizaje automático;
- aplica una metáfora biológica a un problema real de software empresarial. [file:1]

---

## 📈 Trabajo futuro

- Reentrenamiento automático del modelo ML.
- Reglas más específicas para más tablas del ERP.
- Panel gráfico con indicadores inmunológicos.
- Mayor explicabilidad en alertas.
- Auditoría por usuario.
- Aprendizaje incremental basado en excepciones validadas. [file:1]

---

## 👨‍💻 Autor

Proyecto académico orientado al monitoreo inteligente y protección lógica de bases de datos empresariales.

**Autor:** Dylan  
**Última actualización:** Mayo 2026

---

## 🛠️ Depuración

Si el sistema no inserta correctamente, revisa:

1. Conexión a MySQL.
2. Existencia real de claves foráneas.
3. Estructura de tablas con `SHOW CREATE TABLE`.
4. Datos enviados por el formulario.
5. Alertas y memoria inmunológica.
6. Logs de consola del backend. [file:1]

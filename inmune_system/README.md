# 🧬 Sistema Inteligente de Monitoreo de Base de Datos
## Inspirado en el Sistema Inmunológico

---

## 📌 Descripción General

Este proyecto consiste en el diseño e implementación de una aplicación web desarrollada en **Python con Flask** para monitorear, analizar y proteger la integridad de una **base de datos empresarial en MySQL**.

El sistema toma como inspiración el funcionamiento del **sistema inmunológico humano**, trasladando conceptos como **self, non-self, anticuerpos, memoria inmunológica y aprendizaje adaptativo** al contexto de operaciones sobre bases de datos empresariales.

Su propósito principal es evaluar registros antes de ser insertados, detectar comportamientos anómalos, registrar alertas, aprender de eventos previos y fortalecer progresivamente la seguridad lógica del sistema.

---

## 🎯 Objetivo del Sistema

Desarrollar una aplicación que sea capaz de:

- ✅ Detectar anomalías en tiempo real antes de insertar registros.
- ✅ Validar reglas de negocio sobre tablas críticas del ERP.
- ✅ Verificar integridad referencial de claves foráneas.
- ✅ Registrar alertas inmunológicas en una bitácora interna.
- ✅ Mantener una memoria histórica de anomalías detectadas.
- ✅ Aprender de falsos positivos mediante retroalimentación del usuario.
- ✅ Incorporar modelos de Machine Learning para complementar la detección.

---

## 🏗️ Arquitectura del Proyecto

El sistema sigue una arquitectura **cliente-servidor** construida sobre Flask, organizada en backend, frontend y base de datos.

### 🔹 Backend

| Archivo | Descripción |
|---------|-------------|
| `app.py` | Controlador principal. Maneja rutas, formularios dinámicos, inserciones, validación FK, calendario y visualización del sistema. |
| `db.py` | Módulo de conexión a MySQL. |
| `inmunologico.py` | Orquestador de la lógica inmunológica; decide si un registro se permite o se bloquea. |
| `detectores.py` | Reglas específicas por tabla para identificar anomalías de negocio y consistencia. |
| `memoria.py` | Guarda alertas, registra memoria inmunológica y permite aprendizaje de falsos positivos. |
| `ml_detector.py` | Entrenamiento y predicción de modelos de Machine Learning para detección de anomalías multivariadas. |

### 🔹 Frontend

| Archivo | Descripción |
|---------|-------------|
| `index.html` | Dashboard principal del sistema. |
| `formulario.html` | Formulario dinámico generado según la tabla seleccionada. |
| `alertas.html` | Visualización de alertas detectadas. |
| `historial.html` | Historial o trazabilidad de eventos. |
| `tablas.html` | Menú/listado de tablas disponibles. |
| `ver_tabla.html` / `vertabla.html` | Vista detallada de registros de una tabla. |

### 🔹 Base de Datos

#### Tablas principales del ERP
- `venta`
- `compra`
- `producto`
- `cliente`
- `proveedor`
- `empleado`
- `gasto`
- `sucursal`
- `canal_venta`
- `tipo_producto`
- `tipo_gasto`

#### Tablas auxiliares del sistema inmunológico
- `alertas_inmunitarias`
- `memoria_inmunologica`
- `patrones_normales`
- `calendario`

---

## 🧬 Modelo Conceptual Inmunológico

| Sistema Biológico | Sistema Implementado |
|-------------------|---------------------|
| **Self** | Operación válida o comportamiento esperado |
| **Non-self** | Registro anómalo, inconsistente o sospechoso |
| **Antígeno** | Dato ingresado que debe ser evaluado |
| **Anticuerpo** | Regla de validación aplicada |
| **Memoria inmunológica** | Historial de alertas y patrones detectados |
| **Aprendizaje adaptativo** | Marcado de falsos positivos y reentrenamiento futuro |

---

## ⚙️ Funcionamiento General

1. El usuario ingresa al dashboard.
2. Selecciona una tabla del ERP.
3. El sistema genera automáticamente un formulario basado en la estructura de la tabla.
4. El usuario ingresa los datos.
5. Antes de insertar, el sistema:
   - valida tipos,
   - normaliza números,
   - verifica claves foráneas,
   - asegura fechas en la tabla `calendario`,
   - ejecuta el análisis inmunológico,
   - opcionalmente complementa con Machine Learning.
6. Si el registro es válido, se guarda en la base de datos.
7. Si se detecta una anomalía, se bloquea la operación y se registra una alerta.
8. El usuario puede marcar alertas como falsos positivos para que el sistema aprenda.

---

## 🧪 Lógica de Detección Actual

La detección se realiza principalmente en `detectores.py` y puede combinar:

- reglas de negocio,
- validaciones por rangos,
- comparación contra precios base,
- validaciones por cantidad,
- análisis de consistencia entre campos,
- revisión de texto excesivo,
- validación de claves foráneas.

### Ejemplos por tabla

#### `venta`
- Precio inválido o menor/igual a cero.
- Cantidad inválida o menor/igual a cero.
- Comparación del valor de venta frente al precio base del producto.
- Evaluación del monto esperado según la cantidad.

#### `compra`
- Cantidad inválida.
- Precio inválido.
- Revisión de coherencia respecto al producto seleccionado.

#### `producto`
- Validación del precio.
- Validación de tipo de producto.
- Integridad referencial sobre `IdTipoProducto`.

#### `gasto`
- Monto inválido.
- Comparación contra `Monto_Aproximado` del tipo de gasto.

#### `cliente`
- Nombre demasiado corto.
- Edad fuera de rango razonable.
- Validaciones de consistencia general.

---

## 🧠 Memoria Inmunológica

El sistema registra cada anomalía detectada en dos niveles:

### 1. Alertas inmunitarias
Se almacenan en la tabla `alertas_inmunitarias` con información como:
- tabla afectada,
- tipo,
- descripción,
- fecha,
- severidad.

### 2. Memoria inmunológica
Se almacena en `memoria_inmunologica` para llevar control de:
- tipo de anomalía,
- frecuencia,
- última ocurrencia.

Esto permite que el sistema construya un historial útil para análisis posteriores y mejora continua.

---

## 🤖 Machine Learning

El proyecto incorpora un módulo `ml_detector.py` basado en **Isolation Forest** para detectar anomalías multivariadas en tablas con suficientes columnas numéricas.

### Capacidades actuales
- Entrenamiento por tabla.
- Persistencia de modelos `.pkl`.
- Predicción de anomalías.
- Cálculo de score de confianza.
- Integración con rutas Flask.

### Rutas disponibles
- `GET /api/entrenar_ml/<tabla>`
- `POST /api/prediccion_ml/<tabla>`

> El modelo ML actúa como complemento del sistema inmunológico basado en reglas, no como reemplazo total.

---

## 📅 Gestión automática de calendario

Cuando una operación contiene campos de fecha como `Fecha` o `Fecha_Entrega`, el sistema verifica automáticamente si esa fecha existe en la tabla `calendario`.

Si no existe, la inserta con:
- año,
- mes,
- día,
- trimestre,
- semana,
- nombre del día,
- nombre del mes.

Esto garantiza consistencia temporal y evita errores de FK en tablas como `venta`, `compra` y `gasto`.

---

## 🔗 Validación de claves foráneas

Antes de cada inserción, el sistema revisa si los valores de claves foráneas realmente existen en sus tablas relacionadas.

Esto se aplica, por ejemplo, a campos como:
- `IdProducto`
- `IdProveedor`
- `IdCliente`
- `IdEmpleado`
- `IdTipoProducto`
- `IdTipoGasto`
- `IdCanal`
- `IdSucursal`

Además, se incorporó un mapeo explícito para tablas cuyo nombre real no puede inferirse directamente desde el nombre de la columna, como:
- `IdTipoProducto` → `tipo_producto`
- `IdTipoGasto` → `tipo_gasto`
- `IdCanal` → `canal_venta`

---

## 📥 Inserción Inteligente

La ruta principal de inserción es:

```http
POST /api/insertar
```

Características:
- detección automática de la estructura de tabla,
- exclusión de PK autoincrementales,
- normalización de enteros y decimales,
- verificación de FK,
- análisis inmunológico,
- inserción final segura.

---

## 📊 Endpoints principales

### Navegación y vistas
- `GET /`
- `GET /formulario/<tabla>`
- `GET /api/tablas`
- `GET /api/tabla/<tabla>`
- `GET /api/datos/<tabla>`

### Inserción y actualización
- `POST /api/insertar`
- `POST /api/update`
- `GET /api/delete/<tabla>/<pk>`

### Sistema inmunológico
- `GET /api/alertas`
- `GET /api/memoria`
- `GET /api/falso_positivo/<id_alerta>`

### Machine Learning
- `GET /api/entrenar_ml/<tabla>`
- `POST /api/prediccion_ml/<tabla>`

### Estadísticos
- `GET /api/estadisticos`

---

## 🧰 Requisitos

- Python 3.8 o superior
- MySQL 8
- pip
- Navegador web moderno

---

## 🚀 Instalación

### 1. Clonar o abrir el proyecto
```bash
cd "c:\Users\dylan\Documents\Phyton\Sistema Imunologico Sistems de Informacion\inmune_system"
```

### 2. Instalar dependencias
```bash
pip install flask mysql-connector-python scikit-learn pandas numpy joblib
```

### 3. Configurar base de datos
Importa tu esquema SQL:

```bash
mysql -u root -p erp_database < db_schema.sql
```

### 4. Configurar conexión
Edita `db.py` si necesitas cambiar credenciales:

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

### 5. Ejecutar la aplicación
```bash
python app.py
```

### 6. Abrir en navegador
[http://localhost:5000](http://localhost:5000)

---

## 📂 Estructura del Proyecto

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

## 📌 Notas Técnicas Importantes

- Las PK autoincrementales no deben enviarse manualmente en formularios.
- Los formatos numéricos deben normalizarse antes de insertarse.
- Los precios base del catálogo deben almacenarse correctamente en MySQL, por ejemplo `200000.000` y no `200.000` si se quiere representar doscientos mil.
- Los nombres de tablas referenciadas no siempre coinciden automáticamente con el nombre de la columna FK, por lo que se usa un mapeo explícito.
- El sistema inmunológico puede bloquear inserciones antes de llegar al `INSERT`.
- La memoria inmunológica solo crece cuando se detectan anomalías reales.

---

## 💡 Valor del Proyecto

Este sistema aporta valor porque no solo realiza inserciones y consultas, sino que:

- 🧠 Aprende del historial de anomalías.
- 🛡️ Protege la integridad lógica de la base de datos.
- 📊 Centraliza alertas y memoria de eventos.
- 🔍 Permite trazabilidad y auditoría.
- 🤖 Integra reglas determinísticas con Machine Learning.
- 🏥 Traslada una metáfora biológica a una solución real de software empresarial.

---

## 📈 Trabajo Futuro

Líneas de mejora previstas:

- Reentrenamiento automático del modelo ML con excepciones validadas.
- Incorporación de nuevos módulos (`empleado`, `proveedor`, `cliente`) con más reglas específicas.
- Panel gráfico de indicadores inmunológicos.
- Clasificación de severidad más avanzada.
- Auditoría por usuario y trazabilidad de acciones.
- Explicabilidad de alertas con mayor detalle.

---

## 👨‍💻 Autor

Proyecto desarrollado como parte de un sistema inteligente de protección y monitoreo de bases de datos empresariales inspirado en principios inmunológicos.

**Autor:** Dylan  
**Fecha de actualización:** Mayo 2026

---

## 📞 Soporte y Depuración

Si el sistema no inserta correctamente, revisa:

1. Conexión a MySQL.
2. Existencia real de claves foráneas.
3. Estructura de las tablas (`SHOW CREATE TABLE`).
4. Valores enviados por el formulario.
5. Alertas del sistema inmunológico.
6. Logs de consola en `app.py`.
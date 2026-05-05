# 🧬 Sistema Inteligente de Monitoreo de Base de Datos
## Inspirado en el Sistema Inmunológico

---

## 📌 Descripción General del Proyecto

El presente proyecto consiste en el diseño e implementación de una aplicación web desarrollada en **Python con Flask**, cuya finalidad es monitorear, analizar y proteger la integridad de una **base de datos empresarial en MySQL**.

El sistema se inspira en el funcionamiento del **sistema inmunológico humano**, utilizando conceptos como **self, non-self, anticuerpos y memoria inmunológica** para detectar comportamientos anómalos dentro de las operaciones de la base de datos.

---

## 🎯 Objetivo del Sistema

Desarrollar una aplicación que:

- ✅ Aprenda patrones normales de operación en la base de datos.
- ✅ Detecte anomalías en tiempo real.
- ✅ Bloquee o alerte operaciones sospechosas.
- ✅ Registre historial de eventos para mejorar su comportamiento (memoria inmunológica).

---

## 🏗️ Estructura del Proyecto

El sistema fue desarrollado bajo una **arquitectura cliente-servidor** utilizando Flask, organizada en los siguientes componentes:

### 🔹 Backend (Python - Flask)

| Archivo | Descripción |
|---------|-------------|
| **app.py** | Controlador principal del sistema. Maneja rutas, inserción de datos, análisis inmunológico y comunicación con el frontend. |
| **db.py** | Encargado de la conexión a la base de datos MySQL. |
| **inmunologico.py** | Contiene la lógica del sistema inmunológico: detección de anomalías, reglas de validación, registro de alertas y gestión de memoria inmunológica. |
| **detectores.py** | Define las reglas específicas de detección para cada tabla (venta, compra, gasto, cliente, etc.). |
| **memoria.py** | Gestiona el almacenamiento y actualización de alertas e historial inmunológico. |

### 🔹 Base de Datos (MySQL)

**Tablas Principales (ERP simplificado):**
- `venta` - Registros de ventas
- `compra` - Registros de compras
- `producto` - Catálogo de productos
- `cliente` - Base de clientes
- `proveedor` - Base de proveedores
- `canal_venta` - Canales de distribución
- `gasto` - Registro de gastos

**Tablas Auxiliares (Sistema Inmunológico):**
- `alertas_inmunitarias` - Registro de anomalías detectadas
- `memoria_inmunologica` - Historial de comportamiento del sistema
- `patrones_normales` - Valores de referencia (promedios, límites, etc.)

### 🔹 Frontend (HTML + Bootstrap + JS)

| Template | Descripción |
|----------|-------------|
| **index.html** | Dashboard único con panel lateral, formularios dinámicos y visualización en tiempo real. |
| **formulario.html** | Formularios dinámicos generados según la tabla seleccionada. |
| **tablas.html** | Listado de tablas disponibles. |
| **alertas.html** | Visualización de alertas inmunológicas. |
| **historial.html** | Registro histórico de anomalías. |
| **ver_tabla.html** | Vista detallada de registros en una tabla. |

---

## 🧬 Implementación del Sistema Inmunológico

### Concepto Biológico → Implementación Digital

| Sistema Biológico | Sistema Implementado |
|-------------------|---------------------|
| **Self** | Datos normales en la base de datos |
| **Non-self** | Datos anómalos o inconsistentes |
| **Antígeno** | Registro sospechoso (ej: venta fuera de rango) |
| **Anticuerpo** | Reglas de validación |
| **Memoria inmunológica** | Historial de anomalías |

### Función Principal: `analizar_y_guardar(tabla, datos)`

```python
def analizar_y_guardar(tabla, datos):
    """
    Analiza datos ingresados antes de ser guardados.
    
    Retorna: (permitido: bool, anomalias: list)
    - Si hay anomalías: bloquea operación y registra alerta
    - Si es válido: permite inserción
    """
```

---

## ⚙️ Flujo de Funcionamiento

1. 👤 El usuario accede al dashboard
2. 📋 Selecciona una tabla (ej: venta, compra, producto)
3. 📝 El sistema genera un formulario dinámico
4. ✍️ El usuario ingresa datos
5. 🔍 **Sistema Inmunológico analiza:**
   - Compara con patrones normales
   - Valida rangos de valores
   - Verifica integridad referencial (FK)
   - Detecta inconsistencias
6. ✅ **Si es válido:** 
   - Permite inserción
   - Guarda en BD
   - Muestra confirmación
7. ❌ **Si detecta anomalía:**
   - Bloquea operación
   - Registra en `alertas_inmunitarias`
   - Actualiza `memoria_inmunologica`
   - Muestra mensaje de error

---

## 📌 Ejemplos de Detección

### 🔴 VENTA

- ❌ Cantidad = 0 o negativa → **Anomalía**
- ❌ Precio = 0 o negativo → **Anomalía**
- ❌ Precio > 3x el promedio → **Anomalía**
- ❌ Cantidad > 3x el promedio → **Anomalía**
- ⚠️ Campo Precio > 255 caracteres → **Anomalía**

### 🔴 COMPRA

- ❌ Cantidad inválida o cero → **Anomalía**
- ❌ Monto negativo → **Anomalía**

### 🔴 GASTO

- ❌ Monto > 2x el promedio → **Anomalía**
- ❌ Monto negativo → **Anomalía**

### 🔴 CLIENTE

- ❌ Nombre < 5 caracteres → **Anomalía**

---

## 🚀 Instalación y Configuración

### Requisitos

- Python 3.8+
- MySQL Server (WampServer recomendado)
- pip

### Paso 1: Clonar o descargar el proyecto

```bash
cd "c:\Users\dylan\Documents\Phyton\Sistema Imunologico Sistems de Informacion\inmune_system"
```

### Paso 2: Instalar dependencias

```bash
pip install flask mysql-connector-python
```

### Paso 3: Configurar base de datos

1. Importar schema SQL:
   ```bash
   mysql -u root -p erp_database < db_schema.sql
   ```

2. Actualizar credenciales en `db.py` si es necesario

### Paso 4: Ejecutar la aplicación

```bash
python app.py
```

3. Abrir en navegador: [http://localhost:5000](http://localhost:5000)

---

## 🧪 Tecnologías Utilizadas

| Categoría | Tecnología |
|-----------|-----------|
| **Backend** | Python 3, Flask |
| **Base de Datos** | MySQL 8 |
| **Frontend** | HTML5, CSS3, Bootstrap 5 |
| **Interacción** | JavaScript (Fetch API) |
| **Conector** | mysql-connector-python |
| **Animaciones** | Animate.css |

---

## 💡 Valor del Proyecto

Este sistema no solo valida datos, sino que:

- 🧠 **Aprende** del comportamiento histórico
- 📈 **Mejora** con el tiempo
- 🤖 **Simula** inteligencia adaptativa
- 🛡️ **Protege** la integridad de la BD
- 📊 **Registra** todo para auditoría

---

## 📊 Estructura de Tablas SQL

Ver `db_schema.sql` para detalles completos.

**Tablas clave:**

```sql
-- Alertas inmunológicas
CREATE TABLE alertas_inmunitarias (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    tabla_afectada VARCHAR(100),
    tipo VARCHAR(100),
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    severidad ENUM('BAJA', 'MEDIA', 'ALTA')
);

-- Memoria inmunológica
CREATE TABLE memoria_inmunologica (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_anomalia VARCHAR(255) UNIQUE,
    frecuencia INT DEFAULT 1,
    ultima_ocurrencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔗 Endpoints API

### 📥 Inserción con Análisis

- **POST** `/api/insertar` - Inserta registro tras análisis inmunológico

### 📤 Obtención de Datos

- **GET** `/api/datos/<tabla>` - Obtiene registros de una tabla
- **GET** `/api/tabla/<tabla>` - Vista completa de tabla con acciones
- **GET** `/api/alertas` - Obtiene alertas inmunológicas
- **GET** `/api/memoria` - Obtiene memoria inmunológica
- **GET** `/api/formulario/<tabla>` - Genera formulario dinámico

### ✏️ CRUD Genérico

- **GET** `/api/get/<tabla>/<pk>` - Obtiene registro para editar
- **POST** `/api/update` - Actualiza registro
- **DELETE** `/api/delete/<tabla>/<pk>` - Elimina registro

---

## 📝 Notas Importantes

- Todos los valores numéricos soportan formato con comas (ej: "1.234,56" o "1,234.56")
- No se aplican reglas basadas en IDs o Fechas (evita falsos positivos)
- Las FKs se validan antes de cada INSERT
- Los mensajes de error son claros y específicos

---

## 👨‍💼 Autor

Proyecto desarrollado como Sistema de Inteligencia Artificial Inmunológica para ERP.

**Fecha:** Abril 2026

---

## 📞 Soporte

Para errores o sugerencias, verifica:
1. Conexión a MySQL
2. Permisos en tablas
3. Valores de entrada válidos
4. Alertas en dashboard

---

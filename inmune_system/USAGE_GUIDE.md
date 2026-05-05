# 📖 Guía de Uso del Sistema

## Sistema Inteligente de Monitoreo de Base de Datos

---

## 🏠 Dashboard Principal

Al abrir la aplicación, verás:

```
┌─────────────────────────────────────────┐
│  PANEL LATERAL     │     AREA PRINCIPAL  │
│  (Hamburguesa)     │                     │
│  • Tablas          │  [Título]           │
│  • Alertas         │  [Contenido]        │
│  • Memoria         │  [Mensaje resultado]│
│                    │                     │
└─────────────────────────────────────────┘
```

---

## 📋 Operaciones Disponibles

### 1️⃣ VER DATOS DE UNA TABLA

**Pasos:**

1. Haz clic en el menú hamburguesa (☰) arriba a la izquierda
2. En "Tablas" haz clic en el botón **"Ver"**
3. Se mostrará una tabla con todos los registros

**Datos visibles:**
- Para tabla "venta": IdVenta, IdCliente, IdProducto, IdCanal, Cantidad, Precio, Fecha
- Acciones: Editar, Eliminar

---

### 2️⃣ INSERTAR UN NUEVO REGISTRO

**Pasos:**

1. Abre el menú hamburguesa (☰)
2. Haz clic en **"Insertar"** en la tabla deseada
3. Se abrirá un formulario dinámico
4. **Completa los campos:**
   - Campos con prefijo `Id` aparecen como **SELECT** (desplegables)
   - Campos normales son **TEXT INPUT**
   - Campos con "Fecha" son **DATE PICKER**
5. Haz clic en **"Guardar"**

**Ejemplo: Insertar una Venta**

```
IdCliente: [Seleccionar ▼]  → Elige "Juan García López"
IdProducto: [Seleccionar ▼] → Elige "Producto A"
IdCanal: [Seleccionar ▼]    → Elige "E-commerce"
Cantidad: [    5        ]   → Número
Precio: [   25.50      ]    → Decimal (acepta "25,50" o "25.50")
```

**Resultado:**

- ✅ **VERDE**: Registro guardado exitosamente
- ❌ **ROJO**: Anomalía detectada, operación bloqueada

---

### 3️⃣ EDITAR UN REGISTRO EXISTENTE

**Pasos:**

1. Ve la tabla (paso "Ver Datos")
2. En la fila deseada, haz clic en **"Editar"**
3. Se abrirá el formulario prellenado
4. Modifica los campos que desees
5. Haz clic en **"Actualizar"**

**Nota:** El ID (PK) no es editable.

---

### 4️⃣ ELIMINAR UN REGISTRO

**Pasos:**

1. Ve la tabla (paso "Ver Datos")
2. En la fila deseada, haz clic en **"Eliminar"**
3. Se borrará inmediatamente

**Advertencia:** Esta acción no se puede deshacer.

---

## 🚨 ALERTAS INMUNOLÓGICAS

### ¿Qué son?

Cuando detectan anomalías, el sistema:
1. ❌ Bloquea la operación
2. 🔔 Registra una alerta
3. 📊 Actualiza la memoria

### Ver Alertas

1. Abre el menú hamburguesa (☰)
2. Haz clic en **"Alertas"**
3. Verás una tabla con:
   - **ID**: Número de alerta
   - **Tabla**: Tabla afectada
   - **Tipo**: Tipo de anomalía
   - **Descripción**: Detalle
   - **Fecha**: Cuándo ocurrió
   - **Severidad**: BAJA, MEDIA o ALTA (color rojo)

---

## 🧠 MEMORIA INMUNOLÓGICA

### ¿Qué es?

Registro histórico de anomalías aprendidas por el sistema, con frecuencia de ocurrencia.

### Ver Memoria

1. Abre el menú hamburguesa (☰)
2. Haz clic en **"Memoria"**
3. Verás anomalías ordenadas por frecuencia

---

## 📊 EJEMPLOS DE ANOMALÍAS

### ❌ VENTA - Se bloquea si:

| Condición | Mensaje |
|-----------|---------|
| Cantidad = 0 o negativa | "Cantidad inválida o cero" |
| Precio = 0 o negativo | "Precio inválido o cero" |
| Precio > 3x promedio | "Precio de venta muy por encima del promedio" |
| Cantidad > 3x promedio | "Cantidad de venta anómala" |

### ❌ COMPRA - Se bloquea si:

| Condición | Mensaje |
|-----------|---------|
| Cantidad inválida | "Compra con cantidad inválida" |
| Monto negativo | "Monto de compra negativo" |

### ❌ GASTO - Se bloquea si:

| Condición | Mensaje |
|-----------|---------|
| Monto > 2x promedio | "Gasto excesivo detectado" |
| Monto negativo | "Monto de gasto negativo" |

### ❌ CLIENTE - Se bloquea si:

| Condición | Mensaje |
|-----------|---------|
| Nombre < 5 caracteres | "Nombre de cliente sospechoso" |

---

## 💡 FORMATOS ACEPTADOS

### Números Decimales

Todos estos formatos son válidos:

```
✅ 25.50    (punto decimal)
✅ 25,50    (coma decimal)
✅ 1234.56  (con decimales)
✅ 1,234.56 (miles + decimal)
✅ 1.234,56 (formato europeo)
```

### Fechas

Formato calendario interactivo (date picker):

```
Selecciona un día del calendario
Formato interno: YYYY-MM-DD
```

---

## 🔄 FLUJO COMPLETO DE INSERCION

```
┌─────────────────────────────────────┐
│ 1. Usuario abre Dashboard           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Selecciona tabla (venta/compra)  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Presiona "Insertar"              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Se abre Formulario Dinámico      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. Usuario completa datos           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 6. Presiona "Guardar"               │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────┴──────┐
        │             │
        ▼             ▼
   ✅ VÁLIDO     ❌ ANOMALÍA
        │             │
        ▼             ▼
   • Inserta      • Bloquea
   • Verde        • Rojo
   • Registro     • Alerta
     visible      • Memoria
```

---

## 🎮 INTERFAZ DE USUARIO

### Botones en la barra superior

| Botón | Función |
|-------|---------|
| ☰ (Hamburguesa) | Abre/cierra menú lateral |
| [Nombre de sección] | Indica sección actual |

### Menú Lateral (Hamburguesa)

```
TABLAS
├─ Ver [tabla]
├─ Insertar [tabla]

ALERTAS
├─ Mostrar alertas

MEMORIA
├─ Mostrar historial
```

### Área Principal

- Muestra formulario o tabla según selección
- Mensaje de resultado en área gris
- Botones de acción (Guardar, Actualizar, Eliminar)

---

## ⌨️ ATAJOS Y TIPS

### Tips Útiles

1. **Selecciona valores de FK desde dropdowns:**
   - Campos `IdCliente`, `IdProducto`, `IdCanal` cargan automáticamente
   - Evita errores de referencias

2. **Formatos numéricos flexibles:**
   - Escribe "1.234,56" o "1234.56"
   - Sistema convierte automáticamente

3. **Revisa alertas regularmente:**
   - Entiende qué está siendo bloqueado
   - Ajusta tu entrada de datos

4. **Usa memoria para aprender patrones:**
   - "Precio de venta muy por encima del promedio" → Tu precio es 3x más alto
   - Revisa si es intencional

---

## 🔍 VISUALIZACIÓN DE DATOS

### Tabla de Datos

Cada fila muestra:
- ✅ Todos los campos de la tabla
- 🔘 Checkbox (si aplica)
- Botones de acción

### Antes de insertar

Ejemplo: Insertar Venta

```
Tabla: venta
Campos disponibles:
├─ IdVenta (oculto - autogenerado)
├─ IdCliente (SELECT)
├─ IdProducto (SELECT)
├─ IdCanal (SELECT)
├─ Cantidad (TEXTO)
├─ Precio (TEXTO)
└─ Fecha (DATE)
```

---

## 📞 PREGUNTAS COMUNES

### P: "¿Por qué se bloquea mi inserción?"

**R:** Probablemente tu dato coincide con una regla de detección. Revisa el mensaje:
- Si dice "Precio... muy por encima" → Tu precio es muy alto
- Si dice "Cantidad inválida" → Ingresaste 0 o negativo
- Si dice "no existe" → El cliente/producto no existe en BD

### P: "¿Cómo veo el historial de cambios?"

**R:** 
- Alertas: Menú (☰) → "Alertas"
- Memoria: Menú (☰) → "Memoria"

### P: "¿Se puede deshacer una eliminación?"

**R:** No. Antes de eliminar, asegúrate de que sea lo que quieres.

### P: "¿Qué significa 'severidad ALTA'?"

**R:** Anomalía importante (ej: precio 5x superior). Requiere revisión.

---

## 🎓 EJERCICIOS

### Ejercicio 1: Insertar Venta Válida

1. Ve a Dashboard
2. Selecciona "venta"
3. Haz clic en "Insertar"
4. Completa con:
   - Cliente: Cualquiera
   - Producto: Cualquiera
   - Canal: E-commerce
   - Cantidad: 3
   - Precio: 50
5. Guarda
6. **Resultado esperado:** Verde ✅

### Ejercicio 2: Provocar Anomalía

1. Intenta insertar cantidad "-5"
2. **Resultado:** Rojo ❌ "Cantidad inválida"
3. Ve a Alertas, verás registrada

### Ejercicio 3: Ver Memoria

1. Inserta 3 ventas con cantidad excesiva (1000 unidades)
2. Cada una generará anomalía
3. Ve a Memoria
4. Verás "Cantidad de venta anómala" con frecuencia = 3

---

**¡Ahora sabes cómo usar el Sistema Inmunológico! 🧬**

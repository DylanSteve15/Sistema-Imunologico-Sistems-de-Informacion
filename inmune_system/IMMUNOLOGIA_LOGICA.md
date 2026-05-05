# 🧬 LÓGICA DEL SISTEMA INMUNOLÓGICO - Documentación Detallada

## Índice
1. [Conceptos Fundamentales](#conceptos-fundamentales)
2. [Arquitectura General](#arquitectura-general)
3. [Funcionamiento Paso a Paso](#funcionamiento-paso-a-paso)
4. [Reglas de Detección](#reglas-de-detección)
5. [Severidad de Anomalías](#severidad-de-anomalías)
6. [Memoria Inmunológica](#memoria-inmunológica)
7. [Flujo de Datos](#flujo-de-datos)

---

## Conceptos Fundamentales

El sistema es una analogía del **sistema inmunológico biológico humano** aplicada a la protección de bases de datos:

### 🔬 Mapeo Biológico → Digital

| Concepto Biológico | Implementación Digital | Descripción |
|-------------------|----------------------|------------|
| **Antígeno** | Dato ingresado por el usuario | Elemento potencialmente peligroso que entra al sistema |
| **Self** | Patrones normales de la BD | Datos conocidos y seguros (promedios históricos) |
| **Non-self** | Datos anómalos | Elementos que no coinciden con los patrones normales |
| **Anticuerpo** | Regla de detección | Mecanismo que identifica y detiene non-self |
| **Fagocito** | Proceso de bloqueo | Elimina/bloquea la operación anómala |
| **Memoria Inmune** | Tabla `memoria_inmunologica` | Registro histórico de ataques/anomalías |

---

## Arquitectura General

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/JS)                   │
│              Formulario dinámico del usuario             │
└────────────────────┬────────────────────────────────────┘
                     │ (Datos del usuario)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  app.py (Flask)                         │
│              Controlador Principal                       │
│  - Recibe datos del formulario                          │
│  - Delega análisis inmunológico                         │
│  - Gestiona respuestas al usuario                       │
└────────────────────┬────────────────────────────────────┘
                     │ (Datos + Tabla)
                     ▼
┌─────────────────────────────────────────────────────────┐
│         inmunologico.py                                  │
│    ORQUESTADOR DEL SISTEMA INMUNE                       │
│  - Función: analizar_y_guardar(tabla, datos)           │
│  - Coordina detectores                                 │
│  - Gestiona alertas                                    │
└────────┬──────────────────────────────────┬────────────┘
         │                                   │
         ▼                                   ▼
┌────────────────────────┐       ┌──────────────────────────┐
│   detectores.py        │       │   memoria.py             │
│ REGLAS DE DETECCIÓN    │       │ PERSISTENCIA DE ALERTAS  │
│                        │       │                          │
│ - detectar_anomalias() │       │ - guardar_alerta()      │
│   * venta              │       │ - registrar_memoria()   │
│   * compra             │       │                          │
│   * gasto              │       │ Guarda en:              │
│   * cliente            │       │ - alertas_inmunitarias  │
│   * producto           │       │ - memoria_inmunologica  │
│   * proveedor          │       │                          │
│   * canal_venta        │       │                          │
└────────┬───────────────┘       └──────────────┬───────────┘
         │                                      │
         └──────────────┬───────────────────────┘
                        ▼
            ┌──────────────────────────┐
            │    MySQL Database        │
            │                          │
            │ Tablas ERP:              │
            │ - venta, compra, etc.    │
            │                          │
            │ Tablas Inmunes:          │
            │ - alertas_inmunitarias   │
            │ - memoria_inmunologica   │
            │ - patrones_normales      │
            └──────────────────────────┘
```

---

## Funcionamiento Paso a Paso

### 1️⃣ El Usuario Ingresa Datos

```html
Usuario abre el dashboard y selecciona tabla "Venta"
↓
Sistema genera formulario con campos dinámicos
↓
Usuario completa: Precio=500, Cantidad=10
↓
Usuario hace clic en "Guardar y Analizar"
```

### 2️⃣ Frontend Envía los Datos

```javascript
// En index.html - función guardarDatos()
fetch("/api/insertar", {
    method: "POST",
    body: FormData(tabla, Precio, Cantidad, ...)
})
```

### 3️⃣ Backend Recibe en app.py

```python
@app.route('/api/insertar', methods=['POST'])
def insertar():
    tabla = request.form.get('tabla')
    
    # Extrae todos los datos del formulario
    datos = {
        'Precio': request.form.get('Precio'),
        'Cantidad': request.form.get('Cantidad'),
        ...
    }
    
    # PASO CRÍTICO: Analiza con sistema inmunológico
    permitido, anomalias = analizar_y_guardar(tabla, datos)
    
    if permitido:
        # ✅ Si está bien, inserta en BD
        db.insertar(tabla, datos)
        return {'tipo': 'success', 'mensaje': '✅ Datos guardados exitosamente'}
    else:
        # ❌ Si hay anomalía, bloquea
        return {'tipo': 'warning', 'mensaje': '⚠️  Operación bloqueada', 
                'anomalias': anomalias}
```

### 4️⃣ Sistema Inmunológico Analiza

```python
# En inmunologico.py - función analizar_y_guardar()
def analizar_y_guardar(tabla, datos):
    
    # 1. Llama a detectores específicos
    anomalias = detectar_anomalias(tabla, datos)
    
    if anomalias:  # ⚠️ Se encontraron problemas
        
        # 2. Para cada anomalía detectada:
        for a in anomalias:
            
            # Asigna severidad (BAJA, MEDIA, ALTA)
            sev = asignar_severidad(a)
            
            # 3. Guarda en tabla de alertas
            guardar_alerta(tabla, a, severidad=sev)
            
            # 4. Registra en memoria inmunológica
            registrar_memoria(a)
        
        # 5. RETORNA: (False, lista_anomalias)
        return False, anomalias
    
    else:  # ✅ Todo bien
        return True, []
```

### 5️⃣ Frontend Muestra Resultado

```javascript
// Si está bien (tipo='success')
✅ Mensaje verde: "Datos guardados exitosamente"
↓
Recarga tabla automáticamente

// Si hay anomalía (tipo='warning')
⚠️  Mensaje amarillo: "Operación bloqueada"
↓
Muestra lista de problemas detectados
↓
Usuario debe corregir y reintentar
```

---

## Reglas de Detección

Las reglas están en **`detectores.py`** - función `detectar_anomalias(tabla, datos)`

### 📊 Tabla: VENTA

```python
if tabla == "venta":
    precio = parse_float(datos.get("Precio", 0))
    cantidad = parse_int(datos.get("Cantidad", 0))
    
    # REGLA 1: Precio inválido
    if precio <= 0:
        anomalias.append("Precio inválido o cero")
    
    # REGLA 2: Precio excesivo
    elif prom[0] and precio > prom[0] * 3:
        # Si el precio es 3x el promedio histórico → anomalía
        anomalias.append("Precio de venta muy por encima del promedio")
    
    # REGLA 3: Cantidad inválida
    if cantidad <= 0:
        anomalias.append("Cantidad inválida o cero")
    
    # REGLA 4: Cantidad anómala
    elif prom[1] and cantidad > prom[1] * 3:
        # Si la cantidad es 3x el promedio → anomalía
        anomalias.append("Cantidad de venta anómala")
```

**Ejemplo práctico:**
- Promedio histórico de precio: $100
- Usuario intenta ingresar: $350
- Sistema detecta: "Precio muy por encima del promedio" ❌
- Operación bloqueada

### 📦 Tabla: COMPRA

```python
elif tabla == "compra":
    cantidad = int(datos.get("Cantidad", 0) or 0)
    monto = float(datos.get("Monto", 0) or 0)
    
    # REGLA 1: Cantidad inválida
    if cantidad <= 0:
        anomalias.append("Compra con cantidad inválida")
    
    # REGLA 2: Monto negativo
    if monto < 0:
        anomalias.append("Monto de compra negativo")
```

### 💰 Tabla: GASTO

```python
elif tabla == "gasto":
    # Calcula promedio histórico
    cursor.execute("SELECT AVG(Monto) FROM gasto")
    prom = cursor.fetchone()[0]
    
    monto = float(datos.get("Monto", 0) or 0)
    
    # REGLA 1: Gasto excesivo (2x promedio)
    if prom and monto > prom * 2:
        anomalias.append("Gasto excesivo detectado")
    
    # REGLA 2: Monto negativo
    if monto < 0:
        anomalias.append("Monto de gasto negativo")
```

**Ejemplo:**
- Promedio de gastos: $50
- Usuario intenta: $120
- Sistema detecta: "Gasto excesivo detectado" ✋

### 👤 Tabla: CLIENTE

```python
elif tabla == "cliente":
    nombre = datos.get("Nombre_y_Apellido", "")
    
    # REGLA 1: Nombre sospechoso
    if len(nombre) < 5:
        anomalias.append("Nombre de cliente sospechoso")
```

### 🌐 Reglas Generales

```python
for k, v in datos.items():
    if isinstance(v, str) and len(v) > 255:
        anomalias.append(f"Campo {k} demasiado largo")
```

Válida que ningún campo de texto sea absurdamente largo.

---

## Severidad de Anomalías

Cada anomalía detectada tiene un **nivel de severidad**:

### 🟢 BAJA
- Texto largo
- Validaciones menores

### 🟡 MEDIA (Default)
- Cantidad o precio 2x promedio
- Montos negativos

### 🔴 ALTA
- Precio 3x+ el promedio
- Cantidades excesivas (2x+)
- Compra/Gasto por debajo del costo

```python
# En inmunologico.py
sev = 'MEDIA'  # Default
low = a.lower()
if 'muy' in low or '2x' in low or 'por debajo' in low:
    sev = 'ALTA'  # Si contiene palabras clave → ALTA
```

---

## Memoria Inmunológica

### 📋 Tabla: `alertas_inmunitarias`

Almacena cada anomalía detectada:

| Campo | Descripción |
|-------|-------------|
| `id` | ID único |
| `tabla` | Tabla donde ocurrió |
| `descripcion` | Mensaje de la anomalía |
| `severidad` | BAJA, MEDIA o ALTA |
| `fecha` | Cuándo fue detectada |

```sql
INSERT INTO alertas_inmunitarias (tabla, descripcion, severidad) 
VALUES ('venta', 'Precio muy por encima del promedio', 'ALTA');
```

### 🧠 Tabla: `memoria_inmunologica`

Registro histórico más general:

| Campo | Descripción |
|-------|-------------|
| `id` | ID único |
| `evento` | Descripción del evento |
| `fecha` | Cuándo ocurrió |
| `contador` | Cuántas veces se repitió (ON DUPLICATE KEY) |

```sql
-- Primera vez
INSERT INTO memoria_inmunologica (evento) 
VALUES ('Precio muy por encima del promedio')
ON DUPLICATE KEY UPDATE contador = contador + 1;
```

Si la misma anomalía se repite, **incrementa el contador** en lugar de crear duplicados.

---

## Flujo de Datos Completo

```plaintext
┌─────────────────────────────────────────────────────────┐
│ 1. USUARIO INGRESA DATOS EN FORMULARIO                   │
│    Selecciona: venta                                    │
│    Ingresa: Precio=500, Cantidad=10, IdProducto=1      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. FRONTEND ENVÍA VÍA FETCH/POST                         │
│    /api/insertar                                        │
│    FormData: {tabla: 'venta', Precio: 500, ...}         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. app.py RECIBE Y EXTRAE DATOS                         │
│    tabla = 'venta'                                      │
│    datos = {Precio: 500, Cantidad: 10, ...}             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. app.py LLAMA analizar_y_guardar(tabla, datos)        │
│    ▼ SISTEMA INMUNOLÓGICO ACTIVADO ▼                   │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────────┐  ┌──────────────────────┐
│ detectores.py        │  │ memory.py            │
│ detectar_anomalias() │  │ guardar_alerta()     │
│                      │  │ registrar_memoria()  │
│ REGLA 1: Precio      │  │                      │
│ REGLA 2: Cantidad    │  │ INSERT INTO          │
│          ...         │  │ alertas_inmunitarias │
└────────┬─────────────┘  └──────────┬───────────┘
         │                           │
         └────────────┬──────────────┘
                      ▼
        ┿━━━ ¿ANOMALÍA DETECTADA? ━━━┿
       ╱                             ╲
      ✅                               ❌
    NO                                SÍ
     │                                 │
     ▼                                 ▼
┌─────────────────────┐         ┌──────────────────┐
│ Insertar en BD      │         │ BLOQUEAR          │
│ INSERT INTO venta   │         │ Guardar alerta    │
│ (Precio, Cantidad)  │         │ Retornar anomalía │
│                     │         │                  │
│ Retorna:            │         │ Retorna:          │
│ {tipo: success}     │         │ {tipo: warning}   │
└────────┬────────────┘         └────────┬─────────┘
         │                               │
         └───────────────┬───────────────┘
                         ▼
         ┌───────────────────────────────┐
         │ 5. FRONTEND RECIBE RESPUESTA   │
         │    Si success:                 │
         │    - Muestra ✅                 │
         │    - Recarga tabla             │
         │    - Resalta nueva fila        │
         │                                │
         │    Si warning:                 │
         │    - Muestra ⚠️ en rojo        │
         │    - Lista anomalías           │
         │    - No inserta nada           │
         └───────────────────────────────┘
```

---

## Ejemplo Práctico Completo

### Escenario: Usuario intenta ingresar venta con precio excesivo

**DATOS HISTÓRICOS EN BD:**
```
Promedio de Precio en ventas: $100
Promedio de Cantidad: 5 unidades
```

**USUARIO INTENTA INSERTAR:**
```
Tabla: venta
Precio: $350
Cantidad: 3
IdProducto: 1
```

**PROCESO INMUNOLÓGICO:**

```python
# 1. detectar_anomalias('venta', datos)
precio = 350
prom_precio = 100

# 2. Aplica REGLA 2
if precio > prom_precio * 3:  # 350 > 300?
    # ¡SÍ! Cumple la condición
    anomalias.append("Precio de venta muy por encima del promedio")
    
# 3. analizar_y_guardar() recibe anomalia
for a in anomalias:
    if '2x' in a or 'muy' in a:
        sev = 'ALTA'  # Marca como ALTA
    
    guardar_alerta('venta', a, 'ALTA')  # Guarda en BD
    registrar_memoria(a)  # Registra en memoria

# 4. Retorna
return False, ["Precio de venta muy por encima del promedio"]
```

**RESPUESTA AL USUARIO:**

```
⚠️  OPERACIÓN BLOQUEADA
Anomalías detectadas:
- Precio de venta muy por encima del promedio

Por favor, revisa los datos e intenta nuevamente.
```

✅ **El sistema PROTEGIÓ la integridad de datos** impidiendo un valor anómalo.

---

## Mejoras Futuras Sugeridas

1. **Machine Learning**: Usar históricos para ajustar límites automáticamente
2. **Excepciones**: Permitir usuarios con permisos especiales a ignorar alertas
3. **Patrones Complejos**: Detectar anomalías combinadas (multi-campo)
4. **Quarantine**: Guardar registros sospechosos en tabla separada para revisión
5. **Alertas en Tiempo Real**: Enviar notificaciones por email de anomalías ALTA
6. **Dashboard de Inmunidad**: Visualizar salud del sistema

---

## Preguntas Frecuentes

**P: ¿Qué pasa si ingreso datos válidos pero el sistema los bloquea?**  
R: Verifica los umbrales de promedio. Si es legítimo, el admin puede revisar en la tabla `alertas_inmunitarias` y ajustar reglas.

**P: ¿Cómo sé qué reglas se aplicaron a cada tabla?**  
R: Mira la tabla `alertas_inmunitarias` con `SELECT * FROM alertas_inmunitarias WHERE tabla = 'tu_tabla'`

**P: ¿Puedo deshabilitar el sistema inmunológico?**  
R: Sí, eliminando la línea `permitido, anomalias = analizar_y_guardar(tabla, datos)` en `app.py`, pero ¡no se recomienda!

---

*Última actualización: 13 de Abril de 2026*

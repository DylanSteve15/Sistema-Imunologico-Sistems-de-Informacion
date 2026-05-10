import logging
from datetime import datetime
from detectores import detectar_anomalias
from ml_detector import detector_ml
from memoria import (
    guardar_alerta,
    registrar_memoria,
    es_excepcion,
    sugerir_severidad_por_memoria
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

UMBRAL_BLOQUEO = 70

PESOS_SEVERIDAD = {
    "BAJA": 15,
    "MEDIA": 35,
    "ALTA": 60,
    "CRITICA": 90
}

KEYWORDS_CRITICA = ["fraude", "inyeccion", "sql injection", "corrupcion", "tampering"]
KEYWORDS_ALTA = ["muy", "excede", "excesivo", "anomalia", "negativo", "2x", "3x", "invalido"]
KEYWORDS_MEDIA = ["fuera de rango", "sospechoso", "atipico", "inconsistente"]


def analizar_y_guardar(tabla, datos):
    resultado = {
        "tabla": tabla,
        "timestamp": datetime.now().isoformat(),
        "permitido": True,
        "riesgo_total": 0,
        "hallazgos": [],
        "detalle_capas": {
            "determinista": [],
            "ml": None
        }
    }

    try:
        hallazgos_reglas = detectar_anomalias(tabla, datos) or []

        for h in hallazgos_reglas:
            if es_excepcion(tabla, h):
                logging.info(f"Excepción conocida ignorada en {tabla}: {h}")
                continue

            sev = _determinar_severidad(h)
            sev = sugerir_severidad_por_memoria(tabla, h, sev)

            hallazgo = {
                "descripcion": h,
                "severidad": sev,
                "peso": PESOS_SEVERIDAD[sev],
                "origen": "REGLAS"
            }

            resultado["detalle_capas"]["determinista"].append(hallazgo)
            resultado["hallazgos"].append(hallazgo)

    except Exception as e:
        logging.error(f"Error en capa determinista para {tabla}: {e}")
        resultado["hallazgos"].append({
            "descripcion": f"Fallo interno en capa determinista: {str(e)}",
            "severidad": "MEDIA",
            "peso": 20,
            "origen": "SISTEMA"
        })

    try:
        pred = detector_ml.predecir(tabla, datos)

        if isinstance(pred, dict):
            es_anomalia = pred.get("es_anomalia", False)
            score = float(pred.get("score_confianza", 0))
        else:
            es_anomalia = False
            score = 0

        resultado["detalle_capas"]["ml"] = {
            "activo": True,
            "es_anomalia": es_anomalia,
            "score_confianza": score
        }

        if es_anomalia:
            desc_ml = f"Anomalía detectada por modelo ML (confianza: {score:.2f}%)"

            if not es_excepcion(tabla, desc_ml):
                sev_ml = _severidad_por_score_ml(score)
                sev_ml = sugerir_severidad_por_memoria(tabla, desc_ml, sev_ml)
                peso_ml = _peso_ml(score)

                resultado["hallazgos"].append({
                    "descripcion": desc_ml,
                    "severidad": sev_ml,
                    "peso": max(peso_ml, PESOS_SEVERIDAD[sev_ml]),
                    "origen": "ML"
                })
            else:
                logging.info(f"Predicción ML ignorada por excepción aprendida: {desc_ml}")

    except Exception as e:
        logging.warning(f"Capa ML no disponible para {tabla}: {e}")
        resultado["detalle_capas"]["ml"] = {
            "activo": False,
            "es_anomalia": False,
            "score_confianza": 0,
            "error": str(e)
        }

    resultado["riesgo_total"] = _calcular_riesgo_total(resultado["hallazgos"])
    resultado["permitido"] = resultado["riesgo_total"] < _umbral_por_tabla(tabla)

    if resultado["hallazgos"]:
        _procesar_anomalias(tabla, datos, resultado)

    if resultado["permitido"]:
        logging.info(f"Operación permitida en {tabla}. Riesgo={resultado['riesgo_total']}")
        return True, []

    mensajes = [
        f"[{h['origen']}] {h['descripcion']} (Severidad: {h['severidad']})"
        for h in resultado["hallazgos"]
    ]

    logging.warning(
        f"Operación bloqueada en {tabla}. Riesgo={resultado['riesgo_total']}. "
        f"Hallazgos={len(resultado['hallazgos'])}"
    )

    return False, mensajes


def _procesar_anomalias(tabla, datos, resultado):
    for hallazgo in resultado["hallazgos"]:
        ok_alerta = guardar_alerta(
            tabla=tabla,
            descripcion=hallazgo["descripcion"],
            severidad=hallazgo["severidad"]
        )

        ok_memoria = registrar_memoria(
            tabla=tabla,
            tipo_anomalia=hallazgo["descripcion"],
            severidad=hallazgo["severidad"]
        )

        if not ok_alerta:
            logging.error(f"No se pudo guardar alerta: {hallazgo}")

        if not ok_memoria:
            logging.error(f"No se pudo registrar memoria: {hallazgo}")

    logging.warning(
        f"Auditoría | tabla={tabla} | riesgo={resultado['riesgo_total']} | "
        f"datos={datos} | hallazgos={resultado['hallazgos']}"
    )


def _determinar_severidad(desc):
    desc_low = desc.lower()

    if any(k in desc_low for k in KEYWORDS_CRITICA):
        return "CRITICA"
    if any(k in desc_low for k in KEYWORDS_ALTA):
        return "ALTA"
    if any(k in desc_low for k in KEYWORDS_MEDIA):
        return "MEDIA"
    return "BAJA"


def _severidad_por_score_ml(score):
    if score >= 90:
        return "CRITICA"
    if score >= 75:
        return "ALTA"
    if score >= 50:
        return "MEDIA"
    return "BAJA"


def _peso_ml(score):
    if score >= 90:
        return 85
    if score >= 75:
        return 65
    if score >= 50:
        return 40
    return 20


def _calcular_riesgo_total(hallazgos):
    if not hallazgos:
        return 0

    total = sum(h["peso"] for h in hallazgos)

    origenes = {h["origen"] for h in hallazgos}
    if "REGLAS" in origenes and "ML" in origenes:
        total += 15

    return min(total, 100)


def _umbral_por_tabla(tabla):
    umbrales = {
        "venta": 60,
        "compra": 65,
        "gasto": 55,
        "producto": 70,
        "cliente": 75
    }
    return umbrales.get(tabla, UMBRAL_BLOQUEO)
from detectores import detectar_anomalias
from memoria import guardar_alerta, registrar_memoria


def analizar_y_guardar(tabla, datos):
    """Analiza `datos` para `tabla` usando detectores.
    Retorna (permitido: bool, anomalias: list).
    Si hay anomalías las guarda en `alertas_inmunitarias` y en memoria.
    """

    anomalias = detectar_anomalias(tabla, datos)

    if anomalias:
        for a in anomalias:
            # asignar severidad según keywords
            sev = 'MEDIA'
            low = a.lower()
            if 'muy' in low or '2x' in low or 'por encima' in low or 'excesivo' in low or 'por debajo del costo' in low:
                sev = 'ALTA'
            guardar_alerta(tabla, a, severidad=sev)
            registrar_memoria(a)

        print("Sistema inmune activado:", anomalias)
        return False, anomalias

    print("Operación segura (self detectado)")
    return True, []
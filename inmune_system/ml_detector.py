import os
import numpy as np
import pandas as pd
import joblib
import logging

from sklearn.ensemble import IsolationForest
from db import conectar

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DetectorML:
    def __init__(self):
        self.modelos = {}
        self.carpeta_modelos = "modelos_ml"
        os.makedirs(self.carpeta_modelos, exist_ok=True)

    def _ruta_modelo(self, tabla):
        return os.path.join(self.carpeta_modelos, f"{tabla}_modelo.pkl")

    def _ruta_metadata(self, tabla):
        return os.path.join(self.carpeta_modelos, f"{tabla}_metadata.pkl")

    def _obtener_features_validas(self, df):
        columnas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()

        excluidas = {
            "id", "Id", "IdVenta", "IdCompra", "IdProducto", "IdCliente",
            "IdProveedor", "IdEmpleado", "IdSucursal", "IdCanal",
            "IdTipoProducto", "IdTipoGasto", "IdLocalidad", "IdProvincia"
        }

        features = [c for c in columnas_numericas if c not in excluidas]
        return features

    def entrenar(self, tabla):
        conn = conectar()
        if not conn:
            return f"No se pudo conectar a la base de datos para entrenar {tabla}"

        try:
            df = pd.read_sql(f"SELECT * FROM `{tabla}`", conn)

            if df.empty:
                return f"No hay datos en {tabla} para entrenar"

            features = self._obtener_features_validas(df)

            if len(features) < 1:
                return f"No hay suficientes columnas numéricas útiles en {tabla}"

            if len(df) < 20:
                return f"No hay suficientes registros en {tabla} para entrenar un modelo confiable"

            X = df[features].copy().fillna(0)

            modelo = IsolationForest(
                contamination=0.05,
                random_state=42,
                n_estimators=150
            )
            modelo.fit(X)

            metadata = {
                "tabla": tabla,
                "features": features,
                "n_registros": len(df)
            }

            joblib.dump(modelo, self._ruta_modelo(tabla))
            joblib.dump(metadata, self._ruta_metadata(tabla))

            self.modelos[tabla] = {
                "modelo": modelo,
                "metadata": metadata
            }

            logging.info(f"Modelo entrenado para {tabla} con features: {features}")
            return f"✅ Modelo entrenado: {tabla} | features={features} | registros={len(df)}"

        except Exception as e:
            logging.error(f"Error al entrenar {tabla}: {e}")
            return f"Error: {str(e)}"

        finally:
            conn.close()

    def predecir(self, tabla, datos):
        try:
            ruta_modelo = self._ruta_modelo(tabla)
            ruta_metadata = self._ruta_metadata(tabla)

            if not os.path.exists(ruta_modelo) or not os.path.exists(ruta_metadata):
                return {
                    "es_anomalia": False,
                    "score_confianza": 0,
                    "error": "Entrena el modelo primero"
                }

            modelo = joblib.load(ruta_modelo)
            metadata = joblib.load(ruta_metadata)

            features = metadata.get("features", [])
            if not features:
                return {
                    "es_anomalia": False,
                    "score_confianza": 0,
                    "error": "Modelo sin features válidas"
                }

            input_data = {}
            for f in features:
                val = datos.get(f, 0)
                try:
                    input_data[f] = float(val)
                except:
                    input_data[f] = 0.0

            df_nuevo = pd.DataFrame([input_data], columns=features)

            prediccion = modelo.predict(df_nuevo)[0]
            score = float(modelo.decision_function(df_nuevo)[0])

            confianza = round(min(abs(score) * 100, 100), 2)
            es_anomalia = prediccion == -1 and confianza >= 55

            return {
                "es_anomalia": es_anomalia,
                "score_confianza": confianza,
                "score_crudo": score,
                "features_usadas": features
            }

        except Exception as e:
            logging.error(f"Error en predicción para {tabla}: {e}")
            return {
                "es_anomalia": False,
                "score_confianza": 0,
                "error": str(e)
            }


detector_ml = DetectorML()
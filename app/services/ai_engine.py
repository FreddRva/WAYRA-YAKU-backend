import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import os
import joblib
import traceback

MODEL_PATH = "isolation_forest.joblib"

class TelemetryAIModel:
    def __init__(self):
        self.history = []
        self.window_size = 30
        self.is_trained = False
        self.startup_ticks = 0
        self.model = None
        self.features = [
            "temperatura", "humedad", "tds", "aguaAnalogico",
            "ph", "suelo", "turbidez", "caudal",
            "presion", "aire", "sedimento", "temp_liquido"
        ]
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.is_trained = True
            except Exception:
                pass

    def train(self, data_path: str):
        if not os.path.exists(data_path):
            return {"status": "error", "message": "No dataset"}
        try:
            df = pd.read_csv(data_path)
            for f in self.features:
                if f not in df.columns:
                    df[f] = 0.0
            X = df[self.features].fillna(0.0).values
            self.model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
            self.model.fit(X)
            joblib.dump(self.model, MODEL_PATH)
            self.is_trained = True
            return {"status": "success", "message": "Modelo entrenado"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def predict_anomaly(self, current_data: dict):
        self.startup_ticks += 1
        values = [current_data.get(f, 0.0) for f in self.features]
        self.history.append(values)
        if len(self.history) > self.window_size:
            self.history.pop(0)
            
        is_spike = False
        anomalous_sensors = []
        ml_score = 0.0
        stats_score = 0.0
        
        # 1. ML Evaluation
        if self.is_trained and self.model is not None:
            X_current = np.array([values])
            pred = self.model.predict(X_current)[0]
            score = self.model.decision_function(X_current)[0]
            ml_score = -score * 10 
            if pred == -1:
                is_spike = True
                anomalous_sensors.append("Anomalía ML")

        # 2. Stats Evaluation (MAD)
        if len(self.history) >= 4:
            hist_arr = np.array(self.history)
            deltas = np.abs(np.diff(hist_arr, axis=0))
            current_delta = deltas[-1]
            past_deltas = deltas[:-1]
            
            median_delta = np.median(past_deltas, axis=0)
            mad_delta = np.median(np.abs(past_deltas - median_delta), axis=0)
            std_delta = mad_delta * 1.4826
            
            # Ajustamos aguaAnalogico (index 3) de 30.0 a 10.0 para que sea más sensible a las subidas
            min_noise = np.array([0.5, 1.0, 10.0, 10.0, 0.2, 0.5, 5.0, 1.0, 1.0, 10.0, 5.0, 0.5])
            std_delta = np.maximum(std_delta, min_noise)
            
            z_scores = (current_delta - median_delta) / std_delta
            stats_score = float(np.max(z_scores))
            
            if self.startup_ticks > 10 and stats_score > 3.5:
                is_spike = True
                for i, s in enumerate(z_scores):
                    if s > 3.5 and self.features[i] not in anomalous_sensors:
                        anomalous_sensors.append(self.features[i])
        
        final_score = max(ml_score, stats_score)
        score_for_ui = -final_score if is_spike else final_score
        
        return {
            "is_anomaly": is_spike,
            "anomaly_score": round(score_for_ui, 3),
            "status": "danger" if is_spike else "normal",
            "anomalous_sensors": anomalous_sensors if is_spike else []
        }

ai_model = TelemetryAIModel()

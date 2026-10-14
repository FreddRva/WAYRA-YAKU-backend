import requests
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import IsolationForest

def download_and_generate_dataset():
    print("Iniciando descarga de datos climáticos de Cachi-Apacheta (Lat: -13.3500, Lon: -74.6800)...")
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": -13.3500,
        "longitude": -74.6800,
        "start_date": "2024-01-01",
        "end_date": "2025-12-31",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,surface_pressure,direct_normal_irradiance",
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        temperaturas = hourly.get("temperature_2m", [])
        humedades = hourly.get("relative_humidity_2m", [])
        precipitaciones = hourly.get("precipitation", [])
        presiones = hourly.get("surface_pressure", [])
        radiaciones = hourly.get("direct_normal_irradiance", [])
        
        print(f"Descargados {len(times)} registros horarios reales.")
        
        # Mapeo y correlación física con las 12 variables del humedal
        n = len(times)
        
        # 1. Temperatura ambiente (°C)
        temp_arr = np.array(temperaturas, dtype=float)
        
        # 2. Humedad relativa (%)
        hum_arr = np.array(humedades, dtype=float)
        
        # 3. Presión atmosférica (hPa)
        pres_arr = np.array(presiones, dtype=float)
        
        # 4. Radiación UV / Luz solar (convertida a escala ADC 0 - 4095)
        rad_arr = np.array(radiaciones, dtype=float)
        aire_adc = np.clip(rad_arr * 3.5, 0, 4095)
        
        # 5. Precipitación / Lluvia (convertida a escala ADC del sensor de lluvia 0 - 4095)
        precip_arr = np.array(precipitaciones, dtype=float)
        agua_adc = np.clip(precip_arr * 450 + np.random.normal(50, 10, n), 0, 4095)
        
        # 6. Humedad de suelo / bofedal (ADC 0 - 4095)
        # El bofedal retiene humedad, varía entre 1500 y 3200 ADC
        suelo_adc = np.clip(1800 + (precip_arr * 150) + (hum_arr * 10) + np.random.normal(0, 30, n), 800, 3800)
        
        # 7. Temperatura del líquido / agua (°C)
        # El agua en la puna andina es más estable que el aire: varía entre 1°C y 9°C
        temp_liq = np.clip(temp_arr * 0.4 + 3.0 + np.random.normal(0, 0.4, n), 0.5, 12.0)
        
        # 8. pH del agua
        # Aguas de bofedal altoandino: ligeramente neutras a ácidas (6.8 a 7.6)
        ph_arr = np.clip(7.2 - (precip_arr * 0.08) + np.random.normal(0, 0.12, n), 6.5, 8.2)
        
        # 9. Turbidez (NTU)
        # Sube con lluvia fuerte (arrastre de sedimentos), baja en época seca
        turb_arr = np.clip(8.0 + (precip_arr * 12.5) + np.random.normal(0, 1.5, n), 2.0, 95.0)
        
        # 10. Sedimentos (PPM / MQ135)
        sed_arr = np.clip(25.0 + (turb_arr * 0.6) + np.random.normal(0, 3.0, n), 10.0, 180.0)
        
        # 11. Pureza TDS (ppm)
        # TDS en manantiales de bofedal: 150 - 350 ppm
        tds_arr = np.clip(220.0 - (precip_arr * 15.0) + np.random.normal(0, 12.0, n), 80.0, 500.0)
        
        # 12. Caudal (L/min)
        # Sube con lluvias y deshielos
        caudal_arr = np.clip(3.2 + (precip_arr * 1.8) + np.random.normal(0, 0.3, n), 0.5, 22.0)
        
        df_cachi = pd.DataFrame({
            "temperatura": np.round(temp_arr, 2),
            "humedad": np.round(hum_arr, 2),
            "tds": np.round(tds_arr, 2),
            "aguaAnalogico": np.round(agua_adc, 0),
            "ph": np.round(ph_arr, 2),
            "suelo": np.round(suelo_adc, 0),
            "turbidez": np.round(turb_arr, 2),
            "caudal": np.round(caudal_arr, 2),
            "presion": np.round(pres_arr, 2),
            "aire": np.round(aire_adc, 0),
            "sedimento": np.round(sed_arr, 2),
            "temp_liquido": np.round(temp_liq, 2)
        })
        
        csv_path = os.path.join(os.path.dirname(__file__), "history.csv")
        df_cachi.to_csv(csv_path, index=False)
        print(f"Dataset generado exitosamente en: {csv_path} con {len(df_cachi)} filas.")
        
        # Reentrenamiento del modelo Isolation Forest
        print("Entrenando Isolation Forest con los datos reales de Cachi-Apacheta...")
        features = [
            "temperatura", "humedad", "tds", "aguaAnalogico",
            "ph", "suelo", "turbidez", "caudal",
            "presion", "aire", "sedimento", "temp_liquido"
        ]
        X = df_cachi[features].values
        model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
        model.fit(X)
        
        model_path = os.path.join(os.path.dirname(__file__), "isolation_forest.joblib")
        joblib.dump(model, model_path)
        print(f"Modelo entrenado y guardado en: {model_path}")
        print("¡Proceso completado exitosamente!")
        
    except Exception as e:
        print(f"Error procesando dataset: {e}")

if __name__ == "__main__":
    download_and_generate_dataset()

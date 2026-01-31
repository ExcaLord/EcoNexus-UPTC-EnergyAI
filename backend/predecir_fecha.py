"""
Genera predicciones para fechas específicas
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data" / "clean"
OUTPUT_DIR = BASE_DIR / "output"


def predecir_fecha_especifica(sede, fecha_inicio, dias=7):
    """
    Predice consumo para un rango de fechas específico
    
    Args:
        sede: Nombre de la sede
        fecha_inicio: datetime object o string 'YYYY-MM-DD'
        dias: Número de días a predecir (default 7)
    """
    model_path = MODELS_DIR / 'modelo_xgboost.joblib'
    
    if not model_path.exists():
        print("❌ Modelo no encontrado")
        return None
    
    print(f"✅ Cargando modelo...")
    model_data = joblib.load(model_path)
    model = model_data['model']
    feature_cols = model_data['feature_cols']
    
    df = pd.read_csv(DATA_DIR / "consumos_uptc_clean.csv", parse_dates=['timestamp'])
    df_sede = df[df.sede == sede].sort_values('timestamp').tail(168)
    
    if len(df_sede) == 0:
        print(f"❌ No hay datos para {sede}")
        return None
    
    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    
    ultima_potencia = df_sede['potencia_total_kw'].mean()
    ultima_ocupacion = df_sede['ocupacion_pct'].mean()
    ultima_temp = df_sede['temperatura_exterior_c'].mean()
    ultimo_consumo = df_sede['energia_total_kwh'].iloc[-1]
    consumo_24h_atras = df_sede['energia_total_kwh'].iloc[-24] if len(df_sede) >= 24 else ultimo_consumo
    consumo_168h_atras = df_sede['energia_total_kwh'].iloc[0] if len(df_sede) >= 168 else ultimo_consumo
    
    print(f"\n🔮 PREDICCIÓN PARA: {sede}")
    print(f"📅 Desde: {fecha_inicio}")
    print(f"📅 Hasta: {fecha_inicio + timedelta(days=dias)}")
    print("=" * 80)
    
    predicciones = []
    horas_totales = dias * 24
    
    for i in range(horas_totales):
        future_time = fecha_inicio + timedelta(hours=i)
        
        features = {
            'potencia_total_kw': ultima_potencia,
            'agua_litros': df_sede['agua_litros'].mean(),
            'temperatura_exterior_c': ultima_temp,
            'ocupacion_pct': ultima_ocupacion if 7 <= future_time.hour <= 20 and future_time.weekday() < 5 else 0,
            'hora': future_time.hour,
            'dia_semana': future_time.weekday(),
            'mes': future_time.month,
            'trimestre': (future_time.month - 1) // 3 + 1,
            'año': future_time.year,
            'es_fin_semana': 1 if future_time.weekday() >= 5 else 0,
            'es_festivo': 0,
            'es_semana_parciales': 0,
            'es_semana_finales': 0,
            'dia_del_año': future_time.timetuple().tm_yday,
            'semana_del_año': future_time.isocalendar()[1],
            'es_inicio_mes': 1 if future_time.day <= 7 else 0,
            'es_fin_mes': 1 if future_time.day >= 24 else 0,
            'hora_sin': np.sin(2 * np.pi * future_time.hour / 24),
            'hora_cos': np.cos(2 * np.pi * future_time.hour / 24),
            'mes_sin': np.sin(2 * np.pi * future_time.month / 12),
            'mes_cos': np.cos(2 * np.pi * future_time.month / 12),
            'dia_semana_sin': np.sin(2 * np.pi * future_time.weekday() / 7),
            'dia_semana_cos': np.cos(2 * np.pi * future_time.weekday() / 7),
            'consumo_lag_1h': ultimo_consumo if i == 0 else predicciones[-1]['consumo_predicho'],
            'consumo_lag_24h': consumo_24h_atras if i < 24 else predicciones[-24]['consumo_predicho'],
            'consumo_lag_168h': consumo_168h_atras,
            'consumo_rolling_24h': df_sede['energia_total_kwh'].tail(24).mean(),
            'consumo_rolling_168h': df_sede['energia_total_kwh'].tail(168).mean(),
        }
        
        for s in ['Duitama', 'Sogamoso', 'Tunja']:
            features[f'sede_{s}'] = 1 if sede == s else 0
        
        for periodo in ['SEM_2', 'VAC_FIN', 'VAC_MITAD']:
            features[f'periodo_academico_{periodo}'] = 0
        
        pred_df = pd.DataFrame([features])
        
        for col in feature_cols:
            if col not in pred_df.columns:
                pred_df[col] = 0
        
        pred_df = pred_df[feature_cols]
        consumo_pred = model.predict(pred_df)[0]
        
        predicciones.append({
            'timestamp': future_time,
            'hora': future_time.hour,
            'dia': future_time.strftime('%A'),
            'consumo_predicho': consumo_pred
        })
    
    df_pred = pd.DataFrame(predicciones)
    
    print(f"\n📊 RESUMEN:")
    print(f"   Consumo total: {df_pred['consumo_predicho'].sum():.2f} kWh")
    print(f"   Promedio: {df_pred['consumo_predicho'].mean():.2f} kWh")
    
    df_pred['fecha'] = df_pred['timestamp'].dt.date
    consumo_diario = df_pred.groupby('fecha')['consumo_predicho'].sum()
    
    print(f"\n📅 CONSUMO DIARIO:")
    for fecha, consumo in consumo_diario.items():
        print(f"   {fecha}: {consumo:.2f} kWh")
    
    fecha_str = fecha_inicio.strftime('%Y%m%d')
    output_file = OUTPUT_DIR / f"predicciones_{sede.lower()}_{fecha_str}_{dias}dias.csv"
    df_pred.to_csv(output_file, index=False)
    print(f"\n💾 Guardado: {output_file}")
    
    return df_pred


def main():
    import sys
    
    if len(sys.argv) < 4:
        print("Uso: python predecir_fecha.py <sede> <fecha_inicio> <dias>")
        print("Ejemplo: python predecir_fecha.py Tunja 2026-02-01 7")
        return
    
    sede = sys.argv[1]
    fecha_inicio = sys.argv[2]
    dias = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    
    predecir_fecha_especifica(sede, fecha_inicio, dias)


if __name__ == "__main__":
    main()

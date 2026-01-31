"""
Predicciones con modelo XGBoost entrenado
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data" / "clean"


def cargar_modelo():
    model_path = MODELS_DIR / 'modelo_xgboost.joblib'
    
    if not model_path.exists():
        print("❌ Modelo no encontrado. Entrena primero con:")
        print("   python modelo_xgboost.py")
        return None
    
    print(f"✅ Cargando modelo desde: {model_path}")
    model_data = joblib.load(model_path)
    
    print("\n📊 Métricas del modelo:")
    for key, value in model_data['metrics'].items():
        print(f"   {key.upper()}: {value:.4f}")
    
    return model_data


def predecir_proxima_semana(sede='Tunja'):
    model_data = cargar_modelo()
    if model_data is None:
        return
    
    model = model_data['model']
    feature_cols = model_data['feature_cols']
    
    df = pd.read_csv(DATA_DIR / "consumos_uptc_clean.csv", parse_dates=['timestamp'])
    df_sede = df[df.sede == sede].sort_values('timestamp').tail(168)
    
    if len(df_sede) == 0:
        print(f"❌ No hay datos para la sede {sede}")
        return
    
    ultimo_timestamp = df_sede['timestamp'].max()
    ultima_potencia = df_sede['potencia_total_kw'].mean()
    ultima_ocupacion = df_sede['ocupacion_pct'].mean()
    ultima_temp = df_sede['temperatura_exterior_c'].mean()
    ultimo_consumo = df_sede['energia_total_kwh'].iloc[-1]
    consumo_24h_atras = df_sede['energia_total_kwh'].iloc[-24] if len(df_sede) >= 24 else ultimo_consumo
    consumo_168h_atras = df_sede['energia_total_kwh'].iloc[0] if len(df_sede) >= 168 else ultimo_consumo
    
    print(f"\n🔮 PREDICCIÓN PARA: {sede}")
    print(f"📅 Desde: {ultimo_timestamp + timedelta(hours=1)}")
    print(f"📅 Hasta: {ultimo_timestamp + timedelta(hours=168)}")
    print("=" * 80)
    
    predicciones = []
    
    for i in range(1, 169):
        future_time = ultimo_timestamp + timedelta(hours=i)
        
        features = {
            'potencia_total_kw': ultima_potencia,
            'agua_litros': df_sede['agua_litros'].mean(),
            'temperatura_exterior_c': ultima_temp,
            'ocupacion_pct': ultima_ocupacion if future_time.hour >= 7 and future_time.hour <= 20 else 0,
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
            'consumo_lag_1h': ultimo_consumo if i == 1 else predicciones[-1]['consumo_predicho'],
            'consumo_lag_24h': consumo_24h_atras if i <= 24 else predicciones[-24]['consumo_predicho'],
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
    
    print(f"\n📊 RESUMEN DE PREDICCIONES:")
    print(f"   Consumo promedio: {df_pred['consumo_predicho'].mean():.2f} kWh")
    print(f"   Consumo total: {df_pred['consumo_predicho'].sum():.2f} kWh")
    print(f"   Consumo máximo: {df_pred['consumo_predicho'].max():.2f} kWh")
    print(f"   Consumo mínimo: {df_pred['consumo_predicho'].min():.2f} kWh")
    
    df_pred['fecha'] = df_pred['timestamp'].dt.date
    consumo_diario = df_pred.groupby('fecha')['consumo_predicho'].sum()
    
    print(f"\n📅 CONSUMO DIARIO PREDICHO:")
    for fecha, consumo in consumo_diario.items():
        print(f"   {fecha}: {consumo:.2f} kWh")
    
    output_file = BASE_DIR / "output" / f"predicciones_{sede.lower()}_proxima_semana.csv"
    df_pred.to_csv(output_file, index=False)
    print(f"\n💾 Predicciones guardadas en: {output_file}")
    
    return df_pred


def comparar_sedes():
    print("\n" + "=" * 80)
    print("📊 COMPARACIÓN DE PREDICCIONES ENTRE SEDES")
    print("=" * 80)
    
    sedes = ['Tunja', 'Duitama', 'Sogamoso', 'Chiquinquirá']
    resultados = {}
    
    for sede in sedes:
        print(f"\n🔄 Procesando {sede}...")
        df_pred = predecir_proxima_semana(sede)
        if df_pred is not None:
            resultados[sede] = {
                'consumo_total': df_pred['consumo_predicho'].sum(),
                'consumo_promedio': df_pred['consumo_predicho'].mean(),
                'consumo_max': df_pred['consumo_predicho'].max()
            }
    
    if resultados:
        print("\n" + "=" * 80)
        print("📊 RESUMEN COMPARATIVO (PRÓXIMA SEMANA)")
        print("=" * 80)
        
        df_resumen = pd.DataFrame(resultados).T
        print(df_resumen.to_string())
        
        # Costo estimado
        tarifa = 600  # COP/kWh
        print(f"\n💰 COSTO ESTIMADO (@ ${tarifa} COP/kWh):")
        for sede, valores in resultados.items():
            costo = valores['consumo_total'] * tarifa
            print(f"   {sede:15s}: ${costo:,.0f} COP (${costo/4000:,.0f} USD)")

def main():
    print("\n" + "=" * 80)
    print("🔮 PREDICCIONES CON MODELO XGBOOST - UPTC")
    print("=" * 80)
    
    # Menú
    print("\n¿Qué deseas hacer?")
    print("1. Predecir consumo próxima semana (una sede)")
    print("2. Comparar predicciones entre todas las sedes")
    print("3. Salir")
    
    opcion = input("\nElige una opción (1-3): ").strip()
    
    if opcion == '1':
        print("\nSedes disponibles:")
        print("1. Tunja")
        print("2. Duitama")
        print("3. Sogamoso")
        print("4. Chiquinquirá")
        
        sede_num = input("\nElige una sede (1-4): ").strip()
        sedes = {
            '1': 'Tunja',
            '2': 'Duitama',
            '3': 'Sogamoso',
            '4': 'Chiquinquirá'
        }
        
        if sede_num in sedes:
            predecir_proxima_semana(sedes[sede_num])
        else:
            print("❌ Opción inválida")
    
    elif opcion == '2':
        comparar_sedes()
    
    elif opcion == '3':
        print("👋 ¡Hasta luego!")
    
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()

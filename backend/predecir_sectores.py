"""
Predicciones de consumo por sector
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

SECTORES = ['comedor', 'salones', 'laboratorios', 'auditorios', 'oficinas']


def predecir_por_sector(sede, fecha_inicio, dias=7):
    """
    Predice consumo total y desglosado por sector
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
    
    proporciones_sectores = {}
    for sector in SECTORES:
        col_name = f'energia_{sector}_kwh'
        if col_name in df_sede.columns:
            consumo_sector = df_sede[col_name].fillna(0).sum()
            consumo_total = df_sede['energia_total_kwh'].sum()
            proporciones_sectores[sector] = consumo_sector / consumo_total if consumo_total > 0 else 0
        else:
            proporciones_sectores[sector] = 0
    
    print(f"\n🔮 PREDICCIÓN PARA: {sede}")
    print(f"📅 Desde: {fecha_inicio}")
    print(f"📅 Hasta: {fecha_inicio + timedelta(days=dias)}")
    print("=" * 80)
    
    print(f"\n📊 PROPORCIONES POR SECTOR (basadas en histórico):")
    for sector, prop in proporciones_sectores.items():
        print(f"   {sector.capitalize():15s}: {prop*100:5.2f}%")
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
            'consumo_lag_1h': ultimo_consumo if i == 0 else predicciones[-1]['total'],
            'consumo_lag_24h': consumo_24h_atras if i < 24 else predicciones[-24]['total'],
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
        consumo_total_pred = model.predict(pred_df)[0]
        
        pred_entry = {
            'timestamp': future_time,
            'hora': future_time.hour,
            'dia': future_time.strftime('%A'),
            'total': consumo_total_pred
        }
        
        for sector, prop in proporciones_sectores.items():
            pred_entry[sector] = consumo_total_pred * prop
        
        predicciones.append(pred_entry)
    
    df_pred = pd.DataFrame(predicciones)
    
    print(f"\n📊 RESUMEN TOTAL:")
    print(f"   Consumo total: {df_pred['total'].sum():.2f} kWh")
    print(f"   Promedio horario: {df_pred['total'].mean():.2f} kWh")
    
    print(f"\n📊 RESUMEN POR SECTOR:")
    for sector in SECTORES:
        if sector in df_pred.columns:
            consumo_sector = df_pred[sector].sum()
            print(f"   {sector.capitalize():15s}: {consumo_sector:8.2f} kWh ({consumo_sector/df_pred['total'].sum()*100:5.2f}%)")
    
    df_pred['fecha'] = df_pred['timestamp'].dt.date
    
    print(f"\n📅 CONSUMO DIARIO TOTAL:")
    consumo_diario = df_pred.groupby('fecha')['total'].sum()
    for fecha, consumo in consumo_diario.items():
        print(f"   {fecha}: {consumo:.2f} kWh")
    
    fecha_str = fecha_inicio.strftime('%Y%m%d')
    output_file = OUTPUT_DIR / f"predicciones_sectores_{sede.lower()}_{fecha_str}_{dias}dias.csv"
    df_pred.to_csv(output_file, index=False)
    print(f"\n💾 Guardado: {output_file}")
    
    return df_pred


def comparar_sectores(sede, fecha_inicio, dias=7):
    """Compara consumo entre sectores"""
    df_pred = predecir_por_sector(sede, fecha_inicio, dias)
    
    if df_pred is None:
        return
    
    print("\n" + "=" * 80)
    print(f"📊 ANÁLISIS COMPARATIVO POR SECTOR - {sede}")
    print("=" * 80)
    
    import matplotlib.pyplot as plt
    
    consumo_sectores = {}
    for sector in SECTORES:
        if sector in df_pred.columns:
            consumo_sectores[sector.capitalize()] = df_pred[sector].sum()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    ax1.pie(consumo_sectores.values(), labels=consumo_sectores.keys(), autopct='%1.1f%%',
            colors=colors, startangle=90)
    ax1.set_title(f'Distribución de Consumo por Sector - {sede}', fontweight='bold', fontsize=14)
    
    ax2.barh(list(consumo_sectores.keys()), list(consumo_sectores.values()), color=colors)
    ax2.set_xlabel('Consumo Total (kWh)', fontsize=12)
    ax2.set_title(f'Consumo por Sector - {sede}', fontweight='bold', fontsize=14)
    ax2.grid(True, alpha=0.3, axis='x')
    
    for i, v in enumerate(consumo_sectores.values()):
        ax2.text(v, i, f' {v:.1f} kWh', va='center', fontsize=10)
    
    plt.tight_layout()
    fecha_str = fecha_inicio.strftime('%Y%m%d') if isinstance(fecha_inicio, datetime) else fecha_inicio.replace('-', '')
    output_img = OUTPUT_DIR / f"sectores_{sede.lower()}_{fecha_str}.png"
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    print(f"\n📊 Gráfico guardado: {output_img}")
    plt.close()


def main():
    import sys
    
    if len(sys.argv) < 4:
        print("Uso: python predecir_sectores.py <sede> <fecha_inicio> <dias>")
        print("Ejemplo: python predecir_sectores.py Tunja 2026-02-01 7")
        return
    
    sede = sys.argv[1]
    fecha_inicio = sys.argv[2]
    dias = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    
    predecir_por_sector(sede, fecha_inicio, dias)
    comparar_sectores(sede, fecha_inicio, dias)


if __name__ == "__main__":
    main()

"""
Explicabilidad simplificada usando feature importance de XGBoost
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / 'models' / 'modelo_xgboost.joblib'
DATA_PATH = BASE_DIR / 'data' / 'clean' / 'consumos_uptc_clean.csv'
OUTPUT_DIR = BASE_DIR / 'output'
CONFIG_PATH = BASE_DIR / 'config_recomendaciones.json'

def cargar_configuracion():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'umbrales': {'pico_consumo': 1.5, 'fin_semana': 0.5, 'nocturno': 0.3},
        'costos': {'kwh_cop': 1050},
        'ahorros': {'porcentaje_objetivo': 0.15}
    }

def cargar_datos_y_modelo():
    print("📊 Cargando datos y modelo...")
    df = pd.read_csv(DATA_PATH)
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    modelo_dict = joblib.load(MODEL_PATH)
    if isinstance(modelo_dict, dict):
        modelo = modelo_dict['model']
        feature_cols = modelo_dict['feature_cols']
    else:
        modelo = modelo_dict
        feature_cols = None
    return df, modelo, feature_cols

def generar_feature_importance(modelo, feature_names):
    print("\n📊 Generando Feature Importance...")
    
    importance = modelo.feature_importances_
    
    print(f"Debug: importance len={len(importance)}, feature_names len={len(feature_names)}")
    
    if len(importance) != len(feature_names):
        print(f"⚠️ Ajustando longitudes: usando {min(len(importance), len(feature_names))} features")
        min_len = min(len(importance), len(feature_names))
        importance = importance[:min_len]
        feature_names = list(feature_names)[:min_len]
    
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importancia_SHAP': importance
    }).sort_values('Importancia_SHAP', ascending=False)
    
    plt.figure(figsize=(12, 8))
    top_15 = importance_df.head(15)
    plt.barh(range(len(top_15)), top_15['Importancia_SHAP'])
    plt.yticks(range(len(top_15)), top_15['Feature'])
    plt.xlabel('Importancia')
    plt.title('Top 15 Features Más Importantes (XGBoost Feature Importance)', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    
    output_path = OUTPUT_DIR / 'shap_summary.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Feature importance guardado: {output_path}")
    
    plt.figure(figsize=(12, 6))
    top_10 = importance_df.head(10)
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_10)))
    plt.bar(range(len(top_10)), top_10['Importancia_SHAP'], color=colors)
    plt.xticks(range(len(top_10)), top_10['Feature'], rotation=45, ha='right')
    plt.ylabel('Importancia')
    plt.xlabel('Característica')
    plt.title('Impacto de Características en Predicción de Consumo', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    output_path2 = OUTPUT_DIR / 'shap_beeswarm.png'
    plt.savefig(output_path2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico de impacto guardado: {output_path2}")
    
    return importance_df

def preparar_features(df, feature_cols):
    if feature_cols is None:
        features = [
            'hora', 'dia_semana', 'mes', 'es_fin_semana', 'trimestre',
            'temperatura_exterior_c', 'ocupacion_pct', 
            'potencia_total_kw', 'agua_litros', 'año'
        ]
        available_features = [f for f in features if f in df.columns]
        if len(available_features) == 0:
            available_features = ['hora', 'dia_semana', 'mes', 'es_fin_semana']
        return df[available_features].fillna(0), available_features
    else:
        available_features = [f for f in feature_cols if f in df.columns]
        return df[available_features].fillna(0), available_features

def generar_recomendaciones_por_sede(df, sede, importance_df=None, umbral_pico=1.5, umbral_fin_semana=0.5, umbral_nocturno=0.3):
    """Genera recomendaciones personalizadas"""
    print(f"\n💡 Generando recomendaciones para {sede}...")
    
    df_sede = df[df['sede'] == sede].copy()
    recomendaciones = []
    
    consumo_col = 'energia_total_kwh' if 'energia_total_kwh' in df_sede.columns else 'consumo_kwh'
    consumo_promedio = df_sede[consumo_col].mean()
    consumo_max = df_sede.groupby('hora')[consumo_col].mean().idxmax()
    consumo_hora_max = df_sede.groupby('hora')[consumo_col].mean().max()
    
    if consumo_hora_max > consumo_promedio * umbral_pico:
        ahorro_potencial = (consumo_hora_max - consumo_promedio) * 30
        recomendaciones.append({
            'tipo': 'Crítico',
            'categoria': 'Picos de Consumo',
            'descripcion': f'Consumo máximo a las {consumo_max:02d}:00 hrs ({consumo_hora_max:.2f} kWh)',
            'accion': f'Redistribuir actividades de alto consumo fuera del horario pico. Potencial ahorro: {ahorro_potencial:.0f} kWh/mes',
            'ahorro_kwh': ahorro_potencial,
            'impacto': 'Alto'
        })
    
    consumo_fin_semana = df_sede[df_sede['es_fin_semana'] == 1][consumo_col].mean()
    consumo_semana = df_sede[df_sede['es_fin_semana'] == 0][consumo_col].mean()
    
    if consumo_fin_semana > consumo_semana * umbral_fin_semana:
        ahorro_potencial = (consumo_fin_semana - consumo_semana * 0.2) * 8
        recomendaciones.append({
            'tipo': 'Advertencia',
            'categoria': 'Consumo Fin de Semana',
            'descripcion': f'Consumo fin de semana alto ({consumo_fin_semana:.2f} kWh vs {consumo_semana:.2f} kWh)',
            'accion': f'Verificar equipos encendidos innecesariamente. Ahorro: {ahorro_potencial:.0f} kWh/mes',
            'ahorro_kwh': ahorro_potencial,
            'impacto': 'Medio'
        })
    
    consumo_nocturno = df_sede[df_sede['hora'].between(22, 6)][consumo_col].mean()
    if consumo_nocturno > consumo_promedio * umbral_nocturno:
        ahorro_potencial = (consumo_nocturno - consumo_promedio * 0.1) * 8 * 30
        recomendaciones.append({
            'tipo': 'Advertencia',
            'categoria': 'Consumo Nocturno',
            'descripcion': f'Consumo nocturno elevado ({consumo_nocturno:.2f} kWh)',
            'accion': f'Auditar iluminación y equipos nocturnos. Ahorro: {ahorro_potencial:.0f} kWh/mes',
            'ahorro_kwh': ahorro_potencial,
            'impacto': 'Medio'
        })
    
    if importance_df is not None and not importance_df.empty:
        top_feature = importance_df.iloc[0]
        recomendaciones.append({
            'tipo': 'Información',
            'categoria': 'Factor Clave (ML)',
            'descripcion': f'"{top_feature["Feature"]}" es el factor más influyente (importancia: {top_feature["Importancia_SHAP"]:.3f})',
            'accion': f'Priorizar gestión de {top_feature["Feature"]} para maximizar impacto en eficiencia energética.',
            'ahorro_kwh': 0,
            'impacto': 'Estratégico'
        })
    
    recomendaciones.append({
        'tipo': 'Información',
        'categoria': 'Eficiencia Energética',
        'descripcion': f'Consumo promedio: {consumo_promedio:.2f} kWh',
        'accion': 'Monitoreo continuo de patrones. Implementar sistema de gestión energética ISO 50001.',
        'ahorro_kwh': 0,
        'impacto': 'Bajo'
    })
    
    return pd.DataFrame(recomendaciones)

def generar_recomendaciones_generales(df, costo_kwh=1050, porcentaje_ahorro=0.15):
    print(f"\n💡 Generando recomendaciones generales...")
    
    recomendaciones = []
    consumo_col = 'energia_total_kwh' if 'energia_total_kwh' in df.columns else 'consumo_kwh'
    
    consumo_total = df.groupby('sede')[consumo_col].sum()
    sede_mayor_consumo = consumo_total.idxmax()
    sede_menor_consumo = consumo_total.idxmin()
    ratio_consumo = consumo_total[sede_mayor_consumo]/consumo_total[sede_menor_consumo]
    
    recomendaciones.append({
        'tipo': 'Crítico',
        'categoria': 'Comparación entre Sedes',
        'descripcion': f'{sede_mayor_consumo} consume {ratio_consumo:.1f}x más que {sede_menor_consumo}',
        'accion': f'Benchmarking de mejores prácticas de {sede_menor_consumo}. Auditoría energética en {sede_mayor_consumo}.',
        'ahorro_kwh': (consumo_total[sede_mayor_consumo] - consumo_total[sede_menor_consumo] * ratio_consumo) * 0.3,
        'impacto': 'Alto'
    })
    
    if 'temperatura_exterior_c' in df.columns:
        correlacion_temp = df[['temperatura_exterior_c', consumo_col]].corr().iloc[0, 1]
        if abs(correlacion_temp) > 0.5:
            ahorro_climatizacion = df[consumo_col].sum() * 0.2
            recomendaciones.append({
                'tipo': 'Advertencia',
                'categoria': 'Climatización',
                'descripcion': f'Alta correlación consumo-temperatura ({correlacion_temp:.2f})',
                'accion': f'Optimizar climatización. Ahorro: {ahorro_climatizacion:.0f} kWh/año',
                'ahorro_kwh': ahorro_climatizacion,
                'impacto': 'Alto'
            })
    
    variabilidad = df.groupby('sede')[consumo_col].std()
    sede_inestable = variabilidad.idxmax()
    
    recomendaciones.append({
        'tipo': 'Advertencia',
        'categoria': 'Variabilidad de Consumo',
        'descripcion': f'{sede_inestable} tiene alta variabilidad en consumo',
        'accion': 'Identificar causas de fluctuaciones. Establecer protocolos de uso energético.',
        'ahorro_kwh': variabilidad[sede_inestable] * 0.3 * 365,
        'impacto': 'Medio'
    })
    
    ahorro_estimado = df[consumo_col].sum() * porcentaje_ahorro
    ahorro_pesos = ahorro_estimado * costo_kwh
    
    recomendaciones.append({
        'tipo': 'Información',
        'categoria': 'Potencial de Ahorro',
        'descripcion': f'Ahorro estimado con optimizaciones: {ahorro_estimado:.0f} kWh/año',
        'accion': f'Implementar recomendaciones puede ahorrar ${ahorro_pesos:,.0f} COP anuales ({porcentaje_ahorro*100:.0f}%).',
        'ahorro_kwh': ahorro_estimado,
        'impacto': 'Estratégico'
    })
    
    return pd.DataFrame(recomendaciones)

def main():
    print("=" * 80)
    print("🔬 ANÁLISIS DE EXPLICABILIDAD - Feature Importance")
    print("=" * 80)
    
    config = cargar_configuracion()
    print(f"\n⚙️  Configuración cargada:")
    print(f"  • Umbral picos: {config['umbrales']['pico_consumo']}x")
    print(f"  • Costo kWh: ${config['costos']['kwh_cop']} COP")
    print(f"  • Objetivo ahorro: {config['ahorros']['porcentaje_objetivo']*100:.0f}%")
    
    df, modelo, feature_cols = cargar_datos_y_modelo()
    
    X, feature_names = preparar_features(df, feature_cols)
    
    importance_df = generar_feature_importance(modelo, feature_names)
    
    print("\n📊 Top 10 Features por Importancia:")
    print(importance_df.head(10).to_string(index=False))
    
    importance_path = OUTPUT_DIR / 'feature_importance_shap.csv'
    importance_df.to_csv(importance_path, index=False)
    print(f"\n✅ Importancia guardada: {importance_path}")
    
    print("\n" + "=" * 80)
    print("💡 GENERANDO RECOMENDACIONES PERSONALIZADAS")
    print("=" * 80)
    
    sedes = df['sede'].unique()
    todas_recomendaciones = []
    
    umbrales = config['umbrales']
    costo_kwh = config['costos']['kwh_cop']
    porcentaje_ahorro = config['ahorros']['porcentaje_objetivo']
    
    for sede in sedes:
        rec_sede = generar_recomendaciones_por_sede(
            df, sede, 
            importance_df=importance_df,
            umbral_pico=umbrales['pico_consumo'],
            umbral_fin_semana=umbrales['fin_semana'],
            umbral_nocturno=umbrales['nocturno']
        )
        rec_sede['sede'] = sede
        todas_recomendaciones.append(rec_sede)
        
        print(f"\n📍 {sede}:")
        for _, rec in rec_sede.iterrows():
            ahorro_txt = f" [Ahorro: {rec['ahorro_kwh']:.0f} kWh]" if rec.get('ahorro_kwh', 0) > 0 else ""
            print(f"  [{rec['tipo']}] {rec['categoria']}: {rec['accion']}{ahorro_txt}")
    
    rec_generales = generar_recomendaciones_generales(df, costo_kwh=costo_kwh, porcentaje_ahorro=porcentaje_ahorro)
    rec_generales['sede'] = 'Todas'
    todas_recomendaciones.append(rec_generales)
    
    print(f"\n📍 Recomendaciones Generales:")
    for _, rec in rec_generales.iterrows():
        ahorro_txt = f" [Ahorro: {rec['ahorro_kwh']:.0f} kWh]" if rec.get('ahorro_kwh', 0) > 0 else ""
        print(f"  [{rec['tipo']}] {rec['categoria']}: {rec['accion']}{ahorro_txt}")
    
    df_recomendaciones = pd.concat(todas_recomendaciones, ignore_index=True)
    rec_path = OUTPUT_DIR / 'recomendaciones_personalizadas.csv'
    df_recomendaciones.to_csv(rec_path, index=False)
    print(f"\n✅ Recomendaciones guardadas: {rec_path}")
    
    print("\n" + "=" * 80)
    print("✅ ANÁLISIS COMPLETADO")
    print("=" * 80)
    print(f"\n📁 Archivos generados en: {OUTPUT_DIR}")
    print("  • shap_summary.png - Importancia de features")
    print("  • feature_importance_shap.csv - Importancia numérica")
    print("  • recomendaciones_personalizadas.csv - Acciones concretas")
    print("\n🎯 Usa estos resultados para explicar el modelo en la presentación!")
    print("\n💡 Para cambiar umbrales o costos, edita: config_recomendaciones.json")

if __name__ == "__main__":
    main()

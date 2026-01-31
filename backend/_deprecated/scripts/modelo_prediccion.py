"""
Template para modelo de predicción de consumo energético
Este es un punto de partida para implementar ML en el proyecto
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt

# Configuración
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "clean"
OUTPUT_DIR = BASE_DIR / "output"

def load_data():
    """Carga datos limpios"""
    df = pd.read_csv(DATA_DIR / "consumos_uptc_clean.csv", parse_dates=['timestamp'])
    return df

def feature_engineering(df):
    """
    Crea features adicionales para mejorar predicción
    """
    df = df.copy()
    
    # Asegurar que timestamp es datetime
    if df['timestamp'].dtype != 'datetime64[ns]':
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Features temporales adicionales
    df['dia_del_año'] = df['timestamp'].dt.dayofyear
    df['semana_del_año'] = df['timestamp'].dt.isocalendar().week.astype(int)
    df['es_inicio_mes'] = (df['timestamp'].dt.day <= 7).astype(int)
    df['es_fin_mes'] = (df['timestamp'].dt.day >= 24).astype(int)
    
    # Features cíclicas (para capturar periodicidad)
    df['hora_sin'] = np.sin(2 * np.pi * df['hora'] / 24)
    df['hora_cos'] = np.cos(2 * np.pi * df['hora'] / 24)
    df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
    df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)
    
    # Lag features (consumo de horas previas)
    df = df.sort_values(['sede_id', 'timestamp'])
    for sede in df.sede_id.unique():
        mask = df.sede_id == sede
        df.loc[mask, 'consumo_lag_1h'] = df.loc[mask, 'energia_total_kwh'].shift(1)
        df.loc[mask, 'consumo_lag_24h'] = df.loc[mask, 'energia_total_kwh'].shift(24)
        df.loc[mask, 'consumo_lag_168h'] = df.loc[mask, 'energia_total_kwh'].shift(168)  # 1 semana
        
        # Rolling means
        df.loc[mask, 'consumo_rolling_24h'] = df.loc[mask, 'energia_total_kwh'].rolling(24, min_periods=1).mean()
        df.loc[mask, 'consumo_rolling_168h'] = df.loc[mask, 'energia_total_kwh'].rolling(168, min_periods=1).mean()
    
    # One-hot encoding para variables categóricas (solo las que existen)
    categorical_cols = []
    if 'sede' in df.columns:
        categorical_cols.append('sede')
    if 'periodo_academico' in df.columns:
        categorical_cols.append('periodo_academico')
    if 'dia_nombre' in df.columns:
        categorical_cols.append('dia_nombre')
    
    if categorical_cols:
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    
    return df

def prepare_train_test(df, test_size=0.2):
    """
    Prepara datos para entrenamiento
    Split temporal (importante para series de tiempo)
    """
    # Eliminar filas con NaN en lag features
    df = df.dropna()
    
    # Features a usar (excluir target y features que causan data leakage)
    feature_cols = [col for col in df.columns if col not in [
        'reading_id', 'timestamp', 'sede_id', 'energia_total_kwh',
        'energia_comedor_kwh', 'energia_salones_kwh', 'energia_laboratorios_kwh',
        'energia_auditorios_kwh', 'energia_oficinas_kwh', 'co2_kg',
        'flag_ocupacion_fuera_rango', 'flag_agua_fuera_rango',
        'energia_total_calc_kwh', 'energia_total_inconsistente'  # Excluir estas que causan leakage
    ]]
    
    X = df[feature_cols]
    y = df['energia_total_kwh']
    
    # Split temporal (NO aleatorio para series de tiempo)
    split_idx = int(len(df) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"📊 Train size: {len(X_train):,} | Test size: {len(X_test):,}")
    print(f"📅 Train period: {df.timestamp.min()} to {df.timestamp.iloc[split_idx]}")
    print(f"📅 Test period: {df.timestamp.iloc[split_idx]} to {df.timestamp.max()}")
    
    return X_train, X_test, y_train, y_test, feature_cols

def train_baseline_model(X_train, y_train):
    """
    Modelo baseline: Random Forest
    """
    print("\n🌲 Entrenando Random Forest...")
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=20,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """
    Evalúa el modelo con métricas estándar
    """
    print("\n📊 Evaluando modelo...")
    
    y_pred = model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    print("\n" + "=" * 60)
    print("MÉTRICAS DE EVALUACIÓN")
    print("=" * 60)
    print(f"RMSE (Root Mean Squared Error): {rmse:.4f} kWh")
    print(f"MAE (Mean Absolute Error):      {mae:.4f} kWh")
    print(f"R² (Coefficient of Determination): {r2:.4f}")
    print(f"MAPE (Mean Absolute % Error):   {mape:.2f}%")
    print("=" * 60)
    
    return y_pred, {'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape}

def plot_predictions(y_test, y_pred):
    """
    Visualiza predicciones vs. valores reales
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Scatter plot
    axes[0].scatter(y_test, y_pred, alpha=0.3, s=1)
    axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    axes[0].set_xlabel('Consumo Real (kWh)')
    axes[0].set_ylabel('Consumo Predicho (kWh)')
    axes[0].set_title('Predicciones vs. Valores Reales')
    axes[0].grid(True, alpha=0.3)
    
    # Serie temporal (muestra 1000 puntos)
    sample_size = min(1000, len(y_test))
    axes[1].plot(range(sample_size), y_test.iloc[:sample_size].values, label='Real', alpha=0.7)
    axes[1].plot(range(sample_size), y_pred[:sample_size], label='Predicho', alpha=0.7)
    axes[1].set_xlabel('Índice')
    axes[1].set_ylabel('Consumo (kWh)')
    axes[1].set_title('Serie Temporal: Real vs. Predicho (primeros 1000)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'predicciones_ml.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico guardado: {OUTPUT_DIR / 'predicciones_ml.png'}")

def feature_importance(model, feature_cols):
    """
    Muestra las features más importantes
    """
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🎯 TOP 15 FEATURES MÁS IMPORTANTES:")
    print("-" * 60)
    print(importance_df.head(15).to_string(index=False))
    
    # Visualizar
    plt.figure(figsize=(10, 8))
    top_features = importance_df.head(20)
    plt.barh(range(len(top_features)), top_features.importance)
    plt.yticks(range(len(top_features)), top_features.feature)
    plt.xlabel('Importancia')
    plt.title('Top 20 Features Más Importantes')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'feature_importance.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico guardado: {OUTPUT_DIR / 'feature_importance.png'}")

def main():
    """
    Pipeline completo de ML
    """
    print("\n" + "=" * 80)
    print("MODELO DE PREDICCIÓN DE CONSUMO ENERGÉTICO - UPTC")
    print("=" * 80)
    
    # 1. Cargar datos
    print("\n1️⃣ Cargando datos...")
    df = load_data()
    print(f"   Registros cargados: {len(df):,}")
    
    # 2. Feature engineering
    print("\n2️⃣ Creando features...")
    df = feature_engineering(df)
    print(f"   Features creadas: {len(df.columns)} columnas")
    
    # 3. Preparar train/test
    print("\n3️⃣ Preparando datos de entrenamiento...")
    X_train, X_test, y_train, y_test, feature_cols = prepare_train_test(df)
    
    # 4. Entrenar modelo
    print("\n4️⃣ Entrenando modelo...")
    model = train_baseline_model(X_train, y_train)
    
    # 5. Evaluar
    print("\n5️⃣ Evaluando modelo...")
    y_pred, metrics = evaluate_model(model, X_test, y_test)
    
    # 6. Visualizaciones
    print("\n6️⃣ Generando visualizaciones...")
    plot_predictions(y_test, y_pred)
    feature_importance(model, feature_cols)
    
    print("\n" + "=" * 80)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 80)
    print("\n💡 PRÓXIMOS PASOS:")
    print("   • Probar otros modelos: XGBoost, LSTM, Prophet")
    print("   • Optimizar hiperparámetros con GridSearch")
    print("   • Agregar más features (clima, eventos especiales)")
    print("   • Implementar validación cruzada temporal")
    print("   • Integrar predicciones en el dashboard")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

"""
Modelo XGBoost para predicción de consumo energético
"""

import pandas as pd
import numpy as np
from pathlib import Path
import xgboost as xgb
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import joblib

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "clean"
OUTPUT_DIR = BASE_DIR / "output"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)


def load_data():
    df = pd.read_csv(DATA_DIR / "consumos_uptc_clean.csv", parse_dates=['timestamp'])
    return df


def feature_engineering(df):
    df = df.copy()
    
    if df['timestamp'].dtype != 'datetime64[ns]':
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    df['dia_del_año'] = df['timestamp'].dt.dayofyear
    df['semana_del_año'] = df['timestamp'].dt.isocalendar().week.astype(int)
    df['es_inicio_mes'] = (df['timestamp'].dt.day <= 7).astype(int)
    df['es_fin_mes'] = (df['timestamp'].dt.day >= 24).astype(int)
    
    df['hora_sin'] = np.sin(2 * np.pi * df['hora'] / 24)
    df['hora_cos'] = np.cos(2 * np.pi * df['hora'] / 24)
    df['mes_sin'] = np.sin(2 * np.pi * df['mes'] / 12)
    df['mes_cos'] = np.cos(2 * np.pi * df['mes'] / 12)
    df['dia_semana_sin'] = np.sin(2 * np.pi * df['dia_semana'] / 7)
    df['dia_semana_cos'] = np.cos(2 * np.pi * df['dia_semana'] / 7)
    
    df = df.sort_values(['sede_id', 'timestamp'])
    for sede in df.sede_id.unique():
        mask = df.sede_id == sede
        df.loc[mask, 'consumo_lag_1h'] = df.loc[mask, 'energia_total_kwh'].shift(1)
        df.loc[mask, 'consumo_lag_24h'] = df.loc[mask, 'energia_total_kwh'].shift(24)
        df.loc[mask, 'consumo_lag_168h'] = df.loc[mask, 'energia_total_kwh'].shift(168)
        df.loc[mask, 'consumo_rolling_24h'] = df.loc[mask, 'energia_total_kwh'].rolling(24, min_periods=1).mean()
        df.loc[mask, 'consumo_rolling_168h'] = df.loc[mask, 'energia_total_kwh'].rolling(168, min_periods=1).mean()
    
    categorical_cols = []
    if 'sede' in df.columns:
        categorical_cols.append('sede')
    if 'periodo_academico' in df.columns:
        categorical_cols.append('periodo_academico')
    
    if categorical_cols:
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)
    
    return df


def prepare_data(df, test_size=0.2):
    df = df.dropna()
    
    exclude_cols = [
        'reading_id', 'timestamp', 'sede_id', 'energia_total_kwh',
        'energia_comedor_kwh', 'energia_salones_kwh', 'energia_laboratorios_kwh',
        'energia_auditorios_kwh', 'energia_oficinas_kwh', 'co2_kg',
        'flag_ocupacion_fuera_rango', 'flag_agua_fuera_rango',
        'energia_total_calc_kwh', 'energia_total_inconsistente', 'dia_nombre'
    ]
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols]
    y = df['energia_total_kwh']
    
    split_idx = int(len(df) * (1 - test_size))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    
    print(f"📊 Train: {len(X_train):,} | Test: {len(X_test):,}")
    print(f"📅 Train: {df.timestamp.min()} to {df.timestamp.iloc[split_idx]}")
    print(f"📅 Test: {df.timestamp.iloc[split_idx]} to {df.timestamp.max()}")
    
    return X_train, X_test, y_train, y_test, feature_cols


def train_xgboost(X_train, y_train, X_test, y_test):
    print("\n🚀 Entrenando XGBoost...")
    
    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=8,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        n_jobs=-1,
        tree_method='hist',
        early_stopping_rounds=20
    )
    
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=50)
    return model


def evaluate_model(model, X_test, y_test, model_name="XGBoost"):
    print(f"\n📊 Evaluando {model_name}...")
    
    y_pred = model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    
    print("\n" + "=" * 60)
    print(f"MÉTRICAS - {model_name.upper()}")
    print("=" * 60)
    print(f"RMSE: {rmse:.4f} kWh")
    print(f"MAE:  {mae:.4f} kWh")
    print(f"R²:   {r2:.4f}")
    print(f"MAPE: {mape:.2f}%")
    print("=" * 60)
    
    return y_pred, {'rmse': rmse, 'mae': mae, 'r2': r2, 'mape': mape}


def plot_predictions(y_test, y_pred, model_name="XGBoost"):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    axes[0, 0].scatter(y_test, y_pred, alpha=0.3, s=1)
    axes[0, 0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    axes[0, 0].set_xlabel('Consumo Real (kWh)', fontsize=12)
    axes[0, 0].set_ylabel('Consumo Predicho (kWh)', fontsize=12)
    axes[0, 0].set_title(f'{model_name} - Predicciones vs. Reales', fontsize=14, fontweight='bold')
    axes[0, 0].grid(True, alpha=0.3)
    
    sample_size = min(2000, len(y_test))
    axes[0, 1].plot(range(sample_size), y_test.iloc[:sample_size].values, label='Real', alpha=0.7, linewidth=1)
    axes[0, 1].plot(range(sample_size), y_pred[:sample_size], label='Predicho', alpha=0.7, linewidth=1)
    axes[0, 1].set_xlabel('Índice', fontsize=12)
    axes[0, 1].set_ylabel('Consumo (kWh)', fontsize=12)
    axes[0, 1].set_title('Serie Temporal (primeros 2000)', fontsize=14, fontweight='bold')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    errors = y_pred - y_test
    axes[1, 0].hist(errors, bins=50, edgecolor='black', alpha=0.7)
    axes[1, 0].axvline(0, color='r', linestyle='--', linewidth=2)
    axes[1, 0].set_xlabel('Error de Predicción (kWh)', fontsize=12)
    axes[1, 0].set_ylabel('Frecuencia', fontsize=12)
    axes[1, 0].set_title('Distribución de Errores', fontsize=14, fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3)
    
    axes[1, 1].scatter(y_pred, errors, alpha=0.3, s=1)
    axes[1, 1].axhline(0, color='r', linestyle='--', linewidth=2)
    axes[1, 1].set_xlabel('Consumo Predicho (kWh)', fontsize=12)
    axes[1, 1].set_ylabel('Residuos (kWh)', fontsize=12)
    axes[1, 1].set_title('Gráfico de Residuos', fontsize=14, fontweight='bold')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f'predicciones_{model_name.lower()}.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico guardado: {OUTPUT_DIR / f'predicciones_{model_name.lower()}.png'}")


def feature_importance(model, feature_cols, model_name="XGBoost"):
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n🎯 TOP 15 FEATURES - {model_name.upper()}:")
    print("-" * 60)
    print(importance_df.head(15).to_string(index=False))
    
    plt.figure(figsize=(12, 10))
    top_features = importance_df.head(25)
    plt.barh(range(len(top_features)), top_features.importance, color='steelblue')
    plt.yticks(range(len(top_features)), top_features.feature, fontsize=10)
    plt.xlabel('Importancia', fontsize=12)
    plt.title(f'Top 25 Features - {model_name}', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f'feature_importance_{model_name.lower()}.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: {OUTPUT_DIR / f'feature_importance_{model_name.lower()}.png'}")
    
    return importance_df


def save_model(model, feature_cols, metrics, model_name="xgboost"):
    model_path = MODELS_DIR / f'modelo_{model_name}.joblib'
    joblib.dump({
        'model': model,
        'feature_cols': feature_cols,
        'metrics': metrics
    }, model_path)
    print(f"\n💾 Modelo guardado: {model_path}")


def main():
    print("\n" + "=" * 80)
    print("MODELO XGBOOST - PREDICCIÓN DE CONSUMO ENERGÉTICO UPTC")
    print("=" * 80)
    
    print("\n1️⃣ Cargando datos...")
    df = load_data()
    print(f"   Registros: {len(df):,}")
    
    print("\n2️⃣ Feature engineering...")
    df = feature_engineering(df)
    print(f"   Features: {len(df.columns)} columnas")
    
    print("\n3️⃣ Preparando datos...")
    X_train, X_test, y_train, y_test, feature_cols = prepare_data(df)
    
    print("\n4️⃣ Entrenando XGBoost...")
    model = train_xgboost(X_train, y_train, X_test, y_test)
    
    print("\n5️⃣ Evaluando modelo...")
    y_pred, metrics = evaluate_model(model, X_test, y_test)
    
    print("\n6️⃣ Visualizaciones...")
    plot_predictions(y_test, y_pred)
    importance_df = feature_importance(model, feature_cols)
    
    print("\n7️⃣ Guardando modelo...")
    save_model(model, feature_cols, metrics)
    
    print("\n" + "=" * 80)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 80)
    print("\n💡 El modelo está listo para hacer predicciones!")
    print("   Usa 'usar_modelo.py' para predecir consumos futuros")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

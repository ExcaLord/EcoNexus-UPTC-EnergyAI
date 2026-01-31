# Estructura del Proyecto - HackDay IA Minds 2026

## 📂 Estructura de Archivos

```
backend/
├── main.py                      # Pipeline de limpieza de datos
├── analisis_exploratorio.py    # Análisis y visualizaciones
├── modelo_xgboost.py           # Entrenamiento del modelo
├── usar_modelo.py              # Predicciones con modelo
├── dashboard.py                # Dashboard web interactivo
│
├── src/                        # Módulos principales
│   ├── __init__.py
│   ├── clean_data.py          # Limpieza y normalización
│   ├── load_data.py           # Carga de datos
│   └── validate_data.py       # Validación
│
├── data/
│   ├── raw/                   # Datos originales
│   │   ├── consumos_uptc.csv
│   │   └── sedes_uptc.csv
│   └── clean/                 # Datos procesados
│       └── consumos_uptc_clean.csv
│
├── models/                     # Modelos entrenados
│   └── modelo_xgboost.joblib
│
├── output/                     # Resultados y visualizaciones
│   ├── *.png                  # Gráficos generados
│   └── *.csv                  # Predicciones
│
└── _deprecated/               # Archivos obsoletos
    └── scripts/
```

## 🚀 Scripts Principales

### 1. main.py
Pipeline de limpieza de datos.

```bash
python main.py
```

### 2. analisis_exploratorio.py
Genera estadísticas y visualizaciones.

```bash
python analisis_exploratorio.py
```

### 3. modelo_xgboost.py
Entrena modelo de predicción.

```bash
python modelo_xgboost.py
```

### 4. usar_modelo.py
Hace predicciones con modelo entrenado.

```bash
python usar_modelo.py
```

### 5. dashboard.py
Dashboard web interactivo.

```bash
streamlit run dashboard.py
```

## 📊 Datos

### Entrada (raw/)
- `consumos_uptc.csv`: 275,387 registros de consumo (2018-2025)
- `sedes_uptc.csv`: Información de 4 sedes

### Salida (clean/)
- `consumos_uptc_clean.csv`: Datos normalizados y validados

## 🤖 Modelo

- **Algoritmo**: XGBoost
- **Métricas**: R²=0.9754, RMSE=0.44 kWh
- **Ubicación**: `models/modelo_xgboost.joblib`

## 📈 Visualizaciones

Ubicadas en `output/`:
- `consumo_temporal.png`
- `patron_horario.png`
- `heatmap_consumo.png`
- `comparacion_periodos.png`
- `predicciones_xgboost.png`
- `feature_importance_xgboost.png`

## 🗑️ Archivos Obsoletos

Movidos a `_deprecated/`:
- `modelo_prediccion.py` (Random Forest antiguo)
- Duplicados y archivos temporales

---

**Proyecto listo para HackDay 2026** ✅

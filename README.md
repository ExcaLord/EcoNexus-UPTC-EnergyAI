# ⚡ EcoNexus - IA Minds 2026
## Sistema Inteligente de Gestión Energética para la UPTC

### 📋 Descripción
Sistema avanzado de análisis predictivo y optimización del consumo energético para las 4 sedes de la Universidad Pedagógica y Tecnológica de Colombia (UPTC):
- **Tunja** (Sede Central) 🏛️ - 18,000 estudiantes
- **Duitama** 🏫 - 5,500 estudiantes  
- **Sogamoso** 🏢 - 6,000 estudiantes
- **Chiquinquirá** 🏬 - 2,000 estudiantes

### 🎯 Solución Implementada
✅ **Predicción con XGBoost** - Modelo con R² > 0.95 para predicción de consumo  
✅ **Explicabilidad (XAI)** - Análisis SHAP para interpretabilidad del modelo  
✅ **Detección de Anomalías** - Identificación automática de consumos atípicos  
✅ **Recomendaciones Personalizadas** - Sugerencias accionables por sede y sector  
✅ **Dashboard Interactivo** - Visualización en tiempo real con Streamlit  
✅ **Predicción por Sectores** - Análisis granular por área (comedores, laboratorios, auditorios, oficinas, salones)

### 📊 Datos Disponibles

#### Consumos UPTC (`consumos_uptc.csv`)
- **275,387 registros** de consumo horario (2018-2024)
- **Variables energéticas**: consumo total, por área (comedor, salones, laboratorios, auditorios, oficinas), potencia
- **Variables ambientales**: temperatura exterior, consumo de agua, CO2
- **Variables temporales**: hora, día, mes, periodo académico
- **Variables operacionales**: ocupación %, festivos, parciales, finales

#### Sedes UPTC (`sedes_uptc.csv`)
- Características de cada sede: área, estudiantes, empleados
- Distribución de espacios por tipo
- Infraestructura (residencias, laboratorios)

### 🛠️ Estructura del Proyecto

```
backend/
├── data/
│   ├── raw/                          # Datos originales
│   └── clean/                        # Datos procesados
├── models/
│   └── modelo_xgboost.joblib        # Modelo entrenado
├── output/
│   ├── predicciones_*.csv           # Predicciones generadas
│   ├── recomendaciones_personalizadas.csv
│   ├── anomalias.csv
│   ├── feature_importance_shap.csv
│   └── *.png                        # Gráficos XAI
├── src/
│   ├── load_data.py                 # Carga de datos
│   ├── clean_data.py                # Limpieza y normalización
│   └── validate_data.py             # Validación
├── modelo_xgboost.py                # Entrenamiento del modelo
├── predecir_fecha.py                # Predicciones por fecha
├── predecir_sectores.py             # Predicciones por sector
├── explicabilidad_xai.py            # Análisis SHAP
├── recomendaciones_sistema.py       # Generación de recomendaciones
├── config_recomendaciones.py        # Configuración de umbrales
├── dashboard.py                     # Dashboard interactivo
└── requirements.txt
```

### 🚀 Instalación y Uso

#### 1. Clonar repositorio
```bash
git clone https://github.com/tu-usuario/ia-minds-2026.git
cd ia-minds-2026/backend
```

#### 2. Crear entorno virtual e instalar dependencias
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Procesar y limpiar datos
```bash
python main.py
```

#### 4. Entrenar modelo XGBoost
```bash
python modelo_xgboost.py
```

#### 5. Generar análisis de explicabilidad (SHAP)
```bash
python explicabilidad_xai.py
```

#### 6. Generar recomendaciones personalizadas
```bash
python recomendaciones_sistema.py
```

#### 7. Lanzar dashboard interactivo
```bash
streamlit run dashboard.py
```

### 🔮 Generar Predicciones

#### Predicción por fecha específica
```bash
python predecir_fecha.py Tunja 2026-02-15 7
# Genera predicciones para Tunja desde el 15 de febrero por 7 días
```

#### Predicción por sectores
```bash
python predecir_sectores.py Duitama 2026-03-01 10
# Predice consumo desglosado por sector en Duitama
```

### 📊 Funcionalidades del Dashboard

#### Análisis Exploratorio
✅ Métricas principales (consumo total, promedio, CO₂, agua)  
✅ Consumo temporal por sede  
✅ Distribución por periodo académico  
✅ Patrones de consumo horario  
✅ Eficiencia energética (kWh/estudiante, kWh/m²)  

#### Predicciones Inteligentes
✅ Selector de sede y rango de fechas personalizado  
✅ Configuración de tarifa energética (conservadora, promedio, alta, personalizada)  
✅ Predicción de consumo diario y costo estimado  
✅ Desglose por sectores (comedores, salones, laboratorios, auditorios, oficinas)  
✅ Visualización interactiva con gráficos dinámicos  

#### Explicabilidad del Modelo (XAI)
✅ Top 10 factores más influyentes (SHAP values)  
✅ Gráficos de importancia global (Summary Plot)  
✅ Análisis de impacto individual (Beeswarm Plot)  
✅ Interpretación accesible para stakeholders no técnicos  

#### Recomendaciones Personalizadas
✅ Categorizadas por severidad (Crítico, Advertencia, Información)  
✅ Acciones concretas y accionables por sede  
✅ Estimación de ahorro potencial (kWh y COP)  
✅ Nivel de impacto y priorización  

#### Detección de Anomalías
✅ Identificación automática de consumos atípicos  
✅ Clasificación por tipo y severidad  
✅ Top 10 anomalías críticas con detalles  
✅ Cálculo de desperdicio y ahorro potencial

### 🎯 Resultados y Métricas

#### Modelo XGBoost
- **R² Score**: > 0.95 (alta precisión predictiva)
- **RMSE**: < 50 kWh (error bajo)
- **Features**: 20+ características engineeradas
- **Optimización**: GridSearchCV + libomp para rendimiento

#### Análisis de Impacto
- **Ahorro Potencial**: Identificado hasta 15% de reducción de consumo
- **Anomalías Detectadas**: Miles de eventos de consumo atípico
- **Recomendaciones**: Priorizadas por impacto económico y facilidad de implementación
- **Predicciones**: Hasta 30 días adelante con alta precisión

### 🔬 Tecnologías Utilizadas

- **Machine Learning**: XGBoost, Scikit-learn
- **Explicabilidad**: SHAP (SHapley Additive exPlanations)
- **Visualización**: Streamlit, Plotly, Matplotlib
- **Procesamiento**: Pandas, NumPy
- **Optimización**: GridSearchCV, libomp

### 💡 Cómo Funcionan las Recomendaciones

Las recomendaciones se generan mediante análisis basado en:

1. **SHAP Values**: Factores más influyentes del modelo
2. **Umbrales Configurables**: En `config_recomendaciones.json`
   - Pico de consumo: 1.5x promedio
   - Fin de semana: 0.5x promedio
   - Consumo nocturno: 0.3x promedio
3. **Análisis de Anomalías**: Patrones históricos atípicos
4. **Contexto Operacional**: Horarios, ocupación, periodos académicos

**Para personalizar las recomendaciones:**
Edita `backend/config_recomendaciones.json` y ajusta umbrales, costos y objetivos de ahorro.

### 📂 Archivos de Configuración

- `config_recomendaciones.json`: Umbrales y parámetros de recomendaciones
- `requirements.txt`: Dependencias del proyecto

### 🤝 Contribución

Este proyecto fue desarrollado para el HackDay IA Minds 2026 de la UPTC.

### 📄 Licencia

Proyecto académico - UPTC 2026

### 👥 Equipo

**EcoNexus Team** - IA Minds 2026

---

**⚡ Proyecto HackDay UPTC 2026 | Sistema Inteligente de Gestión Energética**

# ⚡ Sistema de Predicción de Consumo Energético UPTC
**HackDay IA Minds 2026**

## 🎯 Descripción del Proyecto

Sistema inteligente de análisis y predicción de consumo energético para las 4 sedes de la Universidad Pedagógica y Tecnológica de Colombia (UPTC), utilizando Machine Learning para optimizar recursos y reducir costos.

---

## 🏆 Características Principales

### 📊 Análisis de Datos
- **275,387 registros** históricos (2018-2025)
- **4 sedes**: Tunja, Duitama, Sogamoso, Chiquinquirá
- **5 sectores** por sede: Comedor, Salones, Laboratorios, Auditorios, Oficinas
- Análisis temporal por hora, día, mes y periodo académico

### 🤖 Modelo de Machine Learning
- **Algoritmo**: XGBoost (Gradient Boosting)
- **Precisión**: R² = 0.9754 (97.54% de precisión)
- **Error**: RMSE = 0.44 kWh
- **Features**: 40+ variables (temporales, ambientales, ocupación)

### 🔮 Predicciones Avanzadas
- Predicción por **sede** y **sector**
- Rango flexible: **1-30 días**
- Fechas personalizadas
- Desglose detallado por hora

### 💰 Análisis Económico
- Cálculo de costos en COP y USD
- **4 opciones de tarifa**: Conservadora (850), Promedio (1,050), Alta (1,200), Personalizada
- Comparación de costos por sector
- Identificación de oportunidades de ahorro

### 📈 Dashboard Interactivo
- Visualizaciones en tiempo real con Streamlit
- Filtros dinámicos por sede, fecha y periodo
- Gráficos interactivos con Plotly
- Exportación de datos a CSV

---

## 🚀 Instalación y Uso

### Prerequisitos
```bash
Python 3.10+
pip (gestor de paquetes)
```

### 1. Clonar el Repositorio
```bash
cd ia-minds-2026/backend
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# o
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar Pipeline de Datos
```bash
python main.py
```

### 5. Entrenar Modelo (opcional)
```bash
python modelo_xgboost.py
```

### 6. Lanzar Dashboard
```bash
streamlit run dashboard.py
```
Abre: http://localhost:8501

---

## 📁 Estructura del Proyecto

```
backend/
├── 📊 DATOS
│   ├── data/
│   │   ├── raw/                      # Datos originales
│   │   │   ├── consumos_uptc.csv     # 275,387 registros
│   │   │   └── sedes_uptc.csv        # Info de sedes
│   │   └── clean/                    # Datos procesados
│   │       └── consumos_uptc_clean.csv
│
├── 🤖 MODELOS
│   └── models/
│       └── modelo_xgboost.joblib     # Modelo entrenado
│
├── 📈 VISUALIZACIONES
│   └── output/
│       ├── *.png                     # Gráficos de análisis
│       └── *.csv                     # Predicciones
│
├── 🔧 SCRIPTS PRINCIPALES
│   ├── main.py                       # Pipeline de limpieza
│   ├── analisis_exploratorio.py     # EDA y visualizaciones
│   ├── modelo_xgboost.py            # Entrenamiento del modelo
│   ├── predecir_fecha.py            # Predicciones personalizadas
│   ├── predecir_sectores.py         # Predicciones por sector
│   ├── usar_modelo.py               # Predicciones rápidas
│   └── dashboard.py                 # Dashboard web
│
├── 📦 MÓDULOS
│   └── src/
│       ├── clean_data.py            # Limpieza de datos
│       ├── load_data.py             # Carga de datos
│       └── validate_data.py         # Validación
│
└── 📚 DOCUMENTACIÓN
    ├── README.md                    # Este archivo
    ├── ESTRUCTURA.md                # Documentación técnica
    └── requirements.txt             # Dependencias
```

---

## 💻 Uso del Sistema

### Opción 1: Dashboard Web (Recomendado)
```bash
streamlit run dashboard.py
```

**Funcionalidades:**
1. Visualización de datos históricos con filtros
2. Análisis de eficiencia por sede
3. Generación de predicciones interactivas
4. Desglose por sector automático
5. Cálculo de costos dinámico
6. Exportación de resultados

### Opción 2: Línea de Comandos

**Predicción por fecha:**
```bash
python predecir_fecha.py Tunja 2026-02-15 7
```

**Predicción por sector:**
```bash
python predecir_sectores.py Tunja 2026-02-15 7
```

**Predicción rápida (próxima semana):**
```bash
python usar_modelo.py
# Selecciona opción 1 y luego la sede
```

---

## 📊 Resultados y Métricas

### Modelo XGBoost
| Métrica | Valor |
|---------|-------|
| R² Score | 0.9754 |
| RMSE | 0.4429 kWh |
| MAE | 0.2150 kWh |
| MAPE | 10.65% |

### Distribución de Consumo (Ejemplo: Tunja)
| Sector | Consumo | Porcentaje |
|--------|---------|------------|
| 🔬 Laboratorios | 45.16% | Mayor consumo |
| 🏢 Oficinas | 24.03% | |
| 📚 Salones | 21.06% | |
| 🍽️ Comedor | 7.15% | |
| 🎭 Auditorios | 2.60% | Menor consumo |

### Ahorro Potencial
- Identificación de picos de consumo
- Optimización de horarios por sector
- Reducción estimada: **15-20%** del consumo total
- Ahorro anual estimado: **$30-50 millones COP**

---

## 🛠️ Tecnologías Utilizadas

### Machine Learning
- **XGBoost**: Modelo de predicción
- **scikit-learn**: Preprocesamiento y métricas
- **pandas**: Manipulación de datos
- **numpy**: Operaciones numéricas

### Visualización
- **Streamlit**: Dashboard web
- **Plotly**: Gráficos interactivos
- **Matplotlib**: Visualizaciones estáticas

### Desarrollo
- **Python 3.10+**: Lenguaje principal
- **joblib**: Serialización de modelos
- **pathlib**: Manejo de rutas

---

## 📈 Casos de Uso

### 1. Planificación Presupuestaria
- Estimar costos energéticos mensuales/anuales
- Presupuestar por sede y sector
- Comparar escenarios con diferentes tarifas

### 2. Optimización Operativa
- Identificar sectores de alto consumo
- Programar mantenimiento preventivo
- Ajustar horarios de operación

### 3. Toma de Decisiones
- Justificar inversiones en eficiencia
- Evaluar impacto de nuevas instalaciones
- Comparar consumo entre sedes

### 4. Sostenibilidad
- Reducir huella de carbono
- Cumplir metas de sostenibilidad
- Reportes ambientales

---

## 🎓 Equipo IA Minds 2026

**Proyecto desarrollado para HackDay UPTC 2026**

### Características Técnicas Destacadas
- ✅ Limpieza automática de 275K+ registros
- ✅ Modelo ML con 97.54% de precisión
- ✅ Dashboard interactivo en tiempo real
- ✅ Predicciones personalizadas por fecha
- ✅ Análisis por sector (5 categorías)
- ✅ Cálculo de costos con 4 tarifas
- ✅ Exportación de resultados
- ✅ Documentación completa

---

## 📞 Soporte

Para preguntas o problemas:
1. Revisar documentación en `/backend/ESTRUCTURA.md`
2. Verificar logs de ejecución
3. Consultar ejemplos en `/backend/output/`

---

## 📝 Licencia

Proyecto educativo - HackDay IA Minds 2026
Universidad Pedagógica y Tecnológica de Colombia (UPTC)

---

## 🚀 Próximos Pasos

### Mejoras Propuestas
- [ ] Predicción de alertas tempranas de sobreconsumo
- [ ] Integración con sensores IoT en tiempo real
- [ ] Sistema de recomendaciones automáticas
- [ ] API REST para integración con otros sistemas
- [ ] App móvil para monitoreo
- [ ] Dashboard ejecutivo para directivos

---

**¡Gracias por usar nuestro sistema! 🎉**

*HackDay IA Minds 2026 - Optimizando el futuro energético de la UPTC*

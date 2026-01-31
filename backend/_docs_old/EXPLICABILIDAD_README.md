# 🔬 Explicabilidad y Recomendaciones - IA Minds 2026

## 📊 ¿Cómo funcionan las recomendaciones?

Las recomendaciones se generan automáticamente basándose en:

### 1. **Análisis de Datos Reales**
   - Patrones históricos de consumo
   - Comparación entre sedes
   - Identificación de picos y anomalías

### 2. **Modelo de Machine Learning**
   - Feature Importance de XGBoost
   - Identifica factores más influyentes
   - **Factor #1: `potencia_total_kw`** (46.9% de importancia)
   - **Factor #2: `ocupacion_pct`** (4.8% de importancia)

### 3. **Umbrales Configurables**
Puedes personalizar las recomendaciones editando `config_recomendaciones.json`:

```json
{
  "umbrales": {
    "pico_consumo": 1.5,        // Detecta picos > 1.5x promedio
    "fin_semana": 0.5,           // Alerta si fin semana > 50% semana
    "nocturno": 0.3              // Alerta si nocturno > 30% promedio
  },
  "costos": {
    "kwh_cop": 1050             // Costo por kWh en Colombia
  },
  "ahorros": {
    "porcentaje_objetivo": 0.15  // Objetivo de ahorro del 15%
  }
}
```

## 🎯 Tipos de Recomendaciones

### 🔴 **Críticas** (Acción Inmediata)
- Picos de consumo excesivos
- Diferencias significativas entre sedes
- **Impacto:** Alto ahorro potencial

### 🟡 **Advertencias** (Acción Preventiva)
- Consumo fin de semana elevado
- Consumo nocturno innecesario
- Variabilidad alta
- **Impacto:** Medio ahorro potencial

### 🔵 **Informativas** (Monitoreo Continuo)
- Factor más influyente del modelo ML
- Métricas de eficiencia energética
- **Impacto:** Estratégico para largo plazo

## 💰 Cálculo de Ahorros

### **Picos de Consumo**
```python
ahorro_potencial = (consumo_hora_max - consumo_promedio) * 30
# Ejemplo: (15 kWh - 13 kWh) * 30 días = 60 kWh/mes
```

### **Fin de Semana**
```python
ahorro_potencial = (consumo_fin_semana - consumo_semana * 0.2) * 8
# Reducir a 20% del consumo semanal en fines de semana
```

### **Nocturno**
```python
ahorro_potencial = (consumo_nocturno - consumo_promedio * 0.1) * 8 * 30
# Reducir a 10% del promedio en horario nocturno (22:00-06:00)
```

## 🔄 Personalización de Recomendaciones

### Cambiar Umbrales
Para obtener recomendaciones diferentes:

1. Edita `backend/config_recomendaciones.json`
2. Modifica los valores según tu caso:
   - `pico_consumo`: 1.3 (más sensible) o 2.0 (menos sensible)
   - `fin_semana`: 0.3 (más estricto) o 0.7 (más permisivo)
   - `nocturno`: 0.2 (más estricto) o 0.4 (más permisivo)

3. Vuelve a generar:
```bash
python explicabilidad_simple.py
```

### Cambiar Costo de Energía
Si el costo del kWh cambia:

```json
{
  "costos": {
    "kwh_cop": 1200  // Nuevo costo
  }
}
```

### Objetivo de Ahorro
Para proyectos más o menos ambiciosos:

```json
{
  "ahorros": {
    "porcentaje_objetivo": 0.20  // 20% de ahorro
  }
}
```

## 📈 Feature Importance (Explicabilidad)

El modelo identifica que estos factores influyen más en el consumo:

| Rank | Feature | Importancia | Interpretación |
|------|---------|-------------|----------------|
| 1 | `potencia_total_kw` | 46.9% | **Factor clave**: Gestionar potencia total |
| 2 | `ocupacion_pct` | 4.8% | Ocupación impacta consumo |
| 3 | `hora` | 1.6% | Patrón horario relevante |
| 4 | `dia_semana` | 0.8% | Día de la semana importa |
| 5 | `es_festivo` | 0.5% | Festivos reducen consumo |

**Acción clave:** Priorizar gestión de `potencia_total_kw` para máximo impacto.

## 📊 Visualizar en el Dashboard

1. Inicia el dashboard:
```bash
streamlit run dashboard.py
```

2. Ve a la sección: **"🔬 Explicabilidad del Modelo (XAI)"**

3. Verás:
   - Top 10 Factores Más Influyentes
   - Gráfico de importancia de features
   - Interpretación automática

4. Sección: **"💡 Recomendaciones Personalizadas"**
   - Filtra por sede
   - Ver críticas, advertencias, informativas
   - Ahorro estimado en kWh y COP

## 🔄 Flujo de Trabajo

```
1. Entrenar modelo
   python modelo_xgboost.py

2. Generar recomendaciones
   python explicabilidad_simple.py

3. Visualizar en dashboard
   streamlit run dashboard.py

4. (Opcional) Ajustar config_recomendaciones.json

5. Regenerar recomendaciones
   python explicabilidad_simple.py
```

## 🎯 Archivos Generados

- `output/feature_importance_shap.csv` - Importancia numérica de características
- `output/shap_summary.png` - Gráfico de importancia
- `output/recomendaciones_personalizadas.csv` - Todas las recomendaciones con ahorros

## ⚙️ Agregar Nuevas Recomendaciones

Edita `explicabilidad_simple.py`:

```python
# En generar_recomendaciones_por_sede()

# Ejemplo: Detectar consumo en horario punta (18:00-20:00)
consumo_punta = df_sede[df_sede['hora'].between(18, 20)][consumo_col].mean()
if consumo_punta > consumo_promedio * 1.3:
    recomendaciones.append({
        'tipo': 'Advertencia',
        'categoria': 'Horario Punta',
        'descripcion': f'Consumo alto en horario punta',
        'accion': 'Redistribuir actividades a horario valle',
        'ahorro_kwh': (consumo_punta - consumo_promedio) * 60,
        'impacto': 'Medio'
    })
```

## 💡 Tips para la Presentación

1. **Destacar:** El modelo identifica que `potencia_total_kw` es el factor #1 (47%)
2. **Mostrar:** Ahorro total estimado: **$215M COP/año** (15%)
3. **Explicar:** Recomendaciones basadas en datos reales + ML
4. **Demostrar:** Sistema configurable y personalizable

---

**Desarrollado para HackDay IA Minds 2026 - UPTC**

# 🎯 SISTEMA DE RECOMENDACIONES - Guía Completa

## 📋 Resumen Ejecutivo

El sistema genera **recomendaciones personalizadas** basadas en:
1. **Análisis de datos reales** de consumo histórico
2. **Feature Importance** del modelo XGBoost (explicabilidad)
3. **Umbrales configurables** que TÚ defines

## 🔍 ¿En base a QUÉ se hacen las recomendaciones?

### 1. Análisis de Patrones Reales

#### **Picos de Consumo** (Crítico)
```python
# ¿Cómo se detecta?
consumo_hora_max = df.groupby('hora')['energia_total_kwh'].mean().max()
consumo_promedio = df['energia_total_kwh'].mean()

if consumo_hora_max > consumo_promedio * umbral_pico:  # umbral_pico = 1.5
    # ¡Hay un pico de consumo!
    ahorro = (consumo_hora_max - consumo_promedio) * 30 días
```

**Ejemplo Real:**
- Sogamoso: Pico a las 10:00 hrs → 11.82 kWh (promedio: 7.19 kWh)
- Excede umbral: 11.82 > 7.19 * 1.5 ✅
- **Recomendación:** "Redistribuir actividades fuera del horario pico"
- **Ahorro:** 139 kWh/mes

#### **Consumo Fin de Semana** (Advertencia)
```python
# ¿Cómo se detecta?
consumo_fin_semana = df[df['es_fin_semana'] == 1]['energia_total_kwh'].mean()
consumo_semana = df[df['es_fin_semana'] == 0]['energia_total_kwh'].mean()

if consumo_fin_semana > consumo_semana * umbral_fin_semana:  # umbral = 0.5
    # ¡Consumo fin de semana muy alto!
    ahorro = (consumo_fin_semana - consumo_semana * 0.2) * 8 días/mes
```

**Ejemplo Real:**
- Duitama: Fin de semana 4.52 kWh vs Semana 8.11 kWh
- Excede umbral: 4.52 > 8.11 * 0.5 ✅
- **Recomendación:** "Implementar apagado automático de equipos"
- **Ahorro:** 23 kWh/mes

#### **Consumo Nocturno** (Advertencia)
```python
# ¿Cómo se detecta?
consumo_nocturno = df[df['hora'].between(22, 6)]['energia_total_kwh'].mean()

if consumo_nocturno > consumo_promedio * umbral_nocturno:  # umbral = 0.3
    # ¡Consumo nocturno innecesario!
    ahorro = (consumo_nocturno - consumo_promedio * 0.1) * 8 hrs * 30 días
```

### 2. Machine Learning (Feature Importance)

El modelo XGBoost analiza **34 características** y determina cuáles son más importantes:

```
Top Features (importancia):
1. potencia_total_kw     → 46.9%  ⭐⭐⭐⭐⭐
2. ocupacion_pct         →  4.8%  ⭐⭐
3. hora                  →  1.6%  ⭐
4. dia_semana            →  0.8%  
5. es_festivo            →  0.5%
```

**¿Qué significa?**
- `potencia_total_kw` es **10 veces más influyente** que el segundo factor
- Cambiar la potencia tiene el **mayor impacto** en el consumo
- **Recomendación automática:** "Priorizar gestión de potencia_total_kw"

### 3. Comparación Entre Sedes

```python
# ¿Cómo se compara?
consumo_total = df.groupby('sede')['energia_total_kwh'].sum()
sede_mayor = consumo_total.idxmax()  # Sogamoso
sede_menor = consumo_total.idxmin()  # Chiquinquirá
ratio = consumo_total[sede_mayor] / consumo_total[sede_menor]  # 3.0x
```

**Ejemplo Real:**
- Sogamoso: 125,456 kWh totales
- Chiquinquirá: 42,152 kWh totales
- Ratio: **3.0x más consumo**
- **Recomendación:** "Benchmarking de mejores prácticas de Chiquinquirá"

## 🎛️ ¿Cómo obtengo recomendaciones DIFERENTES?

### Opción 1: Cambiar Umbrales

Edita `backend/config_recomendaciones.json`:

```json
{
  "umbrales": {
    "pico_consumo": 2.0,      // Antes: 1.5 → Ahora menos estricto
    "fin_semana": 0.3,         // Antes: 0.5 → Ahora MÁS estricto
    "nocturno": 0.2            // Antes: 0.3 → Ahora MÁS estricto
  }
}
```

**Resultado:**
- Menos recomendaciones de "Picos de Consumo" (menos sensible)
- Más recomendaciones de "Fin de Semana" (más sensible)
- Más recomendaciones de "Consumo Nocturno" (más sensible)

### Opción 2: Cambiar Costo kWh

```json
{
  "costos": {
    "kwh_cop": 1200  // Antes: 1050 → Ahorros en COP aumentan
  }
}
```

**Resultado:**
- Mismas recomendaciones en kWh
- Ahorros en COP cambian: 100 kWh × $1,200 = $120,000

### Opción 3: Cambiar Objetivo de Ahorro

```json
{
  "ahorros": {
    "porcentaje_objetivo": 0.20  // Antes: 0.15 (15%) → Ahora 20%
  }
}
```

**Resultado:**
- Recomendación "Potencial de Ahorro" cambia:
  - Antes: "Ahorro de 15% = 205,398 kWh/año"
  - Ahora: "Ahorro de 20% = 273,864 kWh/año"

### Opción 4: Agregar Nuevas Reglas

Edita `backend/explicabilidad_simple.py` función `generar_recomendaciones_por_sede()`:

```python
# Nueva regla: Detectar consumo excesivo en días laborables
consumo_laborable = df_sede[df_sede['dia_semana'] < 5]['energia_total_kwh'].mean()
if consumo_laborable > 10:  # Tu umbral personalizado
    recomendaciones.append({
        'tipo': 'Advertencia',
        'categoria': 'Consumo Laborable Alto',
        'descripcion': f'Consumo promedio entre semana: {consumo_laborable:.2f} kWh',
        'accion': 'Implementar horarios de uso eficiente de equipos',
        'ahorro_kwh': (consumo_laborable - 8) * 20,  # Tu fórmula
        'impacto': 'Medio'
    })
```

## 🔄 Flujo Completo

```bash
# 1. Modifica configuración (opcional)
nano backend/config_recomendaciones.json

# 2. Regenera recomendaciones
cd backend
python explicabilidad_simple.py

# 3. Visualiza en dashboard
streamlit run dashboard.py
```

## 📊 Ejemplos de Diferentes Configuraciones

### Configuración "Estricta" (Más recomendaciones)
```json
{
  "umbrales": {
    "pico_consumo": 1.2,    // Muy sensible
    "fin_semana": 0.3,       // Muy estricto
    "nocturno": 0.2          // Muy estricto
  }
}
```
**Resultado:** 8-10 recomendaciones por sede

### Configuración "Permisiva" (Menos recomendaciones)
```json
{
  "umbrales": {
    "pico_consumo": 2.5,    // Poco sensible
    "fin_semana": 0.8,       // Muy permisivo
    "nocturno": 0.5          // Muy permisivo
  }
}
```
**Resultado:** 3-5 recomendaciones por sede

### Configuración "Balanceada" (Actual)
```json
{
  "umbrales": {
    "pico_consumo": 1.5,
    "fin_semana": 0.5,
    "nocturno": 0.3
  }
}
```
**Resultado:** 5-7 recomendaciones por sede

## 💡 Tips para Personalización

### Para detectar MÁS problemas:
- **Reduce** los valores de umbrales
- Ejemplo: `pico_consumo: 1.2` (más estricto que 1.5)

### Para detectar MENOS problemas:
- **Aumenta** los valores de umbrales
- Ejemplo: `pico_consumo: 2.0` (menos estricto que 1.5)

### Para enfocar en ahorros económicos:
- **Aumenta** `kwh_cop` si tu tarifa es mayor
- **Aumenta** `porcentaje_objetivo` para proyectos ambiciosos

## 🎯 Resumen Visual

```
DATOS REALES → UMBRALES → RECOMENDACIONES
    ↓            ↓              ↓
  Historico   Config     Acciones
  consumo     .json      concretas
    +            +            +
MODELO ML    FEATURE    PRIORIZACION
    ↓         IMPORT.        ↓
 XGBoost   potencia_kw   Alto/Medio
```

## 📈 Métricas Actuales del Sistema

- **Total recomendaciones generadas:** 19 (4 sedes + generales)
- **Recomendaciones críticas:** 5 (26%)
- **Recomendaciones advertencia:** 6 (32%)
- **Recomendaciones informativas:** 8 (42%)
- **Ahorro total estimado:** $215,667,814 COP/año (15%)
- **Factor más influyente:** potencia_total_kw (47%)

---

**¿Preguntas frecuentes?**

**P: ¿Por qué algunas sedes no tienen ciertas recomendaciones?**
R: Porque no superan los umbrales definidos. Chiquinquirá es eficiente y no tiene consumo fin de semana alto.

**P: ¿Puedo agregar recomendaciones basadas en temperatura?**
R: Sí, el código ya detecta correlación temperatura-consumo si es > 0.5

**P: ¿Cómo sé qué umbral usar?**
R: Empieza con valores actuales (1.5, 0.5, 0.3), luego ajusta según resultados.

---

**Desarrollado para IA Minds 2026 - HackDay UPTC** 🚀

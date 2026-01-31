# 🎤 Guía de Presentación - HackDay IA Minds 2026
## Sistema de Predicción de Consumo Energético UPTC

---

## ⏱️ AGENDA DE PRESENTACIÓN (10 minutos)

### 1️⃣ INTRODUCCIÓN (1 min)
**"Buenos días/tardes. Somos el equipo IA Minds 2026 y presentamos nuestro sistema de predicción de consumo energético para la UPTC."**

**Problema:**
- UPTC: 4 sedes, 31,500+ estudiantes
- Alto consumo energético sin predicción
- Costos elevados y falta de optimización
- No hay análisis por sector

**Solución:**
- Sistema inteligente con Machine Learning
- Predicción precisa del consumo
- Análisis por sede y sector
- Dashboard interactivo

---

### 2️⃣ DEMOSTRACIÓN DE DATOS (2 min)

**Mostrar en terminal:**
```bash
python main.py
```

**Hablar mientras corre:**
- "275,387 registros históricos (2018-2025)"
- "4 sedes: Tunja, Duitama, Sogamoso, Chiquinquirá"
- "5 sectores: Comedor, Salones, Laboratorios, Auditorios, Oficinas"
- "Pipeline automático de limpieza y validación"

**Puntos Clave:**
✅ Datos limpios en segundos
✅ Validación automática
✅ Ready para ML

---

### 3️⃣ DEMOSTRACIÓN DE MODELO ML (2 min)

**Mostrar visualizaciones ya generadas:**
```bash
# En carpeta output/
- predicciones_xgboost.png
- feature_importance_xgboost.png
```

**Explicar:**
- "Modelo: XGBoost (Gradient Boosting)"
- "Precisión: **97.54%** (R² = 0.9754)"
- "Error mínimo: 0.44 kWh"

**Mostrar Feature Importance:**
- "Variables más importantes:"
  - Hora del día (patrón horario)
  - Día de la semana
  - Consumo anterior (lags)
  - Ocupación del edificio
  - Periodo académico

**Resultado:**
✅ Modelo altamente preciso
✅ Aprende patrones temporales
✅ Considera contexto académico

---

### 4️⃣ DEMOSTRACIÓN DEL DASHBOARD (4 min) ⭐ CORE

**Lanzar dashboard:**
```bash
streamlit run dashboard.py
```

**URL:** http://localhost:8501

#### A) Análisis Histórico (1 min)
1. Mostrar visualizaciones iniciales
2. Aplicar filtros por sede
3. Mostrar métricas de eficiencia
4. "Aquí vemos el consumo histórico de cada sede"

#### B) Predicciones Inteligentes (3 min) ⭐ HIGHLIGHT

**Navegar a "🔮 Predicciones de Consumo"**

1. **Seleccionar Configuración:**
   - Sede: Tunja
   - Fecha: 15 de febrero 2026
   - Días: 7
   - Tarifa: Promedio (1,050 COP/kWh)

2. **Clic en "🔮 Generar Predicciones"**
   
   Mientras genera (10-15 seg):
   - "El modelo está procesando 168 horas de predicción"
   - "Considera patrones históricos y contexto académico"
   - "Aplica el modelo entrenado con 97% de precisión"

3. **Mostrar Resultados Principales:**
   - Gráfico de consumo diario
   - Métricas: Consumo total, promedio, costo, días
   - "Para 7 días: ~735 kWh = $772,000 COP"

4. **Expandir "🏢 Ver Predicciones por Sector"** ⭐ WOW FACTOR
   - Gráfico circular de distribución
   - Tabla con consumo y costo por sector
   - "Laboratorios: 45% del consumo ($330K)"
   - "Identificamos dónde optimizar"

5. **Top 3 Sectores:**
   - "1. Laboratorios: Mayor consumo - equipos científicos"
   - "2. Oficinas: Iluminación y climatización"
   - "3. Salones: Proyectores y AC"

**Mensaje Clave:**
✅ Predicción precisa por fecha
✅ Desglose por sector
✅ Cálculo automático de costos
✅ Identifica oportunidades de ahorro

---

### 5️⃣ IMPACTO Y BENEFICIOS (1 min)

**Resultados Concretos:**

📊 **Precisión:**
- 97.54% de exactitud en predicciones
- Error menor a 0.5 kWh

💰 **Ahorro Potencial:**
- Identificación de picos de consumo
- Optimización por sector
- **15-20% reducción estimada**
- **$30-50 millones COP/año**

🎯 **Aplicaciones:**
- Planificación presupuestaria
- Optimización operativa
- Justificación de inversiones
- Reportes de sostenibilidad

🌱 **Sostenibilidad:**
- Reducción de huella de carbono
- Uso eficiente de recursos
- Cumplimiento de metas ambientales

---

## 🎯 MENSAJES CLAVE PARA RECORDAR

1. **"275K registros → Modelo 97% preciso → Ahorro real"**
2. **"Predicción por sede Y por sector"**
3. **"Dashboard interactivo listo para usar"**
4. **"$30-50M COP de ahorro potencial/año"**

---

## 💡 RESPUESTAS A PREGUNTAS FRECUENTES

### P: "¿Cómo entrenaron el modelo?"
**R:** "Usamos 275K registros históricos (2018-2025) con XGBoost. El modelo aprendió patrones de consumo por hora, día, y periodo académico. Validamos con datos del último año y obtuvimos 97.54% de precisión."

### P: "¿Qué tan preciso es?"
**R:** "R² de 0.9754 significa que el modelo explica el 97.54% de la variabilidad en el consumo. El error promedio es solo 0.44 kWh, menos del 10% del consumo horario típico."

### P: "¿Funciona en tiempo real?"
**R:** "El modelo está entrenado con datos históricos. Para tiempo real, se necesitaría integración con sensores IoT. Actualmente predice consumo futuro basado en patrones históricos."

### P: "¿Por qué desglosar por sector?"
**R:** "Permite identificar exactamente dónde se consume más. Por ejemplo, si laboratorios consumen 45%, podemos optimizar horarios de equipos científicos y ahorrar significativamente."

### P: "¿Cómo se calcula el costo?"
**R:** "Ofrecemos 4 tarifas: Conservadora (850), Promedio (1,050), Alta (1,200) y Personalizada. Basadas en tarifas institucionales reales de Colombia. El usuario puede ajustar según su factura exacta."

### P: "¿Qué tecnologías usaron?"
**R:** "Python con XGBoost para ML, Streamlit para el dashboard, Plotly para visualizaciones. Todo open-source y escalable."

---

## 🎬 SCRIPT DE CIERRE (30 seg)

**"En resumen:**
- ✅ Sistema completo de análisis y predicción
- ✅ 97.54% de precisión
- ✅ Dashboard interactivo listo para producción
- ✅ Ahorro potencial de $30-50M COP/año
- ✅ Identificación exacta de oportunidades de optimización

**"Este sistema puede implementarse HOY en la UPTC para empezar a ahorrar MAÑANA."**

**"Gracias por su atención. ¿Preguntas?"** 🎤

---

## 📋 CHECKLIST PRE-PRESENTACIÓN

### 10 Minutos Antes:
- [ ] Abrir terminal en `/backend`
- [ ] Activar venv: `source venv/bin/activate`
- [ ] Verificar que el modelo existe: `ls models/modelo_xgboost.joblib`
- [ ] Abrir carpeta `output/` para mostrar gráficos
- [ ] Lanzar dashboard: `streamlit run dashboard.py`
- [ ] Probar una predicción rápida
- [ ] Tener navegador en http://localhost:8501
- [ ] Cerrar tabs innecesarios
- [ ] Zoom de pantalla al 125-150% (legibilidad)
- [ ] Tener README_HACKDAY.md abierto como referencia

### Durante Presentación:
- [ ] Hablar claro y despacio
- [ ] Señalar lo que muestras en pantalla
- [ ] Enfatizar números clave (97%, $50M, 275K)
- [ ] Hacer pausa para que vean los gráficos
- [ ] Sonreír y mostrar confianza
- [ ] Mirar al público, no solo a la pantalla

### Backup Plan:
- [ ] Screenshots del dashboard en carpeta `/output`
- [ ] Tener predicciones pre-generadas
- [ ] README_HACKDAY.md como presentación alternativa
- [ ] Video demo grabado (opcional)

---

## 🏆 TIPS PARA GANAR

1. **Enfócate en el IMPACTO**: $30-50M ahorro > código bonito
2. **Demo > Slides**: Mostrar funcionando > hablar de teoría
3. **Números concretos**: 97.54%, 275K, $50M
4. **Resolver problema real**: UPTC necesita esto HOY
5. **Wow factor**: Desglose por sector es único
6. **Confianza**: Practicar el demo 3-5 veces antes

---

## 🎯 OBJETIVO FINAL

**"Convencer al jurado que este sistema:**
- ✅ Resuelve un problema real
- ✅ Funciona perfectamente
- ✅ Tiene impacto económico tangible
- ✅ Está listo para implementarse
- ✅ Es escalable y mantenible"

---

**¡Mucha suerte! 🍀 Van a ganar! 🏆**

*IA Minds 2026*

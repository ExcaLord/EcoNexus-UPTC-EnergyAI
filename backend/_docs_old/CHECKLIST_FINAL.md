# ✅ CHECKLIST FINAL - HACKDAY IA MINDS 2026

## 🎯 ANTES DE LA PRESENTACIÓN

### 📋 15 Minutos Antes

- [ ] **Ejecutar verificación:**
  ```bash
  cd /Users/exca/Develope/ia-minds-2026/backend
  ./verificar_proyecto.sh
  ```
  ✅ Debe mostrar: "TODO LISTO PARA LA PRESENTACIÓN"

- [ ] **Activar entorno virtual:**
  ```bash
  source venv/bin/activate
  ```

- [ ] **Lanzar dashboard:**
  ```bash
  streamlit run dashboard.py
  ```
  ✅ Debe abrir en http://localhost:8501

- [ ] **Probar una predicción rápida:**
  - Sede: Tunja
  - Fecha: Hoy + 1 día
  - Días: 7
  - Tarifa: Promedio
  - Clic "Generar Predicciones"
  ✅ Debe generar sin errores en ~15 segundos

- [ ] **Verificar desglose por sector:**
  - Expandir "🏢 Ver Predicciones por Sector"
  ✅ Debe mostrar gráfico y tabla

---

## 🖥️ CONFIGURACIÓN DE PANTALLA

- [ ] Cerrar todas las tabs innecesarias
- [ ] Zoom del navegador: 125-150%
- [ ] Modo oscuro/claro según preferencia
- [ ] Pantalla completa del navegador (F11)
- [ ] Cerrar notificaciones del sistema
- [ ] Silenciar teléfono

---

## 📁 ARCHIVOS ABIERTOS

Tener listos para mostrar:

- [ ] Terminal en `/backend`
- [ ] Navegador en http://localhost:8501
- [ ] Carpeta `output/` abierta (para screenshots backup)
- [ ] `PRESENTACION_GUIA.md` en editor
- [ ] `README_HACKDAY.md` como referencia

---

## 🎤 ESTRUCTURA DE PRESENTACIÓN (10 min)

### ⏱️ Minuto 1: Introducción
- [ ] Presentar equipo
- [ ] Problema: "UPTC sin predicción de consumo"
- [ ] Solución: "Sistema ML con 97% precisión"

### ⏱️ Minutos 2-3: Datos
- [ ] Ejecutar `python main.py` (mientras hablas)
- [ ] "275K registros, 4 sedes, 5 sectores"
- [ ] Mostrar CSV limpio

### ⏱️ Minuto 4: Modelo
- [ ] Mostrar `predicciones_xgboost.png`
- [ ] Mostrar `feature_importance_xgboost.png`
- [ ] "97.54% de precisión, error 0.44 kWh"

### ⏱️ Minutos 5-8: DEMO DASHBOARD ⭐
- [ ] Navegar a "Predicciones"
- [ ] Configurar: Tunja, fecha, 7 días, tarifa
- [ ] Generar predicciones
- [ ] Mostrar gráfico y métricas
- [ ] **WOW MOMENT**: Expandir "Ver por Sector"
- [ ] Mostrar top 3 sectores
- [ ] "Laboratorios: 45%, $330K"

### ⏱️ Minutos 9-10: Impacto
- [ ] "Ahorro: $30-50M COP/año"
- [ ] "Listo para implementar HOY"
- [ ] Preguntas

---

## 💬 MENSAJES CLAVE

Memorizar y repetir:

1. **"275 mil registros"**
2. **"97.54% de precisión"**
3. **"Desglose por sector"**
4. **"$30-50 millones de ahorro anual"**

---

## 🆘 PLAN DE CONTINGENCIA

### Si el dashboard falla:
- [ ] Usar screenshots en `/output`
- [ ] Mostrar predicciones pre-generadas CSV
- [ ] Explicar con README_HACKDAY.md

### Si hay preguntas técnicas:
- [ ] "Modelo: XGBoost con 40+ features"
- [ ] "Datos: 2018-2025, hora por hora"
- [ ] "Tech: Python, Streamlit, Plotly"

### Si preguntan por tiempo real:
- [ ] "Actualmente usa histórico"
- [ ] "Próximo paso: integrar IoT"

---

## 📊 NÚMEROS CLAVE A MENCIONAR

| Métrica | Valor |
|---------|-------|
| Registros | 275,387 |
| Precisión | 97.54% |
| Error | 0.44 kWh |
| Sedes | 4 |
| Sectores | 5 |
| Ahorro estimado | $30-50M COP/año |

---

## 🎯 OBJETIVOS DE LA DEMO

Al final, el jurado debe entender:

- [x] Problema real de la UPTC
- [x] Solución técnica robusta
- [x] Sistema funcional (no prototipo)
- [x] Impacto económico tangible
- [x] Listo para implementar

---

## 🏆 TIPS FINALES

### ✅ HACER:
- Hablar con confianza
- Señalar lo que muestras
- Hacer pausas para que vean
- Sonreír
- Mirar al jurado
- Enfatizar números clave

### ❌ NO HACER:
- Leer del código
- Hablar muy rápido
- Disculparse por "bugs"
- Entrar en detalles técnicos irrelevantes
- Pasar más de 10 minutos

---

## 📞 CONTACTOS DE EMERGENCIA

Si hay problemas técnicos durante setup:
- Verificar venv activado
- Reiniciar dashboard
- Usar plan B (screenshots)

---

## 🎬 CIERRE PERFECTO

**Últimas palabras:**

_"En resumen: sistema completo, 97% de precisión, $50 millones de ahorro potencial. Este sistema puede implementarse HOY en la UPTC para empezar a ahorrar MAÑANA. Gracias."_

🎤 **Mic drop** 🎤

---

## ✅ VERIFICACIÓN FINAL

Marcar cuando esté listo:

- [ ] ✅ Verificación técnica pasada (20/20)
- [ ] ✅ Dashboard funcionando
- [ ] ✅ Predicción de prueba exitosa
- [ ] ✅ Pantalla configurada
- [ ] ✅ Archivos abiertos
- [ ] ✅ Mensajes clave memorizados
- [ ] ✅ Plan B preparado
- [ ] ✅ Confianza al 100%

---

## 🎉 ¡A GANAR!

**Remember:**
- Ustedes crearon algo increíble
- El sistema FUNCIONA
- Tienen impacto REAL
- Están PREPARADOS

**¡MUCHA SUERTE! 🍀**

---

**IA Minds 2026** | HackDay UPTC | Sistema de Predicción Energética

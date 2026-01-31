# 💡 Sistema de Recomendaciones Personalizadas

## 📋 ¿Cómo Funciona?

El sistema analiza los datos históricos de consumo energético y genera recomendaciones accionables basadas en **reglas configurables**.

## 🔍 Análisis que Realiza

### Por Sede (Individual):

1. **🔴 Picos de Consumo** (Crítico)
   - Detecta horarios con consumo > 1.5x el promedio
   - Calcula ahorro redistribuyendo cargas
   - Ejemplo: Consumo alto a las 10:00 hrs → Ahorro $62K-$150K/mes

2. **🟡 Consumo Fin de Semana** (Advertencia)
   - Compara consumo sábado/domingo vs entre semana
   - Si fin de semana > 50% del consumo normal → Recomendación
   - Acción: Apagado automático equipos no esenciales

3. **🟡 Consumo Nocturno** (Advertencia)
   - Analiza consumo 22:00-06:00 hrs
   - Si > 30% del promedio → Recomendación
   - Acción: Sensores de movimiento y apagado automático

4. **🔵 Consumo por Sector** (Información)
   - Compara laboratorios vs salones
   - Si laboratorios > 2x salones → Auditoría recomendada
   - Acción: Actualizar equipos a versiones eficientes

5. **🔵 Climatización** (Información)
   - Si temperatura promedio > 20°C → Optimización
   - Acción: Temperatura 24°C, mantenimiento trimestral

### General (Todas las Sedes):

1. **🔴 Benchmarking** (Crítico)
   - Compara consumo entre sedes
   - Identifica mejores prácticas
   - Ejemplo: Replicar prácticas de Chiquinquirá en Sogamoso

2. **🟡 Ocupación vs Consumo** (Advertencia)
   - Si ocupación < 50% → Zonificación
   - Acción: Apagar áreas no utilizadas

3. **🔵 Potencial Global** (Información)
   - Calcula ahorro total: 15-20% del consumo
   - Proyección anual: $27-36M COP

4. **🔵 Certificación ISO 50001** (Información)
   - Implementar sistema de gestión energética
   - ROI positivo en 2-3 años

---

## ⚙️ Personalización

### Archivo: `config_recomendaciones.py`

Puedes modificar los umbrales y reglas según tus necesidades:

#### 1. **Cambiar Tarifa Eléctrica:**
```python
TARIFA_COP_KWH = 1200  # En vez de 1050
```

#### 2. **Ajustar Umbrales de Picos:**
```python
UMBRALES_PICOS = {
    'multiplicador': 2.0,  # Más estricto (antes 1.5)
    'descripcion': 'Si consumo máximo > promedio * 2.0'
}
```

#### 3. **Modificar Consumo Fin de Semana:**
```python
UMBRALES_FIN_SEMANA = {
    'ratio_minimo': 0.4,  # Más sensible (antes 0.5)
    'ratio_objetivo': 0.2,  # Más ambicioso (antes 0.3)
}
```

#### 4. **Cambiar Horario Nocturno:**
```python
UMBRALES_NOCTURNO = {
    'multiplicador': 0.2,  # Más estricto (antes 0.3)
    'hora_inicio': 20,     # Empieza antes (antes 22)
    'hora_fin': 7,         # Termina después (antes 6)
}
```

#### 5. **Ajustar Laboratorios vs Salones:**
```python
UMBRALES_SECTORES = {
    'ratio_laboratorios_salones': 1.8,  # Más sensible (antes 2.0)
}
```

#### 6. **Cambiar Ahorros Estimados:**
```python
AHORROS_ESTIMADOS = {
    'climatizacion_min': 700000,  # Más optimista (antes 500K)
    'climatizacion_max': 1500000, # Más optimista (antes 1M)
    'ahorro_global_min_pct': 0.20,  # Más optimista (antes 15%)
    'ahorro_global_max_pct': 0.30,  # Más optimista (antes 20%)
}
```

#### 7. **Personalizar Mensajes:**
```python
CATEGORIAS = {
    'picos_consumo': {
        'tipo': 'Crítico',
        'nombre': 'Picos de Consumo - URGENTE',  # Cambiar título
        'accion': 'ACCIÓN INMEDIATA: Redistribuir cargas'  # Cambiar acción
    }
}
```

---

## 🚀 Generar Nuevas Recomendaciones

Después de modificar `config_recomendaciones.py`:

```bash
cd backend
source venv/bin/activate
python recomendaciones_sistema.py
```

Esto generará un nuevo archivo:
```
output/recomendaciones_personalizadas.csv
```

El dashboard lo cargará automáticamente.

---

## 📊 Estructura de Datos

### Entrada:
- `data/clean/consumos_uptc_clean.csv`
- Columnas necesarias:
  - `sede`, `hora`, `es_fin_semana`
  - `energia_total_kwh`, `energia_laboratorios_kwh`, `energia_salones_kwh`
  - `ocupacion_pct`, `temperatura_exterior_c`

### Salida:
- `output/recomendaciones_personalizadas.csv`
- Columnas:
  - `sede`, `tipo`, `categoria`
  - `descripcion`, `accion`, `ahorro_estimado_cop`

---

## 💡 Ejemplos de Personalización

### Caso 1: Universidad con Tarifa Diferencial
```python
# Tarifa pico: $1500 COP/kWh
# Tarifa valle: $800 COP/kWh
TARIFA_COP_KWH = 1150  # Promedio ponderado
```

### Caso 2: Universidad con Horario Extendido
```python
UMBRALES_NOCTURNO = {
    'hora_inicio': 23,  # Cierra más tarde
    'hora_fin': 5,      # Abre más temprano
}
```

### Caso 3: Universidad con Muchos Laboratorios
```python
UMBRALES_SECTORES = {
    'ratio_laboratorios_salones': 3.0,  # Más tolerante
}
```

### Caso 4: Universidad Buscando ISO 50001
```python
# Agregar más recomendaciones de certificación
CATEGORIAS['iso_preparacion'] = {
    'tipo': 'Crítico',
    'nombre': 'Preparación ISO 50001',
    'accion': 'Implementar mediciones continuas y auditorías mensuales',
}
```

---

## 🎯 Mejores Prácticas

1. **Ajusta gradualmente**: Empieza con umbrales conservadores y hazlos más estrictos
2. **Valida con datos reales**: Compara ahorros estimados con implementaciones reales
3. **Documenta cambios**: Anota por qué modificaste cada umbral
4. **Regenera periódicamente**: Ejecuta cada mes con datos actualizados
5. **Personaliza por sede**: Usa `RECOMENDACIONES_PERSONALIZADAS` para ajustes específicos

---

## 📈 Métricas de Éxito

El sistema considera una recomendación exitosa cuando:
- ✅ Es accionable (paso concreto)
- ✅ Tiene ahorro cuantificable
- ✅ Es realista de implementar
- ✅ Está basada en datos reales

---

## 🆘 Soporte

Si necesitas ayuda:
1. Revisa los ejemplos en `config_recomendaciones.py`
2. Consulta los logs de ejecución
3. Verifica que tus datos tienen las columnas necesarias
4. Prueba con umbrales más permisivos primero

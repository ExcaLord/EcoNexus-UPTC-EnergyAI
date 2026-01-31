"""
Configuración para el Sistema de Recomendaciones
Modifica estos parámetros para personalizar las recomendaciones
"""

TARIFA_COP_KWH = 1050

UMBRALES_PICOS = {
    'multiplicador': 1.5,
    'descripcion': 'Si consumo máximo por hora > promedio * 1.5 → Recomendación Crítica'
}

UMBRALES_FIN_SEMANA = {
    'ratio_minimo': 0.5,
    'ratio_objetivo': 0.3,
    'descripcion': 'Si consumo fin de semana > 50% del consumo entre semana → Recomendación'
}

UMBRALES_NOCTURNO = {
    'multiplicador': 0.3,
    'objetivo': 0.15,
    'hora_inicio': 22,
    'hora_fin': 6,
    'descripcion': 'Si consumo nocturno (22:00-06:00) > 30% del promedio → Recomendación'
}

UMBRALES_SECTORES = {
    'ratio_laboratorios_salones': 2.0,
    'descripcion': 'Si laboratorios consumen > 2x que salones → Recomendación'
}

UMBRALES_TEMPERATURA = {
    'temperatura_minima': 20,
    'descripcion': 'Si temperatura promedio > 20°C → Recomendación de climatización'
}

UMBRALES_OCUPACION = {
    'ocupacion_maxima': 50,
    'descripcion': 'Si ocupación promedio < 50% → Recomendación de zonificación'
}

AHORROS_ESTIMADOS = {
    'fin_semana_dias_mes': 8,
    'nocturno_horas_noche': 8,
    'nocturno_dias_mes': 30,
    'climatizacion_min': 500000,
    'climatizacion_max': 1000000,
    'zonificacion_min': 300000,
    'zonificacion_max': 500000,
    'ahorro_global_min_pct': 0.15,
    'ahorro_global_max_pct': 0.20
}

CATEGORIAS = {
    'picos_consumo': {
        'tipo': 'Crítico',
        'nombre': 'Picos de Consumo',
        'accion': 'Redistribuir actividades de alto consumo fuera del horario pico'
    },
    'fin_semana': {
        'tipo': 'Advertencia',
        'nombre': 'Consumo Fin de Semana',
        'accion': 'Implementar apagado automático de equipos no esenciales'
    },
    'nocturno': {
        'tipo': 'Advertencia',
        'nombre': 'Consumo Nocturno',
        'accion': 'Instalar sensores de movimiento y apagado automático 22:00-06:00'
    },
    'sectores': {
        'tipo': 'Información',
        'nombre': 'Consumo por Sector',
        'accion': 'Auditoría de equipos en laboratorios. Actualizar a equipos eficientes'
    },
    'climatizacion': {
        'tipo': 'Información',
        'nombre': 'Climatización',
        'accion': 'Optimizar aires acondicionados: Temperatura 24°C, mantenimiento trimestral'
    },
    'benchmarking': {
        'tipo': 'Crítico',
        'nombre': 'Benchmarking entre Sedes',
        'accion_template': 'Replicar mejores prácticas de {sede_menor} en {sede_mayor}'
    },
    'ocupacion': {
        'tipo': 'Advertencia',
        'nombre': 'Ocupación vs Consumo',
        'accion': 'Implementar zonas de uso según ocupación. Apagar áreas no utilizadas'
    },
    'potencial_global': {
        'tipo': 'Información',
        'nombre': 'Potencial de Ahorro Global',
        'accion': 'Implementando todas las recomendaciones: 15-20% de ahorro'
    },
    'certificacion': {
        'tipo': 'Información',
        'nombre': 'Certificación Energética',
        'descripcion': 'Sistema de gestión energética',
        'accion': 'Implementar ISO 50001 para gestión energética sistemática',
        'ahorro': 'ROI positivo en 2-3 años'
    }
}

RECOMENDACIONES_PERSONALIZADAS = {
    'Tunja': {
        'foco_principal': 'Optimización de laboratorios y salones',
        'prioridad_climatizacion': True
    },
    'Duitama': {
        'foco_principal': 'Control de consumo nocturno',
        'prioridad_automatizacion': True
    },
    'Sogamoso': {
        'foco_principal': 'Reducción de picos de consumo',
        'prioridad_redistribucion': True
    },
    'Chiquinquirá': {
        'foco_principal': 'Eficiencia en laboratorios',
        'prioridad_equipos': True
    }
}

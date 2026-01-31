import pandas as pd
import numpy as np
from pathlib import Path
from config_recomendaciones import *

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / 'data' / 'clean' / 'consumos_uptc_clean.csv'
OUTPUT_DIR = BASE_DIR / 'output'

def generar_recomendaciones_por_sede(df, sede):
    print(f"\n💡 Generando recomendaciones para {sede}...")
    
    df_sede = df[df['sede'] == sede].copy()
    recomendaciones = []
    
    consumo_col = 'energia_total_kwh'
    consumo_promedio = df_sede[consumo_col].mean()
    consumo_max_hora = df_sede.groupby('hora')[consumo_col].mean().idxmax()
    consumo_hora_max_val = df_sede.groupby('hora')[consumo_col].mean().max()
    
    if consumo_hora_max_val > consumo_promedio * UMBRALES_PICOS['multiplicador']:
        ahorro_potencial = (consumo_hora_max_val - consumo_promedio) * 30 * TARIFA_COP_KWH
        recomendaciones.append({
            'tipo': CATEGORIAS['picos_consumo']['tipo'],
            'categoria': CATEGORIAS['picos_consumo']['nombre'],
            'descripcion': f'Consumo máximo a las {consumo_max_hora:02d}:00 hrs ({consumo_hora_max_val:.2f} kWh)',
            'accion': CATEGORIAS['picos_consumo']['accion'],
            'ahorro_estimado_cop': f'${ahorro_potencial:,.0f} COP/mes'
        })
    
    consumo_fin_semana = df_sede[df_sede['es_fin_semana'] == 1][consumo_col].mean()
    consumo_semana = df_sede[df_sede['es_fin_semana'] == 0][consumo_col].mean()
    
    if consumo_fin_semana > consumo_semana * UMBRALES_FIN_SEMANA['ratio_minimo']:
        ahorro_findesemana = (consumo_fin_semana - consumo_semana * UMBRALES_FIN_SEMANA['ratio_objetivo']) * AHORROS_ESTIMADOS['fin_semana_dias_mes'] * 4 * TARIFA_COP_KWH
        recomendaciones.append({
            'tipo': CATEGORIAS['fin_semana']['tipo'],
            'categoria': CATEGORIAS['fin_semana']['nombre'],
            'descripcion': f'Consumo fin de semana alto ({consumo_fin_semana:.2f} kWh vs {consumo_semana:.2f} kWh)',
            'accion': CATEGORIAS['fin_semana']['accion'],
            'ahorro_estimado_cop': f'${ahorro_findesemana:,.0f} COP/mes'
        })
    
    consumo_nocturno = df_sede[df_sede['hora'].between(UMBRALES_NOCTURNO['hora_inicio'], UMBRALES_NOCTURNO['hora_fin'])][consumo_col].mean()
    if consumo_nocturno > consumo_promedio * UMBRALES_NOCTURNO['multiplicador']:
        ahorro_nocturno = (consumo_nocturno - consumo_promedio * UMBRALES_NOCTURNO['objetivo']) * AHORROS_ESTIMADOS['nocturno_horas_noche'] * AHORROS_ESTIMADOS['nocturno_dias_mes'] * TARIFA_COP_KWH
        recomendaciones.append({
            'tipo': CATEGORIAS['nocturno']['tipo'],
            'categoria': CATEGORIAS['nocturno']['nombre'],
            'descripcion': f'Consumo nocturno elevado ({consumo_nocturno:.2f} kWh)',
            'accion': CATEGORIAS['nocturno']['accion'],
            'ahorro_estimado_cop': f'${ahorro_nocturno:,.0f} COP/mes'
        })
    
    consumo_laboratorios = df_sede['energia_laboratorios_kwh'].mean()
    consumo_salones = df_sede['energia_salones_kwh'].mean()
    
    if consumo_laboratorios > consumo_salones * UMBRALES_SECTORES['ratio_laboratorios_salones']:
        recomendaciones.append({
            'tipo': CATEGORIAS['sectores']['tipo'],
            'categoria': CATEGORIAS['sectores']['nombre'],
            'descripcion': f'Laboratorios consumen {consumo_laboratorios/consumo_salones:.1f}x más que salones',
            'accion': CATEGORIAS['sectores']['accion'],
            'ahorro_estimado_cop': 'Variable según equipos'
        })
    
    if 'temperatura_exterior_c' in df_sede.columns:
        temp_prom = df_sede['temperatura_exterior_c'].mean()
        if temp_prom > UMBRALES_TEMPERATURA['temperatura_minima']:
            recomendaciones.append({
                'tipo': CATEGORIAS['climatizacion']['tipo'],
                'categoria': CATEGORIAS['climatizacion']['nombre'],
                'descripcion': f'Temperatura promedio: {temp_prom:.1f}°C',
                'accion': CATEGORIAS['climatizacion']['accion'],
                'ahorro_estimado_cop': f"${AHORROS_ESTIMADOS['climatizacion_min']:,.0f}-{AHORROS_ESTIMADOS['climatizacion_max']:,.0f} COP/mes"
            })
    
    return pd.DataFrame(recomendaciones)

def generar_recomendaciones_generales(df):
    print(f"\n💡 Generando recomendaciones generales...")
    
    recomendaciones = []
    consumo_col = 'energia_total_kwh'
    
    consumo_total = df.groupby('sede')[consumo_col].sum()
    sede_mayor = consumo_total.idxmax()
    sede_menor = consumo_total.idxmin()
    ratio = consumo_total[sede_mayor]/consumo_total[sede_menor]
    
    recomendaciones.append({
        'tipo': CATEGORIAS['benchmarking']['tipo'],
        'categoria': CATEGORIAS['benchmarking']['nombre'],
        'descripcion': f'{sede_mayor} consume {ratio:.1f}x más que {sede_menor}',
        'accion': CATEGORIAS['benchmarking']['accion_template'].format(sede_menor=sede_menor, sede_mayor=sede_mayor),
        'ahorro_estimado_cop': f'${(consumo_total[sede_mayor] * AHORROS_ESTIMADOS["ahorro_global_min_pct"] * TARIFA_COP_KWH):,.0f} COP/año'
    })
    
    if 'ocupacion_pct' in df.columns:
        ocupacion_prom = df.groupby('sede')['ocupacion_pct'].mean()
        for sede in ocupacion_prom.index:
            if ocupacion_prom[sede] < UMBRALES_OCUPACION['ocupacion_maxima']:
                recomendaciones.append({
                    'tipo': CATEGORIAS['ocupacion']['tipo'],
                    'categoria': CATEGORIAS['ocupacion']['nombre'],
                    'descripcion': f'{sede}: Ocupación promedio {ocupacion_prom[sede]:.1f}%',
                    'accion': CATEGORIAS['ocupacion']['accion'],
                    'ahorro_estimado_cop': f"${AHORROS_ESTIMADOS['zonificacion_min']:,.0f}-{AHORROS_ESTIMADOS['zonificacion_max']:,.0f} COP/mes"
                })
    
    total_consumo_anual = df[consumo_col].sum() / len(df['año'].unique())
    ahorro_15pct = total_consumo_anual * AHORROS_ESTIMADOS['ahorro_global_min_pct'] * TARIFA_COP_KWH
    ahorro_20pct = total_consumo_anual * AHORROS_ESTIMADOS['ahorro_global_max_pct'] * TARIFA_COP_KWH
    
    recomendaciones.append({
        'tipo': CATEGORIAS['potencial_global']['tipo'],
        'categoria': CATEGORIAS['potencial_global']['nombre'],
        'descripcion': f'Consumo anual: {total_consumo_anual:,.0f} kWh',
        'accion': CATEGORIAS['potencial_global']['accion'],
        'ahorro_estimado_cop': f'${ahorro_15pct:,.0f} - ${ahorro_20pct:,.0f} COP/año'
    })
    
    recomendaciones.append({
        'tipo': CATEGORIAS['certificacion']['tipo'],
        'categoria': CATEGORIAS['certificacion']['nombre'],
        'descripcion': CATEGORIAS['certificacion']['descripcion'],
        'accion': CATEGORIAS['certificacion']['accion'],
        'ahorro_estimado_cop': CATEGORIAS['certificacion']['ahorro']
    })
    
    return pd.DataFrame(recomendaciones)

def main():
    print("=" * 80)
    print("💡 SISTEMA DE RECOMENDACIONES PERSONALIZADAS")
    print("=" * 80)
    
    print("\n📊 Cargando datos...")
    df = pd.read_csv(DATA_PATH)
    
    sedes = df['sede'].unique()
    todas_recomendaciones = []
    
    for sede in sedes:
        rec_sede = generar_recomendaciones_por_sede(df, sede)
        rec_sede['sede'] = sede
        todas_recomendaciones.append(rec_sede)
        
        print(f"\n📍 {sede}:")
        for _, rec in rec_sede.iterrows():
            print(f"  [{rec['tipo']}] {rec['categoria']}")
            print(f"      ▸ {rec['descripcion']}")
            print(f"      ▸ Acción: {rec['accion']}")
            print(f"      ▸ Ahorro: {rec['ahorro_estimado_cop']}")
    
    rec_generales = generar_recomendaciones_generales(df)
    rec_generales['sede'] = 'Todas'
    todas_recomendaciones.append(rec_generales)
    
    print(f"\n📍 Recomendaciones Generales:")
    for _, rec in rec_generales.iterrows():
        print(f"  [{rec['tipo']}] {rec['categoria']}")
        print(f"      ▸ {rec['descripcion']}")
        print(f"      ▸ Acción: {rec['accion']}")
        print(f"      ▸ Ahorro: {rec['ahorro_estimado_cop']}")
    
    df_recomendaciones = pd.concat(todas_recomendaciones, ignore_index=True)
    rec_path = OUTPUT_DIR / 'recomendaciones_personalizadas.csv'
    df_recomendaciones.to_csv(rec_path, index=False)
    print(f"\n✅ Recomendaciones guardadas: {rec_path}")
    
    print("\n" + "=" * 80)
    print("✅ SISTEMA DE RECOMENDACIONES COMPLETADO")
    print("=" * 80)
    print(f"\n📁 Archivo generado: {rec_path}")
    print("\n🎯 Usa estas recomendaciones en el dashboard y presentación!")
    print("📊 Total de recomendaciones: ", len(df_recomendaciones))

if __name__ == "__main__":
    main()

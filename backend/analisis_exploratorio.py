"""
Análisis exploratorio de datos de consumo energético
Genera estadísticas y visualizaciones
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "clean"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


def load_data():
    df = pd.read_csv(DATA_DIR / "consumos_uptc_clean.csv", parse_dates=['timestamp'])
    return df


def analisis_basico(df):
    print("=" * 80)
    print("ANÁLISIS DESCRIPTIVO - CONSUMO ENERGÉTICO UPTC")
    print("=" * 80)
    
    print(f"\n📊 INFORMACIÓN GENERAL")
    print(f"Total de registros: {len(df):,}")
    print(f"Periodo: {df.timestamp.min()} a {df.timestamp.max()}")
    print(f"Sedes: {', '.join(df.sede.unique())}")
    
    print(f"\n⚡ CONSUMO ENERGÉTICO POR SEDE")
    consumo_sede = df.groupby('sede').agg({
        'energia_total_kwh': ['mean', 'sum', 'std', 'min', 'max'],
        'potencia_total_kw': 'mean',
        'co2_kg': 'sum'
    }).round(2)
    print(consumo_sede)
    
    print(f"\n📅 CONSUMO POR PERIODO ACADÉMICO")
    consumo_periodo = df.groupby(['sede', 'periodo_academico'])['energia_total_kwh'].mean().round(2)
    print(consumo_periodo.unstack())
    
    print(f"\n🚨 ANOMALÍAS DETECTADAS")
    anomalias_ocupacion = df['flag_ocupacion_fuera_rango'].sum()
    anomalias_agua = df['flag_agua_fuera_rango'].sum()
    print(f"Registros con ocupación fuera de rango: {anomalias_ocupacion:,} ({anomalias_ocupacion/len(df)*100:.2f}%)")
    print(f"Registros con consumo agua negativo: {anomalias_agua:,} ({anomalias_agua/len(df)*100:.2f}%)")
    
    print(f"\n💧 CONSUMO DE AGUA POR SEDE")
    agua_sede = df.groupby('sede')['agua_litros'].agg(['mean', 'sum']).round(2)
    print(agua_sede)
    
    print(f"\n🌡️ TEMPERATURA PROMEDIO POR SEDE")
    temp_sede = df.groupby('sede')['temperatura_exterior_c'].mean().round(2)
    print(temp_sede)
    
    return consumo_sede

def visualizar_consumo_temporal(df):
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Consumo Energético por Sede - Serie Temporal', fontsize=16, fontweight='bold')
    
    sedes = df.sede.unique()
    for idx, sede in enumerate(sedes):
        ax = axes[idx // 2, idx % 2]
        data_sede = df[df.sede == sede].groupby(df.timestamp.dt.date)['energia_total_kwh'].sum()
        data_sede.plot(ax=ax, color=f'C{idx}')
        ax.set_title(f'Sede {sede}', fontweight='bold')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Consumo Total (kWh)')
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'consumo_temporal.png', dpi=300, bbox_inches='tight')
    print(f"\n✅ Gráfico guardado: {OUTPUT_DIR / 'consumo_temporal.png'}")


def visualizar_patrones_horarios(df):
    fig, ax = plt.subplots(figsize=(14, 6))
    
    consumo_hora = df.groupby(['sede', 'hora'])['energia_total_kwh'].mean().unstack(level=0)
    consumo_hora.plot(ax=ax, marker='o', linewidth=2)
    
    ax.set_title('Patrón de Consumo Promedio por Hora del Día', fontsize=14, fontweight='bold')
    ax.set_xlabel('Hora del Día', fontsize=12)
    ax.set_ylabel('Consumo Promedio (kWh)', fontsize=12)
    ax.legend(title='Sede', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'patron_horario.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: {OUTPUT_DIR / 'patron_horario.png'}")

def visualizar_heatmap_consumo(df):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Heatmap: Consumo por Día y Hora', fontsize=16, fontweight='bold')
    
    sedes = df.sede.unique()
    for idx, sede in enumerate(sedes):
        ax = axes[idx // 2, idx % 2]
        data_sede = df[df.sede == sede].pivot_table(
            values='energia_total_kwh',
            index='hora',
            columns='dia_semana',
            aggfunc='mean'
        )
        
        sns.heatmap(data_sede, ax=ax, cmap='YlOrRd', cbar_kws={'label': 'kWh'}, fmt='.1f')
        ax.set_title(f'Sede {sede}', fontweight='bold')
        ax.set_xlabel('Día de la Semana (0=Lunes)')
        ax.set_ylabel('Hora del Día')
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'heatmap_consumo.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: {OUTPUT_DIR / 'heatmap_consumo.png'}")


def comparar_periodos(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    consumo_periodo = df.groupby(['sede', 'periodo_academico'])['energia_total_kwh'].mean().unstack()
    consumo_periodo.plot(kind='bar', ax=ax, width=0.8)
    
    ax.set_title('Consumo Promedio por Periodo Académico', fontsize=14, fontweight='bold')
    ax.set_xlabel('Sede', fontsize=12)
    ax.set_ylabel('Consumo Promedio (kWh)', fontsize=12)
    ax.legend(title='Periodo Académico', fontsize=10)
    ax.grid(True, axis='y', alpha=0.3)
    plt.xticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'comparacion_periodos.png', dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico guardado: {OUTPUT_DIR / 'comparacion_periodos.png'}")

def analisis_eficiencia(df):
    sedes_info = {
        'Tunja': {'estudiantes': 18000, 'area_m2': 85000},
        'Duitama': {'estudiantes': 5500, 'area_m2': 35000},
        'Sogamoso': {'estudiantes': 6000, 'area_m2': 40000},
        'Chiquinquirá': {'estudiantes': 2000, 'area_m2': 15000}
    }
    
    print(f"\n📊 EFICIENCIA ENERGÉTICA")
    print("-" * 80)
    
    consumo_total = df.groupby('sede')['energia_total_kwh'].sum()
    
    for sede in df.sede.unique():
        consumo = consumo_total[sede]
        est = sedes_info[sede]['estudiantes']
        area = sedes_info[sede]['area_m2']
        
        eficiencia_est = consumo / est
        eficiencia_area = consumo / area
        
        print(f"\n{sede}:")
        print(f"  kWh/estudiante: {eficiencia_est:.2f}")
        print(f"  kWh/m²: {eficiencia_area:.2f}")


def main():
    print("\n🔍 Cargando datos...")
    df = load_data()
    
    print("\n📈 Generando análisis descriptivo...")
    analisis_basico(df)
    
    print("\n📊 Generando visualizaciones...")
    visualizar_consumo_temporal(df)
    visualizar_patrones_horarios(df)
    visualizar_heatmap_consumo(df)
    comparar_periodos(df)
    
    print("\n💡 Análisis de eficiencia...")
    analisis_eficiencia(df)
    
    print("\n" + "=" * 80)
    print("✅ ANÁLISIS COMPLETADO")
    print(f"📁 Resultados guardados en: {OUTPUT_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()

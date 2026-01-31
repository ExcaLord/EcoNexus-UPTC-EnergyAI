"""
Dashboard interactivo para visualización de consumo energético
Ejecutar: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import joblib
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Dashboard Consumo UPTC",
    page_icon="⚡",
    layout="wide"
)


@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "data" / "clean" / "consumos_uptc_clean.csv"
    df = pd.read_csv(data_path, parse_dates=['timestamp'])
    return df


@st.cache_resource
def load_model():
    model_path = Path(__file__).parent / "models" / "modelo_xgboost.joblib"
    if model_path.exists():
        return joblib.load(model_path)
    return None


def load_predictions(sede):
    pred_path = Path(__file__).parent / "output" / f"predicciones_{sede.lower()}_proxima_semana.csv"
    if pred_path.exists():
        return pd.read_csv(pred_path, parse_dates=['timestamp'])
    return None


SEDES_INFO = {
    'Tunja': {'estudiantes': 18000, 'area_m2': 85000, 'emoji': '🏛️'},
    'Duitama': {'estudiantes': 5500, 'area_m2': 35000, 'emoji': '🏫'},
    'Sogamoso': {'estudiantes': 6000, 'area_m2': 40000, 'emoji': '🏢'},
    'Chiquinquirá': {'estudiantes': 2000, 'area_m2': 15000, 'emoji': '🏬'}
}


def main():
    st.title("⚡ Dashboard de Consumo Energético UPTC")
    st.markdown("### Análisis de Eficiencia y Optimización de Recursos")

    with st.spinner("Cargando datos..."):
        df = load_data()

    st.sidebar.header("🔍 Filtros")

    sedes_selected = st.sidebar.multiselect(
        "Sedes",
        options=df.sede.unique(),
        default=df.sede.unique()
    )

    periodo_selected = st.sidebar.multiselect(
        "Periodo Académico",
        options=df.periodo_academico.unique(),
        default=df.periodo_academico.unique()
    )

    fecha_inicio = st.sidebar.date_input("Fecha Inicio", df.timestamp.min())
    fecha_fin = st.sidebar.date_input("Fecha Fin", df.timestamp.max())

    df_filtered = df[
        (df.sede.isin(sedes_selected)) &
        (df.periodo_academico.isin(periodo_selected)) &
        (df.timestamp >= pd.Timestamp(fecha_inicio)) &
        (df.timestamp <= pd.Timestamp(fecha_fin))
    ]

    st.header("📊 Métricas Principales")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        consumo_total = df_filtered.energia_total_kwh.sum()
        st.metric("Consumo Total", f"{consumo_total:,.0f} kWh")

    with col2:
        consumo_promedio = df_filtered.energia_total_kwh.mean()
        st.metric("Consumo Promedio", f"{consumo_promedio:.2f} kWh")

    with col3:
        co2_total = df_filtered.co2_kg.sum()
        st.metric("Emisiones CO₂", f"{co2_total:,.0f} kg")

    with col4:
        agua_total = df_filtered.agua_litros.sum()
        st.metric("Consumo Agua", f"{agua_total:,.0f} L")

    st.header("📈 Consumo en el Tiempo")

    df_daily = df_filtered.groupby([df_filtered.timestamp.dt.date, 'sede'])['energia_total_kwh'].sum().reset_index()
    df_daily.columns = ['fecha', 'sede', 'consumo']

    fig_temporal = px.line(
        df_daily,
        x='fecha',
        y='consumo',
        color='sede',
        title='Consumo Diario por Sede',
        labels={'consumo': 'Consumo (kWh)', 'fecha': 'Fecha'}
    )
    st.plotly_chart(fig_temporal, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏢 Consumo por Sede")
        consumo_sede = df_filtered.groupby('sede')['energia_total_kwh'].sum().sort_values(ascending=True)
        fig_sede = px.bar(
            x=consumo_sede.values,
            y=consumo_sede.index,
            orientation='h',
            labels={'x': 'Consumo Total (kWh)', 'y': 'Sede'},
            color=consumo_sede.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_sede, use_container_width=True)

    with col2:
        st.subheader("📅 Consumo por Periodo")
        consumo_periodo = df_filtered.groupby('periodo_academico')['energia_total_kwh'].mean()
        fig_periodo = px.pie(
            values=consumo_periodo.values,
            names=consumo_periodo.index,
            title='Distribución Promedio'
        )
        st.plotly_chart(fig_periodo, use_container_width=True)

    st.header("🕐 Patrón de Consumo Horario")
    consumo_hora = df_filtered.groupby(['hora', 'sede'])['energia_total_kwh'].mean().reset_index()

    fig_hora = px.line(
        consumo_hora,
        x='hora',
        y='energia_total_kwh',
        color='sede',
        title='Consumo Promedio por Hora del Día',
        labels={'energia_total_kwh': 'Consumo (kWh)', 'hora': 'Hora del Día'}
    )
    st.plotly_chart(fig_hora, use_container_width=True)

    st.header("💡 Eficiencia Energética")

    eficiencia_data = []
    for sede in sedes_selected:
        consumo = df_filtered[df_filtered.sede == sede]['energia_total_kwh'].sum()
        info = SEDES_INFO[sede]
        eficiencia_data.append({
            'Sede': f"{info['emoji']} {sede}",
            'kWh/Estudiante': consumo / info['estudiantes'],
            'kWh/m²': consumo / info['area_m2'],
            'Estudiantes': info['estudiantes'],
            'Área (m²)': info['area_m2']
        })

    df_eficiencia = pd.DataFrame(eficiencia_data)
    st.dataframe(df_eficiencia, use_container_width=True)
    
    st.header("🔮 Predicciones de Consumo")
    
    model_data = load_model()
    
    if model_data is not None:
        st.success(f"✅ Modelo cargado | R²: {model_data['metrics']['r2']:.4f} | RMSE: {model_data['metrics']['rmse']:.4f} kWh")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Configuración")
            sede_pred = st.selectbox("Selecciona Sede", options=list(SEDES_INFO.keys()), key="pred_sede")
            
            st.markdown("**Rango de Predicción**")
            fecha_inicio = st.date_input(
                "Fecha Inicio",
                value=datetime.now().date(),
                min_value=datetime(2018, 1, 1).date(),
                max_value=datetime(2030, 12, 31).date()
            )
            
            dias_pred = st.slider("Días a predecir", min_value=1, max_value=30, value=7)
            
            if st.button("🔮 Generar Predicciones", type="primary"):
                with st.spinner(f"Generando predicciones para {sede_pred}..."):
                    import subprocess
                    fecha_str = fecha_inicio.strftime('%Y-%m-%d')
                    result = subprocess.run(
                        ["python", "predecir_fecha.py", sede_pred, fecha_str, str(dias_pred)],
                        capture_output=True,
                        text=True,
                        cwd=Path(__file__).parent
                    )
                    if result.returncode == 0:
                        st.success("✅ Predicciones generadas!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result.stderr}")
        
        with col2:
            fecha_str = fecha_inicio.strftime('%Y%m%d')
            pred_file = Path(__file__).parent / "output" / f"predicciones_{sede_pred.lower()}_{fecha_str}_{dias_pred}dias.csv"
            
            if pred_file.exists():
                df_pred = pd.read_csv(pred_file, parse_dates=['timestamp'])
                
                st.subheader(f"Predicciones para {SEDES_INFO[sede_pred]['emoji']} {sede_pred}")
                st.caption(f"Desde {fecha_inicio} por {dias_pred} días")
                
                fig_pred = go.Figure()
                
                df_pred['fecha'] = pd.to_datetime(df_pred['timestamp']).dt.date
                consumo_diario_pred = df_pred.groupby('fecha')['consumo_predicho'].sum().reset_index()
                
                fig_pred.add_trace(go.Scatter(
                    x=consumo_diario_pred['fecha'],
                    y=consumo_diario_pred['consumo_predicho'],
                    mode='lines+markers',
                    name='Predicción',
                    line=dict(color='#FF6B6B', width=3),
                    marker=dict(size=8)
                ))
                
                fig_pred.update_layout(
                    title=f'Consumo Predicho Próxima Semana - {sede_pred}',
                    xaxis_title='Fecha',
                    yaxis_title='Consumo Diario (kWh)',
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig_pred, use_container_width=True)
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Consumo Total", f"{df_pred['consumo_predicho'].sum():.0f} kWh")
                with col_b:
                    st.metric("Promedio Diario", f"{consumo_diario_pred['consumo_predicho'].mean():.0f} kWh")
                with col_c:
                    costo = df_pred['consumo_predicho'].sum() * 600
                    st.metric("Costo Estimado", f"${costo:,.0f} COP")
                with col_d:
                    st.metric("Días", f"{len(consumo_diario_pred)}")
                
                with st.expander("📊 Ver Predicciones Detalladas"):
                    st.dataframe(df_pred[['timestamp', 'hora', 'dia', 'consumo_predicho']].head(100), use_container_width=True)
            else:
                st.info(f"📝 No hay predicciones para {sede_pred} desde {fecha_inicio} por {dias_pred} días. Genera nuevas predicciones.")
    else:
        st.warning("⚠️ Modelo no encontrado. Entrena el modelo primero con: `python modelo_xgboost.py`")

    with st.expander("📋 Ver Datos Detallados"):
        num_rows = st.slider("Número de filas a mostrar", min_value=10, max_value=len(df_filtered), value=min(100, len(df_filtered)), step=10)
        show_all = st.checkbox("Mostrar todas las filas", value=False)

        if show_all:
            st.dataframe(df_filtered, use_container_width=True, height=600)
            st.info(f"📊 Mostrando {len(df_filtered):,} registros totales")
        else:
            st.dataframe(df_filtered.head(num_rows), use_container_width=True)
            st.info(f"📊 Mostrando {num_rows:,} de {len(df_filtered):,} registros")

    st.markdown("---")
    st.markdown("**IA Minds 2026** - HackDay UPTC | Datos: 2018-2025")


if __name__ == "__main__":
    main()

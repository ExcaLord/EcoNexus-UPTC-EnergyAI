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


@st.cache_data
def load_recommendations():
    rec_path = Path(__file__).parent / "output" / "recomendaciones_personalizadas.csv"
    if rec_path.exists():
        return pd.read_csv(rec_path)
    return None


@st.cache_data
def load_shap_importance():
    shap_path = Path(__file__).parent / "output" / "feature_importance_shap.csv"
    if shap_path.exists():
        return pd.read_csv(shap_path)
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

    with st.expander("ℹ️ Información sobre Tarifas Energéticas"):
        st.markdown("""
        ### 💰 Tarifas Institucionales en Colombia (2026)

        **Componentes de la Tarifa:**
        - 🔌 Costo de Energía: 450-550 COP/kWh
        - 📡 Transmisión Nacional: 80-120 COP/kWh
        - 🏘️ Distribución Local: 150-200 COP/kWh
        - 💼 Comercialización: 30-50 COP/kWh
        - 🤝 Contribución (20%): 150-196 COP/kWh
        - 📊 IVA (19%): 171-223 COP/kWh

        **Tarifas Sugeridas:**
        - **Conservadora (850 COP/kWh)**: Para estimaciones económicas ✅
        - **Promedio (1,050 COP/kWh)**: Valor realista para instituciones
        - **Alta (1,200 COP/kWh)**: Incluye todos los cargos

        💡 *Recomendación: Revisar factura real de la UPTC para mayor precisión*
        """)

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

            st.markdown("**Tarifa Energética**")
            tarifa_seleccion = st.selectbox(
                "Tipo de Tarifa",
                options=[
                    "Conservadora (850 COP/kWh)",
                    "Promedio (1,050 COP/kWh)",
                    "Alta (1,200 COP/kWh)",
                    "Personalizada"
                ],
                index=0
            )

            if "Personalizada" in tarifa_seleccion:
                tarifa_cop = st.number_input(
                    "Tarifa COP/kWh",
                    min_value=400,
                    max_value=2000,
                    value=850,
                    step=50,
                    help="Ingresa la tarifa según tu factura de energía"
                )
            else:
                tarifa_map = {
                    "Conservadora (850 COP/kWh)": 850,
                    "Promedio (1,050 COP/kWh)": 1050,
                    "Alta (1,200 COP/kWh)": 1200
                }
                tarifa_cop = tarifa_map[tarifa_seleccion]

            st.caption(f"💰 Tarifa: ${tarifa_cop:,} COP/kWh")

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
                    costo = df_pred['consumo_predicho'].sum() * tarifa_cop
                    costo_usd = costo / 4000
                    st.metric("Costo Estimado", f"${costo:,.0f} COP", f"≈ ${costo_usd:,.0f} USD")
                with col_d:
                    st.metric("Días", f"{len(consumo_diario_pred)}")

                st.info(f"💡 Cálculo: {df_pred['consumo_predicho'].sum():.2f} kWh × ${tarifa_cop:,} COP/kWh = ${costo:,.0f} COP")

                with st.expander("🏢 Ver Predicciones por Sector"):
                    import subprocess
                    fecha_str_sector = fecha_inicio.strftime('%Y-%m-%d')
                    result_sector = subprocess.run(
                        ["python", "predecir_sectores.py", sede_pred, fecha_str_sector, str(dias_pred)],
                        capture_output=True,
                        text=True,
                        cwd=Path(__file__).parent
                    )

                    fecha_str_file = fecha_inicio.strftime('%Y%m%d')
                    sector_file = Path(__file__).parent / "output" / f"predicciones_sectores_{sede_pred.lower()}_{fecha_str_file}_{dias_pred}dias.csv"
                    sector_img = Path(__file__).parent / "output" / f"sectores_{sede_pred.lower()}_{fecha_str_file}.png"

                    if sector_file.exists():
                        df_sectores = pd.read_csv(sector_file)

                        st.subheader(f"Distribución por Sector - {sede_pred}")

                        sectores_cols = ['comedor', 'salones', 'laboratorios', 'auditorios', 'oficinas']
                        consumo_sectores = {}
                        for sector in sectores_cols:
                            if sector in df_sectores.columns:
                                consumo_sectores[sector.capitalize()] = df_sectores[sector].sum()

                        col_s1, col_s2 = st.columns(2)

                        with col_s1:
                            if sector_img.exists():
                                st.image(str(sector_img), use_container_width=True)
                            else:
                                fig_pie = go.Figure(data=[go.Pie(
                                    labels=list(consumo_sectores.keys()),
                                    values=list(consumo_sectores.values()),
                                    hole=0.3
                                )])
                                fig_pie.update_layout(title=f"Distribución por Sector")
                                st.plotly_chart(fig_pie, use_container_width=True)

                        with col_s2:
                            st.markdown("**Consumo por Sector (kWh)**")
                            sector_df = pd.DataFrame({
                                'Sector': list(consumo_sectores.keys()),
                                'Consumo (kWh)': [f"{v:.2f}" for v in consumo_sectores.values()],
                                'Porcentaje': [f"{v/sum(consumo_sectores.values())*100:.1f}%" for v in consumo_sectores.values()],
                                'Costo (COP)': [f"${v*tarifa_cop:,.0f}" for v in consumo_sectores.values()]
                            })
                            st.dataframe(sector_df, use_container_width=True, hide_index=True)

                        st.markdown("**Top 3 Sectores con Mayor Consumo:**")
                        top_sectores = sorted(consumo_sectores.items(), key=lambda x: x[1], reverse=True)[:3]
                        for i, (sector, consumo) in enumerate(top_sectores, 1):
                            st.write(f"{i}. **{sector}**: {consumo:.2f} kWh ({consumo/sum(consumo_sectores.values())*100:.1f}%) - ${consumo*tarifa_cop:,.0f} COP")
                    else:
                        st.warning("⚠️ Genera las predicciones primero para ver el desglose por sector")

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

    st.header("🔬 Explicabilidad del Modelo (XAI)")

    shap_importance = load_shap_importance()

    if shap_importance is not None:
        st.markdown("""
        ### 🎯 ¿Qué factores influyen más en el consumo energético?

        El análisis SHAP (SHapley Additive exPlanations) revela los factores más importantes
        que el modelo considera para predecir el consumo energético.
        """)

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📊 Top 10 Factores Más Influyentes")

            top_10 = shap_importance.head(10)
            fig_shap = go.Figure(data=[
                go.Bar(
                    y=top_10['Feature'],
                    x=top_10['Importancia_SHAP'],
                    orientation='h',
                    marker=dict(
                        color=top_10['Importancia_SHAP'],
                        colorscale='Viridis',
                        showscale=True,
                        colorbar=dict(title="Importancia")
                    ),
                    text=[f"{val:.4f}" for val in top_10['Importancia_SHAP']],
                    textposition='auto'
                )
            ])
            fig_shap.update_layout(
                title="Importancia de Características (SHAP Values)",
                xaxis_title="Importancia SHAP",
                yaxis_title="Característica",
                yaxis={'categoryorder':'total ascending'},
                height=500
            )
            st.plotly_chart(fig_shap, use_container_width=True)

        with col2:
            st.subheader("📝 Interpretación")

            if len(top_10) > 0:
                top_feature = top_10.iloc[0]
                st.markdown(f"""
                **Factor #1: {top_feature['Feature']}**

                Importancia: `{top_feature['Importancia_SHAP']:.4f}`

                Este es el factor más influyente en las predicciones del modelo.
                Pequeños cambios aquí tienen gran impacto en el consumo predicho.
                """)

                if len(top_10) > 1:
                    second = top_10.iloc[1]
                    st.markdown(f"""
                    **Factor #2: {second['Feature']}**

                    Importancia: `{second['Importancia_SHAP']:.4f}`
                    """)

                if len(top_10) > 2:
                    third = top_10.iloc[2]
                    st.markdown(f"""
                    **Factor #3: {third['Feature']}**

                    Importancia: `{third['Importancia_SHAP']:.4f}`
                    """)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            shap_summary_path = Path(__file__).parent / "output" / "shap_summary.png"
            if shap_summary_path.exists():
                st.subheader("📊 SHAP Summary Plot")
                st.image(str(shap_summary_path), use_container_width=True)
                st.caption("Importancia global de características")

        with col2:
            shap_beeswarm_path = Path(__file__).parent / "output" / "shap_beeswarm.png"
            if shap_beeswarm_path.exists():
                st.subheader("🐝 SHAP Beeswarm Plot")
                st.image(str(shap_beeswarm_path), use_container_width=True)
                st.caption("Impacto de características en predicciones individuales")

        with st.expander("📚 ¿Cómo leer estos gráficos?"):
            st.markdown("""
            **SHAP Values (SHapley Additive exPlanations)**

            - **Barra horizontal**: Cuanto más larga, mayor es la importancia del factor
            - **Color**: Representa la magnitud del impacto
            - **Beeswarm**: Cada punto es una predicción. Color rojo = valor alto de la característica, azul = valor bajo

            **¿Para qué sirve?**
            - Identificar qué factores controlar para reducir consumo
            - Justificar decisiones con base científica
            - Detectar patrones no obvios en los datos
            """)
    else:
        st.info("⚠️ Genera el análisis de explicabilidad primero: `python explicabilidad_xai.py`")

    st.markdown("---")

    st.header("💡 Recomendaciones Personalizadas")

    df_recomendaciones = load_recommendations()

    if df_recomendaciones is not None:
        sede_rec = st.selectbox(
            "Selecciona Sede para Recomendaciones:",
            options=['Todas'] + list(SEDES_INFO.keys()),
            key='sede_recomendaciones'
        )

        rec_filtradas = df_recomendaciones[df_recomendaciones['sede'] == sede_rec]

        if len(rec_filtradas) > 0:
            st.markdown(f"### 📍 Recomendaciones para {sede_rec}")

            tipos_color = {
                'Crítico': '🔴',
                'Advertencia': '🟡',
                'Información': '🔵'
            }

            for tipo in ['Crítico', 'Advertencia', 'Información']:
                rec_tipo = rec_filtradas[rec_filtradas['tipo'] == tipo]
                if len(rec_tipo) > 0:
                    st.markdown(f"#### {tipos_color[tipo]} {tipo}")
                    for idx, row in rec_tipo.iterrows():
                        ahorro_kwh = row.get('ahorro_kwh', 0)
                        impacto = row.get('impacto', 'N/A')

                        with st.expander(f"**{row['categoria']}** - {row['descripcion']}", expanded=(tipo=='Crítico')):
                            st.markdown(f"**📋 Descripción:** {row['descripcion']}")
                            st.markdown(f"**✅ Acción Recomendada:** {row['accion']}")
                            if ahorro_kwh > 0:
                                st.markdown(f"**⚡ Ahorro Potencial:** {ahorro_kwh:.0f} kWh")
                                st.markdown(f"**💰 Ahorro Estimado:** ${ahorro_kwh * 1050:,.0f} COP")
                            st.markdown(f"**🎯 Impacto:** {impacto}")

            st.markdown("---")
            st.markdown("### 📊 Resumen de Ahorros")

            total_criticos = len(rec_filtradas[rec_filtradas['tipo'] == 'Crítico'])
            total_advertencias = len(rec_filtradas[rec_filtradas['tipo'] == 'Advertencia'])
            total_info = len(rec_filtradas[rec_filtradas['tipo'] == 'Información'])

            col1, col2, col3 = st.columns(3)
            col1.metric("🔴 Críticas", total_criticos)
            col2.metric("🟡 Advertencias", total_advertencias)
            col3.metric("🔵 Informativas", total_info)

        else:
            st.info("No hay recomendaciones específicas para esta sede")
    else:
        st.warning("⚠️ Genera las recomendaciones primero ejecutando: `python recomendaciones_sistema.py`")

# ANOMALÍAS Y RECOMENDACIONES
    st.header("⚠️ Detección de Anomalías")

    anomalias_path = Path(__file__).parent / "output" / "anomalias.csv"
    recomendaciones_path = Path(__file__).parent / "output" / "recomendaciones.csv"

    if anomalias_path.exists():
        df_anomalias = pd.read_csv(anomalias_path, parse_dates=['timestamp'])

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Anomalías", f"{len(df_anomalias):,}")
        with col2:
            criticas = len(df_anomalias[df_anomalias['severidad'] == 'critica'])
            st.metric("Críticas", f"{criticas:,}")
        with col3:
            ahorro_kwh = df_anomalias['diferencia_kwh'].sum()
            st.metric("Desperdicio", f"{ahorro_kwh:.0f} kWh")
        with col4:
            ahorro_cop = ahorro_kwh * 700
            st.metric("Ahorro Potencial", f"${ahorro_cop:,.0f} COP")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Anomalías por Tipo")
            tipo_counts = df_anomalias['tipo_anomalia'].value_counts()
            fig_tipos = px.bar(
                x=tipo_counts.values,
                y=tipo_counts.index,
                orientation='h',
                labels={'x': 'Cantidad', 'y': 'Tipo'},
                color=tipo_counts.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_tipos, use_container_width=True)

        with col2:
            st.subheader("🏢 Anomalías por Sede")
            sede_counts = df_anomalias['sede'].value_counts()
            fig_sedes = px.pie(
                values=sede_counts.values,
                names=sede_counts.index,
                title='Distribución por Sede'
            )
            st.plotly_chart(fig_sedes, use_container_width=True)

        st.subheader("🔥 Top 10 Anomalías Críticas")
        criticas_top = df_anomalias[df_anomalias['severidad'] == 'critica'].nlargest(10, 'diferencia_kwh')

        for idx, row in criticas_top.iterrows():
            with st.expander(f"⚠️ {row['sede']} - {row['sector'].upper()} | {row['timestamp'].strftime('%Y-%m-%d %H:%M')} | +{row['diferencia_kwh']:.2f} kWh"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Real", f"{row['real_kwh']:.2f} kWh")
                with col2:
                    st.metric("Esperado", f"{row['esperado_kwh']:.2f} kWh")
                with col3:
                    st.metric("Exceso", f"+{row['diferencia_pct']:.0f}%")
                st.info(f"**Tipo:** {row['tipo_anomalia']}")
    else:
        st.info("📊 No hay datos de anomalías disponibles")

    if recomendaciones_path.exists():
        st.header("💡 Recomendaciones de Optimización")

        df_recom = pd.read_csv(recomendaciones_path)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Recomendaciones", f"{len(df_recom)}")
        with col2:
            ahorro_total = df_recom['ahorro_potencial_kwh'].sum()
            st.metric("Ahorro Total", f"{ahorro_total:.0f} kWh/mes")
        with col3:
            ahorro_anual = df_recom['ahorro_mensual_cop'].sum() * 12
            st.metric("Ahorro Anual", f"${ahorro_anual:,.0f} COP")

        st.subheader("🎯 Top 10 Recomendaciones Prioritarias")
        top_recom = df_recom.head(10)

        for idx, row in top_recom.iterrows():
            with st.expander(f"#{row['prioridad_final']}. {row['sede']} - {row['sector'].upper()} | 💰 ${row['ahorro_mensual_cop']:,} COP/mes | ⚙️ {row['dificultad_implementacion']}"):
                st.write(f"**📋 Problema:**")
                st.write(row['problema'])

                st.write(f"**🔍 Causa Probable:**")
                st.write(row['causa_probable'])

                st.write(f"**✅ Acciones Recomendadas:**")
                st.write(row['acciones_recomendadas'])

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Eventos", row['cantidad_eventos'])
                with col2:
                    st.metric("Críticos", row['eventos_criticos'])
                with col3:
                    st.metric("Ahorro kWh/mes", f"{row['ahorro_potencial_kwh']:.1f}")
                with col4:
                    st.metric("Responsable", row['responsable'])
    else:
        st.info("📊 No hay recomendaciones disponibles")

    with st.expander("📋 Ver Datos Detallados"):
        num_rows = st.slider("Número de filas a mostrar", min_value=10, max_value=len(df_filtered), value=min(100, len(df_filtered)), step=10, key="slider_datos")
        show_all = st.checkbox("Mostrar todas las filas", value=False, key="checkbox_datos")

        if show_all:
            st.dataframe(df_filtered, use_container_width=True, height=600)
            st.info(f"📊 Mostrando {len(df_filtered):,} registros totales")
        else:
            st.dataframe(df_filtered.head(num_rows), use_container_width=True)
            st.info(f"📊 Mostrando {num_rows:,} de {len(df_filtered):,} registros")

    st.markdown("---")
    st.markdown("**EcoNexus - IA Minds 2026** | HackDay UPTC | Detección de Anomalías + Predicción de Consumo")

if __name__ == "__main__":
    main()

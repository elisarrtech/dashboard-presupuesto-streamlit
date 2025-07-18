import streamlit as st
import pandas as pd
from calendar import month_name
from utils.data_loader import get_gsheet_data, save_gsheet_data, load_excel_data
from utils.data_processor import clean_and_validate_data, convert_df_to_csv, convert_df_to_excel
from components.visuals import (
    show_kpis,
    plot_gasto_por_mes,
    plot_gasto_por_categoria,
    show_filtered_table,
    show_month_comparison,
    show_categoria_presupuesto,
    show_monthly_topes,
    plot_nominas_comisiones
)

st.set_page_config(page_title="Presupuesto", layout="wide")

meses_es = {i: month_name[i] for i in range(1, 13)}
topes_mensuales = {1: 496861.12, 2: 534961.49, 3: 492482.48, 4: 442578.28, 5: 405198.44, 6: 416490.46, 7: 420000.00}

# --- Selección de página ---
pagina = st.sidebar.radio("Selecciona sección", ["📊 Presupuesto General", "👥 Nóminas y Comisiones"])

# --- Carga de datos ---
data_source = st.sidebar.selectbox("Fuente de datos", ["Google Sheets", "Archivo Excel"])
df = pd.DataFrame()

if data_source == "Google Sheets":
    try:
        df, sheet = get_gsheet_data()
    except Exception:
        st.error("Error al conectar con Google Sheets")
        st.stop()
elif data_source == "Archivo Excel":
    uploaded_file = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"])
    if uploaded_file:
        df = load_excel_data(uploaded_file)
        df = df.loc[:, ~df.columns.duplicated()]

if not df.empty:
    try:
        df = clean_and_validate_data(df)
    except ValueError as e:
        st.error(f"Error validando datos: {e}")
        st.stop()

    filtro_mes = st.sidebar.multiselect("📅 Filtrar por mes", options=list(range(1, 13)), format_func=lambda x: month_name[x])
    filtro_status = st.sidebar.multiselect("🔍 Filtrar por estatus", options=df["Status"].unique())

    if pagina == "📊 Presupuesto General":
        show_kpis(df, topes_mensuales, filtro_mes, filtro_status)
        plot_gasto_por_mes(df, filtro_mes, filtro_status)
        show_monthly_topes(df, topes_mensuales, filtro_mes, filtro_status)
        plot_gasto_por_categoria(df, filtro_mes, filtro_status)
        show_filtered_table(df, filtro_mes, filtro_status)
        show_month_comparison(df, filtro_mes, filtro_status)
        show_categoria_presupuesto(df)

        st.sidebar.download_button("⬇️ Exportar CSV", data=convert_df_to_csv(df), file_name="presupuesto.csv", mime="text/csv")
        st.sidebar.download_button("⬇️ Exportar Excel", data=convert_df_to_excel(df), file_name="presupuesto.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    elif pagina == "👥 Nóminas y Comisiones":
        st.header("📊 Análisis de Nóminas y Comisiones")

        mostrar_filtro = st.checkbox("🔲 Mostrar filtro por categoría")
        filtro_categoria = []
        if mostrar_filtro:
            filtro_categoria = st.multiselect("🔍 Filtrar por categoría", options=df["Categoría"].unique())

        df_filtrado = df.copy()
        if filtro_categoria:
            df_filtrado = df_filtrado[df_filtrado["Categoría"].isin(filtro_categoria)]
        if filtro_mes:
            df_filtrado = df_filtrado[df_filtrado["Mes_num"].isin(filtro_mes)]
        if filtro_status:
            df_filtrado = df_filtrado[df_filtrado["Status"].str.upper().isin([s.upper() for s in filtro_status])]

        show_kpis(df_filtrado, topes_mensuales, filtro_mes, filtro_status)
        plot_nominas_comisiones(df_filtrado, filtro_mes, filtro_status)
        show_filtered_table(df_filtrado, filtro_mes, filtro_status)

        st.sidebar.download_button("⬇️ Exportar CSV", data=convert_df_to_csv(df_filtrado), file_name="nominas_comisiones.csv", mime="text/csv")
        st.sidebar.download_button("⬇️ Exportar Excel", data=convert_df_to_excel(df_filtrado), file_name="nominas_comisiones.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.warning("⚠️ No hay datos para mostrar.")

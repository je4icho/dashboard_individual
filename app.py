import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import altair as alt

# --------------------------------------------------
# Función para formatear valores en CLP
# --------------------------------------------------
def formato_clp(valor):
    try:
        return "$" + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "$0,00"

# --------------------------------------------------
# Configuración general
# --------------------------------------------------
st.set_page_config(
    page_title="Dashboard Territorial - Valor y Volumen",
    layout="wide"
)

st.title("Dashboard territorial: volumen vs valor económico")
st.markdown(
    """
    Este dashboard permite explorar la distribución territorial del valor económico y del volumen de pedidos
    en la Región Metropolitana, integrando un mapa interactivo y un ranking por comuna.
    """
)


# --------------------------------------------------
# Carga de datos
# --------------------------------------------------

@st.cache_data
def cargar_datos():
    df = pd.read_excel("dataset_tarea_ind.xlsx")

    # Convertir venta_neta a float
    df["venta_neta"] = (
        df["venta_neta"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # Agregación por comuna
    df_agg = df.groupby("comuna", as_index=False).agg(
        venta_total=("venta_neta", "sum"),
        pedidos=("orden", "nunique"),
        unidades_totales=("unidades", "sum")
    )
 
    df_agg["ticket_promedio"] = df_agg["venta_total"] / df_agg["pedidos"]
    df_agg["venta_total_millones"] = df_agg["venta_total"] / 1_000_000

    return df_agg


@st.cache_data
def cargar_geojson():
    gdf = gpd.read_file("comunas_metropolitana-1.geojson")
    return gdf


df_agg = cargar_datos()
gdf = cargar_geojson()

# --------------------------------------------------
# Normalización de nombres en el GeoJSON
# --------------------------------------------------
gdf["name"] = gdf["name"].replace({
    "Nunoa": "Ñuñoa",
    "nunoa": "Ñuñoa",
    "Nunoa ": "Ñuñoa"
})

# --------------------------------------------------
# Normalización de nombres de comunas
# --------------------------------------------------
df_agg["comuna"] = df_agg["comuna"].replace({
    "Nunoa": "Ñuñoa",
    "nunoa": "Ñuñoa",
    "Nunoa ": "Ñuñoa"
})

# --------------------------------------------------
# Tarjetas KPI (resumen general)
# --------------------------------------------------
st.markdown("### Resumen general")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Venta total RM",
        value=formato_clp(df_agg["venta_total"].sum())
    )

with col2:
    st.metric(
        label="Total de pedidos RM",
        value=f"{df_agg['pedidos'].sum():,}".replace(",", ".")
    )

with col3:
    st.metric(
        label="Ticket promedio RM",
        value=formato_clp(df_agg['venta_total'].sum() / df_agg['pedidos'].sum())
    )


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
st.sidebar.header("Controles de exploración")

metrica_opcion = st.sidebar.selectbox(
    "Métrica a visualizar:",
    (
        "Venta total (millones de CLP)",
        "Número de pedidos",
        "Ticket promedio (CLP)"
    )
)

if metrica_opcion == "Venta total (millones de CLP)":
    metrica_col = "venta_total_millones"
    metrica_label = "Venta total (MM CLP)"
elif metrica_opcion == "Número de pedidos":
    metrica_col = "pedidos"
    metrica_label = "Número de pedidos"
else:
    metrica_col = "ticket_promedio"
    metrica_label = "Ticket promedio (CLP)"

# Rango dinámico sin redondeo
min_val = float(df_agg[metrica_col].min())
max_val = float(df_agg[metrica_col].max())

rango = st.sidebar.slider(
    f"Filtrar comunas por {metrica_label}",
    min_value=float(min_val),
    max_value=float(max_val),
    value=(float(min_val), float(max_val))
)

mostrar_top_n = st.sidebar.slider(
    "Cantidad de comunas en el ranking:",
    min_value=5,
    max_value=min(25, df_agg.shape[0]),
    value=15
)

# --------------------------------------------------
# Filtrado
# --------------------------------------------------
df_filtrado = df_agg[
    (df_agg[metrica_col] >= rango[0]) &
    (df_agg[metrica_col] <= rango[1])
].copy()

df_ranking = df_filtrado.sort_values(metrica_col, ascending=False).head(mostrar_top_n)

# --------------------------------------------------
# Layout principal
# --------------------------------------------------
col_mapa, col_ranking = st.columns([1.3, 1])

# ----------------- Mapa ---------------------------
with col_mapa:
    st.subheader("Distribución territorial")

    gdf_merged = gdf.merge(df_filtrado, how="left", left_on="name", right_on="comuna")

    gdf_merged["valor_fmt"] = gdf_merged[metrica_col].apply(
        lambda x: formato_clp(x) if pd.notnull(x) else "Sin datos en este filtro"
    )

    mapa = folium.Map(location=[-33.45, -70.66], zoom_start=11, tiles="CartoDB positron")

    folium.Choropleth(
        geo_data=gdf_merged.to_json(),
        data=gdf_merged,
        columns=["comuna", metrica_col],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.8,
        line_opacity=0.3,
        nan_fill_color="lightgray",
        legend_name=metrica_label,
    ).add_to(mapa)

    folium.GeoJson(
        gdf_merged,
        style_function=lambda x: {"fillOpacity": 0, "color": "transparent"},
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "valor_fmt"],
            aliases=["Comuna", metrica_label],
            localize=True
        )
    ).add_to(mapa)

    st_folium(mapa, width=800, height=550)

# ----------------- Ranking ------------------------
with col_ranking:
    st.subheader(f"Ranking por {metrica_label}")

    df_ranking_fmt = df_ranking.copy()

    # Formato condicional según tipo de métrica
    if metrica_opcion in ["Venta total (millones de CLP)", "Ticket promedio (CLP)"]:
        df_ranking_fmt[metrica_col] = df_ranking_fmt[metrica_col].apply(formato_clp)
    else:
        df_ranking_fmt[metrica_col] = df_ranking_fmt[metrica_col].astype(int)

    st.dataframe(
    df_ranking_fmt[["comuna", metrica_col]]
    .rename(columns={"comuna": "Comuna", metrica_col: metrica_label}),
    use_container_width=True,
    hide_index=True,
    height=550
)



# --------------------------------------------------
# Top 10 comunas por venta total
# --------------------------------------------------
st.markdown("---")
st.subheader("Top 10 comunas por venta total")

df_top10 = df_agg.sort_values("venta_total", ascending=False).head(10).copy()
df_top10["venta_total_fmt"] = df_top10["venta_total"].apply(formato_clp)

# Barplot ordenado de mayor a menor
chart_top10 = (
    alt.Chart(df_top10)
    .mark_bar(color="#d95f0e")
    .encode(
        x=alt.X("venta_total:Q", title="Venta total (CLP)"),
        y=alt.Y("comuna:N", sort="-x", title="Comuna"),
        tooltip=[
            alt.Tooltip("comuna:N", title="Comuna"),
            alt.Tooltip("venta_total_fmt:N", title="Venta total"),
        ]
    )
    .properties(height=400)
)

st.altair_chart(chart_top10, use_container_width=True)


# --------------------------------------------------
# Scatter: pedidos vs venta total
# --------------------------------------------------
st.markdown("---")
st.subheader("Relación entre pedidos y venta total por comuna")

df_scatter = df_agg.copy()
df_scatter["venta_total_fmt"] = df_scatter["venta_total"].apply(formato_clp)

scatter = (
    alt.Chart(df_scatter)
    .mark_circle(size=120, opacity=0.7)
    .encode(
        x=alt.X("pedidos:Q", title="Número de pedidos"),
        y=alt.Y("venta_total:Q", title="Venta total (CLP)"),
        tooltip=[
            alt.Tooltip("comuna:N", title="Comuna"),
            alt.Tooltip("pedidos:Q", title="Pedidos"),
            alt.Tooltip("venta_total_fmt:N", title="Venta total"),
        ],
        color=alt.Color("venta_total:Q", scale=alt.Scale(scheme="yelloworangered"))
    )
    .properties(height=450)
)

st.altair_chart(scatter, use_container_width=True)

# --------------------------------------------------
# Reflexión
# --------------------------------------------------
st.markdown("---")
st.subheader("Reflexión sobre la interactividad")

st.markdown(
    f"""
    La interactividad del dashboard permite explorar cómo se distribuye **{metrica_label.lower()}**
    entre las distintas comunas de la Región Metropolitana, combinando una vista territorial
    (mapa) con una vista comparativa (ranking), además de análisis complementarios como el Top 10
    y la relación entre pedidos y valor económico.
    """
)

# 📊 Dashboard Territorial de Ventas y Volumen  
### Visualización geoespacial y análisis logístico para la Región Metropolitana  
**Curso:** Visualización de Datos en Python  
**Integrante:** Boris Jara Rojas  

---

## 🧭 Descripción general

Este repositorio contiene el código y los datos utilizados para construir un **dashboard interactivo en Streamlit**, cuyo objetivo es analizar la distribución territorial del **valor económico** y el **volumen de pedidos** en la Región Metropolitana de Santiago.

El dashboard integra:

- Mapas interactivos construidos con **Folium**  
- Gráficos estadísticos con **Altair**  
- KPIs y filtros dinámicos  
- Un ranking territorial configurable  
- Una reflexión sobre la interactividad aplicada  

El despliegue final se realiza en **Streamlit Cloud**, permitiendo explorar el comportamiento espacial de la demanda y su relación con el valor económico generado por comuna.

---

## 🚀 Demo en Streamlit

👉 *Enlace al dashboard:*  
https://dashboardindividual-xrmwzqkjxkl8m2l8tvyydp.streamlit.app/

---

## 🗂️ Estructura del repositorio

/dashboard_individual
│
├── app.py                         # Archivo principal del dashboard (Streamlit)
├── requirements.txt               # Dependencias necesarias para el despliegue
├── dataset_tarea_ind.xlsx         # Dataset base con ventas y pedidos
├── comunas_metropolitana-1.geojson# Polígonos territoriales de la RM
│
└── README.md                      # Documentación del proyecto


---

## 🧩 Funcionalidades principales del dashboard

### 🔹 1. KPIs generales
- Venta total regional  
- Total de pedidos  
- Ticket promedio  

### 🔹 2. Mapa de coropletas (Folium)
- Visualización territorial de:
  - Venta total (MM CLP)
  - Número de pedidos
  - Ticket promedio  
- Tooltip con valores formateados  
- Filtros dinámicos por rango  

### 🔹 3. Ranking por comuna
- Orden configurable  
- Selección del Top N  
- Formato condicional según métrica  

### 🔹 4. Gráficos complementarios
- **Top 10 comunas por venta total** (Altair)  
- **Scatter** pedidos vs venta total  
- Reflexión sobre la interactividad del dashboard  

---

## 🗺️ Interactividad implementada

El dashboard incorpora elementos interactivos que permiten:

- Filtrar comunas por rango de valores  
- Cambiar la métrica visualizada en el mapa  
- Ajustar dinámicamente el ranking territorial  
- Explorar relaciones entre volumen y valor económico  
- Navegar el mapa Folium con zoom, pan y tooltips  

Esta interactividad mejora la exploración geoespacial al permitir que el usuario:

- compare territorios,  
- identifique zonas críticas,  
- detecte patrones espaciales,  
- y conecte métricas operativas con métricas económicas.

---

## 🛠️ Tecnologías utilizadas

- **Python 3.11**  
- **Streamlit**  
- **Folium + streamlit-folium**  
- **GeoPandas**  
- **Altair**  
- **Pandas / NumPy**  
- **OpenPyXL**  

---

## 📦 Instalación local

1. Clonar el repositorio:
```bash
git clone https://github.com/je4icho/dashboard_individual
cd dashboard_individual

2. Instalar dependencias
pip install -r requirements.txt

3. Ejecutar dashboard
streamlit run app.py


import streamlit as st
import pandas as pd

# Datos de ejemplo de 16 startups
startups = [
    {"nombre": f"Startup {i+1}", "sector": "Tech", "empleados": 5 + i, "modelo": "B2B", "ubicacion": "Ciudad X"}
    for i in range(16)
]

st.set_page_config(page_title="Snapshot Startups", layout="wide")

st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .card {
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Snapshot de Startups")

# Filtros
sectores = list(set([s["sector"] for s in startups]))
modelo_negocios = list(set([s["modelo"] for s in startups]))

sector_filtro = st.selectbox("Filtrar por sector", options=["Todos"] + sectores)
modelo_filtro = st.selectbox("Filtrar por modelo de negocio", options=["Todos"] + modelo_negocios)

# Filtrado de datos
filtradas = startups
if sector_filtro != "Todos":
    filtradas = [s for s in filtradas if s["sector"] == sector_filtro]
if modelo_filtro != "Todos":
    filtradas = [s for s in filtradas if s["modelo"] == modelo_filtro]

# Paginación
page_size = 4
num_pages = (len(filtradas) - 1) // page_size + 1
page = st.number_input("Página", min_value=1, max_value=num_pages, step=1)

start = (page - 1) * page_size
end = start + page_size
current_startups = filtradas[start:end]

st.markdown(f"Mostrando página {page} de {num_pages}")

# Mostrar en tarjetas Bootstrap
cards_html = "<div class='container'><div class='row'>"
for startup in current_startups:
    cards_html += f"""
        <div class='col-md-3'>
            <div class='card'>
                <div class='card-body'>
                    <h5 class='card-title'>{startup['nombre']}</h5>
                    <p class='card-text'>
                        <strong>Sector:</strong> {startup['sector']}<br>
                        <strong>Modelo:</strong> {startup['modelo']}<br>
                        <strong>Empleados:</strong> {startup['empleados']}<br>
                        <strong>Ubicación:</strong> {startup['ubicacion']}
                    </p>
                </div>
            </div>
        </div>
    """
cards_html += "</div></div>"

st.markdown(cards_html, unsafe_allow_html=True)
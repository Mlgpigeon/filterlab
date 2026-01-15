"""
FilterLab - Explorador de Filtros de Imagen
Versión modularizada con cola de filtros, sin duplicados y actualización en tiempo real

Estructura:
    filterlab/
    ├── app.py              # Este archivo (punto de entrada)
    ├── filters/            # Definiciones e implementaciones de filtros
    │   ├── definitions.py  # Configuración de filtros
    │   ├── spatial.py      # Filtros espaciales
    │   └── morphological.py # Filtros morfológicos
    ├── core/               # Lógica de procesamiento
    │   ├── processor.py    # Aplicación de filtros
    │   └── utils.py        # Utilidades de imagen
    └── ui/                 # Componentes de interfaz
        ├── sidebar.py      # Panel lateral
        └── components.py   # Visualización y cola
"""

import streamlit as st

from core import apply_filter_chain, load_image
from ui import (
    render_sidebar,
    render_image_viewer,
    render_download_button,
    render_placeholder,
    render_filter_queue,
    render_footer,
)

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="FilterLab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================================

if 'filtros_activos' not in st.session_state:
    st.session_state.filtros_activos = []

if 'filter_params' not in st.session_state:
    st.session_state.filter_params = {}

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

# Título
st.title("🔬 FilterLab")
st.caption("Explorador de Filtros Espaciales y Morfológicos")

# Layout principal
col_main, col_queue = st.columns([3, 1])

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    img_rgb = render_sidebar()
    if img_rgb is not None:
        st.success(f"✅ Imagen cargada: {img_rgb.shape[1]}x{img_rgb.shape[0]}")


# ============================================================================
# COLUMNA PRINCIPAL - VISUALIZACIÓN
# ============================================================================

with col_main:
    if img_rgb is not None:
        # Preparar cadena de filtros
        filter_chain = [
            (f, st.session_state.filter_params.get(f, {}))
            for f in st.session_state.filtros_activos
        ]
        
        # Aplicar filtros
        if filter_chain:
            result_img = apply_filter_chain(img_rgb, filter_chain)
        else:
            result_img = img_rgb
        
        # Mostrar imágenes
        render_image_viewer(img_rgb, result_img)
        
        # Botón de descarga
        render_download_button(result_img)
    else:
        render_placeholder()

# ============================================================================
# COLUMNA DERECHA - COLA DE FILTROS
# ============================================================================

with col_queue:
    render_filter_queue()

# ============================================================================
# FOOTER
# ============================================================================

render_footer()

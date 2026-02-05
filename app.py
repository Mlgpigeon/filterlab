"""
FilterLab - Explorador de Filtros de Imagen
Versión con soporte de timeline para GIFs animados

Estructura:
    filterlab/
    ├── app.py              # Este archivo (punto de entrada)
    ├── filters/            # Definiciones e implementaciones de filtros
    │   ├── definitions.py  # Configuración de filtros
    │   ├── spatial.py      # Filtros espaciales
    │   ├── morphological.py # Filtros morfológicos
    │   └── segmentation.py  # Filtros de segmentación
    ├── core/               # Lógica de procesamiento
    │   ├── processor.py    # Aplicación de filtros
    │   ├── utils.py        # Utilidades de imagen
    │   ├── analysis.py     # Análisis de área
    │   └── batch.py        # Procesamiento batch
    └── ui/                 # Componentes de interfaz
        ├── sidebar.py      # Panel lateral
        ├── components.py   # Visualización y cola
        └── timeline.py     # Timeline para GIFs
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
    render_analysis_section,
    render_frame_timeline,
    render_frame_info,
    is_gif_loaded,
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
        # ================================================================
        # TIMELINE PARA GIFS
        # ================================================================
        if is_gif_loaded():
            # Mostrar timeline de navegación
            current_frame_idx = render_frame_timeline(start_year=2000)
            
            # Mostrar información del frame
            render_frame_info()
            
            st.markdown("---")
        
        # ================================================================
        # PROCESAMIENTO DE IMAGEN
        # ================================================================
        
        # Preparar cadena de filtros
        filter_chain = [
            (f, st.session_state.filter_params.get(f, {}))
            for f in st.session_state.filtros_activos
        ]
        
        # Aplicar filtros al frame actual
        if filter_chain:
            result_img = apply_filter_chain(img_rgb, filter_chain)
        else:
            result_img = img_rgb
        
        # ================================================================
        # VISUALIZACIÓN
        # ================================================================
        
        # Mostrar título con info del frame si es GIF
        if is_gif_loaded():
            current_idx = st.session_state.get('current_frame_idx', 0)
            year = 2000 + current_idx
            st.subheader(f"📅 Año {year} (Frame {current_idx + 1})")
        
        # Mostrar imágenes original y resultado
        render_image_viewer(img_rgb, result_img)
        
        # Botón de descarga
        render_download_button(result_img)
        
        # ================================================================
        # ANÁLISIS (HISTOGRAMAS Y ESTADÍSTICAS)
        # ================================================================
        
        render_analysis_section(img_rgb, result_img)
        
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

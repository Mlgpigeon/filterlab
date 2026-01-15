"""
Componentes del sidebar - Carga de imagen y controles de filtros.
"""

import streamlit as st
import numpy as np
import cv2
from PIL import Image

from filters import FILTROS_ESPACIALES, FILTROS_MORFOLOGICOS


def render_image_loader():
    """
    Renderiza el cargador de imágenes.
    
    Returns:
        numpy array de la imagen en RGB o None si no hay imagen
    """
    st.header("📁 Cargar Imagen")
    uploaded_file = st.file_uploader(
        "Selecciona una imagen",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        help="Formatos soportados: PNG, JPG, JPEG, BMP, TIFF"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        
        # Convertir a RGB si es necesario
        if len(img_array.shape) == 2:
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[2] == 4:
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        else:
            img_rgb = img_array
        
        st.success(f"✅ Imagen cargada: {img_rgb.shape[1]}x{img_rgb.shape[0]}")
        return img_rgb
    
    return None


def render_filter_controls(filter_dict, section_title, section_icon):
    """
    Renderiza los controles de un grupo de filtros.
    
    Args:
        filter_dict: Diccionario con definiciones de filtros
        section_title: Título de la sección
        section_icon: Icono para el título
    """
    st.header(f"{section_icon} {section_title}")
    
    for key, info in filter_dict.items():
        is_active = key in st.session_state.filtros_activos
        icon = "✅" if is_active else "⚪"
        
        with st.expander(f"{icon} {info['nombre']}", expanded=is_active):
            st.caption(info['descripcion'])
            
            # Inicializar parámetros si no existen
            if key not in st.session_state.filter_params:
                st.session_state.filter_params[key] = {
                    p: v['default'] for p, v in info['params'].items()
                }
            
            # Mostrar sliders para los parámetros
            current_params = {}
            for param_name, param_config in info['params'].items():
                val = st.slider(
                    param_config['label'],
                    min_value=param_config['min'],
                    max_value=param_config['max'],
                    value=st.session_state.filter_params[key].get(
                        param_name, param_config['default']
                    ),
                    step=param_config['step'],
                    key=f"{key}_{param_name}"
                )
                current_params[param_name] = val
            
            # Actualizar parámetros en session state
            st.session_state.filter_params[key] = current_params
            
            # Botón de añadir/quitar
            if is_active:
                if st.button(
                    f"❌ Quitar {info['nombre']}", 
                    key=f"remove_{key}", 
                    use_container_width=True
                ):
                    st.session_state.filtros_activos.remove(key)
                    st.rerun()
            else:
                if st.button(
                    f"➕ Añadir {info['nombre']}", 
                    key=f"add_{key}", 
                    use_container_width=True
                ):
                    st.session_state.filtros_activos.append(key)
                    st.rerun()


def render_sidebar():
    """
    Renderiza el sidebar completo.
    
    Returns:
        numpy array de la imagen en RGB o None si no hay imagen
    """
    img_rgb = render_image_loader()
    
    st.markdown("---")
    
    # Filtros Espaciales
    render_filter_controls(FILTROS_ESPACIALES, "Filtros Espaciales", "🎨")
    
    st.markdown("---")
    
    # Filtros Morfológicos
    render_filter_controls(FILTROS_MORFOLOGICOS, "Filtros Morfológicos", "🔷")
    
    return img_rgb

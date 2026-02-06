"""
Componentes del sidebar - Carga de imagen y controles de filtros.
Soporta carga de GIFs con múltiples frames.
"""

import streamlit as st
import numpy as np
import cv2
from PIL import Image

from filters import FILTROS_ESPACIALES, FILTROS_MORFOLOGICOS, FILTROS_SEGMENTACION


def render_image_loader():
    """
    Renderiza el cargador de imágenes.
    Soporta GIFs animados extrayendo todos los frames.
    
    Returns:
        numpy array de la imagen actual en RGB o None si no hay imagen
    """
    st.header("📁 Cargar Imagen")
    uploaded_file = st.file_uploader(
        "Selecciona una imagen",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif', 'webp'],
        help="Formatos soportados: PNG, JPG, JPEG, BMP, TIFF, GIF, WEBP"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        # Detectar si es un archivo animado (GIF/WEBP)
        n_frames = getattr(image, 'n_frames', 1)
        
        if n_frames > 1:
            # Es un archivo animado - extraer todos los frames
            frames = []
            for i in range(n_frames):
                image.seek(i)
                frame = image.convert('RGB')
                frame_array = np.array(frame)
                frames.append(frame_array)
            
            # Guardar frames en session_state
            st.session_state.gif_frames = frames
            st.session_state.gif_n_frames = n_frames
            st.session_state.gif_filename = uploaded_file.name
            
            # Inicializar índice del frame actual si no existe
            if 'current_frame_idx' not in st.session_state:
                st.session_state.current_frame_idx = 0
            
            # Asegurar que el índice esté dentro del rango
            if st.session_state.current_frame_idx >= n_frames:
                st.session_state.current_frame_idx = 0
            
            st.info(f"🎞️ Archivo animado: {n_frames} frames detectados")
            
            # Devolver el frame actual
            return frames[st.session_state.current_frame_idx]
        
        else:
            # Imagen estática normal
            # Limpiar datos de GIF si existían
            if 'gif_frames' in st.session_state:
                del st.session_state.gif_frames
            if 'gif_n_frames' in st.session_state:
                del st.session_state.gif_n_frames
            if 'current_frame_idx' in st.session_state:
                del st.session_state.current_frame_idx
            
            # Convertir a RGB
            image = image.convert('RGB')
            img_array = np.array(image)
            
            # Convertir a RGB si es necesario
            if len(img_array.shape) == 2:
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
            elif img_array.shape[2] == 4:
                img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
            else:
                img_rgb = img_array
            
            return img_rgb
    
    else:
        # No hay archivo - limpiar estado de GIF
        if 'gif_frames' in st.session_state:
            del st.session_state.gif_frames
        if 'gif_n_frames' in st.session_state:
            del st.session_state.gif_n_frames
        if 'current_frame_idx' in st.session_state:
            del st.session_state.current_frame_idx
    
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
            
            # Mostrar controles para los parámetros
            current_params = {}
            for param_name, param_config in info['params'].items():
                
                # Tipo 1: Slider (tiene min/max/step)
                if 'min' in param_config and 'max' in param_config:
                    val = st.slider(
                        param_config['label'],
                        min_value=param_config['min'],
                        max_value=param_config['max'],
                        value=st.session_state.filter_params[key].get(
                            param_name, param_config['default']
                        ),
                        step=param_config.get('step', 1),
                        key=f"{key}_{param_name}"
                    )
                    current_params[param_name] = val
                
                # Tipo 2: Selector (tiene options)
                elif 'options' in param_config:
                    val = st.selectbox(
                        param_config['label'],
                        options=param_config['options'],
                        index=param_config['options'].index(
                            st.session_state.filter_params[key].get(
                                param_name, param_config['default']
                            )
                        ),
                        key=f"{key}_{param_name}"
                    )
                    current_params[param_name] = val
                
                # Tipo 3: Checkbox (default es booleano)
                elif isinstance(param_config.get('default'), bool):
                    val = st.checkbox(
                        param_config['label'],
                        value=st.session_state.filter_params[key].get(
                            param_name, param_config['default']
                        ),
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
                ):
                    st.session_state.filtros_activos.remove(key)
                    st.rerun()
            else:
                if st.button(
                    f"➕ Añadir {info['nombre']}", 
                    key=f"add_{key}", 
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
    
    st.markdown("---")
    
    # Filtros de Segmentación
    render_filter_controls(FILTROS_SEGMENTACION, "Segmentación", "✂️")
    
    return img_rgb

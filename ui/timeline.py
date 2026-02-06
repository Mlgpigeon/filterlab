"""
Componente de Timeline para navegación de frames de GIF/animaciones.
"""

import streamlit as st

def _go_to_frame(idx: int):
    """Callback para cambiar de frame."""
    st.session_state.current_frame_idx = idx

def render_frame_timeline(start_year: int = 2000):
    """
    Renderiza la timeline de navegación para archivos animados (GIF/WEBP).
    """
    if 'gif_frames' not in st.session_state or 'gif_n_frames' not in st.session_state:
        return None
    
    n_frames = st.session_state.gif_n_frames
    
    # IMPORTANTE: Leer directamente de session_state, NO hacer una copia local
    if 'current_frame_idx' not in st.session_state:
        st.session_state.current_frame_idx = 0
    
    # Asegurar que el índice está en rango válido
    if st.session_state.current_frame_idx >= n_frames:
        st.session_state.current_frame_idx = n_frames - 1
    
    current_idx = st.session_state.current_frame_idx  # Solo para mostrar info
    
    st.markdown("---")
    st.markdown("### 🎬 Timeline de Frames")
    
    current_year = start_year + st.session_state.current_frame_idx
    st.markdown(f"**Frame {st.session_state.current_frame_idx + 1} de {n_frames}** | Año: **{current_year}**")
    
    # Controles de navegación
    col_first, col_prev, col_slider, col_next, col_last = st.columns([1, 1, 6, 1, 1])
    
    with col_first:
        st.button(
            "⏮️", 
            key="btn_first", 
            help="Ir al primer frame", 
            disabled=(st.session_state.current_frame_idx == 0),
            on_click=_go_to_frame,
            args=(0,)
        )
    
    with col_prev:
        st.button(
            "◀️", 
            key="btn_prev", 
            help="Frame anterior", 
            disabled=(st.session_state.current_frame_idx == 0),
            on_click=_go_to_frame,
            args=(max(0, st.session_state.current_frame_idx - 1),)
        )
    
    with col_slider:
        # CLAVE: El slider debe leer Y escribir directamente en session_state
        st.slider(
            "Frame",
            min_value=0,
            max_value=n_frames - 1,
            value=st.session_state.current_frame_idx,  # Lee el valor actual
            format=f"Frame %d",
            key="frame_slider_control",  # Nombre diferente para evitar conflictos
            label_visibility="collapsed",
            on_change=lambda: setattr(st.session_state, 'current_frame_idx', st.session_state.frame_slider_control)
        )
    
    with col_next:
        st.button(
            "▶️", 
            key="btn_next", 
            help="Frame siguiente", 
            disabled=(st.session_state.current_frame_idx >= n_frames - 1),
            on_click=_go_to_frame,
            args=(min(n_frames - 1, st.session_state.current_frame_idx + 1),)
        )
    
    with col_last:
        st.button(
            "⏭️", 
            key="btn_last", 
            help="Ir al último frame", 
            disabled=(st.session_state.current_frame_idx >= n_frames - 1),
            on_click=_go_to_frame,
            args=(n_frames - 1,)
        )
    
    # Mostrar barra de años
    _render_year_bar(n_frames, st.session_state.current_frame_idx, start_year)
    
    return st.session_state.current_frame_idx

def _render_year_bar(n_frames: int, current_idx: int, start_year: int):
    """
    Renderiza una barra visual con los años y el frame actual destacado.
    """
    # Determinar cuántos años mostrar (max 10 para no saturar)
    if n_frames <= 10:
        step = 1
    elif n_frames <= 20:
        step = 2
    else:
        step = max(1, n_frames // 10)
    
    # Crear marcadores de años
    years_display = []
    for i in range(0, n_frames, step):
        year = start_year + i
        if i == current_idx:
            years_display.append(f"**[{year}]**")
        else:
            years_display.append(str(year))
    
    # Añadir el último año si no está incluido
    if (n_frames - 1) % step != 0:
        last_year = start_year + n_frames - 1
        if current_idx == n_frames - 1:
            years_display.append(f"**[{last_year}]**")
        else:
            years_display.append(str(last_year))
    
    # Mostrar la barra de años
    st.caption(" · ".join(years_display))


def render_frame_info():
    """
    Renderiza información detallada del frame actual.
    """
    if 'gif_frames' not in st.session_state:
        return
    
    current_idx = st.session_state.get('current_frame_idx', 0)
    frame = st.session_state.gif_frames[current_idx]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Frame", f"{current_idx + 1}/{st.session_state.gif_n_frames}")
    
    with col2:
        st.metric("Resolución", f"{frame.shape[1]}x{frame.shape[0]}")
    
    with col3:
        if 'gif_filename' in st.session_state:
            st.metric("Archivo", st.session_state.gif_filename[:15] + "...")


def render_mini_timeline_thumbnails(max_thumbnails: int = 10):
    """
    Renderiza miniaturas de los frames como timeline visual clickeable.
    
    Args:
        max_thumbnails: Número máximo de miniaturas a mostrar
    """
    if 'gif_frames' not in st.session_state:
        return
    
    frames = st.session_state.gif_frames
    n_frames = len(frames)
    current_idx = st.session_state.get('current_frame_idx', 0)
    
    # Calcular qué frames mostrar
    if n_frames <= max_thumbnails:
        indices_to_show = list(range(n_frames))
    else:
        # Mostrar frames distribuidos uniformemente
        step = n_frames / max_thumbnails
        indices_to_show = [int(i * step) for i in range(max_thumbnails)]
        # Asegurar que el último frame esté incluido
        if indices_to_show[-1] != n_frames - 1:
            indices_to_show[-1] = n_frames - 1
    
    # Crear columnas para las miniaturas
    cols = st.columns(len(indices_to_show))
    
    for col, idx in zip(cols, indices_to_show):
        with col:
            # Resaltar el frame actual
            if idx == current_idx:
                st.markdown("🔽")
            
            # Mostrar miniatura
            frame = frames[idx]
            # Redimensionar para miniatura
            import cv2
            thumbnail = cv2.resize(frame, (60, 60))
            
            if st.button(
                f"{2000 + idx}",
                key=f"thumb_{idx}",
                help=f"Ir a frame {idx + 1} (año {2000 + idx})",
                use_container_width=True
            ):
                st.session_state.current_frame_idx = idx
                st.rerun()


def is_gif_loaded() -> bool:
    """
    Verifica si hay un GIF cargado en session_state.
    
    Returns:
        bool: True si hay un GIF cargado
    """
    return 'gif_frames' in st.session_state and st.session_state.gif_n_frames > 1


def get_current_frame():
    """
    Obtiene el frame actual del GIF.
    
    Returns:
        numpy.ndarray o None: El frame actual o None si no hay GIF
    """
    if not is_gif_loaded():
        return None
    
    current_idx = st.session_state.get('current_frame_idx', 0)
    return st.session_state.gif_frames[current_idx]


def get_all_frames():
    """
    Obtiene todos los frames del GIF.
    
    Returns:
        list o None: Lista de frames o None si no hay GIF
    """
    if not is_gif_loaded():
        return None
    
    return st.session_state.gif_frames

"""
Componentes de la interfaz principal - Visualización y cola de filtros.
"""

import streamlit as st
from PIL import Image
import io

from filters import get_filter_info


def render_image_viewer(img_original, img_result):
    """
    Renderiza el visor de imágenes lado a lado.
    
    Args:
        img_original: Imagen original (numpy array)
        img_result: Imagen procesada (numpy array)
    """
    col_orig, col_result = st.columns(2)
    
    with col_orig:
        st.subheader("Original")
        st.image(img_original, use_container_width=True)
    
    with col_result:
        st.subheader("Resultado")
        st.image(img_result, use_container_width=True, clamp=True)


def render_download_button(img_result):
    """
    Renderiza el botón de descarga.
    
    Args:
        img_result: Imagen procesada (numpy array)
    """
    st.markdown("---")
    
    result_pil = Image.fromarray(img_result)
    buf = io.BytesIO()
    result_pil.save(buf, format='PNG')
    
    st.download_button(
        label="📥 Descargar resultado",
        data=buf.getvalue(),
        file_name="filterlab_resultado.png",
        mime="image/png",
        use_container_width=True
    )


def render_placeholder():
    """Renderiza el placeholder cuando no hay imagen cargada."""
    st.info("👈 Carga una imagen desde el panel lateral para comenzar")
    
    st.markdown("""
    ### Cómo usar FilterLab:
    
    1. **Cargar imagen** - Usa el panel izquierdo para subir una imagen
    2. **Añadir filtros** - Selecciona filtros y ajusta sus parámetros
    3. **Ver resultado** - La imagen se actualiza en tiempo real
    4. **Reordenar** - Usa la cola de la derecha para cambiar el orden
    5. **Descargar** - Guarda el resultado cuando estés satisfecho
    """)


def render_filter_queue():
    """Renderiza la cola de filtros activos."""
    st.subheader("📋 Cola de Filtros")
    
    if st.session_state.filtros_activos:
        st.caption(f"{len(st.session_state.filtros_activos)} filtro(s) activo(s)")
        
        for idx, filter_key in enumerate(st.session_state.filtros_activos):
            info = get_filter_info(filter_key)
            params = st.session_state.filter_params.get(filter_key, {})
            
            with st.container():
                # Card del filtro
                st.markdown(f"""
                <div style="
                    background-color: #1E1E1E;
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 8px;
                    border-left: 4px solid #4CAF50;
                ">
                    <div style="font-weight: bold; color: #4CAF50;">
                        {idx + 1}. {info['nombre']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar parámetros actuales
                if params:
                    param_str = ", ".join([f"{k}={v}" for k, v in params.items()])
                    st.caption(f"   └─ {param_str}")
                
                # Botones de reordenar
                col_up, col_down, col_del = st.columns(3)
                
                with col_up:
                    if idx > 0:
                        if st.button("⬆️", key=f"up_{idx}", help="Subir"):
                            _swap_filters(idx, idx - 1)
                
                with col_down:
                    if idx < len(st.session_state.filtros_activos) - 1:
                        if st.button("⬇️", key=f"down_{idx}", help="Bajar"):
                            _swap_filters(idx, idx + 1)
                
                with col_del:
                    if st.button("🗑️", key=f"del_{idx}", help="Eliminar"):
                        st.session_state.filtros_activos.pop(idx)
                        st.rerun()
        
        st.markdown("---")
        
        # Botón para limpiar todo
        if st.button("🗑️ Limpiar todo", use_container_width=True, type="secondary"):
            st.session_state.filtros_activos = []
            st.rerun()
    
    else:
        st.info("No hay filtros activos")
        st.caption("Añade filtros desde el panel izquierdo")


def _swap_filters(idx1, idx2):
    """Intercambia dos filtros en la cola."""
    filters = st.session_state.filtros_activos
    filters[idx1], filters[idx2] = filters[idx2], filters[idx1]
    st.rerun()


def render_footer():
    """Renderiza el footer de la aplicación."""
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>
        FilterLab | Visión Artificial - UNIR 2025<br>
        Basado en OpenCV
        </small>
    </div>
    """, unsafe_allow_html=True)

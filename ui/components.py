"""
Componentes de la interfaz principal - Visualización y cola de filtros.
"""

import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io

from filters import get_filter_info


def _ensure_rgb(img):
    """Asegura que la imagen sea RGB (3 canales)."""
    if img.ndim == 2:
        return np.stack([img, img, img], axis=2)
    elif img.ndim == 3 and img.shape[2] == 1:
        return np.concatenate([img, img, img], axis=2)
    return img


def _create_histogram_figure(img, title, show_rgb=True):
    """
    Crea una figura de histograma.
    
    Args:
        img: Imagen numpy array (RGB o escala de grises)
        title: Título del gráfico
        show_rgb: Si True muestra canales RGB, si False escala de grises
    
    Returns:
        Figura matplotlib
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    
    # Asegurar que la imagen tenga 3 canales
    img = _ensure_rgb(img)
    
    if show_rgb:
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        labels = ['Rojo', 'Verde', 'Azul']
        for i, (color, label) in enumerate(zip(colors, labels)):
            hist = np.histogram(img[:, :, i].flatten(), bins=256, range=(0, 256))[0]
            ax.fill_between(range(256), hist, alpha=0.3, color=color, label=label)
            ax.plot(hist, color=color, linewidth=1)
    else:
        gray = np.mean(img, axis=2).astype(np.uint8)
        hist = np.histogram(gray.flatten(), bins=256, range=(0, 256))[0]
        ax.fill_between(range(256), hist, alpha=0.5, color='#FFFFFF')
        ax.plot(hist, color='#FFFFFF', linewidth=1)
    
    ax.set_title(title, color='white', fontsize=12, fontweight='bold')
    ax.set_xlabel('Intensidad', color='gray')
    ax.set_ylabel('Frecuencia', color='gray')
    ax.set_xlim(0, 255)
    ax.tick_params(colors='gray')
    ax.spines['bottom'].set_color('gray')
    ax.spines['left'].set_color('gray')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    if show_rgb:
        ax.legend(loc='upper right', facecolor='#1E1E1E', edgecolor='gray', labelcolor='white')
    
    plt.tight_layout()
    return fig


def _create_comparison_histogram(img_orig, img_result, channel='gray'):
    """
    Crea histograma comparativo original vs resultado.
    
    Args:
        img_orig: Imagen original
        img_result: Imagen procesada
        channel: 'gray', 'red', 'green', 'blue'
    
    Returns:
        Figura matplotlib
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    
    # Asegurar que las imágenes tengan 3 canales
    img_orig = _ensure_rgb(img_orig)
    img_result = _ensure_rgb(img_result)
    
    channel_map = {'gray': -1, 'red': 0, 'green': 1, 'blue': 2}
    ch = channel_map.get(channel, -1)
    
    if ch == -1:
        orig_data = np.mean(img_orig, axis=2).flatten()
        result_data = np.mean(img_result, axis=2).flatten()
        color_orig, color_result = '#888888', '#FFFFFF'
        title = 'Histograma Escala de Grises'
    else:
        orig_data = img_orig[:, :, ch].flatten()
        result_data = img_result[:, :, ch].flatten()
        colors = {'red': '#FF6B6B', 'green': '#4ECDC4', 'blue': '#45B7D1'}
        color_orig = colors[channel]
        color_result = colors[channel]
        title = f'Histograma Canal {channel.capitalize()}'
    
    hist_orig = np.histogram(orig_data, bins=256, range=(0, 256))[0]
    hist_result = np.histogram(result_data, bins=256, range=(0, 256))[0]
    
    ax.fill_between(range(256), hist_orig, alpha=0.3, color=color_orig, label='Original')
    ax.plot(hist_orig, color=color_orig, linewidth=1, linestyle='--', alpha=0.7)
    
    ax.fill_between(range(256), hist_result, alpha=0.5, color=color_result, label='Resultado')
    ax.plot(hist_result, color=color_result, linewidth=1.5)
    
    ax.set_title(title, color='white', fontsize=12, fontweight='bold')
    ax.set_xlabel('Intensidad', color='gray')
    ax.set_ylabel('Frecuencia', color='gray')
    ax.set_xlim(0, 255)
    ax.tick_params(colors='gray')
    ax.spines['bottom'].set_color('gray')
    ax.spines['left'].set_color('gray')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(loc='upper right', facecolor='#1E1E1E', edgecolor='gray', labelcolor='white')
    
    plt.tight_layout()
    return fig


def _create_stats_figure(img_orig, img_result):
    """
    Crea figura con estadísticas comparativas.
    """
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.patch.set_facecolor('#0E1117')
    
    # Asegurar que las imágenes tengan 3 canales
    img_orig = _ensure_rgb(img_orig)
    img_result = _ensure_rgb(img_result)
    
    for ax, img, title in [(axes[0], img_orig, 'Original'), (axes[1], img_result, 'Resultado')]:
        ax.set_facecolor('#0E1117')
        
        # Calcular estadísticas
        gray = np.mean(img, axis=2)
        stats = {
            'Media': np.mean(gray),
            'Desv. Std': np.std(gray),
            'Min': np.min(gray),
            'Max': np.max(gray),
            'Contraste': np.max(gray) - np.min(gray)
        }
        
        # Crear barras
        names = list(stats.keys())
        values = list(stats.values())
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0']
        
        bars = ax.barh(names, values, color=colors, alpha=0.8)
        ax.set_title(title, color='white', fontsize=12, fontweight='bold')
        ax.set_xlim(0, 260)
        ax.tick_params(colors='gray')
        ax.spines['bottom'].set_color('gray')
        ax.spines['left'].set_color('gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Añadir valores
        for bar, val in zip(bars, values):
            ax.text(val + 5, bar.get_y() + bar.get_height()/2, 
                   f'{val:.1f}', va='center', color='white', fontsize=9)
    
    plt.tight_layout()
    return fig


def _fig_to_bytes(fig, format='png'):
    """Convierte figura matplotlib a bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format=format, facecolor=fig.get_facecolor(), 
                edgecolor='none', bbox_inches='tight', dpi=150)
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


def render_analysis_section(img_original, img_result):
    """
    Renderiza la sección desplegable con histogramas y gráficos.
    
    Args:
        img_original: Imagen original (numpy array)
        img_result: Imagen procesada (numpy array)
    """
    with st.expander("📊 Análisis y Gráficos", expanded=False):
        st.caption("Histogramas y estadísticas con descarga individual")
        
        # Tabs para organizar los gráficos
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎨 RGB Comparativo", 
            "⬜ Escala de Grises", 
            "📈 Por Canal",
            "📋 Estadísticas"
        ])
        
        # Tab 1: Histogramas RGB
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_orig_rgb = _create_histogram_figure(img_original, "Original - RGB", show_rgb=True)
                st.pyplot(fig_orig_rgb)
                st.download_button(
                    "📥 Descargar",
                    data=_fig_to_bytes(fig_orig_rgb),
                    file_name="histograma_original_rgb.png",
                    mime="image/png",
                    key="dl_orig_rgb"
                )
            
            with col2:
                fig_result_rgb = _create_histogram_figure(img_result, "Resultado - RGB", show_rgb=True)
                st.pyplot(fig_result_rgb)
                st.download_button(
                    "📥 Descargar",
                    data=_fig_to_bytes(fig_result_rgb),
                    file_name="histograma_resultado_rgb.png",
                    mime="image/png",
                    key="dl_result_rgb"
                )
        
        # Tab 2: Escala de grises comparativo
        with tab2:
            fig_gray_comp = _create_comparison_histogram(img_original, img_result, 'gray')
            st.pyplot(fig_gray_comp)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.download_button(
                    "📥 Descargar Comparativa",
                    data=_fig_to_bytes(fig_gray_comp),
                    file_name="histograma_comparativo_gris.png",
                    mime="image/png",
                    key="dl_gray_comp",
                    use_container_width=True
                )
        
        # Tab 3: Por canal individual
        with tab3:
            channel_selected = st.selectbox(
                "Seleccionar canal:",
                ['red', 'green', 'blue'],
                format_func=lambda x: {'red': '🔴 Rojo', 'green': '🟢 Verde', 'blue': '🔵 Azul'}[x],
                key="channel_select"
            )
            
            fig_channel = _create_comparison_histogram(img_original, img_result, channel_selected)
            st.pyplot(fig_channel)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.download_button(
                    f"📥 Descargar Canal {channel_selected.capitalize()}",
                    data=_fig_to_bytes(fig_channel),
                    file_name=f"histograma_canal_{channel_selected}.png",
                    mime="image/png",
                    key=f"dl_channel_{channel_selected}",
                    use_container_width=True
                )
        
        # Tab 4: Estadísticas
        with tab4:
            fig_stats = _create_stats_figure(img_original, img_result)
            st.pyplot(fig_stats)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.download_button(
                    "📥 Descargar Estadísticas",
                    data=_fig_to_bytes(fig_stats),
                    file_name="estadisticas_comparativa.png",
                    mime="image/png",
                    key="dl_stats",
                    use_container_width=True
                )
            
            # Tabla de estadísticas numéricas
            st.markdown("---")
            st.markdown("**Valores numéricos:**")
            
            img_orig_rgb = _ensure_rgb(img_original)
            img_result_rgb = _ensure_rgb(img_result)
            gray_orig = np.mean(img_orig_rgb, axis=2)
            gray_result = np.mean(img_result_rgb, axis=2)
            
            col_stat1, col_stat2 = st.columns(2)
            
            with col_stat1:
                st.markdown("**Original**")
                st.markdown(f"- Media: `{np.mean(gray_orig):.2f}`")
                st.markdown(f"- Desv. Std: `{np.std(gray_orig):.2f}`")
                st.markdown(f"- Rango: `{np.min(gray_orig):.0f}` - `{np.max(gray_orig):.0f}`")
            
            with col_stat2:
                st.markdown("**Resultado**")
                st.markdown(f"- Media: `{np.mean(gray_result):.2f}`")
                st.markdown(f"- Desv. Std: `{np.std(gray_result):.2f}`")
                st.markdown(f"- Rango: `{np.min(gray_result):.0f}` - `{np.max(gray_result):.0f}`")


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

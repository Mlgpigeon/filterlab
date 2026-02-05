"""
Análisis temporal para series de imágenes (GIF/secuencias).
Genera gráficos de evolución de área deforestada.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from core.analysis import AnalisisArea
from core import apply_filter_chain
import io


def render_temporal_analysis_section():
    """
    Renderiza la sección de análisis temporal para GIFs.
    Procesa todos los frames y genera gráficos de evolución.
    """
    if 'gif_frames' not in st.session_state:
        return
    
    with st.expander("📈 Análisis Temporal (Serie Completa)", expanded=False):
        st.caption("Procesa TODOS los frames del GIF y genera gráficos de evolución")
        
        col1, col2 = st.columns(2)
        with col1:
            pixels_escala = st.number_input("Píxeles en escala", value=51, min_value=1, key="temp_px")
        with col2:
            km_escala = st.number_input("Km en escala", value=20.0, min_value=0.1, key="temp_km")
        
        col3, col4 = st.columns(2)
        with col3:
            start_year = st.number_input("Año inicial", value=2000, min_value=1900, max_value=2100, key="start_yr")
        with col4:
            contar_blancos = st.checkbox("Contar blancos (deforestado)", value=True, key="temp_blancos")
        
        if st.button("🚀 Procesar Toda la Serie", use_container_width=True, type="primary"):
            _run_temporal_analysis(pixels_escala, km_escala, start_year, contar_blancos)
        
        # Mostrar resultados si existen
        if 'temporal_results' in st.session_state:
            _display_temporal_results(start_year)


def _run_temporal_analysis(pixels_escala, km_escala, start_year, contar_blancos):
    """Ejecuta el análisis en todos los frames."""
    frames = st.session_state.gif_frames
    n_frames = len(frames)
    
    # Obtener pipeline de filtros actual
    filter_chain = [
        (f, st.session_state.filter_params.get(f, {}))
        for f in st.session_state.filtros_activos
    ]
    
    analizador = AnalisisArea.desde_escala(pixels_escala, km_escala)
    
    results = []
    progress = st.progress(0, text="Procesando frames...")
    
    for i, frame in enumerate(frames):
        # Aplicar filtros
        if filter_chain:
            processed = apply_filter_chain(frame, filter_chain)
        else:
            processed = frame
        
        # Calcular área
        area_result = analizador.calcular_area(processed, contar_blancos)
        
        year = start_year + i
        results.append({
            'year': year,
            'frame': i,
            'area_km2': area_result.area_km2,
            'area_ha': area_result.area_ha,
            'porcentaje': area_result.porcentaje_blanco if contar_blancos else area_result.porcentaje_negro,
            'pixels': area_result.pixels_blancos if contar_blancos else area_result.pixels_negros
        })
        
        progress.progress((i + 1) / n_frames, text=f"Procesando frame {i+1}/{n_frames} (Año {year})")
    
    progress.empty()
    st.session_state.temporal_results = results
    st.success(f"✅ Procesados {n_frames} frames")


def _display_temporal_results(start_year):
    """Muestra los resultados del análisis temporal."""
    results = st.session_state.temporal_results
    
    years = [r['year'] for r in results]
    areas = [r['area_km2'] for r in results]
    
    # Tabs para diferentes visualizaciones
    tab1, tab2, tab3 = st.tabs(["📊 Área Acumulada", "📈 Deforestación Anual", "📋 Datos"])
    
    with tab1:
        fig1 = _create_accumulated_chart(years, areas)
        st.pyplot(fig1)
        st.download_button(
            "📥 Descargar gráfico",
            data=_fig_to_bytes(fig1),
            file_name="area_acumulada.png",
            mime="image/png"
        )
    
    with tab2:
        fig2 = _create_annual_chart(years, areas)
        st.pyplot(fig2)
        st.download_button(
            "📥 Descargar gráfico",
            data=_fig_to_bytes(fig2),
            file_name="deforestacion_anual.png",
            mime="image/png"
        )
    
    with tab3:
        # Tabla de datos
        st.dataframe(results, use_container_width=True)
        
        # CSV export
        csv = _results_to_csv(results)
        st.download_button(
            "📥 Descargar CSV",
            data=csv,
            file_name="analisis_temporal.csv",
            mime="text/csv"
        )
        
        # Estadísticas
        st.markdown("### Estadísticas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Área mínima", f"{min(areas):.2f} km²")
        with col2:
            st.metric("Área máxima", f"{max(areas):.2f} km²")
        with col3:
            st.metric("Cambio total", f"{areas[-1] - areas[0]:.2f} km²")
        
        # Tendencia lineal
        if len(areas) > 1:
            slope = np.polyfit(range(len(areas)), areas, 1)[0]
            st.metric("Tendencia", f"{slope:.2f} km²/año")


def _create_accumulated_chart(years, areas):
    """Crea gráfico de área acumulada."""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    
    ax.fill_between(years, areas, alpha=0.3, color='#FF6B6B')
    ax.plot(years, areas, color='#FF6B6B', linewidth=2, marker='o', markersize=6)
    
    ax.set_title('Área Acumulada de Deforestación', color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel('Año', color='gray')
    ax.set_ylabel('Área (km²)', color='gray')
    ax.tick_params(colors='gray')
    ax.spines['bottom'].set_color('gray')
    ax.spines['left'].set_color('gray')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    return fig


def _create_annual_chart(years, areas):
    """Crea gráfico de deforestación anual (diferencias)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    
    # Calcular cambio anual
    annual_change = [areas[0]] + [areas[i] - areas[i-1] for i in range(1, len(areas))]
    
    colors = ['#4CAF50' if v >= 0 else '#2196F3' for v in annual_change]
    ax.bar(years, annual_change, color=colors, alpha=0.8, edgecolor='white', linewidth=0.5)
    
    # Línea de tendencia
    z = np.polyfit(range(len(annual_change)), annual_change, 1)
    p = np.poly1d(z)
    ax.plot(years, p(range(len(years))), '--', color='#FFD700', linewidth=2, label=f'Tendencia: {z[0]:.1f} km²/año')
    
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5)
    ax.set_title('Deforestación Anual', color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel('Año', color='gray')
    ax.set_ylabel('Cambio (km²)', color='gray')
    ax.tick_params(colors='gray')
    ax.spines['bottom'].set_color('gray')
    ax.spines['left'].set_color('gray')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.legend(facecolor='#1E1E1E', edgecolor='gray', labelcolor='white')
    
    plt.tight_layout()
    return fig


def _fig_to_bytes(fig):
    """Convierte figura a bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', facecolor=fig.get_facecolor(), dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()


def _results_to_csv(results):
    """Convierte resultados a CSV."""
    lines = ["Año,Frame,Área (km²),Área (ha),Porcentaje,Píxeles"]
    for r in results:
        lines.append(f"{r['year']},{r['frame']},{r['area_km2']:.4f},{r['area_ha']:.4f},{r['porcentaje']:.2f},{r['pixels']}")
    return "\n".join(lines)
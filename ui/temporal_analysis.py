"""
Análisis temporal para series de imágenes (GIF/secuencias).
Genera gráficos de evolución de área.
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
        st.caption("Procesa todos los frames y genera análisis estadístico de evolución")
        
        col1, col2 = st.columns(2)
        with col1:
            pixels_escala = st.number_input("Píxeles en escala", value=51, min_value=1, key="temp_px")
        with col2:
            km_escala = st.number_input("Km en escala", value=20.0, min_value=0.1, key="temp_km")
        
        contar_blancos = st.checkbox("Contar píxeles blancos (área de interés)", value=True, key="temp_blancos")
        
        if st.button("🚀 Procesar Toda la Serie", type="primary"):
            _run_temporal_analysis(pixels_escala, km_escala, contar_blancos)
        
        # Mostrar resultados si existen
        if 'temporal_results' in st.session_state:
            _display_temporal_results()


def _run_temporal_analysis(pixels_escala, km_escala, contar_blancos):
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
        
        results.append({
            'frame': i + 1,  # Frame number (1-indexed for display)
            'area_km2': area_result.area_km2,
            'area_ha': area_result.area_ha,
            'porcentaje': area_result.porcentaje_blanco if contar_blancos else area_result.porcentaje_negro,
            'pixels': area_result.pixels_blancos if contar_blancos else area_result.pixels_negros
        })
        
        progress.progress((i + 1) / n_frames, text=f"Procesando frame {i+1}/{n_frames}")
    
    progress.empty()
    st.session_state.temporal_results = results
    st.success(f"✅ Procesados {n_frames} frames")


def _display_temporal_results():
    """Muestra los resultados del análisis temporal."""
    results = st.session_state.temporal_results
    
    frames = [r['frame'] for r in results]
    areas = [r['area_km2'] for r in results]
    
    # Calcular estadísticas
    stats = _create_statistics_summary(results)
    
    # Tabs para diferentes visualizaciones
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Resumen Estadístico", 
        "📈 Gráficos",
        "⚠️ Frames Críticos",
        "📋 Datos Completos",
        "📊 Tabla Visual"
    ])

    
    with tab1:
        st.markdown("### Resumen Estadístico")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Área Inicial (Frame 1)", f"{stats['area_inicial']:.0f} km²")
        with col2:
            st.metric(f"Área Final (Frame {len(results)})", f"{stats['area_total']:.0f} km²")
        with col3:
            st.metric("Cambio Total", f"+{stats['cambio_total']:.0f} km²", 
                     delta=f"{(stats['cambio_total']/stats['area_inicial']*100):.1f}%")
        with col4:
            slope = np.polyfit(range(len(areas)), areas, 1)[0]
            st.metric("Tendencia", f"{slope:.2f} km²/frame")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Promedio", f"{stats['promedio']:.0f} km²")
        with col2:
            st.metric("Mediana", f"{stats['mediana']:.0f} km²")
        with col3:
            st.metric("Desviación Estándar", f"{stats['std']:.0f} km²")
    
    with tab2:
        fig_comp = _create_comparison_plot(frames, areas)
        st.pyplot(fig_comp, clear_figure=True)
        st.download_button(
            "📥 Descargar gráfico combinado",
            data=_fig_to_bytes(fig_comp),
            file_name="comparacion_temporal.png",
            mime="image/png",
            key="dl_temporal_comp"
        )
    
    with tab3:
        st.markdown(f"### Frames con Valores Críticos")
        st.caption(f"Frames con área > {stats['promedio'] + stats['std']:.0f} km² "
                f"(promedio + 1 desviación estándar)")
        
        if stats['critical_periods']:
            critical_df = {
                'Frame': [r['frame'] for r in stats['critical_periods']],
                'Área (km²)': [f"{r['area_km2']:.2f}" for r in stats['critical_periods']],
                'Desviación': [f"+{r['area_km2'] - stats['promedio']:.2f}" for r in stats['critical_periods']]
            }
            st.dataframe(critical_df, use_container_width=True)
            
            avg_critical = np.mean([r['area_km2'] for r in stats['critical_periods']])
            st.info(f"📌 Área promedio en frames críticos: **{avg_critical:.0f} km²**")
        else:
             st.success("✅ No se detectaron frames con valores significativamente superiores al promedio")
    
    with tab4:
        st.dataframe(results, use_container_width=True)
        
        csv = _results_to_csv(results)
        st.download_button(
            "📥 Descargar CSV",
            data=csv,
            file_name="analisis_temporal.csv",
            mime="text/csv",
            key="dl_temporal_csv"
        )
    with tab5:
        st.caption("Tabla de resultados con formato profesional para exportar")
        fig_table = _create_results_table_figure(results)
        st.pyplot(fig_table, clear_figure=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.download_button(
                "📥 Descargar tabla (PNG)",
                data=_fig_to_bytes(fig_table),
                file_name="tabla_resultados_frames.png",
                mime="image/png",
                key="dl_table_visual"
            )


def _create_statistics_summary(results):
    """Crea resumen estadístico detallado."""
    areas = [r['area_km2'] for r in results]
    
    area_total = areas[-1]
    area_inicial = areas[0]
    cambio_total = area_total - area_inicial
    promedio = np.mean(areas)
    mediana = np.median(areas)
    std = np.std(areas)
    
    threshold = promedio + std
    critical_periods = [r for r in results if r['area_km2'] > threshold]
    
    return {
        'area_total': area_total,
        'area_inicial': area_inicial,
        'cambio_total': cambio_total,
        'promedio': promedio,
        'mediana': mediana,
        'std': std,
        'critical_periods': critical_periods,
        'n_critical': len(critical_periods)
    }


def _create_comparison_plot(frames, areas):
    """Crea gráfico combinado: acumulado, incremental y tendencia."""
    import numpy as np
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
    fig.patch.set_facecolor('white')
    
    # --- Gráfico 1: Área Acumulada ---
    ax1.set_facecolor('white')
    ax1.fill_between(frames, areas, alpha=0.4, color='#FF6B6B', label='Área Acumulada')
    ax1.plot(frames, areas, color='#FF0000', linewidth=2.5, marker='o', markersize=6)
    
    # Línea de tendencia
    z = np.polyfit(frames, areas, 1)
    p = np.poly1d(z)
    ax1.plot(frames, p(frames), '--', color='#000000', linewidth=2, 
             label=f'Tendencia: y = {z[0]:.2f}x + {z[1]:.2f}')
    
    ax1.set_title('Área Acumulada', fontsize=14, fontweight='bold', color='black')
    ax1.set_ylabel('Área Acumulada (km²)', fontsize=11, color='black')
    ax1.tick_params(colors='black')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # --- Gráfico 2: Cambio Incremental ---
    ax2.set_facecolor('white')
    cambios = [areas[0]] + [areas[i] - areas[i-1] for i in range(1, len(areas))]
    
    colors = ['#4CAF50' if v >= 0 else '#F44336' for v in cambios]
    ax2.bar(frames, cambios, color=colors, alpha=0.8, edgecolor='black', linewidth=0.8)
    
    # Valores en barras significativas
    for i, (frame, cambio) in enumerate(zip(frames, cambios)):
        if abs(cambio) > np.mean(np.abs(cambios)):
            ax2.text(frame, cambio + (50 if cambio > 0 else -50), 
                    f'{cambio:.0f}', ha='center', fontsize=8, fontweight='bold')
    
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_title('Cambio Incremental por Frame', fontsize=14, fontweight='bold', color='black')
    ax2.set_ylabel('Cambio (km²)', fontsize=11, color='black')
    ax2.tick_params(colors='black')
    ax2.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # --- Gráfico 3: Comparación Acumulado vs Incremental ---
    ax3_twin = ax3.twinx()
    
    ax3.plot(frames, areas, color='#FF0000', linewidth=2.5, marker='o', 
             markersize=6, label='Acumulado')
    ax3_twin.bar(frames, cambios, alpha=0.6, color='#FFA500', 
                 edgecolor='black', linewidth=0.5, label='Incremental', width=0.6)
    
    # Umbral crítico
    threshold = np.mean(areas) + np.std(areas)
    ax3.axhline(y=threshold, color='#FFD700', linestyle='--', linewidth=2, 
                label=f'Umbral crítico: {threshold:.0f} km²')
    
    ax3.set_title('Comparación: Acumulado vs Incremental', fontsize=14, fontweight='bold', color='black')
    ax3.set_xlabel('Frame', fontsize=11, color='black')
    ax3.set_ylabel('Área Acumulada (km²)', fontsize=11, color='black')
    ax3_twin.set_ylabel('Cambio Incremental (km²)', fontsize=11, color='#FFA500')
    ax3.tick_params(colors='black')
    ax3_twin.tick_params(colors='#FFA500')
    ax3.legend(loc='upper left', fontsize=10)
    ax3_twin.legend(loc='upper right', fontsize=10)
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    return fig

def _create_results_table_figure(results):
    """Crea tabla visual de resultados."""
    fig, ax = plt.subplots(figsize=(10, len(results) * 0.4 + 2))
    fig.patch.set_facecolor('white')
    ax.axis('tight')
    ax.axis('off')
    
    # Preparar datos
    table_data = [['Frame', 'Área (km²)', 'Área (ha)', 'Porcentaje (%)']]
    for r in results:
        table_data.append([
            f"{r['frame']}", 
            f"{r['area_km2']:.2f}",
            f"{r['area_ha']:.2f}",
            f"{r['porcentaje']:.2f}"
        ])
    
    # Crear tabla
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.2, 0.3, 0.3, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    
    # Estilizar encabezado
    for i in range(4):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternar colores
    for i in range(1, len(table_data)):
        color = '#F0F0F0' if i % 2 == 0 else 'white'
        for j in range(4):
            table[(i, j)].set_facecolor(color)
    
    plt.title('Resultados por Frame', fontsize=14, fontweight='bold', pad=20)
    
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
    lines = ["Frame,Área (km²),Área (ha),Porcentaje,Píxeles"]
    for r in results:
        lines.append(f"{r['frame']},{r['area_km2']:.4f},{r['area_ha']:.4f},{r['porcentaje']:.2f},{r['pixels']}")
    return "\n".join(lines)
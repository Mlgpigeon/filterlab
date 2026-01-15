"""
Aplicación interactiva para aplicar filtros espaciales y morfológicos.
Trabajo Grupal - Visión Artificial UNIR

Ejecutar con: streamlit run app.py
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# Configuración de la página
st.set_page_config(
    page_title="Filtros de Imagen - VA UNIR",
    page_icon="🔬",
    layout="wide"
)

# Título
st.title("🔬 Explorador de Filtros Espaciales y Morfológicos")
st.markdown("*Trabajo Grupal - Visión Artificial UNIR*")
st.markdown("---")

# ============================================================================
# DEFINICIÓN DE FILTROS
# ============================================================================

FILTROS_ESPACIALES = {
    "gaussiano": {
        "nombre": "Filtro Gaussiano",
        "descripcion": "Suavizado mediante convolución con máscara gaussiana. Reduce ruido gaussiano.",
        "params": ["kernel_size", "sigma"]
    },
    "mediana": {
        "nombre": "Filtro de Mediana",
        "descripcion": "Sustituye cada píxel por la mediana de su vecindad. Elimina ruido sal y pimienta.",
        "params": ["kernel_size"]
    },
    "clahe": {
        "nombre": "CLAHE",
        "descripcion": "Ecualización adaptativa de histograma con límite de contraste.",
        "params": ["clip_limit", "tile_size"]
    },
    "canny": {
        "nombre": "Detector de Bordes Canny",
        "descripcion": "Detecta bordes mediante gradiente y umbralización por histéresis.",
        "params": ["low_threshold", "high_threshold"]
    },
    "otsu": {
        "nombre": "Umbralización Otsu",
        "descripcion": "Binarización automática maximizando varianza inter-clase.",
        "params": []
    }
}

FILTROS_MORFOLOGICOS = {
    "apertura": {
        "nombre": "Apertura",
        "descripcion": "Erosión + Dilatación. Elimina objetos pequeños preservando forma.",
        "params": ["kernel_size"]
    },
    "clausura": {
        "nombre": "Clausura",
        "descripcion": "Dilatación + Erosión. Cierra huecos pequeños en objetos.",
        "params": ["kernel_size"]
    },
    "tophat": {
        "nombre": "White Top-Hat",
        "descripcion": "Imagen - Apertura. Resalta objetos brillantes sobre fondo.",
        "params": ["kernel_size"]
    },
    "blackhat": {
        "nombre": "Black Top-Hat",
        "descripcion": "Clausura - Imagen. Resalta objetos oscuros sobre fondo.",
        "params": ["kernel_size"]
    },
    "gradiente": {
        "nombre": "Gradiente Morfológico",
        "descripcion": "Dilatación - Erosión. Detecta contornos de objetos.",
        "params": ["kernel_size"]
    },
    "erosion": {
        "nombre": "Erosión",
        "descripcion": "Reduce objetos. Elimina píxeles en bordes.",
        "params": ["kernel_size", "iterations"]
    },
    "dilatacion": {
        "nombre": "Dilatación",
        "descripcion": "Expande objetos. Añade píxeles en bordes.",
        "params": ["kernel_size", "iterations"]
    }
}

# ============================================================================
# FUNCIONES DE FILTRADO
# ============================================================================

def apply_filter(img, filter_name, params):
    """Aplica un filtro específico a la imagen."""
    result = img.copy()
    
    # Asegurar que la imagen esté en escala de grises para ciertos filtros
    if len(result.shape) == 3:
        gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    else:
        gray = result
    
    # FILTROS ESPACIALES
    if filter_name == "gaussiano":
        k = params.get("kernel_size", 5)
        k = k if k % 2 == 1 else k + 1  # Asegurar impar
        sigma = params.get("sigma", 1.0)
        if len(result.shape) == 3:
            result = cv2.GaussianBlur(result, (k, k), sigma)
        else:
            result = cv2.GaussianBlur(result, (k, k), sigma)
            
    elif filter_name == "mediana":
        k = params.get("kernel_size", 5)
        k = k if k % 2 == 1 else k + 1
        if len(result.shape) == 3:
            result = cv2.medianBlur(result, k)
        else:
            result = cv2.medianBlur(result, k)
            
    elif filter_name == "clahe":
        clip = params.get("clip_limit", 2.0)
        tile = params.get("tile_size", 8)
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
        if len(result.shape) == 3:
            # Aplicar CLAHE en canal L de LAB
            lab = cv2.cvtColor(result, cv2.COLOR_RGB2LAB)
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        else:
            result = clahe.apply(result)
            
    elif filter_name == "canny":
        low = params.get("low_threshold", 50)
        high = params.get("high_threshold", 150)
        result = cv2.Canny(gray, low, high)
        
    elif filter_name == "otsu":
        _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # FILTROS MORFOLÓGICOS
    elif filter_name == "apertura":
        k = params.get("kernel_size", 5)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        if len(result.shape) == 3:
            result = cv2.morphologyEx(result, cv2.MORPH_OPEN, kernel)
        else:
            result = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            
    elif filter_name == "clausura":
        k = params.get("kernel_size", 5)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        if len(result.shape) == 3:
            result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
        else:
            result = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
    elif filter_name == "tophat":
        k = params.get("kernel_size", 15)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        result = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
        
    elif filter_name == "blackhat":
        k = params.get("kernel_size", 15)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        result = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
        
    elif filter_name == "gradiente":
        k = params.get("kernel_size", 3)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        result = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
        
    elif filter_name == "erosion":
        k = params.get("kernel_size", 3)
        iters = params.get("iterations", 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        if len(result.shape) == 3:
            result = cv2.erode(result, kernel, iterations=iters)
        else:
            result = cv2.erode(gray, kernel, iterations=iters)
            
    elif filter_name == "dilatacion":
        k = params.get("kernel_size", 3)
        iters = params.get("iterations", 1)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        if len(result.shape) == 3:
            result = cv2.dilate(result, kernel, iterations=iters)
        else:
            result = cv2.dilate(gray, kernel, iterations=iters)
    
    return result

# ============================================================================
# INTERFAZ DE USUARIO
# ============================================================================

# Inicializar estado de sesión
if 'filtros_activos' not in st.session_state:
    st.session_state.filtros_activos = []
if 'params' not in st.session_state:
    st.session_state.params = {}

# Sidebar para cargar imagen
with st.sidebar:
    st.header("📁 Cargar Imagen")
    uploaded_file = st.file_uploader(
        "Selecciona una imagen",
        type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
        help="Formatos soportados: PNG, JPG, BMP, TIFF"
    )
    
    st.markdown("---")
    
    # Botón para limpiar filtros
    if st.button("🗑️ Limpiar todos los filtros", use_container_width=True):
        st.session_state.filtros_activos = []
        st.rerun()
    
    # Mostrar orden de filtros activos
    if st.session_state.filtros_activos:
        st.markdown("---")
        st.subheader("📋 Orden de aplicación:")
        for i, (fname, _) in enumerate(st.session_state.filtros_activos, 1):
            all_filters = {**FILTROS_ESPACIALES, **FILTROS_MORFOLOGICOS}
            nombre = all_filters.get(fname, {}).get("nombre", fname)
            st.markdown(f"**{i}.** {nombre}")

# Layout principal: dos columnas
col_img, col_filters = st.columns([2, 1])

# Columna de imagen
with col_img:
    if uploaded_file is not None:
        # Cargar imagen
        image = Image.open(uploaded_file)
        img_array = np.array(image)
        
        # Convertir a RGB si es necesario
        if len(img_array.shape) == 2:
            # Escala de grises
            original = img_array.copy()
        elif img_array.shape[2] == 4:
            # RGBA -> RGB
            original = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        else:
            original = img_array.copy()
        
        # Aplicar filtros en orden
        resultado = original.copy()
        for filter_name, params in st.session_state.filtros_activos:
            resultado = apply_filter(resultado, filter_name, params)
        
        # Mostrar imágenes lado a lado
        subcol1, subcol2 = st.columns(2)
        
        with subcol1:
            st.markdown("### 📷 Original")
            st.image(original, use_container_width=True)
        
        with subcol2:
            st.markdown("### 🎨 Resultado")
            st.image(resultado, use_container_width=True, clamp=True)
        
        # Botón de descarga
        st.markdown("---")
        
        # Convertir resultado para descarga
        if len(resultado.shape) == 2:
            result_pil = Image.fromarray(resultado)
        else:
            result_pil = Image.fromarray(resultado)
        
        buf = io.BytesIO()
        result_pil.save(buf, format='PNG')
        
        st.download_button(
            label="⬇️ Descargar imagen resultado",
            data=buf.getvalue(),
            file_name="imagen_procesada.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.info("👈 Carga una imagen desde el panel lateral para comenzar")
        
        # Mostrar imagen de ejemplo
        st.markdown("### 💡 Ejemplo de uso:")
        st.markdown("""
        1. Carga una imagen (rayos X, médica, industrial, etc.)
        2. Activa los filtros en el panel derecho
        3. Ajusta los parámetros según necesites
        4. Los filtros se aplican en el orden que los activas
        5. Descarga el resultado final
        """)

# Columna de filtros
with col_filters:
    st.markdown("## 🎛️ Filtros")
    
    # Tabs para organizar filtros
    tab_espacial, tab_morfologico = st.tabs(["🌊 Espaciales", "🔲 Morfológicos"])
    
    with tab_espacial:
        st.markdown("### Filtros Espaciales")
        
        for key, info in FILTROS_ESPACIALES.items():
            with st.expander(f"**{info['nombre']}**", expanded=False):
                st.caption(info['descripcion'])
                
                # Parámetros específicos
                params = {}
                
                if "kernel_size" in info['params']:
                    params["kernel_size"] = st.slider(
                        f"Tamaño kernel ({key})", 3, 31, 5, 2,
                        key=f"{key}_kernel"
                    )
                
                if "sigma" in info['params']:
                    params["sigma"] = st.slider(
                        f"Sigma ({key})", 0.1, 5.0, 1.0, 0.1,
                        key=f"{key}_sigma"
                    )
                
                if "clip_limit" in info['params']:
                    params["clip_limit"] = st.slider(
                        f"Clip Limit ({key})", 1.0, 10.0, 2.0, 0.5,
                        key=f"{key}_clip"
                    )
                
                if "tile_size" in info['params']:
                    params["tile_size"] = st.slider(
                        f"Tile Size ({key})", 2, 16, 8, 1,
                        key=f"{key}_tile"
                    )
                
                if "low_threshold" in info['params']:
                    params["low_threshold"] = st.slider(
                        f"Umbral bajo ({key})", 0, 200, 50, 5,
                        key=f"{key}_low"
                    )
                
                if "high_threshold" in info['params']:
                    params["high_threshold"] = st.slider(
                        f"Umbral alto ({key})", 50, 300, 150, 5,
                        key=f"{key}_high"
                    )
                
                # Botones para añadir/quitar
                col_add, col_remove = st.columns(2)
                
                with col_add:
                    if st.button(f"➕ Añadir", key=f"add_{key}", use_container_width=True):
                        st.session_state.filtros_activos.append((key, params.copy()))
                        st.rerun()
                
                with col_remove:
                    # Buscar si este filtro está activo
                    idx_to_remove = None
                    for i, (fname, _) in enumerate(st.session_state.filtros_activos):
                        if fname == key:
                            idx_to_remove = i
                            break
                    
                    if idx_to_remove is not None:
                        if st.button(f"➖ Quitar", key=f"rem_{key}", use_container_width=True):
                            st.session_state.filtros_activos.pop(idx_to_remove)
                            st.rerun()
    
    with tab_morfologico:
        st.markdown("### Filtros Morfológicos")
        
        for key, info in FILTROS_MORFOLOGICOS.items():
            with st.expander(f"**{info['nombre']}**", expanded=False):
                st.caption(info['descripcion'])
                
                # Parámetros específicos
                params = {}
                
                if "kernel_size" in info['params']:
                    default_k = 15 if key in ['tophat', 'blackhat'] else 5
                    params["kernel_size"] = st.slider(
                        f"Tamaño kernel ({key})", 3, 31, default_k, 2,
                        key=f"{key}_kernel"
                    )
                
                if "iterations" in info['params']:
                    params["iterations"] = st.slider(
                        f"Iteraciones ({key})", 1, 10, 1, 1,
                        key=f"{key}_iter"
                    )
                
                # Botones para añadir/quitar
                col_add, col_remove = st.columns(2)
                
                with col_add:
                    if st.button(f"➕ Añadir", key=f"add_{key}", use_container_width=True):
                        st.session_state.filtros_activos.append((key, params.copy()))
                        st.rerun()
                
                with col_remove:
                    idx_to_remove = None
                    for i, (fname, _) in enumerate(st.session_state.filtros_activos):
                        if fname == key:
                            idx_to_remove = i
                            break
                    
                    if idx_to_remove is not None:
                        if st.button(f"➖ Quitar", key=f"rem_{key}", use_container_width=True):
                            st.session_state.filtros_activos.pop(idx_to_remove)
                            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>
    Filtros Espaciales y Morfológicos | Visión Artificial - UNIR<br>
    Basado en OpenCV | Trabajo Grupal 2025
    </small>
</div>
""", unsafe_allow_html=True)

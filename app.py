"""
FilterLab - Explorador de Filtros de Imagen
Versión mejorada con cola de filtros, sin duplicados y actualización en tiempo real
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

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
# DEFINICIÓN DE FILTROS
# ============================================================================

FILTROS_ESPACIALES = {
    "gaussiano": {
        "nombre": "Gaussiano",
        "descripcion": "Suavizado mediante convolución gaussiana. Reduce ruido.",
        "params": {
            "kernel_size": {"min": 3, "max": 31, "default": 5, "step": 2, "label": "Tamaño kernel"},
            "sigma": {"min": 0.1, "max": 10.0, "default": 1.0, "step": 0.1, "label": "Sigma"}
        }
    },
    "mediana": {
        "nombre": "Mediana",
        "descripcion": "Elimina ruido sal y pimienta preservando bordes.",
        "params": {
            "kernel_size": {"min": 3, "max": 31, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "clahe": {
        "nombre": "CLAHE",
        "descripcion": "Ecualización adaptativa de histograma con límite de contraste.",
        "params": {
            "clip_limit": {"min": 1.0, "max": 10.0, "default": 2.0, "step": 0.5, "label": "Clip Limit"},
            "tile_size": {"min": 2, "max": 16, "default": 8, "step": 1, "label": "Tile Size"}
        }
    },
    "canny": {
        "nombre": "Canny",
        "descripcion": "Detecta bordes mediante gradiente e histéresis.",
        "params": {
            "low_threshold": {"min": 0, "max": 255, "default": 50, "step": 5, "label": "Umbral bajo"},
            "high_threshold": {"min": 0, "max": 255, "default": 150, "step": 5, "label": "Umbral alto"}
        }
    },
    "otsu": {
        "nombre": "Otsu",
        "descripcion": "Binarización automática óptima.",
        "params": {}
    },
    "laplaciano": {
        "nombre": "Laplaciano",
        "descripcion": "Detecta bordes mediante segunda derivada.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "sobel": {
        "nombre": "Sobel",
        "descripcion": "Detecta bordes horizontales y verticales.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    }
}

FILTROS_MORFOLOGICOS = {
    "erosion": {
        "nombre": "Erosión",
        "descripcion": "Reduce objetos. Elimina píxeles en bordes.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"},
            "iterations": {"min": 1, "max": 10, "default": 1, "step": 1, "label": "Iteraciones"}
        }
    },
    "dilatacion": {
        "nombre": "Dilatación",
        "descripcion": "Expande objetos. Añade píxeles en bordes.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"},
            "iterations": {"min": 1, "max": 10, "default": 1, "step": 1, "label": "Iteraciones"}
        }
    },
    "apertura": {
        "nombre": "Apertura",
        "descripcion": "Erosión + Dilatación. Elimina objetos pequeños.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "clausura": {
        "nombre": "Clausura",
        "descripcion": "Dilatación + Erosión. Cierra huecos pequeños.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "tophat": {
        "nombre": "White Top-Hat",
        "descripcion": "Resalta objetos brillantes sobre fondo oscuro.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 9, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "blackhat": {
        "nombre": "Black Top-Hat",
        "descripcion": "Resalta objetos oscuros sobre fondo brillante.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 9, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "gradiente": {
        "nombre": "Gradiente Morfológico",
        "descripcion": "Dilatación - Erosión. Detecta contornos.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    }
}

# ============================================================================
# FUNCIONES DE FILTRADO
# ============================================================================

def apply_filter(img, filter_name, params):
    """Aplica un filtro específico a la imagen."""
    result = img.copy()
    
    # Convertir a escala de grises si es necesario
    if len(result.shape) == 3:
        gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    else:
        gray = result
    
    # FILTROS ESPACIALES
    if filter_name == "gaussiano":
        k = int(params.get("kernel_size", 5))
        k = k if k % 2 == 1 else k + 1
        sigma = params.get("sigma", 1.0)
        if len(result.shape) == 3:
            result = cv2.GaussianBlur(result, (k, k), sigma)
        else:
            result = cv2.GaussianBlur(result, (k, k), sigma)
            
    elif filter_name == "mediana":
        k = int(params.get("kernel_size", 5))
        k = k if k % 2 == 1 else k + 1
        result = cv2.medianBlur(result if len(result.shape) == 3 else gray, k)
        if len(img.shape) == 3 and len(result.shape) == 2:
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            
    elif filter_name == "clahe":
        clip = params.get("clip_limit", 2.0)
        tile = int(params.get("tile_size", 8))
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
        if len(result.shape) == 3:
            lab = cv2.cvtColor(result, cv2.COLOR_RGB2LAB)
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        else:
            result = clahe.apply(gray)
            
    elif filter_name == "canny":
        low = int(params.get("low_threshold", 50))
        high = int(params.get("high_threshold", 150))
        result = cv2.Canny(gray, low, high)
        
    elif filter_name == "otsu":
        _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
    elif filter_name == "laplaciano":
        k = int(params.get("kernel_size", 3))
        k = k if k % 2 == 1 else k + 1
        result = cv2.Laplacian(gray, cv2.CV_64F, ksize=k)
        result = np.uint8(np.absolute(result))
        
    elif filter_name == "sobel":
        k = int(params.get("kernel_size", 3))
        k = k if k % 2 == 1 else k + 1
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k)
        result = np.uint8(np.sqrt(sobelx**2 + sobely**2))
    
    # FILTROS MORFOLÓGICOS
    elif filter_name == "erosion":
        k = int(params.get("kernel_size", 5))
        iterations = int(params.get("iterations", 1))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        if len(result.shape) == 3:
            result = cv2.erode(result, kernel, iterations=iterations)
        else:
            result = cv2.erode(gray, kernel, iterations=iterations)
            
    elif filter_name == "dilatacion":
        k = int(params.get("kernel_size", 5))
        iterations = int(params.get("iterations", 1))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        if len(result.shape) == 3:
            result = cv2.dilate(result, kernel, iterations=iterations)
        else:
            result = cv2.dilate(gray, kernel, iterations=iterations)
            
    elif filter_name == "apertura":
        k = int(params.get("kernel_size", 5))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        if len(result.shape) == 3:
            result = cv2.morphologyEx(result, cv2.MORPH_OPEN, kernel)
        else:
            result = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            
    elif filter_name == "clausura":
        k = int(params.get("kernel_size", 5))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        if len(result.shape) == 3:
            result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
        else:
            result = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
    elif filter_name == "tophat":
        k = int(params.get("kernel_size", 9))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        if len(result.shape) == 3:
            result = cv2.morphologyEx(result, cv2.MORPH_TOPHAT, kernel)
        else:
            result = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
            
    elif filter_name == "blackhat":
        k = int(params.get("kernel_size", 9))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        if len(result.shape) == 3:
            result = cv2.morphologyEx(result, cv2.MORPH_BLACKHAT, kernel)
        else:
            result = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
            
    elif filter_name == "gradiente":
        k = int(params.get("kernel_size", 5))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
        if len(result.shape) == 3:
            result = cv2.morphologyEx(result, cv2.MORPH_GRADIENT, kernel)
        else:
            result = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
    
    return result


def apply_filter_chain(img, filter_list):
    """Aplica una cadena de filtros a la imagen."""
    result = img.copy()
    for filter_name, params in filter_list:
        result = apply_filter(result, filter_name, params)
    return result


def get_filter_info(filter_name):
    """Obtiene la información de un filtro."""
    if filter_name in FILTROS_ESPACIALES:
        return FILTROS_ESPACIALES[filter_name]
    elif filter_name in FILTROS_MORFOLOGICOS:
        return FILTROS_MORFOLOGICOS[filter_name]
    return None


def get_all_filters():
    """Retorna todos los filtros disponibles."""
    return {**FILTROS_ESPACIALES, **FILTROS_MORFOLOGICOS}

# ============================================================================
# INICIALIZACIÓN DE SESSION STATE
# ============================================================================

if 'filtros_activos' not in st.session_state:
    st.session_state.filtros_activos = []  # Lista de filter_keys activos

if 'filter_params' not in st.session_state:
    st.session_state.filter_params = {}  # Diccionario de parámetros por filtro

# ============================================================================
# INTERFAZ PRINCIPAL
# ============================================================================

# Título
st.title("🔬 FilterLab")
st.caption("Explorador de Filtros Espaciales y Morfológicos")

# Layout de 3 columnas: Sidebar izq | Imagen centro | Cola derecha
col_main, col_queue = st.columns([3, 1])

# ============================================================================
# SIDEBAR - CARGA DE IMAGEN Y SELECCIÓN DE FILTROS
# ============================================================================

with st.sidebar:
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
    
    st.markdown("---")
    
    # ========================================================================
    # FILTROS ESPACIALES
    # ========================================================================
    st.header("🎨 Filtros Espaciales")
    
    for key, info in FILTROS_ESPACIALES.items():
        # Verificar si el filtro ya está activo
        is_active = key in st.session_state.filtros_activos
        
        # Crear expander con indicador visual
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
                if isinstance(param_config['default'], float):
                    val = st.slider(
                        param_config['label'],
                        min_value=param_config['min'],
                        max_value=param_config['max'],
                        value=st.session_state.filter_params[key].get(param_name, param_config['default']),
                        step=param_config['step'],
                        key=f"{key}_{param_name}"
                    )
                else:
                    val = st.slider(
                        param_config['label'],
                        min_value=param_config['min'],
                        max_value=param_config['max'],
                        value=st.session_state.filter_params[key].get(param_name, param_config['default']),
                        step=param_config['step'],
                        key=f"{key}_{param_name}"
                    )
                current_params[param_name] = val
            
            # Actualizar parámetros en session state (actualización en tiempo real)
            st.session_state.filter_params[key] = current_params
            
            # Botón de añadir/quitar
            if is_active:
                if st.button(f"❌ Quitar {info['nombre']}", key=f"remove_{key}", use_container_width=True):
                    st.session_state.filtros_activos.remove(key)
                    st.rerun()
            else:
                if st.button(f"➕ Añadir {info['nombre']}", key=f"add_{key}", use_container_width=True):
                    st.session_state.filtros_activos.append(key)
                    st.rerun()
    
    st.markdown("---")
    
    # ========================================================================
    # FILTROS MORFOLÓGICOS
    # ========================================================================
    st.header("🔷 Filtros Morfológicos")
    
    for key, info in FILTROS_MORFOLOGICOS.items():
        is_active = key in st.session_state.filtros_activos
        
        icon = "✅" if is_active else "⚪"
        with st.expander(f"{icon} {info['nombre']}", expanded=is_active):
            st.caption(info['descripcion'])
            
            if key not in st.session_state.filter_params:
                st.session_state.filter_params[key] = {
                    p: v['default'] for p, v in info['params'].items()
                }
            
            current_params = {}
            for param_name, param_config in info['params'].items():
                val = st.slider(
                    param_config['label'],
                    min_value=param_config['min'],
                    max_value=param_config['max'],
                    value=st.session_state.filter_params[key].get(param_name, param_config['default']),
                    step=param_config['step'],
                    key=f"{key}_{param_name}"
                )
                current_params[param_name] = val
            
            st.session_state.filter_params[key] = current_params
            
            if is_active:
                if st.button(f"❌ Quitar {info['nombre']}", key=f"remove_{key}", use_container_width=True):
                    st.session_state.filtros_activos.remove(key)
                    st.rerun()
            else:
                if st.button(f"➕ Añadir {info['nombre']}", key=f"add_{key}", use_container_width=True):
                    st.session_state.filtros_activos.append(key)
                    st.rerun()

# ============================================================================
# COLUMNA PRINCIPAL - VISUALIZACIÓN DE IMAGEN
# ============================================================================

with col_main:
    if uploaded_file:
        # Preparar la lista de filtros con parámetros actuales
        filter_chain = [
            (f, st.session_state.filter_params.get(f, {})) 
            for f in st.session_state.filtros_activos
        ]
        
        # Aplicar filtros
        if filter_chain:
            result_img = apply_filter_chain(img_rgb, filter_chain)
        else:
            result_img = img_rgb
        
        # Mostrar imágenes lado a lado
        col_orig, col_result = st.columns(2)
        
        with col_orig:
            st.subheader("Original")
            st.image(img_rgb, use_container_width=True)
        
        with col_result:
            st.subheader("Resultado")
            st.image(result_img, use_container_width=True, clamp=True)
        
        # Botón de descarga
        st.markdown("---")
        
        # Convertir resultado a bytes para descarga
        if len(result_img.shape) == 2:
            result_pil = Image.fromarray(result_img)
        else:
            result_pil = Image.fromarray(result_img)
        
        buf = io.BytesIO()
        result_pil.save(buf, format='PNG')
        
        st.download_button(
            label="📥 Descargar resultado",
            data=buf.getvalue(),
            file_name="filterlab_resultado.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.info("👈 Carga una imagen desde el panel lateral para comenzar")
        
        # Placeholder visual
        st.markdown("""
        ### Cómo usar FilterLab:
        
        1. **Cargar imagen** - Usa el panel izquierdo para subir una imagen
        2. **Añadir filtros** - Selecciona filtros y ajusta sus parámetros
        3. **Ver resultado** - La imagen se actualiza en tiempo real
        4. **Reordenar** - Usa la cola de la derecha para cambiar el orden
        5. **Descargar** - Guarda el resultado cuando estés satisfecho
        """)

# ============================================================================
# COLUMNA DERECHA - COLA DE FILTROS
# ============================================================================

with col_queue:
    st.subheader("📋 Cola de Filtros")
    
    if st.session_state.filtros_activos:
        st.caption(f"{len(st.session_state.filtros_activos)} filtro(s) activo(s)")
        
        # Mostrar cada filtro en orden
        for idx, filter_key in enumerate(st.session_state.filtros_activos):
            info = get_filter_info(filter_key)
            params = st.session_state.filter_params.get(filter_key, {})
            
            # Crear card para cada filtro
            with st.container():
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
                            # Intercambiar con el anterior
                            st.session_state.filtros_activos[idx], st.session_state.filtros_activos[idx-1] = \
                                st.session_state.filtros_activos[idx-1], st.session_state.filtros_activos[idx]
                            st.rerun()
                
                with col_down:
                    if idx < len(st.session_state.filtros_activos) - 1:
                        if st.button("⬇️", key=f"down_{idx}", help="Bajar"):
                            # Intercambiar con el siguiente
                            st.session_state.filtros_activos[idx], st.session_state.filtros_activos[idx+1] = \
                                st.session_state.filtros_activos[idx+1], st.session_state.filtros_activos[idx]
                            st.rerun()
                
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

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>
    FilterLab | Visión Artificial - UNIR 2025<br>
    Basado en OpenCV
    </small>
</div>
""", unsafe_allow_html=True)

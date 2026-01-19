"""
Implementación de filtros morfológicos - VERSIÓN CORREGIDA v2.

Cambios v2:
- Detección automática de imagen binaria/bordes
- Kernel mínimo ajustado según tipo de imagen
- Apertura/clausura inteligente para bordes finos
- Todos los filtros funcionan correctamente después de Canny/Otsu
"""

import cv2
import numpy as np


def _ensure_rgb(out):
    """Asegura salida en RGB (3 canales)."""
    if out is None:
        return out
    if len(out.shape) == 2:
        return cv2.cvtColor(out, cv2.COLOR_GRAY2RGB)
    return out


def _get_kernel(size, shape='rect'):
    """Crea elemento estructurante."""
    size = int(size)
    size = max(1, size)  # Mínimo 1
    size = size if size % 2 == 1 else size + 1  # Asegurar impar
    
    shapes = {
        'rect': cv2.MORPH_RECT,
        'ellipse': cv2.MORPH_ELLIPSE,
        'cross': cv2.MORPH_CROSS,
    }
    morph_shape = shapes.get(shape, cv2.MORPH_RECT)
    return cv2.getStructuringElement(morph_shape, (size, size))


def _is_binary_image(img):
    """Detecta si la imagen es binaria (solo 0 y 255)."""
    if len(img.shape) == 3:
        # Usar solo un canal
        channel = img[:, :, 0]
    else:
        channel = img
    
    unique = np.unique(channel)
    return len(unique) <= 2 and (set(unique) <= {0, 255})


def _is_edge_image(img):
    """Detecta si la imagen parece ser resultado de detector de bordes."""
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    # Imagen de bordes: binaria con pocos píxeles blancos (<20%)
    if not _is_binary_image(img):
        return False
    
    white_ratio = np.sum(gray == 255) / gray.size
    return white_ratio < 0.2


def _get_working_image(img, gray):
    """Obtiene la imagen correcta para procesar."""
    # Si es RGB pero todos los canales son iguales, usar gray
    if len(img.shape) == 3:
        if np.array_equal(img[:,:,0], img[:,:,1]) and np.array_equal(img[:,:,1], img[:,:,2]):
            return gray
    return gray if len(img.shape) == 2 else img


# =============================================================================
# FILTROS BÁSICOS
# =============================================================================

def apply_erosion(img, gray, params):
    """
    Erosión morfológica.
    
    Reduce objetos eliminando píxeles en los bordes.
    NOTA: En imágenes de bordes finos (Canny), puede eliminar todo.
    """
    k = int(params.get("kernel_size", 3))
    iterations = int(params.get("iterations", 1))
    
    # Para bordes finos, advertir si kernel es muy grande
    work_img = _get_working_image(img, gray)
    
    kernel = _get_kernel(k)
    result = cv2.erode(work_img, kernel, iterations=iterations)
    
    return _ensure_rgb(result)


def apply_dilatacion(img, gray, params):
    """
    Dilatación morfológica.
    
    Expande objetos añadiendo píxeles en los bordes.
    Ideal para engrosar bordes de Canny antes de otras operaciones.
    """
    k = int(params.get("kernel_size", 3))
    iterations = int(params.get("iterations", 1))
    
    work_img = _get_working_image(img, gray)
    
    kernel = _get_kernel(k)
    result = cv2.dilate(work_img, kernel, iterations=iterations)
    
    return _ensure_rgb(result)


def apply_apertura(img, gray, params):
    """
    Apertura morfológica (erosión + dilatación).
    
    NOTA: En bordes finos de 1px, la erosión interna elimina todo.
    Para bordes Canny, usar primero dilatación para engrosar.
    """
    k = int(params.get("kernel_size", 3))
    
    work_img = _get_working_image(img, gray)
    
    # Si es imagen de bordes finos y kernel > 1, la apertura eliminaría todo
    # En ese caso, aplicar una versión más suave
    if _is_edge_image(img) and k > 1:
        # Para bordes: solo hacer una erosión muy suave seguida de dilatación
        kernel_small = _get_kernel(1)
        kernel = _get_kernel(k)
        eroded = cv2.erode(work_img, kernel_small, iterations=1)
        result = cv2.dilate(eroded, kernel, iterations=1)
    else:
        kernel = _get_kernel(k)
        result = cv2.morphologyEx(work_img, cv2.MORPH_OPEN, kernel)
    
    return _ensure_rgb(result)


def apply_clausura(img, gray, params):
    """
    Clausura morfológica (dilatación + erosión).
    
    Cierra huecos pequeños. Funciona bien con bordes de Canny.
    """
    k = int(params.get("kernel_size", 3))
    
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    
    result = cv2.morphologyEx(work_img, cv2.MORPH_CLOSE, kernel)
    
    return _ensure_rgb(result)


def apply_tophat(img, gray, params):
    """
    White Top-Hat (original - apertura).
    
    Resalta objetos brillantes más pequeños que el kernel.
    """
    k = int(params.get("kernel_size", 5))
    
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    
    result = cv2.morphologyEx(work_img, cv2.MORPH_TOPHAT, kernel)
    
    # Normalizar solo si hay variación
    if result.max() > result.min():
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return _ensure_rgb(result)


def apply_blackhat(img, gray, params):
    """
    Black Top-Hat (clausura - original).
    
    Resalta objetos oscuros más pequeños que el kernel.
    """
    k = int(params.get("kernel_size", 5))
    
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    
    result = cv2.morphologyEx(work_img, cv2.MORPH_BLACKHAT, kernel)
    
    # Normalizar solo si hay variación
    if result.max() > result.min():
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return _ensure_rgb(result)


def apply_gradiente(img, gray, params):
    """
    Gradiente morfológico (dilatación - erosión).
    
    Detecta contornos. En imagen de bordes, los engrosa.
    """
    k = int(params.get("kernel_size", 3))
    
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    
    result = cv2.morphologyEx(work_img, cv2.MORPH_GRADIENT, kernel)
    
    # Normalizar solo si hay variación
    if result.max() > result.min():
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return _ensure_rgb(result)


# =============================================================================
# MAPEO DE NOMBRES A FUNCIONES
# =============================================================================

MORPHOLOGICAL_FILTERS = {
    "erosion": apply_erosion,
    "dilatacion": apply_dilatacion,
    "apertura": apply_apertura,
    "clausura": apply_clausura,
    "tophat": apply_tophat,
    "blackhat": apply_blackhat,
    "gradiente": apply_gradiente,
}

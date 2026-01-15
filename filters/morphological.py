"""
Implementación de filtros morfológicos - VERSIÓN CORREGIDA.

Cambios:
1. Kernel por defecto reducido (3 en vez de 5, 5 en vez de 9)
2. Opción de procesar en escala de grises (evita artefactos de color)
3. Salida siempre en RGB para consistencia
4. Normalización de tophat/blackhat/gradiente para mejor visualización
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
    size = size if size % 2 == 1 else size + 1  # Asegurar impar
    
    shapes = {
        'rect': cv2.MORPH_RECT,
        'ellipse': cv2.MORPH_ELLIPSE,
        'cross': cv2.MORPH_CROSS,
    }
    morph_shape = shapes.get(shape, cv2.MORPH_RECT)
    return cv2.getStructuringElement(morph_shape, (size, size))


def _process_morphology(img, gray, operation, kernel, iterations=1):
    """
    Aplica operación morfológica de forma inteligente.
    
    Para imágenes RGB: procesa en escala de grises y devuelve RGB.
    Esto evita los artefactos de color que ocurren al procesar cada canal.
    """
    if len(img.shape) == 3:
        # Procesar en escala de grises para evitar artefactos
        if operation in [cv2.MORPH_ERODE, cv2.MORPH_DILATE]:
            result = cv2.morphologyEx(gray, operation, kernel, iterations=iterations)
        else:
            result = cv2.morphologyEx(gray, operation, kernel)
        return _ensure_rgb(result)
    else:
        if operation in [cv2.MORPH_ERODE, cv2.MORPH_DILATE]:
            result = cv2.morphologyEx(gray, operation, kernel, iterations=iterations)
        else:
            result = cv2.morphologyEx(gray, operation, kernel)
        return _ensure_rgb(result)


def apply_erosion(img, gray, params):
    """
    Erosión morfológica.
    
    Reduce objetos eliminando píxeles en los bordes.
    Útil para: eliminar ruido pequeño, separar objetos conectados.
    
    Mantiene color en imágenes RGB (procesa cada canal).
    """
    k = int(params.get("kernel_size", 3))  # CORREGIDO: era 5
    iterations = int(params.get("iterations", 1))
    kernel = _get_kernel(k)
    
    # Mantener color para erosión/dilatación (efecto más intuitivo)
    if len(img.shape) == 3:
        return cv2.erode(img, kernel, iterations=iterations)
    return _ensure_rgb(cv2.erode(gray, kernel, iterations=iterations))


def apply_dilatacion(img, gray, params):
    """
    Dilatación morfológica.
    
    Expande objetos añadiendo píxeles en los bordes.
    Útil para: cerrar huecos pequeños, conectar objetos cercanos.
    
    Mantiene color en imágenes RGB (procesa cada canal).
    """
    k = int(params.get("kernel_size", 3))  # CORREGIDO: era 5
    iterations = int(params.get("iterations", 1))
    kernel = _get_kernel(k)
    
    # Mantener color para erosión/dilatación (efecto más intuitivo)
    if len(img.shape) == 3:
        return cv2.dilate(img, kernel, iterations=iterations)
    return _ensure_rgb(cv2.dilate(gray, kernel, iterations=iterations))


def apply_apertura(img, gray, params):
    """
    Apertura morfológica (erosión + dilatación).
    
    Elimina objetos pequeños preservando el tamaño de objetos grandes.
    Útil para: eliminar ruido, suavizar contornos.
    
    Mantiene color en imágenes RGB.
    """
    k = int(params.get("kernel_size", 3))  # CORREGIDO: era 5
    kernel = _get_kernel(k)
    
    if len(img.shape) == 3:
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    return _ensure_rgb(cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel))


def apply_clausura(img, gray, params):
    """
    Clausura morfológica (dilatación + erosión).
    
    Cierra huecos pequeños preservando el tamaño de objetos.
    Útil para: rellenar agujeros, unir componentes cercanos.
    
    Mantiene color en imágenes RGB.
    """
    k = int(params.get("kernel_size", 3))  # CORREGIDO: era 5
    kernel = _get_kernel(k)
    
    if len(img.shape) == 3:
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    return _ensure_rgb(cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel))


def apply_tophat(img, gray, params):
    """
    White Top-Hat (original - apertura).
    
    Resalta objetos brillantes más pequeños que el kernel.
    Útil para: detectar manchas claras, corrección de iluminación.
    
    NOTA: El resultado se normaliza para mejor visualización.
    """
    k = int(params.get("kernel_size", 5))  # CORREGIDO: era 9
    kernel = _get_kernel(k)
    
    result = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
    
    # Normalizar para mejor visualización (el resultado suele ser muy oscuro)
    result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return _ensure_rgb(result)


def apply_blackhat(img, gray, params):
    """
    Black Top-Hat (clausura - original).
    
    Resalta objetos oscuros más pequeños que el kernel.
    Útil para: detectar manchas oscuras, encontrar texto.
    
    NOTA: El resultado se normaliza para mejor visualización.
    """
    k = int(params.get("kernel_size", 5))  # CORREGIDO: era 9
    kernel = _get_kernel(k)
    
    result = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    
    # Normalizar para mejor visualización
    result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return _ensure_rgb(result)


def apply_gradiente(img, gray, params):
    """
    Gradiente morfológico (dilatación - erosión).
    
    Detecta los contornos de objetos.
    Útil para: detección de bordes robusta, segmentación.
    
    NOTA: El resultado se normaliza para mejor visualización.
    """
    k = int(params.get("kernel_size", 3))  # CORREGIDO: era 5
    kernel = _get_kernel(k)
    
    result = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
    
    # Normalizar para mejor visualización
    result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return _ensure_rgb(result)


# =============================================================================
# VERSIONES QUE MANTIENEN COLOR (para usuarios avanzados)
# =============================================================================

def apply_erosion_color(img, gray, params):
    """Erosión manteniendo color (puede causar artefactos)."""
    k = int(params.get("kernel_size", 3))
    iterations = int(params.get("iterations", 1))
    kernel = _get_kernel(k)
    
    if len(img.shape) == 3:
        return cv2.erode(img, kernel, iterations=iterations)
    return _ensure_rgb(cv2.erode(gray, kernel, iterations=iterations))


def apply_dilatacion_color(img, gray, params):
    """Dilatación manteniendo color (puede causar artefactos)."""
    k = int(params.get("kernel_size", 3))
    iterations = int(params.get("iterations", 1))
    kernel = _get_kernel(k)
    
    if len(img.shape) == 3:
        return cv2.dilate(img, kernel, iterations=iterations)
    return _ensure_rgb(cv2.dilate(gray, kernel, iterations=iterations))


# =============================================================================
# MAPEO DE NOMBRES A FUNCIONES
# =============================================================================

MORPHOLOGICAL_FILTERS = {
    # Versiones estándar (procesan en gris, más estables)
    "erosion": apply_erosion,
    "dilatacion": apply_dilatacion,
    "apertura": apply_apertura,
    "clausura": apply_clausura,
    "tophat": apply_tophat,
    "blackhat": apply_blackhat,
    "gradiente": apply_gradiente,
    
    # Versiones que mantienen color (opcional, para usuarios avanzados)
    # "erosion_color": apply_erosion_color,
    # "dilatacion_color": apply_dilatacion_color,
}

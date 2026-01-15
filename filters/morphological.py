"""
Implementación de filtros morfológicos.
"""

import cv2


def apply_erosion(img, gray, params):
    """Aplica erosión morfológica."""
    k = int(params.get("kernel_size", 5))
    iterations = int(params.get("iterations", 1))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    
    if len(img.shape) == 3:
        return cv2.erode(img, kernel, iterations=iterations)
    else:
        return cv2.erode(gray, kernel, iterations=iterations)


def apply_dilatacion(img, gray, params):
    """Aplica dilatación morfológica."""
    k = int(params.get("kernel_size", 5))
    iterations = int(params.get("iterations", 1))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    
    if len(img.shape) == 3:
        return cv2.dilate(img, kernel, iterations=iterations)
    else:
        return cv2.dilate(gray, kernel, iterations=iterations)


def apply_apertura(img, gray, params):
    """Aplica apertura morfológica (erosión + dilatación)."""
    k = int(params.get("kernel_size", 5))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    
    if len(img.shape) == 3:
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    else:
        return cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)


def apply_clausura(img, gray, params):
    """Aplica clausura morfológica (dilatación + erosión)."""
    k = int(params.get("kernel_size", 5))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    
    if len(img.shape) == 3:
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    else:
        return cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)


def apply_tophat(img, gray, params):
    """Aplica White Top-Hat (resalta brillante sobre oscuro)."""
    k = int(params.get("kernel_size", 9))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    
    if len(img.shape) == 3:
        return cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel)
    else:
        return cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)


def apply_blackhat(img, gray, params):
    """Aplica Black Top-Hat (resalta oscuro sobre brillante)."""
    k = int(params.get("kernel_size", 9))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    
    if len(img.shape) == 3:
        return cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel)
    else:
        return cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)


def apply_gradiente(img, gray, params):
    """Aplica gradiente morfológico (dilatación - erosión)."""
    k = int(params.get("kernel_size", 5))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
    
    if len(img.shape) == 3:
        return cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel)
    else:
        return cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)


# Mapeo de nombres a funciones
MORPHOLOGICAL_FILTERS = {
    "erosion": apply_erosion,
    "dilatacion": apply_dilatacion,
    "apertura": apply_apertura,
    "clausura": apply_clausura,
    "tophat": apply_tophat,
    "blackhat": apply_blackhat,
    "gradiente": apply_gradiente,
}

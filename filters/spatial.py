"""
Implementación de filtros espaciales.
"""

import cv2
import numpy as np


def apply_gaussiano(img, gray, params):
    """Aplica filtro Gaussiano."""
    k = int(params.get("kernel_size", 5))
    k = k if k % 2 == 1 else k + 1
    sigma = params.get("sigma", 1.0)
    return cv2.GaussianBlur(img, (k, k), sigma)


def apply_mediana(img, gray, params):
    """Aplica filtro de Mediana."""
    k = int(params.get("kernel_size", 5))
    k = k if k % 2 == 1 else k + 1
    result = cv2.medianBlur(img if len(img.shape) == 3 else gray, k)
    if len(img.shape) == 3 and len(result.shape) == 2:
        result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
    return result


def apply_clahe(img, gray, params):
    """Aplica CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    clip = params.get("clip_limit", 2.0)
    tile = int(params.get("tile_size", 8))
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
    
    if len(img.shape) == 3:
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    else:
        return clahe.apply(gray)


def apply_canny(img, gray, params):
    """Aplica detector de bordes Canny."""
    low = int(params.get("low_threshold", 50))
    high = int(params.get("high_threshold", 150))
    return cv2.Canny(gray, low, high)


def apply_otsu(img, gray, params):
    """Aplica binarización de Otsu."""
    _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return result


def apply_laplaciano(img, gray, params):
    """Aplica filtro Laplaciano para detección de bordes."""
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    result = cv2.Laplacian(gray, cv2.CV_64F, ksize=k)
    return np.uint8(np.absolute(result))


def apply_sobel(img, gray, params):
    """Aplica filtro Sobel para detección de bordes."""
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k)
    return np.uint8(np.sqrt(sobel_x**2 + sobel_y**2))


# Mapeo de nombres a funciones
SPATIAL_FILTERS = {
    "gaussiano": apply_gaussiano,
    "mediana": apply_mediana,
    "clahe": apply_clahe,
    "canny": apply_canny,
    "otsu": apply_otsu,
    "laplaciano": apply_laplaciano,
    "sobel": apply_sobel,
}

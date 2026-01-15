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


def _to_gray_u8(img, gray):
    """Asegura una imagen en gris uint8 para operaciones puntuales."""
    g = gray
    if g is None:
        if len(img.shape) == 3:
            g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            g = img
    if g.dtype != np.uint8:
        g = cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return g


def apply_bilateral(img, gray, params):
    """Suavizado preservando bordes (bilateral)."""
    g = _to_gray_u8(img, gray)
    d = int(params.get("d", 9))
    sigma_color = float(params.get("sigmaColor", 75))
    sigma_space = float(params.get("sigmaSpace", 75))
    return cv2.bilateralFilter(g, d, sigma_color, sigma_space)


def apply_normalize(img, gray, params):
    """Normaliza intensidades al rango 0-255."""
    g = _to_gray_u8(img, gray)
    return cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX)


def apply_log_transform(img, gray, params):
    """Transformación logarítmica (realce de sombras)."""
    g = _to_gray_u8(img, gray).astype(np.float32)
    gain = float(params.get("gain", 255))
    out = np.log1p(g)
    out = out / (out.max() + 1e-8)
    out = (out * gain).clip(0, 255).astype(np.uint8)
    return out


def apply_gamma(img, gray, params):
    """Corrección gamma mediante LUT. gamma_x100=80 equivale a gamma=0.80"""
    g = _to_gray_u8(img, gray)
    gamma_x100 = float(params.get("gamma_x100", 80))
    gamma = max(gamma_x100 / 100.0, 0.01)
    lut = (np.power(np.arange(256, dtype=np.float32) / 255.0, gamma) * 255.0)
    lut = np.clip(lut, 0, 255).astype(np.uint8)
    return cv2.LUT(g, lut)


def apply_unsharp(img, gray, params):
    """Unsharp mask: realce de detalle controlado."""
    g = _to_gray_u8(img, gray)
    sigma = float(params.get("sigma_x10", 10)) / 10.0
    amount = float(params.get("amount_x100", 120)) / 100.0
    blur = cv2.GaussianBlur(g, (0, 0), sigmaX=sigma, sigmaY=sigma)
    return cv2.addWeighted(g, 1.0 + amount, blur, -amount, 0)


def apply_sobel_x(img, gray, params):
    """Sobel en X."""
    g = _to_gray_u8(img, gray)
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    sx = cv2.Sobel(g, cv2.CV_64F, 1, 0, ksize=k)
    sx = np.uint8(np.absolute(sx))
    return cv2.normalize(sx, None, 0, 255, cv2.NORM_MINMAX)


def apply_sobel_y(img, gray, params):
    """Sobel en Y."""
    g = _to_gray_u8(img, gray)
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    sy = cv2.Sobel(g, cv2.CV_64F, 0, 1, ksize=k)
    sy = np.uint8(np.absolute(sy))
    return cv2.normalize(sy, None, 0, 255, cv2.NORM_MINMAX)

# Mapeo de nombres a funciones
SPATIAL_FILTERS = {
"gaussiano": apply_gaussiano,
    "mediana": apply_mediana,
    "clahe": apply_clahe,
    "canny": apply_canny,
    "otsu": apply_otsu,
    "laplaciano": apply_laplaciano,
    "sobel": apply_sobel,
    "bilateral": apply_bilateral,
    "normalize": apply_normalize,
    "log_transform": apply_log_transform,
    "gamma": apply_gamma,
    "unsharp": apply_unsharp,
    "sobel_x": apply_sobel_x,
    "sobel_y": apply_sobel_y,
}

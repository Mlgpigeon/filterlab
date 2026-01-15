"""
Implementación de filtros espaciales - VERSIÓN CORREGIDA.

Cambios respecto a la versión original:
1. Todos los filtros devuelven RGB (3 canales) para consistencia
2. normalize mejorado con opción de estiramiento por percentiles
3. Filtros de bordes normalizados y con colormap opcional
4. Mejor documentación de comportamientos
"""

import cv2
import numpy as np


def _ensure_rgb(out):
    """Asegura salida en RGB (3 canales) para visualización consistente."""
    if out is None:
        return out
    if len(out.shape) == 2:
        return cv2.cvtColor(out, cv2.COLOR_GRAY2RGB)
    return out


def _is_gray_rgb(img):
    """Detecta imágenes RGB que en realidad son gris duplicado en 3 canales."""
    if img is None or len(img.shape) != 3 or img.shape[2] != 3:
        return False
    return (not np.any(img[:, :, 0] != img[:, :, 1])) and (not np.any(img[:, :, 0] != img[:, :, 2]))


def _apply_colormap(gray_u8):
    """Convierte un mapa de grises (uint8) a color (RGB) usando un colormap."""
    if gray_u8.dtype != np.uint8:
        gray_u8 = gray_u8.astype(np.uint8)
    cmap = getattr(cv2, "COLORMAP_TURBO", cv2.COLORMAP_JET)
    bgr = cv2.applyColorMap(gray_u8, cmap)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


# =============================================================================
# FILTROS DE SUAVIZADO
# =============================================================================

def apply_gaussiano(img, gray, params):
    """Aplica filtro Gaussiano para reducir ruido."""
    k = int(params.get("kernel_size", 5))
    k = k if k % 2 == 1 else k + 1
    sigma = params.get("sigma", 1.0)
    return cv2.GaussianBlur(img, (k, k), sigma)


def apply_mediana(img, gray, params):
    """Aplica filtro de Mediana para eliminar ruido sal y pimienta."""
    k = int(params.get("kernel_size", 5))
    k = k if k % 2 == 1 else k + 1
    result = cv2.medianBlur(img if len(img.shape) == 3 else gray, k)
    return _ensure_rgb(result)


def apply_bilateral(img, gray, params):
    """Aplica filtro Bilateral (suaviza preservando bordes)."""
    d = int(params.get("d", 9))
    d = d if d > 0 else 9
    sigma_color = float(params.get("sigma_color", 75))
    sigma_space = float(params.get("sigma_space", 75))
    
    src = img if len(img.shape) == 3 else gray
    out = cv2.bilateralFilter(src, d, sigma_color, sigma_space)
    return _ensure_rgb(out)


# =============================================================================
# FILTROS DE MEJORA DE CONTRASTE
# =============================================================================

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
        result = clahe.apply(gray)
        return _ensure_rgb(result)


def apply_normalize(img, gray, params):
    """
    Normaliza intensidades al rango 0-255.
    
    NOTA: Si la imagen ya tiene píxeles en 0 y 255, este filtro no tendrá
    efecto visible. Es útil para imágenes con rango reducido (ej: [50, 200]).
    
    Para mejorar contraste en imágenes normales, usar CLAHE o el nuevo
    normalize_percentile.
    """
    src = img if len(img.shape) == 3 else gray
    out = cv2.normalize(src, None, 0, 255, cv2.NORM_MINMAX)
    return _ensure_rgb(out.astype(np.uint8))


def apply_normalize_percentile(img, gray, params):
    """
    Normaliza por percentiles - SIEMPRE mejora el contraste.
    
    Recorta el 1% más oscuro y el 1% más brillante, luego estira
    el rango restante a [0, 255]. Esto garantiza una mejora visible.
    """
    low_pct = float(params.get("low_percentile", 1.0))
    high_pct = float(params.get("high_percentile", 99.0))
    
    src = img if len(img.shape) == 3 else gray
    
    if len(src.shape) == 3:
        # Procesar cada canal
        result = np.zeros_like(src)
        for i in range(3):
            channel = src[:, :, i]
            low_val = np.percentile(channel, low_pct)
            high_val = np.percentile(channel, high_pct)
            
            # Evitar división por cero
            if high_val - low_val < 1:
                result[:, :, i] = channel
            else:
                stretched = (channel.astype(float) - low_val) / (high_val - low_val) * 255
                result[:, :, i] = np.clip(stretched, 0, 255).astype(np.uint8)
        return result
    else:
        low_val = np.percentile(src, low_pct)
        high_val = np.percentile(src, high_pct)
        
        if high_val - low_val < 1:
            return _ensure_rgb(src)
        
        stretched = (src.astype(float) - low_val) / (high_val - low_val) * 255
        result = np.clip(stretched, 0, 255).astype(np.uint8)
        return _ensure_rgb(result)


def apply_log_transform(img, gray, params):
    """
    Transformación logarítmica: expande intensidades bajas.
    
    Útil para imágenes con mucho detalle en zonas oscuras que no se ve.
    c = gain / log(1 + 255), output = c * log(1 + input)
    """
    gain = float(params.get("gain", 255))
    
    src = img if len(img.shape) == 3 else gray
    src_f = src.astype(np.float32)
    
    # Transformación logarítmica normalizada
    c = gain / np.log1p(255.0)
    out = c * np.log1p(src_f)
    out = np.clip(out, 0, 255).astype(np.uint8)
    
    return _ensure_rgb(out)


def apply_gamma(img, gray, params):
    """
    Corrección gamma: output = 255 * (input/255)^gamma.
    
    - gamma < 1: Aclara la imagen (expande sombras)
    - gamma > 1: Oscurece la imagen (comprime sombras)
    """
    gamma = float(params.get("gamma", 0.8))
    gamma = max(gamma, 0.01)
    
    src = img if len(img.shape) == 3 else gray
    
    # Crear LUT para eficiencia
    lut = (np.power(np.arange(256, dtype=np.float32) / 255.0, gamma) * 255.0)
    lut = np.clip(lut, 0, 255).astype(np.uint8)
    
    out = cv2.LUT(src, lut)
    return _ensure_rgb(out)


def apply_unsharp(img, gray, params):
    """
    Unsharp Mask: aumenta la nitidez.
    
    output = input + amount * (input - blur(input))
    """
    sigma = float(params.get("sigma", 1.0))
    amount = float(params.get("amount", 1.2))
    
    src = img if len(img.shape) == 3 else gray
    blur = cv2.GaussianBlur(src, (0, 0), sigmaX=sigma, sigmaY=sigma)
    out = cv2.addWeighted(src, 1.0 + amount, blur, -amount, 0)
    
    return _ensure_rgb(out)


# =============================================================================
# FILTROS DE DETECCIÓN DE BORDES
# =============================================================================

def apply_canny(img, gray, params):
    """
    Detector de bordes Canny.
    
    Devuelve imagen binaria (bordes en blanco sobre negro).
    """
    low = int(params.get("low_threshold", 50))
    high = int(params.get("high_threshold", 150))
    result = cv2.Canny(gray, low, high)
    # CORRECCIÓN: Devolver RGB para consistencia
    return _ensure_rgb(result)


def apply_otsu(img, gray, params):
    """
    Binarización de Otsu.
    
    Encuentra automáticamente el umbral óptimo para separar
    el fondo del primer plano.
    """
    _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # CORRECCIÓN: Devolver RGB para consistencia
    return _ensure_rgb(result)


def apply_laplaciano(img, gray, params):
    """
    Filtro Laplaciano para detección de bordes.
    
    Detecta cambios rápidos de intensidad (segunda derivada).
    """
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    
    result = cv2.Laplacian(gray, cv2.CV_64F, ksize=k)
    result = np.uint8(np.absolute(result))
    
    # CORRECCIÓN: Normalizar y devolver RGB
    result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _ensure_rgb(result)


def apply_sobel(img, gray, params):
    """
    Filtro Sobel combinado (magnitud del gradiente).
    
    Combina gradientes horizontal y vertical.
    """
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k)
    magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    
    # CORRECCIÓN: Normalizar al rango completo [0, 255]
    result = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _ensure_rgb(result)


def apply_sobel_x(img, gray, params):
    """
    Sobel en dirección X (detecta bordes verticales).
    """
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    
    sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=k)
    sx = np.abs(sx)
    result = cv2.normalize(sx, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _apply_colormap(result)


def apply_sobel_y(img, gray, params):
    """
    Sobel en dirección Y (detecta bordes horizontales).
    """
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    
    sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=k)
    sy = np.abs(sy)
    result = cv2.normalize(sy, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _apply_colormap(result)


# =============================================================================
# MAPEO DE NOMBRES A FUNCIONES
# =============================================================================

SPATIAL_FILTERS = {
    # Suavizado
    "gaussiano": apply_gaussiano,
    "mediana": apply_mediana,
    "bilateral": apply_bilateral,
    
    # Mejora de contraste
    "clahe": apply_clahe,
    "normalize": apply_normalize,
    "normalize_percentile": apply_normalize_percentile,  # NUEVO
    "log_transform": apply_log_transform,
    "gamma": apply_gamma,
    "unsharp": apply_unsharp,
    
    # Detección de bordes
    "canny": apply_canny,
    "otsu": apply_otsu,
    "laplaciano": apply_laplaciano,
    "sobel": apply_sobel,
    "sobel_x": apply_sobel_x,
    "sobel_y": apply_sobel_y,
}

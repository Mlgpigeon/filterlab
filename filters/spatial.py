"""
Implementación de filtros espaciales.
"""

import cv2
import numpy as np


def _ensure_rgb(out):
    """Asegura salida en RGB (3 canales) para visualización consistente en Streamlit."""
    if out is None:
        return out
    if len(out.shape) == 2:
        return cv2.cvtColor(out, cv2.COLOR_GRAY2RGB)
    return out


def _is_gray_rgb(img):
    """Detecta imágenes RGB que en realidad son gris duplicado en 3 canales."""
    if img is None or len(img.shape) != 3 or img.shape[2] != 3:
        return False
    # Comparación rápida: si algún pixel difiere entre canales, no es gris.
    return (not np.any(img[:, :, 0] != img[:, :, 1])) and (not np.any(img[:, :, 0] != img[:, :, 2]))


def _apply_colormap(gray_u8):
    """Convierte un mapa de grises (uint8) a color (RGB) usando un colormap."""
    if gray_u8.dtype != np.uint8:
        gray_u8 = gray_u8.astype(np.uint8)
    # TURBO suele verse mejor que JET (menos 'arcoíris engañoso'), pero si no existe, fallback.
    cmap = getattr(cv2, "COLORMAP_TURBO", cv2.COLORMAP_JET)
    bgr = cv2.applyColorMap(gray_u8, cmap)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


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



def apply_bilateral(img, gray, params):
    """Aplica filtro Bilateral (suaviza preservando bordes)."""
    d = int(params.get("d", 9))
    d = d if d > 0 else 9
    sigma_color = float(params.get("sigma_color", 75))
    sigma_space = float(params.get("sigma_space", 75))
    # Si la imagen es realmente gris (duplicada en RGB), colorizamos el resultado
    if len(img.shape) == 3 and _is_gray_rgb(img):
        g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        out_g = cv2.bilateralFilter(g, d, sigma_color, sigma_space)
        return _apply_colormap(out_g)

    src = img if len(img.shape) == 3 else gray
    out = cv2.bilateralFilter(src, d, sigma_color, sigma_space)
    return _ensure_rgb(out)


def apply_normalize(img, gray, params):
    """Normaliza intensidades al rango 0-255."""
    if len(img.shape) == 3 and _is_gray_rgb(img):
        g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        out_g = cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        return _apply_colormap(out_g)

    src = img if len(img.shape) == 3 else gray
    out = cv2.normalize(src, None, 0, 255, cv2.NORM_MINMAX)
    return _ensure_rgb(out.astype(np.uint8))


def apply_log_transform(img, gray, params):
    """Transformación logarítmica: expande intensidades bajas."""
    gain = float(params.get("gain", 255))
    if len(img.shape) == 3 and _is_gray_rgb(img):
        src = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        src_f = src.astype(np.float32)
        denom = np.log1p(255.0)
        out_g = (np.log1p(src_f) / denom)
        out_g = (out_g * gain).clip(0, 255).astype(np.uint8)
        return _apply_colormap(out_g)

    src = img if len(img.shape) == 3 else gray
    src_f = src.astype(np.float32)

    # Escalado logarítmico estable: log(1 + x) / log(1 + 255)
    denom = np.log1p(255.0)
    out = np.log1p(src_f) / denom
    out = (out * gain).clip(0, 255).astype(np.uint8)
    return _ensure_rgb(out)


def apply_gamma(img, gray, params):
    """Corrección gamma: out = 255*(in/255)^gamma."""
    gamma = float(params.get("gamma", 0.8))
    gamma = max(gamma, 0.01)
    if len(img.shape) == 3 and _is_gray_rgb(img):
        g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        lut = (np.power(np.arange(256, dtype=np.float32) / 255.0, gamma) * 255.0)
        lut = np.clip(lut, 0, 255).astype(np.uint8)
        out_g = cv2.LUT(g, lut)
        return _apply_colormap(out_g)

    src = img if len(img.shape) == 3 else gray

    lut = (np.power(np.arange(256, dtype=np.float32) / 255.0, gamma) * 255.0)
    lut = np.clip(lut, 0, 255).astype(np.uint8)

    out = cv2.LUT(src, lut)
    return _ensure_rgb(out)


def apply_unsharp(img, gray, params):
    """Unsharp mask: realce de detalle controlado."""
    sigma = float(params.get("sigma", 1.0))
    amount = float(params.get("amount", 1.2))
    if len(img.shape) == 3 and _is_gray_rgb(img):
        g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(g, (0, 0), sigmaX=sigma, sigmaY=sigma)
        out_g = cv2.addWeighted(g, 1.0 + amount, blur, -amount, 0)
        return _apply_colormap(out_g)

    src = img if len(img.shape) == 3 else gray

    blur = cv2.GaussianBlur(src, (0, 0), sigmaX=sigma, sigmaY=sigma)
    out = cv2.addWeighted(src, 1.0 + amount, blur, -amount, 0)
    return _ensure_rgb(out)


def apply_sobel_x(img, gray, params):
    """Sobel en X (bordes verticales)."""
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=k)
    sx = np.abs(sx)
    out_g = cv2.normalize(sx, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _apply_colormap(out_g)


def apply_sobel_y(img, gray, params):
    """Sobel en Y (bordes horizontales)."""
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=k)
    sy = np.abs(sy)
    out_g = cv2.normalize(sy, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _apply_colormap(out_g)


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

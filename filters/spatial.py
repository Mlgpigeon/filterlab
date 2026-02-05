"""
Implementación de filtros espaciales.
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


def _apply_colormap(gray_u8):
    """Convierte un mapa de grises a color usando un colormap."""
    if gray_u8.dtype != np.uint8:
        gray_u8 = gray_u8.astype(np.uint8)
    cmap = getattr(cv2, "COLORMAP_TURBO", cv2.COLORMAP_JET)
    bgr = cv2.applyColorMap(gray_u8, cmap)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def apply_gaussiano(img, gray, params):
    k = int(params.get("kernel_size", 5))
    k = k if k % 2 == 1 else k + 1
    sigma = params.get("sigma", 1.0)
    return cv2.GaussianBlur(img, (k, k), sigma)


def apply_mediana(img, gray, params):
    k = int(params.get("kernel_size", 5))
    k = k if k % 2 == 1 else k + 1
    result = cv2.medianBlur(img if len(img.shape) == 3 else gray, k)
    return _ensure_rgb(result)


def apply_bilateral(img, gray, params):
    d = int(params.get("d", 9))
    d = d if d > 0 else 9
    sigma_color = float(params.get("sigma_color", 75))
    sigma_space = float(params.get("sigma_space", 75))
    src = img if len(img.shape) == 3 else gray
    out = cv2.bilateralFilter(src, d, sigma_color, sigma_space)
    return _ensure_rgb(out)


def apply_clahe(img, gray, params):
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
    src = img if len(img.shape) == 3 else gray
    out = cv2.normalize(src, None, 0, 255, cv2.NORM_MINMAX)
    return _ensure_rgb(out.astype(np.uint8))


def apply_normalize_percentile(img, gray, params):
    low_pct = float(params.get("low_percentile", 1.0))
    high_pct = float(params.get("high_percentile", 99.0))
    src = img if len(img.shape) == 3 else gray
    
    if len(src.shape) == 3:
        result = np.zeros_like(src)
        for i in range(3):
            channel = src[:, :, i]
            low_val = np.percentile(channel, low_pct)
            high_val = np.percentile(channel, high_pct)
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
    gain = float(params.get("gain", 255))
    src = img if len(img.shape) == 3 else gray
    src_f = src.astype(np.float32)
    c = gain / np.log1p(255.0)
    out = c * np.log1p(src_f)
    out = np.clip(out, 0, 255).astype(np.uint8)
    return _ensure_rgb(out)


def apply_gamma(img, gray, params):
    gamma = float(params.get("gamma", 0.8))
    gamma = max(gamma, 0.01)
    src = img if len(img.shape) == 3 else gray
    lut = (np.power(np.arange(256, dtype=np.float32) / 255.0, gamma) * 255.0)
    lut = np.clip(lut, 0, 255).astype(np.uint8)
    out = cv2.LUT(src, lut)
    return _ensure_rgb(out)


def apply_unsharp(img, gray, params):
    sigma = float(params.get("sigma", 1.0))
    amount = float(params.get("amount", 1.2))
    src = img if len(img.shape) == 3 else gray
    blur = cv2.GaussianBlur(src, (0, 0), sigmaX=sigma, sigmaY=sigma)
    out = cv2.addWeighted(src, 1.0 + amount, blur, -amount, 0)
    return _ensure_rgb(out)


def apply_canny(img, gray, params):
    low = int(params.get("low_threshold", 50))
    high = int(params.get("high_threshold", 150))
    result = cv2.Canny(gray, low, high)
    return _ensure_rgb(result)


def apply_otsu(img, gray, params):
    _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return _ensure_rgb(result)


def apply_laplaciano(img, gray, params):
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    result = cv2.Laplacian(gray, cv2.CV_64F, ksize=k)
    result = np.uint8(np.absolute(result))
    result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _ensure_rgb(result)


def apply_sobel(img, gray, params):
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k)
    magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
    result = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _ensure_rgb(result)


def apply_sobel_x(img, gray, params):
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=k)
    sx = np.abs(sx)
    result = cv2.normalize(sx, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _apply_colormap(result)


def apply_sobel_y(img, gray, params):
    k = int(params.get("kernel_size", 3))
    k = k if k % 2 == 1 else k + 1
    sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=k)
    sy = np.abs(sy)
    result = cv2.normalize(sy, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _apply_colormap(result)

def apply_equalize_hist(img, gray, params):
    """Ecualización global del histograma."""
    if len(img.shape) == 3:
        # Ecualizar cada canal
        result = np.zeros_like(img)
        for i in range(3):
            result[:, :, i] = cv2.equalizeHist(img[:, :, i])
        return result
    else:
        result = cv2.equalizeHist(gray)
        return _ensure_rgb(result)


def apply_skeleton(img, gray, params):
    """Esqueletización - reduce estructuras a líneas de 1 pixel."""
    from skimage.morphology import skeletonize
    # Binarizar primero
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    binary_bool = binary > 0
    skeleton = skeletonize(binary_bool)
    result = (skeleton * 255).astype(np.uint8)
    return _ensure_rgb(result)


def apply_hough_lines(img, gray, params):
    """Detecta líneas rectas usando transformada de Hough."""
    threshold = int(params.get("threshold", 50))
    min_line_length = int(params.get("min_line_length", 50))
    max_line_gap = int(params.get("max_line_gap", 10))
    
    # Detectar bordes primero
    edges = cv2.Canny(gray, 50, 150)
    
    # Detectar líneas
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold, 
                            minLineLength=min_line_length, 
                            maxLineGap=max_line_gap)
    
    # Dibujar líneas en imagen negra
    result = np.zeros_like(gray)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(result, (x1, y1), (x2, y2), 255, 2)
    
    return _ensure_rgb(result)


SPATIAL_FILTERS = {
    "gaussiano": apply_gaussiano,
    "mediana": apply_mediana,
    "bilateral": apply_bilateral,
    "clahe": apply_clahe,
    "normalize": apply_normalize,
    "normalize_percentile": apply_normalize_percentile,
    "log_transform": apply_log_transform,
    "gamma": apply_gamma,
    "unsharp": apply_unsharp,
    "canny": apply_canny,
    "otsu": apply_otsu,
    "laplaciano": apply_laplaciano,
    "sobel": apply_sobel,
    "sobel_x": apply_sobel_x,
    "sobel_y": apply_sobel_y,
    "equalize_hist": apply_equalize_hist,
    "skeleton": apply_skeleton,
    "hough_lines": apply_hough_lines,
}

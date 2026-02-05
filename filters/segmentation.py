"""
Filtros de segmentación para FilterLab.

Incluye:
- Otsu adaptativo (por bloques)
- Segmentación por color en espacio HSV
- Segmentación por color en espacio Lab
- Umbralización manual y adaptativa
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


# =============================================================================
# UMBRALIZACIÓN
# =============================================================================

def apply_umbral_manual(img, gray, params):
    """
    Umbralización manual con valor fijo.
    
    Convierte la imagen a binario usando un umbral específico.
    Píxeles >= umbral -> blanco (255), resto -> negro (0)
    """
    threshold = int(params.get("threshold", 127))
    invert = params.get("invert", False)
    
    if invert:
        _, result = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    else:
        _, result = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    
    return _ensure_rgb(result)


def apply_otsu(img, gray, params):
    """
    Binarización de Otsu (global).
    
    Encuentra automáticamente el umbral óptimo para separar
    fondo y primer plano minimizando la varianza intra-clase.
    """
    invert = params.get("invert", False)
    
    if invert:
        _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return _ensure_rgb(result)


def apply_otsu_adaptativo(img, gray, params):
    """
    Otsu Adaptativo (por bloques).
    
    Divide la imagen en bloques y aplica Otsu localmente a cada uno.
    Útil para imágenes con iluminación no uniforme.
    
    Params:
        block_size: Tamaño de cada bloque (debe ser impar)
        c: Constante a restar del umbral calculado
    """
    block_size = int(params.get("block_size", 35))
    c = int(params.get("c", 5))
    invert = params.get("invert", False)
    
    # Asegurar que block_size sea impar
    if block_size % 2 == 0:
        block_size += 1
    
    # Usar umbralización adaptativa con método Gaussiano
    # que pondera los píxeles vecinos según su distancia
    method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    
    if invert:
        thresh_type = cv2.THRESH_BINARY_INV
    else:
        thresh_type = cv2.THRESH_BINARY
    
    result = cv2.adaptiveThreshold(
        gray, 255, method, thresh_type, block_size, c
    )
    
    return _ensure_rgb(result)


def apply_umbral_adaptativo_media(img, gray, params):
    """
    Umbral adaptativo usando media local.
    
    El umbral se calcula como la media de los píxeles vecinos
    menos una constante C.
    """
    block_size = int(params.get("block_size", 35))
    c = int(params.get("c", 5))
    invert = params.get("invert", False)
    
    if block_size % 2 == 0:
        block_size += 1
    
    method = cv2.ADAPTIVE_THRESH_MEAN_C
    thresh_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    
    result = cv2.adaptiveThreshold(
        gray, 255, method, thresh_type, block_size, c
    )
    
    return _ensure_rgb(result)


# =============================================================================
# SEGMENTACIÓN POR COLOR - HSV
# =============================================================================

def apply_segmentacion_hsv(img, gray, params):
    """
    Segmentación por color en espacio HSV.
    
    HSV (Hue, Saturation, Value) separa el color (H) de la
    intensidad (V), lo que facilita la segmentación por color
    independientemente de la iluminación.
    
    Rangos HSV en OpenCV:
        H: 0-179 (360°/2)
        S: 0-255
        V: 0-255
    
    Para detectar VERDE (vegetación):
        H: 35-85 (verde en HSV)
        S: 40-255 (saturación mínima para evitar grises)
        V: 40-255 (brillo mínimo para evitar negros)
    """
    h_min = int(params.get("h_min", 35))
    h_max = int(params.get("h_max", 85))
    s_min = int(params.get("s_min", 40))
    s_max = int(params.get("s_max", 255))
    v_min = int(params.get("v_min", 40))
    v_max = int(params.get("v_max", 255))
    invert = params.get("invert", False)
    
    # Convertir a HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    # Crear máscara con los rangos especificados
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower, upper)
    
    if invert:
        mask = cv2.bitwise_not(mask)
    
    return _ensure_rgb(mask)


def apply_segmentacion_hsv_verde(img, gray, params):
    """
    Segmentación de vegetación (verde) en HSV.
    
    Preset optimizado para detectar zonas verdes/vegetación
    en imágenes satelitales.
    """
    # Parámetros preconfigurados para verde
    tolerancia = int(params.get("tolerancia", 25))
    s_min = int(params.get("saturacion_min", 30))
    v_min = int(params.get("brillo_min", 30))
    invert = params.get("invert", False)
    
    # Centro del verde en HSV: ~60 (de 0-179)
    h_center = 60
    h_min = max(0, h_center - tolerancia)
    h_max = min(179, h_center + tolerancia)
    
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    if invert:
        mask = cv2.bitwise_not(mask)
    
    return _ensure_rgb(mask)


def apply_segmentacion_hsv_marron(img, gray, params):
    """
    Segmentación de zonas deforestadas (marrón/tierra) en HSV.
    
    Preset optimizado para detectar suelo expuesto, tierra,
    y zonas deforestadas en imágenes satelitales.
    """
    tolerancia = int(params.get("tolerancia", 15))
    s_min = int(params.get("saturacion_min", 20))
    v_min = int(params.get("brillo_min", 40))
    invert = params.get("invert", False)
    
    # Marrón en HSV: H ~10-20
    h_center = 15
    h_min = max(0, h_center - tolerancia)
    h_max = min(30, h_center + tolerancia)
    
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    if invert:
        mask = cv2.bitwise_not(mask)
    
    return _ensure_rgb(mask)


# =============================================================================
# SEGMENTACIÓN POR COLOR - LAB
# =============================================================================

def apply_segmentacion_lab(img, gray, params):
    """
    Segmentación por color en espacio CIE Lab.
    
    Lab separa la luminosidad (L) de los componentes de color:
        L: 0-255 (luminosidad, negro a blanco)
        a: 0-255 (verde a rojo, centro=128)
        b: 0-255 (azul a amarillo, centro=128)
    
    Ventaja: Más uniforme perceptualmente que RGB o HSV.
    Ideal para distinguir vegetación (valores bajos de 'a')
    de suelo/tierra (valores altos de 'a' y 'b').
    """
    l_min = int(params.get("l_min", 0))
    l_max = int(params.get("l_max", 255))
    a_min = int(params.get("a_min", 0))
    a_max = int(params.get("a_max", 128))  # <128 = verde
    b_min = int(params.get("b_min", 0))
    b_max = int(params.get("b_max", 255))
    invert = params.get("invert", False)
    
    # Convertir a Lab
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    
    lower = np.array([l_min, a_min, b_min])
    upper = np.array([l_max, a_max, b_max])
    mask = cv2.inRange(lab, lower, upper)
    
    if invert:
        mask = cv2.bitwise_not(mask)
    
    return _ensure_rgb(mask)


def apply_segmentacion_lab_vegetacion(img, gray, params):
    """
    Segmentación de vegetación en espacio Lab.
    
    En Lab, la vegetación tiene valores bajos de 'a' (componente verde-rojo).
    Este preset está optimizado para detectar vegetación.
    """
    sensibilidad = int(params.get("sensibilidad", 120))  # Umbral de 'a'
    l_min = int(params.get("luminosidad_min", 20))
    invert = params.get("invert", False)
    
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    
    # Vegetación: L > l_min, a < sensibilidad (verde)
    lower = np.array([l_min, 0, 0])
    upper = np.array([255, sensibilidad, 255])
    mask = cv2.inRange(lab, lower, upper)
    
    if invert:
        mask = cv2.bitwise_not(mask)
    
    return _ensure_rgb(mask)


def apply_segmentacion_lab_suelo(img, gray, params):
    """
    Segmentación de suelo/tierra en espacio Lab.
    
    El suelo expuesto típicamente tiene:
    - Valores altos de 'a' (hacia rojo)
    - Valores altos de 'b' (hacia amarillo)
    """
    a_min = int(params.get("a_min", 128))  # >128 = hacia rojo
    b_min = int(params.get("b_min", 128))  # >128 = hacia amarillo
    l_min = int(params.get("luminosidad_min", 30))
    invert = params.get("invert", False)
    
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    
    lower = np.array([l_min, a_min, b_min])
    upper = np.array([255, 255, 255])
    mask = cv2.inRange(lab, lower, upper)
    
    if invert:
        mask = cv2.bitwise_not(mask)
    
    return _ensure_rgb(mask)


# =============================================================================
# VISUALIZACIÓN DE ESPACIOS DE COLOR
# =============================================================================

def apply_convertir_hsv(img, gray, params):
    """
    Convierte la imagen a espacio HSV para visualización.
    
    Útil para explorar los valores de H, S, V antes de segmentar.
    """
    canal = params.get("canal", "H")
    
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    
    if canal == "H":
        # Normalizar H de 0-179 a 0-255 para visualización
        result = (hsv[:, :, 0].astype(np.float32) * 255 / 179).astype(np.uint8)
    elif canal == "S":
        result = hsv[:, :, 1]
    elif canal == "V":
        result = hsv[:, :, 2]
    else:  # Todos
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    # Aplicar colormap para mejor visualización
    colored = cv2.applyColorMap(result, cv2.COLORMAP_JET)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)


def apply_convertir_lab(img, gray, params):
    """
    Convierte la imagen a espacio Lab para visualización.
    
    Útil para explorar los valores de L, a, b antes de segmentar.
    """
    canal = params.get("canal", "a")
    
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    
    if canal == "L":
        result = lab[:, :, 0]
    elif canal == "a":
        result = lab[:, :, 1]
    elif canal == "b":
        result = lab[:, :, 2]
    else:  # Todos
        return img  # Devolver original ya que Lab no es visualizable directamente
    
    # Aplicar colormap para mejor visualización
    colored = cv2.applyColorMap(result, cv2.COLORMAP_JET)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)


# =============================================================================
# DICCIONARIO DE FILTROS PARA REGISTRO
# =============================================================================

SEGMENTATION_FILTERS = {
    "umbral_manual": apply_umbral_manual,
    "otsu": apply_otsu,
    "otsu_adaptativo": apply_otsu_adaptativo,
    "umbral_adaptativo_media": apply_umbral_adaptativo_media,
    "segmentacion_hsv": apply_segmentacion_hsv,
    "segmentacion_hsv_verde": apply_segmentacion_hsv_verde,
    "segmentacion_hsv_marron": apply_segmentacion_hsv_marron,
    "segmentacion_lab": apply_segmentacion_lab,
    "segmentacion_lab_vegetacion": apply_segmentacion_lab_vegetacion,
    "segmentacion_lab_suelo": apply_segmentacion_lab_suelo,
    "convertir_hsv": apply_convertir_hsv,
    "convertir_lab": apply_convertir_lab,
}

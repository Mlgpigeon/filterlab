"""
Filtros de segmentación para FilterLab.
"""

import cv2
import numpy as np


def _ensure_rgb(out):
    if out is None:
        return out
    if len(out.shape) == 2:
        return cv2.cvtColor(out, cv2.COLOR_GRAY2RGB)
    return out


def apply_umbral_manual(img, gray, params):
    threshold = int(params.get("threshold", 127))
    invert = params.get("invert", False)
    if invert:
        _, result = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    else:
        _, result = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return _ensure_rgb(result)


def apply_otsu(img, gray, params):
    invert = params.get("invert", False)
    if invert:
        _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    else:
        _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return _ensure_rgb(result)


def apply_otsu_adaptativo(img, gray, params):
    block_size = int(params.get("block_size", 35))
    c = int(params.get("c", 5))
    invert = params.get("invert", False)
    if block_size % 2 == 0:
        block_size += 1
    method = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
    thresh_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    result = cv2.adaptiveThreshold(gray, 255, method, thresh_type, block_size, c)
    return _ensure_rgb(result)


def apply_umbral_adaptativo_media(img, gray, params):
    block_size = int(params.get("block_size", 35))
    c = int(params.get("c", 5))
    invert = params.get("invert", False)
    if block_size % 2 == 0:
        block_size += 1
    method = cv2.ADAPTIVE_THRESH_MEAN_C
    thresh_type = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    result = cv2.adaptiveThreshold(gray, 255, method, thresh_type, block_size, c)
    return _ensure_rgb(result)


def apply_segmentacion_hsv(img, gray, params):
    h_min = int(params.get("h_min", 35))
    h_max = int(params.get("h_max", 85))
    s_min = int(params.get("s_min", 40))
    s_max = int(params.get("s_max", 255))
    v_min = int(params.get("v_min", 40))
    v_max = int(params.get("v_max", 255))
    invert = params.get("invert", False)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower, upper)
    if invert:
        mask = cv2.bitwise_not(mask)
    return _ensure_rgb(mask)


def apply_segmentacion_hsv_verde(img, gray, params):
    tolerancia = int(params.get("tolerancia", 25))
    s_min = int(params.get("saturacion_min", 30))
    v_min = int(params.get("brillo_min", 30))
    invert = params.get("invert", False)
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
    tolerancia = int(params.get("tolerancia", 15))
    s_min = int(params.get("saturacion_min", 20))
    v_min = int(params.get("brillo_min", 40))
    invert = params.get("invert", False)
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


def apply_segmentacion_lab(img, gray, params):
    l_min = int(params.get("l_min", 0))
    l_max = int(params.get("l_max", 255))
    a_min = int(params.get("a_min", 0))
    a_max = int(params.get("a_max", 128))
    b_min = int(params.get("b_min", 0))
    b_max = int(params.get("b_max", 255))
    invert = params.get("invert", False)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    lower = np.array([l_min, a_min, b_min])
    upper = np.array([l_max, a_max, b_max])
    mask = cv2.inRange(lab, lower, upper)
    if invert:
        mask = cv2.bitwise_not(mask)
    return _ensure_rgb(mask)


def apply_segmentacion_lab_vegetacion(img, gray, params):
    sensibilidad = int(params.get("sensibilidad", 120))
    l_min = int(params.get("luminosidad_min", 20))
    invert = params.get("invert", False)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    lower = np.array([l_min, 0, 0])
    upper = np.array([255, sensibilidad, 255])
    mask = cv2.inRange(lab, lower, upper)
    if invert:
        mask = cv2.bitwise_not(mask)
    return _ensure_rgb(mask)


def apply_segmentacion_lab_suelo(img, gray, params):
    a_min = int(params.get("a_min", 128))
    b_min = int(params.get("b_min", 128))
    l_min = int(params.get("luminosidad_min", 30))
    invert = params.get("invert", False)
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    lower = np.array([l_min, a_min, b_min])
    upper = np.array([255, 255, 255])
    mask = cv2.inRange(lab, lower, upper)
    if invert:
        mask = cv2.bitwise_not(mask)
    return _ensure_rgb(mask)


def apply_convertir_hsv(img, gray, params):
    canal = params.get("canal", "H")
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    if canal == "H":
        result = (hsv[:, :, 0].astype(np.float32) * 255 / 179).astype(np.uint8)
    elif canal == "S":
        result = hsv[:, :, 1]
    elif canal == "V":
        result = hsv[:, :, 2]
    else:
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    colored = cv2.applyColorMap(result, cv2.COLORMAP_JET)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)


def apply_convertir_lab(img, gray, params):
    canal = params.get("canal", "a")
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    if canal == "L":
        result = lab[:, :, 0]
    elif canal == "a":
        result = lab[:, :, 1]
    elif canal == "b":
        result = lab[:, :, 2]
    else:
        return img
    colored = cv2.applyColorMap(result, cv2.COLORMAP_JET)
    return cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)


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

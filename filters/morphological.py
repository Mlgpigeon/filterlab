"""
Implementación de filtros morfológicos.
"""

import cv2
import numpy as np


def _ensure_rgb(out):
    if out is None:
        return out
    if len(out.shape) == 2:
        return cv2.cvtColor(out, cv2.COLOR_GRAY2RGB)
    return out


def _get_kernel(size, shape='rect'):
    size = int(size)
    size = max(1, size)
    size = size if size % 2 == 1 else size + 1
    shapes = {'rect': cv2.MORPH_RECT, 'ellipse': cv2.MORPH_ELLIPSE, 'cross': cv2.MORPH_CROSS}
    morph_shape = shapes.get(shape, cv2.MORPH_RECT)
    return cv2.getStructuringElement(morph_shape, (size, size))


def _is_binary_image(img):
    if len(img.shape) == 3:
        channel = img[:, :, 0]
    else:
        channel = img
    unique = np.unique(channel)
    return len(unique) <= 2 and (set(unique) <= {0, 255})


def _is_edge_image(img):
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    if not _is_binary_image(img):
        return False
    white_ratio = np.sum(gray == 255) / gray.size
    return white_ratio < 0.2


def _get_working_image(img, gray):
    if len(img.shape) == 3:
        if np.array_equal(img[:,:,0], img[:,:,1]) and np.array_equal(img[:,:,1], img[:,:,2]):
            return gray
    return gray if len(img.shape) == 2 else img


def apply_erosion(img, gray, params):
    k = int(params.get("kernel_size", 3))
    iterations = int(params.get("iterations", 1))
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    result = cv2.erode(work_img, kernel, iterations=iterations)
    return _ensure_rgb(result)


def apply_dilatacion(img, gray, params):
    k = int(params.get("kernel_size", 3))
    iterations = int(params.get("iterations", 1))
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    result = cv2.dilate(work_img, kernel, iterations=iterations)
    return _ensure_rgb(result)


def apply_apertura(img, gray, params):
    k = int(params.get("kernel_size", 3))
    work_img = _get_working_image(img, gray)
    if _is_edge_image(img) and k > 1:
        kernel_small = _get_kernel(1)
        kernel = _get_kernel(k)
        eroded = cv2.erode(work_img, kernel_small, iterations=1)
        result = cv2.dilate(eroded, kernel, iterations=1)
    else:
        kernel = _get_kernel(k)
        result = cv2.morphologyEx(work_img, cv2.MORPH_OPEN, kernel)
    return _ensure_rgb(result)


def apply_clausura(img, gray, params):
    k = int(params.get("kernel_size", 3))
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    result = cv2.morphologyEx(work_img, cv2.MORPH_CLOSE, kernel)
    return _ensure_rgb(result)


def apply_tophat(img, gray, params):
    k = int(params.get("kernel_size", 5))
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    result = cv2.morphologyEx(work_img, cv2.MORPH_TOPHAT, kernel)
    if result.max() > result.min():
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _ensure_rgb(result)


def apply_blackhat(img, gray, params):
    k = int(params.get("kernel_size", 5))
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    result = cv2.morphologyEx(work_img, cv2.MORPH_BLACKHAT, kernel)
    if result.max() > result.min():
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _ensure_rgb(result)


def apply_gradiente(img, gray, params):
    k = int(params.get("kernel_size", 3))
    work_img = _get_working_image(img, gray)
    kernel = _get_kernel(k)
    result = cv2.morphologyEx(work_img, cv2.MORPH_GRADIENT, kernel)
    if result.max() > result.min():
        result = cv2.normalize(result, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return _ensure_rgb(result)


MORPHOLOGICAL_FILTERS = {
    "erosion": apply_erosion,
    "dilatacion": apply_dilatacion,
    "apertura": apply_apertura,
    "clausura": apply_clausura,
    "tophat": apply_tophat,
    "blackhat": apply_blackhat,
    "gradiente": apply_gradiente,
}

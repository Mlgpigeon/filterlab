"""
Utilidades para procesamiento de imágenes.
"""

import cv2
import numpy as np
from PIL import Image
import io


def load_image(uploaded_file):
    """
    Carga una imagen desde un archivo subido y la convierte a RGB.
    """
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    
    if len(img_array.shape) == 2:
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
    elif img_array.shape[2] == 4:
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    else:
        img_rgb = img_array
    
    return img_rgb


def image_to_bytes(img, format='PNG'):
    """Convierte una imagen numpy a bytes para descarga."""
    pil_img = Image.fromarray(img)
    buf = io.BytesIO()
    pil_img.save(buf, format=format)
    return buf.getvalue()


def get_image_info(img):
    """Obtiene información básica de una imagen."""
    return {
        "width": img.shape[1],
        "height": img.shape[0],
        "channels": img.shape[2] if len(img.shape) == 3 else 1,
        "dtype": str(img.dtype),
    }

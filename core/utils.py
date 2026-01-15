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
    
    Args:
        uploaded_file: Archivo subido desde Streamlit
        
    Returns:
        numpy array en formato RGB
    """
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    
    # Convertir a RGB si es necesario
    if len(img_array.shape) == 2:
        # Grayscale -> RGB
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
    elif img_array.shape[2] == 4:
        # RGBA -> RGB
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    else:
        img_rgb = img_array
    
    return img_rgb


def image_to_bytes(img, format='PNG'):
    """
    Convierte una imagen numpy a bytes para descarga.
    
    Args:
        img: numpy array de imagen
        format: Formato de salida (PNG, JPEG, etc.)
        
    Returns:
        bytes de la imagen
    """
    if len(img.shape) == 2:
        pil_img = Image.fromarray(img)
    else:
        pil_img = Image.fromarray(img)
    
    buf = io.BytesIO()
    pil_img.save(buf, format=format)
    return buf.getvalue()


def get_image_info(img):
    """
    Obtiene información básica de una imagen.
    
    Args:
        img: numpy array de imagen
        
    Returns:
        dict con información de la imagen
    """
    info = {
        "width": img.shape[1],
        "height": img.shape[0],
        "channels": img.shape[2] if len(img.shape) == 3 else 1,
        "dtype": str(img.dtype),
    }
    return info

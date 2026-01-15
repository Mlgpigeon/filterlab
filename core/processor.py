"""
Procesador central de filtros.
Orquesta la aplicación de filtros a imágenes.
"""

import cv2
from filters import SPATIAL_FILTERS, MORPHOLOGICAL_FILTERS


def apply_filter(img, filter_name, params):
    """
    Aplica un filtro específico a la imagen.
    
    Args:
        img: Imagen de entrada (numpy array RGB o grayscale)
        filter_name: Nombre del filtro a aplicar
        params: Diccionario con parámetros del filtro
        
    Returns:
        Imagen procesada
    """
    result = img.copy()
    
    # Convertir a escala de grises si es necesario
    if len(result.shape) == 3:
        gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    else:
        gray = result
    
    # Buscar y aplicar el filtro
    if filter_name in SPATIAL_FILTERS:
        return SPATIAL_FILTERS[filter_name](result, gray, params)
    elif filter_name in MORPHOLOGICAL_FILTERS:
        return MORPHOLOGICAL_FILTERS[filter_name](result, gray, params)
    
    # Si no se encuentra el filtro, devolver imagen sin cambios
    return result


def apply_filter_chain(img, filter_list):
    """
    Aplica una cadena de filtros a la imagen.
    
    Args:
        img: Imagen de entrada
        filter_list: Lista de tuplas (filter_name, params)
        
    Returns:
        Imagen con todos los filtros aplicados en orden
    """
    result = img.copy()
    for filter_name, params in filter_list:
        result = apply_filter(result, filter_name, params)
    return result

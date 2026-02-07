"""
Procesador central de filtros.
Orquesta la aplicación de filtros a imágenes.
"""

import cv2
import numpy as np
from filters import SPATIAL_FILTERS, MORPHOLOGICAL_FILTERS
from filters.segmentation import SEGMENTATION_FILTERS


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
    elif filter_name in SEGMENTATION_FILTERS:
        return SEGMENTATION_FILTERS[filter_name](result, gray, params)
    
    # Si no se encuentra el filtro, devolver imagen sin cambios
    return result


def apply_filter_chain(img, filter_list):
    """
    Aplica una cadena de filtros a la imagen.
    
    COMPORTAMIENTO ESPECIAL CON OVERLAY:
    Si 'overlay_mask' está en la cadena:
    - Se guarda la imagen justo ANTES del overlay
    - Los filtros de segmentación DESPUÉS del overlay se aplican sobre esa imagen guardada
    - El resultado se pasa al overlay para superposición
    
    Args:
        img: Imagen de entrada
        filter_list: Lista de tuplas (filter_name, params)
        
    Returns:
        Imagen con todos los filtros aplicados en orden
    """
    result = img.copy()
    
    # Detectar si hay overlay en la cadena
    overlay_idx = None
    for idx, (filter_name, _) in enumerate(filter_list):
        if filter_name == "overlay_mask":
            overlay_idx = idx
            break
    
    # CASO 1: NO hay overlay - procesamiento normal
    if overlay_idx is None:
        for filter_name, params in filter_list:
            result = apply_filter(result, filter_name, params)
        return result
    
    # CASO 2: HAY overlay - procesamiento especial
    # Aplicar filtros ANTES del overlay
    for i in range(overlay_idx):
        filter_name, params = filter_list[i]
        result = apply_filter(result, filter_name, params)
    
    # Guardar imagen preprocesada (para overlay)
    img_preprocesada = result.copy()
    
    # Aplicar filtros DESPUÉS del overlay (segmentación)
    # Estos generan la máscara binaria
    for i in range(overlay_idx + 1, len(filter_list)):
        filter_name, params = filter_list[i]
        result = apply_filter(result, filter_name, params)
    
    # Ahora result es la máscara binaria
    # Convertir a escala de grises si es necesario
    if len(result.shape) == 3:
        mask_gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    else:
        mask_gray = result
    
    # Aplicar overlay usando imagen preprocesada + máscara
    _, overlay_params = filter_list[overlay_idx]
    
    # Llamar directamente a la función de overlay con los datos correctos
    from filters.segmentation import apply_overlay_mask
    result_final = apply_overlay_mask(img_preprocesada, mask_gray, overlay_params)
    
    return result_final
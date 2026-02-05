"""
Módulo para cálculo de áreas a partir de máscaras binarias.

Permite convertir el conteo de píxeles en unidades reales (km², hectáreas, etc.)
usando la escala de la imagen.
"""

import numpy as np
import cv2
from typing import Tuple, Dict, Optional


class AreaCalculator:
    """
    Calculadora de áreas para imágenes con escala conocida.
    
    Parameters
    ----------
    scale_km : float
        Kilómetros que representa la escala de referencia
    scale_pixels : int
        Píxeles que representa la escala de referencia
    """
    
    def __init__(self, scale_km: float = 20.0, scale_pixels: int = 51):
        """
        Inicializa el calculador con la escala.
        
        Escala por defecto: 20 km = 51 píxeles (Jamanxim)
        """
        self.scale_km = scale_km
        self.scale_pixels = scale_pixels
        self.km_per_pixel = scale_km / scale_pixels
        self.km2_per_pixel = self.km_per_pixel ** 2
    
    def set_scale(self, scale_km: float, scale_pixels: int):
        """Actualiza la escala."""
        self.scale_km = scale_km
        self.scale_pixels = scale_pixels
        self.km_per_pixel = scale_km / scale_pixels
        self.km2_per_pixel = self.km_per_pixel ** 2
    
    def get_scale_info(self) -> Dict[str, float]:
        """Retorna información de la escala actual."""
        return {
            'scale_km': self.scale_km,
            'scale_pixels': self.scale_pixels,
            'km_per_pixel': self.km_per_pixel,
            'km2_per_pixel': self.km2_per_pixel,
            'ha_per_pixel': self.km2_per_pixel * 100  # 1 km² = 100 ha
        }
    
    def count_white_pixels(self, mask: np.ndarray) -> int:
        """
        Cuenta píxeles blancos (255) en una máscara.
        
        Parameters
        ----------
        mask : np.ndarray
            Máscara binaria (puede ser grayscale o RGB)
        
        Returns
        -------
        int
            Número de píxeles blancos
        """
        # Convertir a grayscale si es necesario
        if len(mask.shape) == 3:
            gray = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        else:
            gray = mask
        
        return np.sum(gray > 127)
    
    def calculate_area_km2(self, mask: np.ndarray) -> float:
        """
        Calcula el área en km² de los píxeles blancos.
        
        Parameters
        ----------
        mask : np.ndarray
            Máscara binaria
        
        Returns
        -------
        float
            Área en km²
        """
        n_pixels = self.count_white_pixels(mask)
        return n_pixels * self.km2_per_pixel
    
    def calculate_area_hectares(self, mask: np.ndarray) -> float:
        """Calcula el área en hectáreas."""
        return self.calculate_area_km2(mask) * 100
    
    def calculate_percentage(self, mask: np.ndarray) -> float:
        """
        Calcula el porcentaje de área blanca respecto al total.
        
        Returns
        -------
        float
            Porcentaje (0-100)
        """
        if len(mask.shape) == 3:
            gray = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        else:
            gray = mask
        
        total_pixels = gray.size
        white_pixels = np.sum(gray > 127)
        
        return (white_pixels / total_pixels) * 100
    
    def get_statistics(self, mask: np.ndarray) -> Dict[str, float]:
        """
        Obtiene estadísticas completas de área.
        
        Returns
        -------
        dict
            - n_pixels: número de píxeles blancos
            - area_km2: área en km²
            - area_ha: área en hectáreas
            - percentage: porcentaje del total
        """
        n_pixels = self.count_white_pixels(mask)
        area_km2 = n_pixels * self.km2_per_pixel
        
        if len(mask.shape) == 3:
            gray = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        else:
            gray = mask
        
        total_pixels = gray.size
        percentage = (n_pixels / total_pixels) * 100
        
        return {
            'n_pixels': n_pixels,
            'area_km2': area_km2,
            'area_ha': area_km2 * 100,
            'percentage': percentage,
            'total_pixels': total_pixels
        }


def create_overlay(original: np.ndarray, mask: np.ndarray, 
                   color: Tuple[int, int, int] = (255, 0, 0),
                   alpha: float = 0.5) -> np.ndarray:
    """
    Crea una superposición coloreada de la máscara sobre la imagen original.
    
    Parameters
    ----------
    original : np.ndarray
        Imagen original RGB
    mask : np.ndarray
        Máscara binaria
    color : tuple
        Color RGB para la superposición
    alpha : float
        Transparencia (0-1)
    
    Returns
    -------
    np.ndarray
        Imagen con overlay
    """
    # Asegurar que la máscara es grayscale
    if len(mask.shape) == 3:
        mask_gray = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
    else:
        mask_gray = mask
    
    # Crear capa de color
    overlay = original.copy()
    color_layer = np.zeros_like(original)
    color_layer[:, :] = color
    
    # Crear máscara booleana
    mask_bool = mask_gray > 127
    
    # Aplicar overlay
    overlay[mask_bool] = (
        (1 - alpha) * original[mask_bool] + 
        alpha * color_layer[mask_bool]
    ).astype(np.uint8)
    
    return overlay


def add_area_text(image: np.ndarray, area_km2: float, 
                  position: str = 'top-right',
                  font_scale: float = 1.0) -> np.ndarray:
    """
    Añade texto con el área calculada a la imagen.
    
    Parameters
    ----------
    image : np.ndarray
        Imagen donde añadir el texto
    area_km2 : float
        Área en km²
    position : str
        'top-left', 'top-right', 'bottom-left', 'bottom-right'
    font_scale : float
        Escala de la fuente
    
    Returns
    -------
    np.ndarray
        Imagen con texto
    """
    result = image.copy()
    h, w = result.shape[:2]
    
    text = f"{area_km2:,.2f} km2"
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = max(1, int(font_scale * 2))
    
    # Calcular tamaño del texto
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # Determinar posición
    padding = 10
    positions = {
        'top-left': (padding, text_h + padding),
        'top-right': (w - text_w - padding, text_h + padding),
        'bottom-left': (padding, h - padding),
        'bottom-right': (w - text_w - padding, h - padding)
    }
    pos = positions.get(position, positions['top-right'])
    
    # Añadir fondo semitransparente
    bg_rect = (pos[0] - 5, pos[1] - text_h - 5, 
               pos[0] + text_w + 5, pos[1] + 5)
    cv2.rectangle(result, (bg_rect[0], bg_rect[1]), (bg_rect[2], bg_rect[3]), 
                  (0, 0, 0), -1)
    
    # Añadir texto
    cv2.putText(result, text, pos, font, font_scale, (255, 255, 255), thickness)
    
    return result

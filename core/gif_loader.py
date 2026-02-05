"""
Módulo para carga y procesamiento de archivos animados (GIF/WEBP).

Permite extraer frames individuales de archivos animados para
análisis multitemporal (ej: deforestación a lo largo del tiempo).
"""

import numpy as np
from PIL import Image
from typing import List, Tuple, Optional
import io


def load_animated_file(file_or_path) -> Tuple[List[np.ndarray], dict]:
    """
    Carga un archivo animado (GIF/WEBP) y extrae todos los frames.
    
    Parameters
    ----------
    file_or_path : str or file-like object
        Ruta al archivo o objeto file (ej: UploadedFile de Streamlit)
    
    Returns
    -------
    frames : List[np.ndarray]
        Lista de frames como arrays RGB (H, W, 3)
    info : dict
        Información del archivo:
        - n_frames: número de frames
        - size: (width, height)
        - format: formato del archivo
    """
    # Abrir imagen
    if isinstance(file_or_path, str):
        img = Image.open(file_or_path)
    else:
        # Objeto file-like (ej: Streamlit UploadedFile)
        img = Image.open(file_or_path)
    
    frames = []
    n_frames = getattr(img, 'n_frames', 1)
    
    for i in range(n_frames):
        img.seek(i)
        # Convertir a RGB
        frame = img.convert('RGB')
        frame_array = np.array(frame)
        frames.append(frame_array)
    
    info = {
        'n_frames': n_frames,
        'size': img.size,  # (width, height)
        'format': img.format or 'Unknown'
    }
    
    return frames, info


def crop_frames(frames: List[np.ndarray], 
                top: int = 0, bottom: int = 0,
                left: int = 0, right: int = 0) -> List[np.ndarray]:
    """
    Recorta todos los frames para eliminar bordes (texto, escalas, etc.).
    
    Parameters
    ----------
    frames : List[np.ndarray]
        Lista de frames
    top, bottom, left, right : int
        Píxeles a recortar de cada lado
    
    Returns
    -------
    List[np.ndarray]
        Frames recortados
    """
    cropped = []
    for frame in frames:
        h, w = frame.shape[:2]
        cropped_frame = frame[top:h-bottom if bottom > 0 else h, 
                              left:w-right if right > 0 else w]
        cropped.append(cropped_frame)
    return cropped


def get_frame_by_index(frames: List[np.ndarray], index: int) -> np.ndarray:
    """Obtiene un frame específico por índice."""
    if 0 <= index < len(frames):
        return frames[index]
    raise IndexError(f"Índice {index} fuera de rango [0, {len(frames)-1}]")


def assign_years_to_frames(frames: List[np.ndarray], 
                           start_year: int = 2000) -> List[Tuple[int, np.ndarray]]:
    """
    Asigna años a los frames (asumiendo un frame por año).
    
    Parameters
    ----------
    frames : List[np.ndarray]
        Lista de frames
    start_year : int
        Año del primer frame
    
    Returns
    -------
    List[Tuple[int, np.ndarray]]
        Lista de tuplas (año, frame)
    """
    return [(start_year + i, frame) for i, frame in enumerate(frames)]

"""
Módulo core de FilterLab - Análisis y procesamiento batch.

Incluye:
- AnalisisArea: Cálculo de áreas en unidades reales
- AnalisisTemporal: Series temporales de imágenes
- ProcesadorBatch: Procesamiento de múltiples imágenes
- PipelineFiltros: Cadenas configurables de filtros
"""

from .processor import apply_filter, apply_filter_chain
from .utils import load_image, image_to_bytes, get_image_info

__all__ = [
    
]

from .analysis import (
    AnalisisArea,
    AnalisisTemporal,
    ImageStats,
    AreaResult,
    calcular_area_rapido,
    comparar_imagenes
)

from .batch import (
    CargadorImagenes,
    PipelineFiltros,
    ProcesadorBatch,
    ImagenProcesada,
    procesar_carpeta_rapido,
    extraer_frames_gif
)

__all__ = [
    # Analysis
    'AnalisisArea',
    'AnalisisTemporal',
    'ImageStats',
    'AreaResult',
    'calcular_area_rapido',
    'comparar_imagenes',
    # Batch
    'CargadorImagenes',
    'PipelineFiltros',
    'ProcesadorBatch',
    'ImagenProcesada',
    'procesar_carpeta_rapido',
    'extraer_frames_gif',
    "apply_filter",
    "apply_filter_chain",
    "load_image",
    "image_to_bytes",
    "get_image_info",
]

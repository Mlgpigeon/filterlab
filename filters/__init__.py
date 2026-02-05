"""
Paquete de filtros de imagen.
"""
from .segmentation import SEGMENTATION_FILTERS

from .definitions import (
    FILTROS_ESPACIALES,
    FILTROS_MORFOLOGICOS,
    FILTROS_SEGMENTACION,
    get_all_filters,
    get_filter_info,
    get_filters_by_category,
    get_categories,
    CATEGORIAS
)
from .spatial import SPATIAL_FILTERS
from .morphological import MORPHOLOGICAL_FILTERS

__all__ = [
    "FILTROS_ESPACIALES",
    "FILTROS_MORFOLOGICOS",
    "SPATIAL_FILTERS",
    "MORPHOLOGICAL_FILTERS",
    "get_all_filters",
    "get_filter_info",
    'SEGMENTATION_FILTERS',
    'FILTROS_ESPACIALES',
    'FILTROS_MORFOLOGICOS',
    'FILTROS_SEGMENTACION',
    'get_all_filters',
    'get_filter_info',
    'get_filters_by_category',
    'get_categories',
    'CATEGORIAS'
]

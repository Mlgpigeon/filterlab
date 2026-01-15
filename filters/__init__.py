"""
Paquete de filtros de imagen.
"""

from .definitions import (
    FILTROS_ESPACIALES,
    FILTROS_MORFOLOGICOS,
    get_all_filters,
    get_filter_info,
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
]

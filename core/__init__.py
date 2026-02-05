"""
Módulo core de FilterLab - Análisis y procesamiento batch.
"""

from .processor import apply_filter, apply_filter_chain
from .utils import load_image, image_to_bytes, get_image_info

__all__ = [
    "apply_filter",
    "apply_filter_chain",
    "load_image",
    "image_to_bytes",
    "get_image_info",
]

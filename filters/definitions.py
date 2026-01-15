"""
Definiciones de filtros disponibles en FilterLab.
Cada filtro tiene: nombre, descripción y parámetros configurables.
"""

FILTROS_ESPACIALES = {
    "gaussiano": {
        "nombre": "Gaussiano",
        "descripcion": "Suavizado mediante convolución gaussiana. Reduce ruido.",
        "params": {
            "kernel_size": {"min": 3, "max": 31, "default": 5, "step": 2, "label": "Tamaño kernel"},
            "sigma": {"min": 0.1, "max": 10.0, "default": 1.0, "step": 0.1, "label": "Sigma"}
        }
    },
    "mediana": {
        "nombre": "Mediana",
        "descripcion": "Elimina ruido sal y pimienta preservando bordes.",
        "params": {
            "kernel_size": {"min": 3, "max": 31, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "clahe": {
        "nombre": "CLAHE",
        "descripcion": "Ecualización adaptativa de histograma con límite de contraste.",
        "params": {
            "clip_limit": {"min": 1.0, "max": 10.0, "default": 2.0, "step": 0.5, "label": "Clip Limit"},
            "tile_size": {"min": 2, "max": 16, "default": 8, "step": 1, "label": "Tile Size"}
        }
    },
    "canny": {
        "nombre": "Canny",
        "descripcion": "Detecta bordes mediante gradiente e histéresis.",
        "params": {
            "low_threshold": {"min": 0, "max": 255, "default": 50, "step": 5, "label": "Umbral bajo"},
            "high_threshold": {"min": 0, "max": 255, "default": 150, "step": 5, "label": "Umbral alto"}
        }
    },
    "otsu": {
        "nombre": "Otsu",
        "descripcion": "Binarización automática óptima.",
        "params": {}
    },
    "laplaciano": {
        "nombre": "Laplaciano",
        "descripcion": "Detecta bordes mediante segunda derivada.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "sobel": {
        "nombre": "Sobel",
        "descripcion": "Detecta bordes horizontales y verticales.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    }
    ,
    "bilateral": {
        "nombre": "Bilateral",
        "descripcion": "Suaviza preservando bordes (reduce ruido sin emborronar contornos).",
        "params": {
            "d": {"min": 1, "max": 25, "default": 9, "step": 2, "label": "Diámetro (d)"},
            "sigmaColor": {"min": 1, "max": 200, "default": 75, "step": 1, "label": "Sigma Color"},
            "sigmaSpace": {"min": 1, "max": 200, "default": 75, "step": 1, "label": "Sigma Space"}
        }
    },
    "normalize": {
        "nombre": "Normalizar (0-255)",
        "descripcion": "Reescala intensidades al rango completo (mejora contraste global).",
        "params": {}
    },
    "log_transform": {
        "nombre": "Transformación logarítmica",
        "descripcion": "Expande intensidades bajas: aparece detalle en zonas oscuras.",
        "params": {
            "gain": {"min": 1, "max": 255, "default": 255, "step": 1, "label": "Ganancia"}
        }
    },
    "gamma": {
        "nombre": "Corrección gamma",
        "descripcion": "Ajusta rango dinámico: γ<1 aclara sombras, γ>1 oscurece sombras.",
        "params": {
            "gamma_x100": {"min": 10, "max": 300, "default": 80, "step": 1, "label": "Gamma x100"}
        }
    },
    "unsharp": {
        "nombre": "Unsharp Mask (enfoque)",
        "descripcion": "Aumenta nitidez: imagen + k*(imagen - blur).",
        "params": {
            "sigma_x10": {"min": 1, "max": 50, "default": 10, "step": 1, "label": "Sigma x10"},
            "amount_x100": {"min": 0, "max": 300, "default": 120, "step": 1, "label": "Cantidad x100"}
        }
    },
    "sobel_x": {
        "nombre": "Sobel X",
        "descripcion": "Gradiente horizontal (resalta bordes verticales).",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "sobel_y": {
        "nombre": "Sobel Y",
        "descripcion": "Gradiente vertical (resalta bordes horizontales).",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    }
}

FILTROS_MORFOLOGICOS = {
    "erosion": {
        "nombre": "Erosión",
        "descripcion": "Reduce objetos. Elimina píxeles en bordes.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"},
            "iterations": {"min": 1, "max": 10, "default": 1, "step": 1, "label": "Iteraciones"}
        }
    },
    "dilatacion": {
        "nombre": "Dilatación",
        "descripcion": "Expande objetos. Añade píxeles en bordes.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"},
            "iterations": {"min": 1, "max": 10, "default": 1, "step": 1, "label": "Iteraciones"}
        }
    },
    "apertura": {
        "nombre": "Apertura",
        "descripcion": "Erosión + Dilatación. Elimina objetos pequeños.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "clausura": {
        "nombre": "Clausura",
        "descripcion": "Dilatación + Erosión. Cierra huecos pequeños.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "tophat": {
        "nombre": "White Top-Hat",
        "descripcion": "Resalta objetos brillantes sobre fondo oscuro.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 9, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "blackhat": {
        "nombre": "Black Top-Hat",
        "descripcion": "Resalta objetos oscuros sobre fondo brillante.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 9, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "gradiente": {
        "nombre": "Gradiente Morfológico",
        "descripcion": "Dilatación - Erosión. Detecta contornos.",
        "params": {
            "kernel_size": {"min": 3, "max": 21, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    }
}


def get_all_filters():
    """Retorna todos los filtros disponibles."""
    return {**FILTROS_ESPACIALES, **FILTROS_MORFOLOGICOS}


def get_filter_info(filter_name):
    """Obtiene la información de un filtro por su clave."""
    if filter_name in FILTROS_ESPACIALES:
        return FILTROS_ESPACIALES[filter_name]
    elif filter_name in FILTROS_MORFOLOGICOS:
        return FILTROS_MORFOLOGICOS[filter_name]
    return None

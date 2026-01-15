"""
Definiciones de filtros disponibles en FilterLab - VERSIÓN CORREGIDA COMPLETA.

CAMBIOS ESPACIALES:
- Añadido filtro "normalize_percentile" que SIEMPRE mejora el contraste
- Mejoradas las descripciones
- Añadida advertencia en "normalize"
- Step de 2 para kernels (solo impares son válidos)

CAMBIOS MORFOLÓGICOS:
- Kernel default reducido (3 en vez de 5, 5 en vez de 9)
- Rangos máximos reducidos (15 en vez de 21)
- Descripciones más claras
- Iterations max reducido a 5
"""

FILTROS_ESPACIALES = {
    # =========================================================================
    # SUAVIZADO
    # =========================================================================
    "gaussiano": {
        "nombre": "Gaussiano",
        "descripcion": "Suavizado gaussiano. Reduce ruido pero difumina bordes.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 5, "step": 1, "label": "Tamaño kernel"},
            "sigma": {"min": 0.1, "max": 10.0, "default": 1.0, "step": 0.1, "label": "Sigma"}
        }
    },
    "mediana": {
        "nombre": "Mediana",
        "descripcion": "Elimina ruido sal y pimienta preservando bordes.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 5, "step": 1, "label": "Tamaño kernel"}
        }
    },
    "bilateral": {
        "nombre": "Bilateral",
        "descripcion": "Suaviza preservando bordes. Combina proximidad y similitud de color.",
        "params": {
            "d": {"min": 1, "max": 25, "default": 9, "step": 1, "label": "Diámetro (d)"},
            "sigma_color": {"min": 1, "max": 200, "default": 75, "step": 1, "label": "Sigma Color"},
            "sigma_space": {"min": 1, "max": 200, "default": 75, "step": 1, "label": "Sigma Space"}
        }
    },
    
    # =========================================================================
    # MEJORA DE CONTRASTE
    # =========================================================================
    "clahe": {
        "nombre": "CLAHE",
        "descripcion": "Ecualización adaptativa. Mejora contraste local sin saturar.",
        "params": {
            "clip_limit": {"min": 1.0, "max": 10.0, "default": 2.0, "step": 0.5, "label": "Clip Limit"},
            "tile_size": {"min": 1, "max": 16, "default": 8, "step": 1, "label": "Tile Size"}
        }
    },
    "normalize": {
        "nombre": "Normalizar (Min-Max)",
        "descripcion": "⚠️ Estira rango a [0-255]. Sin efecto si ya usa rango completo.",
        "params": {}
    },
    "normalize_percentile": {
        "nombre": "Normalizar (Percentil)",
        "descripcion": "✅ SIEMPRE mejora contraste. Recorta extremos y estira.",
        "params": {
            "low_percentile": {"min": 0.0, "max": 10.0, "default": 1.0, "step": 0.5, "label": "Percentil bajo (%)"},
            "high_percentile": {"min": 90.0, "max": 100.0, "default": 99.0, "step": 0.5, "label": "Percentil alto (%)"}
        }
    },
    "log_transform": {
        "nombre": "Transformación Log",
        "descripcion": "Expande detalles en zonas oscuras. Para alto rango dinámico.",
        "params": {
            "gain": {"min": 1, "max": 255, "default": 255, "step": 1, "label": "Ganancia"}
        }
    },
    "gamma": {
        "nombre": "Corrección Gamma",
        "descripcion": "γ<1 aclara sombras, γ>1 las oscurece. γ=1 sin cambio.",
        "params": {
            "gamma": {"min": 0.1, "max": 3.0, "default": 0.8, "step": 0.05, "label": "Gamma (γ)"}
        }
    },
    "unsharp": {
        "nombre": "Unsharp Mask",
        "descripcion": "Aumenta nitidez restando versión difuminada.",
        "params": {
            "sigma": {"min": 0.1, "max": 5.0, "default": 1.0, "step": 0.1, "label": "Sigma"},
            "amount": {"min": 0.0, "max": 3.0, "default": 1.2, "step": 0.1, "label": "Amount"}
        }
    },
    
    # =========================================================================
    # DETECCIÓN DE BORDES
    # =========================================================================
    "canny": {
        "nombre": "Canny",
        "descripcion": "Detector de bordes con histéresis. Resultado binario.",
        "params": {
            "low_threshold": {"min": 0, "max": 255, "default": 50, "step": 1, "label": "Umbral bajo"},
            "high_threshold": {"min": 0, "max": 255, "default": 150, "step": 1, "label": "Umbral alto"}
        }
    },
    "otsu": {
        "nombre": "Otsu",
        "descripcion": "Binarización automática. Umbral óptimo para separar fondo/objeto.",
        "params": {}
    },
    "laplaciano": {
        "nombre": "Laplaciano",
        "descripcion": "Bordes por segunda derivada. Sensible al ruido.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 1, "label": "Tamaño kernel"}
        }
    },
    "sobel": {
        "nombre": "Sobel",
        "descripcion": "Magnitud del gradiente. Combina bordes H y V.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 1, "label": "Tamaño kernel"}
        }
    },
    "sobel_x": {
        "nombre": "Sobel X",
        "descripcion": "Gradiente horizontal. Resalta bordes verticales.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 1, "label": "Tamaño kernel"}
        }
    },
    "sobel_y": {
        "nombre": "Sobel Y",
        "descripcion": "Gradiente vertical. Resalta bordes horizontales.",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 1, "label": "Tamaño kernel"}
        }
    }
}

FILTROS_MORFOLOGICOS = {
    "erosion": {
        "nombre": "Erosión",
        "descripcion": "Reduce objetos eliminando píxeles en bordes.",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 3, "step": 1, "label": "Tamaño kernel"},
            "iterations": {"min": 1, "max": 5, "default": 1, "step": 1, "label": "Iteraciones"}
        }
    },
    "dilatacion": {
        "nombre": "Dilatación",
        "descripcion": "Expande objetos añadiendo píxeles en bordes.",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 3, "step": 1, "label": "Tamaño kernel"},
            "iterations": {"min": 1, "max": 5, "default": 1, "step": 1, "label": "Iteraciones"}
        }
    },
    "apertura": {
        "nombre": "Apertura",
        "descripcion": "Erosión + Dilatación. Elimina ruido pequeño.",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 3, "step": 1, "label": "Tamaño kernel"}
        }
    },
    "clausura": {
        "nombre": "Clausura",
        "descripcion": "Dilatación + Erosión. Cierra huecos pequeños.",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 3, "step": 1, "label": "Tamaño kernel"}
        }
    },
    "tophat": {
        "nombre": "White Top-Hat",
        "descripcion": "Extrae brillos menores que el kernel. Normalizado.",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 5, "step": 1, "label": "Tamaño kernel"}
        }
    },
    "blackhat": {
        "nombre": "Black Top-Hat",
        "descripcion": "Extrae oscuros menores que el kernel. Normalizado.",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 5, "step": 1, "label": "Tamaño kernel"}
        }
    },
    "gradiente": {
        "nombre": "Gradiente Morfológico",
        "descripcion": "Dilatación - Erosión. Detecta contornos. Normalizado.",
        "params": {
            "kernel_size": {"min": 1, "max": 11, "default": 3, "step": 1, "label": "Tamaño kernel"}
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

"""
Definiciones de filtros disponibles en FilterLab.
"""

FILTROS_ESPACIALES = {
    "gaussiano": {
        "nombre": "Gaussiano",
        "descripcion": "Suavizado con kernel gaussiano. Reduce ruido preservando bordes.",
        "categoria": "suavizado",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 5, "step": 2, "label": "Tamaño kernel"},
            "sigma": {"min": 0.1, "max": 10.0, "default": 1.0, "step": 0.1, "label": "Sigma"}
        }
    },
    "mediana": {
        "nombre": "Mediana",
        "descripcion": "Reemplaza cada píxel por la mediana de sus vecinos.",
        "categoria": "suavizado",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "bilateral": {
        "nombre": "Bilateral",
        "descripcion": "Suaviza preservando bordes.",
        "categoria": "suavizado",
        "params": {
            "d": {"min": 1, "max": 15, "default": 9, "step": 2, "label": "Diámetro"},
            "sigma_color": {"min": 1, "max": 200, "default": 75, "step": 5, "label": "Sigma Color"},
            "sigma_space": {"min": 1, "max": 200, "default": 75, "step": 5, "label": "Sigma Espacio"}
        }
    },
    "clahe": {
        "nombre": "CLAHE",
        "descripcion": "Ecualización adaptativa del histograma.",
        "categoria": "contraste",
        "params": {
            "clip_limit": {"min": 1.0, "max": 10.0, "default": 2.0, "step": 0.5, "label": "Clip Limit"},
            "tile_size": {"min": 1, "max": 16, "default": 8, "step": 1, "label": "Tile Size"}
        }
    },
    "normalize": {
        "nombre": "Normalizar (Min-Max)",
        "descripcion": "Estira rango a [0-255].",
        "categoria": "contraste",
        "params": {}
    },
    "normalize_percentile": {
        "nombre": "Normalizar (Percentil)",
        "descripcion": "SIEMPRE mejora contraste. Recorta extremos y estira.",
        "categoria": "contraste",
        "params": {
            "low_percentile": {"min": 0.0, "max": 10.0, "default": 1.0, "step": 0.5, "label": "Percentil bajo (%)"},
            "high_percentile": {"min": 90.0, "max": 100.0, "default": 99.0, "step": 0.5, "label": "Percentil alto (%)"}
        }
    },
    "gamma": {
        "nombre": "Corrección Gamma",
        "descripcion": "γ<1 aclara sombras, γ>1 las oscurece.",
        "categoria": "contraste",
        "params": {
            "gamma": {"min": 0.1, "max": 3.0, "default": 0.8, "step": 0.05, "label": "Gamma (γ)"}
        }
    },
    "log_transform": {
        "nombre": "Transformación Log",
        "descripcion": "Expande detalles en zonas oscuras.",
        "categoria": "contraste",
        "params": {
            "gain": {"min": 1, "max": 255, "default": 255, "step": 5, "label": "Ganancia"}
        }
    },
    "unsharp": {
        "nombre": "Unsharp Mask",
        "descripcion": "Aumenta nitidez.",
        "categoria": "contraste",
        "params": {
            "sigma": {"min": 0.1, "max": 5.0, "default": 1.0, "step": 0.1, "label": "Sigma"},
            "amount": {"min": 0.0, "max": 3.0, "default": 1.2, "step": 0.1, "label": "Amount"}
        }
    },
    "canny": {
        "nombre": "Canny",
        "descripcion": "Detector de bordes con histéresis.",
        "categoria": "bordes",
        "params": {
            "low_threshold": {"min": 0, "max": 255, "default": 50, "step": 5, "label": "Umbral bajo"},
            "high_threshold": {"min": 0, "max": 255, "default": 150, "step": 5, "label": "Umbral alto"}
        }
    },
    "laplaciano": {
        "nombre": "Laplaciano",
        "descripcion": "Bordes por segunda derivada.",
        "categoria": "bordes",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "sobel": {
        "nombre": "Sobel",
        "descripcion": "Magnitud del gradiente.",
        "categoria": "bordes",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "sobel_x": {
        "nombre": "Sobel X",
        "descripcion": "Gradiente horizontal.",
        "categoria": "bordes",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "sobel_y": {
        "nombre": "Sobel Y",
        "descripcion": "Gradiente vertical.",
        "categoria": "bordes",
        "params": {
            "kernel_size": {"min": 1, "max": 31, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "equalize_hist": {
        "nombre": "Ecualización Histograma",
        "descripcion": "Ecualización global. Mejora contraste distribuyendo intensidades.",
        "categoria": "contraste",
        "params": {}
    },
    "skeleton": {
        "nombre": "Esqueletización",
        "descripcion": "Reduce estructuras binarias a líneas de 1 píxel.",
        "categoria": "bordes",
        "params": {}
    },
    "hough_lines": {
        "nombre": "Detección de Líneas (Hough)",
        "descripcion": "Detecta carreteras y estructuras lineales.",
        "categoria": "bordes",
        "params": {
            "threshold": {"min": 10, "max": 200, "default": 50, "step": 10, "label": "Umbral votos"},
            "min_line_length": {"min": 10, "max": 200, "default": 50, "step": 10, "label": "Longitud mínima"},
            "max_line_gap": {"min": 1, "max": 50, "default": 10, "step": 5, "label": "Gap máximo"}
        }
    },
        "rotate": {
        "nombre": "🔄 Rotar Imagen",
        "descripcion": "Rota la imagen en grados.",
        "categoria": "transformacion",
        "params": {
            "angle": {"min": -180, "max": 180, "default": 0, "step": 1, "label": "Ángulo (grados)"}
        }
    },
    "crop": {
        "nombre": "✂️ Recortar Imagen",
        "descripcion": "Recorta píxeles de los bordes (útil para eliminar texto/escala).",
        "categoria": "transformacion",
        "params": {
            "top": {"min": 0, "max": 200, "default": 0, "step": 5, "label": "Recortar arriba (px)"},
            "bottom": {"min": 0, "max": 200, "default": 0, "step": 5, "label": "Recortar abajo (px)"},
            "left": {"min": 0, "max": 200, "default": 0, "step": 5, "label": "Recortar izquierda (px)"},
            "right": {"min": 0, "max": 200, "default": 0, "step": 5, "label": "Recortar derecha (px)"}
        }
    },
}

FILTROS_MORFOLOGICOS = {
    "erosion": {
        "nombre": "Erosión",
        "descripcion": "Reduce objetos eliminando píxeles en bordes.",
        "categoria": "morfologico",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 3, "step": 2, "label": "Tamaño kernel"},
            "iterations": {"min": 1, "max": 5, "default": 1, "step": 1, "label": "Iteraciones"}
        }
    },
    "dilatacion": {
        "nombre": "Dilatación",
        "descripcion": "Expande objetos añadiendo píxeles en bordes.",
        "categoria": "morfologico",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 3, "step": 2, "label": "Tamaño kernel"},
            "iterations": {"min": 1, "max": 5, "default": 1, "step": 1, "label": "Iteraciones"}
        }
    },
    "apertura": {
        "nombre": "Apertura",
        "descripcion": "Erosión + Dilatación. Elimina ruido pequeño.",
        "categoria": "morfologico",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "clausura": {
        "nombre": "Clausura",
        "descripcion": "Dilatación + Erosión. Cierra huecos pequeños.",
        "categoria": "morfologico",
        "params": {
            "kernel_size": {"min": 1, "max": 15, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "tophat": {
        "nombre": "White Top-Hat",
        "descripcion": "Extrae objetos brillantes menores que el kernel.",
        "categoria": "morfologico",
        "params": {
            "kernel_size": {"min": 3, "max": 15, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "blackhat": {
        "nombre": "Black Top-Hat",
        "descripcion": "Extrae objetos oscuros menores que el kernel.",
        "categoria": "morfologico",
        "params": {
            "kernel_size": {"min": 3, "max": 15, "default": 5, "step": 2, "label": "Tamaño kernel"}
        }
    },
    "gradiente": {
        "nombre": "Gradiente Morfológico",
        "descripcion": "Dilatación - Erosión. Detecta contornos.",
        "categoria": "morfologico",
        "params": {
            "kernel_size": {"min": 1, "max": 11, "default": 3, "step": 2, "label": "Tamaño kernel"}
        }
    }
}

FILTROS_SEGMENTACION = {
    "umbral_manual": {
        "nombre": "Umbral Manual",
        "descripcion": "Binarización con umbral fijo.",
        "categoria": "segmentacion",
        "params": {
            "threshold": {"min": 0, "max": 255, "default": 127, "step": 1, "label": "Umbral"},
            "invert": {"default": False, "label": "Invertir"}
        }
    },
    "otsu": {
        "nombre": "Otsu (Global)",
        "descripcion": "Binarización automática.",
        "categoria": "segmentacion",
        "params": {
            "invert": {"default": False, "label": "Invertir"}
        }
    },
    "otsu_adaptativo": {
        "nombre": "Otsu Adaptativo",
        "descripcion": "Umbral local por bloques. Ideal para iluminación no uniforme.",
        "categoria": "segmentacion",
        "params": {
            "block_size": {"min": 3, "max": 99, "default": 35, "step": 2, "label": "Tamaño bloque"},
            "c": {"min": -20, "max": 20, "default": 5, "step": 1, "label": "Constante C"},
            "invert": {"default": False, "label": "Invertir"}
        }
    },
    "umbral_adaptativo_media": {
        "nombre": "Umbral Adaptativo (Media)",
        "descripcion": "Umbral local basado en media de vecinos.",
        "categoria": "segmentacion",
        "params": {
            "block_size": {"min": 3, "max": 99, "default": 35, "step": 2, "label": "Tamaño bloque"},
            "c": {"min": -20, "max": 20, "default": 5, "step": 1, "label": "Constante C"},
            "invert": {"default": False, "label": "Invertir"}
        }
    },
    "segmentacion_hsv": {
        "nombre": "Segmentación HSV (Manual)",
        "descripcion": "Segmenta por rangos de color en espacio HSV.",
        "categoria": "segmentacion_color",
        "params": {
            "h_min": {"min": 0, "max": 179, "default": 35, "step": 1, "label": "H mínimo"},
            "h_max": {"min": 0, "max": 179, "default": 85, "step": 1, "label": "H máximo"},
            "s_min": {"min": 0, "max": 255, "default": 40, "step": 5, "label": "S mínimo"},
            "s_max": {"min": 0, "max": 255, "default": 255, "step": 5, "label": "S máximo"},
            "v_min": {"min": 0, "max": 255, "default": 40, "step": 5, "label": "V mínimo"},
            "v_max": {"min": 0, "max": 255, "default": 255, "step": 5, "label": "V máximo"},
            "invert": {"default": False, "label": "Invertir"}
        }
    },
    "segmentacion_hsv_verde": {
        "nombre": "🌿 HSV Verde (Vegetación)",
        "descripcion": "Preset para detectar vegetación/zonas verdes.",
        "categoria": "segmentacion_color",
        "params": {
            "tolerancia": {"min": 5, "max": 50, "default": 25, "step": 5, "label": "Tolerancia H"},
            "saturacion_min": {"min": 0, "max": 100, "default": 30, "step": 5, "label": "Saturación mín"},
            "brillo_min": {"min": 0, "max": 100, "default": 30, "step": 5, "label": "Brillo mín"},
            "invert": {"default": False, "label": "Invertir (mostrar NO verde)"}
        }
    },
    "segmentacion_hsv_marron": {
        "nombre": "🏜️ HSV Marrón (Suelo)",
        "descripcion": "Preset para detectar suelo/tierra/deforestación.",
        "categoria": "segmentacion_color",
        "params": {
            "tolerancia": {"min": 5, "max": 30, "default": 15, "step": 5, "label": "Tolerancia H"},
            "saturacion_min": {"min": 0, "max": 100, "default": 20, "step": 5, "label": "Saturación mín"},
            "brillo_min": {"min": 0, "max": 100, "default": 40, "step": 5, "label": "Brillo mín"},
            "invert": {"default": False, "label": "Invertir"}
        }
    },
    "segmentacion_lab": {
        "nombre": "Segmentación Lab (Manual)",
        "descripcion": "Segmenta por rangos en espacio CIE Lab.",
        "categoria": "segmentacion_color",
        "params": {
            "l_min": {"min": 0, "max": 255, "default": 0, "step": 5, "label": "L mínimo"},
            "l_max": {"min": 0, "max": 255, "default": 255, "step": 5, "label": "L máximo"},
            "a_min": {"min": 0, "max": 255, "default": 0, "step": 5, "label": "a mínimo"},
            "a_max": {"min": 0, "max": 255, "default": 128, "step": 5, "label": "a máximo"},
            "b_min": {"min": 0, "max": 255, "default": 0, "step": 5, "label": "b mínimo"},
            "b_max": {"min": 0, "max": 255, "default": 255, "step": 5, "label": "b máximo"},
            "invert": {"default": False, "label": "Invertir"}
        }
    },
    "segmentacion_lab_vegetacion": {
        "nombre": "🌿 Lab Vegetación",
        "descripcion": "Detecta vegetación usando canal 'a' (verde-rojo).",
        "categoria": "segmentacion_color",
        "params": {
            "sensibilidad": {"min": 100, "max": 140, "default": 120, "step": 2, "label": "Umbral 'a'"},
            "luminosidad_min": {"min": 0, "max": 100, "default": 20, "step": 5, "label": "Luminosidad mín"},
            "invert": {"default": False, "label": "Invertir (mostrar NO vegetación)"}
        }
    },
    "segmentacion_lab_suelo": {
        "nombre": "🏜️ Lab Suelo",
        "descripcion": "Detecta suelo expuesto usando canales 'a' y 'b'.",
        "categoria": "segmentacion_color",
        "params": {
            "a_min": {"min": 100, "max": 150, "default": 128, "step": 2, "label": "a mínimo (rojo)"},
            "b_min": {"min": 100, "max": 150, "default": 128, "step": 2, "label": "b mínimo (amarillo)"},
            "luminosidad_min": {"min": 0, "max": 100, "default": 30, "step": 5, "label": "Luminosidad mín"},
            "invert": {"default": False, "label": "Invertir"}
        }
    },
    "convertir_hsv": {
        "nombre": "Ver Canal HSV",
        "descripcion": "Visualiza canales H, S o V individualmente.",
        "categoria": "visualizacion",
        "params": {
            "canal": {"options": ["H", "S", "V", "Todos"], "default": "H", "label": "Canal"}
        }
    },
    "convertir_lab": {
        "nombre": "Ver Canal Lab",
        "descripcion": "Visualiza canales L, a o b individualmente.",
        "categoria": "visualizacion",
        "params": {
            "canal": {"options": ["L", "a", "b", "Todos"], "default": "a", "label": "Canal"}
        }
    },
    "cloud_detection": {
        "nombre": "☁️ Detección de Nubes",
        "descripcion": "Detecta nubes usando HSV+LAB. Ideal para preprocesar imágenes satelitales.",
        "categoria": "segmentacion_color",
        "params": {
            "v_threshold": {"min": 150, "max": 255, "default": 200, "step": 5, "label": "Umbral V (brillo)"},
            "s_threshold": {"min": 10, "max": 100, "default": 50, "step": 5, "label": "Umbral S máx"},
            "l_threshold": {"min": 150, "max": 255, "default": 200, "step": 5, "label": "Umbral L (luminosidad)"},
            "invert": {"default": False, "label": "Invertir (mostrar NO nubes)"}
        }
    },
    "overlay_mask": {
        "nombre": "🎭 Superponer Máscara",
        "descripcion": "Superpone la imagen binaria actual sobre la original con color.",
        "categoria": "visualizacion",
        "params": {
            "alpha": {"min": 0.1, "max": 1.0, "default": 0.5, "step": 0.1, "label": "Opacidad"},
            "color_r": {"min": 0, "max": 255, "default": 255, "step": 10, "label": "Rojo"},
            "color_g": {"min": 0, "max": 255, "default": 0, "step": 10, "label": "Verde"},
            "color_b": {"min": 0, "max": 255, "default": 0, "step": 10, "label": "Azul"}
        }
    },

}


def get_all_filters():
    return {**FILTROS_ESPACIALES, **FILTROS_MORFOLOGICOS, **FILTROS_SEGMENTACION}


def get_filter_info(filter_name):
    all_filters = get_all_filters()
    return all_filters.get(filter_name)


def get_filters_by_category(categoria):
    all_filters = get_all_filters()
    return {nombre: info for nombre, info in all_filters.items() if info.get("categoria") == categoria}


def get_categories():
    all_filters = get_all_filters()
    categorias = set()
    for info in all_filters.values():
        if "categoria" in info:
            categorias.add(info["categoria"])
    return sorted(categorias)


CATEGORIAS = {
    "suavizado": {"nombre": "🔵 Suavizado", "descripcion": "Reducción de ruido"},
    "contraste": {"nombre": "☀️ Contraste", "descripcion": "Mejora de intensidad"},
    "bordes": {"nombre": "📐 Bordes", "descripcion": "Detección de contornos"},
    "morfologico": {"nombre": "🔷 Morfológicos", "descripcion": "Operaciones de forma"},
    "segmentacion": {"nombre": "✂️ Segmentación", "descripcion": "Binarización y umbralización"},
    "segmentacion_color": {"nombre": "🎨 Seg. por Color", "descripcion": "HSV y Lab"},
    "visualizacion": {"nombre": "👁️ Visualización", "descripcion": "Ver espacios de color"},
    "transformacion": {"nombre": "🔧 Transformación", "descripcion": "Recorte y rotación"},
}

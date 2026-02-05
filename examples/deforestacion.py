"""
Ejemplo completo: Análisis de Deforestación en el Bosque Jamanxim

Este script demuestra cómo usar la expansión de FilterLab para:
1. Cargar las 20 imágenes del GIF
2. Aplicar un pipeline de segmentación
3. Calcular áreas deforestadas por año
4. Generar análisis temporal y exportar resultados

Uso:
    python deforestacion.py ruta/al/gif_o_carpeta [--metodo hsv|lab|otsu]
"""

import sys
import os
import argparse
from pathlib import Path

# Añadir el directorio padre al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import cv2
import numpy as np
import matplotlib.pyplot as plt

# Imports de la expansión FilterLab
from filters.segmentation import (
    apply_gaussiano,
    apply_clahe,
    apply_otsu_adaptativo,
    apply_segmentacion_hsv_verde,
    apply_segmentacion_lab_vegetacion,
    apply_clausura,
    apply_apertura,
    SEGMENTATION_FILTERS
)
from core.analysis import AnalisisArea, AnalisisTemporal, calcular_area_rapido
from core.batch import CargadorImagenes, PipelineFiltros, ProcesadorBatch


# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Escala del caso Jamanxim: 51 píxeles = 20 km
PIXELS_ESCALA = 51
KM_ESCALA = 20

# Parámetros de segmentación por método
PARAMS_HSV = {
    "preprocesamiento": [
        ("gaussiano", {"kernel_size": 5, "sigma": 1.0}),
        ("clahe", {"clip_limit": 2.0, "tile_size": 8}),
    ],
    "segmentacion": ("segmentacion_hsv_verde", {
        "tolerancia": 25,
        "saturacion_min": 30,
        "brillo_min": 30,
        "invert": True  # Invertir para detectar NO-verde (deforestado)
    }),
    "postprocesamiento": [
        ("clausura", {"kernel_size": 5}),
        ("apertura", {"kernel_size": 3}),
    ]
}

PARAMS_LAB = {
    "preprocesamiento": [
        ("gaussiano", {"kernel_size": 5, "sigma": 1.0}),
        ("clahe", {"clip_limit": 2.0, "tile_size": 8}),
    ],
    "segmentacion": ("segmentacion_lab_vegetacion", {
        "sensibilidad": 120,
        "luminosidad_min": 20,
        "invert": True  # Invertir para detectar NO-vegetación
    }),
    "postprocesamiento": [
        ("clausura", {"kernel_size": 5}),
        ("apertura", {"kernel_size": 3}),
    ]
}

PARAMS_OTSU = {
    "preprocesamiento": [
        ("gaussiano", {"kernel_size": 5, "sigma": 1.0}),
        ("clahe", {"clip_limit": 3.0, "tile_size": 8}),
    ],
    "segmentacion": ("otsu_adaptativo", {
        "block_size": 35,
        "c": 5,
        "invert": False
    }),
    "postprocesamiento": [
        ("clausura", {"kernel_size": 3}),
        ("apertura", {"kernel_size": 3}),
    ]
}


# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def aplicar_filtro(img, nombre_filtro, params):
    """Aplica un filtro individual a una imagen."""
    # Importar dinámicamente la función del filtro
    if nombre_filtro == "gaussiano":
        from filters.segmentation import apply_gaussiano as func
        func = lambda i, g, p: cv2.GaussianBlur(i, (p.get("kernel_size", 5), p.get("kernel_size", 5)), p.get("sigma", 1.0))
    elif nombre_filtro == "clahe":
        def func(img, gray, params):
            clip = params.get("clip_limit", 2.0)
            tile = params.get("tile_size", 8)
            clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
            if len(img.shape) == 3:
                lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
                lab[:,:,0] = clahe.apply(lab[:,:,0])
                return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            return clahe.apply(gray)
        func = func
    elif nombre_filtro == "clausura":
        def func(img, gray, params):
            k = params.get("kernel_size", 3)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            result = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            return cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
        func = func
    elif nombre_filtro == "apertura":
        def func(img, gray, params):
            k = params.get("kernel_size", 3)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k, k))
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            result = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            return cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
        func = func
    elif nombre_filtro in SEGMENTATION_FILTERS:
        func = SEGMENTATION_FILTERS[nombre_filtro]
    else:
        raise ValueError(f"Filtro desconocido: {nombre_filtro}")
    
    # Calcular versión gris
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray = img
    
    return func(img, gray, params)


def procesar_imagen(img, config):
    """Aplica el pipeline completo a una imagen."""
    resultado = img.copy()
    
    # Preprocesamiento
    for nombre, params in config["preprocesamiento"]:
        resultado = aplicar_filtro(resultado, nombre, params)
    
    # Segmentación
    nombre_seg, params_seg = config["segmentacion"]
    resultado = aplicar_filtro(resultado, nombre_seg, params_seg)
    
    # Postprocesamiento
    for nombre, params in config["postprocesamiento"]:
        resultado = aplicar_filtro(resultado, nombre, params)
    
    return resultado


def extraer_año_de_nombre(nombre):
    """Intenta extraer el año del nombre del frame."""
    import re
    
    # Buscar número de 4 dígitos que parezca año
    match = re.search(r'(\d{4})', nombre)
    if match:
        año = int(match.group(1))
        if 1990 <= año <= 2030:
            return año
    
    # Si no hay año, intentar extraer número de frame
    match = re.search(r'frame_(\d+)', nombre)
    if match:
        frame = int(match.group(1))
        # Asumir que empezamos en 2000 si hay 20 frames
        return 2000 + frame
    
    return None


def generar_grafico(serie_temporal, titulo, ruta_salida):
    """Genera un gráfico de la evolución temporal."""
    años = sorted(serie_temporal.keys())
    areas = [serie_temporal[año] for año in años]
    
    plt.figure(figsize=(12, 6))
    
    # Gráfico de línea
    plt.subplot(1, 2, 1)
    plt.plot(años, areas, 'b-o', linewidth=2, markersize=8)
    plt.xlabel('Año')
    plt.ylabel('Área deforestada (km²)')
    plt.title(f'{titulo}\nEvolución del área deforestada')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    # Gráfico de barras
    plt.subplot(1, 2, 2)
    colores = plt.cm.Reds(np.linspace(0.3, 0.9, len(años)))
    plt.bar(años, areas, color=colores)
    plt.xlabel('Año')
    plt.ylabel('Área deforestada (km²)')
    plt.title('Comparación por año')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Gráfico guardado en: {ruta_salida}")


def generar_mosaico_comparacion(imagenes_originales, imagenes_procesadas, nombres, ruta_salida, cols=5):
    """Genera un mosaico comparando originales vs procesadas."""
    n = len(imagenes_originales)
    rows = (n + cols - 1) // cols
    
    # Tamaño de cada imagen
    h, w = imagenes_originales[0].shape[:2]
    
    # Crear figura
    fig, axes = plt.subplots(rows * 2, cols, figsize=(cols * 3, rows * 6))
    
    for i in range(n):
        row = (i // cols) * 2
        col = i % cols
        
        # Original
        if rows * 2 > 1:
            ax_orig = axes[row, col]
            ax_proc = axes[row + 1, col]
        else:
            ax_orig = axes[col]
            ax_proc = axes[col]
        
        ax_orig.imshow(imagenes_originales[i])
        ax_orig.set_title(f'{nombres[i]}', fontsize=8)
        ax_orig.axis('off')
        
        # Procesada
        if len(imagenes_procesadas[i].shape) == 2:
            ax_proc.imshow(imagenes_procesadas[i], cmap='gray')
        else:
            ax_proc.imshow(imagenes_procesadas[i])
        ax_proc.axis('off')
    
    # Ocultar ejes vacíos
    for i in range(n, rows * cols):
        row = (i // cols) * 2
        col = i % cols
        if rows * 2 > 1:
            axes[row, col].axis('off')
            axes[row + 1, col].axis('off')
    
    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Mosaico guardado en: {ruta_salida}")


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Análisis de deforestación en imágenes satelitales'
    )
    parser.add_argument(
        'entrada',
        help='Ruta al GIF o carpeta con imágenes'
    )
    parser.add_argument(
        '--metodo', '-m',
        choices=['hsv', 'lab', 'otsu'],
        default='hsv',
        help='Método de segmentación (default: hsv)'
    )
    parser.add_argument(
        '--salida', '-o',
        default='resultados_deforestacion',
        help='Carpeta de salida (default: resultados_deforestacion)'
    )
    parser.add_argument(
        '--escala-pixels',
        type=float,
        default=PIXELS_ESCALA,
        help=f'Píxeles en la escala (default: {PIXELS_ESCALA})'
    )
    parser.add_argument(
        '--escala-km',
        type=float,
        default=KM_ESCALA,
        help=f'Kilómetros en la escala (default: {KM_ESCALA})'
    )
    
    args = parser.parse_args()
    
    # Seleccionar configuración según método
    if args.metodo == 'hsv':
        config = PARAMS_HSV
        metodo_nombre = "HSV Verde (invertido)"
    elif args.metodo == 'lab':
        config = PARAMS_LAB
        metodo_nombre = "Lab Vegetación (invertido)"
    else:
        config = PARAMS_OTSU
        metodo_nombre = "Otsu Adaptativo"
    
    print("=" * 60)
    print("ANÁLISIS DE DEFORESTACIÓN - BOSQUE JAMANXIM")
    print("=" * 60)
    print(f"\nMétodo de segmentación: {metodo_nombre}")
    print(f"Escala: {args.escala_pixels} px = {args.escala_km} km")
    
    # Crear carpeta de salida
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    
    # Cargar imágenes
    entrada = Path(args.entrada)
    print(f"\nCargando imágenes desde: {entrada}")
    
    if entrada.suffix.lower() == '.gif':
        imagenes = CargadorImagenes.desde_gif(entrada)
    elif entrada.is_dir():
        imagenes = CargadorImagenes.desde_carpeta(entrada)
    else:
        imagenes = CargadorImagenes.desde_lista_rutas([entrada])
    
    print(f"Imágenes cargadas: {len(imagenes)}")
    
    # Crear analizador de área
    analizador = AnalisisArea.desde_escala(args.escala_pixels, args.escala_km)
    temporal = AnalisisTemporal(analizador)
    
    # Procesar cada imagen
    print("\nProcesando imágenes...")
    imagenes_originales = []
    imagenes_procesadas = []
    nombres = []
    
    for i, (nombre, img) in enumerate(imagenes):
        print(f"  [{i+1}/{len(imagenes)}] {nombre}...", end=" ")
        
        # Procesar
        procesada = procesar_imagen(img, config)
        
        # Extraer año
        año = extraer_año_de_nombre(nombre)
        if año is None:
            año = 2000 + i  # Asumir secuencia desde 2000
        
        # Calcular área
        resultado = temporal.agregar_imagen(str(año), procesada, contar_blancos=True)
        
        print(f"Año {año}: {resultado.area_km2:.2f} km² ({resultado.porcentaje_blanco:.1f}%)")
        
        # Guardar para visualización
        imagenes_originales.append(img)
        imagenes_procesadas.append(procesada)
        nombres.append(str(año))
        
        # Guardar imagen procesada
        ruta_img = salida / f"{año}_segmentada.png"
        if len(procesada.shape) == 3:
            cv2.imwrite(str(ruta_img), cv2.cvtColor(procesada, cv2.COLOR_RGB2BGR))
        else:
            cv2.imwrite(str(ruta_img), procesada)
    
    # Generar resumen
    print("\n" + "=" * 60)
    print("RESULTADOS")
    print("=" * 60)
    
    resumen = temporal.resumen()
    serie = temporal.obtener_serie_temporal()
    
    print(f"\nImágenes analizadas: {resumen['n_imagenes']}")
    print(f"Período: {min(resumen['nombres'])} - {max(resumen['nombres'])}")
    
    stats = resumen['estadisticas']
    print(f"\nEstadísticas de área deforestada:")
    print(f"  Mínima: {stats['area_minima_km2']:.2f} km²")
    print(f"  Máxima: {stats['area_maxima_km2']:.2f} km²")
    print(f"  Media:  {stats['area_media_km2']:.2f} km²")
    print(f"  Cambio total: {stats['area_total_cambio_km2']:.2f} km²")
    
    # Calcular cambio entre primer y último año
    años_ordenados = sorted(serie.keys())
    if len(años_ordenados) >= 2:
        cambio = temporal.calcular_cambio(años_ordenados[0], años_ordenados[-1])
        print(f"\nCambio {años_ordenados[0]} → {años_ordenados[-1]}:")
        print(f"  Absoluto: +{cambio['cambio_absoluto_km2']:.2f} km²")
        print(f"  Relativo: +{cambio['cambio_porcentual']:.1f}%")
        
        n_años = int(años_ordenados[-1]) - int(años_ordenados[0])
        if n_años > 0:
            tasa_anual = cambio['cambio_absoluto_km2'] / n_años
            print(f"  Tasa anual media: +{tasa_anual:.2f} km²/año")
    
    # Exportar datos
    print(f"\nExportando resultados...")
    temporal.exportar_csv(salida / "resultados.csv")
    temporal.exportar_json(salida / "resultados.json")
    print(f"  CSV: {salida / 'resultados.csv'}")
    print(f"  JSON: {salida / 'resultados.json'}")
    
    # Generar gráficos
    print(f"\nGenerando visualizaciones...")
    generar_grafico(
        {int(k): v for k, v in serie.items()},
        f"Deforestación Bosque Jamanxim\nMétodo: {metodo_nombre}",
        salida / "evolucion_temporal.png"
    )
    
    generar_mosaico_comparacion(
        imagenes_originales,
        imagenes_procesadas,
        nombres,
        salida / "comparacion_mosaico.png",
        cols=5
    )
    
    print(f"\n✅ Análisis completado. Resultados en: {salida}/")
    print("=" * 60)


if __name__ == "__main__":
    main()

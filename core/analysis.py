"""
Módulo de análisis para FilterLab.

Incluye:
- Cálculo de área en píxeles y unidades reales (km², m², ha)
- Estadísticas de imagen binaria
- Análisis temporal (comparación entre imágenes)
- Exportación de resultados
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import json


@dataclass
class AreaResult:
    """Resultado del cálculo de área."""
    pixels_blancos: int
    pixels_negros: int
    pixels_totales: int
    porcentaje_blanco: float
    porcentaje_negro: float
    area_km2: Optional[float] = None
    area_m2: Optional[float] = None
    area_ha: Optional[float] = None
    escala_info: Optional[str] = None


@dataclass
class ImageStats:
    """Estadísticas de una imagen."""
    media: float
    desviacion: float
    minimo: int
    maximo: int
    mediana: float
    histograma: np.ndarray


class AnalisisArea:
    """
    Calculadora de área para imágenes segmentadas.
    
    Convierte píxeles a unidades reales usando una escala definida.
    """
    
    def __init__(self, pixels_por_km: float = 2.55):
        """
        Inicializa el analizador.
        
        Args:
            pixels_por_km: Número de píxeles que equivalen a 1 km.
                          Por defecto: 51 px = 20 km -> 2.55 px/km
                          (escala del caso Jamanxim)
        """
        self.pixels_por_km = pixels_por_km
        self.km_por_pixel = 1.0 / pixels_por_km
        self.m_por_pixel = self.km_por_pixel * 1000
    
    @classmethod
    def desde_escala(cls, pixels: float, km: float) -> 'AnalisisArea':
        """
        Crea un analizador a partir de una escala conocida.
        
        Args:
            pixels: Número de píxeles en la escala
            km: Número de kilómetros que representan esos píxeles
        
        Ejemplo:
            # 51 píxeles = 20 km (caso Jamanxim)
            analizador = AnalisisArea.desde_escala(51, 20)
        """
        pixels_por_km = pixels / km
        return cls(pixels_por_km=pixels_por_km)
    
    def calcular_area(self, img_binaria: np.ndarray, 
                      contar_blancos: bool = True) -> AreaResult:
        """
        Calcula el área de una imagen binaria.
        
        Args:
            img_binaria: Imagen binaria (blanco/negro) o en escala de grises
            contar_blancos: Si True, cuenta píxeles blancos (255).
                           Si False, cuenta píxeles negros (0).
        
        Returns:
            AreaResult con todas las métricas calculadas.
        """
        # Convertir a escala de grises si es necesario
        if len(img_binaria.shape) == 3:
            gray = cv2.cvtColor(img_binaria, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_binaria
        
        # Binarizar si no es estrictamente binaria
        _, binaria = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Contar píxeles
        pixels_blancos = np.count_nonzero(binaria == 255)
        pixels_totales = binaria.size
        pixels_negros = pixels_totales - pixels_blancos
        
        # Porcentajes
        porcentaje_blanco = (pixels_blancos / pixels_totales) * 100
        porcentaje_negro = (pixels_negros / pixels_totales) * 100
        
        # Área en unidades reales
        pixels_a_medir = pixels_blancos if contar_blancos else pixels_negros
        
        # Área de un píxel en km²
        area_pixel_km2 = self.km_por_pixel ** 2
        area_km2 = pixels_a_medir * area_pixel_km2
        
        # Conversiones
        area_m2 = area_km2 * 1_000_000
        area_ha = area_km2 * 100  # 1 km² = 100 ha
        
        return AreaResult(
            pixels_blancos=pixels_blancos,
            pixels_negros=pixels_negros,
            pixels_totales=pixels_totales,
            porcentaje_blanco=porcentaje_blanco,
            porcentaje_negro=porcentaje_negro,
            area_km2=area_km2,
            area_m2=area_m2,
            area_ha=area_ha,
            escala_info=f"{self.pixels_por_km:.2f} px/km"
        )
    
    def calcular_estadisticas(self, img: np.ndarray) -> ImageStats:
        """
        Calcula estadísticas básicas de una imagen.
        
        Args:
            img: Imagen en cualquier formato
        
        Returns:
            ImageStats con todas las métricas.
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        
        histograma = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
        
        return ImageStats(
            media=float(np.mean(gray)),
            desviacion=float(np.std(gray)),
            minimo=int(np.min(gray)),
            maximo=int(np.max(gray)),
            mediana=float(np.median(gray)),
            histograma=histograma
        )


class AnalisisTemporal:
    """
    Análisis de series temporales de imágenes.
    
    Permite comparar la evolución de áreas segmentadas a lo largo del tiempo.
    """
    
    def __init__(self, analizador: AnalisisArea):
        """
        Inicializa el análisis temporal.
        
        Args:
            analizador: Instancia de AnalisisArea para cálculos
        """
        self.analizador = analizador
        self.resultados: Dict[str, AreaResult] = {}
    
    def agregar_imagen(self, nombre: str, img_binaria: np.ndarray,
                       contar_blancos: bool = True) -> AreaResult:
        """
        Agrega una imagen al análisis temporal.
        
        Args:
            nombre: Identificador (típicamente el año o fecha)
            img_binaria: Imagen binaria segmentada
            contar_blancos: Si True, cuenta píxeles blancos
        
        Returns:
            AreaResult para esta imagen
        """
        resultado = self.analizador.calcular_area(img_binaria, contar_blancos)
        self.resultados[nombre] = resultado
        return resultado
    
    def obtener_serie_temporal(self) -> Dict[str, float]:
        """
        Obtiene la serie temporal de áreas en km².
        
        Returns:
            Diccionario {nombre: area_km2}
        """
        return {
            nombre: resultado.area_km2 
            for nombre, resultado in self.resultados.items()
        }
    
    def calcular_cambio(self, nombre_inicial: str, 
                        nombre_final: str) -> Dict[str, float]:
        """
        Calcula el cambio entre dos momentos.
        
        Args:
            nombre_inicial: Identificador del momento inicial
            nombre_final: Identificador del momento final
        
        Returns:
            Diccionario con métricas de cambio
        """
        if nombre_inicial not in self.resultados:
            raise ValueError(f"No se encontró '{nombre_inicial}' en los resultados")
        if nombre_final not in self.resultados:
            raise ValueError(f"No se encontró '{nombre_final}' en los resultados")
        
        inicial = self.resultados[nombre_inicial]
        final = self.resultados[nombre_final]
        
        cambio_km2 = final.area_km2 - inicial.area_km2
        cambio_porcentual = ((final.area_km2 - inicial.area_km2) / inicial.area_km2) * 100 if inicial.area_km2 > 0 else 0
        
        return {
            "area_inicial_km2": inicial.area_km2,
            "area_final_km2": final.area_km2,
            "cambio_absoluto_km2": cambio_km2,
            "cambio_porcentual": cambio_porcentual,
            "tasa_anual_km2": None  # Se puede calcular si se conoce el período
        }
    
    def resumen(self) -> Dict:
        """
        Genera un resumen completo del análisis temporal.
        
        Returns:
            Diccionario con todas las métricas y la serie temporal
        """
        if not self.resultados:
            return {"error": "No hay resultados disponibles"}
        
        areas = [r.area_km2 for r in self.resultados.values()]
        nombres = list(self.resultados.keys())
        
        return {
            "n_imagenes": len(self.resultados),
            "nombres": nombres,
            "serie_temporal": self.obtener_serie_temporal(),
            "estadisticas": {
                "area_minima_km2": min(areas),
                "area_maxima_km2": max(areas),
                "area_media_km2": np.mean(areas),
                "area_total_cambio_km2": max(areas) - min(areas),
                "desviacion_km2": np.std(areas)
            },
            "escala": self.analizador.pixels_por_km
        }
    
    def exportar_csv(self, filepath: str) -> None:
        """
        Exporta los resultados a un archivo CSV.
        
        Args:
            filepath: Ruta del archivo de salida
        """
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Nombre', 'Pixels_Blancos', 'Pixels_Negros', 'Pixels_Totales',
                'Porcentaje_Blanco', 'Porcentaje_Negro', 
                'Area_km2', 'Area_ha', 'Area_m2'
            ])
            
            for nombre, resultado in self.resultados.items():
                writer.writerow([
                    nombre,
                    resultado.pixels_blancos,
                    resultado.pixels_negros,
                    resultado.pixels_totales,
                    f"{resultado.porcentaje_blanco:.2f}",
                    f"{resultado.porcentaje_negro:.2f}",
                    f"{resultado.area_km2:.4f}",
                    f"{resultado.area_ha:.4f}",
                    f"{resultado.area_m2:.2f}"
                ])
    
    def exportar_json(self, filepath: str) -> None:
        """
        Exporta los resultados a un archivo JSON.
        
        Args:
            filepath: Ruta del archivo de salida
        """
        data = {
            "configuracion": {
                "pixels_por_km": self.analizador.pixels_por_km,
                "km_por_pixel": self.analizador.km_por_pixel
            },
            "resultados": {
                nombre: {
                    "pixels_blancos": r.pixels_blancos,
                    "pixels_negros": r.pixels_negros,
                    "pixels_totales": r.pixels_totales,
                    "porcentaje_blanco": r.porcentaje_blanco,
                    "porcentaje_negro": r.porcentaje_negro,
                    "area_km2": r.area_km2,
                    "area_ha": r.area_ha,
                    "area_m2": r.area_m2
                }
                for nombre, r in self.resultados.items()
            },
            "resumen": self.resumen()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# =============================================================================
# FUNCIONES DE UTILIDAD
# =============================================================================

def calcular_area_rapido(img_binaria: np.ndarray, 
                         pixels_escala: float = 51, 
                         km_escala: float = 20,
                         contar_blancos: bool = True) -> Dict[str, float]:
    """
    Función rápida para calcular área sin crear instancias.
    
    Args:
        img_binaria: Imagen binaria segmentada
        pixels_escala: Píxeles en la escala de referencia
        km_escala: Kilómetros en la escala de referencia
        contar_blancos: Si True, cuenta área blanca
    
    Returns:
        Diccionario con área en diferentes unidades
    """
    analizador = AnalisisArea.desde_escala(pixels_escala, km_escala)
    resultado = analizador.calcular_area(img_binaria, contar_blancos)
    
    return {
        "pixels": resultado.pixels_blancos if contar_blancos else resultado.pixels_negros,
        "porcentaje": resultado.porcentaje_blanco if contar_blancos else resultado.porcentaje_negro,
        "km2": resultado.area_km2,
        "ha": resultado.area_ha,
        "m2": resultado.area_m2
    }


def comparar_imagenes(img1: np.ndarray, img2: np.ndarray) -> Dict[str, float]:
    """
    Compara dos imágenes binarias y calcula métricas de cambio.
    
    Args:
        img1: Primera imagen (antes)
        img2: Segunda imagen (después)
    
    Returns:
        Diccionario con métricas de comparación
    """
    # Asegurar que son binarias y del mismo tamaño
    if len(img1.shape) == 3:
        img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    if len(img2.shape) == 3:
        img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
    
    _, bin1 = cv2.threshold(img1, 127, 255, cv2.THRESH_BINARY)
    _, bin2 = cv2.threshold(img2, 127, 255, cv2.THRESH_BINARY)
    
    # Redimensionar si es necesario
    if bin1.shape != bin2.shape:
        bin2 = cv2.resize(bin2, (bin1.shape[1], bin1.shape[0]))
    
    # Calcular diferencias
    diferencia = cv2.absdiff(bin1, bin2)
    cambio_pixels = np.count_nonzero(diferencia)
    
    # Intersección y unión (para IoU)
    interseccion = np.count_nonzero((bin1 == 255) & (bin2 == 255))
    union = np.count_nonzero((bin1 == 255) | (bin2 == 255))
    
    iou = interseccion / union if union > 0 else 0
    
    return {
        "pixels_cambiados": cambio_pixels,
        "porcentaje_cambio": (cambio_pixels / bin1.size) * 100,
        "iou": iou,
        "similitud": iou * 100
    }

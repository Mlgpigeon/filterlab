"""
Pipeline de análisis de deforestación multitemporal.

Integra:
- Carga de GIF/WEBP multiframe
- Preprocesamiento (CLAHE, filtro bilateral)
- Detección de nubes
- Segmentación (LAB, HSV, Otsu)
- Refinamiento morfológico
- Cálculo de áreas
- Análisis estadístico y tendencias
"""

import numpy as np
import cv2
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
from scipy import stats


@dataclass
class FrameResult:
    """Resultado del procesamiento de un frame."""
    year: int
    original: np.ndarray
    preprocessed: np.ndarray
    cloud_mask: np.ndarray
    mask_lab: np.ndarray
    mask_hsv: np.ndarray
    mask_combined: np.ndarray
    mask_final: np.ndarray
    area_km2: float
    area_percentage: float
    n_pixels: int


class DeforestationAnalyzer:
    """
    Analizador de deforestación para series temporales de imágenes satelitales.
    
    Parameters
    ----------
    scale_km : float
        Kilómetros de la escala de referencia
    scale_pixels : int
        Píxeles de la escala de referencia
    start_year : int
        Año del primer frame
    """
    
    def __init__(self, scale_km: float = 20.0, scale_pixels: int = 51, 
                 start_year: int = 2000):
        self.scale_km = scale_km
        self.scale_pixels = scale_pixels
        self.start_year = start_year
        self.km_per_pixel = scale_km / scale_pixels
        self.km2_per_pixel = self.km_per_pixel ** 2
        
        self.results: List[FrameResult] = []
        
        # Parámetros de procesamiento (ajustables)
        self.params = {
            # CLAHE
            'clahe_clip_limit': 2.0,
            'clahe_tile_size': 8,
            
            # Filtro bilateral
            'bilateral_d': 9,
            'bilateral_sigma_color': 75,
            'bilateral_sigma_space': 75,
            
            # Detección de nubes
            'cloud_v_min': 200,
            'cloud_s_max': 50,
            'cloud_l_min': 200,
            'cloud_ab_tolerance': 15,
            
            # Segmentación LAB
            'lab_a_min': 125,
            'lab_b_min': 128,
            'lab_l_min': 50,
            'lab_l_max': 230,
            
            # Segmentación HSV
            'hsv_detect_brown': True,
            'hsv_detect_yellow': True,
            'hsv_detect_orange': True,
            'hsv_detect_beige': True,
            
            # Refinamiento morfológico
            'morph_open_kernel': 3,
            'morph_close_kernel': 5,
            'min_area_pixels': 50,
            
            # Recorte de imagen
            'crop_top': 30,
            'crop_bottom': 45,
            'crop_left': 10,
            'crop_right': 10,
        }
    
    def set_param(self, key: str, value):
        """Establece un parámetro de procesamiento."""
        if key in self.params:
            self.params[key] = value
        else:
            raise KeyError(f"Parámetro desconocido: {key}")
    
    def get_params(self) -> Dict:
        """Retorna los parámetros actuales."""
        return self.params.copy()
    
    def preprocess(self, img: np.ndarray) -> np.ndarray:
        """
        Preprocesa la imagen con CLAHE y filtro bilateral.
        """
        # Convertir a LAB
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # CLAHE en canal L
        clahe = cv2.createCLAHE(
            clipLimit=self.params['clahe_clip_limit'],
            tileGridSize=(self.params['clahe_tile_size'], self.params['clahe_tile_size'])
        )
        l_enhanced = clahe.apply(l_channel)
        
        # Reconstruir LAB
        lab_enhanced = cv2.merge([l_enhanced, a_channel, b_channel])
        img_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)
        
        # Filtro bilateral
        img_filtered = cv2.bilateralFilter(
            img_enhanced,
            d=self.params['bilateral_d'],
            sigmaColor=self.params['bilateral_sigma_color'],
            sigmaSpace=self.params['bilateral_sigma_space']
        )
        
        return img_filtered
    
    def detect_clouds(self, img: np.ndarray) -> np.ndarray:
        """Detecta nubes en la imagen."""
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        
        h, s, v = cv2.split(hsv)
        l, a, b = cv2.split(lab)
        
        # Criterio HSV
        cloud_hsv = (v > self.params['cloud_v_min']) & (s < self.params['cloud_s_max'])
        
        # Criterio LAB
        cloud_lab = (l > self.params['cloud_l_min']) & \
                    (np.abs(a.astype(int) - 128) < self.params['cloud_ab_tolerance']) & \
                    (np.abs(b.astype(int) - 128) < self.params['cloud_ab_tolerance'])
        
        cloud_mask = (cloud_hsv | cloud_lab).astype(np.uint8) * 255
        
        # Refinamiento morfológico
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cloud_mask = cv2.morphologyEx(cloud_mask, cv2.MORPH_CLOSE, kernel)
        cloud_mask = cv2.morphologyEx(cloud_mask, cv2.MORPH_OPEN, kernel)
        
        return cloud_mask
    
    def segment_lab(self, img: np.ndarray) -> np.ndarray:
        """Segmentación de deforestación en espacio LAB."""
        lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Suelo expuesto
        mask_soil = (a > self.params['lab_a_min']) & \
                    (b > self.params['lab_b_min']) & \
                    (l > self.params['lab_l_min']) & \
                    (l < self.params['lab_l_max'])
        
        # Áreas brillantes no vegetadas
        mask_bright = (l > 120) & (a > 118) & (b > 130) & (l < self.params['lab_l_max'])
        
        return ((mask_soil | mask_bright).astype(np.uint8) * 255)
    
    def segment_hsv(self, img: np.ndarray) -> np.ndarray:
        """Segmentación de deforestación en espacio HSV."""
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        masks = []
        
        if self.params['hsv_detect_brown']:
            masks.append(cv2.inRange(hsv, np.array([5, 30, 50]), np.array([25, 255, 255])))
        
        if self.params['hsv_detect_yellow']:
            masks.append(cv2.inRange(hsv, np.array([15, 25, 70]), np.array([45, 255, 255])))
        
        if self.params['hsv_detect_orange']:
            masks.append(cv2.inRange(hsv, np.array([0, 40, 60]), np.array([15, 255, 255])))
        
        if self.params['hsv_detect_beige']:
            masks.append(cv2.inRange(hsv, np.array([10, 15, 120]), np.array([35, 100, 255])))
        
        if masks:
            combined = masks[0]
            for m in masks[1:]:
                combined = cv2.bitwise_or(combined, m)
            return combined
        
        return np.zeros(img.shape[:2], dtype=np.uint8)
    
    def combine_masks(self, mask_lab: np.ndarray, mask_hsv: np.ndarray) -> np.ndarray:
        """Combina máscaras LAB y HSV."""
        m1 = (mask_lab > 0).astype(np.uint8)
        m2 = (mask_hsv > 0).astype(np.uint8)
        
        # Intersección (ambos métodos coinciden)
        combined = (m1 & m2).astype(np.uint8) * 255
        
        return combined
    
    def refine_mask(self, mask: np.ndarray, cloud_mask: np.ndarray) -> np.ndarray:
        """Refina la máscara con morfología y excluye nubes."""
        # Excluir nubes
        result = cv2.bitwise_and(mask, cv2.bitwise_not(cloud_mask))
        
        # Apertura
        k_open = self.params['morph_open_kernel']
        if k_open > 0:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_open, k_open))
            result = cv2.morphologyEx(result, cv2.MORPH_OPEN, kernel)
        
        # Cierre
        k_close = self.params['morph_close_kernel']
        if k_close > 0:
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_close, k_close))
            result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)
        
        # Filtrar componentes pequeños
        min_area = self.params['min_area_pixels']
        if min_area > 0:
            num_labels, labels, stats_, _ = cv2.connectedComponentsWithStats(result, connectivity=8)
            for i in range(1, num_labels):
                if stats_[i, cv2.CC_STAT_AREA] < min_area:
                    result[labels == i] = 0
        
        return result
    
    def calculate_area(self, mask: np.ndarray) -> Tuple[float, float, int]:
        """Calcula área en km², porcentaje y número de píxeles."""
        n_pixels = np.sum(mask > 0)
        area_km2 = n_pixels * self.km2_per_pixel
        percentage = (n_pixels / mask.size) * 100
        return area_km2, percentage, n_pixels
    
    def process_frame(self, frame: np.ndarray, year: int) -> FrameResult:
        """Procesa un único frame."""
        # Recortar bordes
        h, w = frame.shape[:2]
        crop = self.params
        cropped = frame[
            crop['crop_top']:h-crop['crop_bottom'] if crop['crop_bottom'] > 0 else h,
            crop['crop_left']:w-crop['crop_right'] if crop['crop_right'] > 0 else w
        ]
        
        # Preprocesar
        preprocessed = self.preprocess(cropped)
        
        # Detectar nubes
        cloud_mask = self.detect_clouds(preprocessed)
        
        # Segmentación
        mask_lab = self.segment_lab(preprocessed)
        mask_hsv = self.segment_hsv(preprocessed)
        
        # Combinar
        mask_combined = self.combine_masks(mask_lab, mask_hsv)
        
        # Refinar
        mask_final = self.refine_mask(mask_combined, cloud_mask)
        
        # Calcular área
        area_km2, percentage, n_pixels = self.calculate_area(mask_final)
        
        return FrameResult(
            year=year,
            original=cropped,
            preprocessed=preprocessed,
            cloud_mask=cloud_mask,
            mask_lab=mask_lab,
            mask_hsv=mask_hsv,
            mask_combined=mask_combined,
            mask_final=mask_final,
            area_km2=area_km2,
            area_percentage=percentage,
            n_pixels=n_pixels
        )
    
    def analyze_frames(self, frames: List[np.ndarray]) -> List[FrameResult]:
        """Analiza todos los frames."""
        self.results = []
        for i, frame in enumerate(frames):
            year = self.start_year + i
            result = self.process_frame(frame, year)
            self.results.append(result)
        return self.results
    
    def get_statistics(self) -> Dict:
        """Calcula estadísticas del análisis."""
        if not self.results:
            return {}
        
        years = [r.year for r in self.results]
        areas = [r.area_km2 for r in self.results]
        
        # Regresión lineal
        slope, intercept, r_value, p_value, std_err = stats.linregress(years, areas)
        
        # Cambios anuales
        changes = [0] + [areas[i] - areas[i-1] for i in range(1, len(areas))]
        
        return {
            'years': years,
            'areas_km2': areas,
            'annual_changes': changes,
            'area_initial': areas[0],
            'area_final': areas[-1],
            'area_mean': np.mean(areas),
            'area_std': np.std(areas),
            'area_min': min(areas),
            'area_max': max(areas),
            'year_min': years[np.argmin(areas)],
            'year_max': years[np.argmax(areas)],
            'trend_slope': slope,
            'trend_intercept': intercept,
            'trend_r_squared': r_value ** 2,
            'total_change': areas[-1] - areas[0],
            'percent_change': ((areas[-1] - areas[0]) / areas[0] * 100) if areas[0] > 0 else 0,
            'scale_km': self.scale_km,
            'scale_pixels': self.scale_pixels,
            'km2_per_pixel': self.km2_per_pixel
        }
    
    def generate_summary_table(self) -> List[Dict]:
        """Genera tabla resumen para exportar."""
        if not self.results:
            return []
        
        table = []
        for r in self.results:
            table.append({
                'Año': r.year,
                'Área (km²)': round(r.area_km2, 2),
                'Porcentaje': round(r.area_percentage, 2),
                'Píxeles': r.n_pixels
            })
        return table
    
    def create_overlay(self, result: FrameResult, 
                       color: Tuple[int, int, int] = (255, 0, 0),
                       alpha: float = 0.5) -> np.ndarray:
        """Crea overlay de la máscara sobre la imagen original."""
        overlay = result.original.copy()
        mask_bool = result.mask_final > 127
        
        color_layer = np.zeros_like(overlay)
        color_layer[:, :] = color
        
        overlay[mask_bool] = (
            (1 - alpha) * overlay[mask_bool] +
            alpha * color_layer[mask_bool]
        ).astype(np.uint8)
        
        return overlay


def create_temporal_plots(analyzer: DeforestationAnalyzer, 
                          output_path: Optional[str] = None) -> plt.Figure:
    """
    Crea gráficos de análisis temporal.
    
    Returns
    -------
    matplotlib.figure.Figure
        Figura con 4 subplots
    """
    stats_ = analyzer.get_statistics()
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    years = stats_['years']
    areas = stats_['areas_km2']
    changes = stats_['annual_changes']
    
    # Gráfico 1: Evolución temporal
    ax1 = axes[0, 0]
    ax1.plot(years, areas, 'o-', color='darkgreen', linewidth=2, markersize=8)
    ax1.fill_between(years, areas, alpha=0.3, color='green')
    ax1.set_xlabel('Año')
    ax1.set_ylabel('Área Deforestada (km²)')
    ax1.set_title('Evolución del Área Deforestada')
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: Variación anual
    ax2 = axes[0, 1]
    colors = ['green' if x < 0 else 'red' for x in changes]
    ax2.bar(years, changes, color=colors, alpha=0.7, edgecolor='black')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_xlabel('Año')
    ax2.set_ylabel('Cambio Anual (km²)')
    ax2.set_title('Variación Anual de Deforestación')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Gráfico 3: Tendencia lineal
    ax3 = axes[1, 0]
    trend_line = [stats_['trend_slope'] * y + stats_['trend_intercept'] for y in years]
    ax3.scatter(years, areas, color='darkred', s=80, zorder=5, label='Datos observados')
    ax3.plot(years, trend_line, 'b--', linewidth=2, 
             label=f'Tendencia: {stats_["trend_slope"]:.2f} km²/año')
    ax3.set_xlabel('Año')
    ax3.set_ylabel('Área Deforestada (km²)')
    ax3.set_title('Tendencia de Deforestación')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Gráfico 4: Estadísticas
    ax4 = axes[1, 1]
    stats_text = f"""
ESTADÍSTICAS DEL ANÁLISIS
─────────────────────────────

Área inicial ({years[0]}):  {stats_['area_initial']:,.2f} km²
Área final ({years[-1]}):    {stats_['area_final']:,.2f} km²

Incremento total:       {stats_['total_change']:,.2f} km²
Incremento porcentual:  {stats_['percent_change']:.1f}%

Promedio anual:         {stats_['area_mean']:,.2f} km²
Desviación estándar:    {stats_['area_std']:,.2f} km²

Tendencia lineal:       {stats_['trend_slope']:.2f} km²/año
R²:                     {stats_['trend_r_squared']:.3f}

Año mínimo defor.:      {stats_['year_min']} ({stats_['area_min']:,.2f} km²)
Año máximo defor.:      {stats_['year_max']} ({stats_['area_max']:,.2f} km²)

Escala: {stats_['scale_km']} km = {stats_['scale_pixels']} px
"""
    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=10,
             verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax4.axis('off')
    ax4.set_title('Resumen Estadístico')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
    
    return fig

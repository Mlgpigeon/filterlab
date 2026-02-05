# 🌳 FilterLab Expansión: Análisis de Deforestación

## Descripción

Esta expansión añade a FilterLab capacidades específicas para el análisis de deforestación en imágenes satelitales, incluyendo:

- **Nuevos filtros de segmentación** (Otsu adaptativo, HSV, Lab)
- **Módulo de análisis de área** (conversión píxeles → km²)
- **Procesamiento batch** (múltiples imágenes/GIF)
- **Análisis temporal** (evolución año a año)

## 📁 Estructura de Archivos

```
filterlab_expansion/
├── filters/
│   ├── segmentation.py      # Nuevos filtros de segmentación
│   └── definitions.py       # Definiciones actualizadas
├── core/
│   ├── analysis.py          # Cálculo de áreas y estadísticas
│   └── batch.py             # Procesamiento de múltiples imágenes
├── examples/
│   └── deforestacion.py     # Script de ejemplo completo
└── README.md                # Esta documentación
```

## 🔧 Instalación

### Opción 1: Integrar en FilterLab existente

1. Copia `filters/segmentation.py` a tu carpeta `filters/`
2. Reemplaza `filters/definitions.py` con la versión expandida
3. Copia la carpeta `core/` completa
4. Actualiza `filters/__init__.py`:

```python
from .spatial import SPATIAL_FILTERS
from .morphological import MORPHOLOGICAL_FILTERS
from .segmentation import SEGMENTATION_FILTERS  # NUEVO

ALL_FILTERS = {
    **SPATIAL_FILTERS,
    **MORPHOLOGICAL_FILTERS,
    **SEGMENTATION_FILTERS  # NUEVO
}
```

### Opción 2: Uso independiente

```python
import sys
sys.path.append('/ruta/a/filterlab_expansion')

from filters.segmentation import SEGMENTATION_FILTERS
from core.analysis import AnalisisArea, AnalisisTemporal
from core.batch import ProcesadorBatch, PipelineFiltros
```

## 📖 Uso

### Filtros de Segmentación

```python
from filters.segmentation import (
    apply_otsu_adaptativo,
    apply_segmentacion_hsv_verde,
    apply_segmentacion_lab_vegetacion
)

# Otsu Adaptativo (ideal para iluminación no uniforme)
resultado = apply_otsu_adaptativo(img, gray, {
    "block_size": 35,
    "c": 5,
    "invert": False
})

# Detectar vegetación con HSV
vegetacion = apply_segmentacion_hsv_verde(img, gray, {
    "tolerancia": 25,
    "saturacion_min": 30,
    "brillo_min": 30,
    "invert": False  # True para ver NO-vegetación (deforestado)
})

# Detectar vegetación con Lab
vegetacion_lab = apply_segmentacion_lab_vegetacion(img, gray, {
    "sensibilidad": 120,
    "luminosidad_min": 20,
    "invert": True  # Invertir para ver deforestación
})
```

### Cálculo de Área

```python
from core.analysis import AnalisisArea, calcular_area_rapido

# Crear analizador con escala del caso Jamanxim
# 51 píxeles = 20 km
analizador = AnalisisArea.desde_escala(pixels=51, km=20)

# Calcular área de una imagen binaria
resultado = analizador.calcular_area(img_segmentada, contar_blancos=True)

print(f"Área deforestada: {resultado.area_km2:.2f} km²")
print(f"Equivalente a: {resultado.area_ha:.2f} hectáreas")
print(f"Porcentaje de la imagen: {resultado.porcentaje_blanco:.1f}%")

# Función rápida (sin crear instancia)
area = calcular_area_rapido(
    img_segmentada,
    pixels_escala=51,
    km_escala=20,
    contar_blancos=True
)
print(f"Área: {area['km2']:.2f} km²")
```

### Análisis Temporal

```python
from core.analysis import AnalisisArea, AnalisisTemporal

# Crear analizador
analizador = AnalisisArea.desde_escala(51, 20)
temporal = AnalisisTemporal(analizador)

# Agregar imágenes por año
for año in range(2000, 2020):
    img = cargar_imagen(f"frame_{año}.png")
    img_segmentada = procesar(img)
    temporal.agregar_imagen(str(año), img_segmentada)

# Obtener serie temporal
serie = temporal.obtener_serie_temporal()
# {'2000': 125.3, '2001': 134.7, ...}

# Calcular cambio total
cambio = temporal.calcular_cambio("2000", "2019")
print(f"Cambio: {cambio['cambio_absoluto_km2']:.2f} km²")
print(f"Incremento: {cambio['cambio_porcentual']:.1f}%")

# Exportar resultados
temporal.exportar_csv("resultados.csv")
temporal.exportar_json("resultados.json")
```

### Procesamiento Batch

```python
from core.batch import ProcesadorBatch, PipelineFiltros, CargadorImagenes
from filters.segmentation import SEGMENTATION_FILTERS
from filters.spatial import SPATIAL_FILTERS
from filters.morphological import MORPHOLOGICAL_FILTERS

# Crear pipeline
pipeline = PipelineFiltros()

# Registrar todos los filtros disponibles
pipeline.registrar_filtros_desde_modulo(SPATIAL_FILTERS)
pipeline.registrar_filtros_desde_modulo(MORPHOLOGICAL_FILTERS)
pipeline.registrar_filtros_desde_modulo(SEGMENTATION_FILTERS)

# Definir secuencia de procesamiento
pipeline.agregar_paso("gaussiano", {"kernel_size": 5})
pipeline.agregar_paso("clahe", {"clip_limit": 2.0})
pipeline.agregar_paso("segmentacion_hsv_verde", {"tolerancia": 25, "invert": True})
pipeline.agregar_paso("clausura", {"kernel_size": 3})
pipeline.agregar_paso("apertura", {"kernel_size": 3})

# Crear procesador
procesador = ProcesadorBatch(pipeline)

# Cargar desde GIF
procesador.cargar_imagenes("deforestacion.gif", tipo="gif")

# O desde carpeta
# procesador.cargar_imagenes("imagenes/", tipo="carpeta")

# Procesar todas
def progreso(actual, total, nombre):
    print(f"[{actual}/{total}] Procesando: {nombre}")

resultados = procesador.procesar(callback=progreso)

# Guardar imágenes procesadas
procesador.guardar_resultados("salida/")

# Generar comparación visual
procesador.generar_comparacion("salida/")
```

## 🌿 Guía para Análisis de Deforestación

### Flujo de Trabajo Recomendado

1. **Preprocesamiento**
   - Gaussiano (k=3-5) para reducir ruido
   - CLAHE para normalizar iluminación

2. **Segmentación** (elegir UNA opción)
   - `segmentacion_hsv_verde` con `invert=True` → detecta NO-verde
   - `segmentacion_lab_vegetacion` con `invert=True` → detecta NO-vegetación
   - `otsu_adaptativo` → si la imagen tiene buen contraste

3. **Post-procesamiento**
   - Clausura (k=3) para cerrar huecos pequeños
   - Apertura (k=3) para eliminar ruido

4. **Análisis**
   - Calcular área con escala correcta
   - Comparar años para ver evolución

### Escala del Caso Jamanxim

```
20 km en terreno = 51 píxeles en imagen
1 km = 2.55 píxeles
1 píxel = 0.392 km (392 metros)
Área de 1 píxel = 0.154 km² = 15.4 ha
```

### Comparación de Métodos de Segmentación

| Método | Ventajas | Desventajas | Uso ideal |
|--------|----------|-------------|-----------|
| HSV Verde | Intuitivo, configurable | Sensible a sombras | Imágenes con buen color |
| Lab Vegetación | Robusto a iluminación | Menos intuitivo | Iluminación variable |
| Otsu Adaptativo | No requiere color | Necesita buen contraste | Imágenes en B/N |

## 📊 Ejemplo de Salida

```
=== Análisis de Deforestación Bosque Jamanxim ===

Escala: 51 px = 20 km (2.55 px/km)

Año 2000:
  - Área deforestada: 156.32 km²
  - Porcentaje del área total: 8.2%

Año 2019:
  - Área deforestada: 892.45 km²
  - Porcentaje del área total: 46.8%

Cambio 2000-2019:
  - Incremento absoluto: +736.13 km²
  - Incremento relativo: +471%
  - Tasa media anual: +38.7 km²/año
```

## ⚠️ Notas Importantes

1. **La segmentación NO es perfecta**: Siempre habrá falsos positivos/negativos. Los resultados son aproximaciones.

2. **Calibrar con cada imagen**: Los parámetros óptimos varían según la imagen. Usar la UI de FilterLab para encontrar los mejores valores.

3. **Consistencia temporal**: Usar los MISMOS parámetros para todas las imágenes de una serie temporal.

4. **Validar resultados**: Comparar visualmente la segmentación con la imagen original para verificar que detecta lo esperado.

## 📚 Referencias

- OpenCV: Adaptive Thresholding
- Color Spaces: HSV vs Lab for vegetation detection
- Mathematical Morphology: Opening and Closing operations

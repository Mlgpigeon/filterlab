# 🔬 Explorador de Filtros Espaciales y Morfológicos

Aplicación interactiva para experimentar con filtros de procesamiento de imagen.
**Trabajo Grupal - Visión Artificial UNIR**

## 🚀 Instalación y Ejecución

### Requisitos
- Python 3.8+
- pip

### Instalar dependencias

```bash
pip install streamlit opencv-python numpy pillow
```

### Ejecutar la aplicación

```bash
streamlit run app.py
```

Se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📋 Filtros Disponibles

### Filtros Espaciales
| Filtro | Descripción |
|--------|-------------|
| **Gaussiano** | Suavizado mediante convolución gaussiana. Reduce ruido. |
| **Mediana** | Elimina ruido sal y pimienta preservando bordes. |
| **CLAHE** | Ecualización adaptativa de histograma con límite de contraste. |
| **Canny** | Detección de bordes mediante gradiente e histéresis. |
| **Otsu** | Binarización automática óptima. |

### Filtros Morfológicos
| Filtro | Descripción |
|--------|-------------|
| **Apertura** | Erosión + Dilatación. Elimina objetos pequeños. |
| **Clausura** | Dilatación + Erosión. Cierra huecos pequeños. |
| **White Top-Hat** | Resalta objetos brillantes sobre fondo oscuro. |
| **Black Top-Hat** | Resalta objetos oscuros sobre fondo brillante. |
| **Gradiente** | Dilatación - Erosión. Detecta contornos. |
| **Erosión** | Reduce/adelgaza objetos. |
| **Dilatación** | Expande/engrosa objetos. |

## 🎮 Cómo usar

1. **Cargar imagen**: Usa el panel lateral para subir una imagen (PNG, JPG, etc.)
2. **Seleccionar filtros**: Expande cada filtro, ajusta parámetros y pulsa "Añadir"
3. **Ver resultado**: La imagen procesada se actualiza en tiempo real
4. **Orden importa**: Los filtros se aplican en el orden que los añades
5. **Descargar**: Pulsa el botón de descarga para guardar el resultado

## 💡 Consejos

- **Para imágenes ruidosas**: Empieza con Mediana o Gaussiano
- **Para realzar contraste**: Usa CLAHE antes de otros filtros
- **Para detectar objetos**: Combina CLAHE → Otsu → Apertura
- **Para bordes**: Gaussiano → Canny o Gradiente Morfológico
- **Para objetos brillantes**: White Top-Hat funciona muy bien en rayos X

## 📁 Estructura del proyecto

```
filter_app/
├── app.py          # Aplicación principal
├── README.md       # Este archivo
└── requirements.txt # Dependencias
```

## 🔧 Dependencias

```
streamlit>=1.28.0
opencv-python>=4.8.0
numpy>=1.24.0
pillow>=10.0.0
```

---
*Visión Artificial - UNIR 2025*

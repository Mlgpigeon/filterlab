# 🔬 FilterLab

Aplicación interactiva para explorar filtros espaciales y morfológicos.  
**Trabajo Grupal - Visión Artificial UNIR**

## 📁 Estructura del Proyecto

```
filterlab/
├── app.py                  # Punto de entrada principal
├── requirements.txt        # Dependencias
├── run.bat                 # Script de ejecución (Windows)
├── README.md
│
├── filters/                # Paquete de filtros
│   ├── __init__.py
│   ├── definitions.py      # Configuración de filtros (nombres, params)
│   ├── spatial.py          # Implementación filtros espaciales
│   └── morphological.py    # Implementación filtros morfológicos
│
├── core/                   # Paquete de procesamiento
│   ├── __init__.py
│   ├── processor.py        # Aplicación de filtros
│   └── utils.py            # Utilidades de imagen
│
└── ui/                     # Paquete de interfaz
    ├── __init__.py
    ├── sidebar.py          # Panel lateral con filtros
    └── components.py       # Visualización y cola
```

## 🚀 Instalación y Ejecución

### Opción 1: Script automático (Windows)
```bash
run.bat
```

### Opción 2: Manual
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

Se abrirá automáticamente en `http://localhost:8501`

## ✨ Características

- **Cola de filtros**: Panel derecho muestra filtros activos y su orden
- **Sin duplicados**: Solo 1 instancia de cada filtro
- **Tiempo real**: Cambios en parámetros se reflejan inmediatamente
- **Reordenar**: Sube/baja filtros en la cola

## 📋 Filtros Disponibles

### Filtros Espaciales
| Filtro | Descripción |
|--------|-------------|
| Gaussiano | Suavizado, reduce ruido |
| Mediana | Elimina ruido sal y pimienta |
| CLAHE | Ecualización adaptativa de histograma |
| Canny | Detección de bordes |
| Otsu | Binarización automática |
| Laplaciano | Bordes (2ª derivada) |
| Sobel | Bordes direccionales |

### Filtros Morfológicos
| Filtro | Descripción |
|--------|-------------|
| Erosión | Reduce objetos |
| Dilatación | Expande objetos |
| Apertura | Elimina objetos pequeños |
| Clausura | Cierra huecos |
| White Top-Hat | Resalta brillante sobre oscuro |
| Black Top-Hat | Resalta oscuro sobre brillante |
| Gradiente | Detecta contornos |

## 🎮 Cómo Usar

1. **Cargar imagen** desde el panel lateral
2. **Añadir filtros** - cada filtro solo puede añadirse una vez
3. **Ajustar parámetros** - los cambios se aplican en tiempo real
4. **Reordenar** con ⬆️⬇️ en la cola de la derecha
5. **Descargar** el resultado

## 🔧 Añadir Nuevos Filtros

Para añadir un nuevo filtro espacial:

1. Añadir definición en `filters/definitions.py`:
```python
FILTROS_ESPACIALES["mi_filtro"] = {
    "nombre": "Mi Filtro",
    "descripcion": "Descripción del filtro",
    "params": {
        "param1": {"min": 0, "max": 100, "default": 50, "step": 1, "label": "Parámetro 1"}
    }
}
```

2. Implementar en `filters/spatial.py`:
```python
def apply_mi_filtro(img, gray, params):
    param1 = params.get("param1", 50)
    # ... lógica del filtro
    return result

SPATIAL_FILTERS["mi_filtro"] = apply_mi_filtro
```

---
*Visión Artificial - UNIR 2025*

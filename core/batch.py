"""
Módulo de procesamiento batch para FilterLab.

Permite:
- Cargar múltiples imágenes (carpeta, GIF, lista)
- Aplicar pipeline de filtros a todas
- Análisis temporal automático
- Exportar resultados y visualizaciones
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Callable, Optional, Tuple, Union
from dataclasses import dataclass
import json
from PIL import Image
import io


@dataclass
class ImagenProcesada:
    """Resultado del procesamiento de una imagen."""
    nombre: str
    original: np.ndarray
    procesada: np.ndarray
    filtros_aplicados: List[str]
    parametros: Dict
    metadatos: Dict


class CargadorImagenes:
    """
    Carga imágenes desde diferentes fuentes.
    """
    
    EXTENSIONES_VALIDAS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.gif'}
    
    @staticmethod
    def desde_carpeta(ruta: Union[str, Path], 
                      patron: str = "*") -> List[Tuple[str, np.ndarray]]:
        """
        Carga todas las imágenes de una carpeta.
        
        Args:
            ruta: Ruta a la carpeta
            patron: Patrón glob para filtrar archivos (ej: "*.png")
        
        Returns:
            Lista de tuplas (nombre, imagen)
        """
        ruta = Path(ruta)
        imagenes = []
        
        for ext in CargadorImagenes.EXTENSIONES_VALIDAS:
            for archivo in sorted(ruta.glob(f"{patron}{ext}")):
                img = cv2.imread(str(archivo))
                if img is not None:
                    # Convertir BGR a RGB
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    imagenes.append((archivo.stem, img))
        
        return imagenes
    
    @staticmethod
    def desde_gif(ruta: Union[str, Path]) -> List[Tuple[str, np.ndarray]]:
        """
        Extrae todos los frames de un GIF.
        
        Args:
            ruta: Ruta al archivo GIF
        
        Returns:
            Lista de tuplas (nombre_frame, imagen)
        """
        ruta = Path(ruta)
        imagenes = []
        
        with Image.open(ruta) as gif:
            for i in range(gif.n_frames):
                gif.seek(i)
                # Convertir a RGB
                frame = gif.convert('RGB')
                # Convertir a numpy array
                img = np.array(frame)
                nombre = f"{ruta.stem}_frame_{i:03d}"
                imagenes.append((nombre, img))
        
        return imagenes
    
    @staticmethod
    def desde_lista_rutas(rutas: List[Union[str, Path]]) -> List[Tuple[str, np.ndarray]]:
        """
        Carga imágenes desde una lista de rutas.
        
        Args:
            rutas: Lista de rutas a archivos de imagen
        
        Returns:
            Lista de tuplas (nombre, imagen)
        """
        imagenes = []
        
        for ruta in rutas:
            ruta = Path(ruta)
            if ruta.suffix.lower() == '.gif':
                # Si es GIF, extraer frames
                imagenes.extend(CargadorImagenes.desde_gif(ruta))
            else:
                img = cv2.imread(str(ruta))
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    imagenes.append((ruta.stem, img))
        
        return imagenes
    
    @staticmethod
    def extraer_años_de_nombres(nombres: List[str]) -> Dict[str, int]:
        """
        Intenta extraer años de los nombres de archivo.
        
        Busca patrones como: 2000, 2019, frame_2000, etc.
        
        Args:
            nombres: Lista de nombres de archivo
        
        Returns:
            Diccionario {nombre: año}
        """
        import re
        
        años = {}
        patron = re.compile(r'(\d{4})')
        
        for nombre in nombres:
            match = patron.search(nombre)
            if match:
                año = int(match.group(1))
                if 1900 <= año <= 2100:  # Rango razonable
                    años[nombre] = año
        
        return años


class PipelineFiltros:
    """
    Pipeline configurable de filtros.
    
    Permite definir una secuencia de filtros con sus parámetros
    y aplicarla a múltiples imágenes.
    """
    
    def __init__(self):
        """Inicializa el pipeline vacío."""
        self.pasos: List[Tuple[str, Callable, Dict]] = []
        self.filtros_registrados: Dict[str, Callable] = {}
    
    def registrar_filtro(self, nombre: str, funcion: Callable) -> None:
        """
        Registra un filtro para uso en el pipeline.
        
        Args:
            nombre: Nombre identificador del filtro
            funcion: Función que aplica el filtro (img, gray, params) -> img
        """
        self.filtros_registrados[nombre] = funcion
    
    def registrar_filtros_desde_modulo(self, modulo_dict: Dict[str, Callable]) -> None:
        """
        Registra múltiples filtros desde un diccionario de módulo.
        
        Args:
            modulo_dict: Diccionario {nombre: funcion}
        """
        for nombre, funcion in modulo_dict.items():
            self.registrar_filtro(nombre, funcion)
    
    def agregar_paso(self, nombre_filtro: str, params: Dict = None) -> 'PipelineFiltros':
        """
        Agrega un paso al pipeline.
        
        Args:
            nombre_filtro: Nombre del filtro registrado
            params: Parámetros para el filtro
        
        Returns:
            self (para encadenar llamadas)
        """
        if nombre_filtro not in self.filtros_registrados:
            raise ValueError(f"Filtro '{nombre_filtro}' no registrado. "
                           f"Disponibles: {list(self.filtros_registrados.keys())}")
        
        funcion = self.filtros_registrados[nombre_filtro]
        self.pasos.append((nombre_filtro, funcion, params or {}))
        return self
    
    def limpiar(self) -> None:
        """Elimina todos los pasos del pipeline."""
        self.pasos = []
    
    def aplicar(self, img: np.ndarray) -> np.ndarray:
        """
        Aplica el pipeline completo a una imagen.
        
        Args:
            img: Imagen de entrada (RGB)
        
        Returns:
            Imagen procesada
        """
        resultado = img.copy()
        
        for nombre, funcion, params in self.pasos:
            # Calcular versión en grises para filtros que la necesitan
            if len(resultado.shape) == 3:
                gray = cv2.cvtColor(resultado, cv2.COLOR_RGB2GRAY)
            else:
                gray = resultado
            
            # Aplicar filtro
            resultado = funcion(resultado, gray, params)
            
            # Asegurar que el resultado es válido
            if resultado is None:
                raise RuntimeError(f"El filtro '{nombre}' devolvió None")
        
        return resultado
    
    def obtener_descripcion(self) -> List[Dict]:
        """
        Obtiene una descripción del pipeline.
        
        Returns:
            Lista de diccionarios con nombre y parámetros de cada paso
        """
        return [
            {"filtro": nombre, "parametros": params}
            for nombre, _, params in self.pasos
        ]


class ProcesadorBatch:
    """
    Procesador batch de imágenes.
    
    Combina carga de imágenes, pipeline de filtros y análisis.
    """
    
    def __init__(self, pipeline: PipelineFiltros = None):
        """
        Inicializa el procesador.
        
        Args:
            pipeline: Pipeline de filtros a usar (opcional)
        """
        self.pipeline = pipeline or PipelineFiltros()
        self.imagenes: List[Tuple[str, np.ndarray]] = []
        self.resultados: List[ImagenProcesada] = []
    
    def cargar_imagenes(self, fuente: Union[str, Path, List], 
                        tipo: str = "auto") -> int:
        """
        Carga imágenes desde una fuente.
        
        Args:
            fuente: Ruta a carpeta, archivo GIF, o lista de rutas
            tipo: "carpeta", "gif", "lista", o "auto" para detectar
        
        Returns:
            Número de imágenes cargadas
        """
        if tipo == "auto":
            if isinstance(fuente, list):
                tipo = "lista"
            else:
                fuente = Path(fuente)
                if fuente.is_dir():
                    tipo = "carpeta"
                elif fuente.suffix.lower() == '.gif':
                    tipo = "gif"
                else:
                    tipo = "lista"
                    fuente = [fuente]
        
        if tipo == "carpeta":
            self.imagenes = CargadorImagenes.desde_carpeta(fuente)
        elif tipo == "gif":
            self.imagenes = CargadorImagenes.desde_gif(fuente)
        elif tipo == "lista":
            self.imagenes = CargadorImagenes.desde_lista_rutas(fuente)
        else:
            raise ValueError(f"Tipo no válido: {tipo}")
        
        return len(self.imagenes)
    
    def procesar(self, callback: Callable[[int, int, str], None] = None) -> List[ImagenProcesada]:
        """
        Procesa todas las imágenes cargadas.
        
        Args:
            callback: Función de progreso (actual, total, nombre)
        
        Returns:
            Lista de ImagenProcesada
        """
        self.resultados = []
        total = len(self.imagenes)
        
        for i, (nombre, img) in enumerate(self.imagenes):
            if callback:
                callback(i + 1, total, nombre)
            
            try:
                procesada = self.pipeline.aplicar(img)
                
                resultado = ImagenProcesada(
                    nombre=nombre,
                    original=img,
                    procesada=procesada,
                    filtros_aplicados=[p[0] for p in self.pipeline.pasos],
                    parametros={p[0]: p[2] for p in self.pipeline.pasos},
                    metadatos={
                        "tamaño_original": img.shape,
                        "tamaño_procesada": procesada.shape
                    }
                )
                self.resultados.append(resultado)
                
            except Exception as e:
                print(f"Error procesando {nombre}: {e}")
                # Agregar resultado con error
                self.resultados.append(ImagenProcesada(
                    nombre=nombre,
                    original=img,
                    procesada=img,  # Devolver original si falla
                    filtros_aplicados=[],
                    parametros={},
                    metadatos={"error": str(e)}
                ))
        
        return self.resultados
    
    def guardar_resultados(self, carpeta_salida: Union[str, Path],
                           formato: str = "png") -> List[str]:
        """
        Guarda las imágenes procesadas.
        
        Args:
            carpeta_salida: Carpeta donde guardar
            formato: Formato de imagen (png, jpg, etc.)
        
        Returns:
            Lista de rutas guardadas
        """
        carpeta = Path(carpeta_salida)
        carpeta.mkdir(parents=True, exist_ok=True)
        
        rutas = []
        for resultado in self.resultados:
            ruta = carpeta / f"{resultado.nombre}_procesada.{formato}"
            
            # Convertir RGB a BGR para OpenCV
            if len(resultado.procesada.shape) == 3:
                img_bgr = cv2.cvtColor(resultado.procesada, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = resultado.procesada
            
            cv2.imwrite(str(ruta), img_bgr)
            rutas.append(str(ruta))
        
        return rutas
    
    def generar_comparacion(self, carpeta_salida: Union[str, Path],
                            columnas: int = 2) -> str:
        """
        Genera una imagen de comparación lado a lado.
        
        Args:
            carpeta_salida: Carpeta donde guardar
            columnas: Número de columnas en la cuadrícula
        
        Returns:
            Ruta de la imagen generada
        """
        if not self.resultados:
            raise RuntimeError("No hay resultados para comparar")
        
        carpeta = Path(carpeta_salida)
        carpeta.mkdir(parents=True, exist_ok=True)
        
        # Crear mosaico
        n = len(self.resultados)
        filas = (n + columnas - 1) // columnas
        
        # Tamaño de cada celda
        alto_celda = self.resultados[0].original.shape[0]
        ancho_celda = self.resultados[0].original.shape[1]
        
        # Crear imagen grande (original + procesada lado a lado)
        mosaico = np.zeros(
            (filas * alto_celda, columnas * ancho_celda * 2, 3),
            dtype=np.uint8
        )
        
        for i, resultado in enumerate(self.resultados):
            fila = i // columnas
            col = i % columnas
            
            y = fila * alto_celda
            x = col * ancho_celda * 2
            
            # Original
            orig = resultado.original
            if len(orig.shape) == 2:
                orig = cv2.cvtColor(orig, cv2.COLOR_GRAY2RGB)
            mosaico[y:y+alto_celda, x:x+ancho_celda] = orig
            
            # Procesada
            proc = resultado.procesada
            if len(proc.shape) == 2:
                proc = cv2.cvtColor(proc, cv2.COLOR_GRAY2RGB)
            mosaico[y:y+alto_celda, x+ancho_celda:x+ancho_celda*2] = proc
        
        ruta = carpeta / "comparacion_batch.png"
        cv2.imwrite(str(ruta), cv2.cvtColor(mosaico, cv2.COLOR_RGB2BGR))
        
        return str(ruta)


# =============================================================================
# FUNCIONES DE CONVENIENCIA
# =============================================================================

def procesar_carpeta_rapido(carpeta_entrada: Union[str, Path],
                            carpeta_salida: Union[str, Path],
                            filtros: List[Tuple[str, Dict]],
                            filtros_disponibles: Dict[str, Callable]) -> Dict:
    """
    Procesa rápidamente una carpeta de imágenes.
    
    Args:
        carpeta_entrada: Carpeta con imágenes originales
        carpeta_salida: Carpeta para guardar resultados
        filtros: Lista de (nombre_filtro, params)
        filtros_disponibles: Diccionario de filtros registrados
    
    Returns:
        Diccionario con resumen del procesamiento
    
    Ejemplo:
        resultado = procesar_carpeta_rapido(
            "imagenes/",
            "salida/",
            [
                ("gaussiano", {"kernel_size": 5}),
                ("otsu_adaptativo", {"block_size": 35}),
                ("clausura", {"kernel_size": 3})
            ],
            TODOS_LOS_FILTROS
        )
    """
    # Crear pipeline
    pipeline = PipelineFiltros()
    pipeline.registrar_filtros_desde_modulo(filtros_disponibles)
    
    for nombre, params in filtros:
        pipeline.agregar_paso(nombre, params)
    
    # Crear procesador
    procesador = ProcesadorBatch(pipeline)
    
    # Cargar y procesar
    n_imagenes = procesador.cargar_imagenes(carpeta_entrada)
    
    def progreso(actual, total, nombre):
        print(f"Procesando {actual}/{total}: {nombre}")
    
    procesador.procesar(callback=progreso)
    
    # Guardar
    rutas = procesador.guardar_resultados(carpeta_salida)
    
    return {
        "imagenes_procesadas": n_imagenes,
        "archivos_guardados": rutas,
        "pipeline": pipeline.obtener_descripcion()
    }


def extraer_frames_gif(ruta_gif: Union[str, Path],
                       carpeta_salida: Union[str, Path]) -> List[str]:
    """
    Extrae frames de un GIF y los guarda como imágenes individuales.
    
    Args:
        ruta_gif: Ruta al archivo GIF
        carpeta_salida: Carpeta donde guardar los frames
    
    Returns:
        Lista de rutas de los frames guardados
    """
    carpeta = Path(carpeta_salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    
    frames = CargadorImagenes.desde_gif(ruta_gif)
    rutas = []
    
    for nombre, img in frames:
        ruta = carpeta / f"{nombre}.png"
        cv2.imwrite(str(ruta), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        rutas.append(str(ruta))
    
    return rutas

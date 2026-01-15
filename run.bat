@echo off
title FilterLab - Vision Artificial UNIR
echo ============================================
echo   FilterLab - Explorador de Filtros
echo   Vision Artificial - UNIR 2025
echo ============================================
echo.

:: Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

:: Crear entorno virtual si no existe
if not exist ".venv" (
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado
    echo.
) else (
    echo [OK] Entorno virtual existente
    echo.
)

:: Activar entorno virtual
echo Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo [OK] Entorno virtual activado
echo.

:: Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [AVISO] Hubo problemas instalando algunas dependencias
    echo Intentando continuar...
)
echo [OK] Dependencias instaladas
echo.

:: Ejecutar aplicación
echo ============================================
echo   Iniciando aplicacion...
echo   Se abrira en tu navegador automaticamente
echo   Para cerrar: Ctrl+C en esta ventana
echo ============================================
echo.

streamlit run app.py

:: Desactivar entorno virtual al cerrar
call deactivate
pause

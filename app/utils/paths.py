import sys
import os
from pathlib import Path
from typing import Union

# Resuelve las rutas del sistema de archivos para desarrollo y producción
# Asegura que los recursos se encuentren independientemente de si es un script o un ejecutable compilado

def get_root_path() -> Path:
    # Determina la raíz del proyecto
    
    # Intenta resolver la ruta basándose en la ubicación de este archivo
    base_path: Path = Path(__file__).parent.parent.parent
    
    # Valida la estructura de directorios
    if (base_path / "app" / "resources").exists():
        return base_path
        
    # Fallback para entornos congelados (PyInstaller)
    if getattr(sys, 'frozen', False):
        return Path(os.path.dirname(sys.executable))
        
    return base_path

def get_exe_location() -> Path:
    # Retorna la ubicación física del ejecutable o script
    if getattr(sys, 'frozen', False):
        return Path(os.path.dirname(sys.executable))
    
    # En desarrollo, normaliza a la raíz del repositorio
    return Path(__file__).parent.parent.parent

def get_resource_path(relative_path: str) -> str:
    # Resuelve la ruta absoluta de un recurso estático
    base_path: Path = get_root_path()
    
    # Intenta localizar el recurso en la estructura estándar
    path: Path = base_path / 'app' / 'resources' / relative_path
    
    # Fallback para estructura plana o distribuida
    if not path.exists():
        path = base_path / 'resources' / relative_path
        
    return str(path)

def get_config_path() -> str:
    # Obtiene el directorio de configuración del usuario
    
    # En Windows, utiliza %APPDATA%
    app_data: Union[str, None] = os.getenv('APPDATA')
    if not app_data:
        # Fallback genérico al directorio home
        app_data = os.path.expanduser("~")
        
    config_dir: Path = Path(app_data) / 'Typhera' / 'config'
    
    # Asegura que el directorio exista
    try:
        os.makedirs(config_dir, exist_ok=True)
    except OSError:
        pass
            
    return str(config_dir)

def get_user_sounds_path() -> str:
    # Obtiene el directorio de AppData para sonidos de usuario
    # En Windows, utiliza %APPDATA%
    app_data: Union[str, None] = os.getenv('APPDATA')
    if not app_data:
        # Fallback genérico al directorio home
        app_data = os.path.expanduser("~")

    sounds_path: Path = Path(app_data) / "Typhera" / "sounds"
    
    if not sounds_path.exists():
        try:
            os.makedirs(sounds_path, exist_ok=True)
        except OSError:
            pass
            
    return str(sounds_path)

def get_custom_sounds_path() -> str:
    # Retorna la ruta específica para packs de sonido personalizados
    # Ahora apunta al mismo directorio base de sonidos
    return get_user_sounds_path()

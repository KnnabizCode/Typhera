import sys
import os
from pathlib import Path

# Este archivo ayuda a encontrar las carpetas importantes del proyecto.
# Funciona tanto si estamos programando como si ya creamos el archivo .exe.

def get_root_path():
    # Intentamos ir 3 niveles arriba desde este archivo: utils -> app -> raiz
    base_path = Path(__file__).parent.parent.parent
    
    # Comprobamos si 'app/resources' existe desde aqui (indicativo de la estructura correcta)
    if (base_path / "app" / "resources").exists():
        return base_path
        
    # Fallback para casos donde __file__ no sea fiable
    if getattr(sys, 'frozen', False):
        return Path(os.path.dirname(sys.executable))
        
    return base_path

def get_exe_location():
    if getattr(sys, 'frozen', False):
        return Path(os.path.dirname(sys.executable))
    
    # En desarrollo, es la raiz
    return Path(__file__).parent.parent.parent

def get_resource_path(relative_path):
    base_path = get_root_path()
    
    path = base_path / 'app' / 'resources' / relative_path
    
    if not path.exists():
        path = base_path / 'resources' / relative_path
        
    return str(path)

def get_config_path():
    # En Windows, APPDATA apunta a Roaming
    app_data = os.getenv('APPDATA')
    if not app_data:
        # Fallback genérico (ej: linux/mac o error)
        app_data = os.path.expanduser("~")
        
    config_dir = Path(app_data) / 'Typhera' / 'config'
    
    # Creamos la carpeta si no existe
    try:
        os.makedirs(config_dir, exist_ok=True)
    except OSError:
        pass
            
    return str(config_dir)

def get_user_sounds_path():
    # En Windows: C:/Users/Usuario/Documents/Typhera
    docs_path = Path(os.path.expanduser("~")) / "Documents" / "Typhera"
    
    if not docs_path.exists():
        try:
            os.makedirs(docs_path)
            # Creamos la carpeta 'Custom'
            os.makedirs(docs_path / "Custom", exist_ok=True)
        except OSError:
            pass
            
    return str(docs_path)

def get_custom_sounds_path():
    return str(Path(get_user_sounds_path()) / "Custom")

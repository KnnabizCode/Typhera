import json
import os
from typing import Any, Dict, Optional
from app.utils.paths import get_config_path

# Gestiona la persistencia de la configuración del usuario
class ConfigManager:
    _instance: Optional['ConfigManager'] = None
    _config: Dict[str, Any] = {}
    _file_path: str = ""
    
    # Define la configuración base por defecto
    DEFAULT_SETTINGS: Dict[str, Any] = {
        "volume": 50,
        "theme": "dark",
        "sound_pack": "default"
    }

    def __new__(cls) -> 'ConfigManager':
        # Implementa el patrón Singleton para mantener una única instancia
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        # Establece la ruta del archivo y carga la configuración inicial
        config_dir: str = get_config_path()
        self._file_path = os.path.join(config_dir, "settings.json")
        self.load_config()

    def load_config(self) -> None:
        # Carga la configuración desde el disco o crea una por defecto si falla
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"Error cargando config: {e}")
                self._config = self.DEFAULT_SETTINGS.copy()
        else:
            self._config = self.DEFAULT_SETTINGS.copy()
            self.save_config()

    def save_config(self) -> None:
        # Persiste la configuración actual en el archivo JSON
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"Error guardando config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        # Recupera un valor de configuración
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        # Actualiza un valor y persiste los cambios
        self._config[key] = value
        self.save_config()

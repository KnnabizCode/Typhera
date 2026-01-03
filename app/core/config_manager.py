import json
import os
from app.utils.paths import get_config_path

# Se encarga de guardar y leer las opciones del usuario.

class ConfigManager:
    _instance = None
    _config = {}
    _file_path = ""
    
    # Valores por defecto si no existe el archivo
    DEFAULT_SETTINGS = {
        "volume": 50,
        "theme": "dark", # 'dark' o 'light'
        "sound_pack": "default"
    }

    def __new__(cls):
        # Aseguramos que solo haya un ConfigManager en toda la app
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        config_dir = get_config_path()
        self._file_path = os.path.join(config_dir, "settings.json")
        self.load_config()

    def load_config(self):
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

    def save_config(self):
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            print(f"Error guardando config: {e}")

    def get(self, key, default=None):
        return self._config.get(key, default)

    def set(self, key, value):
        self._config[key] = value
        self.save_config()

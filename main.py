import sys
import os
from PySide6.QtWidgets import QApplication

# Aseguramos que Python encuentre nuestros modulos
# Agregamos la carpeta actual al path de busqueda
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config_manager import ConfigManager
from app.core.keyboard_listener import KeyboardMonitor
from app.core.state import AppState
from app.core.sound_engine import initialize_sound_engine
from app.ui.main_window import TypheraWindow
from app.ui.tray import TypheraTray

# Función principal
def main():
    # Crear la aplicacion Qt
    app = QApplication(sys.argv)
    
    # Esto es importante para que la app no se cierre si cerramos la ventana
    # porque queremos que siga en la bandeja del sistema
    app.setQuitOnLastWindowClosed(False)

    # Cargar configuracion
    config = ConfigManager()
    
    # Iniciar motor de sonido
    initialize_sound_engine()
    
    # Iniciar monitor de teclado (en segundo plano)
    kb_monitor = KeyboardMonitor()
    kb_monitor.start()

    # Iniciar UI
    window = TypheraWindow()
    tray = TypheraTray(window)

    # Iniciar bucle de eventos
    exit_code = app.exec()

    # Limpieza al salir
    kb_monitor.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

import sys
import os
from PySide6.QtWidgets import QApplication

# Configura la ruta de búsqueda para módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config_manager import ConfigManager
from app.core.keyboard_listener import KeyboardMonitor
from app.core.sound_engine import initialize_sound_engine
from app.ui.main_window import TypheraWindow
from app.ui.tray import TypheraTray

# Orquesta la inicialización de servicios y el ciclo de vida de la UI
def main() -> None:
    # Inicializa el contexto de la aplicación Qt
    app: QApplication = QApplication(sys.argv)
    
    # Mantiene la ejecución activa en segundo plano al cerrar ventanas
    app.setQuitOnLastWindowClosed(False)

    # Carga la configuración del sistema
    _config: ConfigManager = ConfigManager()
    
    # Prepara el motor de audio
    initialize_sound_engine()
    
    # Inicia el monitoreo de eventos de teclado en hilo separado
    kb_monitor: KeyboardMonitor = KeyboardMonitor()
    kb_monitor.start()

    # Instancia y conecta los componentes visuales
    window: TypheraWindow = TypheraWindow()
    _tray: TypheraTray = TypheraTray(window)

    # Ejecuta el bucle de eventos principal
    exit_code: int = app.exec()

    # Finaliza hilos y libera recursos
    kb_monitor.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

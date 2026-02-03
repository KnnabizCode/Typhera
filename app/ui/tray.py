from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QMainWindow
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QCoreApplication
from app.utils.paths import get_resource_path
from app.core.state import AppState

# Controla el icono en la bandeja del sistema y su menú contextual
# Permite interacción básica con la aplicación minimizada
class TypheraTray(QSystemTrayIcon):
    def __init__(self, main_window: QMainWindow) -> None:
        # Inicializa el icono con la referencia a la ventana principal
        icon_path: str = get_resource_path("icons/icon.ico")
        super().__init__(QIcon(icon_path), main_window)
        
        self.window: QMainWindow = main_window
        self.setToolTip("Typhera")
        
        # Construye el menú contextual
        self.menu: QMenu = QMenu()
        
        # Opción para restaurar la ventana
        self.action_show: QAction = self.menu.addAction("Abrir Configuración")
        self.action_show.triggered.connect(self.show_window)
        
        # Opción para pausar/reanudar el listener
        self.action_toggle: QAction = self.menu.addAction("Pausar")
        self.action_toggle.triggered.connect(self.toggle_state)
        
        self.menu.addSeparator()
        
        # Opción para cerrar la aplicación completamente
        self.action_quit: QAction = self.menu.addAction("Salir")
        self.action_quit.triggered.connect(self.quit_app)
        
        self.setContextMenu(self.menu)
        
        # Maneja la activación por doble clic
        self.activated.connect(self.on_activated)
        
        self.show()

    def show_window(self) -> None:
        # Restaura y enfoca la ventana principal
        self.window.show()
        self.window.activateWindow()

    def toggle_state(self) -> None:
        # Alterna el estado global de pausa
        AppState.toggle()
        self.update_menu_text()
        
        # Sincroniza la interfaz de la ventana principal si está visible
        if hasattr(self.window, 'update_ui_state'):
            self.window.update_ui_state()

    def update_menu_text(self) -> None:
        # Actualiza el texto del menú según el estado actual
        if AppState.is_active():
            self.action_toggle.setText("Pausar")
            self.setToolTip("Typhera: Activo")
        else:
            self.action_toggle.setText("Reanudar")
            self.setToolTip("Typhera: Pausa")

    def on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        # Abre la ventana al hacer doble clic en el icono
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def quit_app(self) -> None:
        # Finaliza el proceso de la aplicación
        QCoreApplication.quit()

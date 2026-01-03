from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon
from PySide6.QtCore import QCoreApplication
from app.utils.paths import get_resource_path
from app.core.state import AppState

# Icono en la bandeja del sistema.
# Permite controlar la app sin abrir la ventana.

class TypheraTray(QSystemTrayIcon):
    def __init__(self, main_window):
        # Necesitamos una referencia a la ventana principal para mostrarla/ocultarla
        icon_path = get_resource_path("icons/icon.ico")
        # Si no hay icono, PySide usara uno por defecto o nada
        super().__init__(QIcon(icon_path), main_window)
        self.window = main_window
        
        self.setToolTip("Typhera")
        
        # Crear menu
        self.menu = QMenu()
        
        # Accion: Abrir
        self.action_show = self.menu.addAction("Abrir Configuración")
        self.action_show.triggered.connect(self.show_window)
        
        # Accion: Pausar/Reanudar
        self.action_toggle = self.menu.addAction("Pausar")
        self.action_toggle.triggered.connect(self.toggle_state)
        
        # Separador
        self.menu.addSeparator()
        
        # Accion: Salir
        self.action_quit = self.menu.addAction("Salir")
        self.action_quit.triggered.connect(self.quit_app)
        
        self.setContextMenu(self.menu)
        
        # Al hacer doble clic en el icono, abrimos la ventana
        self.activated.connect(self.on_activated)
        
        self.show()

    def show_window(self):
        self.window.show()
        self.window.activateWindow() # Traer al frente

    def toggle_state(self):
        AppState.toggle()
        self.update_menu_text()
        self.window.update_ui_state() # Sincronizar ventana si esta abierta

    def update_menu_text(self):
        if AppState.is_active():
            self.action_toggle.setText("Pausar")
            self.setToolTip("Typhera: Activo")
        else:
            self.action_toggle.setText("Reanudar")
            self.setToolTip("Typhera: Pausa")

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def quit_app(self):
        QCoreApplication.quit()

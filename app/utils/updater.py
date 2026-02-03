import sys
import json
import webbrowser
from typing import Optional, List, Any, Dict
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, Signal, Qt, QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget
from app.core.config_manager import ConfigManager
from app import __version__

# Define el repositorio de GitHub y el intervalo de verificación
GITHUB_REPO: str = "KnnabizCode/Typhera"
CHECK_INTERVAL_HOURS: int = 24

# Gestiona la verificación de actualizaciones en segundo plano utilizando QtNetwork
class UpdateChecker(QObject):
    # Emite una señal cuando se detecta una nueva versión: (tag_versión, url_descarga)
    update_available: Signal = Signal(str, str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self.manager: QNetworkAccessManager = QNetworkAccessManager(self)
        self.manager.finished.connect(self.on_request_finished)

    def check(self) -> None:
        # Inicia la consulta de actualizaciones si ha pasado el tiempo suficiente
        try:
            config: ConfigManager = ConfigManager()
            last_check_str: Any = config.get("last_update_check")
            
            # Valida el límite de frecuencia de solicitudes (Rate Limiting local)
            if last_check_str:
                try:
                    last_check: datetime = datetime.fromisoformat(last_check_str)
                    if datetime.now() - last_check < timedelta(hours=CHECK_INTERVAL_HOURS):
                        return 
                except ValueError:
                    pass

            # Prepara la solicitud a la API de GitHub
            url: QUrl = QUrl(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest")
            request: QNetworkRequest = QNetworkRequest(url)
            request.setHeader(QNetworkRequest.UserAgentHeader, "Typhera-App")
            
            self.manager.get(request)
            
            # Registra el intento de actualización
            config.set("last_update_check", datetime.now().isoformat())
            
        except Exception:
            pass

    def on_request_finished(self, reply: QNetworkReply) -> None:
        # Procesa la respuesta de la API de GitHub
        try:
            if reply.error() == QNetworkReply.NoError:
                data: Dict[str, Any] = json.loads(str(reply.readAll(), 'utf-8'))
                
                latest_tag: str = data.get("tag_name", "").lstrip("v")
                html_url: str = data.get("html_url", "")
                
                # Compara las versiones semánticas
                if self.is_newer(latest_tag, __version__):
                    self.update_available.emit(latest_tag, html_url)
        except Exception:
            pass
        finally:
            reply.deleteLater()

    def is_newer(self, remote_ver: str, local_ver: str) -> bool:
        # Compara dos cadenas de versión
        try:
            r_parts: List[int] = [int(p) for p in remote_ver.split('.')]
            l_parts: List[int] = [int(p) for p in local_ver.split('.')]
            return r_parts > l_parts
        except Exception:
            # Fallback a comparación de cadenas simple
            return remote_ver > local_ver

# Diálogo modal para notificar al usuario sobre nuevas actualizaciones
class UpdateDialog(QDialog):
    def __init__(self, new_version: str, download_url: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.download_url: str = download_url
        self.setWindowTitle("Actualización disponible")
        
        self.setFixedSize(320, 180)
        
        # Elimina el botón de ayuda del contexto en la barra de título
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Muestra el título
        title_label: QLabel = QLabel(f"¡Nueva versión disponible!")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Muestra la información de la versión
        info_label: QLabel = QLabel(f"La versión <b>{new_version}</b> está disponible.<br>¿Deseas descargarla ahora?")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Configura los botones de acción
        btn_layout: QHBoxLayout = QHBoxLayout()
        
        self.btn_later: QPushButton = QPushButton("Más tarde")
        self.btn_later.setCursor(Qt.PointingHandCursor)
        self.btn_later.clicked.connect(self.reject)
        
        self.btn_update: QPushButton = QPushButton("Actualizar")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.setObjectName("primary_btn")
        self.btn_update.clicked.connect(self.open_download)
        
        # Aplica estilos CSS a los botones
        common_style: str = """
            QPushButton {
                background-color: #313244; 
                color: white; 
                font-weight: bold; 
                padding: 8px 16px; 
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """
        self.btn_later.setStyleSheet(common_style)
        self.btn_update.setStyleSheet(common_style)
        
        btn_layout.addWidget(self.btn_later)
        btn_layout.addWidget(self.btn_update)
        
        layout.addLayout(btn_layout)

    def open_download(self) -> None:
        # Abre el navegador predeterminado en la URL de descarga
        webbrowser.open(self.download_url)
        self.accept()

# Interfaz pública para iniciar el proceso de actualización
def check_for_updates(parent_window: Optional[Any] = None, force: bool = False) -> None:
    # Inicia el chequeo de actualizaciones y vincula el diálogo al padre si es necesario
    if parent_window:
        if force:
            ConfigManager().set("last_update_check", "")

        # Mantiene la referencia viva adjuntándola a la ventana padre
        checker: UpdateChecker = UpdateChecker(parent_window)
        parent_window._update_checker = checker
        
        checker.update_available.connect(lambda ver, url: show_update_dialog(ver, url, parent_window))
        
        checker.check()

def show_update_dialog(version: str, url: str, parent: Optional[QWidget]) -> None:
    # Instancia y muestra el diálogo de actualización de manera modal
    dialog: UpdateDialog = UpdateDialog(version, url, parent)
    dialog.exec()

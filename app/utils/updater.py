import sys
import json
import urllib.request
import webbrowser
from datetime import datetime, timedelta
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from app.core.config_manager import ConfigManager
from app import __version__

# Repositorio de GitHub para verificar releases (Usuario/Repo)
# Se asume este repo dado el contexto del usuario.
GITHUB_REPO = "KnnabizCode/Typhera"
# Intervalo mínimo entre verificaciones (en horas)
CHECK_INTERVAL_HOURS = 0.0000000000000001

# Hilo de Verificación
class UpdateCheckerWorker(QThread):
    # Señal que se emite si hay una actualización: (nueva_version, url_descarga)
    update_available = Signal(str, str)

    def run(self):
        try:
            # Instancia del gestor de configuración
            config = ConfigManager()
            last_check_str = config.get("last_update_check")
            
            # Verificar la caché de tiempo (Rate Limiting local)
            # Si ya verificamos recientemente, no hacemos nada.
            if last_check_str:
                try:
                    last_check = datetime.fromisoformat(last_check_str)
                    if datetime.now() - last_check < timedelta(hours=CHECK_INTERVAL_HOURS):
                        return # Aún no ha pasado el tiempo suficiente
                except ValueError:
                    # Si el formato está corrupto, procedemos a verificar
                    pass

            # Consultar API de Releases de GitHub
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            
            # Es importante poner un User-Agent para que GitHub no bloquee la petición
            req = urllib.request.Request(url, headers={'User-Agent': 'Typhera-App'})
            
            # Timeout corto para no dejar el hilo colgado si falla la red
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    
                    # Obtener tag y url. Ejemplo tag: "v1.2.0" -> "1.2.0"
                    latest_tag = data.get("tag_name", "").lstrip("v")
                    html_url = data.get("html_url", "")
                    
                    # Comparar versiones
                    if self.is_newer(latest_tag, __version__):
                        self.update_available.emit(latest_tag, html_url)
            
            # Actualizar timestamp de última verificación exitosa (o intento)
            config.set("last_update_check", datetime.now().isoformat())
            
        except Exception:
            # Manejo de errores silencioso como se solicitó.
            # (Sin internet, error de API, etc. no molestamos al usuario).
            pass

    def is_newer(self, remote_ver, local_ver):
        try:
            # Convertimos "1.2.3" -> [1, 2, 3] para comparación numérica
            r_parts = [int(p) for p in remote_ver.split('.')]
            l_parts = [int(p) for p in local_ver.split('.')]
            return r_parts > l_parts
        except Exception:
            # Fallback por si las etiquetas no siguen formato estándar
            return remote_ver > local_ver

# Ventana Emergente
class UpdateDialog(QDialog):
    def __init__(self, new_version, download_url, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.setWindowTitle("Actualización disponible")
        
        # Tamaño fijo y diseño limpio
        self.setFixedSize(320, 180)
        
        # Ocultar botón de ayuda en la barra de título (común en diálogos Qt)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Layout principal vertical
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Título destacado
        title_label = QLabel(f"¡Nueva versión disponible!")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;") # Color oscuro genérico
        if parent:
            pass

        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Texto informativo
        info_label = QLabel(f"La versión <b>{new_version}</b> está disponible.<br>¿Deseas descargarla ahora?")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # Botones (Más tarde | Actualizar)
        btn_layout = QHBoxLayout()
        
        self.btn_later = QPushButton("Más tarde")
        self.btn_later.setCursor(Qt.PointingHandCursor)
        self.btn_later.clicked.connect(self.reject)
        
        self.btn_update = QPushButton("Actualizar")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.setObjectName("primary_btn")
        self.btn_update.clicked.connect(self.open_download)
        
        # Estilo común para ambos botones
        common_style = """
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

    def open_download(self):
        webbrowser.open(self.download_url)
        self.accept()

# Función de Entrada (API Pública)
def check_for_updates(parent_window=None):
    # Guardamos el worker en el objeto parent para evitar que el Garbage Collector lo elimine
    if parent_window and not hasattr(parent_window, "_update_worker"):
        worker = UpdateCheckerWorker()
        
        # Conectamos la señal de "actualización encontrada" para mostrar el diálogo
        # Usamos lambda para pasar los argumentos al slot
        worker.update_available.connect(lambda ver, url: show_update_dialog(ver, url, parent_window))
        
        # Asignamos el worker al parent
        parent_window._update_worker = worker
        
        # Iniciamos el hilo
        worker.start()

def show_update_dialog(version, url, parent):
    dialog = UpdateDialog(version, url, parent)
    dialog.exec()
